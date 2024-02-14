from difflib import SequenceMatcher
from string import ascii_letters, digits
import uuid

from django.db import migrations

from nautobot.core.models.managers import TagsManager
from nautobot.core.models.utils import serialize_object
import nautobot.dcim.choices as dcim_choices
from nautobot.extras import choices as extras_choices, models as extras_models
from nautobot.extras.constants import CHANGELOG_MAX_OBJECT_REPR


def migrate_dlm_software_models_to_core(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    DLMSoftwareVersion = apps.get_model("nautobot_device_lifecycle_mgmt", "SoftwareLCM")
    DLMSoftwareImage = apps.get_model("nautobot_device_lifecycle_mgmt", "SoftwareImageLCM")
    CoreSoftwareVersion = apps.get_model("dcim", "SoftwareVersion")
    CoreSoftwareImage = apps.get_model("dcim", "SoftwareImageFile")
    Device = apps.get_model("dcim", "Device")
    InventoryItem = apps.get_model("dcim", "InventoryItem")
    ObjectChange = apps.get_model("extras", "ObjectChange")
    RelationshipAssociation = apps.get_model("extras", "RelationshipAssociation")
    Status = apps.get_model("extras", "Status")
    TaggedItem = apps.get_model("extras", "TaggedItem")

    dlm_software_version_ct = ContentType.objects.get_for_model(DLMSoftwareVersion)
    dlm_software_image_ct = ContentType.objects.get_for_model(DLMSoftwareImage)
    core_software_version_ct = ContentType.objects.get_for_model(CoreSoftwareVersion)
    core_software_image_ct = ContentType.objects.get_for_model(CoreSoftwareImage)

    device_ct = ContentType.objects.get_for_model(Device)
    inventory_item_ct = ContentType.objects.get_for_model(InventoryItem)

    _migrate_content_types(apps, dlm_software_version_ct, core_software_version_ct)
    _migrate_content_types(apps, dlm_software_image_ct, core_software_image_ct)

    status_active = Status.objects.get(name="Active")

    # Migrate nautobot_device_lifecycle_mgmt.SoftwareLCM instances to dcim.SoftwareVersion
    for dlm_software_version in DLMSoftwareVersion.objects.all():
        core_software_version = CoreSoftwareVersion(
            id=dlm_software_version.id,
            platform=dlm_software_version.device_platform,
            version=dlm_software_version.version,
            alias=dlm_software_version.alias,
            release_date=dlm_software_version.release_date,
            end_of_support_date=dlm_software_version.end_of_support,
            documentation_url=dlm_software_version.documentation_url,
            long_term_support=dlm_software_version.long_term_support,
            pre_release=dlm_software_version.pre_release,
            status=status_active,
            _custom_field_data=dlm_software_version._custom_field_data,
        )
        core_software_version.save()

        # Work around created field's auto_now_add behavior
        CoreSoftwareVersion.objects.filter(id=core_software_version.id).update(created=dlm_software_version.created)
        core_software_version.refresh_from_db()

        # Migrate "Software on Device" relationships to the Device.software_version foreign key
        for relationship_association in RelationshipAssociation.objects.filter(
            relationship__key="device_soft",
            source_type=core_software_version_ct,
            source_id=core_software_version.id,
            destination_type=device_ct,
        ):
            device = Device.objects.get(id=relationship_association.destination_id)
            device.software_version = core_software_version
            device.save()

        # Migrate "Software on InventoryItem" relationships to the InventoryItem.software_version foreign key
        for relationship_association in RelationshipAssociation.objects.filter(
            relationship__key="inventory_item_soft",
            source_id=core_software_version.id,
            source_type=core_software_version_ct,
            destination_type=inventory_item_ct,
        ):
            inventory_item = InventoryItem.objects.get(id=relationship_association.destination_id)
            inventory_item.software_version = core_software_version
            inventory_item.save()

        # make tag manager available in migration for nautobot.core.models.utils.serialize_object
        # https://github.com/jazzband/django-taggit/issues/101
        # https://github.com/jazzband/django-taggit/issues/454
        core_software_version.tags = TagsManager(
            through=extras_models.TaggedItem,
            model=CoreSoftwareVersion,
            instance=core_software_version,
            prefetch_cache_name="tags",
        )

        # Create an object change to document migration
        ObjectChange.objects.create(
            action=extras_choices.ObjectChangeActionChoices.ACTION_UPDATE,
            change_context=extras_choices.ObjectChangeEventContextChoices.CONTEXT_ORM,
            change_context_detail="Migrated from Nautobot App Device Lifecycle Management",
            changed_object_id=core_software_version.id,
            changed_object_type=core_software_version_ct,
            object_data=serialize_object(core_software_version),
            object_repr=f"{core_software_version.platform.name} - {core_software_version.version}"[
                :CHANGELOG_MAX_OBJECT_REPR
            ],
            request_id=uuid.uuid4(),
        )

    for dlm_software_image in DLMSoftwareImage.objects.all():
        core_software_image = CoreSoftwareImage(
            id=dlm_software_image.id,
            software_version=CoreSoftwareVersion.objects.get(id=dlm_software_image.software.id),
            image_file_name=dlm_software_image.image_file_name,
            image_file_checksum=dlm_software_image.image_file_checksum,
            hashing_algorithm=_migrate_hashing_algorithm(dlm_software_image.hashing_algorithm),
            download_url=dlm_software_image.download_url,
            status=status_active,
            _custom_field_data=dlm_software_image._custom_field_data or {},
        )
        core_software_image.save()
        core_software_image.device_types.set(dlm_software_image.device_types.all())

        # Work around created field's auto_now_add behavior
        CoreSoftwareImage.objects.filter(id=core_software_image.id).update(created=dlm_software_image.created)

        # Map the DLM object_tags to devices and set the Device.software_image_files m2m field
        device_pks = (
            TaggedItem.objects.filter(tag__in=dlm_software_image.object_tags.all(), content_type=device_ct)
            .values_list("object_id")
            .distinct()
        )
        for device in Device.objects.filter(pk__in=device_pks):
            device.software_image_files.add(core_software_image)

        # TODO: Map the DLM object_tags to inventory items and set the InventoryItem.software_image_files m2m field
        # TODO: Map the DLM object_tags to virtual machines and set the VirtualMachine.software_image_files m2m field

        core_software_image.refresh_from_db()

        # make tag manager available in migration for nautobot.core.models.utils.serialize_object
        # https://github.com/jazzband/django-taggit/issues/101
        # https://github.com/jazzband/django-taggit/issues/454
        core_software_image.tags = TagsManager(
            through=extras_models.TaggedItem,
            model=CoreSoftwareImage,
            instance=core_software_image,
            prefetch_cache_name="tags",
        )

        # Create an object change to document migration
        ObjectChange.objects.create(
            action=extras_choices.ObjectChangeActionChoices.ACTION_UPDATE,
            change_context=extras_choices.ObjectChangeEventContextChoices.CONTEXT_ORM,
            change_context_detail="Migrated from Nautobot App Device Lifecycle Management",
            changed_object_id=core_software_image.id,
            changed_object_type=core_software_image_ct,
            object_data=serialize_object(core_software_image),
            object_repr=f"{core_software_image.software_version.platform.name} - "
            f"{core_software_image.software_version.version} - "
            f"{core_software_image.image_file_name}"[:CHANGELOG_MAX_OBJECT_REPR],
            request_id=uuid.uuid4(),
        )


def _migrate_content_types(apps, old_ct, new_ct):
    ComputedField = apps.get_model("extras", "ComputedField")
    CustomField = apps.get_model("extras", "CustomField")
    CustomLink = apps.get_model("extras", "CustomLink")
    ExportTemplate = apps.get_model("extras", "ExportTemplate")
    JobButton = apps.get_model("extras", "JobButton")
    JobHook = apps.get_model("extras", "JobHook")
    Note = apps.get_model("extras", "Note")
    ObjectChange = apps.get_model("extras", "ObjectChange")
    ObjectPermission = apps.get_model("users", "ObjectPermission")
    Relationship = apps.get_model("extras", "Relationship")
    RelationshipAssociation = apps.get_model("extras", "RelationshipAssociation")
    Status = apps.get_model("extras", "Status")
    Tag = apps.get_model("extras", "Tag")
    TaggedItem = apps.get_model("extras", "TaggedItem")
    WebHook = apps.get_model("extras", "WebHook")

    # Migrate ComputedField content type
    ComputedField.objects.filter(content_type=old_ct).update(content_type=new_ct)

    # Migrate CustomField content type
    for cf in CustomField.objects.filter(content_types=old_ct):
        cf.content_types.add(new_ct)

    # Migrate CustomLink content type
    CustomLink.objects.filter(content_type=old_ct).update(content_type=new_ct)

    # Migrate ExportTemplate content type - skip git export templates
    ExportTemplate.objects.filter(content_type=old_ct, owner_content_type=None).update(content_type=new_ct)

    # Migrate JobButton content type
    for job_button in JobButton.objects.filter(content_types=old_ct):
        job_button.content_types.add(new_ct)

    # Migrate JobHook content type
    for job_hook in JobHook.objects.filter(content_types=old_ct):
        job_hook.content_types.add(new_ct)

    # Migrate Note content type
    Note.objects.filter(assigned_object_type=old_ct).update(assigned_object_type=new_ct)

    # Migrate ObjectChange content type
    ObjectChange.objects.filter(changed_object_type=old_ct).update(changed_object_type=new_ct)

    # Migrate ObjectPermission content type
    for object_permission in ObjectPermission.objects.filter(object_types=old_ct):
        object_permission.object_types.add(new_ct)

    # Migrate Relationship content type
    Relationship.objects.filter(source_type=old_ct).update(source_type=new_ct)
    Relationship.objects.filter(destination_type=old_ct).update(destination_type=new_ct)

    # Migration RelationshipAssociation content type
    RelationshipAssociation.objects.filter(source_type=old_ct).update(source_type=new_ct)
    RelationshipAssociation.objects.filter(destination_type=old_ct).update(destination_type=new_ct)

    # Migrate Status content type
    for status in Status.objects.filter(content_types=old_ct):
        status.content_types.add(new_ct)

    # Migrate Tag content type
    for tag in Tag.objects.filter(content_types=old_ct):
        tag.content_types.add(new_ct)

    # Migrate TaggedItem content type
    TaggedItem.objects.filter(content_type=old_ct).update(content_type=new_ct)

    # DLM forms are using a custom tag field that doesn't enforce content type. Fix that here if necessary.
    for tag_id in TaggedItem.objects.filter(content_type=new_ct).values_list("tag_id", flat=True).distinct():
        tag = Tag.objects.get(id=tag_id)
        if not tag.content_types.filter(id=new_ct.id).exists():
            tag.content_types.add(new_ct)

    # Migrate WebHook content type
    for web_hook in WebHook.objects.filter(content_types=old_ct):
        web_hook.content_types.add(new_ct)


def _migrate_hashing_algorithm(value):
    # Attempt to map the hashing algorithm to one of the valid choices for dcim.SoftwareImageFile
    similarity = {}
    for choice in dcim_choices.SoftwareImageFileHashingAlgorithmChoices.values():
        ratio = SequenceMatcher(lambda x: x not in ascii_letters + digits, value.lower(), choice.lower()).ratio()
        similarity.setdefault(ratio, []).append(choice)
    max_similarity = max(similarity.keys())

    # Only return values that are at least 80% similar to one of the valid choices, and only if there is a single best match
    if max_similarity > 0.8 and len(similarity[max_similarity]) == 1:
        return similarity[max_similarity][0]
    return ""


class Migration(migrations.Migration):
    dependencies = [
        ("dcim", "0056_softwareimage_m2m_and_device_fk"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("nautobot_device_lifecycle_mgmt", "0020_alter_created_tags"),
    ]

    operations = [
        migrations.RunPython(migrate_dlm_software_models_to_core, migrations.RunPython.noop),
    ]

from difflib import SequenceMatcher
from string import ascii_letters, digits
import uuid

from django.db import migrations

from nautobot.apps.choices import (
    ObjectChangeActionChoices,
    ObjectChangeEventContextChoices,
    SoftwareImageFileHashingAlgorithmChoices,
)
from nautobot.apps.models import serialize_object, serialize_object_v2, TagsManager
from nautobot.apps.utils import migrate_content_type_references_to_new_model
from nautobot.extras import models as extras_models
from nautobot.extras.constants import CHANGELOG_MAX_OBJECT_REPR

common_objectchange_request_id = uuid.uuid4()


def migrate_dlm_software_models_to_core(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    DLMSoftwareVersion = apps.get_model("nautobot_device_lifecycle_mgmt", "SoftwareLCM")
    DLMSoftwareImage = apps.get_model("nautobot_device_lifecycle_mgmt", "SoftwareImageLCM")
    CoreSoftwareVersion = apps.get_model("dcim", "SoftwareVersion")
    CoreSoftwareImage = apps.get_model("dcim", "SoftwareImageFile")
    Relationship = apps.get_model("extras", "Relationship")

    dlm_software_version_ct = ContentType.objects.get_for_model(DLMSoftwareVersion)
    dlm_software_image_ct = ContentType.objects.get_for_model(DLMSoftwareImage)
    core_software_version_ct = ContentType.objects.get_for_model(CoreSoftwareVersion)
    core_software_image_ct = ContentType.objects.get_for_model(CoreSoftwareImage)

    # Migrate content types for all related extras models
    migrate_content_type_references_to_new_model(apps, dlm_software_version_ct, core_software_version_ct)
    migrate_content_type_references_to_new_model(apps, dlm_software_image_ct, core_software_image_ct)

    # Migrate nautobot_device_lifecycle_mgmt.SoftwareLCM instances to dcim.SoftwareVersion
    for dlm_software_version in DLMSoftwareVersion.objects.all():
        _migrate_software_version(apps, dlm_software_version)

    # Migrate nautobot_device_lifecycle_mgmt.SoftwareImageLCM instances to dcim.SoftwareImageFile
    for dlm_software_image in DLMSoftwareImage.objects.all():
        _migrate_software_image(apps, dlm_software_image)

    # Delete DLM relationships from software to devices and inventory items
    Relationship.objects.filter(key="device_soft").delete()
    Relationship.objects.filter(key="inventory_item_soft").delete()

    # Delete DLM SoftwareLCM and SoftwareImageLCM instances
    DLMSoftwareImage.objects.all().delete()
    DLMSoftwareVersion.objects.all().delete()


def _migrate_hashing_algorithm(value):
    # Attempt to map the hashing algorithm to one of the valid choices for dcim.SoftwareImageFile
    similarity = {}
    for choice in SoftwareImageFileHashingAlgorithmChoices.values():
        # Use difflib.SequenceMatcher to compare the similarity of the hashing algorithm to the valid choices, ignoring case and punctuation
        # This returns a float between 0 and 1; 1 if the compared strings are identical, and 0 if they have nothing in common
        ratio = SequenceMatcher(lambda x: x not in ascii_letters + digits, value.lower(), choice.lower()).ratio()
        similarity.setdefault(ratio, []).append(choice)
    max_similarity = max(similarity.keys())

    # Only return values that are at least 80% similar to one of the valid choices, and only if there is a single best match
    if max_similarity > 0.8 and len(similarity[max_similarity]) == 1:
        return similarity[max_similarity][0]
    return ""


def _migrate_software_image(apps, dlm_software_image):
    ContentType = apps.get_model("contenttypes", "ContentType")
    CoreSoftwareImage = apps.get_model("dcim", "SoftwareImageFile")
    Device = apps.get_model("dcim", "Device")
    DLMSoftwareImage = apps.get_model("nautobot_device_lifecycle_mgmt", "SoftwareImageLCM")
    InventoryItem = apps.get_model("dcim", "InventoryItem")
    ObjectChange = apps.get_model("extras", "ObjectChange")
    Status = apps.get_model("extras", "Status")
    TaggedItem = apps.get_model("extras", "TaggedItem")

    core_software_image_ct = ContentType.objects.get_for_model(CoreSoftwareImage)
    dlm_software_image_ct = ContentType.objects.get_for_model(DLMSoftwareImage)
    device_ct = ContentType.objects.get_for_model(Device)
    inventory_item_ct = ContentType.objects.get_for_model(InventoryItem)

    status_active = Status.objects.get(name="Active")

    hashing_algorithm = _migrate_hashing_algorithm(dlm_software_image.hashing_algorithm)
    if dlm_software_image.hashing_algorithm != "" and hashing_algorithm == "":
        print(
            f"\n\nUnable to map hashing algorithm '{dlm_software_image.hashing_algorithm}' for software image "
            f"'{dlm_software_image.software.version} - {dlm_software_image.image_file_name}' ({dlm_software_image.id}). "
            "Please update the hashing algorithm manually."
        )

    core_software_image = CoreSoftwareImage(
        id=dlm_software_image.id,
        software_version_id=dlm_software_image.software.id,
        image_file_name=dlm_software_image.image_file_name,
        image_file_checksum=dlm_software_image.image_file_checksum,
        hashing_algorithm=hashing_algorithm,
        download_url=dlm_software_image.download_url,
        default_image=dlm_software_image.default_image,
        status=status_active,  # DLM model lacks a status field so we default to active
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

    # Map the DLM object_tags to inventory items and set the InventoryItem.software_image_files m2m field
    inventory_item_pks = (
        TaggedItem.objects.filter(tag__in=dlm_software_image.object_tags.all(), content_type=inventory_item_ct)
        .values_list("object_id")
        .distinct()
    )
    for inventory_item in InventoryItem.objects.filter(pk__in=inventory_item_pks):
        inventory_item.software_image_files.add(core_software_image)

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
        action=ObjectChangeActionChoices.ACTION_UPDATE,
        change_context=ObjectChangeEventContextChoices.CONTEXT_ORM,
        change_context_detail="Migrated from Nautobot App Device Lifecycle Management",
        changed_object_id=core_software_image.id,
        changed_object_type=core_software_image_ct,
        object_data=serialize_object(core_software_image),
        object_data_v2=serialize_object_v2(core_software_image),
        object_repr=f"{core_software_image.software_version.platform.name} - "
        f"{core_software_image.software_version.version} - "
        f"{core_software_image.image_file_name}"[:CHANGELOG_MAX_OBJECT_REPR],
        related_object_id=dlm_software_image.id,
        related_object_type=dlm_software_image_ct,
        request_id=common_objectchange_request_id,
        user=None,
        user_name="Undefined",
    )


def _migrate_software_version(apps, dlm_software_version):
    ContentType = apps.get_model("contenttypes", "ContentType")
    CoreSoftwareVersion = apps.get_model("dcim", "SoftwareVersion")
    Device = apps.get_model("dcim", "Device")
    DLMSoftwareVersion = apps.get_model("nautobot_device_lifecycle_mgmt", "SoftwareLCM")
    ObjectChange = apps.get_model("extras", "ObjectChange")
    Status = apps.get_model("extras", "Status")
    InventoryItem = apps.get_model("dcim", "InventoryItem")
    RelationshipAssociation = apps.get_model("extras", "RelationshipAssociation")

    core_software_version_ct = ContentType.objects.get_for_model(CoreSoftwareVersion)
    device_ct = ContentType.objects.get_for_model(Device)
    dlm_software_version_ct = ContentType.objects.get_for_model(DLMSoftwareVersion)
    inventory_item_ct = ContentType.objects.get_for_model(InventoryItem)

    status_active = Status.objects.get(name="Active")

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
        status=status_active,  # DLM model lacks a status field so we default to active
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

    core_software_version.refresh_from_db()

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
        action=ObjectChangeActionChoices.ACTION_UPDATE,
        change_context=ObjectChangeEventContextChoices.CONTEXT_ORM,
        change_context_detail="Migrated from Nautobot App Device Lifecycle Management",
        changed_object_id=core_software_version.id,
        changed_object_type=core_software_version_ct,
        object_data=serialize_object(core_software_version),
        object_data_v2=serialize_object_v2(core_software_version),
        object_repr=f"{core_software_version.platform.name} - {core_software_version.version}"[
            :CHANGELOG_MAX_OBJECT_REPR
        ],
        related_object_id=dlm_software_version.id,
        related_object_type=dlm_software_version_ct,
        request_id=common_objectchange_request_id,
        user=None,
        user_name="Undefined",
    )


class Migration(migrations.Migration):
    dependencies = [
        ("dcim", "0055_softwareimage_softwareversion_data_migration"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("extras", "0057_jobbutton"),
        ("nautobot_device_lifecycle_mgmt", "0020_alter_created_tags"),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(migrate_dlm_software_models_to_core, migrations.RunPython.noop),
    ]

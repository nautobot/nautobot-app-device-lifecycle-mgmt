from django.core.exceptions import ValidationError
from django.db import migrations
from django.db.models import Q


def verify_dlm_models_migated_to_core(apps, schema_editor):
    """Verifies whether the objects for the following DLM models have been migrated to the corresponding Core models
    DLM SoftwareLCM -> Core SoftwareVersion
    DLM SoftwareImageLCM -> Core SoftwareImageFile
    DLM Contact -> Core Contact
    """
    ContentType = apps.get_model("contenttypes", "ContentType")
    DLMContact = apps.get_model("nautobot_device_lifecycle_mgmt", "ContactLCM")
    DLMSoftwareVersion = apps.get_model("nautobot_device_lifecycle_mgmt", "SoftwareLCM")
    DLMSoftwareImage = apps.get_model("nautobot_device_lifecycle_mgmt", "SoftwareImageLCM")
    CoreContact = apps.get_model("extras", "Contact")
    CoreSoftwareVersion = apps.get_model("dcim", "SoftwareVersion")
    CoreSoftwareImage = apps.get_model("dcim", "SoftwareImageFile")

    dlm_contact_ct = ContentType.objects.get_for_model(DLMContact)
    dlm_software_version_ct = ContentType.objects.get_for_model(DLMSoftwareVersion)
    dlm_software_image_ct = ContentType.objects.get_for_model(DLMSoftwareImage)
    core_contact_ct = ContentType.objects.get_for_model(CoreContact)
    core_software_version_ct = ContentType.objects.get_for_model(CoreSoftwareVersion)
    core_software_image_ct = ContentType.objects.get_for_model(CoreSoftwareImage)

    # Verify nautobot_device_lifecycle_mgmt.SoftwareLCM instances were migrated to dcim.SoftwareVersion
    for dlm_software_version in DLMSoftwareVersion.objects.all():
        _verify_software_version_migrated(apps, dlm_software_version)
    _verify_content_type_references_migrated_to_new_model(apps, dlm_software_version_ct, core_software_version_ct)

    # Verify nautobot_device_lifecycle_mgmt.SoftwareImageLCM instances were migrated to dcim.SoftwareImageFile
    for dlm_software_image in DLMSoftwareImage.objects.all():
        _verify_software_image_migrated(apps, dlm_software_image)
    _verify_content_type_references_migrated_to_new_model(apps, dlm_software_image_ct, core_software_image_ct)

    # Verify nautobot_device_lifecycle_mgmt.ContactLCM instances were migrated to extras.Contact
    for dlm_contact in DLMContact.objects.all():
        _verify_contact_migrated(apps, dlm_contact)
    _verify_content_type_references_migrated_to_new_model(apps, dlm_contact_ct, core_contact_ct)


def _verify_software_version_migrated(apps, dlm_software_version):
    """Verifies instances of DLM SoftwareLCM were migrated to Core SoftwareVersion."""
    CoreSoftwareVersion = apps.get_model("dcim", "SoftwareVersion")

    core_software_version_q = CoreSoftwareVersion.objects.filter(
        platform=dlm_software_version.device_platform, version=dlm_software_version.version
    )
    if not core_software_version_q.exists():
        raise ValidationError(
            f"DLM Migration Error: Did not find Core SoftwareVersion object matching DLM Software object: {dlm_software_version}"
        )
    return


def _verify_software_image_migrated(apps, dlm_software_image):
    """Verifies instances of DLM SoftwareImageLCM were migrated to Core SoftwareImageFile."""
    SoftwareVersion = apps.get_model("dcim", "SoftwareVersion")
    SoftwareImageFile = apps.get_model("dcim", "SoftwareImageFile")

    dlm_software_version = dlm_software_image.software
    core_software_version_q = SoftwareVersion.objects.filter(
        platform=dlm_software_version.device_platform, version=dlm_software_version.version
    )
    if not core_software_version_q.exists():
        raise ValidationError(
            f"DLM Migration Error: Did not find Core SoftwareVersion matching DLM SoftwareVersion on DLM SoftwareImage object: {dlm_software_image}"
        )
    core_software_image_q = SoftwareImageFile.objects.filter(
        image_file_name=dlm_software_image.image_file_name, software_version=core_software_version_q.first()
    )
    if not core_software_image_q.exists():
        raise ValidationError(
            f"DLM Migration Error: Did not find Core SoftwareImage object matching DLM SoftwareImage object: {dlm_software_image}"
        )
    return


def _verify_contact_migrated(apps, dlm_contact):
    """Verifies instances of DLM Contact were migrated to Core Contact."""
    CoreContact = apps.get_model("extras", "Contact")

    core_contact_q = CoreContact.objects.filter(name=dlm_contact.name, phone=dlm_contact.phone, email=dlm_contact.email)
    if not core_contact_q.exists():
        raise ValidationError(
            f"DLM Migration Error: Did not find Core Contact object matching DLM Contact object: {dlm_contact}"
        )
    return


def _verify_content_type_references_migrated_to_new_model(apps, old_ct, new_ct):
    """Verify Nautobot extension objects and relationships linked to deprecated DLM models were migrated."""
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

    old_ct_computed_fields = ComputedField.objects.filter(content_type=old_ct)
    for computed_field in old_ct_computed_fields:
        print(
            f"Migration error. The Computed Field '{computed_field.label}' has not been migrated to the new model '{str(new_ct)}'"
        )
    if old_ct_computed_fields.exists():
        raise ValidationError(
            f"DLM Migration Error: Found computed fields that have not been migrated from DLM to Core model: {old_ct_computed_fields}."
        )

    # Migrate CustomField content type
    old_ct_custom_fields = CustomField.objects.filter(content_types=old_ct).exclude(content_types=new_ct)
    for custom_field in old_ct_custom_fields:
        print(
            f"Migration error. The Custom Field '{custom_field.label}' has not been migrated to Core model '{str(new_ct)}'"
        )
    if old_ct_custom_fields.exists():
        raise ValidationError(
            f"DLM Migration Error: Found custom fields that have not been migrated from DLM to Core model: {old_ct_custom_fields}."
        )

    # Migrate CustomLink content type
    old_ct_custom_links = CustomLink.objects.filter(content_type=old_ct)
    for custom_link in old_ct_custom_links:
        print(
            f"Migration error. The Custom Link '{custom_link.name}' has not been migrated to Core model '{str(new_ct)}'"
        )
    if old_ct_custom_links.exists():
        raise ValidationError(
            f"DLM Migration Error: Found custom links that have not been migrated from DLM to Core model: {old_ct_custom_links}."
        )

    # Migrate ExportTemplate content type - skip git export templates
    old_ct_export_templates = ExportTemplate.objects.filter(content_type=old_ct, owner_content_type=None)
    for export_template in old_ct_export_templates:
        print(
            f"Migration error. The Export Template '{export_template.name}' has not been migrated to Core model '{str(new_ct)}'"
        )
    if old_ct_export_templates.exists():
        raise ValidationError(
            f"DLM Migration Error: Found export templates that have not been migrated from DLM to Core model: {old_ct_export_templates}."
        )

    # Migrate JobButton content type
    old_ct_job_buttons = JobButton.objects.filter(content_types=old_ct).exclude(content_types=new_ct)
    for job_button in old_ct_job_buttons:
        print(
            f"Migration error. The Job Button '{job_button.name}' has not been migrated to Core model '{str(new_ct)}'"
        )
    if old_ct_job_buttons.exists():
        raise ValidationError(
            f"DLM Migration Error: Found job buttons that have not been migrated from DLM to Core model: {old_ct_job_buttons}."
        )

    # Migrate JobHook content type
    old_ct_job_hooks = JobHook.objects.filter(content_types=old_ct).exclude(content_types=new_ct)
    for job_hook in old_ct_job_hooks:
        print(f"Migration error. The Job Hook '{job_hook.name}' has not been migrated to Core model '{str(new_ct)}'")
    if old_ct_job_hooks.exists():
        raise ValidationError(
            f"DLM Migration Error: Found job hooks that have not been migrated from DLM to Core model: {old_ct_job_hooks}."
        )

    # Migrate Note content type
    old_ct_notes = Note.objects.filter(assigned_object_type=old_ct)
    for note in old_ct_notes:
        print(f"Migration error.The Note '{str(note)}' has not been migrated to Core model '{str(new_ct)}'")
    if old_ct_notes.exists():
        raise ValidationError(
            f"DLM Migration Error: Found notes that have not been migrated from DLM to Core model: {old_ct_notes}."
        )

    # Migrate ObjectChange content type
    old_ct_object_changes = ObjectChange.objects.filter(changed_object_type=old_ct)
    for object_change in old_ct_object_changes:
        print(
            f"Migration error. The ObjectChange {str(object_change)} has not been migrated to Core model '{str(new_ct)}'"
        )
    if old_ct_object_changes.exists():
        raise ValidationError(
            f"DLM Migration Error: Found object changes that have not been migrated from DLM to Core model: {old_ct_object_changes}."
        )

    # Migrate Status content type
    old_ct_statuses = Status.objects.filter(content_types=old_ct).exclude(content_types=new_ct)
    for status in old_ct_statuses:
        print(f"Migration error. The Status '{status.name}' has not been migrated to Core model '{str(new_ct)}'")
    if old_ct_statuses.exists():
        raise ValidationError(
            f"DLM Migration Error: Found statuses that have not been migrated from DLM to Core model: {old_ct_statuses}."
        )

    # Migrate Tag content type
    old_ct_tags = Tag.objects.filter(content_types=old_ct).exclude(content_types=new_ct)
    for tag in old_ct_tags:
        print(f"Migration error. The Tag '{tag.name}' has not been migrated to Core model '{str(new_ct)}'")
    if old_ct_tags.exists():
        raise ValidationError(
            f"DLM Migration Error: Found tags that have not been migrated from DLM to Core model: {old_ct_tags}."
        )

    # Migrate TaggedItem content type
    old_ct_tagged_items = TaggedItem.objects.filter(content_type=old_ct)
    for tagged_item in old_ct_tagged_items:
        print(
            f"Migration error. The Tagged Item '{str(tagged_item)}' has not been migrated to Core model '{str(new_ct)}'"
        )
    if old_ct_tagged_items.exists():
        raise ValidationError(
            f"DLM Migration Error: Found tagged items that have not been migrated from DLM to Core model: {old_ct_tagged_items}."
        )

    # Migrate WebHook content type
    old_ct_web_hooks = WebHook.objects.filter(content_types=old_ct).exclude(content_types=new_ct)
    for web_hook in old_ct_web_hooks:
        print(f"Migration error. The Web Hook '{web_hook.name}' has not been migrated to Core model '{str(new_ct)}'")
    if old_ct_web_hooks.exists():
        raise ValidationError(
            f"DLM Migration Error: Found web hooks that have not been migrated from DLM to Core model: {old_ct_web_hooks}."
        )

    # Migrate ObjectPermission content type
    old_ct_permissions = ObjectPermission.objects.filter(object_types=old_ct).exclude(object_types=new_ct)
    for object_permission in old_ct_permissions:
        print(
            f"Migration error. The Object Permission '{str(object_permission)}' has not been migrated to Core model '{str(new_ct)}'",
        )
    if old_ct_permissions.exists():
        raise ValidationError(
            f"DLM Migration Error: Found object permissions that have not been migrated from DLM to Core models: {old_ct_permissions}."
        )

    # These are migrated separately as they follow specific business logic
    excluded_relationships = ("device_soft", "inventory_item_soft")
    old_ct_relationships = Relationship.objects.filter(
        ~Q(key__in=excluded_relationships) & (Q(source_type=old_ct) | Q(destination_type=old_ct))
    )
    for relationship in old_ct_relationships:
        print(
            f"Migration error. The Relationship '{relationship.label}' has not been migrated to Core model '{str(new_ct)}'"
        )

        old_ct_relationship_assoc_src = RelationshipAssociation.objects.filter(
            source_type=old_ct, relationship=relationship
        )
        for relationship_association in old_ct_relationship_assoc_src:
            print(
                f"Migration error. The Relationship Association '{str(relationship_association)}' has not been migrated to Core model '{str(new_ct)}'"
            )
        old_ct_relationship_assoc_src = RelationshipAssociation.objects.filter(
            source_type=old_ct, relationship=relationship
        )
        if old_ct_relationship_assoc_src:
            raise ValidationError(
                f"DLM Migration Error: Found relationship associations that have not been migrated from DLM to Core model: {old_ct_relationship_assoc_src}."
            )

        old_ct_relationship_assoc_dst = RelationshipAssociation.objects.filter(
            destination_type=old_ct, relationship=relationship
        )
        for relationship_association in old_ct_relationship_assoc_dst:
            print(
                f"Migration error. The Relationship Association '{str(relationship_association)}' has not been migrated to Core model '{str(new_ct)}'"
            )
        if old_ct_relationship_assoc_dst:
            raise ValidationError(
                f"DLM Migration Error: Found relationship associations that have not been migrated from DLM to Core models: {old_ct_relationship_assoc_dst}."
            )
    if old_ct_relationships.exists():
        raise ValidationError(
            f"DLM Migration Error: Found relationships that have not been migrated from DLM to Core model: {old_ct_relationships}."
        )


class Migration(migrations.Migration):
    dependencies = [
        ("dcim", "0055_softwareimage_softwareversion_data_migration"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("extras", "0057_jobbutton"),
        ("nautobot_device_lifecycle_mgmt", "0023_cvelcm_affected_softwares_tmp_and_more"),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(code=verify_dlm_models_migated_to_core, reverse_code=migrations.RunPython.noop),
    ]

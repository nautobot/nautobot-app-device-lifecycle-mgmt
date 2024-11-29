from difflib import SequenceMatcher
from string import ascii_letters, digits

from django.core.exceptions import ValidationError
from django.db import migrations
from django.db.models import Q
from nautobot.apps.choices import (
    SoftwareImageFileHashingAlgorithmChoices,
)


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
    ContentType = apps.get_model("contenttypes", "ContentType")
    CoreSoftwareVersion = apps.get_model("dcim", "SoftwareVersion")
    Device = apps.get_model("dcim", "Device")
    DLMSoftwareVersion = apps.get_model("nautobot_device_lifecycle_mgmt", "SoftwareLCM")
    InventoryItem = apps.get_model("dcim", "InventoryItem")
    RelationshipAssociation = apps.get_model("extras", "RelationshipAssociation")
    Tag = apps.get_model("extras", "Tag")

    device_ct = ContentType.objects.get_for_model(Device)
    dlm_software_version_ct = ContentType.objects.get_for_model(DLMSoftwareVersion)
    inventory_item_ct = ContentType.objects.get_for_model(InventoryItem)

    dlm_software_version_id = str(dlm_software_version.id)
    TaggedItem = apps.get_model("extras", "TaggedItem")
    try:
        # DLM_migration-SoftwareLCM__{UUID} tag is created by migration job in DLM 2.3
        tag = Tag.objects.get(name=f"DLM_migration-SoftwareLCM__{dlm_software_version_id}")
        tagged_software = TaggedItem.objects.get(tag=tag)
        core_software_version = CoreSoftwareVersion.objects.get(id=tagged_software.object_id)
    except (TaggedItem.DoesNotExist, Tag.DoesNotExist, CoreSoftwareVersion.DoesNotExist):
        raise ValidationError(
            f"DLM Migration Error: Could not find Core SoftwareVersion matching DLM Software object: {dlm_software_version}"
        )
    except TaggedItem.MultipleObjectsReturned:
        raise ValidationError(
            f"DLM Migration Error: Found multiple Core SoftwareVersion objects matching DLM Software object: {dlm_software_version}"
        )

    # Ensure we are linked to one DLM Software only
    try:
        TaggedItem.objects.get(object_id=core_software_version.id, tag__name__istartswith="DLM_migration-SoftwareLCM__")
    except TaggedItem.MultipleObjectsReturned:
        raise ValidationError(
            f"DLM Migration Error: Found multiple DLM Software objects attached to Core SoftwareVersion: {core_software_version}"
        )

    # Compare attributes between Software in Core and DLM
    dlm_soft_attrs = {
        "alias": dlm_software_version.alias,
        "release_date": dlm_software_version.release_date,
        "end_of_support_date": dlm_software_version.end_of_support,
        "documentation_url": dlm_software_version.documentation_url,
        "long_term_support": dlm_software_version.long_term_support,
        "pre_release": dlm_software_version.pre_release,
    }

    attrs_diff = {}
    for attr_name, dlm_attr_value in dlm_soft_attrs.items():
        core_attr_value = getattr(core_software_version, attr_name)
        if core_attr_value == dlm_attr_value:
            continue
        attrs_diff[attr_name] = {
            "dlm_value": dlm_attr_value,
            "core_value": core_attr_value,
        }

    for dlm_cf_key, dlm_cf_value in dlm_software_version._custom_field_data.items():
        # We set a synthetic value if Core side doesn't have given custom field
        core_cf_value = core_software_version._custom_field_data.get(
            dlm_cf_key, f"Custom Field {dlm_cf_key} does not exist."
        )
        if core_cf_value != dlm_cf_value:
            attrs_diff.setdefault("_custom_field_data", {}).setdefault("dlm_value", {})[dlm_cf_key] = dlm_cf_value
            attrs_diff.setdefault("_custom_field_data", {}).setdefault("core_value", {})[dlm_cf_key] = core_cf_value

    if attrs_diff:
        raise ValidationError(
            f"DLM Migration Error: Attributes values differ between DLM Software {dlm_software_version} and Core SoftwareVersion {core_software_version}: {attrs_diff}"
        )

    # Verify 'device_soft' and 'inventory_item_soft' relationships were migrated
    for relationship_association in RelationshipAssociation.objects.filter(
        relationship__key="device_soft",
        source_type=dlm_software_version_ct,
        source_id=dlm_software_version.id,
        destination_type=device_ct,
    ):
        device = Device.objects.get(id=relationship_association.destination_id)
        existing_device_software = device.software_version
        if existing_device_software and existing_device_software != core_software_version:
            raise ValidationError(
                f"Device {device} has Core SoftwareVersion {existing_device_software} assigned but its DLM Software {dlm_software_version} assignment is different."
            )
        elif not existing_device_software:
            raise ValidationError(
                f"Device {device} has no Core SoftwareVersion assigned but it has an existing DLM Software {dlm_software_version} assignment."
            )

    for relationship_association in RelationshipAssociation.objects.filter(
        relationship__key="inventory_item_soft",
        source_type=dlm_software_version_ct,
        source_id=dlm_software_version.id,
        destination_type=inventory_item_ct,
    ):
        inventory_item = InventoryItem.objects.get(id=relationship_association.destination_id)
        existing_invitem_software = inventory_item.software_version
        if existing_invitem_software and inventory_item.software_version != core_software_version:
            raise ValidationError(
                f"Inventory Item {inventory_item} has Core SoftwareVersion {existing_invitem_software} assigned but its DLM Software {dlm_software_version} assignment is different."
            )
        elif not existing_invitem_software:
            raise ValidationError(
                f"Inventory Item {inventory_item} has no Core SoftwareVersion assigned but it has an existing DLM Software {dlm_software_version} assignment."
            )


def _map_hashing_algorithm(value):
    """Map DLM SoftwareImage hashing algorithm from free-text field to Core SoftwareImageFile choice."""
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


def _verify_software_image_migrated(apps, dlm_software_image):
    """Verifies instances of DLM SoftwareImageLCM were migrated to Core SoftwareImageFile."""
    ContentType = apps.get_model("contenttypes", "ContentType")
    CoreSoftwareImage = apps.get_model("dcim", "SoftwareImageFile")
    Device = apps.get_model("dcim", "Device")
    DeviceType = apps.get_model("dcim", "DeviceType")
    InventoryItem = apps.get_model("dcim", "InventoryItem")
    SoftwareVersion = apps.get_model("dcim", "SoftwareVersion")
    SoftwareImageFile = apps.get_model("dcim", "SoftwareImageFile")
    Tag = apps.get_model("extras", "Tag")
    TaggedItem = apps.get_model("extras", "TaggedItem")

    device_ct = ContentType.objects.get_for_model(Device)
    inventory_item_ct = ContentType.objects.get_for_model(InventoryItem)

    dlm_software_image_id = str(dlm_software_image.id)
    try:
        tag = Tag.objects.get(name=f"DLM_migration-SoftwareImageLCM__{dlm_software_image_id}")
        tagged_software_image = TaggedItem.objects.get(tag=tag)
        core_software_image = CoreSoftwareImage.objects.get(id=tagged_software_image.object_id)
    except (TaggedItem.DoesNotExist, Tag.DoesNotExist, CoreSoftwareImage.DoesNotExist):
        raise ValidationError(
            f"DLM Migration Error: Could not find Core SoftwareImageFile matching DLM SoftwareImage object: {dlm_software_image}"
        )
    except TaggedItem.MultipleObjectsReturned:
        raise ValidationError(
            f"DLM Migration Error: Found multiple Core SoftwareImageFile objects matching DLM SoftwareImage object: {dlm_software_image}"
        )

    # Ensure we are linked to one DLM Software Image only
    try:
        TaggedItem.objects.get(
            object_id=core_software_image.id, tag__name__istartswith="DLM_migration-SoftwareImageLCM__"
        )
    except TaggedItem.MultipleObjectsReturned:
        raise ValidationError(
            f"DLM Migration Error: Found multiple DLM SoftwareImage objects attached to Core SoftwareImageFile: {core_software_image}"
        )

    # Compare attributes between SoftwareImage in Core and DLM
    dlm_soft_img_attrs = (
        "image_file_checksum",
        "download_url",
        "default_image",
    )

    attrs_diff = {}
    for attr_name in dlm_soft_img_attrs:
        dlm_attr_value = getattr(dlm_software_image, attr_name)
        core_attr_value = getattr(core_software_image, attr_name)
        if core_attr_value == dlm_attr_value:
            continue
        attrs_diff[attr_name] = {
            "dlm_value": dlm_attr_value,
            "core_value": core_attr_value,
        }

    for dlm_cf_key, dlm_cf_value in dlm_software_image._custom_field_data.items():
        # We set a synthetic value if Core side doesn't have given custom field
        core_cf_value = core_software_image._custom_field_data.get(
            dlm_cf_key, f"Custom Field {dlm_cf_key} does not exist."
        )
        if core_cf_value != dlm_cf_value:
            attrs_diff.setdefault("_custom_field_data", {}).setdefault("dlm_value", {})[dlm_cf_key] = dlm_cf_value
            attrs_diff["_custom_field_data"].setdefault("core_value", {})[dlm_cf_key] = core_cf_value

    # Hashing algorithm is mapped from free-text in DLM to fixed choice in Core. Migration sets `dlm-migration-manual-hash` tag if that can't be done automatically.
    if dlm_software_image.hashing_algorithm != "":
        hashing_algorithm = _map_hashing_algorithm(dlm_software_image.hashing_algorithm)
    else:
        hashing_algorithm = ""

    if (
        hashing_algorithm != core_software_image.hashing_algorithm
        and not core_software_image.tags.filter(name="dlm-migration-manual-hash").exists()
    ):
        attrs_diff.setdefault("hashing_algorithm", {})["dlm_value"] = hashing_algorithm
        attrs_diff["hashing_algorithm"]["core_value"] = core_software_image.hashing_algorithm

    if attrs_diff:
        raise ValidationError(
            f"DLM Migration Error: Attribute values differ between DLM SoftwareImage {dlm_software_image} and Core SoftwareImageFile {core_software_image}: {attrs_diff}"
        )

    dtypes_in_dlm_not_in_core = set(dlm_software_image.device_types.all()) - set(core_software_image.device_types.all())
    if dtypes_in_dlm_not_in_core:
        raise ValidationError(
            f"Core SoftwareImageFile {core_software_image} is missing DLM SoftwareImage DeviceType assignments {dtypes_in_dlm_not_in_core}"
        )

    # Verify the DLM object_tags were migrated to the Device.software_image_files m2m field
    device_pks = (
        TaggedItem.objects.filter(tag__in=dlm_software_image.object_tags.all(), content_type=device_ct)
        .values_list("object_id")
        .distinct()
    )
    for device in Device.objects.filter(pk__in=device_pks):
        if core_software_image not in device.software_image_files.all():
            raise ValidationError(f"Device {device} is missing SoftwareImage {core_software_image} assignment.")

    # Verify the DLM object_tags were migrated to the InventoryItem.software_image_files m2m field
    inventory_item_pks = (
        TaggedItem.objects.filter(
            tag__in=dlm_software_image.object_tags.all(),
            content_type=inventory_item_ct,
        )
        .values_list("object_id")
        .distinct()
    )
    for inventory_item in InventoryItem.objects.filter(pk__in=inventory_item_pks):
        if core_software_image not in inventory_item.software_image_files.all():
            raise ValidationError(
                f"InventoryItem {inventory_item} is missing SoftwareImage {core_software_image} assignment."
            )

    # Verify devices that have software assigned have also corresponding software image file
    for software_id, device_type_id in (
        Device.objects.filter(software_version__isnull=False)
        .order_by()
        .values_list("software_version", "device_type")
        .distinct()
    ):
        if SoftwareImageFile.objects.filter(software_version=software_id, device_types=device_type_id).exists():
            continue
        software_version = SoftwareVersion.objects.get(id=software_id)
        device_type = DeviceType.objects.get(id=device_type_id)
        ValidationError(
            f"Found SoftwareVersion {software_version} assigned to Device that doesn't have a SoftwareImageFile matching DeviceType {device_type}."
        )


def _verify_contact_migrated(apps, dlm_contact):
    """Verifies instances of DLM Contact were migrated to Core Contact."""
    ContactAssociation = apps.get_model("extras", "ContactAssociation")
    ContentType = apps.get_model("contenttypes", "ContentType")
    ContractLCM = apps.get_model("nautobot_device_lifecycle_mgmt", "ContractLCM")
    CoreContact = apps.get_model("extras", "Contact")
    Role = apps.get_model("extras", "Role")
    Tag = apps.get_model("extras", "Tag")
    TaggedItem = apps.get_model("extras", "TaggedItem")

    dlm_contract_ct = ContentType.objects.get_for_model(ContractLCM)

    dlm_contact_id = str(dlm_contact.id)
    try:
        tag = Tag.objects.get(name=f"DLM_migration-ContactLCM__{dlm_contact_id}")
        tagged_contact = TaggedItem.objects.get(tag=tag)
        core_contact = CoreContact.objects.get(id=tagged_contact.object_id)
    except (TaggedItem.DoesNotExist, CoreContact.DoesNotExist, Tag.DoesNotExist):
        raise ValidationError(
            f"DLM Migration Error: Could not find Core Contact matching DLM Contact object: {dlm_contact}"
        )
    except TaggedItem.MultipleObjectsReturned:
        raise ValidationError(
            f"DLM Migration Error: Found multiple Core Contact objects matching DLM Contact object: {dlm_contact}"
        )

    # Ensure we are linked to one DLM Contact only
    try:
        TaggedItem.objects.get(object_id=core_contact.id, tag__name__istartswith="DLM_migration-ContactLCM__")
    except TaggedItem.MultipleObjectsReturned:
        raise ValidationError(
            f"DLM Migration Error: Found multiple DLM Contact objects attached to Core Contact: {core_contact}"
        )

    # Compare attributes between Contact in Core and DLM
    dlm_soft_img_attrs = (
        "address",
        "comments",
    )

    attrs_diff = {}
    for attr_name in dlm_soft_img_attrs:
        dlm_attr_value = getattr(dlm_contact, attr_name)
        core_attr_value = getattr(core_contact, attr_name)
        if core_attr_value == dlm_attr_value:
            continue
        attrs_diff[attr_name] = {
            "dlm_value": dlm_attr_value,
            "core_value": core_attr_value,
        }

    for dlm_cf_key, dlm_cf_value in dlm_contact._custom_field_data.items():
        # We set a synthetic value if Core side doesn't have given custom field
        core_cf_value = core_contact._custom_field_data.get(dlm_cf_key, f"Custom Field {dlm_cf_key} does not exist.")
        if core_cf_value != dlm_cf_value:
            attrs_diff.setdefault("_custom_field_data", {}).setdefault("dlm_value", {})[dlm_cf_key] = dlm_cf_value
            attrs_diff["_custom_field_data"].setdefault("core_value", {})[dlm_cf_key] = core_cf_value

    if attrs_diff:
        raise ValidationError(
            f"DLM Migration Error: Attribute values differ between DLM Contact {dlm_contact} and Core Contact {core_contact}: {attrs_diff}"
        )

    # Verify contact association role was migrated
    try:
        contact_association_role = Role.objects.get(name=dlm_contact.type)
    except Role.DoesNotExist:
        raise ValidationError(
            f"Contact Association Role {dlm_contact.type}, linked to {dlm_contact}, was not migrated."
        )

    # Verify contact to contract association was migrated
    try:
        ContactAssociation.objects.get(
            contact=core_contact,
            associated_object_id=dlm_contact.contract.id,
            associated_object_type=dlm_contract_ct,
            role=contact_association_role,
        )
    except ContactAssociation.DoesNotExist:
        raise ValidationError(
            f"Contact Association between Core Contact {core_contact} and DLM Contract {dlm_contact.contract} was not migrated."
        )


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
        ("nautobot_device_lifecycle_mgmt", "0022_alter_softwareimagelcm_inventory_items_and_more"),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(code=verify_dlm_models_migated_to_core, reverse_code=migrations.RunPython.noop),
    ]

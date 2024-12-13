# pylint: disable=logging-not-lazy, consider-using-f-string
"""Jobs for the Lifecycle Management app."""

import uuid
from difflib import SequenceMatcher
from string import ascii_letters, digits

from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from nautobot.apps.choices import (
    ObjectChangeActionChoices,
    ObjectChangeEventContextChoices,
    SoftwareImageFileHashingAlgorithmChoices,
)
from nautobot.apps.models import serialize_object, serialize_object_v2
from nautobot.dcim.models import Device, DeviceType, InventoryItem, SoftwareImageFile, SoftwareVersion
from nautobot.extras.constants import CHANGELOG_MAX_OBJECT_REPR
from nautobot.extras.jobs import BooleanVar, DryRunVar, Job
from nautobot.extras.models import (
    ComputedField,
    Contact,
    ContactAssociation,
    CustomField,
    CustomLink,
    ExportTemplate,
    JobButton,
    JobHook,
    Note,
    ObjectChange,
    Relationship,
    RelationshipAssociation,
    Role,
    Status,
    Tag,
    TaggedItem,
    Webhook,
)
from nautobot.users.models import ObjectPermission

from nautobot_device_lifecycle_mgmt.models import (
    CVELCM,
    ContactLCM,
    ContractLCM,
    DeviceSoftwareValidationResult,
    InventoryItemSoftwareValidationResult,
    SoftwareImageLCM,
    SoftwareLCM,
    ValidatedSoftwareLCM,
    VulnerabilityLCM,
)

common_objectchange_request_id = uuid.uuid4()

name = "DLM Models -> Nautobot Core Models Migration"  # pylint: disable=invalid-name


class DLMToNautoboCoreModelMigration(Job):
    """Utility migrating DLM models ContactLCM, SoftwareLCM and SoftwareImageLCM to Nautobot Core (2.2.0+)."""

    dryrun = DryRunVar(description="Enable for reporting mode.")
    hide_changelog_migrations = BooleanVar(
        label="Hide ChangeLog migration messages",
        description="Don't display log messages related to ChangeLog object migrations.",
    )
    update_core_to_match_dlm = BooleanVar(
        label="Update Core to match DLM",
        description="Forcibly update existing Core objects to match DLM objects.",
    )
    remove_dangling_relationships = BooleanVar(
        label="Remove dangling relationship associations",
        description="Remove DLM relationship associations where one side refers to the object that is gone.",
    )
    debug = BooleanVar(label="Show debug messages")

    class Meta:
        """Meta class for the job."""

        name = "Device Lifecycle Management to Nautobot Core Model Migration"
        description = "Migrates DLM models ContactLCM, SoftwareLCM and SoftwareImageLCM to Nautobot Core."
        read_only = False
        dryrun_default = True
        has_sensitive_variables = False

    def run(
        self, dryrun, hide_changelog_migrations, update_core_to_match_dlm, remove_dangling_relationships, debug
    ) -> None:  # pylint: disable=arguments-differ
        """Migration logic."""
        self.dryrun = dryrun
        self.debug = debug
        self.update_core_to_match_dlm = update_core_to_match_dlm
        self.hide_changelog_migrations = hide_changelog_migrations
        self.remove_corrupted_relationships = remove_dangling_relationships

        self.softlcm_ct_str = str(ContentType.objects.get_for_model(SoftwareLCM))
        self.softimglcm_ct_str = str(ContentType.objects.get_for_model(SoftwareImageLCM))
        self.contactlcm_ct_str = str(ContentType.objects.get_for_model(ContactLCM))
        self.dlm_to_core_id_map = {
            self.softlcm_ct_str: {},
            self.softimglcm_ct_str: {},
            self.contactlcm_ct_str: {},
        }

        self.migrate_dlm_models_to_core()

    def _update_migrated_dlm_object_ids(self):
        """Updates DLM object ID to Core object ID mappings for already migrated objects."""
        for contact in Contact.objects.filter(tags__name__istartswith="DLM_migration-ContactLCM__"):
            dlm_contact_id = (
                contact.tags.filter(name__istartswith="DLM_migration-ContactLCM__")
                .first()
                .name.strip("DLM_migration-ContactLCM__")
            )
            if dlm_contact_id not in self.dlm_to_core_id_map[self.contactlcm_ct_str]:
                self.dlm_to_core_id_map[self.contactlcm_ct_str][dlm_contact_id] = str(contact.id)
        for software_version in SoftwareVersion.objects.filter(tags__name__istartswith="DLM_migration-SoftwareLCM__"):
            dlm_software_id = (
                software_version.tags.filter(name__istartswith="DLM_migration-SoftwareLCM__")
                .first()
                .name.strip("DLM_migration-SoftwareLCM__")
            )
            if dlm_software_id not in self.dlm_to_core_id_map[self.softlcm_ct_str]:
                self.dlm_to_core_id_map[self.softlcm_ct_str][dlm_software_id] = str(software_version.id)
        for software_image in SoftwareImageFile.objects.filter(
            tags__name__istartswith="DLM_migration-SoftwareImageLCM__"
        ):
            dlm_software_image_id = (
                software_image.tags.filter(name__istartswith="DLM_migration-SoftwareImageLCM__")
                .first()
                .name.strip("DLM_migration-SoftwareImageLCM__")
            )
            if dlm_software_image_id not in self.dlm_to_core_id_map[self.softimglcm_ct_str]:
                self.dlm_to_core_id_map[self.softimglcm_ct_str][dlm_software_image_id] = str(software_image.id)

    def _migrate_custom_fields(self, old_ct, new_ct):
        """Migrate custom fields."""
        # Migrate CustomField content type
        for custom_field in CustomField.objects.filter(content_types=old_ct).exclude(content_types=new_ct):
            self.logger.info(
                "The Custom Field __%s__ will be migrated to Core model __%s__",
                custom_field.label,
                str(new_ct),
            )
            if not self.dryrun:
                custom_field.content_types.add(new_ct)
                custom_field.validated_save()

    def _migrate_software_references(self):
        """Save references, using temporary attributes, to Core SoftwareVersion in objects that reference corresponding DLM SoftwareVersion."""
        for valid_soft in ValidatedSoftwareLCM.objects.all():
            dlm_soft = valid_soft.software
            core_soft = self.dlm_to_core_id_map[self.softlcm_ct_str][str(dlm_soft.id)]
            if str(valid_soft.software_tmp) == core_soft:
                continue
            if not self.dryrun:
                valid_soft.software_tmp = uuid.UUID(core_soft)
                valid_soft.validated_save()
                self.logger.info(
                    "Migrated DLM Software __%s__ reference in ValidatedSoftwareLCM __%s__.",
                    dlm_soft,
                    valid_soft,
                    extra={"object": valid_soft},
                )

        for device_svr in DeviceSoftwareValidationResult.objects.filter(software__isnull=False):
            dlm_soft = device_svr.software
            core_soft = self.dlm_to_core_id_map[self.softlcm_ct_str][str(dlm_soft.id)]
            if str(device_svr.software_tmp) == core_soft:
                continue
            if not self.dryrun:
                device_svr.software_tmp = uuid.UUID(core_soft)
                device_svr.validated_save()
                self.logger.info(
                    "Migrated DLM Software __%s__ reference in DeviceSoftwareValidationResult __%s__.",
                    dlm_soft,
                    device_svr,
                    extra={"object": device_svr},
                )

        for invitem_svr in InventoryItemSoftwareValidationResult.objects.filter(software__isnull=False):
            dlm_soft = invitem_svr.software
            core_soft = self.dlm_to_core_id_map[self.softlcm_ct_str][str(dlm_soft.id)]
            if str(invitem_svr.software_tmp) == core_soft:
                continue
            if not self.dryrun:
                invitem_svr.software_tmp = uuid.UUID(core_soft)
                invitem_svr.validated_save()
                self.logger.info(
                    "Migrated DLM Software __%s__ reference in InventoryItemSoftwareValidationResult __%s__.",
                    dlm_soft,
                    invitem_svr,
                    extra={"object": invitem_svr},
                )

        for vuln in VulnerabilityLCM.objects.all():
            dlm_soft = vuln.software
            core_soft = self.dlm_to_core_id_map[self.softlcm_ct_str][str(dlm_soft.id)]
            if str(vuln.software_tmp) == core_soft:
                continue
            if not self.dryrun:
                vuln.software_tmp = uuid.UUID(core_soft)
                vuln.validated_save()
                self.logger.info(
                    "Migrated DLM Software __%s__ reference in VulnerabilityLCM __%s__.",
                    dlm_soft,
                    vuln,
                    extra={"object": vuln},
                )

        for cve in CVELCM.objects.all():
            dlm_soft_refs = cve.affected_softwares.all()
            if not dlm_soft_refs.exists():
                continue
            core_soft_refs = [
                self.dlm_to_core_id_map[self.softlcm_ct_str][str(dlm_soft.id)] for dlm_soft in dlm_soft_refs
            ]
            if cve.affected_softwares_tmp == core_soft_refs:
                continue
            if not self.dryrun:
                cve.affected_softwares_tmp = core_soft_refs
                cve.validated_save()
                self.logger.info(
                    "Migrated DLM Software __%s__ references in CVELCM __%s__.",
                    str(dlm_soft_refs),
                    cve,
                    extra={"object": cve},
                )

    def migrate_dlm_models_to_core(self):
        """Migrates Software, SoftwareImage and Contact model instances to corresponding Core models."""
        dlm_software_version_ct = ContentType.objects.get_for_model(SoftwareLCM)
        core_software_version_ct = ContentType.objects.get_for_model(SoftwareVersion)
        dlm_software_image_ct = ContentType.objects.get_for_model(SoftwareImageLCM)
        core_software_image_ct = ContentType.objects.get_for_model(SoftwareImageFile)
        dlm_contact_ct = ContentType.objects.get_for_model(ContactLCM)
        core_contact_ct = ContentType.objects.get_for_model(Contact)

        # Need to update DLM to Core references for already migrated objects
        self._update_migrated_dlm_object_ids()

        # Need to add Core content type to custom fields before we can copy over values from the DLM Software custom fields.
        self._migrate_custom_fields(dlm_software_version_ct, core_software_version_ct)
        # Migrate nautobot_device_lifecycle_mgmt.SoftwareLCM instances to dcim.SoftwareVersion
        for dlm_software_version in SoftwareLCM.objects.all():
            self.logger.info(
                "Migrating DLM Software object __%s__.", dlm_software_version, extra={"object": dlm_software_version}
            )
            self._migrate_software_version(dlm_software_version)
        self.migrate_content_type_references_to_new_model(
            dlm_software_version_ct,
            core_software_version_ct,
        )

        # Need to add Core content type to custom fields before we can copy over values from the DLM Software Image custom fields.
        self._migrate_custom_fields(dlm_software_image_ct, core_software_image_ct)
        # Migrate nautobot_device_lifecycle_mgmt.SoftwareImageLCM instances to dcim.SoftwareImageFile
        for dlm_software_image in SoftwareImageLCM.objects.all():
            self.logger.info(
                "Migrating DLM SoftwareImage object __%s__.", dlm_software_image, extra={"object": dlm_software_image}
            )
            self._migrate_software_image(dlm_software_image)
        self.migrate_content_type_references_to_new_model(
            dlm_software_image_ct,
            core_software_image_ct,
        )
        # Create placeholder software image files for (software, device type) pairs that don't currently have image files
        # This is to satisfy Nautobot's 2.2 requirement that device can only have software assigned if there is a matching image
        self._create_placeholder_software_images()

        # Need to add Core content type to custom fields before we can copy over values from the DLM Contact custom fields.
        self._migrate_custom_fields(dlm_contact_ct, core_contact_ct)
        # Migrate nautobot_device_lifecycle_mgmt.ContactLCM instances to extras.Contact
        for dlm_contact in ContactLCM.objects.all():
            self.logger.info("Migrating DLM Contact object __%s__.", dlm_contact, extra={"object": dlm_contact})
            self._migrate_contact(dlm_contact)
        self.migrate_content_type_references_to_new_model(
            dlm_contact_ct,
            core_contact_ct,
        )

        self._migrate_software_references()

    def _migrate_software_version(self, dlm_software_version):
        """Migrate DLM Software to Core SoftwareVersion."""
        core_software_version_ct = ContentType.objects.get_for_model(SoftwareVersion)
        device_ct = ContentType.objects.get_for_model(Device)
        dlm_software_version_ct = ContentType.objects.get_for_model(SoftwareLCM)
        inventory_item_ct = ContentType.objects.get_for_model(InventoryItem)
        status_active = Status.objects.get(name="Active")

        platform = dlm_software_version.device_platform
        version = dlm_software_version.version

        dlm_soft_attrs = {
            "alias": dlm_software_version.alias,
            "release_date": dlm_software_version.release_date,
            "end_of_support_date": dlm_software_version.end_of_support,
            "documentation_url": dlm_software_version.documentation_url,
            "long_term_support": dlm_software_version.long_term_support,
            "pre_release": dlm_software_version.pre_release,
            "_custom_field_data": dlm_software_version._custom_field_data,
        }

        new_core_software_version_created = False
        attrs_diff = {}
        core_software_version = None
        core_software_version_q = SoftwareVersion.objects.filter(platform=platform, version=version)
        if core_software_version_q.exists():
            core_software_version = core_software_version_q.first()
            self.logger.info(
                "Found existing Core SoftwareVersion __%s__ matching DLM Software __%s__.",
                core_software_version,
                dlm_software_version,
                extra={"object": core_software_version},
            )
            for attr_name, dlm_attr_value in dlm_soft_attrs.items():
                core_attr_value = getattr(core_software_version, attr_name)
                if core_attr_value == dlm_attr_value:
                    continue
                attrs_diff[attr_name] = {
                    "dlm_value": dlm_attr_value,
                    "core_value": core_attr_value,
                }
                if not self.dryrun and self.update_core_to_match_dlm:
                    setattr(core_software_version, attr_name, dlm_attr_value)
            if not self.dryrun and self.update_core_to_match_dlm and attrs_diff:
                self.logger.info(
                    "Updated existing Core SoftwareVersion __%s__ to match DLM Software __%s__. Diff before update __%s__.",
                    core_software_version,
                    dlm_software_version,
                    attrs_diff,
                    extra={"object": core_software_version},
                )
                attrs_diff.clear()
        elif not self.dryrun:
            core_software_version = SoftwareVersion(
                platform=dlm_software_version.device_platform,
                version=dlm_software_version.version,
                status=status_active,  # DLM model lacks a status field so we default to active
                **dlm_soft_attrs,
            )
            core_software_version.validated_save()
            new_core_software_version_created = True

        # Dry-run and no existing Core Software Version found
        if core_software_version is None:
            return

        # Map the DLM Software Version ID to the Core Software version ID. This is needed for SoftwareImage migrations.
        self.dlm_to_core_id_map[self.softlcm_ct_str][str(dlm_software_version.id)] = str(core_software_version.id)

        # Preserve ID of the DLM SoftwareLCM object. This is needed to rewrite references in DLM models that referenced this software.
        dlm_id_tag_name = f"DLM_migration-SoftwareLCM__{dlm_software_version.id}"
        if not self.dryrun:
            dlm_id_tag, _ = Tag.objects.get_or_create(
                name=dlm_id_tag_name,
                defaults={
                    "description": f"ID of the corresponding DLM Software for SoftwareVersion {str(core_software_version)}",
                },
            )
            dlm_id_tag.content_types.add(ContentType.objects.get_for_model(SoftwareVersion))

        # Validate whether the Core Software Version has the correct tag that references DLM Software Version ID
        core_sv_dlm_id_tags = core_software_version.tags.filter(name__istartswith="DLM_migration-SoftwareLCM__")
        if core_sv_dlm_id_tags.count() > 1:
            self.logger.warning(
                "SoftwareVersion __%s__ has multiple tags with ID of the DLM Software",
                core_software_version,
                extra={"object": core_software_version},
            )
            if not self.dryrun and self.update_core_to_match_dlm:
                for extra_tag in core_sv_dlm_id_tags:
                    if extra_tag != dlm_id_tag:
                        core_software_version.tags.remove(extra_tag)
                core_software_version.tags.add(dlm_id_tag)
                self.logger.info(
                    "Updated tag referencing ID of the corresponding DLM Software on SoftwareVersion __%s__",
                    core_software_version,
                    extra={"object": core_software_version},
                )
        elif core_sv_dlm_id_tags.count() == 1 and core_sv_dlm_id_tags.first() != dlm_id_tag:
            self.logger.warning(
                "SoftwareVersion __%s__ has tag referencing incorrect ID of the corresponding DLM Software",
                core_software_version,
                extra={"object": core_software_version},
            )
            if not self.dryrun and self.update_core_to_match_dlm:
                core_software_version.tags.remove(core_sv_dlm_id_tags.first())
                core_software_version.tags.add(dlm_id_tag)
                self.logger.info(
                    "Updated tag referencing ID of the corresponding DLM Software on SoftwareVersion __%s__",
                    core_software_version,
                    extra={"object": core_software_version},
                )
        elif core_sv_dlm_id_tags.count() == 0:
            if not new_core_software_version_created:
                self.logger.warning(
                    "SoftwareVersion __%s__ is missing tag referencing ID of the corresponding DLM Software",
                    core_software_version,
                    extra={"object": core_software_version},
                )
            if not self.dryrun:
                core_software_version.tags.add(dlm_id_tag)
                self.logger.info(
                    "Updated tag referencing ID of the corresponding DLM Software on SoftwareVersion __%s__",
                    core_software_version,
                    extra={"object": core_software_version},
                )

        if not self.dryrun:
            core_software_version.validated_save()

        if attrs_diff:
            self.logger.warning(
                "Attributes differ between DLM and Core SoftwareVersion objects: ```__%s__```",
                attrs_diff,
                extra={"object": core_software_version},
            )

        # Match the creation date of the Core Software with the DLM Software
        if (
            not self.dryrun
            and core_software_version.created != dlm_software_version.created
            and self.update_core_to_match_dlm
        ):
            core_software_version.created = dlm_software_version.created
            core_software_version.validated_save()
            core_software_version.refresh_from_db()
            self.logger.info(
                "Updated creation date of Core SoftwareVersion to match the corresponding DLM Software on SoftwareVersion __%s__",
                core_software_version,
                extra={"object": core_software_version},
            )

        # Migrate "Software on Device" relationships to the Device.software_version foreign key
        for relationship_association in RelationshipAssociation.objects.filter(
            relationship__key="device_soft",
            source_type=dlm_software_version_ct,
            source_id=dlm_software_version.id,
            destination_type=device_ct,
        ):
            try:
                device = Device.objects.get(id=relationship_association.destination_id)
            except Device.DoesNotExist:
                self.logger.error(
                    "Found Software Relationship Association for DLM Software __%s__ that points to a non-existent Device with ID __%s__.",
                    dlm_software_version,
                    relationship_association.destination_id,
                    extra={"object": dlm_software_version},
                )
                if self.remove_dangling_relationships:
                    relationship_association.delete()
                    self.logger.info(
                        "Deleted Software Relationship Association for DLM Software __%s__ that points to a non-existent Device with ID __%s__.",
                        dlm_software_version,
                        relationship_association.destination_id,
                        extra={"object": dlm_software_version},
                    )
                continue
            existing_device_software = device.software_version
            if existing_device_software and existing_device_software != core_software_version:
                self.logger.warning(
                    "Device __%s__ is already assigned to Core SoftwareVersion __%s__ but DLM software relationship implies it should be assigned to __%s__.",
                    device,
                    existing_device_software,
                    core_software_version,
                    extra={"object": device},
                )
                if not self.dryrun and self.update_core_to_match_dlm:
                    device.software_version = core_software_version
                    device.validated_save()
                    self.logger.info(
                        "Updated SoftwareVersion assignment for device __%s__. Old SoftwareVersion: __%s__. New SoftwareVersion: __%s__.",
                        device,
                        core_software_version,
                        existing_device_software,
                        extra={"object": device},
                    )
            elif not existing_device_software and not self.dryrun:
                device.software_version = core_software_version
                device.validated_save()
                self.logger.info(
                    "Assigned SoftwareVersion __%s__ to device __%s__",
                    core_software_version,
                    device,
                    extra={"object": device},
                )

        # Migrate "Software on InventoryItem" relationships to the InventoryItem.software_version foreign key
        for relationship_association in RelationshipAssociation.objects.filter(
            relationship__key="inventory_item_soft",
            source_type=dlm_software_version_ct,
            source_id=dlm_software_version.id,
            destination_type=inventory_item_ct,
        ):
            try:
                inventory_item = InventoryItem.objects.get(id=relationship_association.destination_id)
            except InventoryItem.DoesNotExist:
                self.logger.error(
                    "Found Software Relationship Association for DLM Software __%s__ that points to a non-existent InventoryItem with ID __%s__.",
                    dlm_software_version,
                    relationship_association.destination_id,
                    extra={"object": dlm_software_version},
                )
                if self.remove_dangling_relationships:
                    relationship_association.delete()
                    self.logging.info(
                        "Deleted Software Relationship Association for DLM Software __%s__ that points to a non-existent InventoryItem with ID __%s__.",
                        dlm_software_version,
                        relationship_association.destination_id,
                        extra={"object": dlm_software_version},
                    )
                continue
            existing_invitem_software = inventory_item.software_version
            if existing_invitem_software and existing_invitem_software != core_software_version:
                self.logger.warning(
                    "Inventory Item __%s__ is already assigned to Core SoftwareVersion __%s__ but DLM software relationship implies it should be assigned to __%s__.",
                    inventory_item,
                    existing_invitem_software,
                    core_software_version,
                    extra={"object": inventory_item},
                )
                if not self.dryrun and self.update_core_to_match_dlm:
                    inventory_item.software_version = core_software_version
                    inventory_item.validated_save()
                    self.logger.info(
                        "Updated SoftwareVersion assignment for inventory item __%s__. Old SoftwareVersion: __%s__. New SoftwareVersion: __%s__.",
                        inventory_item,
                        core_software_version,
                        existing_invitem_software,
                        extra={"object": inventory_item},
                    )
            elif not existing_invitem_software and not self.dryrun:
                inventory_item.software_version = core_software_version
                inventory_item.validated_save()
                self.logger.info(
                    "Assigned SoftwareVersion __%s__ to inventory item __%s__",
                    core_software_version,
                    inventory_item,
                    extra={"object": inventory_item},
                )

        core_software_version.refresh_from_db()

        # Create an object change to document migration
        if ObjectChange.objects.filter(
            changed_object_id=core_software_version.id,
            related_object_id=dlm_software_version.id,
        ).exists():
            if self.debug:
                self.logger.debug(
                    "DLM Software __%s__ to Core SoftwareVersion __%s__ migration change log already in place. Skipping.",
                    dlm_software_version,
                    core_software_version,
                )
            return

        if not self.dryrun:
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
            self.logger.info(
                "DLM Software __%s__ to Core SoftwareVersion __%s__ migration change log created.",
                dlm_software_version,
                core_software_version,
            )

    def _migrate_contact(self, dlm_contact: ContactLCM):
        """Migrates DLM Contact object to Core Contact."""
        dlm_contact_ct = ContentType.objects.get_for_model(ContactLCM)
        dlm_contract_ct = ContentType.objects.get_for_model(ContractLCM)
        core_contact_ct = ContentType.objects.get_for_model(Contact)
        contact_association_ct = ContentType.objects.get_for_model(ContactAssociation)

        status_active, _ = Status.objects.get_or_create(name="Active")

        dlm_contact_attrs = {
            "address": dlm_contact.address,
            "comments": dlm_contact.comments,
            "_custom_field_data": dlm_contact._custom_field_data,
        }

        new_core_contact_created = False
        attrs_diff = {}
        core_contact = None
        core_contact_q = Contact.objects.filter(name=dlm_contact.name, phone=dlm_contact.phone, email=dlm_contact.email)
        if core_contact_q.exists():
            core_contact = core_contact_q.first()
            self.logger.info(
                "Found existing Core Contact __%s__ matching DLM Contact __%s__.",
                core_contact,
                dlm_contact,
                extra={"object": core_contact},
            )
            for attr_name, dlm_attr_value in dlm_contact_attrs.items():
                core_attr_value = getattr(core_contact, attr_name)
                if core_attr_value == dlm_attr_value:
                    continue
                attrs_diff[attr_name] = {
                    "dlm_value": dlm_attr_value,
                    "core_value": core_attr_value,
                }
                if not self.dryrun and self.update_core_to_match_dlm:
                    setattr(core_contact, attr_name, dlm_attr_value)
            if not self.dryrun and self.update_core_to_match_dlm and attrs_diff:
                self.logger.info(
                    "Updated existing Core Contact __%s__ to match DLM Contact __%s__. Diff before update __%s__.",
                    core_contact,
                    dlm_contact,
                    attrs_diff,
                    extra={"object": core_contact},
                )
                attrs_diff.clear()
        elif not self.dryrun:
            core_contact = Contact(
                name=dlm_contact.name,
                phone=dlm_contact.phone,
                email=dlm_contact.email,
                **dlm_contact_attrs,
            )
            core_contact.validated_save()
            new_core_contact_created = True

        if core_contact is None:
            return

        # Map the DLM Contact ID to Core Contact ID.
        self.dlm_to_core_id_map[self.contactlcm_ct_str][str(dlm_contact.id)] = str(core_contact.id)

        # Preserve ID of the DLM Contact object.
        dlm_id_tag_name = f"DLM_migration-ContactLCM__{dlm_contact.id}"
        if not self.dryrun:
            dlm_id_tag, _ = Tag.objects.get_or_create(
                name=dlm_id_tag_name,
                defaults={
                    "description": f"ID of the corresponding DLM Contact for Contact {str(core_contact)}",
                },
            )
            dlm_id_tag.content_types.add(ContentType.objects.get_for_model(Contact))

        # Validate whether the Core Contact has the correct tag that references DLM Contact ID
        core_contact_dlm_id_tags = core_contact.tags.filter(name__istartswith="DLM_migration-ContactLCM__")
        if core_contact_dlm_id_tags.count() > 1:
            self.logger.warning(
                "Contact __%s__ has multiple tags with ID of the DLM Contact",
                core_contact,
                extra={"object": core_contact},
            )
            if not self.dryrun and self.update_core_to_match_dlm:
                for extra_tag in core_contact_dlm_id_tags:
                    if extra_tag != dlm_id_tag:
                        core_contact.tags.remove(extra_tag)
                core_contact.tags.add(dlm_id_tag)
                self.logger.info(
                    "Updated tag referencing ID of the corresponding DLM Contact on Contact __%s__",
                    core_contact,
                    extra={"object": core_contact},
                )
        elif core_contact_dlm_id_tags.count() == 1 and core_contact_dlm_id_tags.first() != dlm_id_tag:
            self.logger.warning(
                "Contact __%s__ has tag referencing incorrect ID of the corresponding DLM Contact",
                core_contact,
                extra={"object": core_contact},
            )
            if not self.dryrun and self.update_core_to_match_dlm:
                core_contact.tags.remove(core_contact_dlm_id_tags.first())
                core_contact.tags.add(dlm_id_tag)
                self.logger.info(
                    "Updated tag referencing ID of the corresponding DLM Contact on Contact __%s__",
                    core_contact,
                    extra={"object": core_contact},
                )
        elif core_contact_dlm_id_tags.count() == 0:
            if not new_core_contact_created:
                self.logger.warning(
                    "Contact __%s__ is missing tag referencing ID of the corresponding DLM Contact",
                    core_contact,
                    extra={"object": core_contact},
                )
            if not self.dryrun:
                core_contact.tags.add(dlm_id_tag)
                self.logger.info(
                    "Updated tag referencing ID of the corresponding DLM Contact on Contact __%s__",
                    core_contact,
                    extra={"object": core_contact},
                )

        if not self.dryrun:
            core_contact.validated_save()

        if attrs_diff:
            self.logger.warning(
                "Attributes differ between DLM and Core Contact objects: ```__%s__```",
                attrs_diff,
                extra={"object": core_contact},
            )

        # Match the creation date of the Core Software with the DLM Software
        if not self.dryrun and core_contact.created != dlm_contact.created:
            core_contact.created = dlm_contact.created
            core_contact.validated_save()
            core_contact.refresh_from_db()
            self.logger.info(
                "Updated creation date of Core Contact __%s__ to match the corresponding DLM Contact",
                core_contact,
                extra={"object": core_contact},
            )

        # Migrate ContactLCM types to Core Roles
        try:
            contact_association_role = Role.objects.get(name=dlm_contact.type)
        except Role.DoesNotExist:
            self.logger.info(
                "Contact Association Role __%s__ will be created to match the DLM Contact Type.",
                dlm_contact.type,
            )
            if not self.dryrun:
                contact_association_role = Role.objects.create(name=dlm_contact.type)
        finally:
            if not self.dryrun:
                contact_association_role.content_types.add(contact_association_ct)

        # Recreate the DLM Contact -> Contract association with Core Contact -> Contract
        try:
            ContactAssociation.objects.get(
                contact=core_contact,
                associated_object_id=dlm_contact.contract.id,
                associated_object_type=dlm_contract_ct,
                role=contact_association_role,
            )
        except ContactAssociation.DoesNotExist:
            self.logger.info(
                "Contact Association between Core Contact __%s__ and DLM Contract __%s__ will be created.",
                core_contact,
                dlm_contact.contract,
            )
            if not self.dryrun:
                ContactAssociation.objects.create(
                    contact=core_contact,
                    associated_object_id=dlm_contact.contract.id,
                    associated_object_type=dlm_contract_ct,
                    role=contact_association_role,
                    status=status_active,
                )

        def contact_repr(contact):
            result = contact.name
            if contact.phone:
                result += f" ({contact.phone})"
            if contact.email:
                result += f" ({contact.email})"
            return result

        # Create an object change to document migration
        if ObjectChange.objects.filter(
            changed_object_id=core_contact.id,
            related_object_id=dlm_contact.id,
        ).exists():
            if self.debug:
                self.logger.debug(
                    "DLM Contact __%s__ to Core Contact __%s__ migration change log already in place. Skipping.",
                    dlm_contact,
                    core_contact,
                )
            return

        if not self.dryrun:
            # Create an object change to document migration
            ObjectChange.objects.create(
                action=ObjectChangeActionChoices.ACTION_UPDATE,
                change_context=ObjectChangeEventContextChoices.CONTEXT_ORM,
                change_context_detail="Migrated from Nautobot App Device Lifecycle Management",
                changed_object_id=core_contact.id,
                changed_object_type=core_contact_ct,
                object_data=serialize_object(core_contact),
                object_data_v2=serialize_object_v2(core_contact),
                object_repr=contact_repr(core_contact)[:CHANGELOG_MAX_OBJECT_REPR],
                related_object_id=dlm_contact.id,
                related_object_type=dlm_contact_ct,
                request_id=common_objectchange_request_id,
                user=None,
                user_name="Undefined",
            )
            self.logger.info(
                "DLM Contact __%s__ to Core Contact __%s__ migration change log created.",
                dlm_contact,
                core_contact,
            )

    def _migrate_hashing_algorithm(self, value):
        """Migrate DLM SoftwareImage hashing algorithm from free-text field to Core SoftwareImageFile choice."""
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

    def _migrate_software_image(self, dlm_software_image):
        """Migrate DLM SoftwareImage to Core SoftwareImageFile."""
        core_software_image_ct = ContentType.objects.get_for_model(SoftwareImageFile)
        dlm_software_image_ct = ContentType.objects.get_for_model(SoftwareImageLCM)
        device_ct = ContentType.objects.get_for_model(Device)
        inventory_item_ct = ContentType.objects.get_for_model(InventoryItem)
        status_active, _ = Status.objects.get_or_create(name="Active")

        image_file_name = dlm_software_image.image_file_name
        dlm_software_version = dlm_software_image.software.id
        # Dry-run will not have populated mappings for not-yet-migrated Software Versions
        core_software_version_id = self.dlm_to_core_id_map[self.softlcm_ct_str].get(str(dlm_software_version), None)
        # Flag tracking whether hashing algorithm could be automatically migrated

        if dlm_software_image.hashing_algorithm != "":
            hashing_algorithm = self._migrate_hashing_algorithm(dlm_software_image.hashing_algorithm)
        else:
            hashing_algorithm = ""

        if dlm_software_image.hashing_algorithm != "" and hashing_algorithm == "":
            self.logger.warning(
                f"\n\nUnable to map hashing algorithm '{dlm_software_image.hashing_algorithm}' for software image "
                f"'{dlm_software_image.software.version} - {dlm_software_image.image_file_name}' ({dlm_software_image.id}). "
                "Please update the hashing algorithm manually."
            )

        dlm_soft_img_attrs = {
            "image_file_checksum": dlm_software_image.image_file_checksum,
            "hashing_algorithm": hashing_algorithm,
            "download_url": dlm_software_image.download_url,
            "default_image": dlm_software_image.default_image,
            "_custom_field_data": dlm_software_image._custom_field_data or {},
        }

        new_core_software_image_created = False
        attrs_diff = {}
        core_software_image = None
        core_software_image_q = SoftwareImageFile.objects.filter(
            image_file_name=image_file_name, software_version=core_software_version_id
        )
        if core_software_image_q.exists():
            core_software_image = core_software_image_q.first()
            self.logger.info(
                "Found existing Core SoftwareImageFile __%s__ matching DLM SoftwareImage __%s__.",
                core_software_image,
                dlm_software_image,
                extra={"object": core_software_image},
            )
            for attr_name, dlm_attr_value in dlm_soft_img_attrs.items():
                core_attr_value = getattr(core_software_image, attr_name)
                if core_attr_value == dlm_attr_value:
                    continue
                attrs_diff[attr_name] = {
                    "dlm_value": dlm_attr_value,
                    "core_value": core_attr_value,
                }
                if not self.dryrun and self.update_core_to_match_dlm:
                    setattr(core_software_image, attr_name, dlm_attr_value)
            if not self.dryrun and self.update_core_to_match_dlm and attrs_diff:
                self.logger.info(
                    "Updated existing Core SoftwareImageFile __%s__ to match DLM SoftwareImage __%s__. Diff before update __%s__.",
                    core_software_image,
                    dlm_software_image,
                    attrs_diff,
                    extra={"object": core_software_image},
                )
                attrs_diff.clear()
        elif not self.dryrun:
            core_software_image = SoftwareImageFile(
                software_version_id=core_software_version_id,
                image_file_name=image_file_name,
                status=status_active,  # DLM model lacks a status field so we default to active
                **dlm_soft_img_attrs,
            )
            core_software_image.validated_save()
            new_core_software_image_created = True

        # Dry-run and no existing Core SoftwareImageFile found
        if core_software_image is None:
            return

        # Map the DLM Software Version ID to the Core Software version ID. This is needed for SoftwareImage migrations.
        self.dlm_to_core_id_map[self.softimglcm_ct_str][str(dlm_software_image.id)] = str(core_software_image.id)

        # Preserve ID of the DLM SoftwareImageLCM object. This is needed for migrations.
        csv_dlm_id_tag_name = f"DLM_migration-SoftwareImageLCM__{dlm_software_image.id}"
        if not self.dryrun:
            dlm_id_tag, _ = Tag.objects.get_or_create(
                name=csv_dlm_id_tag_name,
                defaults={
                    "description": f"ID of the corresponding DLM SoftwareImageLCM for SoftwareImageFile {str(core_software_image)}",
                },
            )
            dlm_id_tag.content_types.add(ContentType.objects.get_for_model(SoftwareImageFile))

        # Validate whether the Core Software Image File has the correct tag that references DLM Software Image ID
        core_sif_dlm_id_tags = core_software_image.tags.filter(name__istartswith="DLM_migration-SoftwareImageLCM__")
        if core_sif_dlm_id_tags.count() > 1:
            self.logger.warning(
                "SoftwareImageFile __%s__ has multiple tags with ID of the DLM SoftwareImage",
                core_software_image,
                extra={"object": core_software_image},
            )
            if not self.dryrun and self.update_core_to_match_dlm:
                for extra_tag in core_sif_dlm_id_tags:
                    if extra_tag != dlm_id_tag:
                        core_software_image.tags.remove(extra_tag)
                core_software_image.tags.add(dlm_id_tag)
                self.logger.warning(
                    "Updated tag referencing ID of thr corresponding DLM SoftwareImage on SoftwareImageFile __%s__",
                    core_software_image,
                    extra={"object": core_software_image},
                )
        elif core_sif_dlm_id_tags.count() == 1 and core_sif_dlm_id_tags.first() != dlm_id_tag:
            self.logger.warning(
                "SoftwareImageFile __%s__ has tag referencing incorrect ID of the corresponding DLM SoftwareImage",
                core_software_image,
                extra={"object": core_software_image},
            )
            if not self.dryrun and self.update_core_to_match_dlm:
                core_software_image.tags.remove(core_sif_dlm_id_tags.first())
                core_software_image.tags.add(dlm_id_tag)
                self.logger.warning(
                    "Updated tag referencing ID of the corresponding DLM SoftwareImage on SoftwareImageFile __%s__",
                    core_software_image,
                    extra={"object": core_software_image},
                )
        elif core_sif_dlm_id_tags.count() == 0:
            if not new_core_software_image_created:
                self.logger.warning(
                    "SoftwareImageFile __%s__ is missing tag referencing ID of the corresponding DLM SoftwareImage",
                    core_software_image,
                    extra={"object": core_software_image},
                )
            if not self.dryrun:
                core_software_image.tags.add(dlm_id_tag)
                self.logger.info(
                    "Updated tag referencing ID of corresponding DLM SoftwareImage on SoftwareImageFile __%s__",
                    core_software_image,
                    extra={"object": core_software_image},
                )

        if not self.dryrun:
            core_software_image.validated_save()

        if attrs_diff:
            self.logger.warning(
                "Attributes differ between DLM and Core SoftwareImageFile objects: ```__%s__```",
                attrs_diff,
                extra={"object": core_software_image},
            )

        dtypes_in_dlm_not_in_core = set(dlm_software_image.device_types.all()) - set(
            core_software_image.device_types.all()
        )
        if dtypes_in_dlm_not_in_core:
            self.logger.info(
                "Core SoftwareImageFile __%s__ is missing DLM SoftwareImage DeviceType assignments __%s__",
                core_software_image,
                ", ".join(str(d) for d in dtypes_in_dlm_not_in_core),
                extra={"object": core_software_image},
            )
            if not self.dryrun:
                for dtype in dtypes_in_dlm_not_in_core:
                    core_software_image.device_types.add(dtype)

        # Work around created field's auto_now_add behavior
        if (
            not self.dryrun
            and core_software_image.created != dlm_software_image.created
            and self.update_core_to_match_dlm
        ):
            core_software_image.created = dlm_software_image.created
            core_software_image.validated_save()
            core_software_image.refresh_from_db()
            self.logger.info(
                "Updated creation date of Core SoftwareImageFile to match the corresponding DLM SoftwareImage on SoftwareImageFile __%s__",
                core_software_image,
                extra={"object": core_software_image},
            )

        # Map the DLM SoftwareImage object_tags to devices and set the Device.software_image_files m2m field
        device_pks = (
            TaggedItem.objects.filter(tag__in=dlm_software_image.object_tags.all(), content_type=device_ct)
            .values_list("object_id")
            .distinct()
        )
        for device in Device.objects.filter(pk__in=device_pks):
            if core_software_image not in device.software_image_files.all():
                self.logger.info(
                    "Device __%s__ is missing SoftwareImage __%s__ assignment.",
                    device,
                    core_software_image,
                    extra={"object": core_software_image},
                )
                if not self.dryrun:
                    device.software_image_files.add(core_software_image)
                    self.logger.info(
                        "SoftwareImage __%s__ assigned to Device __%s__.",
                        core_software_image,
                        device,
                        extra={"object": core_software_image},
                    )

        # Map the DLM object_tags to inventory items and set the InventoryItem.software_image_files m2m field
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
                self.logger.info(
                    "InventoryItem __%s__ is missing SoftwareImage __%s__ assignment.",
                    inventory_item,
                    core_software_image,
                    extra={"object": core_software_image},
                )
                if not self.dryrun:
                    inventory_item.software_image_files.add(core_software_image)
                    self.logger.info(
                        "SoftwareImage __%s__ assigned to InventoryItem __%s__.",
                        core_software_image,
                        inventory_item,
                        extra={"object": core_software_image},
                    )

        core_software_image.refresh_from_db()

        # Create an object change to document migration
        if ObjectChange.objects.filter(
            changed_object_id=core_software_image.id,
            related_object_id=dlm_software_image.id,
        ).exists():
            if self.debug:
                self.logger.debug(
                    "DLM SoftwareImage __%s__ to Core SoftwareImageFile __%s__ migration change log already in place. Skipping.",
                    dlm_software_image,
                    core_software_image,
                )
            return

        if not self.dryrun:
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
            self.logger.info(
                "DLM SoftwareImage __%s__ to Core SoftwareImageFile __%s__ migration change log created.",
                dlm_software_image,
                core_software_image,
            )

    def migrate_content_type_references_to_new_model(self, old_ct, new_ct):
        """When replacing a model, this will update references to the content type on related models such as tags and object changes.

        This also updates the primary key references.

        This will replace the old content type with the new content type on the following models:
            - ComputedField.content_type
            - CustomLink.content_type
            - ExportTemplate.content_type
            - Note.assigned_object_type
            - ObjectChange.changed_object_type
            - Relationship.source_type
            - Relationship.destination_type
            - RelationshipAssociation.source_type
            - RelationshipAssociation.destination_type
            - TaggedItem.content_type

        For these one-to-many and many-to-many relationships, the new content type is added
        to the related model's content type list, but the old content type is not removed:
            - CustomField.content_types
            - JobButton.content_types
            - JobHook.content_types
            - ObjectPermission.object_types
            - Status.content_types
            - Tag.content_types
            - WebHook.content_types

        This will also fix tags that were not properly enforced by adding the new model's content type to the tag's
        content types if an instance of the new model is using the tag.

        Args:
            apps (obj): An instance of the Django 'apps' object.
            old_ct (obj): An instance of ContentType for the old model.
            new_ct (obj): An instance of ContentType for the new model.

        """
        # Migrate ComputedField content type
        for computed_field in ComputedField.objects.filter(content_type=old_ct):
            self.logger.info(
                "The Computed Field __%s__ will be migrated to Core model __%s__",
                computed_field.label,
                str(new_ct),
            )
            if not self.dryrun:
                computed_field.content_type = new_ct
                computed_field.validated_save()

        # Migrate CustomLink content type
        for custom_link in CustomLink.objects.filter(content_type=old_ct):
            self.logger.info(
                "The Custom Link __%s__ will be migrated to Core model __%s__",
                custom_link.name,
                str(new_ct),
            )
            if not self.dryrun:
                custom_link.content_type = new_ct
                custom_link.validated_save()

        # Migrate ExportTemplate content type - skip git export templates
        for export_template in ExportTemplate.objects.filter(content_type=old_ct, owner_content_type=None):
            self.logger.info(
                "The Export Template __%s__ will be migrated to Core model __%s__",
                export_template.name,
                str(new_ct),
            )
            if not self.dryrun:
                export_template.content_type = new_ct
                export_template.validated_save()

        # Migrate JobButton content type
        for job_button in JobButton.objects.filter(content_types=old_ct).exclude(content_types=new_ct):
            self.logger.info(
                "The Job Button __%s__ will be migrated to Core model __%s__",
                job_button.name,
                str(new_ct),
            )
            if not self.dryrun:
                job_button.content_types.add(new_ct)

        # Migrate JobHook content type
        for job_hook in JobHook.objects.filter(content_types=old_ct).exclude(content_types=new_ct):
            self.logger.info("The Job Hook __%s__ will be migrated to Core model __%s__", job_hook.name, str(new_ct))
            if not self.dryrun:
                job_hook.content_types.add(new_ct)

        # Migrate Note content type
        for note in Note.objects.filter(assigned_object_type=old_ct):
            self.logger.info("The Note __%s__ will be migrated to Core model __%s__", str(note), str(new_ct))
            if not self.dryrun:
                note.assigned_object_type = new_ct
                note.assigned_object_id = self.dlm_to_core_id_map[str(old_ct)][str(note.assigned_object_id)]
                note.validated_save()

        # Migrate ObjectChange content type
        for object_change in ObjectChange.objects.filter(changed_object_type=old_ct):
            if not self.hide_changelog_migrations:
                self.logger.info(
                    "The Object Change __%s__ will be migrated to Core model __%s__",
                    str(object_change),
                    str(new_ct),
                )
            if not self.dryrun:
                object_change.changed_object_type = new_ct
                # We might have a reference to deleted object so need to check if it exists
                if not old_ct.model_class().objects.filter(id=object_change.changed_object_id).exists():
                    if not self.hide_changelog_migrations:
                        self.logger.warning(
                            "The DLM Software object __%s__ referenced in Object Change __%s__ is gone. Updating content type only to __%s__",
                            str(object_change.changed_object_id),
                            str(object_change),
                            str(new_ct),
                        )
                    object_change.validated_save()
                    continue
                object_change.changed_object_id = self.dlm_to_core_id_map[str(old_ct)][
                    str(object_change.changed_object_id)
                ]
                object_change.validated_save()

        # Migrate Status content type
        for status in Status.objects.filter(content_types=old_ct).exclude(content_types=new_ct):
            self.logger.info("The Status __%s__ will be migrated to Core model __%s__", status.name, str(new_ct))
            if not self.dryrun:
                status.content_types.add(new_ct)

        # Migrate Tag content type
        for tag in Tag.objects.filter(content_types=old_ct).exclude(content_types=new_ct):
            self.logger.info("The Tag __%s__ will be migrated to Core model __%s__", tag.name, str(new_ct))
            if not self.dryrun:
                tag.content_types.add(new_ct)

        # Migrate TaggedItem content type
        for tagged_item in TaggedItem.objects.filter(content_type=old_ct):
            self.logger.info(
                "The Tagged Item __%s__ will be migrated to Core model __%s__",
                str(tagged_item),
                str(new_ct),
            )
            if not self.dryrun:
                tagged_item.content_type = new_ct
                tagged_item.object_id = self.dlm_to_core_id_map[str(old_ct)][str(tagged_item.object_id)]
                tagged_item.validated_save()

        # Fix tags that were implemented incorrectly and didn't enforce content type
        # If a tag is related to an instance of a model, make sure the content type for that model exists on the tag object
        if not self.dryrun:
            for tag_id in TaggedItem.objects.filter(content_type=new_ct).values_list("tag_id", flat=True).distinct():
                try:
                    tag = Tag.objects.get(id=tag_id)
                    if not tag.content_types.filter(id=new_ct.id).exists():
                        tag.content_types.add(new_ct)
                except Tag.DoesNotExist:
                    pass

        # Migrate WebHook content type
        for web_hook in Webhook.objects.filter(content_types=old_ct).exclude(content_types=new_ct):
            self.logger.info("The Web Hook __%s__ will be migrated to Core model __%s__", web_hook.name, str(new_ct))
            if not self.dryrun:
                web_hook.content_types.add(new_ct)

        # Migrate ObjectPermission content type
        for object_permission in ObjectPermission.objects.filter(object_types=old_ct).exclude(object_types=new_ct):
            self.logger.info(
                "The Object Permission __%s__ will be migrated to Core model __%s__",
                str(object_permission),
                str(new_ct),
            )
            if not self.dryrun:
                object_permission.object_types.add(new_ct)

        # These are migrated separately as they follow specific business logic
        excluded_relationships = ("device_soft", "inventory_item_soft")
        # Migrate Relationship content type
        relationship_associations_dlm_source = []
        for relationship in Relationship.objects.filter(source_type=old_ct).exclude(key__in=excluded_relationships):
            self.logger.info(
                "The Relationship __%s__ will be migrated to Core model __%s__", relationship.label, str(new_ct)
            )
            # We can't migrate relationships in place
            if not self.dryrun:
                try:
                    for relationship_association in RelationshipAssociation.objects.filter(
                        source_type=old_ct, relationship=relationship
                    ).exclude(relationship__key__in=excluded_relationships):
                        self.logger.info(
                            "The Relationship Association __%s__ will be migrated to Core model __%s__",
                            str(relationship_association),
                            str(new_ct),
                        )
                        relationship_associations_dlm_source.append(
                            {
                                "relationship_id": relationship_association.relationship_id,
                                "source_type_id": relationship_association.source_type_id,
                                "source_id": relationship_association.source_id,
                                "destination_type_id": relationship_association.destination_type_id,
                                "destination_id": relationship_association.destination_id,
                            }
                        )
                        relationship_association.delete()
                except Exception as err:
                    self.logger.error(
                        "Encountered exception __%s__ while disassociating Relationship __%s__. Rolling back relationship updates.",
                        str(err),
                        relationship.label,
                    )
                    for relationship_attrs in relationship_associations_dlm_source:
                        RelationshipAssociation.objects.get_or_create(**relationship_attrs)
                    raise Exception("Error while migrating relationships. Review your relationships and try again.")

                try:
                    relationship.source_type = new_ct
                    relationship.validated_save()
                    new_relationship_associations = []
                    for relationship_attrs in relationship_associations_dlm_source:
                        new_relationship_association = RelationshipAssociation(
                            relationship_id=relationship_attrs["relationship_id"],
                            destination_type_id=relationship_attrs["destination_type_id"],
                            destination_id=relationship_attrs["destination_id"],
                            source_type=new_ct,
                            source_id=self.dlm_to_core_id_map[str(old_ct)][str(relationship_attrs["source_id"])],
                        )
                        new_relationship_association.validated_save()
                        new_relationship_associations.append(new_relationship_association)
                except Exception as err:
                    self.logger.warning(
                        "Encountered exception __%s__ while migrating Relationship __%s__. Rolling back relationship updates.",
                        str(err),
                        relationship.label,
                    )
                    for new_relationship_association in new_relationship_associations:
                        new_relationship_association.delete()
                    relationship.source_type = old_ct
                    relationship.validated_save()

                    for relationship_attrs in relationship_associations_dlm_source:
                        RelationshipAssociation.objects.get_or_create(**relationship_attrs)
                    raise Exception("Error while migrating relationships. Review your relationships and try again.")

        relationship_associations_dlm_destination = []
        for relationship in Relationship.objects.filter(destination_type=old_ct).exclude(
            key__in=excluded_relationships
        ):
            self.logger.info(
                "The Relationship __%s__ will be migrated to Core model __%s__", relationship.label, str(new_ct)
            )
            # We can't migrate relationships in place
            if not self.dryrun:
                try:
                    for relationship_association in RelationshipAssociation.objects.filter(
                        destination_type=old_ct, relationship=relationship
                    ).exclude(relationship__key__in=excluded_relationships):
                        self.logger.info(
                            "The Relationship Association __%s__ will be migrated to Core model __%s__",
                            str(relationship_association),
                            str(new_ct),
                        )
                        relationship_associations_dlm_destination.append(
                            {
                                "relationship_id": relationship_association.relationship_id,
                                "source_type_id": relationship_association.source_type_id,
                                "source_id": relationship_association.source_id,
                                "destination_type_id": relationship_association.destination_type_id,
                                "destination_id": relationship_association.destination_id,
                            }
                        )
                        relationship_association.delete()
                except Exception as err:
                    self.logger.warning(
                        "Encountered exception __%s__ while disassociating instance of Relationship __%s__. Rolling back relationship updates.",
                        str(err),
                        relationship.label,
                    )
                    for relationship_attrs in relationship_associations_dlm_destination:
                        RelationshipAssociation.objects.get_or_create(**relationship_attrs)
                    raise Exception("Error while migrating relationships. Review your relationships and try again.")

                try:
                    relationship.destination_type = new_ct
                    relationship.validated_save()
                    new_relationship_associations = []
                    for relationship_attrs in relationship_associations_dlm_destination:
                        new_relationship_association = RelationshipAssociation(
                            relationship_id=relationship_attrs["relationship_id"],
                            source_type_id=relationship_attrs["source_type_id"],
                            source_id=relationship_attrs["source_id"],
                            destination_type=new_ct,
                            destination_id=self.dlm_to_core_id_map[str(old_ct)][
                                str(relationship_attrs["destination_id"])
                            ],
                        )
                        new_relationship_association.validated_save()
                        new_relationship_associations.append(new_relationship_association)
                except Exception as err:
                    self.logger.warning(
                        "Encountered exception __%s__ while migrating Relationship __%s__. Rolling back relationship updates.",
                        str(err),
                        relationship.label,
                    )
                    for new_relationship_association in new_relationship_associations:
                        new_relationship_association.delete()
                    relationship.destination_type = old_ct
                    relationship.validated_save()

                    for relationship_attrs in relationship_associations_dlm_destination:
                        RelationshipAssociation.objects.get_or_create(**relationship_attrs)
                    raise Exception("Error while migrating relationships. Review your relationships and try again.")

    def _create_placeholder_software_images(self):
        """Create placeholder software image files for software that is used by devices but no image currently exists."""
        status_active, _ = Status.objects.get_or_create(name="Active")

        # Get all (software_version, device_type) pairs where software_version is in use by a device with given device_type
        for software, device_type in (
            Device.objects.filter(software_version__isnull=False)
            .order_by()
            .values_list("software_version", "device_type")
            .distinct()
        ):
            if SoftwareImageFile.objects.filter(software_version=software, device_types=device_type).exists():
                continue
            software_version = SoftwareVersion.objects.get(id=software)
            device_type = DeviceType.objects.get(id=device_type)
            image_soft_and_dt = f"{slugify(software_version.version)}-{slugify(device_type.model)}"[:227]
            image_file_name = f"{image_soft_and_dt}-dlm-migrations-placeholder"
            if SoftwareImageFile.objects.filter(image_file_name=image_file_name).exists():
                invalid_soft_image = SoftwareImageFile.objects.filter(image_file_name=image_file_name).first()
                self.logger.error(
                    "Found incorrectly assigned SoftwareImageVersion __%s__. This Image should be assigned to Software __%s__ and DeviceType __%s__.",
                    invalid_soft_image,
                    software_version,
                    device_type,
                    extra={"object": invalid_soft_image},
                )
                continue
            self.logger.warning(
                "Found SoftwareVersion __%s__, assigned to Devices, that doesn't have a SoftwareImageFile matching DeviceType __%s__.",
                software_version,
                device_type,
            )
            if not self.dryrun:
                software_image = SoftwareImageFile(
                    software_version=software_version,
                    image_file_name=image_file_name,
                    status=status_active,
                )
                software_image.validated_save()
                software_image.device_types.add(device_type)
                self.logger.warning(
                    "Created placeholder SoftwareImageFile __%s__ assigned to DeviceType __%s__.",
                    software_image,
                    device_type,
                    extra={"object": software_image},
                )

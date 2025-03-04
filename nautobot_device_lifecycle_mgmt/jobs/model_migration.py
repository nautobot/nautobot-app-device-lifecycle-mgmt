# pylint: disable=too-many-lines
"""Jobs for the Lifecycle Management app."""

import html
import uuid
from difflib import SequenceMatcher
from string import ascii_letters, digits

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Count, Q
from django.urls import reverse
from django.utils.text import slugify
from nautobot.apps.choices import (
    ObjectChangeActionChoices,
    ObjectChangeEventContextChoices,
    SoftwareImageFileHashingAlgorithmChoices,
)
from nautobot.apps.models import serialize_object, serialize_object_v2
from nautobot.apps.utils import get_route_for_model
from nautobot.dcim.models import Device, InventoryItem, SoftwareImageFile, SoftwareVersion
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
from packaging import version

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


class RollbackTransaction(Exception):
    """Exception to rollback database transaction."""


class DLMToNautobotCoreModelMigration(Job):  # pylint: disable=too-many-instance-attributes
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

    # pylint: disable=arguments-differ, too-many-arguments
    def run(
        self, dryrun, hide_changelog_migrations, update_core_to_match_dlm, remove_dangling_relationships, debug
    ) -> None:
        """Migration logic."""
        # Fail if running on nautobot < 2.2.0
        if version.parse(settings.VERSION) < version.parse("2.2.0"):
            raise ValueError("This job requires Nautobot 2.2.0 or later.")

        try:
            with transaction.atomic():
                self.migrate_dlm_models_to_core(
                    debug, hide_changelog_migrations, update_core_to_match_dlm, remove_dangling_relationships
                )
                if dryrun:
                    raise RollbackTransaction("Dryrun mode. Rolling back changes.")
        except RollbackTransaction:
            self.logger.info("Transaction rolled back.")

    def _migrate_custom_fields(self, old_ct, new_ct):
        """Migrate custom fields."""
        # Migrate CustomField content type
        for custom_field in CustomField.objects.filter(content_types=old_ct).exclude(content_types=new_ct):
            self.logger.info(
                "The Custom Field __%s__ will be migrated to Core model __%s__",
                html.escape(str(custom_field.label)),
                html.escape(str(new_ct)),
            )
            custom_field.content_types.add(new_ct)

    def _migrate_software_reference_for_model(self, model):
        """Change foreignkey references to DLM SoftwareLCM to the migrated Core SoftwareVersion."""
        for instance in model.objects.filter(old_software__isnull=False):
            dlm_soft = instance.old_software
            core_soft = dlm_soft.migrated_to_core_model
            if instance.software != core_soft:
                instance.software = core_soft
                instance.validated_save()
                self.logger.info(
                    "Migrated DLM Software __%s__ reference in %s __%s__.",
                    html.escape(str(dlm_soft)),
                    html.escape(str(model.__name__)),
                    html.escape(str(instance)),
                    extra={"object": instance},
                )

    def _migrate_software_references(self):
        """Change foreignkey/m2m references to DLM SoftwareLCM to the migrated Core SoftwareVersion."""
        for model in [
            ValidatedSoftwareLCM,
            DeviceSoftwareValidationResult,
            InventoryItemSoftwareValidationResult,
            VulnerabilityLCM,
        ]:
            self._migrate_software_reference_for_model(model)

        for cve in CVELCM.objects.all():
            dlm_soft_refs = cve.old_affected_softwares.all()
            if not dlm_soft_refs.exists():
                continue
            core_soft_refs = dlm_soft_refs.values_list("migrated_to_core_model__id")
            if set(cve.affected_softwares.values_list("id")) == set(core_soft_refs):
                continue
            cve.affected_softwares.clear()
            for dlm_soft_ref in dlm_soft_refs:
                cve.affected_softwares.add(dlm_soft_ref.migrated_to_core_model)
            self.logger.info(
                "Migrated DLM Software __%s__ references in CVELCM __%s__.",
                html.escape(str(list(dlm_soft_refs))),
                html.escape(str(cve)),
                extra={"object": cve},
            )

    def migrate_dlm_models_to_core(
        self, debug, hide_changelog_migrations, update_core_to_match_dlm, remove_dangling_relationships
    ):
        """Migrates Software, SoftwareImage and Contact model instances to corresponding Core models."""
        dlm_software_version_ct = ContentType.objects.get_for_model(SoftwareLCM)
        core_software_version_ct = ContentType.objects.get_for_model(SoftwareVersion)
        dlm_software_image_ct = ContentType.objects.get_for_model(SoftwareImageLCM)
        core_software_image_ct = ContentType.objects.get_for_model(SoftwareImageFile)
        dlm_contact_ct = ContentType.objects.get_for_model(ContactLCM)
        core_contact_ct = ContentType.objects.get_for_model(Contact)

        # Need to add Core content type to custom fields before we can copy over values from the DLM Software custom fields.
        self._migrate_custom_fields(dlm_software_version_ct, core_software_version_ct)
        # Migrate nautobot_device_lifecycle_mgmt.SoftwareLCM instances to dcim.SoftwareVersion
        for dlm_software_version in SoftwareLCM.objects.filter(migrated_to_core_model_flag=False):
            self.logger.info(
                "Migrating DLM Software object __%s__.",
                html.escape(str(dlm_software_version)),
                extra={"object": dlm_software_version},
            )
            self._migrate_software_version(dlm_software_version, update_core_to_match_dlm, debug)
        self.migrate_content_type_references_to_new_model(
            dlm_software_version_ct,
            core_software_version_ct,
            hide_changelog_migrations,
        )

        # Need to add Core content type to custom fields before we can copy over values from the DLM Software Image custom fields.
        self._migrate_custom_fields(dlm_software_image_ct, core_software_image_ct)
        # Migrate nautobot_device_lifecycle_mgmt.SoftwareImageLCM instances to dcim.SoftwareImageFile
        for dlm_software_image in SoftwareImageLCM.objects.filter(migrated_to_core_model_flag=False):
            self.logger.info(
                "Migrating DLM SoftwareImage object __%s__.",
                html.escape(str(dlm_software_image)),
                extra={"object": dlm_software_image},
            )
            self._migrate_software_image(dlm_software_image, update_core_to_match_dlm, debug)
        self.migrate_content_type_references_to_new_model(
            dlm_software_image_ct,
            core_software_image_ct,
            hide_changelog_migrations,
        )
        # Create placeholder software image files for (software, device type) pairs that don't currently have image files
        # This is to satisfy Nautobot's 2.2 requirement that device can only have software assigned if there is a matching image
        self._create_placeholder_software_images(debug)

        # Need to add Core content type to custom fields before we can copy over values from the DLM Contact custom fields.
        self._migrate_custom_fields(dlm_contact_ct, core_contact_ct)
        # Migrate nautobot_device_lifecycle_mgmt.ContactLCM instances to extras.Contact
        for dlm_contact in ContactLCM.objects.filter(migrated_to_core_model_flag=False):
            self.logger.info(
                "Migrating DLM Contact object __%s__.",
                html.escape(str(dlm_contact)),
                extra={"object": dlm_contact},
            )
            self._migrate_contact(dlm_contact, update_core_to_match_dlm, debug)
        self.migrate_content_type_references_to_new_model(
            dlm_contact_ct,
            core_contact_ct,
            hide_changelog_migrations,
        )

        self.migrate_relationships(
            content_types={
                dlm_software_version_ct: core_software_version_ct,
                dlm_software_image_ct: core_software_image_ct,
                dlm_contact_ct: core_contact_ct,
            },
            debug=debug,
        )

        self._migrate_software_references()

        self._migrate_devices(update_core_to_match_dlm, remove_dangling_relationships)
        self._migrate_inventory_items(update_core_to_match_dlm, remove_dangling_relationships)

        # Emit warning if there are multiple DLM SoftwareLCM objects that migrated to the same Core SoftwareVersion object
        self._warn_on_duplicate_migrated_objects(SoftwareLCM, SoftwareVersion)
        # Emit warning if there are multiple DLM SoftwareImageLCM objects that migrated to the same Core SoftwareImageFile object
        self._warn_on_duplicate_migrated_objects(SoftwareImageLCM, SoftwareImageFile)
        # Emit warning if there are multiple DLM ContactLCM objects that migrated to the same Core Contact object
        self._warn_on_duplicate_migrated_objects(ContactLCM, Contact)

    def _warn_on_duplicate_migrated_objects(self, dlm_model, core_model):
        """Emit a warning if there are multiple DLM objects that migrated to the same Core object."""
        qs = (
            dlm_model.objects.filter(migrated_to_core_model_flag=True)
            .values("migrated_to_core_model")
            .annotate(count_migrated_to_core_model=Count("migrated_to_core_model"))
            .filter(count_migrated_to_core_model__gt=1)
        )
        api_url = reverse(get_route_for_model(dlm_model, "list", api=True))
        for instance in qs:
            self.logger.warning(
                "Multiple [(%s)](%s) DLM %s objects migrated to the same Core %s object __%s__.",
                html.escape(str(instance["count_migrated_to_core_model"])),
                html.escape(f"{api_url}?migrated_to_core_model={instance['migrated_to_core_model']}"),
                html.escape(str(dlm_model.__name__)),
                html.escape(str(core_model.__name__)),
                html.escape(str(core_model.objects.get(id=instance["migrated_to_core_model"]))),
            )

    def _migrate_software_version(self, dlm_software_version, update_core_to_match_dlm, debug):
        """Migrate DLM Software to Core SoftwareVersion."""
        core_software_version_ct = ContentType.objects.get_for_model(SoftwareVersion)
        dlm_software_version_ct = ContentType.objects.get_for_model(SoftwareLCM)
        status_active = Status.objects.get(name="Active")

        platform = dlm_software_version.device_platform

        dlm_soft_attrs = {
            "alias": dlm_software_version.alias,
            "release_date": dlm_software_version.release_date,
            "end_of_support_date": dlm_software_version.end_of_support,
            "documentation_url": dlm_software_version.documentation_url,
            "long_term_support": dlm_software_version.long_term_support,
            "pre_release": dlm_software_version.pre_release,
            "_custom_field_data": dlm_software_version.cf,
        }

        attrs_diff = {}
        core_software_version = None
        core_software_version_q = SoftwareVersion.objects.filter(
            platform=platform, version=dlm_software_version.version
        )
        if core_software_version_q.exists():
            core_software_version = core_software_version_q.first()
            self.logger.info(
                "Found existing Core SoftwareVersion __%s__ matching DLM Software __%s__.",
                html.escape(str(core_software_version)),
                html.escape(str(dlm_software_version)),
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
                if update_core_to_match_dlm:
                    setattr(core_software_version, attr_name, dlm_attr_value)
            if update_core_to_match_dlm and attrs_diff:
                self.logger.info(
                    "Updated existing Core SoftwareVersion __%s__ to match DLM Software __%s__. Diff before update __%s__.",
                    html.escape(str(core_software_version)),
                    html.escape(str(dlm_software_version)),
                    html.escape(str(attrs_diff)),
                    extra={"object": core_software_version},
                )
                attrs_diff.clear()
        else:
            core_software_version = SoftwareVersion(
                platform=dlm_software_version.device_platform,
                version=dlm_software_version.version,
                status=status_active,  # DLM model lacks a status field so we default to active
                **dlm_soft_attrs,
            )
            core_software_version.validated_save()

        # Dry-run and no existing Core Software Version found
        if core_software_version is None:
            return

        # Set migrated_to_core_model field on DLM Software object
        dlm_software_version.migrated_to_core_model = core_software_version
        dlm_software_version.migrated_to_core_model_flag = True
        dlm_software_version.validated_save()

        core_software_version.validated_save()

        if attrs_diff:
            self.logger.warning(
                "Attributes differ between DLM and Core SoftwareVersion objects: ```__%s__```",
                html.escape(str(attrs_diff)),
                extra={"object": core_software_version},
            )

        # Match the creation date of the Core Software with the DLM Software
        if core_software_version.created != dlm_software_version.created and update_core_to_match_dlm:
            core_software_version.created = dlm_software_version.created
            core_software_version.validated_save()
            core_software_version.refresh_from_db()
            self.logger.info(
                "Updated creation date of Core SoftwareVersion to match the corresponding DLM Software on SoftwareVersion __%s__",
                html.escape(str(core_software_version)),
                extra={"object": core_software_version},
            )

        core_software_version.refresh_from_db()

        # Create an object change to document migration
        if ObjectChange.objects.filter(
            changed_object_id=core_software_version.id,
            related_object_id=dlm_software_version.id,
        ).exists():
            if debug:
                self.logger.debug(
                    "DLM Software __%s__ to Core SoftwareVersion __%s__ migration change log already in place. Skipping.",
                    html.escape(str(dlm_software_version)),
                    html.escape(str(core_software_version)),
                )
            return

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
            html.escape(str(dlm_software_version)),
            html.escape(str(core_software_version)),
        )

    def _migrate_devices(self, update_core_to_match_dlm, remove_dangling_relationships):
        """Migrate "Software on Device" relationships to the Device.software_version foreign key."""
        device_ct = ContentType.objects.get_for_model(Device)
        dlm_software_version_ct = ContentType.objects.get_for_model(SoftwareLCM)

        for relationship_association in RelationshipAssociation.objects.filter(
            relationship__key="device_soft",
            source_type=dlm_software_version_ct,
            destination_type=device_ct,
        ):
            try:
                dlm_software_version = SoftwareLCM.objects.get(id=relationship_association.source_id)
            except SoftwareLCM.DoesNotExist:
                self.logger.error(
                    "Found Software Relationship Association for DLM Software with ID __%s__ that points to a non-existent SoftwareLCM object.",
                    html.escape(str(relationship_association.source_id)),
                )
                if remove_dangling_relationships:
                    relationship_association.delete()
                    self.logger.info(
                        "Deleted Software Relationship Association for DLM Software with ID __%s__ that points to a non-existent SoftwareLCM object.",
                        html.escape(str(relationship_association.source_id)),
                    )
                continue
            try:
                device = Device.objects.get(id=relationship_association.destination_id)
            except Device.DoesNotExist:
                self.logger.error(
                    "Found Software Relationship Association for DLM Software __%s__ that points to a non-existent Device with ID __%s__.",
                    html.escape(str(dlm_software_version)),
                    html.escape(str(relationship_association.destination_id)),
                    extra={"object": dlm_software_version},
                )
                if remove_dangling_relationships:
                    relationship_association.delete()
                    self.logger.info(
                        "Deleted Software Relationship Association for DLM Software __%s__ that points to a non-existent Device with ID __%s__.",
                        html.escape(str(dlm_software_version)),
                        html.escape(str(relationship_association.destination_id)),
                        extra={"object": dlm_software_version},
                    )
                continue
            existing_device_software = device.software_version
            if existing_device_software and existing_device_software != dlm_software_version.migrated_to_core_model:
                self.logger.warning(
                    "Device __%s__ is already assigned to Core SoftwareVersion __%s__ but DLM software relationship implies it should be assigned to __%s__.",
                    html.escape(str(device)),
                    html.escape(str(existing_device_software)),
                    html.escape(str(dlm_software_version.migrated_to_core_model)),
                    extra={"object": device},
                )
                if update_core_to_match_dlm:
                    device.software_version = dlm_software_version.migrated_to_core_model
                    device.validated_save()
                    self.logger.info(
                        "Updated SoftwareVersion assignment for device __%s__. Old SoftwareVersion: __%s__. New SoftwareVersion: __%s__.",
                        html.escape(str(device)),
                        html.escape(str(dlm_software_version.migrated_to_core_model)),
                        html.escape(str(existing_device_software)),
                        extra={"object": device},
                    )
            elif not existing_device_software:
                device.software_version = dlm_software_version.migrated_to_core_model
                device.validated_save()
                self.logger.info(
                    "Assigned SoftwareVersion __%s__ to device __%s__",
                    html.escape(str(dlm_software_version.migrated_to_core_model)),
                    html.escape(str(device)),
                    extra={"object": device},
                )

    def _migrate_inventory_items(self, update_core_to_match_dlm, remove_dangling_relationships):
        """Migrate "Software on InventoryItem" relationships to the InventoryItem.software_version foreign key."""
        inventory_item_ct = ContentType.objects.get_for_model(InventoryItem)
        dlm_software_version_ct = ContentType.objects.get_for_model(SoftwareLCM)

        for relationship_association in RelationshipAssociation.objects.filter(
            relationship__key="inventory_item_soft",
            source_type=dlm_software_version_ct,
            destination_type=inventory_item_ct,
        ):
            try:
                dlm_software_version = SoftwareLCM.objects.get(id=relationship_association.source_id)
            except SoftwareLCM.DoesNotExist:
                self.logger.error(
                    "Found Software Relationship Association for DLM Software with ID __%s__ that points to a non-existent SoftwareLCM object.",
                    html.escape(str(relationship_association.source_id)),
                )
                if remove_dangling_relationships:
                    relationship_association.delete()
                    self.logger.info(
                        "Deleted Software Relationship Association for DLM Software with ID __%s__ that points to a non-existent SoftwareLCM object.",
                        html.escape(str(relationship_association.source_id)),
                    )
                continue

            try:
                inventory_item = InventoryItem.objects.get(id=relationship_association.destination_id)
            except InventoryItem.DoesNotExist:
                self.logger.error(
                    "Found Software Relationship Association for DLM Software __%s__ that points to a non-existent InventoryItem with ID __%s__.",
                    html.escape(str(dlm_software_version)),
                    html.escape(str(relationship_association.destination_id)),
                    extra={"object": dlm_software_version},
                )
                if remove_dangling_relationships:
                    relationship_association.delete()
                    self.logger.info(
                        "Deleted Software Relationship Association for DLM Software __%s__ that points to a non-existent InventoryItem with ID __%s__.",
                        html.escape(str(dlm_software_version)),
                        html.escape(str(relationship_association.destination_id)),
                        extra={"object": dlm_software_version},
                    )
                continue
            existing_invitem_software = inventory_item.software_version
            if existing_invitem_software and existing_invitem_software != dlm_software_version.migrated_to_core_model:
                self.logger.warning(
                    "Inventory Item __%s__ is already assigned to Core SoftwareVersion __%s__ but DLM software relationship implies it should be assigned to __%s__.",
                    html.escape(str(inventory_item)),
                    html.escape(str(existing_invitem_software)),
                    html.escape(str(dlm_software_version.migrated_to_core_model)),
                    extra={"object": inventory_item},
                )
                if update_core_to_match_dlm:
                    inventory_item.software_version = dlm_software_version.migrated_to_core_model
                    inventory_item.validated_save()
                    self.logger.info(
                        "Updated SoftwareVersion assignment for inventory item __%s__. Old SoftwareVersion: __%s__. New SoftwareVersion: __%s__.",
                        html.escape(str(inventory_item)),
                        html.escape(str(dlm_software_version.migrated_to_core_model)),
                        html.escape(str(existing_invitem_software)),
                        extra={"object": inventory_item},
                    )
            elif not existing_invitem_software:
                inventory_item.software_version = dlm_software_version.migrated_to_core_model
                inventory_item.validated_save()
                self.logger.info(
                    "Assigned SoftwareVersion __%s__ to inventory item __%s__",
                    html.escape(str(dlm_software_version.migrated_to_core_model)),
                    html.escape(str(inventory_item)),
                    extra={"object": inventory_item},
                )

    def _migrate_contact(self, dlm_contact: ContactLCM, update_core_to_match_dlm, debug):  # pylint: disable=too-many-locals, too-many-branches
        """Migrates DLM Contact object to Core Contact."""
        dlm_contact_ct = ContentType.objects.get_for_model(ContactLCM)
        dlm_contract_ct = ContentType.objects.get_for_model(ContractLCM)
        core_contact_ct = ContentType.objects.get_for_model(Contact)
        contact_association_ct = ContentType.objects.get_for_model(ContactAssociation)

        status_active, _ = Status.objects.get_or_create(name="Active")

        dlm_contact_attrs = {
            "address": dlm_contact.address,
            "comments": dlm_contact.comments,
            "_custom_field_data": dlm_contact.cf,
        }

        attrs_diff = {}
        core_contact = None
        core_contact_q = Contact.objects.filter(name=dlm_contact.name, phone=dlm_contact.phone, email=dlm_contact.email)
        if core_contact_q.exists():
            core_contact = core_contact_q.first()
            self.logger.info(
                "Found existing Core Contact __%s__ matching DLM Contact __%s__.",
                html.escape(str(core_contact)),
                html.escape(str(dlm_contact)),
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
                if update_core_to_match_dlm:
                    setattr(core_contact, attr_name, dlm_attr_value)
            if update_core_to_match_dlm and attrs_diff:
                self.logger.info(
                    "Updated existing Core Contact __%s__ to match DLM Contact __%s__. Diff before update __%s__.",
                    html.escape(str(core_contact)),
                    html.escape(str(dlm_contact)),
                    html.escape(str(attrs_diff)),
                    extra={"object": core_contact},
                )
                attrs_diff.clear()
        else:
            core_contact = Contact(
                name=dlm_contact.name,
                phone=dlm_contact.phone,
                email=dlm_contact.email,
                **dlm_contact_attrs,
            )
            core_contact.validated_save()

        if core_contact is None:
            return

        # Set migrated_to_core_model field on DLM Contact object
        dlm_contact.migrated_to_core_model = core_contact
        dlm_contact.migrated_to_core_model_flag = True
        dlm_contact.validated_save()

        core_contact.validated_save()

        if attrs_diff:
            self.logger.warning(
                "Attributes differ between DLM and Core Contact objects: ```__%s__```",
                html.escape(str(attrs_diff)),
                extra={"object": core_contact},
            )

        # Match the creation date of the Core Software with the DLM Software
        if core_contact.created != dlm_contact.created:
            core_contact.created = dlm_contact.created
            core_contact.validated_save()
            core_contact.refresh_from_db()
            self.logger.info(
                "Updated creation date of Core Contact __%s__ to match the corresponding DLM Contact",
                html.escape(str(core_contact)),
                extra={"object": core_contact},
            )

        # Migrate ContactLCM types to Core Roles
        contact_association_role, created = Role.objects.get_or_create(name=dlm_contact.type)
        contact_association_role.content_types.add(contact_association_ct)
        if created:
            self.logger.info(
                "Role __%s__ created to match the DLM Contact Type.",
                html.escape(str(dlm_contact.type)),
            )

        # Recreate the DLM Contact -> Contract association with Core Contact -> Contract
        _, created = ContactAssociation.objects.get_or_create(
            contact=core_contact,
            associated_object_id=dlm_contact.contract.id,
            associated_object_type=dlm_contract_ct,
            role=contact_association_role,
            defaults={"status": status_active},
        )
        if created:
            self.logger.info(
                "Contact Association between Core Contact __%s__ and DLM Contract __%s__ created.",
                html.escape(str(core_contact)),
                html.escape(str(dlm_contact.contract)),
            )

        # Create an object change to document migration
        _, created = ObjectChange.objects.get_or_create(
            changed_object_id=core_contact.id,
            changed_object_type=core_contact_ct,
            related_object_id=dlm_contact.id,
            related_object_type=dlm_contact_ct,
            defaults={
                "action": ObjectChangeActionChoices.ACTION_UPDATE,
                "change_context": ObjectChangeEventContextChoices.CONTEXT_ORM,
                "change_context_detail": "Migrated from Nautobot App Device Lifecycle Management",
                "object_data": serialize_object(core_contact),
                "object_data_v2": serialize_object_v2(core_contact),
                "object_repr": str(core_contact)[:CHANGELOG_MAX_OBJECT_REPR],
                "request_id": common_objectchange_request_id,
                "user": None,
                "user_name": "Undefined",
            },
        )
        if created:
            self.logger.info(
                "DLM Contact __%s__ to Core Contact __%s__ migration change log created.",
                html.escape(str(dlm_contact)),
                html.escape(str(core_contact)),
            )
        elif debug:
            self.logger.debug(
                "DLM Contact __%s__ to Core Contact __%s__ migration change log already in place. Skipping.",
                html.escape(str(dlm_contact)),
                html.escape(str(core_contact)),
            )

    def _migrate_hashing_algorithm(self, value):
        """Migrate DLM SoftwareImage hashing algorithm from free-text field to Core SoftwareImageFile choice."""
        if value == "":
            return value

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

    def _migrate_software_image(self, dlm_software_image, update_core_to_match_dlm, debug):  # pylint: disable=too-many-locals, too-many-branches, too-many-statements
        """Migrate DLM SoftwareImage to Core SoftwareImageFile."""
        core_software_image_ct = ContentType.objects.get_for_model(SoftwareImageFile)
        dlm_software_image_ct = ContentType.objects.get_for_model(SoftwareImageLCM)
        device_ct = ContentType.objects.get_for_model(Device)
        inventory_item_ct = ContentType.objects.get_for_model(InventoryItem)
        status_active, _ = Status.objects.get_or_create(name="Active")

        image_file_name = dlm_software_image.image_file_name
        dlm_software_version = dlm_software_image.software
        # Dry-run will not have populated mappings for not-yet-migrated Software Versions
        core_software_version_id = dlm_software_version.migrated_to_core_model.id
        # Flag tracking whether hashing algorithm could be automatically migrated

        hashing_algorithm = self._migrate_hashing_algorithm(dlm_software_image.hashing_algorithm)

        if dlm_software_image.hashing_algorithm != "" and hashing_algorithm == "":
            self.logger.warning(
                "Unable to map hashing algorithm '%s' for software image '%s - %s' (%s). Please update the hashing algorithm manually.",
                html.escape(str(dlm_software_image.hashing_algorithm)),
                html.escape(str(dlm_software_image.software.version)),
                html.escape(str(dlm_software_image.image_file_name)),
                html.escape(str(dlm_software_image.id)),
            )

        dlm_soft_img_attrs = {
            "image_file_checksum": dlm_software_image.image_file_checksum,
            "hashing_algorithm": hashing_algorithm,
            "download_url": dlm_software_image.download_url,
            "default_image": dlm_software_image.default_image,
            "_custom_field_data": dlm_software_image.cf or {},
        }

        attrs_diff = {}
        core_software_image = None
        core_software_image_q = SoftwareImageFile.objects.filter(
            image_file_name=image_file_name, software_version=core_software_version_id
        )
        if core_software_image_q.exists():
            core_software_image = core_software_image_q.first()
            self.logger.info(
                "Found existing Core SoftwareImageFile __%s__ matching DLM SoftwareImage __%s__.",
                html.escape(str(core_software_image)),
                html.escape(str(dlm_software_image)),
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
                if update_core_to_match_dlm:
                    setattr(core_software_image, attr_name, dlm_attr_value)
            if update_core_to_match_dlm and attrs_diff:
                self.logger.info(
                    "Updated existing Core SoftwareImageFile __%s__ to match DLM SoftwareImage __%s__. Diff before update __%s__.",
                    html.escape(str(core_software_image)),
                    html.escape(str(dlm_software_image)),
                    html.escape(str(attrs_diff)),
                    extra={"object": core_software_image},
                )
                attrs_diff.clear()
        else:
            core_software_image = SoftwareImageFile(
                software_version_id=core_software_version_id,
                image_file_name=image_file_name,
                status=status_active,  # DLM model lacks a status field so we default to active
                **dlm_soft_img_attrs,
            )
            core_software_image.validated_save()

        # Dry-run and no existing Core SoftwareImageFile found
        if core_software_image is None:
            return

        # Set migrated_to_core_model field on DLM SoftwareImage object
        dlm_software_image.migrated_to_core_model = core_software_image
        dlm_software_image.migrated_to_core_model_flag = True
        dlm_software_image.validated_save()

        core_software_image.validated_save()

        if attrs_diff:
            self.logger.warning(
                "Attributes differ between DLM and Core SoftwareImageFile objects: ```__%s__```",
                html.escape(str(attrs_diff)),
                extra={"object": core_software_image},
            )

        dtypes_in_dlm_not_in_core = set(dlm_software_image.device_types.all()) - set(
            core_software_image.device_types.all()
        )
        if dtypes_in_dlm_not_in_core:
            self.logger.info(
                "Core SoftwareImageFile __%s__ is missing DLM SoftwareImage DeviceType assignments __%s__",
                html.escape(str(core_software_image)),
                html.escape(str(", ".join(str(d) for d in dtypes_in_dlm_not_in_core))),
                extra={"object": core_software_image},
            )
            for dtype in dtypes_in_dlm_not_in_core:
                core_software_image.device_types.add(dtype)

        # Work around created field's auto_now_add behavior
        if core_software_image.created != dlm_software_image.created and update_core_to_match_dlm:
            core_software_image.created = dlm_software_image.created
            core_software_image.validated_save()
            core_software_image.refresh_from_db()
            self.logger.info(
                "Updated creation date of Core SoftwareImageFile to match the corresponding DLM SoftwareImage on SoftwareImageFile __%s__",
                html.escape(str(core_software_image)),
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
                    html.escape(str(device)),
                    html.escape(str(core_software_image)),
                    extra={"object": core_software_image},
                )
                device.software_image_files.add(core_software_image)
                self.logger.info(
                    "SoftwareImage __%s__ assigned to Device __%s__.",
                    html.escape(str(core_software_image)),
                    html.escape(str(device)),
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
                    html.escape(str(inventory_item)),
                    html.escape(str(core_software_image)),
                    extra={"object": core_software_image},
                )
                inventory_item.software_image_files.add(core_software_image)
                self.logger.info(
                    "SoftwareImage __%s__ assigned to InventoryItem __%s__.",
                    html.escape(str(core_software_image)),
                    html.escape(str(inventory_item)),
                    extra={"object": core_software_image},
                )

        core_software_image.refresh_from_db()

        # Create an object change to document migration
        if ObjectChange.objects.filter(
            changed_object_id=core_software_image.id,
            related_object_id=dlm_software_image.id,
        ).exists():
            if debug:
                self.logger.debug(
                    "DLM SoftwareImage __%s__ to Core SoftwareImageFile __%s__ migration change log already in place. Skipping.",
                    html.escape(str(dlm_software_image)),
                    html.escape(str(core_software_image)),
                )
            return

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
            html.escape(str(dlm_software_image)),
            html.escape(str(core_software_image)),
        )

    def migrate_content_type_references_to_new_model(self, old_ct, new_ct, hide_changelog_migrations):  # pylint: disable=too-many-locals, too-many-branches, too-many-statements
        """When replacing a model, this will update references to the content type on related models such as tags and object changes.

        This also updates the primary key references.

        This will replace the old content type with the new content type on the following models:
            - ComputedField.content_type
            - CustomLink.content_type
            - ExportTemplate.content_type
            - Note.assigned_object_type
            - ObjectChange.changed_object_type
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
            hide_changelog_migrations (bool): If True, do not log migrations of ObjectChange objects.

        """
        # Migrate ComputedField content type
        for computed_field in ComputedField.objects.filter(content_type=old_ct):
            self.logger.info(
                "The Computed Field __%s__ will be migrated to Core model __%s__",
                html.escape(str(computed_field.label)),
                html.escape(str(new_ct)),
            )
            computed_field.content_type = new_ct
            computed_field.validated_save()

        # Migrate CustomLink content type
        for custom_link in CustomLink.objects.filter(content_type=old_ct):
            self.logger.info(
                "The Custom Link __%s__ will be migrated to Core model __%s__",
                html.escape(str(custom_link.name)),
                html.escape(str(new_ct)),
            )
            custom_link.content_type = new_ct
            custom_link.validated_save()

        # Migrate ExportTemplate content type - skip git export templates
        for export_template in ExportTemplate.objects.filter(content_type=old_ct, owner_content_type=None):
            self.logger.info(
                "The Export Template __%s__ will be migrated to Core model __%s__",
                html.escape(str(export_template.name)),
                html.escape(str(new_ct)),
            )
            export_template.content_type = new_ct
            export_template.validated_save()

        # Migrate JobButton content type
        for job_button in JobButton.objects.filter(content_types=old_ct).exclude(content_types=new_ct):
            self.logger.info(
                "The Job Button __%s__ will be migrated to Core model __%s__",
                html.escape(str(job_button.name)),
                html.escape(str(new_ct)),
            )
            job_button.content_types.add(new_ct)

        # Migrate JobHook content type
        for job_hook in JobHook.objects.filter(content_types=old_ct).exclude(content_types=new_ct):
            self.logger.info(
                "The Job Hook __%s__ will be migrated to Core model __%s__",
                html.escape(str(job_hook.name)),
                html.escape(str(new_ct)),
            )
            job_hook.content_types.add(new_ct)

        # Migrate Note content type
        for note in Note.objects.filter(assigned_object_type=old_ct):
            self.logger.info(
                "The Note __%s__ will be migrated to Core model __%s__",
                html.escape(str(note)),
                html.escape(str(new_ct)),
            )
            old_assigned_object = note.assigned_object
            if getattr(old_assigned_object, "migrated_to_core_model", None):
                note.assigned_object = old_assigned_object.migrated_to_core_model
                note.validated_save()

        # Migrate ObjectChange content type
        for object_change in ObjectChange.objects.filter(changed_object_type=old_ct):
            if not hide_changelog_migrations:
                self.logger.info(
                    "The Object Change __%s__ will be migrated to Core model __%s__",
                    html.escape(str(object_change)),
                    html.escape(str(new_ct)),
                )
            # We might have a reference to deleted object so need to check if it exists
            object_change.changed_object_type = new_ct
            if not old_ct.model_class().objects.filter(id=object_change.changed_object_id).exists():
                if not hide_changelog_migrations:
                    self.logger.warning(
                        "The DLM Software object __%s__ referenced in Object Change __%s__ is gone. Updating content type only to __%s__",
                        html.escape(str(object_change.changed_object_id)),
                        html.escape(str(object_change)),
                        html.escape(str(new_ct)),
                    )
            else:
                old_changed_object = old_ct.model_class().objects.filter(id=object_change.changed_object_id).first()
                if getattr(old_changed_object, "migrated_to_core_model", None):
                    object_change.changed_object_id = old_changed_object.migrated_to_core_model_id
            object_change.validated_save()

        # Migrate Status content type
        for status in Status.objects.filter(content_types=old_ct).exclude(content_types=new_ct):
            self.logger.info(
                "The Status __%s__ will be migrated to Core model __%s__",
                html.escape(str(status.name)),
                html.escape(str(new_ct)),
            )
            status.content_types.add(new_ct)

        # Migrate Tag content type
        for tag in Tag.objects.filter(content_types=old_ct).exclude(content_types=new_ct):
            self.logger.info(
                "The Tag __%s__ will be migrated to Core model __%s__",
                html.escape(str(tag.name)),
                html.escape(str(new_ct)),
            )
            tag.content_types.add(new_ct)

        # Migrate TaggedItem content type
        for tagged_item in TaggedItem.objects.filter(content_type=old_ct):
            self.logger.info(
                "The Tagged Item __%s__ will be migrated to Core model __%s__",
                html.escape(str(tagged_item)),
                html.escape(str(new_ct)),
            )
            old_object = tagged_item.content_object
            if getattr(old_object, "migrated_to_core_model", None):
                tagged_item.content_object_id = old_object.migrated_to_core_model_id
            tagged_item.content_type = new_ct
            tagged_item.validated_save()

        # Fix tags that were implemented incorrectly and didn't enforce content type
        # If a tag is related to an instance of a model, make sure the content type for that model exists on the tag object
        for tag_id in TaggedItem.objects.filter(content_type=new_ct).values_list("tag_id", flat=True).distinct():
            try:
                tag = Tag.objects.get(id=tag_id)
                if not tag.content_types.filter(id=new_ct.id).exists():
                    tag.content_types.add(new_ct)
            except Tag.DoesNotExist:
                pass

        # Migrate WebHook content type
        for web_hook in Webhook.objects.filter(content_types=old_ct).exclude(content_types=new_ct):
            self.logger.info(
                "The Web Hook __%s__ will be migrated to Core model __%s__",
                html.escape(str(web_hook.name)),
                html.escape(str(new_ct)),
            )
            web_hook.content_types.add(new_ct)

        # Migrate ObjectPermission content type
        for object_permission in ObjectPermission.objects.filter(object_types=old_ct).exclude(object_types=new_ct):
            self.logger.info(
                "The Object Permission __%s__ will be migrated to Core model __%s__",
                html.escape(str(object_permission)),
                html.escape(str(new_ct)),
            )
            object_permission.object_types.add(new_ct)

    def migrate_relationships(self, content_types, debug):
        """Migrate Relationships and RelationshipAssociations from the old models to the new models.

        Relationships will be renamed to `{foo}_old` and a new relationship called `{foo}` will be created
        with the same data and the `source_type`/`destination_type` will be updated with the new model's content type.
        RelationshipAssociations will be duplicated and the content types updated as well.

        """
        # These relationships are migrated separately as they follow specific business logic
        excluded_relationships = ("device_soft", "inventory_item_soft")
        # Migrate Relationship content type
        for old_relationship in Relationship.objects.filter(
            Q(source_type__in=content_types.keys()) | Q(destination_type__in=content_types.keys())
        ).exclude(key__in=excluded_relationships):
            if (
                old_relationship.key.endswith("_old")
                and Relationship.objects.filter(key=old_relationship.key[:-4]).exists()
            ) or (
                old_relationship.label.endswith(" (old)")
                and Relationship.objects.filter(label=old_relationship.label[:-6]).exists()
            ):
                if debug:
                    self.logger.debug(
                        "The Relationship __%s__ has already been migrated. Skipping migration of this Relationship.",
                        html.escape(str(old_relationship.label)),
                    )
                continue

            new_ct = content_types.get(
                old_relationship.source_type, content_types.get(old_relationship.destination_type)
            )
            self.logger.info(
                "The Relationship __%s__ will be migrated to Core model __%s__",
                html.escape(str(old_relationship.label)),
                html.escape(str(new_ct)),
            )

            # Duplicate the relationship with the new content type
            new_relationship = Relationship(
                key=old_relationship.key,
                label=old_relationship.label,
                description=old_relationship.description,
                type=old_relationship.type,
                required_on=old_relationship.required_on,
                source_type=content_types.get(old_relationship.source_type, old_relationship.source_type),
                source_label=old_relationship.source_label,
                source_filter=old_relationship.source_filter,
                source_hidden=old_relationship.source_hidden,
                destination_type=content_types.get(
                    old_relationship.destination_type, old_relationship.destination_type
                ),
                destination_label=old_relationship.destination_label,
                destination_filter=old_relationship.destination_filter,
                destination_hidden=old_relationship.destination_hidden,
                advanced_ui=old_relationship.advanced_ui,
            )

            # Rename relationship key to {key}_old, rename label to "{label} (old)" and hide the old relationship in the ui
            old_relationship.key = f"{old_relationship.key}_old"
            old_relationship.label = f"{old_relationship.label} (old)"
            old_relationship.source_hidden = True
            old_relationship.destination_hidden = True
            old_relationship.validated_save()
            new_relationship.validated_save()

            # Create duplicate relationshipassociations with new content type
            for relationship_association in RelationshipAssociation.objects.filter(
                relationship=old_relationship
            ).exclude(relationship__key__in=excluded_relationships):
                self.logger.info(
                    "The Relationship Association __%s__ will be migrated to Core model __%s__",
                    html.escape(str(relationship_association)),
                    html.escape(str(new_ct)),
                )

                RelationshipAssociation.objects.create(
                    relationship=new_relationship,
                    source=getattr(
                        relationship_association.source,
                        "migrated_to_core_model",
                        relationship_association.source,
                    ),
                    destination=getattr(
                        relationship_association.destination,
                        "migrated_to_core_model",
                        relationship_association.destination,
                    ),
                )

    def _create_placeholder_software_images(self, debug):
        """Create placeholder software image files for software that is used by devices but no image currently exists."""
        if version.parse(settings.VERSION) >= version.parse("2.3.1"):
            if debug:
                self.logger.debug(
                    "Skipping placeholder SoftwareImageFile creation. Nautobot version is 2.3.1 or later."
                )
            return

        if debug:
            self.logger.debug(
                "Creating placeholder SoftwareImageFiles for SoftwareVersions used by Devices without SoftwareImageFiles."
            )

        status_active, _ = Status.objects.get_or_create(name="Active")

        device_ct = ContentType.objects.get_for_model(Device)
        dlm_software_version_ct = ContentType.objects.get_for_model(SoftwareLCM)

        for relationship_association in RelationshipAssociation.objects.filter(
            relationship__key="device_soft",
            source_type=dlm_software_version_ct,
            destination_type=device_ct,
        ):
            try:
                old_software = relationship_association.source
                software_version = old_software.migrated_to_core_model
            except SoftwareLCM.DoesNotExist:
                continue
            try:
                device = relationship_association.destination
                device_type = device.device_type
            except Device.DoesNotExist:
                continue

            if SoftwareImageFile.objects.filter(software_version=software_version, device_types=device_type).exists():
                continue
            image_soft_and_dt = f"{slugify(software_version.version)}-{slugify(device_type.model)}"[:227]
            image_file_name = f"{image_soft_and_dt}-dlm-migrations-placeholder"
            if SoftwareImageFile.objects.filter(image_file_name=image_file_name).exists():
                invalid_soft_image = SoftwareImageFile.objects.filter(image_file_name=image_file_name).first()
                self.logger.error(
                    "Found incorrectly assigned SoftwareImageVersion __%s__. This Image should be assigned to Software __%s__ and DeviceType __%s__.",
                    html.escape(str(invalid_soft_image)),
                    html.escape(str(software_version)),
                    html.escape(str(device_type)),
                    extra={"object": invalid_soft_image},
                )
                continue
            self.logger.warning(
                "Found SoftwareVersion __%s__, assigned to Devices, that doesn't have a SoftwareImageFile matching DeviceType __%s__.",
                html.escape(str(software_version)),
                html.escape(str(device_type)),
            )
            software_image = SoftwareImageFile(
                software_version=software_version,
                image_file_name=image_file_name,
                status=status_active,
            )
            software_image.validated_save()
            note = (
                "This SoftwareImageFile was created as a placeholder. In Nautobot v2.2.0 - v2.3.0, a SoftwareImageFile "
                "associated with a DeviceType is required before any Devices of that DeviceType can be associated with a SoftwareVersion. "
                "This placeholder can be deleted after upgrading to Nautobot v2.3.1 or later."
            )
            Note.objects.create(
                assigned_object=software_image,
                user=None,
                note=note,
            )
            device_type.software_image_files.add(software_image)
            self.logger.warning(
                "Created placeholder SoftwareImageFile __%s__ assigned to DeviceType __%s__.",
                html.escape(str(software_image)),
                html.escape(str(device_type)),
                extra={"object": software_image},
            )

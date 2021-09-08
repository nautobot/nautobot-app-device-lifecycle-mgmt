"""Jobs for the LifeCycle Management plugin."""

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from nautobot.dcim.models import Device, InventoryItem
from nautobot.extras.jobs import Job
from nautobot.extras.models import RelationshipAssociation

from .models import SoftwareLCM, ValidatedSoftwareLCM


name = "Device/Software Lifecycle Reporting"  # pylint: disable=invalid-name


class SoftwareComplianceCheck(Job):
    """Checks if devices and inventory items run validated software version."""

    name = "Software Compliance Check"
    description = "Validates software version on devices and inventory items."
    read_only = True

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta class for the job."""

        commit_default = False

    @staticmethod
    def get_object_software(soft_relation_name, obj_model, dst_obj_id):
        """Get software assigned to the object."""
        try:
            obj_soft_relation = RelationshipAssociation.objects.get(
                relationship__slug=soft_relation_name,
                destination_type=ContentType.objects.get_for_model(obj_model),
                destination_id=dst_obj_id,
            )
            obj_soft = SoftwareLCM.objects.get(id=obj_soft_relation.source_id)
        except (RelationshipAssociation.DoesNotExist, SoftwareLCM.DoesNotExist):
            obj_soft = None

        return obj_soft

    @staticmethod
    def valid_software(validated_soft_list, software):
        """Check whether given software version is on the validated software list."""
        if not (validated_soft_list and software):
            return False

        soft_valid_obj = validated_soft_list.filter(software_id=software)
        return soft_valid_obj.exists() and soft_valid_obj[0].valid

    def test_device_software_validity(self) -> None:
        """Check if software assigned to each device is valid. If no software is assigned return warning message."""
        for device in Device.objects.all():
            valid_soft_filter = Q(
                assigned_to_content_type=ContentType.objects.get(app_label="dcim", model="device"),
                assigned_to_object_id=device.pk,
            ) | Q(
                assigned_to_content_type=ContentType.objects.get(app_label="dcim", model="devicetype"),
                assigned_to_object_id=device.device_type.pk,
            )
            validsoft_list = ValidatedSoftwareLCM.objects.filter(valid_soft_filter)
            device_software = SoftwareComplianceCheck.get_object_software("device_soft", Device, device.pk)

            if SoftwareComplianceCheck.valid_software(validsoft_list, device_software):
                self.log_success(
                    device,
                    f"Device {device.name} is running validated software: {device_software}.",
                )
            else:
                if device_software is None:
                    msg = f"Device {device.name} does not have software assigned."
                    self.log_warning(device, msg)
                else:
                    msg = f"Device {device.name} is running invalid software: {device_software}."
                    self.log_failure(device, msg)

    def test_inventory_item_software_validity(self):
        """Check if software assigned to each inventory item is valid. If no software is assigned return warning message."""
        for inventoryitem in InventoryItem.objects.all():
            valid_soft_filter = Q(
                assigned_to_content_type=ContentType.objects.get(app_label="dcim", model="inventoryitem"),
                assigned_to_object_id=inventoryitem.pk,
            )
            validsoft_list = ValidatedSoftwareLCM.objects.filter(valid_soft_filter)
            inventoryitem_software = SoftwareComplianceCheck.get_object_software(
                "inventory_item_soft", InventoryItem, inventoryitem.pk
            )

            if SoftwareComplianceCheck.valid_software(validsoft_list, inventoryitem_software):
                self.log_success(
                    inventoryitem,
                    f"InventoryItem {inventoryitem.name} is running validated software: {inventoryitem_software}.",
                )
            else:
                if inventoryitem_software is None:
                    msg = f"InventoryItem {inventoryitem.name} does not have software assigned."
                    self.log_warning(inventoryitem, msg)
                else:
                    msg = f"InventoryItem {inventoryitem.name} is running invalid software: {inventoryitem_software}."
                    self.log_failure(inventoryitem, msg)


jobs = [SoftwareComplianceCheck]

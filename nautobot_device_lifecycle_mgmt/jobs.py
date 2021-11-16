"""Jobs for the Lifecycle Management plugin."""

from nautobot.dcim.models import Device, InventoryItem
from nautobot.extras.jobs import Job

from .software import DeviceSoftware, InventoryItemSoftware


name = "Device/Software Lifecycle Reporting"  # pylint: disable=invalid-name


class SoftwareComplianceCheck(Job):
    """Checks if devices and inventory items run validated software version."""

    name = "Software Compliance Check"
    description = "Validates software version on devices and inventory items."
    read_only = True

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta class for the job."""

        commit_default = False

    def test_device_software_validity(self) -> None:
        """Check if software assigned to each device is valid. If no software is assigned return warning message."""
        for device in Device.objects.all():
            device_software = DeviceSoftware(device)
            software_version = device_software.software

            if device_software.validate_software():
                self.log_success(
                    device,
                    f"Device {device.name} is running validated software: {software_version}.",
                )
            else:
                if software_version is None:
                    msg = f"Device {device.name} does not have software assigned."
                    self.log_warning(device, msg)
                else:
                    msg = f"Device {device.name} is running invalid software: {software_version}."
                    self.log_failure(device, msg)

    def test_inventory_item_software_validity(self):
        """Check if software assigned to each inventory item is valid. If no software is assigned return warning message."""
        for inventoryitem in InventoryItem.objects.all():
            inventoryitem_software = InventoryItemSoftware(inventoryitem)
            software_version = inventoryitem_software.software

            if inventoryitem_software.validate_software():
                self.log_success(
                    inventoryitem,
                    f"InventoryItem {inventoryitem.name} is running validated software: {software_version}.",
                )
            else:
                if software_version is None:
                    msg = f"InventoryItem {inventoryitem.name} does not have software assigned."
                    self.log_warning(inventoryitem, msg)
                else:
                    msg = f"InventoryItem {inventoryitem.name} is running invalid software: {software_version}."
                    self.log_failure(inventoryitem, msg)


jobs = [SoftwareComplianceCheck]

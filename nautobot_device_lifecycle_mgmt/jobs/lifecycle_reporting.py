# pylint: disable=logging-not-lazy, consider-using-f-string
"""Jobs for the Lifecycle Management app."""
from datetime import datetime

from nautobot.dcim.models import Device, InventoryItem
from nautobot.extras.jobs import Job

from nautobot_device_lifecycle_mgmt import choices
from nautobot_device_lifecycle_mgmt.models import (
    DeviceSoftwareValidationResult,
    InventoryItemSoftwareValidationResult,
    ValidatedSoftwareLCM,
)
from nautobot_device_lifecycle_mgmt.software import DeviceSoftware, InventoryItemSoftware

name = "Device/Software Lifecycle Reporting"  # pylint: disable=invalid-name


class DeviceSoftwareValidationFullReport(Job):
    """Checks if devices run validated software version."""

    name = "Device Software Validation Report"
    description = "Validates software version on devices."
    read_only = False

    class Meta:
        """Meta class for the job."""

        has_sensitive_variables = False

    def run(self) -> None:  # pylint: disable=arguments-differ
        """Check if software assigned to each device is valid. If no software is assigned return warning message."""
        devices = Device.objects.all()
        job_run_time = datetime.now()

        for device in devices:
            device_software = DeviceSoftware(device)

            validate_obj, _ = DeviceSoftwareValidationResult.objects.get_or_create(device=device)
            validate_obj.is_validated = device_software.validate_software()
            validate_obj.valid_software.set(ValidatedSoftwareLCM.objects.get_for_object(device))
            validate_obj.software = device_software.software
            validate_obj.last_run = job_run_time
            validate_obj.run_type = choices.ReportRunTypeChoices.REPORT_FULL_RUN
            validate_obj.validated_save()

        self.logger.info("Performed validation on: %d devices.", devices.count())


class InventoryItemSoftwareValidationFullReport(Job):
    """Checks if inventory items run validated software version."""

    name = "Inventory Item Software Validation Report"
    description = "Validates software version on inventory items."
    read_only = False

    class Meta:
        """Meta class for the job."""

        has_sensitive_variables = False

    def run(self):  # pylint: disable=arguments-differ
        """Check if software assigned to each inventory item is valid. If no software is assigned return warning message."""
        inventory_items = InventoryItem.objects.all()
        job_run_time = datetime.now()

        for inventoryitem in inventory_items:
            inventoryitem_software = InventoryItemSoftware(inventoryitem)

            validate_obj, _ = InventoryItemSoftwareValidationResult.objects.get_or_create(inventory_item=inventoryitem)
            validate_obj.is_validated = inventoryitem_software.validate_software()
            validate_obj.valid_software.set(ValidatedSoftwareLCM.objects.get_for_object(inventoryitem))
            validate_obj.software = inventoryitem_software.software
            validate_obj.last_run = job_run_time
            validate_obj.run_type = choices.ReportRunTypeChoices.REPORT_FULL_RUN
            validate_obj.validated_save()

        self.logger.info("Performed validation on: %d inventory items." % inventory_items.count())

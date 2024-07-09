# pylint: disable=logging-not-lazy, consider-using-f-string
"""Jobs for the Lifecycle Management app."""
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from nautobot.dcim.models import Device, InventoryItem
from nautobot.extras.jobs import Job

from nautobot_device_lifecycle_mgmt import choices
from nautobot_device_lifecycle_mgmt.models import (
    DeviceHardwareNoticeResult,
    DeviceSoftwareValidationResult,
    HardwareLCM,
    InventoryItemSoftwareValidationResult,
    ValidatedSoftwareLCM,
)
from nautobot_device_lifecycle_mgmt.software import DeviceSoftware, InventoryItemSoftware

name = "Device/Software Lifecycle Reporting"  # pylint: disable=invalid-name


class DeviceHardwareNoticeFullReport(Job):
    """Checks if devices are linked to hardware notices."""

    name = "Device Hardware Notice Report"
    description = "Creates data for reporting on hardware notices."
    read_only = False

    class Meta:
        """Meta class for the job."""

        has_sensitive_variables = False

    def run(self) -> None:  # pylint: disable=arguments-differ
        """Check if device is affected by a hardware notice."""
        job_run_time = datetime.now()
        notice_count = 0
        device_count = 0

        # Process devices through HardwareLCM.device_type
        for notice in HardwareLCM.objects.all():
            if notice.device_type:
                devices_qs = Device.objects.filter(device_type=notice.device_type)
                for device in devices_qs:
                    try:
                        DeviceHardwareNoticeResult.objects.get(
                            device=device,
                            last_run=job_run_time,
                            run_type=choices.ReportRunTypeChoices.REPORT_FULL_RUN,
                        )
                        self.logger.warning(
                            f"Device {device} belongs to multiple hardware notices! Only the first processed result will be used."
                        )
                    except ObjectDoesNotExist:
                        if notice.end_of_support:
                            is_supported = datetime.today().date() <= notice.end_of_support
                        else:
                            is_supported = True
                        try:
                            hardware_notice_result, _ = DeviceHardwareNoticeResult.objects.get_or_create(device=device)
                            hardware_notice_result.hardware_notice = notice
                            hardware_notice_result.is_supported = is_supported
                            hardware_notice_result.last_run = job_run_time
                            hardware_notice_result.run_type = choices.ReportRunTypeChoices.REPORT_FULL_RUN
                            hardware_notice_result.validated_save()
                            device_count += 1
                        except Exception as err:
                            self.logger.error(f"Error creating hadware notice result {err}")
                notice_count += 1
        # Process all devices skipping devices already processed in the previous step
        for device in Device.objects.all():
            try:
                DeviceHardwareNoticeResult.objects.get(
                    device=device,
                    last_run=job_run_time,
                    run_type=choices.ReportRunTypeChoices.REPORT_FULL_RUN,
                )
                continue
            except ObjectDoesNotExist:
                try:
                    hardware_notice_result, _ = DeviceHardwareNoticeResult.objects.get_or_create(device=device)
                    hardware_notice_result.hardware_notice = None
                    hardware_notice_result.is_supported = True
                    hardware_notice_result.last_run = job_run_time
                    hardware_notice_result.run_type = choices.ReportRunTypeChoices.REPORT_FULL_RUN
                    hardware_notice_result.validated_save()
                    device_count += 1
                except Exception as err:
                    self.logger.error(f"Error creating hadware notice result {err}")

        self.logger.info(f"Processed {notice_count} hardware notices and {device_count} devices.")

    # TODO: CREATE INVENTORY ITEM JOB


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
        job_run_time = datetime.now()
        validation_count = 0

        for device in Device.objects.filter(software_version__isnull=True):
            validate_obj, _ = DeviceSoftwareValidationResult.objects.get_or_create(device=device)
            validate_obj.is_validated = False
            validate_obj.valid_software.set(ValidatedSoftwareLCM.objects.get_for_object(device))
            validate_obj.software = None
            validate_obj.last_run = job_run_time
            validate_obj.run_type = choices.ReportRunTypeChoices.REPORT_FULL_RUN
            validate_obj.validated_save()
            validation_count += 1

        for device in Device.objects.filter(software_version__isnull=False):
            device_software = DeviceSoftware(device)
            validate_obj, _ = DeviceSoftwareValidationResult.objects.get_or_create(device=device)
            validate_obj.is_validated = device_software.validate_software()
            validate_obj.valid_software.set(ValidatedSoftwareLCM.objects.get_for_object(device))
            validate_obj.software = device.software_version
            validate_obj.last_run = job_run_time
            validate_obj.run_type = choices.ReportRunTypeChoices.REPORT_FULL_RUN
            validate_obj.validated_save()
            validation_count += 1

        self.logger.info("Performed validation on: %d devices.", validation_count)


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
        job_run_time = datetime.now()
        validation_count = 0

        for inventoryitem in InventoryItem.objects.filter(software_version__isnull=True):
            validate_obj, _ = InventoryItemSoftwareValidationResult.objects.get_or_create(inventory_item=inventoryitem)
            validate_obj.is_validated = False
            validate_obj.valid_software.set(ValidatedSoftwareLCM.objects.get_for_object(inventoryitem))
            validate_obj.software = None
            validate_obj.last_run = job_run_time
            validate_obj.run_type = choices.ReportRunTypeChoices.REPORT_FULL_RUN
            validate_obj.validated_save()
            validation_count += 1

        for inventoryitem in InventoryItem.objects.filter(software_version__isnull=False):
            inventoryitem_software = InventoryItemSoftware(inventoryitem)
            validate_obj, _ = InventoryItemSoftwareValidationResult.objects.get_or_create(inventory_item=inventoryitem)
            validate_obj.is_validated = inventoryitem_software.validate_software()
            validate_obj.valid_software.set(ValidatedSoftwareLCM.objects.get_for_object(inventoryitem))
            validate_obj.software = inventoryitem.software_version
            validate_obj.last_run = job_run_time
            validate_obj.run_type = choices.ReportRunTypeChoices.REPORT_FULL_RUN
            validate_obj.validated_save()
            validation_count += 1

        self.logger.info("Performed validation on: %d inventory items." % validation_count)

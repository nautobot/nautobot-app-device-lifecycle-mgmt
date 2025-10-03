# pylint: disable=logging-not-lazy, consider-using-f-string
"""Jobs for the Lifecycle Management app."""

from datetime import datetime
from itertools import product

from nautobot.dcim.models import Device, InventoryItem, Platform
from nautobot.extras.jobs import Job, MultiObjectVar
from nautobot.tenancy.models import Tenant

from nautobot_device_lifecycle_mgmt import choices
from nautobot_device_lifecycle_mgmt.models import (
    DeviceHardwareNoticeResult,
    DeviceSoftwareValidationHistoricResult,
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
        devices_with_hw_notices_count = 0
        devices_without_hw_notices_count = 0

        # Process devices through HardwareLCM.device_type
        for notice in HardwareLCM.objects.all():
            if notice.device_type:
                devices_qs = Device.objects.filter(device_type=notice.device_type)
                for device in devices_qs:
                    is_supported = not notice.expired
                    try:
                        hardware_notice_result, _ = DeviceHardwareNoticeResult.objects.get_or_create(device=device)
                        hardware_notice_result.hardware_notice = notice
                        hardware_notice_result.is_supported = is_supported
                        hardware_notice_result.last_run = job_run_time
                        hardware_notice_result.run_type = choices.ReportRunTypeChoices.REPORT_FULL_RUN
                        hardware_notice_result.validated_save()
                        device_count += 1
                        devices_with_hw_notices_count += 1
                    except Exception as err:  # pylint: disable=broad-exception-caught
                        self.logger.error("Error creating hardware notice result %s", err)
                notice_count += 1
        self.logger.info("%s devices are affected by a hardware notice.", devices_with_hw_notices_count)
        # Process all devices skipping devices already processed in the previous step
        for device in Device.objects.exclude(device_hardware_notice__last_run=job_run_time):
            try:
                hardware_notice_result, _ = DeviceHardwareNoticeResult.objects.get_or_create(device=device)
                hardware_notice_result.hardware_notice = None
                hardware_notice_result.is_supported = True
                hardware_notice_result.last_run = job_run_time
                hardware_notice_result.run_type = choices.ReportRunTypeChoices.REPORT_FULL_RUN
                hardware_notice_result.validated_save()
                device_count += 1
                devices_without_hw_notices_count += 1
            except Exception as err:  # pylint: disable=broad-exception-caught
                self.logger.error("Error creating hadware notice result %s", err)
        self.logger.info("%s devices are not affected by a hardware notice.", devices_without_hw_notices_count)
        self.logger.info("Processed %s hardware notices and %s devices.", notice_count, device_count)

    # TODO: Create Inventory Item Report job (and related table, view, forms, filters etc.)


class DeviceSoftwareValidationReport(Job):
    """Checks if devices run validated software version."""

    name = "Device Software Validation Report"
    description = "Validates software version on devices."
    read_only = False

    # Add dropdowns for platform and tenant filters; Defaults to all platforms and tenants
    platform = MultiObjectVar(
        model=Platform,
        label="Platform",
        description="Filter by platform; defaults to all platforms",
        required=False,
    )
    tenant = MultiObjectVar(
        model=Tenant,
        label="Tenant",
        description="Filter by tenant; defaults to all tenants",
        required=False,
    )

    filters = [platform, tenant]

    class Meta:
        """Meta class for the job."""

        has_sensitive_variables = False

    def run(self, **filters) -> None:  # pylint: disable=arguments-differ, too-many-locals
        """Check if software assigned to each device is valid. If no software is assigned return warning message."""
        job_run_time = datetime.now()
        validation_count = 0

        versioned_devices = []  # Devices with software version
        non_versioned_devices = []  # Devices without software version

        # Get filters
        platforms = filters.get("platform")
        tenants = filters.get("tenant")

        # If no platforms or tenants are provided, use all platforms and tenants
        if not platforms:
            platforms = Platform.objects.all()
            all_platforms = True
        else:
            all_platforms = False

        if not tenants:
            tenants = Tenant.objects.all()
            all_tenants = True
        else:
            all_tenants = False

        if all_tenants and all_platforms:
            run_type = choices.ReportRunTypeChoices.REPORT_FULL_RUN
        else:
            run_type = choices.ReportRunTypeChoices.REPORT_FILTERED_RUN

        # Create history result
        history_result = DeviceSoftwareValidationHistoricResult.objects.create(
            date=job_run_time,
            filters={
                "platforms": [{"id": str(platform.id), "name": platform.name} for platform in platforms],
                "tenants": [{"id": str(tenant.id), "name": tenant.name} for tenant in tenants],
            },
            all_tenants=all_tenants,
            all_platforms=all_platforms,
            run_type=run_type,
        )

        # Get all combinations of platforms and tenants
        filtered_products = product(platforms, tenants)
        # Get versioned and non-versioned devices
        for platform, tenant in filtered_products:
            versioned_devices.extend(
                Device.objects.filter(platform_id=platform.id, tenant_id=tenant.id, software_version__isnull=False)
            )
            non_versioned_devices.extend(
                Device.objects.filter(platform_id=platform.id, tenant_id=tenant.id, software_version__isnull=True)
            )
        self.logger.info(
            "Found %d versioned devices and %d non-versioned devices.",
            len(versioned_devices),
            len(non_versioned_devices),
        )

        # Validate devices without software version
        for device in non_versioned_devices:
            validate_obj, _ = DeviceSoftwareValidationResult.objects.update_or_create(
                device=device, defaults={"is_validated": False, "software": None, "run_type": run_type}
            )
            validate_obj.is_validated = False
            validate_obj.software = None
            validate_obj.last_run = job_run_time
            validate_obj.valid_software.set(ValidatedSoftwareLCM.objects.get_for_object(device))
            validate_obj.validated_save()
            validation_count += 1

            # Add the current validation result to the historic results
            history_result.device_validation_results.append(
                {
                    "device": str(validate_obj.device.id),
                    "is_validated": validate_obj.is_validated,
                    "valid_software": [str(software.id) for software in validate_obj.valid_software.all()]
                    if validate_obj.valid_software.exists()
                    else [],
                }
            )
            history_result.save()

        # Validate devices with software version
        for device in versioned_devices:
            device_software = DeviceSoftware(device)
            validate_obj, _ = DeviceSoftwareValidationResult.objects.update_or_create(
                device=device,
                defaults={
                    "is_validated": device_software.validate_software(),
                    "software": device.software_version,
                    "run_type": run_type,
                },
            )
            validate_obj.is_validated = device_software.validate_software()
            validate_obj.software = device.software_version
            validate_obj.last_run = job_run_time
            validate_obj.valid_software.set(ValidatedSoftwareLCM.objects.get_for_object(device))
            validate_obj.validated_save()
            validation_count += 1

            # Add the current validation result to the historic results
            history_result.device_validation_results.append(
                {
                    "device": str(validate_obj.device.id),
                    "is_validated": validate_obj.is_validated,
                    "software": str(validate_obj.software.id) if validate_obj.software else None,
                    "valid_software": [str(software.id) for software in validate_obj.valid_software.all()]
                    if validate_obj.valid_software.exists()
                    else [],
                }
            )
            history_result.save()

        self.logger.info("Performed validation on: %d devices.", validation_count)

        history_result.validated_save()
        self.logger.info("Created historic result.")


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

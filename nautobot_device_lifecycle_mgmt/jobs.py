"""Jobs for the Lifecycle Management plugin."""
from datetime import datetime

from nautobot.dcim.models import Device, InventoryItem
from nautobot.extras.jobs import Job, StringVar
from nautobot.extras.models import Relationship, RelationshipAssociation

from nautobot_device_lifecycle_mgmt import choices
from .models import DeviceSoftwareValidationResult, InventoryItemSoftwareValidationResult, CVELCM, VulnerabilityLCM
from .software import DeviceSoftware, InventoryItemSoftware


name = "Device/Software Lifecycle Reporting"  # pylint: disable=invalid-name


class DeviceSoftwareValidationFullReport(Job):
    """Checks if devices run validated software version."""

    name = "Device Software Validation Report"
    description = "Validates software version on devices."
    read_only = False

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta class for the job."""

        commit_default = True

    def test_device_software_validity(self) -> None:
        """Check if software assigned to each device is valid. If no software is assigned return warning message."""
        devices = Device.objects.all()
        job_run_time = datetime.now()

        for device in devices:
            device_software = DeviceSoftware(device)

            validate_obj, _ = DeviceSoftwareValidationResult.objects.get_or_create(device=device)
            validate_obj.is_validated = device_software.validate_software()
            validate_obj.software = device_software.software
            validate_obj.last_run = job_run_time
            validate_obj.run_type = choices.ReportRunTypeChoices.REPORT_FULL_RUN
            validate_obj.validated_save()
        self.log_success(message=f"Performed validation on: {devices.count()} devices.")


class InventoryItemSoftwareValidationFullReport(Job):
    """Checks if inventory items run validated software version."""

    name = "Inventory Item Software Validation Report"
    description = "Validates software version on inventory items."
    read_only = False

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta class for the job."""

        commit_default = True

    def test_inventory_item_software_validity(self):
        """Check if software assigned to each inventory item is valid. If no software is assigned return warning message."""
        inventory_items = InventoryItem.objects.all()
        job_run_time = datetime.now()

        for inventoryitem in inventory_items:
            inventoryitem_software = InventoryItemSoftware(inventoryitem)

            validate_obj, _ = InventoryItemSoftwareValidationResult.objects.get_or_create(inventory_item=inventoryitem)
            validate_obj.is_validated = inventoryitem_software.validate_software()
            validate_obj.software = inventoryitem_software.software
            validate_obj.last_run = job_run_time
            validate_obj.run_type = choices.ReportRunTypeChoices.REPORT_FULL_RUN
            validate_obj.validated_save()

        self.log_success(message=f"Performed validation on: {inventory_items.count()} inventory items.")


class GenerateVulnerabilities(Job):
    """Generates VulnerabilityLCM objects based on CVEs that are related to Devices."""

    name = "Generate Vulnerabilities"
    description = "Generates any missing Vulnerability objects."
    read_only = False
    published_after = StringVar(
        regex=r"^[0-9]{4}\-[0-9]{2}\-[0-9]{2}$",
        label="CVEs Published After",
        description="Enter a date in ISO Format (YYYY-MM-DD) to only process CVEs published after that date.",
        default="1970-01-01",
        required=False,
    )

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta class for the job."""

        commit_default = True

    def run(self, data, commit):  # pylint: disable=too-many-locals
        """Check if software assigned to each device is valid. If no software is assigned return warning message."""
        # Although the default is set on the class attribute for the UI, it doesn't default for the API
        published_after = data.get("published_after", "1970-01-01")
        cves = CVELCM.objects.filter(published_date__gte=datetime.fromisoformat(published_after))
        count_before = VulnerabilityLCM.objects.count()

        for cve in cves:
            software_rels = RelationshipAssociation.objects.filter(relationship__slug="soft_cve", destination_id=cve.id)
            for soft_rel in software_rels:

                # Loop through any device relationships
                device_rels = soft_rel.source.get_relationships()["source"][
                    Relationship.objects.get(slug="device_soft")
                ]
                for dev_rel in device_rels:
                    vuln_obj, _ = VulnerabilityLCM.objects.get_or_create(
                        cve=cve, software=dev_rel.source, device=dev_rel.destination
                    )
                    vuln_obj.validated_save()

                # Loop through any inventory tem relationships
                item_rels = soft_rel.source.get_relationships()["source"][
                    Relationship.objects.get(slug="inventory_item_soft")
                ]
                for item_rel in item_rels:
                    vuln_obj, _ = VulnerabilityLCM.objects.get_or_create(
                        cve=cve, software=item_rel.source, inventory_item=item_rel.destination
                    )
                    vuln_obj.validated_save()

        diff = VulnerabilityLCM.objects.count() - count_before
        self.log_success(message=f"Processed {cves.count()} CVEs and generated {diff} Vulnerabilities.")


jobs = [DeviceSoftwareValidationFullReport, InventoryItemSoftwareValidationFullReport, GenerateVulnerabilities]

"""Generate test data for the Device Lifecycle Management app."""

import random

from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS
from nautobot.core.factory import get_random_instances
from nautobot.dcim.models import Device, DeviceType, InventoryItem, Platform

from nautobot_device_lifecycle_mgmt.choices import CVESeverityChoices
from nautobot_device_lifecycle_mgmt.models import (
    CVELCM,
    ContactLCM,
    ContractLCM,
    DeviceSoftwareValidationResult,
    HardwareLCM,
    InventoryItemSoftwareValidationResult,
    ProviderLCM,
    SoftwareImageLCM,
    SoftwareLCM,
    ValidatedSoftwareLCM,
    VulnerabilityLCM,
)


class Command(BaseCommand):
    """Populate the database with various data as a baseline for testing (automated or manual)."""

    help = __doc__

    def add_arguments(self, parser):  # noqa: D102
        parser.add_argument(
            "--database",
            default=DEFAULT_DB_ALIAS,
            help='The database to generate the test data in. Defaults to the "default" database.',
        )

    def _generate_static_data(self, db):
        devices = get_random_instances(Device.objects.using(db), minimum=2, maximum=4)
        device_types = get_random_instances(DeviceType.objects.using(db), minimum=2, maximum=4)
        inventory_items = get_random_instances(InventoryItem.objects.using(db), minimum=2, maximum=4)
        platforms = get_random_instances(Platform.objects.using(db), minimum=2, maximum=4)

        # create HardwareLCM
        for device_type in device_types:
            HardwareLCM.objects.using(db).create(device_type=device_type, end_of_sale="2022-03-14")
        for inventory_item in inventory_items:
            HardwareLCM.objects.using(db).create(inventory_item=inventory_item, end_of_support="2020-05-04")

        # create SoftwareLCM
        for platform in platforms:
            SoftwareLCM.objects.using(db).create(
                device_platform=platform,
                version=f"Test SoftwareLCM for {platform.name}",
            )

        # create SoftwareImageLCM
        for software in SoftwareLCM.objects.using(db).all():
            SoftwareImageLCM.objects.using(db).create(
                software=software,
                image_file_name=f"{software.device_platform.name}_vxyz.bin",
            )

        # create ValidatedSoftwareLCM
        for software in SoftwareLCM.objects.using(db).all():
            ValidatedSoftwareLCM.objects.using(db).create(
                software=software,
                start="2020-01-01",
                end="2020-12-31",
            )

        # create DeviceSoftwareValidationResult
        software_choices = list(SoftwareLCM.objects.using(db).all())
        for device in devices:
            DeviceSoftwareValidationResult.objects.using(db).create(
                device=device,
                software=random.choice(software_choices),  # noqa: S311
            )

        # create InventoryItemSoftwareValidationResult
        for inventory_item in inventory_items:
            InventoryItemSoftwareValidationResult.objects.using(db).create(
                inventory_item=inventory_item,
                software=random.choice(software_choices),  # noqa: S311
            )

        # create ProviderLCM
        for i in range(1, 9):
            ProviderLCM.objects.using(db).create(
                name=f"Test Provider {i}",
                description=f"Description for Provider {i}",
            )

        # create ContractLCM
        for provider in ProviderLCM.objects.using(db).all():
            ContractLCM.objects.using(db).create(
                provider=provider,
                name=f"Test Contract for {provider.name}",
            )

        # create ContactLCM
        for contract in ContractLCM.objects.using(db).all():
            ContactLCM.objects.using(db).create(
                contract=contract,
                name=f"Test Contact for {contract.name}",
            )

        # create CVELCM
        for i in range(1, 5):
            cve = CVELCM.objects.using(db).create(
                name=f"Test CVELCM {i}",
                published_date="2020-01-01",
                link="http://cve.example.org/{i}/details/",
                severity=random.choice(CVESeverityChoices.values()),  # noqa: S311
            )
            cve.affected_softwares.set(get_random_instances(SoftwareLCM, minimum=1))

        # create VulnerabilityLCM
        VulnerabilityLCM.objects.using(db).create(cve=CVELCM.objects.using(db).get(name="Test CVELCM 1"))
        VulnerabilityLCM.objects.using(db).create(software=SoftwareLCM.objects.using(db).first())
        VulnerabilityLCM.objects.using(db).create(device=Device.objects.using(db).first())
        VulnerabilityLCM.objects.using(db).create(inventory_item=InventoryItem.objects.using(db).first())

    def handle(self, *args, **options):
        """Entry point to the management command."""
        self._generate_static_data(db=options["database"])

        self.stdout.write(self.style.SUCCESS(f"Database {options['database']} populated with app data successfully!"))

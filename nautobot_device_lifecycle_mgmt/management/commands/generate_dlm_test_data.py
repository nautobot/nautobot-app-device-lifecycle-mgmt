"""Generate test data for the Device Lifecycle Management app."""

import random
from datetime import date

from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS
from nautobot.apps.change_logging import web_request_context
from nautobot.core.factory import get_random_instances
from nautobot.dcim.models import Device, DeviceType, InventoryItem, SoftwareVersion
from nautobot.users.models import User

from nautobot_device_lifecycle_mgmt.choices import CVESeverityChoices
from nautobot_device_lifecycle_mgmt.models import (
    CVELCM,
    ContactLCM,
    ContractLCM,
    DeviceSoftwareValidationResult,
    HardwareLCM,
    InventoryItemSoftwareValidationResult,
    ProviderLCM,
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
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Flush any existing device lifecycle management models data from the database before generating new data.",
        )

    def _generate_static_data(self, db):
        devices = get_random_instances(Device.objects.using(db), minimum=2, maximum=4)
        device_types = get_random_instances(DeviceType.objects.using(db), minimum=2, maximum=4)
        inventory_items = get_random_instances(InventoryItem.objects.using(db), minimum=2, maximum=4)
        software_versions = get_random_instances(SoftwareVersion.objects.using(db), minimum=2, maximum=4)

        # create HardwareLCM
        for device_type in device_types:
            HardwareLCM.objects.using(db).create(device_type=device_type, end_of_sale=date(2022, 3, 14))
        for inventory_item in inventory_items:
            HardwareLCM.objects.using(db).create(inventory_item=inventory_item, end_of_support=date(2020, 5, 4))

        # create ValidatedSoftwareLCM
        for software in software_versions:
            ValidatedSoftwareLCM.objects.using(db).create(
                software=software,
                start=date(2020, 1, 1),
                end=date(2020, 12, 31),
            )

        # create DeviceSoftwareValidationResult
        for device in devices:
            DeviceSoftwareValidationResult.objects.using(db).create(
                device=device,
                software=random.choice(software_versions),  # noqa: S311
            )

        # create InventoryItemSoftwareValidationResult
        for inventory_item in inventory_items:
            InventoryItemSoftwareValidationResult.objects.using(db).create(
                inventory_item=inventory_item,
                software=random.choice(software_versions),  # noqa: S311
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
                published_date=date(2020, 1, 1),
                link="http://cve.example.org/{i}/details/",
                severity=random.choice(CVESeverityChoices.values()),  # noqa: S311
            )
            cve.affected_softwares.set(get_random_instances(SoftwareVersion.objects.using(db), minimum=1))

        # create VulnerabilityLCM
        VulnerabilityLCM.objects.using(db).create(cve=CVELCM.objects.using(db).get(name="Test CVELCM 1"))
        VulnerabilityLCM.objects.using(db).create(software=SoftwareVersion.objects.using(db).first())
        VulnerabilityLCM.objects.using(db).create(device=Device.objects.using(db).first())
        VulnerabilityLCM.objects.using(db).create(inventory_item=InventoryItem.objects.using(db).first())

    def handle(self, *args, **options):
        """Entry point to the management command."""
        if options["flush"]:
            self.stdout.write(
                self.style.WARNING("Flushing device lifecycle management models objects from the database...")
            )
            VulnerabilityLCM.objects.using(options["database"]).all().delete()
            CVELCM.objects.using(options["database"]).all().delete()
            ContactLCM.objects.using(options["database"]).all().delete()
            ContractLCM.objects.using(options["database"]).all().delete()
            ProviderLCM.objects.using(options["database"]).all().delete()
            InventoryItemSoftwareValidationResult.objects.using(options["database"]).all().delete()
            DeviceSoftwareValidationResult.objects.using(options["database"]).all().delete()
            ValidatedSoftwareLCM.objects.using(options["database"]).all().delete()
            HardwareLCM.objects.using(options["database"]).all().delete()

        with web_request_context(user=User.objects.first(), context_detail="generate_dlm_test_data"):
            self._generate_static_data(db=options["database"])

        self.stdout.write(self.style.SUCCESS(f"Database {options['database']} populated with app data successfully!"))

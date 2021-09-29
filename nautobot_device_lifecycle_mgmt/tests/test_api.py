"""Unit tests for nautobot_device_lifecycle_mgmt."""
import datetime
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from nautobot.utilities.testing import APIViewTestCases
from nautobot.dcim.models import DeviceType, Manufacturer, Platform, Device, DeviceRole, InventoryItem, Site
from nautobot.extras.models import Status

from nautobot_device_lifecycle_mgmt.models import (
    HardwareLCM,
    SoftwareLCM,
    ContractLCM,
    ProviderLCM,
    ValidatedSoftwareLCM,
)


User = get_user_model()


class HardwareLCMAPITest(APIViewTestCases.APIViewTestCase):  # pylint: disable=too-many-ancestors
    """Test the HardwareLCM API."""

    model = HardwareLCM
    bulk_update_data = {"documentation_url": "https://cisco.com/eox"}
    brief_fields = [
        "custom_fields",
        "device_type",
        "display",
        "documentation_url",
        "end_of_sale",
        "end_of_security_patches",
        "end_of_support",
        "end_of_sw_releases",
        "expired",
        "id",
        "inventory_item",
        "release_date",
        "tags",
    ]

    @classmethod
    def setUpTestData(cls):
        """Create a superuser and token for API calls."""
        manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        device_types = (
            DeviceType.objects.create(model="c9300-24", slug="c9300-24", manufacturer=manufacturer),
            DeviceType.objects.create(model="c9300-48", slug="c9300-48", manufacturer=manufacturer),
            DeviceType.objects.create(model="c9500-24", slug="c9500-24", manufacturer=manufacturer),
            DeviceType.objects.create(model="c9500-48", slug="c9500-48", manufacturer=manufacturer),
            DeviceType.objects.create(model="c9407", slug="c9407", manufacturer=manufacturer),
            DeviceType.objects.create(model="c9410", slug="c9410", manufacturer=manufacturer),
        )

        HardwareLCM.objects.create(device_type=device_types[3], end_of_sale=datetime.date(2021, 4, 1))
        HardwareLCM.objects.create(device_type=device_types[4], end_of_sale=datetime.date(2021, 4, 1))
        HardwareLCM.objects.create(device_type=device_types[5], end_of_sale=datetime.date(2021, 4, 1))

        cls.create_data = [
            # Setting end_of_sale as datetime.date for proper comparison
            {"device_type": device_types[0].id, "end_of_sale": datetime.date(2021, 4, 1)},
            {"device_type": device_types[1].id, "end_of_sale": datetime.date(2021, 4, 1)},
            {"device_type": device_types[2].id, "end_of_sale": datetime.date(2021, 4, 1)},
        ]

    def test_bulk_create_objects(self):
        """Currently don't support bulk operations."""

    def test_bulk_delete_objects(self):
        """Currently don't support bulk operations."""

    def test_bulk_update_objects(self):
        """Currently don't support bulk operations."""


class SoftwareLCMAPITest(APIViewTestCases.APIViewTestCase):  # pylint: disable=too-many-ancestors
    """Test the SoftwareLCM API."""

    model = SoftwareLCM
    brief_fields = [
        "device_platform",
        "display",
        "end_of_support",
        "id",
        "url",
        "version",
    ]

    @classmethod
    def setUpTestData(cls):

        device_platforms = (
            Platform.objects.create(name="Cisco IOS", slug="cisco_ios"),
            Platform.objects.create(name="Arista EOS", slug="arista_eos"),
            Platform.objects.create(name="Juniper Junos", slug="juniper_junos"),
        )

        cls.create_data = [
            {
                "device_platform": device_platforms[0].id,
                "version": "15.4(3)M",
                "end_of_support": datetime.date(2022, 2, 28),
            },
            {
                "device_platform": device_platforms[1].id,
                "version": "4.21.3F",
                "end_of_support": datetime.date(2021, 8, 9),
            },
            {
                "device_platform": device_platforms[2].id,
                "version": "20.3R3",
                "end_of_support": datetime.date(2023, 9, 29),
            },
        ]

        SoftwareLCM.objects.create(
            device_platform=device_platforms[0], version="15.1(2)M", end_of_support=datetime.date(2023, 5, 8)
        )
        SoftwareLCM.objects.create(
            device_platform=device_platforms[1], version="4.22.9M", end_of_support=datetime.date(2022, 4, 11)
        )
        SoftwareLCM.objects.create(
            device_platform=device_platforms[2], version="21.4R3", end_of_support=datetime.date(2024, 5, 19)
        )

    def test_bulk_create_objects(self):
        """Currently don't support bulk operations."""

    def test_bulk_delete_objects(self):
        """Currently don't support bulk operations."""

    def test_bulk_update_objects(self):
        """Currently don't support bulk operations."""


class ContractLCMAPITest(APIViewTestCases.APIViewTestCase):  # pylint: disable=too-many-ancestors
    """Test the ContractLCM API."""

    model = ContractLCM
    bulk_update_data = {"documentation_url": "https://cisco.com/eox"}
    brief_fields = [
        "contract_type",
        "cost",
        "display",
        "end",
        "expired",
        "id",
        "name",
        "provider",
        "start",
        "support_level",
    ]

    @classmethod
    def setUpTestData(cls):
        """Create a superuser and token for API calls."""
        provider = ProviderLCM.objects.create(
            name="Cisco",
            description="Cisco Support",
            physical_address="123 Cisco Way, San Jose, CA",
            phone="(123) 456-7890",
            email="email@cisco.com",
            portal_url="https://www.cisco.com/",
            comments="Test Comment",
        )
        cls.create_data = [
            {
                "name": "Nexus Support - Hardware",
                "start": datetime.date(2021, 4, 1),
                "end": datetime.date(2022, 4, 1),
                "support_level": "24/7",
                "contract_type": "Hardware",
                "provider": provider.id,
            },
            {
                "name": "Nexus Support - Software",
                "start": datetime.date(2021, 4, 1),
                "end": datetime.date(2022, 4, 1),
                "support_level": "8-5, M-F",
                "contract_type": "Software",
                "provider": provider.id,
            },
            {
                "name": "ASA Support - Hardware",
                "start": datetime.date(2021, 4, 1),
                "end": datetime.date(2022, 4, 1),
                "support_level": "24/7",
                "contract_type": "Hardware",
                "provider": provider.id,
            },
        ]

        ContractLCM.objects.create(
            name="Meraki Hardware Support",
            number="MERK00001",
            start=datetime.date(2021, 4, 1),
            end=datetime.date(2022, 4, 1),
            provider=provider,
        )
        ContractLCM.objects.create(
            name="Meraki Software Support",
            number="MERK00002",
            start=datetime.date(2021, 4, 1),
            end=datetime.date(2022, 4, 1),
            provider=provider,
        )
        ContractLCM.objects.create(
            name="Juniper Hardware Support",
            number="CSCO0000001",
            start=datetime.date(2021, 4, 1),
            end=datetime.date(2022, 4, 1),
            provider=provider,
        )

    def test_bulk_create_objects(self):
        """Currently don't support bulk operations."""

    def test_bulk_delete_objects(self):
        """Currently don't support bulk operations."""

    def test_bulk_update_objects(self):
        """Currently don't support bulk operations."""


class ValidatedSoftwareLCMAPITest(APIViewTestCases.APIViewTestCase):  # pylint: disable=too-many-ancestors
    """Test the SoftwareLCM API."""

    model = ValidatedSoftwareLCM
    brief_fields = [
        "assigned_to",
        "assigned_to_content_type",
        "assigned_to_object_id",
        "custom_fields",
        "display",
        "end",
        "id",
        "preferred",
        "software",
        "start",
        "tags",
        "url",
        "valid",
    ]

    @classmethod
    def setUpTestData(cls):
        """Create a superuser and token for API calls."""
        device_platform = Platform.objects.create(name="Cisco IOS", slug="cisco_ios")
        softwares = (
            SoftwareLCM.objects.create(
                **{
                    "device_platform": device_platform,
                    "version": "17.3.3 MD",
                    "alias": "Amsterdam-17.3.3 MD",
                    "end_of_support": "2022-05-15",
                    "documentation_url": "https://www.cisco.com/c/en/us/support/ios-nx-os-software/ios-15-4m-t/series.html",
                    "download_url": "ftp://device-images.local.com/cisco/asr1001x-universalk9.17.03.03.SPA.bin",
                    "image_file_name": "asr1001x-universalk9.17.03.03.SPA.bin",
                    "image_file_checksum": "9cf2e09b59207a4d8ea40886fbbe5b4b68e19e58a8f96b34240e4cea9971f6ae6facab9a1855a34e1ed8755f3ffe4c969cf6e6ef1df95d42a91540a44d4b9e14",
                    "long_term_support": True,
                    "pre_release": False,
                }
            ),
            SoftwareLCM.objects.create(
                **{
                    "device_platform": device_platform,
                    "version": "15.5(1)SY",
                    "alias": "Catalyst-15.5(1)SY",
                    "end_of_support": "2019-02-5",
                    "documentation_url": "https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst6500/ios/15-1SY/config_guide/sup2T/15_1_sy_swcg_2T/cef.html",
                    "download_url": "ftp://device-images.local.com/cisco/s2t54-ipservicesk9_npe-mz.SPA.155-1.SY1.bin",
                    "image_file_name": "s2t54-ipservicesk9_npe-mz.SPA.155-1.SY1.bin",
                    "image_file_checksum": "74e61320f5518a2954b2d307b7e6a038",
                    "long_term_support": False,
                    "pre_release": True,
                }
            ),
        )

        status_active = Status.objects.get(slug="active")
        manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        site = Site.objects.create(name="Site 1", slug="site-1")
        deviceroles = (
            DeviceRole.objects.create(name="Router", slug="router", color="ff0000"),
            DeviceRole.objects.create(name="Switch", slug="switch", color="ffff00"),
        )
        devicetypes = (
            DeviceType.objects.create(manufacturer=manufacturer, model="ASR-1000", slug="asr-1000"),
            DeviceType.objects.create(manufacturer=manufacturer, model="Catalyst 6500", slug="catalyst-6500"),
        )
        devices = (
            Device.objects.create(
                device_type=devicetypes[0], device_role=deviceroles[0], name="Device 1", site=site, status=status_active
            ),
            Device.objects.create(
                device_type=devicetypes[1], device_role=deviceroles[1], name="Device 2", site=site, status=status_active
            ),
        )
        inventoryitems = (
            InventoryItem.objects.create(device=devices[0], name="SwitchModule1"),
            InventoryItem.objects.create(device=devices[1], name="Supervisor Engine 720"),
        )

        content_type_device = ContentType.objects.get(app_label="dcim", model="device")
        content_type_devicetype = ContentType.objects.get(app_label="dcim", model="devicetype")
        content_type_inventoryitem = ContentType.objects.get(app_label="dcim", model="inventoryitem")

        cls.create_data = [
            {
                "software": softwares[0].id,
                "assigned_to_content_type": "dcim.device",
                "assigned_to_object_id": devices[0].id,
                "start": datetime.date(2020, 1, 14),
                "end": datetime.date(2024, 10, 18),
                "preferred": False,
            },
            {
                "software": softwares[0].id,
                "assigned_to_content_type": "dcim.devicetype",
                "assigned_to_object_id": devicetypes[0].id,
                "start": datetime.date(2021, 6, 4),
                "end": datetime.date(2025, 1, 8),
                "preferred": True,
            },
            {
                "software": softwares[0].id,
                "assigned_to_content_type": "dcim.inventoryitem",
                "assigned_to_object_id": inventoryitems[0].id,
                "start": datetime.date(2019, 3, 6),
                "end": datetime.date(2023, 6, 1),
                "preferred": False,
            },
        ]

        ValidatedSoftwareLCM.objects.create(
            software=softwares[1],
            assigned_to_content_type=content_type_device,
            assigned_to_object_id=devices[1].id,
            start=datetime.date(2021, 6, 4),
            end=datetime.date(2025, 1, 8),
            preferred=True,
        )
        ValidatedSoftwareLCM.objects.create(
            software=softwares[1],
            assigned_to_content_type=content_type_devicetype,
            assigned_to_object_id=devicetypes[1].id,
            start=datetime.date(2018, 2, 23),
            end=datetime.date(2019, 6, 12),
            preferred=False,
        )
        ValidatedSoftwareLCM.objects.create(
            software=softwares[1],
            assigned_to_content_type=content_type_inventoryitem,
            assigned_to_object_id=inventoryitems[1].id,
            start=datetime.date(2019, 11, 19),
            end=datetime.date(2030, 7, 30),
            preferred=False,
        )

    def test_bulk_create_objects(self):
        """Currently don't support bulk operations."""

    def test_bulk_delete_objects(self):
        """Currently don't support bulk operations."""

    def test_bulk_update_objects(self):
        """Currently don't support bulk operations."""

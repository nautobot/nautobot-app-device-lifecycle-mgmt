"""Unit tests for nautobot_device_lifecycle_mgmt."""
import datetime
from django.contrib.auth import get_user_model

from nautobot.utilities.testing import APIViewTestCases
from nautobot.dcim.models import DeviceType, Manufacturer, Platform

from nautobot_device_lifecycle_mgmt.models import HardwareLCM, SoftwareLCM

User = get_user_model()


class HardwareLCMAPITest(APIViewTestCases.APIViewTestCase):  # pylint: disable=too-many-ancestors
    """Test the HardwareLCM API."""

    model = HardwareLCM
    bulk_update_data = {"documentation_url": "https://cisco.com/eox"}
    brief_fields = [
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

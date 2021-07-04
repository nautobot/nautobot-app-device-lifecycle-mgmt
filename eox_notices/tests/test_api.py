"""Unit tests for eox_notices."""
import datetime
from django.contrib.auth import get_user_model

from nautobot.utilities.testing import APIViewTestCases
from nautobot.dcim.models import DeviceType, Manufacturer

from eox_notices.models import EoxNotice

User = get_user_model()


class EoxNoticeAPITest(APIViewTestCases.APIViewTestCase):
    """Test the EoxNotices API."""

    model = EoxNotice
    bulk_update_data = {"notice_url": "https://cisco.com/eox"}
    brief_fields = [
        "device_type",
        "devices",
        "display",
        "end_of_sale",
        "end_of_security_patches",
        "end_of_support",
        "end_of_sw_releases",
        "expired",
        "id",
        "notice_url",
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

        EoxNotice.objects.create(device_type=device_types[3], end_of_sale=datetime.date(2021, 4, 1))
        EoxNotice.objects.create(device_type=device_types[4], end_of_sale=datetime.date(2021, 4, 1))
        EoxNotice.objects.create(device_type=device_types[5], end_of_sale=datetime.date(2021, 4, 1))

        cls.create_data = [
            # Setting end_of_sale as datetime.date for proper comparison
            {"device_type": device_types[0].id, "end_of_sale": datetime.date(2021, 4, 1)},
            {"device_type": device_types[1].id, "end_of_sale": datetime.date(2021, 4, 1)},
            {"device_type": device_types[2].id, "end_of_sale": datetime.date(2021, 4, 1)},
        ]

    def test_bulk_create_objects(self):
        """Currently don't support bulk operations."""
        pass

    def test_bulk_delete_objects(self):
        """Currently don't support bulk operations."""
        pass

    def test_bulk_update_objects(self):
        """Currently don't support bulk operations."""
        pass

"""Unit tests for eox_notices."""
from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

# Import rest_framework related helpers
from rest_framework import status
from rest_framework.test import APIClient

# from nautobot.utilities.testing import APIViewTestCases
from nautobot.dcim.models import DeviceType, Manufacturer
from nautobot.users.models import Token

from eox_notices.models import EoxNotice

User = get_user_model()


class EoxNoticeAPITest(TestCase):
    """Test the EoxNotices API."""

    def setUp(self):
        """Create a superuser and token for API calls."""
        # Setup user and APIClient
        self.user = User.objects.create(username="testuser", is_superuser=True)
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        self.base_url_lookup = "plugins-api:eox_notices-api:eoxnotice"

        # Create test objects
        self.manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        self.device_types = (
            DeviceType.objects.create(model="c9300-24", slug="c9300-24", manufacturer=self.manufacturer),
            DeviceType.objects.create(model="c9300-48", slug="c9300-48", manufacturer=self.manufacturer),
            DeviceType.objects.create(model="c9500-24", slug="c9500-24", manufacturer=self.manufacturer),
        )

        self.notices = (
            EoxNotice.objects.create(device_type=self.device_types[0], end_of_sale="2021-04-01"),
            EoxNotice.objects.create(device_type=self.device_types[1], end_of_sale="2021-04-01"),
            EoxNotice.objects.create(device_type=self.device_types[2], end_of_sale="2021-04-01"),
        )

    def test_list_eox_notices_ok(self):
        """Verify notices are listed."""
        url = reverse(f"{self.base_url_lookup}-list")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)

    def test_detail_eox_notice_ok(self):
        """Verify notices are listed."""
        url = reverse(f"{self.base_url_lookup}-detail", kwargs={"pk": self.notices[0].pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["end_of_sale"], "2021-04-01")

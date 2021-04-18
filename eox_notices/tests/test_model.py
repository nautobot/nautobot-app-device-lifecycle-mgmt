from django.test import TestCase
from django.core.exceptions import ValidationError

from nautobot.dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site

from eox_notices.models import EoxNotice


class TestModelBasic(TestCase):
    def setUp(self):
        """Set up base objects."""
        self.manufacturer = Manufacturer.objects.create(name="Cisco")
        self.device_type = DeviceType.objects.create(model="c9300-24", slug="c9300-24", manufacturer=self.manufacturer)

    def test_create_eox_notice_success_eo_sale(self):
        """Successfully create basic notice with end_of_sale."""
        eox_obj = EoxNotice.objects.create(device_type=self.device_type, end_of_sale="2023-04-01")

        self.assertEqual(eox_obj.device_type, self.device_type)
        self.assertEqual(str(eox_obj.end_of_sale), "2023-04-01")
        self.assertEqual(str(eox_obj), "c9300-24 - End of sale: 2023-04-01")

    def test_create_eox_notice_success_eo_support(self):
        """Successfully create basic notice with end_of_support."""
        eox_obj = EoxNotice.objects.create(device_type=self.device_type, end_of_support="2022-04-01")

        self.assertEqual(eox_obj.device_type, self.device_type)
        self.assertEqual(str(eox_obj.end_of_support), "2022-04-01")
        self.assertEqual(str(eox_obj), "c9300-24 - End of support: 2022-04-01")

    def test_create_eox_notice_success_eo_all(self):
        """Successfully create basic notice."""
        eox_obj = EoxNotice.objects.create(
            device_type=self.device_type,
            end_of_sale="2022-04-01",
            end_of_support="2023-04-01",
            end_of_sw_releases="2024-04-01",
            end_of_security_patches="2025-04-01",
            notice_url="https://test.com",
        )

        self.assertEqual(eox_obj.device_type, self.device_type)
        self.assertEqual(str(eox_obj.end_of_sale), "2022-04-01")
        self.assertEqual(str(eox_obj.end_of_support), "2023-04-01")
        self.assertEqual(str(eox_obj.end_of_sw_releases), "2024-04-01")
        self.assertEqual(str(eox_obj.end_of_security_patches), "2025-04-01")
        self.assertEqual(eox_obj.notice_url, "https://test.com")
        self.assertEqual(str(eox_obj), "c9300-24 - End of support: 2023-04-01")

    def test_create_eox_notice_failed_missing_one_of(self):
        """Successfully create basic notice."""
        with self.assertRaises(ValidationError) as failure_exception:
            EoxNotice.objects.create(device_type=self.device_type)
        self.assertEquals(failure_exception.exception.messages[0], "End of Sale or End of Support must be specified.")

    def test_create_eox_notice_failed_validation_notice_url(self):
        """Successfully create basic notice."""
        with self.assertRaises(ValidationError) as failure_exception:
            EoxNotice.objects.create(device_type=self.device_type, end_of_support="2023-04-01", notice_url="test.com")
        self.assertEquals(failure_exception.exception.messages[0], "Enter a valid URL.")

    def test_create_eox_notice_failed_validation_date(self):
        """Successfully create basic notice."""
        with self.assertRaises(ValidationError) as failure_exception:
            EoxNotice.objects.create(device_type=self.device_type, end_of_support="April 1st 2022")
        self.assertIn("invalid date format. It must be in YYYY-MM-DD format.", failure_exception.exception.messages[0])

    def test_create_eox_notice_check_devices(self):
        """Successfully create notice and assert correct amount of devices attached."""
        # Create Device dependencies
        self.site = Site.objects.create(name="Test Site")
        self.device_role = DeviceRole.objects.create(name="Core Switch")

        # Create 4 devices to assert they get attached to EoxNotice
        for i in range(0, 4):
            Device.objects.create(
                name=f"r{i}", site=self.site, device_role=self.device_role, device_type=self.device_type
            )

        # Create Notice now
        eox_obj = EoxNotice.objects.create(device_type=self.device_type, end_of_support="2022-04-01")
        self.assertEqual(eox_obj.device_type, self.device_type)
        self.assertEqual(str(eox_obj.end_of_support), "2022-04-01")
        self.assertEqual(str(eox_obj), "c9300-24 - End of support: 2022-04-01")
        self.assertEqual(eox_obj.devices.count(), 4)

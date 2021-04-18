"""Test forms."""
from django.test import TestCase

from nautobot.dcim.models import DeviceType, Manufacturer

from eox_notices.forms import EoxNoticeForm


class EoxFormTest(TestCase):
    def setUp(self):
        """Create necessary objects."""
        self.manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        self.device_type = DeviceType.objects.create(model="c9300-24", slug="c9300-24", manufacturer=self.manufacturer)

    def test_specifying_all_fields(self):
        form = EoxNoticeForm(
            data={
                "device_type": self.device_type,
                "end_of_sale": "2021-04-01",
                "end_of_support": "2022-04-01",
                "end_of_sw_releases": "2023-04-01",
                "end_of_security_patches": "2024-04-01",
                "notice_url": "https://cisco.com",
            }
        )
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_one_of_eo_sale(self):
        form = EoxNoticeForm(data={"device_type": self.device_type, "end_of_sale": "2021-04-01"})
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_one_of_eo_support(self):
        form = EoxNoticeForm(data={"device_type": self.device_type, "end_of_support": "2021-04-01"})
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_required_field_device_type_missing(self):
        form = EoxNoticeForm(
            data={
                "end_of_sale": "2021-04-01",
                "end_of_support": "2022-04-01",
                "end_of_sw_releases": "2023-04-01",
                "end_of_security_patches": "2024-04-01",
                "notice_url": "https://cisco.com",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("device_type", form.errors)
        self.assertIn("This field is required", form.errors["device_type"][0])

    def test_eo_sale_support_fields_missing(self):
        form = EoxNoticeForm(data={"device_type": self.device_type})
        self.assertFalse(form.is_valid())
        self.assertIn("End of Sale or End of Support must be specified.", form.errors["__all__"][0])

    def test_validation_error_end_of_sale(self):
        form = EoxNoticeForm(data={"device_type": self.device_type, "end_of_sale": "April 1st, 2021"})
        self.assertFalse(form.is_valid())
        self.assertIn("end_of_sale", form.errors)
        self.assertIn("Enter a valid date.", form.errors["end_of_sale"])

    def test_validation_error_end_of_support(self):
        form = EoxNoticeForm(
            data={"device_type": self.device_type, "end_of_sale": "2021-04-01", "end_of_support": "April 1st, 2022"}
        )
        self.assertFalse(form.is_valid())
        self.assertIn("end_of_support", form.errors)
        self.assertIn("Enter a valid date.", form.errors["end_of_support"])

    def test_validation_error_end_of_sw_releases(self):
        form = EoxNoticeForm(
            data={
                "device_type": self.device_type,
                "end_of_sale": "2021-04-01",
                "end_of_support": "2021-04-01",
                "end_of_sw_releases": "April 1st, 2022",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("end_of_sw_releases", form.errors)
        self.assertIn("Enter a valid date.", form.errors["end_of_sw_releases"])

    def test_validation_error_end_of_security_patches(self):
        form = EoxNoticeForm(
            data={
                "device_type": self.device_type,
                "end_of_sale": "2021-04-01",
                "end_of_support": "2022-04-01",
                "end_of_sw_releases": "2023-04-01",
                "end_of_security_patches": "April 1st, 2022",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("end_of_security_patches", form.errors)
        self.assertIn("Enter a valid date.", form.errors["end_of_security_patches"])

    def test_validation_error_notice_url(self):
        form = EoxNoticeForm(
            data={
                "device_type": self.device_type,
                "end_of_sale": "2021-04-01",
                "end_of_support": "2022-04-01",
                "end_of_sw_releases": "2023-04-01",
                "end_of_security_patches": "2024-04-01",
                "notice_url": "htttps://cisco.com",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("notice_url", form.errors)
        self.assertIn("Enter a valid URL.", form.errors["notice_url"])

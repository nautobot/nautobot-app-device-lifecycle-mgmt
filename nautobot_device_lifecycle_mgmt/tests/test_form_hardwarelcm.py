"""Test hardwarelcm forms."""

from django.test import TestCase

from nautobot_device_lifecycle_mgmt import forms


class HardwareLCMTest(TestCase):
    """Test HardwareLCM forms."""

    def test_specifying_all_fields_success(self):
        form = forms.HardwareLCMForm(
            data={
                "name": "Development",
                "description": "Development Testing",
            }
        )
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_specifying_only_required_success(self):
        form = forms.HardwareLCMForm(
            data={
                "name": "Development",
            }
        )
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_validate_name_hardwarelcm_is_required(self):
        form = forms.HardwareLCMForm(data={"description": "Development Testing"})
        self.assertFalse(form.is_valid())
        self.assertIn("This field is required.", form.errors["name"])

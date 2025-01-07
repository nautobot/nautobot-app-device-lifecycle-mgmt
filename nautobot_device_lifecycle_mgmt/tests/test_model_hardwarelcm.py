"""Test HardwareLCM."""

from django.test import TestCase

from nautobot_device_lifecycle_mgmt import models


class TestHardwareLCM(TestCase):
    """Test HardwareLCM."""

    def test_create_hardwarelcm_only_required(self):
        """Create with only required fields, and validate null description and __str__."""
        hardwarelcm = models.HardwareLCM.objects.create(name="Development")
        self.assertEqual(hardwarelcm.name, "Development")
        self.assertEqual(hardwarelcm.description, "")
        self.assertEqual(str(hardwarelcm), "Development")

    def test_create_hardwarelcm_all_fields_success(self):
        """Create HardwareLCM with all fields."""
        hardwarelcm = models.HardwareLCM.objects.create(name="Development", description="Development Test")
        self.assertEqual(hardwarelcm.name, "Development")
        self.assertEqual(hardwarelcm.description, "Development Test")

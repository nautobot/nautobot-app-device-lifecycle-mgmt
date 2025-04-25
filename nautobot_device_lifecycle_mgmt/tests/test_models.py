"""Test HardwareLCM."""

from nautobot.apps.testing import ModelTestCases

from nautobot_device_lifecycle_mgmt import models
from nautobot_device_lifecycle_mgmt.tests import fixtures


class TestHardwareLCM(ModelTestCases.BaseModelTestCase):
    """Test HardwareLCM."""

    model = models.HardwareLCM

    @classmethod
    def setUpTestData(cls):
        """Create test data for HardwareLCM Model."""
        super().setUpTestData()
        # Create 3 objects for the model test cases.
        fixtures.create_hardwarelcm()

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

"""Test management commands."""

from io import StringIO

from django.core.management import call_command
from nautobot.apps.testing import TestCase

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
from nautobot_device_lifecycle_mgmt.tests.conftest import create_inventory_items, create_softwares


class GenerateDLMTestDataTest(TestCase):
    """Test the `generate_dlm_test_data` management command."""

    def test_generated_objects_pass_validation(self):
        """Every model gets test data, and every generated object passes model validation."""
        create_inventory_items()
        create_softwares()

        call_command("generate_dlm_test_data", stdout=StringIO())

        for model in (
            HardwareLCM,
            ValidatedSoftwareLCM,
            DeviceSoftwareValidationResult,
            InventoryItemSoftwareValidationResult,
            ProviderLCM,
            ContractLCM,
            ContactLCM,
            CVELCM,
            VulnerabilityLCM,
        ):
            with self.subTest(model=model.__name__):
                self.assertTrue(model.objects.exists())
                for obj in model.objects.all():
                    obj.full_clean()

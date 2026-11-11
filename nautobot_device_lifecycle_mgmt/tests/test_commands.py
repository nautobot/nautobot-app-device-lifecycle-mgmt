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

COMMAND = "generate_nautobot_device_lifecycle_mgmt_test_data"
GENERATED_MODELS = (
    HardwareLCM,
    ValidatedSoftwareLCM,
    DeviceSoftwareValidationResult,
    InventoryItemSoftwareValidationResult,
    ProviderLCM,
    ContractLCM,
    ContactLCM,
    CVELCM,
    VulnerabilityLCM,
)
FIXED_COUNT_MODELS = (ProviderLCM, ContractLCM, ContactLCM, CVELCM, VulnerabilityLCM)


class GenerateDLMTestDataTest(TestCase):
    """Test the `generate_nautobot_device_lifecycle_mgmt_test_data` management command."""

    @classmethod
    def setUpTestData(cls):
        create_inventory_items()
        create_softwares()

    def assert_generated_objects_are_valid(self):
        """Assert that every model has test data and every object passes model validation."""
        for model in GENERATED_MODELS:
            with self.subTest(model=model.__name__):
                self.assertTrue(model.objects.exists())
                for obj in model.objects.all():
                    obj.full_clean()

    def test_generated_objects_pass_validation(self):
        """Every model gets test data, and every generated object passes model validation."""
        call_command(COMMAND, stdout=StringIO())

        self.assert_generated_objects_are_valid()

    def test_running_again_with_flush_replaces_the_data(self):
        """A second run with `--flush` replaces the first run's objects with the same amount of valid data."""
        call_command(COMMAND, stdout=StringIO())
        first_run_pks = {model: set(model.objects.values_list("pk", flat=True)) for model in GENERATED_MODELS}

        call_command(COMMAND, "--flush", stdout=StringIO())

        self.assert_generated_objects_are_valid()
        for model, pks in first_run_pks.items():
            with self.subTest(model=model.__name__):
                self.assertFalse(model.objects.filter(pk__in=pks).exists())
        for model in FIXED_COUNT_MODELS:
            with self.subTest(model=model.__name__):
                self.assertEqual(model.objects.count(), len(first_run_pks[model]))

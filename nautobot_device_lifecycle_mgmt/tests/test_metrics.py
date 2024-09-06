"""nautobot_device_lifecycle_mgmt test class for metrics."""

from django.db import ProgrammingError
from nautobot.core.testing import TestCase

from nautobot_device_lifecycle_mgmt.metrics import (
    metrics_lcm_hw_end_of_support_location,
    metrics_lcm_hw_end_of_support_part_number,
    metrics_lcm_validation_report_device_type,
    metrics_lcm_validation_report_inventory_item,
)

from .conftest import create_devices, create_inventory_item_hardware_notices, create_inventory_items


class MetricsTest(TestCase):
    """Test class for Device Lifecycle metrics."""

    def setUp(self):
        create_inventory_items()
        create_inventory_item_hardware_notices()

    def test_metrics_lcm_validation_report_device_type(self):
        """Test metric device_software_compliance_gauge."""
        create_devices()
        # TODO: Generate DeviceSoftwareValidationResult
        metric_gen = metrics_lcm_validation_report_device_type()
        metric = next(metric_gen)

        expected_ts_samples = {
            (("device_type", "6509-E"), ("is_valid", "False")): 0,
            (("device_type", "6509-E"), ("is_valid", "True")): 0,
        }

        for sample in metric.samples:
            sample_labels = tuple(sample.labels.items())
            self.assertEqual(expected_ts_samples[sample_labels], sample.value)

    def test_metrics_lcm_validation_report_inventory_item(self):
        """Test metric inventory_item_software_compliance_gauge."""
        # TODO: Generate InventoryItemSoftwareValidationResult
        metric_gen = metrics_lcm_validation_report_inventory_item()
        metric = next(metric_gen)

        expected_ts_samples = {
            (("inventory_item", "VS-S2T-10G"), ("is_valid", "False")): 0,
            (("inventory_item", "QSFP-100G-SR4-S"), ("is_valid", "False")): 0,
            (("inventory_item", "WS-X6548-GE-TX"), ("is_valid", "False")): 0,
            (("inventory_item", "VS-S2T-10G"), ("is_valid", "True")): 0,
            (("inventory_item", "QSFP-100G-SR4-S"), ("is_valid", "True")): 0,
            (("inventory_item", "WS-X6548-GE-TX"), ("is_valid", "True")): 0,
        }

        for sample in metric.samples:
            sample_labels = tuple(sample.labels.items())
            self.assertEqual(expected_ts_samples[sample_labels], sample.value)

    def test_metrics_lcm_hw_end_of_support_location_does_not_error(self):
        """Query providing data to hw_end_of_support_location_gauge metric should not error out.
        Guards against https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/309
        """
        metric_gen = metrics_lcm_hw_end_of_support_location()
        try:
            # Get hw_end_of_support_location_gauge
            next(metric_gen)
        except ProgrammingError:
            self.fail("metrics_lcm_hw_end_of_support_location query bug")

    def test_metrics_lcm_hw_end_of_support_part_number(self):
        """Test metric hw_end_of_support_part_number_gauge."""
        metric_gen = metrics_lcm_hw_end_of_support_part_number()

        # Get hw_end_of_support_part_number_gauge
        metric = next(metric_gen)

        expected_ts_samples = {
            ("part_number", "6509-E"): 0,
            ("part_number", "VS-S2T-10G"): 1,
            ("part_number", "QSFP-100G-SR4-S"): 1,
            ("part_number", "WS-X6548-GE-TX"): 0,
        }

        for sample in metric.samples:
            sample_labels = tuple(sample.labels.items())[0]
            self.assertEqual(expected_ts_samples[sample_labels], sample.value)

    def test_metrics_lcm_hw_end_of_support_location(self):
        """Test metric hw_end_of_support_location_gauge."""
        metric_gen = metrics_lcm_hw_end_of_support_location()

        # Get hw_end_of_support_location_gauge
        metric = next(metric_gen)

        expected_ts_samples = {
            ("location", "Location1"): 2,
            ("location", "Location2"): 0,
        }

        for sample in metric.samples:
            sample_labels = tuple(sample.labels.items())[0]
            self.assertEqual(expected_ts_samples[sample_labels], sample.value)

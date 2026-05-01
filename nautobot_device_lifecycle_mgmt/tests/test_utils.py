"""Tests for utility helpers."""

from nautobot.apps.testing import TestCase

from nautobot_device_lifecycle_mgmt.choices import CVESeverityChoices
from nautobot_device_lifecycle_mgmt.jobs.cve_tracking import NistCveSyncSoftware
from nautobot_device_lifecycle_mgmt.utils import standardize_cvss_severity


class StandardizeCvssSeverityTest(TestCase):
    """Test the standardize_cvss_severity function."""

    def test_nist_uppercase_values_map_to_choices(self):
        cases = {
            "CRITICAL": CVESeverityChoices.CRITICAL,
            "HIGH": CVESeverityChoices.HIGH,
            "MEDIUM": CVESeverityChoices.MEDIUM,
            "LOW": CVESeverityChoices.LOW,
            "NONE": CVESeverityChoices.NONE,
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(standardize_cvss_severity(raw), expected)

    def test_already_title_cased_values_pass_through(self):
        for value in (
            CVESeverityChoices.CRITICAL,
            CVESeverityChoices.HIGH,
            CVESeverityChoices.MEDIUM,
            CVESeverityChoices.LOW,
            CVESeverityChoices.NONE,
        ):
            with self.subTest(value=value):
                self.assertEqual(standardize_cvss_severity(value), value)

    def test_surrounding_whitespace_is_stripped(self):
        self.assertEqual(standardize_cvss_severity("  critical  "), CVESeverityChoices.CRITICAL)

    def test_empty_and_none_default_to_none_choice(self):
        self.assertEqual(standardize_cvss_severity(None), CVESeverityChoices.NONE)
        self.assertEqual(standardize_cvss_severity(""), CVESeverityChoices.NONE)

    def test_unknown_value_defaults_to_none_and_warns(self):
        logger_name = "nautobot_device_lifecycle_mgmt"
        for raw in ("UNDEFINED", "garbage", "extreme"):
            with self.subTest(raw=raw), self.assertLogs(logger_name, level="WARNING") as captured:
                self.assertEqual(standardize_cvss_severity(raw), CVESeverityChoices.NONE)
            self.assertTrue(any("Unrecognized CVSS severity" in message for message in captured.output))


class ConvertV2BaseScoreToSeverityTest(TestCase):
    """Test the convert_v2_base_score_to_severity function."""

    def test_low_band(self):
        for score in (0.0, 1.5, 3.9):
            with self.subTest(score=score):
                self.assertEqual(NistCveSyncSoftware.convert_v2_base_score_to_severity(score), CVESeverityChoices.LOW)

    def test_medium_band(self):
        for score in (4.0, 5.0, 6.9):
            with self.subTest(score=score):
                self.assertEqual(
                    NistCveSyncSoftware.convert_v2_base_score_to_severity(score), CVESeverityChoices.MEDIUM
                )

    def test_high_band(self):
        for score in (7.0, 8.5, 10.0):
            with self.subTest(score=score):
                self.assertEqual(NistCveSyncSoftware.convert_v2_base_score_to_severity(score), CVESeverityChoices.HIGH)

    def test_out_of_band_returns_none(self):
        for score in (-1.0, 11.0):
            with self.subTest(score=score):
                self.assertEqual(NistCveSyncSoftware.convert_v2_base_score_to_severity(score), CVESeverityChoices.NONE)

"""Tests for custom management commands."""

from io import StringIO

from django.core.management import call_command
from nautobot.apps.testing import TestCase

from nautobot_device_lifecycle_mgmt.choices import CVESeverityChoices
from nautobot_device_lifecycle_mgmt.models import CVELCM


class FixCveSeveritiesCommandTest(TestCase):
    """Test the fix_cve_severities management command."""

    def test_standardizes_non_standard_severities(self):
        cve_lower = CVELCM.objects.create(
            name="CVE-1", published_date="2024-01-01", link="https://example.com/cve-1", severity="critical"
        )
        cve_upper = CVELCM.objects.create(
            name="CVE-2", published_date="2024-01-02", link="https://example.com/cve-2", severity="HIGH"
        )
        cve_padded = CVELCM.objects.create(
            name="CVE-3", published_date="2024-01-03", link="https://example.com/cve-3", severity="  low  "
        )
        cve_unknown = CVELCM.objects.create(
            name="CVE-4", published_date="2024-01-04", link="https://example.com/cve-4", severity="UNDEFINED"
        )
        cve_already_valid = CVELCM.objects.create(
            name="CVE-5",
            published_date="2024-01-05",
            link="https://example.com/cve-5",
            severity=CVESeverityChoices.MEDIUM,
        )

        out = StringIO()
        call_command("fix_cve_severities", stdout=out)

        for cve in (cve_lower, cve_upper, cve_padded, cve_unknown, cve_already_valid):
            cve.refresh_from_db()

        self.assertEqual(cve_lower.severity, CVESeverityChoices.CRITICAL)
        self.assertEqual(cve_upper.severity, CVESeverityChoices.HIGH)
        self.assertEqual(cve_padded.severity, CVESeverityChoices.LOW)
        self.assertEqual(cve_unknown.severity, CVESeverityChoices.NONE)
        self.assertEqual(cve_already_valid.severity, CVESeverityChoices.MEDIUM)
        self.assertIn("Standardized severity on 4 CVE record(s).", out.getvalue())

    def test_idempotent_second_run_changes_nothing(self):
        CVELCM.objects.create(
            name="CVE-100",
            published_date="2024-01-01",
            link="https://example.com/cve-100",
            severity="critical",
        )

        call_command("fix_cve_severities", stdout=StringIO())
        out = StringIO()
        call_command("fix_cve_severities", stdout=out)

        self.assertIn("Standardized severity on 0 CVE record(s).", out.getvalue())

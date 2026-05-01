"""Standardize existing CVELCM severity values to CVESeverityChoices."""

from django.core.management.base import BaseCommand

from nautobot_device_lifecycle_mgmt.models import CVELCM
from nautobot_device_lifecycle_mgmt.utils import standardize_cvss_severity


class Command(BaseCommand):
    """Standardize existing CVELCM severity values to CVESeverityChoices."""

    help = __doc__

    def handle(self, *args, **options):
        """Update any non-standard CVELCM.severity values to the title-cased choices."""
        updated = 0
        for raw in CVELCM.objects.values_list("severity", flat=True).distinct():
            standardized = standardize_cvss_severity(raw)
            if standardized != raw:
                updated += CVELCM.objects.filter(severity=raw).update(severity=standardized)
        self.stdout.write(self.style.SUCCESS(f"Standardized severity on {updated} CVE record(s)."))

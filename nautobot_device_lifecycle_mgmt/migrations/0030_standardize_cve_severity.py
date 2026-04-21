from django.db import migrations

from nautobot_device_lifecycle_mgmt.utils import standardize_cvss_severity


def standardize_cve_severity(apps, schema_editor):
    """Coerce CVELCM.severity values to CVESeverityChoices via standardize_cvss_severity."""
    CVELCM = apps.get_model("nautobot_device_lifecycle_mgmt", "CVELCM")
    for raw in CVELCM.objects.values_list("severity", flat=True).distinct():
        standardized = standardize_cvss_severity(raw)
        if standardized != raw:
            CVELCM.objects.filter(severity=raw).update(severity=standardized)


class Migration(migrations.Migration):
    dependencies = [
        ("nautobot_device_lifecycle_mgmt", "0029_contractlcm_status"),
    ]

    operations = [
        migrations.RunPython(code=standardize_cve_severity, reverse_code=migrations.RunPython.noop),
    ]

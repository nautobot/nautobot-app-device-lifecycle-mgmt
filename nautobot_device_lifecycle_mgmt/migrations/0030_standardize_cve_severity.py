from django.db import migrations

_VALID_SEVERITIES = {"Critical", "High", "Medium", "Low", "None"}


def _standardize(raw):
    if not raw:
        return "None"
    candidate = raw.strip().title()
    return candidate if candidate in _VALID_SEVERITIES else "None"


def standardize_cve_severity(apps, schema_editor):
    """Coerce CVELCM.severity values to CVESeverityChoices via standardize_cvss_severity."""
    CVELCM = apps.get_model("nautobot_device_lifecycle_mgmt", "CVELCM")
    for raw in CVELCM.objects.values_list("severity", flat=True).distinct():
        standardized = _standardize(raw)
        if standardized != raw:
            CVELCM.objects.filter(severity=raw).update(severity=standardized)


class Migration(migrations.Migration):
    dependencies = [
        ("nautobot_device_lifecycle_mgmt", "0029_contractlcm_status"),
    ]

    operations = [
        migrations.RunPython(code=standardize_cve_severity, reverse_code=migrations.RunPython.noop),
    ]

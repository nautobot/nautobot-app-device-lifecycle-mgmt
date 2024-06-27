import uuid

from django.db import migrations


def migrate_softwarelcm_references(apps, schema_editor):
    """
    Save to the temp field the current software version id.
    """
    Software = apps.get_model("nautobot_device_lifecycle_mgmt", "SoftwareLCM")
    ValidatedSoftware = apps.get_model("nautobot_device_lifecycle_mgmt", "ValidatedSoftwareLCM")
    DeviceSoftwareValidationResult = apps.get_model("nautobot_device_lifecycle_mgmt", "DeviceSoftwareValidationResult")
    InventoryItemSoftwareValidationResult = apps.get_model(
        "nautobot_device_lifecycle_mgmt", "InventoryItemSoftwareValidationResult"
    )
    CVE = apps.get_model("nautobot_device_lifecycle_mgmt", "CVELCM")
    Vulnerability = apps.get_model("nautobot_device_lifecycle_mgmt", "VulnerabilityLCM")

    for validated_software in ValidatedSoftware.objects.all():
        validated_software.software_id = validated_software.software_tmp
        validated_software.save()

    for device_soft_val_res in DeviceSoftwareValidationResult.objects.all():
        if device_soft_val_res.software_tmp:
            device_soft_val_res.software_id = device_soft_val_res.software_tmp
            device_soft_val_res.save()

    for invitem_soft_val_res in InventoryItemSoftwareValidationResult.objects.all():
        if invitem_soft_val_res.software_tmp:
            invitem_soft_val_res.software_id = invitem_soft_val_res.software_tmp
            invitem_soft_val_res.save()

    for cve in CVE.objects.all():
        if cve.software_tmp:
            softwares = [uuid.UUID(soft_id) for soft_id in cve.software_tmp]
            cve.affected_softwares.set(softwares)
            cve.save()

    for vuln in Vulnerability.objects.all():
        if vuln.software_tmp:
            vuln.software_id = vuln.software_tmp
            vuln.save()

    Software.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("nautobot_device_lifecycle_mgmt", "0026_migrate_soft_references_p3"),
    ]

    operations = [
        migrations.RunPython(migrate_softwarelcm_references),
    ]

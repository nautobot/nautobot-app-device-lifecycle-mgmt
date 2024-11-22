from django.db import migrations


def save_existing_softwarelcm_references(apps, schema_editor):
    """
    Save the current SoftwareLCM reference to the temp fields.
    """
    ValidatedSoftware = apps.get_model("nautobot_device_lifecycle_mgmt", "ValidatedSoftwareLCM")
    DeviceSoftwareValidationResult = apps.get_model("nautobot_device_lifecycle_mgmt", "DeviceSoftwareValidationResult")
    InventoryItemSoftwareValidationResult = apps.get_model(
        "nautobot_device_lifecycle_mgmt", "InventoryItemSoftwareValidationResult"
    )
    CVE = apps.get_model("nautobot_device_lifecycle_mgmt", "CVELCM")
    Vulnerability = apps.get_model("nautobot_device_lifecycle_mgmt", "VulnerabilityLCM")

    for validated_software in ValidatedSoftware.objects.all():
        validated_software.software_tmp = validated_software.software.id
        validated_software.save()

    for device_soft_val_res in DeviceSoftwareValidationResult.objects.all():
        if device_soft_val_res.software:
            device_soft_val_res.software_tmp = device_soft_val_res.software.id
            device_soft_val_res.save()

    for invitem_soft_val_res in InventoryItemSoftwareValidationResult.objects.all():
        if invitem_soft_val_res.software:
            invitem_soft_val_res.software_tmp = invitem_soft_val_res.software.id
            invitem_soft_val_res.save()

    for cve in CVE.objects.all():
        cve.software_tmp = [str(soft.id) for soft in cve.affected_softwares.all()]
        cve.save()

    for vuln in Vulnerability.objects.all():
        if vuln.software:
            vuln.software_tmp = vuln.software.id
            vuln.save()


class Migration(migrations.Migration):
    dependencies = [
        ("nautobot_device_lifecycle_mgmt", "0024_migrate_soft_references_p1"),
    ]

    operations = [
        migrations.RunPython(save_existing_softwarelcm_references),
    ]

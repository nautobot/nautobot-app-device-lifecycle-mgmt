from django.db import migrations

import logging

logger = logging.getLogger(__name__)


def save_existing_softwarelcm_references(apps, schema_editor):
    """
    Save to the temp field the current software version id.
    """
    ValidatedSoftware = apps.get_model("nautobot_device_lifecycle_mgmt", "ValidatedSoftwareLCM")
    DeviceSoftwareValidationResult = apps.get_model("nautobot_device_lifecycle_mgmt", "DeviceSoftwareValidationResult")
    InventoryItemSoftwareValidationResult = apps.get_model(
        "nautobot_device_lifecycle_mgmt", "InventoryItemSoftwareValidationResult"
    )
    CVE = apps.get_model("nautobot_device_lifecycle_mgmt", "CVELCM")
    Vulnerability = apps.get_model("nautobot_device_lifecycle_mgmt", "VulnerabilityLCM")

    for validated_software in ValidatedSoftware.objects.all():
        logger.info(validated_software)
        validated_software.software_tmp = validated_software.software.id
        logger.info(validated_software.software_tmp)
        validated_software.save()

    for device_soft_val_res in DeviceSoftwareValidationResult.objects.all():
        logger.info(device_soft_val_res)
        if device_soft_val_res.software:
            device_soft_val_res.software_tmp = device_soft_val_res.software.id
            logger.info(device_soft_val_res.software_tmp)
            device_soft_val_res.save()

    for invitem_soft_val_res in InventoryItemSoftwareValidationResult.objects.all():
        logger.info(invitem_soft_val_res)
        if invitem_soft_val_res.software:
            invitem_soft_val_res.software_tmp = invitem_soft_val_res.software.id
            logger.info(invitem_soft_val_res.software_tmp)
            invitem_soft_val_res.save()

    for cve in CVE.objects.all():
        logger.info(cve)
        cve.software_tmp = [str(soft.id) for soft in cve.affected_softwares.all()]
        logger.info(cve.software_tmp)
        cve.save()

    for vuln in Vulnerability.objects.all():
        logger.info(vuln)
        if vuln.software:
            vuln.software_tmp = vuln.software.id
            logger.info(vuln.software_tmp)
            vuln.save()


class Migration(migrations.Migration):
    dependencies = [
        ("nautobot_device_lifecycle_mgmt", "0023_migrate_soft_references_p1"),
    ]

    operations = [
        migrations.RunPython(save_existing_softwarelcm_references),
    ]

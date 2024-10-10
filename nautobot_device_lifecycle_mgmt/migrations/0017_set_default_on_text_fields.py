from django.db import migrations


def set_default_on_contact_text_fields(apps, schema_editor):
    """
    Set default on ContactLCM text field to an empty string instead of None.
    """
    ContactLCM = apps.get_model("nautobot_device_lifecycle_mgmt", "ContactLCM")

    for contact in ContactLCM.objects.all():
        if contact.comments is None:
            contact.comments = ""
            contact.save()


def set_default_on_contract_text_fields(apps, schema_editor):
    """
    Set default on ContractLCM text field to an empty string instead of None.
    """
    ContractLCM = apps.get_model("nautobot_device_lifecycle_mgmt", "ContractLCM")

    for contract in ContractLCM.objects.all():
        object_updated = False
        for field in ("comments", "contract_type", "currency", "number", "support_level"):
            if getattr(contract, field) is None:
                setattr(contract, field, "")
                object_updated = True
        if object_updated:
            contract.save()


def set_default_on_cve_text_fields(apps, schema_editor):
    """
    Set default on CVELCM text field to an empty string instead of None.
    """
    CVELCM = apps.get_model("nautobot_device_lifecycle_mgmt", "CVELCM")

    for cve in CVELCM.objects.all():
        object_updated = False
        for field in ("comments", "description", "fix"):
            if getattr(cve, field) is None:
                setattr(cve, field, "")
                object_updated = True
        if object_updated:
            cve.save()


def set_default_on_hardware_text_fields(apps, schema_editor):
    """
    Set default on HardwareLCM text field to an empty string instead of None.
    """
    HardwareLCM = apps.get_model("nautobot_device_lifecycle_mgmt", "HardwareLCM")

    for hardware in HardwareLCM.objects.all():
        if hardware.comments is None:
            hardware.comments = ""
            hardware.save()


def set_default_on_provider_text_fields(apps, schema_editor):
    """
    Set default on ProviderLCM text field to an empty string instead of None.
    """
    ProviderLCM = apps.get_model("nautobot_device_lifecycle_mgmt", "ProviderLCM")

    for provider in ProviderLCM.objects.all():
        if provider.comments is None:
            provider.comments = ""
            provider.save()


def set_default_on_software_text_fields(apps, schema_editor):
    """
    Set default on SoftwareLCM text field to an empty string instead of None.
    """
    SoftwareLCM = apps.get_model("nautobot_device_lifecycle_mgmt", "SoftwareLCM")

    for software in SoftwareLCM.objects.all():
        if software.alias is None:
            software.alias = ""
            software.save()


class Migration(migrations.Migration):
    dependencies = [
        ("nautobot_device_lifecycle_mgmt", "0001_hardwarelcm"),
        ("nautobot_device_lifecycle_mgmt", "0002_softwarelcm"),
        ("nautobot_device_lifecycle_mgmt", "0003_service_contracts"),
        ("nautobot_device_lifecycle_mgmt", "0006_cvelcm_vulnerabilitylcm"),
    ]

    operations = [
        migrations.RunPython(code=set_default_on_contact_text_fields, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(code=set_default_on_contract_text_fields, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(code=set_default_on_cve_text_fields, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(code=set_default_on_hardware_text_fields, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(code=set_default_on_provider_text_fields, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(code=set_default_on_software_text_fields, reverse_code=migrations.RunPython.noop),
    ]

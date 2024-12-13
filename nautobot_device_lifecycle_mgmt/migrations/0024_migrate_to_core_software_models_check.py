from django.core.exceptions import ValidationError
from django.db import migrations


def verify_dlm_models_migated_to_core(apps, schema_editor):
    """Verifies whether the objects for the following DLM models have been migrated to the corresponding Core models
    DLM SoftwareLCM -> Core SoftwareVersion
    DLM SoftwareImageLCM -> Core SoftwareImageFile
    DLM Contact -> Core Contact
    """
    DLMContact = apps.get_model("nautobot_device_lifecycle_mgmt", "ContactLCM")
    DLMSoftwareVersion = apps.get_model("nautobot_device_lifecycle_mgmt", "SoftwareLCM")
    DLMSoftwareImage = apps.get_model("nautobot_device_lifecycle_mgmt", "SoftwareImageLCM")

    # Verify nautobot_device_lifecycle_mgmt.SoftwareLCM instances were migrated to dcim.SoftwareVersion
    for dlm_software_version in DLMSoftwareVersion.objects.all():
        _verify_software_version_migrated(apps, dlm_software_version)

    # Verify nautobot_device_lifecycle_mgmt.SoftwareImageLCM instances were migrated to dcim.SoftwareImageFile
    for dlm_software_image in DLMSoftwareImage.objects.all():
        _verify_software_image_migrated(apps, dlm_software_image)

    # Verify nautobot_device_lifecycle_mgmt.ContactLCM instances were migrated to extras.Contact
    for dlm_contact in DLMContact.objects.all():
        _verify_contact_migrated(apps, dlm_contact)


def _verify_software_version_migrated(apps, dlm_software_version):
    """Verifies instances of DLM SoftwareLCM were migrated to Core SoftwareVersion."""
    CoreSoftwareVersion = apps.get_model("dcim", "SoftwareVersion")

    core_software_version_q = CoreSoftwareVersion.objects.filter(
        platform=dlm_software_version.device_platform, version=dlm_software_version.version
    )
    if not core_software_version_q.exists():
        raise ValidationError(
            f"DLM Migration Error: Did not find Core SoftwareVersion object matching DLM Software object: {dlm_software_version}"
        )
    return


def _verify_software_image_migrated(apps, dlm_software_image):
    """Verifies instances of DLM SoftwareImageLCM were migrated to Core SoftwareImageFile."""
    SoftwareVersion = apps.get_model("dcim", "SoftwareVersion")
    SoftwareImageFile = apps.get_model("dcim", "SoftwareImageFile")

    dlm_software_version = dlm_software_image.software
    core_software_version_q = SoftwareVersion.objects.filter(
        platform=dlm_software_version.device_platform, version=dlm_software_version.version
    )
    if not core_software_version_q.exists():
        raise ValidationError(
            f"DLM Migration Error: Did not find Core SoftwareVersion matching DLM SoftwareVersion on DLM SoftwareImage object: {dlm_software_image}"
        )
    core_software_image_q = SoftwareImageFile.objects.filter(
        image_file_name=dlm_software_image.image_file_name, software_version=core_software_version_q.first()
    )
    if not core_software_image_q.exists():
        raise ValidationError(
            f"DLM Migration Error: Did not find Core SoftwareImage object matching DLM SoftwareImage object: {dlm_software_image}"
        )
    return


def _verify_contact_migrated(apps, dlm_contact):
    """Verifies instances of DLM Contact were migrated to Core Contact."""
    CoreContact = apps.get_model("extras", "Contact")

    core_contact_q = CoreContact.objects.filter(name=dlm_contact.name, phone=dlm_contact.phone, email=dlm_contact.email)
    if not core_contact_q.exists():
        raise ValidationError(
            f"DLM Migration Error: Did not find Core Contact object matching DLM Contact object: {dlm_contact}"
        )
    return


class Migration(migrations.Migration):
    dependencies = [
        ("dcim", "0055_softwareimage_softwareversion_data_migration"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("extras", "0057_jobbutton"),
        ("nautobot_device_lifecycle_mgmt", "0023_cvelcm_affected_softwares_tmp_and_more"),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(code=verify_dlm_models_migated_to_core, reverse_code=migrations.RunPython.noop),
    ]

# Migrates software image data from the SoftwareLCM objects to their own SoftwareImageLCM objects
from django.db import migrations
from django.db.models import Q


def migrate_software_images(apps, schema_editor):
    """
    Migrate software image data from SoftwareLCM objects to SoftwareImageLCM objects.
    """
    SoftwareLCM = apps.get_model("nautobot_device_lifecycle_mgmt", "SoftwareLCM")
    SoftwareImageLCM = apps.get_model("nautobot_device_lifecycle_mgmt", "SoftwareImageLCM")
    image_name_q = Q(image_file_name="")
    for software in SoftwareLCM.objects.filter(~image_name_q):
        software_image = SoftwareImageLCM(
            software=software,
            image_file_name=software.image_file_name,
            image_file_checksum=software.image_file_checksum,
            download_url=software.download_url,
            default_image=True,
        )
        software_image.save()


class Migration(migrations.Migration):
    dependencies = [
        ("nautobot_device_lifecycle_mgmt", "0007_softwareimagelcm"),
    ]

    operations = [
        migrations.RunPython(code=migrate_software_images, reverse_code=migrations.RunPython.noop),
    ]

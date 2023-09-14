from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("nautobot_device_lifecycle_mgmt", "0010_softwareimagelcm_hash_algorithm"),
    ]

    operations = [
        migrations.AddField(
            model_name="devicesoftwarevalidationresult",
            name="valid_software",
            field=models.ManyToManyField(
                related_name="_nautobot_device_lifecycle_mgmt_devicesoftwarevalidationresult_valid_software_+",
                to="nautobot_device_lifecycle_mgmt.ValidatedSoftwareLCM",
            ),
        ),
        migrations.AddField(
            model_name="inventoryitemsoftwarevalidationresult",
            name="valid_software",
            field=models.ManyToManyField(
                related_name="_nautobot_device_lifecycle_mgmt_inventoryitemsoftwarevalidationresult_valid_software_+",
                to="nautobot_device_lifecycle_mgmt.ValidatedSoftwareLCM",
            ),
        ),
    ]

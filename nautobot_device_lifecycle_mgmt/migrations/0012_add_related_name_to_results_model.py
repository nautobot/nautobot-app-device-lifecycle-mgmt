from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("nautobot_device_lifecycle_mgmt", "0011_add_valid_software_field_to_result"),
    ]

    operations = [
        migrations.AlterField(
            model_name="devicesoftwarevalidationresult",
            name="valid_software",
            field=models.ManyToManyField(
                related_name="device_software_validation_results",
                to="nautobot_device_lifecycle_mgmt.ValidatedSoftwareLCM",
            ),
        ),
        migrations.AlterField(
            model_name="inventoryitemsoftwarevalidationresult",
            name="valid_software",
            field=models.ManyToManyField(
                related_name="inventory_item_software_validation_results",
                to="nautobot_device_lifecycle_mgmt.ValidatedSoftwareLCM",
            ),
        ),
    ]

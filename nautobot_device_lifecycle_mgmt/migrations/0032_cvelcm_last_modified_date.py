# Generated by Django 4.2.15 on 2024-11-28 00:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("nautobot_device_lifecycle_mgmt", "0031_devicehardwarenoticeresult"),
    ]

    operations = [
        migrations.AddField(
            model_name="cvelcm",
            name="last_modified_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]

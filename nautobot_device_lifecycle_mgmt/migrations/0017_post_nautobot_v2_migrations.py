from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dcim", "0049_remove_slugs_and_change_device_primary_ip_fields"),
        ("nautobot_device_lifecycle_mgmt", "0016_role_migration_cleanup"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contractlcm",
            name="contract_type",
            field=models.CharField(blank=True, default="", max_length=32),
        ),
        migrations.AlterField(
            model_name="contractlcm",
            name="currency",
            field=models.CharField(blank=True, default="", max_length=4),
        ),
        migrations.AlterField(
            model_name="contractlcm",
            name="number",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AlterField(
            model_name="contractlcm",
            name="support_level",
            field=models.CharField(blank=True, default="", max_length=64),
        ),
        migrations.AlterField(
            model_name="cvelcm",
            name="description",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AlterField(
            model_name="cvelcm",
            name="fix",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AlterField(
            model_name="hardwarelcm",
            name="comments",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="softwarelcm",
            name="alias",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
        migrations.AlterUniqueTogether(
            name="validatedsoftwarelcm",
            unique_together={("software", "start", "end")},
        ),
        migrations.AlterUniqueTogether(
            name="vulnerabilitylcm",
            unique_together={("cve", "software", "inventory_item"), ("cve", "software", "device")},
        ),
    ]

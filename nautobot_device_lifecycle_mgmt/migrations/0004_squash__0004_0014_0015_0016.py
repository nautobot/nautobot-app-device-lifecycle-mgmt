from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dcim", "0005_device_local_context_schema"),
        ("extras", "0013_default_fallback_value_computedfield"),
        ("nautobot_device_lifecycle_mgmt", "0003_service_contracts"),
    ]

    replaces = [
        ("nautobot_device_lifecycle_mgmt", "0004_validated_software_m2m"),
        ("nautobot_device_lifecycle_mgmt", "0014_pre_nautobot_v2_migrations"),
        ("nautobot_device_lifecycle_mgmt", "0015_role_migration"),
        ("nautobot_device_lifecycle_mgmt", "0016_role_migration_cleanup"),
    ]

    operations = [
        # 0004_validated_software_m2m
        migrations.AlterModelOptions(
            name="softwarelcm",
            options={
                "ordering": ("device_platform", "version", "end_of_support", "release_date"),
                "verbose_name": "Software",
            },
        ),
        migrations.AddField(
            model_name="validatedsoftwarelcm",
            name="device_roles",
            field=models.ManyToManyField(
                blank=True, related_name="_validatedsoftwarelcm_device_roles_+", to="extras.Role"
            ),
        ),
        migrations.AddField(
            model_name="validatedsoftwarelcm",
            name="device_types",
            field=models.ManyToManyField(
                blank=True, related_name="_validatedsoftwarelcm_device_types_+", to="dcim.DeviceType"
            ),
        ),
        migrations.AddField(
            model_name="validatedsoftwarelcm",
            name="devices",
            field=models.ManyToManyField(blank=True, related_name="_validatedsoftwarelcm_devices_+", to="dcim.Device"),
        ),
        migrations.AddField(
            model_name="validatedsoftwarelcm",
            name="inventory_items",
            field=models.ManyToManyField(
                blank=True, related_name="_validatedsoftwarelcm_inventory_items_+", to="dcim.InventoryItem"
            ),
        ),
        migrations.AddField(
            model_name="validatedsoftwarelcm",
            name="object_tags",
            field=models.ManyToManyField(
                blank=True, related_name="_validatedsoftwarelcm_object_tags_+", to="extras.Tag"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="validatedsoftwarelcm",
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name="validatedsoftwarelcm",
            name="assigned_to_content_type",
        ),
        migrations.RemoveField(
            model_name="validatedsoftwarelcm",
            name="assigned_to_object_id",
        ),
    ]

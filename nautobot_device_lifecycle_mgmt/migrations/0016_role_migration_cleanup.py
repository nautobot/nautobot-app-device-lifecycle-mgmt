from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("nautobot_device_lifecycle_mgmt", "0015_role_migration"),
    ]

    run_before = [("dcim", "0031_remove_device_role_and_rack_role")]

    operations = [
        migrations.RemoveField(
            model_name="validatedsoftwarelcm",
            name="legacy_roles",
        ),
        migrations.RenameField(
            model_name="validatedsoftwarelcm",
            old_name="new_roles",
            new_name="device_roles",
        ),
    ]

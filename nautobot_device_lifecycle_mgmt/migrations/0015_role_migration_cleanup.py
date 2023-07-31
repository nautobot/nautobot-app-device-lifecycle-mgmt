from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("nautobot_device_lifecycle_mgmt", "0014_role_migration"),
    ]

    run_before = [("dcim", "0027_remove_device_role_and_rack_role")]

    operations = [
        migrations.RemoveField(
            model_name="validatedsoftwarelcm",
            name="legacy_roles",
        ),
        migrations.RenameField(
            model_name="validatedsoftwarelcm",
            old_name="new_roles",
            new_name="roles",
        ),
    ]

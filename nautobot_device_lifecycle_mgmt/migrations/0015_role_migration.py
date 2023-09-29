from django.db import migrations
from nautobot.extras.utils import migrate_role_data


def migrate_data_from_legacy_role_to_new_role(apps, schema):
    """Transfer data from legacy_role to new_role."""
    to_role_model = apps.get_model("extras", "Role")
    from_role_model = apps.get_model("dcim", "DeviceRole")
    model = apps.get_model("nautobot_device_lifecycle_mgmt", "ValidatedSoftwareLCM")
    migrate_role_data(
        is_m2m_field=True,
        model_to_migrate=model,
        from_role_field_name="legacy_roles",
        from_role_model=from_role_model,
        to_role_field_name="new_roles",
        to_role_model=to_role_model,
    )


def reverse_role_data_migrate(apps, schema):
    """Transfer data from new_role to legacy_role."""
    from_role_model = apps.get_model("extras", "Role")
    model = apps.get_model("nautobot_device_lifecycle_mgmt", "ValidatedSoftwareLCM")
    to_role_model = apps.get_model("dcim", "DeviceRole")

    migrate_role_data(
        is_m2m_field=True,
        model_to_migrate=model,
        from_role_field_name="new_roles",
        from_role_model=from_role_model,
        to_role_field_name="legacy_roles",
        to_role_model=to_role_model,
    )


class Migration(migrations.Migration):
    dependencies = [
        ("nautobot_device_lifecycle_mgmt", "0014_pre_nautobot_v2_migrations"),
    ]

    operations = [
        migrations.RunPython(migrate_data_from_legacy_role_to_new_role, reverse_role_data_migrate),
    ]

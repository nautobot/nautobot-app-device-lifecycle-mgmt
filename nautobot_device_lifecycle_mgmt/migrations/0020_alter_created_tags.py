import nautobot.core.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("nautobot_device_lifecycle_mgmt", "0001_hardwarelcm"),
        ("nautobot_device_lifecycle_mgmt", "0002_softwarelcm"),
        ("nautobot_device_lifecycle_mgmt", "0003_service_contracts"),
        ("nautobot_device_lifecycle_mgmt", "0005_software_reporting"),
        ("nautobot_device_lifecycle_mgmt", "0006_cvelcm_vulnerabilitylcm"),
        ("nautobot_device_lifecycle_mgmt", "0007_softwareimagelcm"),
        # This migration does not actually depend on the below migrations but they are added here to
        # prevent Django from failing to migrate due to multiple leaf nodes in the migration graph
        ("nautobot_device_lifecycle_mgmt", "0013_alter_softwareimagelcm_device_types"),
        ("nautobot_device_lifecycle_mgmt", "0016_role_migration_cleanup"),
        ("nautobot_device_lifecycle_mgmt", "0019_cve_and_contract_m2m_migration"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contactlcm",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="contactlcm",
            name="tags",
            field=nautobot.core.models.fields.TagsField(through="extras.TaggedItem", to="extras.Tag"),
        ),
        migrations.AlterField(
            model_name="contractlcm",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="contractlcm",
            name="tags",
            field=nautobot.core.models.fields.TagsField(through="extras.TaggedItem", to="extras.Tag"),
        ),
        migrations.AlterField(
            model_name="cvelcm",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="cvelcm",
            name="tags",
            field=nautobot.core.models.fields.TagsField(through="extras.TaggedItem", to="extras.Tag"),
        ),
        migrations.AlterField(
            model_name="devicesoftwarevalidationresult",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="devicesoftwarevalidationresult",
            name="tags",
            field=nautobot.core.models.fields.TagsField(through="extras.TaggedItem", to="extras.Tag"),
        ),
        migrations.AlterField(
            model_name="hardwarelcm",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="hardwarelcm",
            name="tags",
            field=nautobot.core.models.fields.TagsField(through="extras.TaggedItem", to="extras.Tag"),
        ),
        migrations.AlterField(
            model_name="inventoryitemsoftwarevalidationresult",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="inventoryitemsoftwarevalidationresult",
            name="tags",
            field=nautobot.core.models.fields.TagsField(through="extras.TaggedItem", to="extras.Tag"),
        ),
        migrations.AlterField(
            model_name="providerlcm",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="softwareimagelcm",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="softwareimagelcm",
            name="tags",
            field=nautobot.core.models.fields.TagsField(through="extras.TaggedItem", to="extras.Tag"),
        ),
        migrations.AlterField(
            model_name="softwarelcm",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="softwarelcm",
            name="tags",
            field=nautobot.core.models.fields.TagsField(through="extras.TaggedItem", to="extras.Tag"),
        ),
        migrations.AlterField(
            model_name="validatedsoftwarelcm",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="validatedsoftwarelcm",
            name="tags",
            field=nautobot.core.models.fields.TagsField(through="extras.TaggedItem", to="extras.Tag"),
        ),
        migrations.AlterField(
            model_name="vulnerabilitylcm",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="vulnerabilitylcm",
            name="tags",
            field=nautobot.core.models.fields.TagsField(through="extras.TaggedItem", to="extras.Tag"),
        ),
    ]

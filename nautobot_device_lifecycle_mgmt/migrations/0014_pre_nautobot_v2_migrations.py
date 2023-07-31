from django.db import migrations, models
import nautobot.core.models.fields


class Migration(migrations.Migration):
    dependencies = [
        ("extras", "0062_collect_roles_from_related_apps_roles"),
        ("nautobot_device_lifecycle_mgmt", "0013_alter_softwareimagelcm_device_types"),
    ]

    operations = [
        migrations.AddField(
            model_name="validatedsoftwarelcm",
            name="new_roles",
            field=models.ManyToManyField(
                blank=True, related_name="_validatedsoftwarelcm_new_roles_+", to="extras.Role"
            ),
        ),
        migrations.RenameField(
            model_name="validatedsoftwarelcm",
            old_name="device_roles",
            new_name="legacy_roles",
        ),
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

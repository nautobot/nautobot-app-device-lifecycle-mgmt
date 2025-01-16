# Generated by Django 4.2.16 on 2025-01-16 17:02

import uuid

import django.core.serializers.json
import django.db.models.deletion
import nautobot.core.models.fields
import nautobot.extras.models.mixins
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dcim", "0062_module_data_migration"),
        ("extras", "0114_computedfield_grouping"),
        ("nautobot_device_lifecycle_mgmt", "0029_devicehardwarenoticeresult"),
    ]

    operations = [
        migrations.CreateModel(
            name="SoftwareNotice",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "_custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
                ),
                ("end_of_sale", models.DateField(blank=True, null=True)),
                ("end_of_support", models.DateField(blank=True, null=True)),
                ("end_of_sw_releases", models.DateField(blank=True, null=True)),
                ("end_of_security_patches", models.DateField(blank=True, null=True)),
                ("documentation_url", models.URLField(blank=True)),
                ("comments", models.TextField(blank=True, default="")),
                (
                    "device_type",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="dcim.devicetype"
                    ),
                ),
                (
                    "software_version",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="dcim.softwareversion"
                    ),
                ),
                ("tags", nautobot.core.models.fields.TagsField(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "verbose_name": "Software Notice",
                "ordering": ("end_of_sale",),
                "unique_together": {("software_version", "device_type")},
            },
            bases=(
                nautobot.extras.models.mixins.DynamicGroupMixin,
                nautobot.extras.models.mixins.NotesMixin,
                models.Model,
            ),
        ),
    ]

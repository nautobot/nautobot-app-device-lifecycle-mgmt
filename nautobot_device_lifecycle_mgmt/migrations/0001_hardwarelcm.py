# Generated by Django 3.1.13 on 2021-08-19 16:59

import uuid

import django.core.serializers.json
import django.db.models.deletion
import taggit.managers
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("extras", "0005_configcontext_device_types"),
        ("dcim", "0004_initial_part_4"),
    ]

    operations = [
        migrations.CreateModel(
            name="HardwareLCM",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("created", models.DateField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "_custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
                ),
                ("inventory_item", models.CharField(blank=True, max_length=255, null=True)),
                ("release_date", models.DateField(blank=True, null=True)),
                ("end_of_sale", models.DateField(blank=True, null=True)),
                ("end_of_support", models.DateField(blank=True, null=True)),
                ("end_of_sw_releases", models.DateField(blank=True, null=True)),
                ("end_of_security_patches", models.DateField(blank=True, null=True)),
                ("documentation_url", models.URLField(blank=True)),
                ("comments", models.TextField(blank=True, null=True)),
                (
                    "device_type",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="dcim.devicetype"
                    ),
                ),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "verbose_name": "Hardware Notice",
                "ordering": ("end_of_support", "end_of_sale"),
            },
        ),
        migrations.AddConstraint(
            model_name="hardwarelcm",
            constraint=models.UniqueConstraint(fields=("device_type",), name="unique_device_type"),
        ),
        migrations.AddConstraint(
            model_name="hardwarelcm",
            constraint=models.UniqueConstraint(fields=("inventory_item",), name="unique_inventory_item_part"),
        ),
        migrations.AddConstraint(
            model_name="hardwarelcm",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(("device_type__isnull", False), ("inventory_item__isnull", True)),
                    models.Q(("device_type__isnull", True), ("inventory_item__isnull", False)),
                    _connector="OR",
                ),
                name="At least one of InventoryItem or DeviceType specified.",
            ),
        ),
        migrations.AddConstraint(
            model_name="hardwarelcm",
            constraint=models.CheckConstraint(
                check=models.Q(("end_of_sale__isnull", False), ("end_of_support__isnull", False), _connector="OR"),
                name="End of Sale or End of Support must be specified.",
            ),
        ),
    ]

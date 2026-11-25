import uuid

import django.core.serializers.json
from django.db import migrations, models
from nautobot.apps.models import DynamicGroupMixin, NotesMixin, TagsField


class Migration(migrations.Migration):
    dependencies = [
        ("extras", "0106_populate_default_statuses_and_roles_for_contact_associations"),
        ("nautobot_device_lifecycle_mgmt", "0031_validatedsoftwarelcm_device_tenant"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeviceSoftwareValidationHistoricResult",
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
                ("date", models.DateTimeField()),
                ("run_type", models.CharField(max_length=255)),
                ("all_platforms", models.BooleanField(default=True)),
                ("all_tenants", models.BooleanField(default=True)),
                ("filters", models.JSONField(blank=True, default=dict)),
                ("device_validation_results", models.JSONField(blank=True, default=list)),
                ("tags", TagsField(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "verbose_name": "Device Software Validation Historic Result",
                "ordering": ("-date",),
                "unique_together": {("date", "run_type")},
            },
            bases=(
                models.Model,
                DynamicGroupMixin,
                NotesMixin,
            ),
        ),
    ]

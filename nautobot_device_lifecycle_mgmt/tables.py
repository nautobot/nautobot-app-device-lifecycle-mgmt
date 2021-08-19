<<<<<<< HEAD
"""Tables implementation for the LifeCycle Management plugin."""
=======
"""Tables for nautobot_plugin_device_lifecycle_mgmt."""
>>>>>>> c9c3a9d (Rename plugin)

import django_tables2 as tables
from django_tables2.utils import A
from nautobot.utilities.tables import BaseTable, ButtonsColumn, ToggleColumn
<<<<<<< HEAD
from nautobot_device_lifecycle_mgmt.models import HardwareLCM


class HardwareLCMTable(BaseTable):
=======
from nautobot_plugin_device_lifecycle_mgmt.models import EoxNotice, SoftwareLCM, ValidatedSoftwareLCM


class EoxNoticesTable(BaseTable):
>>>>>>> c9c3a9d (Rename plugin)
    """Table for list view."""

    pk = ToggleColumn()
    name = tables.LinkColumn(
<<<<<<< HEAD
        "plugins:nautobot_device_lifecycle_mgmt:hardwarelcm", text=lambda record: record, args=[A("pk")]
    )
    reference_item = tables.TemplateColumn(
        template_code="""{% if record.device_type %}
                    <a href="{% url 'dcim:devicetype' pk=record.device_type.pk %}">{{ record.device_type }}</a>
                    {% elif record.inventory_item %}
                    {{ record.inventory_item }}
                    {% endif %}""",
        verbose_name="Reference",
    )
    documentation_url = tables.TemplateColumn(
        template_code="""{% if record.documentation_url %}
                    <a href="{{ record.documentation_url }}" target="_blank" data-toggle="tooltip" data-placement="left" title="{{ record.documentation_url }}">
                        <span class="mdi mdi-open-in-new"></span>
                    </a>
                    {% else %}
                    —
                    {% endif %}""",
        verbose_name="Documentation",
    )
    actions = ButtonsColumn(HardwareLCM, buttons=("changelog", "edit", "delete"))
=======
        "plugins:nautobot_plugin_device_lifecycle_mgmt:eoxnotice", text=lambda record: record, args=[A("pk")]
    )
    devices = tables.TemplateColumn("{{ record.devices.count }}")
    device_type = tables.LinkColumn()
    actions = ButtonsColumn(EoxNotice, buttons=("edit", "delete"))
>>>>>>> c9c3a9d (Rename plugin)

    class Meta(BaseTable.Meta):  # pylint: disable=too-few-public-methods
        """Meta attributes."""

<<<<<<< HEAD
        model = HardwareLCM
        fields = (
            "pk",
            "name",
            "reference_item",
            "release_date",
=======
        model = EoxNotice
        fields = (
            "pk",
            "name",
            "devices",
            "device_type",
>>>>>>> c9c3a9d (Rename plugin)
            "end_of_sale",
            "end_of_support",
            "end_of_sw_releases",
            "end_of_security_patches",
<<<<<<< HEAD
            "documentation_url",
=======
            "notice_url",
            "actions",
        )


class SoftwareLCMTable(BaseTable):
    """Table for SoftwareLCMListView."""

    pk = ToggleColumn()
    name = tables.LinkColumn(
        "plugins:nautobot_plugin_device_lifecycle_mgmt:softwarelcm",
        text=lambda record: record,
        args=[A("pk")],
        orderable=False,
    )
    device_platform = tables.TemplateColumn("{{ record.device_platform }}")
    actions = ButtonsColumn(SoftwareLCM, buttons=("edit", "delete"))

    class Meta(BaseTable.Meta):  # pylint: disable=too-few-public-methods
        """Meta attributes."""

        model = SoftwareLCM
        fields = (
            "pk",
            "name",
            "version",
            "alias",
            "device_platform",
            "end_of_support",
            "end_of_security_patches",
            "long_term_support",
            "pre_release",
            "actions",
        )


class ValidatedSoftwareLCMTable(BaseTable):
    """Table for ValidatedSoftwareLCMListView."""

    pk = ToggleColumn()
    name = tables.LinkColumn(
        "plugins:nautobot_plugin_device_lifecycle_mgmt:validatedsoftwarelcm",
        text=lambda record: record,
        args=[
            A("pk"),
        ],
        orderable=False,
    )
    software = tables.LinkColumn(verbose_name="Software")
    assigned_to = tables.LinkColumn(verbose_name="Assigned To", orderable=False)
    actions = ButtonsColumn(ValidatedSoftwareLCM, buttons=("edit", "delete"))

    class Meta(BaseTable.Meta):  # pylint: disable=too-few-public-methods
        """Meta attributes."""

        model = ValidatedSoftwareLCM
        fields = (
            "pk",
            "name",
            "software",
            "assigned_to",
            "start",
            "end",
            "preferred",
>>>>>>> c9c3a9d (Rename plugin)
            "actions",
        )

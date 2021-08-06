"""Tables implementation for the LifeCycle Management plugin."""

import django_tables2 as tables
from django_tables2.utils import A
from nautobot.utilities.tables import BaseTable, ButtonsColumn, ToggleColumn
from nautobot_plugin_device_lifecycle_mgmt.models import HardwareLCM


class HardwareLCMNoticesTable(BaseTable):
    """Table for list view."""

    pk = ToggleColumn()
    name = tables.LinkColumn(
        "plugins:nautobot_plugin_device_lifecycle_mgmt:hardwarelcm", text=lambda record: record, args=[A("pk")]
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

    class Meta(BaseTable.Meta):  # pylint: disable=too-few-public-methods
        """Meta attributes."""

        model = HardwareLCM
        fields = (
            "pk",
            "name",
            "reference_item",
            "release_date",
            "end_of_sale",
            "end_of_support",
            "end_of_sw_releases",
            "end_of_security_patches",
            "documentation_url",
            "actions",
        )

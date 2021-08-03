"""Tables for nautobot_plugin_device_lifecycle_mgmt."""

import django_tables2 as tables
from django_tables2.utils import A
from nautobot.dcim.models import DeviceType, InventoryItem
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
                    <a href="{% url 'dcim:inventoryitem' pk=record.inventory_item.pk %}">{{ record.inventory_item }}</a>
                    {% endif %}""",
        verbose_name="Reference",
    )
    actions = ButtonsColumn(HardwareLCM, buttons=("edit", "delete"))

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

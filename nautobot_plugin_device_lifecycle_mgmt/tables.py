"""Tables for nautobot_plugin_device_lifecycle_mgmt."""

import django_tables2 as tables
from django_tables2.utils import A
from nautobot.utilities.tables import BaseTable, ButtonsColumn, ToggleColumn
from nautobot_plugin_device_lifecycle_mgmt.models import EoxNotice


class EoxNoticesTable(BaseTable):
    """Table for list view."""

    pk = ToggleColumn()
    name = tables.LinkColumn(
        "plugins:nautobot_plugin_device_lifecycle_mgmt:eoxnotice", text=lambda record: record, args=[A("pk")]
    )
    devices = tables.TemplateColumn("{{ record.devices.count }}")
    device_type = tables.LinkColumn()
    actions = ButtonsColumn(EoxNotice, buttons=("edit", "delete"))

    class Meta(BaseTable.Meta):  # pylint: disable=too-few-public-methods
        """Meta attributes."""

        model = EoxNotice
        fields = tuple(["pk", "name", "devices"] + EoxNotice.csv_headers + ["actions"])

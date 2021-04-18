"""Tables for eox_notices."""

import django_tables2 as tables
from django_tables2.utils import A
from nautobot.utilities.tables import BaseTable
from .models import EoxNotice


class EoxNoticesTable(BaseTable):
    """Table for list view."""

    name = tables.LinkColumn("plugins:eox_notices:eoxnotice", text=lambda record: record, args=[A("pk")])
    devices = tables.TemplateColumn("{{ record.devices.count }}")
    device_type = tables.LinkColumn()

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = EoxNotice
        fields = (
            "name",
            "devices",
            "device_type",
            "end_of_sale",
            "end_of_support",
            "end_of_sw_releases",
            "end_of_security_patches",
            "notice_url",
        )

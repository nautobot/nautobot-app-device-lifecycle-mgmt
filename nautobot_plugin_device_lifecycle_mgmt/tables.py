"""Tables for nautobot_plugin_device_lifecycle_mgmt."""

import django_tables2 as tables
from django_tables2.utils import A
from nautobot.utilities.tables import BaseTable, ButtonsColumn, ToggleColumn
from nautobot_plugin_device_lifecycle_mgmt.models import EoxNotice, SoftwareLCM, ValidatedSoftwareLCM


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
        fields = (
            "pk",
            "name",
            "devices",
            "device_type",
            "end_of_sale",
            "end_of_support",
            "end_of_sw_releases",
            "end_of_security_patches",
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
    softwarelcm = tables.LinkColumn(verbose_name="Software")
    assigned_to = tables.LinkColumn(verbose_name="Assigned To", orderable=False)
    actions = ButtonsColumn(ValidatedSoftwareLCM, buttons=("edit", "delete"))

    class Meta(BaseTable.Meta):  # pylint: disable=too-few-public-methods
        """Meta attributes."""

        model = ValidatedSoftwareLCM
        fields = (
            "pk",
            "name",
            "softwarelcm",
            "assigned_to",
            "start",
            "end",
            "preferred",
            "actions",
        )

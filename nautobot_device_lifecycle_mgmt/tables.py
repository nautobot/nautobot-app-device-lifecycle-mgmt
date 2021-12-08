"""Tables implementation for the Lifecycle Management plugin."""

import django_tables2 as tables
from django_tables2.utils import A
from nautobot.utilities.tables import BaseTable, ButtonsColumn, BooleanColumn, ToggleColumn
from nautobot_device_lifecycle_mgmt.models import (
    HardwareLCM,
    SoftwareLCM,
    ValidatedSoftwareLCM,
    ContractLCM,
    ProviderLCM,
    ContactLCM,
    DeviceSoftwareValidationResult,
    InventoryItemSoftwareValidationResult,
)


class PercentageColumn(tables.Column):
    """Column used to display percentage."""

    def render(self, value):
        """Render percentage value."""
        return f"{value} %"


class HardwareLCMTable(BaseTable):
    """Table for list view."""

    pk = ToggleColumn()
    name = tables.LinkColumn(
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


class SoftwareLCMTable(BaseTable):
    """Table for SoftwareLCMListView."""

    pk = ToggleColumn()
    name = tables.LinkColumn(
        "plugins:nautobot_device_lifecycle_mgmt:softwarelcm",
        text=lambda record: record,
        args=[A("pk")],
        orderable=False,
    )
    device_platform = tables.TemplateColumn("{{ record.device_platform }}")
    long_term_support = BooleanColumn()
    pre_release = BooleanColumn()
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
            "release_date",
            "end_of_support",
            "long_term_support",
            "pre_release",
            "actions",
        )


class ValidatedSoftwareLCMTable(BaseTable):
    """Table for ValidatedSoftwareLCMListView."""

    pk = ToggleColumn()
    name = tables.LinkColumn(
        "plugins:nautobot_device_lifecycle_mgmt:validatedsoftwarelcm",
        text=lambda record: record,
        args=[
            A("pk"),
        ],
        orderable=False,
    )
    valid = BooleanColumn(verbose_name="Valid Now", orderable=False)
    software = tables.LinkColumn(verbose_name="Software")
    actions = ButtonsColumn(ValidatedSoftwareLCM, buttons=("edit", "delete"))
    preferred = BooleanColumn()

    class Meta(BaseTable.Meta):  # pylint: disable=too-few-public-methods
        """Meta attributes."""

        model = ValidatedSoftwareLCM
        fields = (
            "pk",
            "name",
            "software",
            "start",
            "end",
            "valid",
            "preferred",
            "actions",
        )


class DeviceSoftwareValidationResultTable(BaseTable):
    """Table for device software validation report."""

    name = tables.Column(accessor="device__device_type__model", verbose_name="Device Type")
    total = tables.Column(accessor="total", verbose_name="Total")
    valid = tables.Column(accessor="valid", verbose_name="Valid")
    invalid = tables.Column(accessor="invalid", verbose_name="Invalid")
    no_software = tables.Column(accessor="no_software", verbose_name="No Software")
    valid_percent = PercentageColumn(accessor="valid_percent", verbose_name="Compliance (%)")

    class Meta(BaseTable.Meta):  # pylint: disable=too-few-public-methods
        """Metaclass attributes of DeviceSoftwareValidationResultTable."""

        model = DeviceSoftwareValidationResult
        fields = ["name", "total", "valid", "invalid", "no_software", "valid_percent"]
        default_columns = [
            "name",
            "total",
            "valid",
            "invalid",
            "no_software",
            "valid_percent",
        ]


class InventoryItemSoftwareValidationResultTable(BaseTable):
    """Table for inventory item software validation report."""

    part_id = tables.Column(accessor="inventory_item__part_id", verbose_name="Part ID")
    total = tables.Column(accessor="total", verbose_name="Total")
    valid = tables.Column(accessor="valid", verbose_name="Valid")
    invalid = tables.Column(accessor="invalid", verbose_name="Invalid")
    no_software = tables.Column(accessor="no_software", verbose_name="No Software")
    valid_percent = PercentageColumn(accessor="valid_percent", verbose_name="Compliance (%)")

    class Meta(BaseTable.Meta):  # pylint: disable=too-few-public-methods
        """Metaclass attributes of InventoryItemSoftwareValidationResultTable."""

        model = InventoryItemSoftwareValidationResult
        fields = ["part_id", "total", "valid", "invalid", "no_software", "valid_percent"]
        default_columns = [
            "part_id",
            "total",
            "valid",
            "invalid",
            "no_software",
            "valid_percent",
        ]


class ContractLCMTable(BaseTable):
    """Table for list view."""

    pk = ToggleColumn()
    name = tables.LinkColumn(
        "plugins:nautobot_device_lifecycle_mgmt:contractlcm", text=lambda record: record, args=[A("pk")]
    )
    provider = tables.LinkColumn(
        "plugins:nautobot_device_lifecycle_mgmt:providerlcm",
        text=lambda record: record.provider,
        args=[A("provider.pk")],
    )
    cost = tables.TemplateColumn(
        template_code="""{{ record.cost }}{% if record.currency %} {{ record.currency }}{% endif %}"""
    )
    actions = ButtonsColumn(ContractLCM, buttons=("changelog", "edit", "delete"))

    class Meta(BaseTable.Meta):  # pylint: disable=too-few-public-methods
        """Meta attributes."""

        model = ContractLCM
        fields = (
            "pk",
            "name",
            "start",
            "end",
            "cost",
            "support_level",
            "contract_type",
            "provider",
            "actions",
        )


class ProviderLCMTable(BaseTable):
    """Table for list view."""

    pk = ToggleColumn()
    name = tables.LinkColumn(
        "plugins:nautobot_device_lifecycle_mgmt:providerlcm", text=lambda record: record, args=[A("pk")]
    )
    portal_url = tables.TemplateColumn(
        template_code="""{% if record.portal_url %}
                    <a href="{{ record.portal_url }}" target="_blank" data-toggle="tooltip" data-placement="left" title="{{ record.portal_url }}">
                        <span class="mdi mdi-open-in-new"></span>
                    </a>{% else %} — {% endif %}""",
        verbose_name="URL",
    )
    actions = ButtonsColumn(ProviderLCM, buttons=("changelog", "edit", "delete"))

    class Meta(BaseTable.Meta):  # pylint: disable=too-few-public-methods
        """Meta attributes."""

        model = ProviderLCM
        fields = (
            "pk",
            "name",
            "physical_address",
            "phone",
            "email",
            "portal_url",
            "actions",
        )


class ContactLCMTable(BaseTable):
    """Table for list view."""

    pk = ToggleColumn()
    name = tables.LinkColumn(
        "plugins:nautobot_device_lifecycle_mgmt:contactlcm", text=lambda record: record, args=[A("pk")]
    )
    actions = ButtonsColumn(ContactLCM, buttons=("changelog", "edit", "delete"))

    class Meta(BaseTable.Meta):  # pylint: disable=too-few-public-methods
        """Meta attributes."""

        model = ContactLCM
        fields = (
            "pk",
            "name",
            "address",
            "phone",
            "email",
            "comments",
            "priority",
            "contract",
            "actions",
        )

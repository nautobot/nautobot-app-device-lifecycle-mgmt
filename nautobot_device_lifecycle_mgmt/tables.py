# pylint: disable='nb-use-fields-all'
"""Tables implementation for the Lifecycle Management app."""

import django_tables2 as tables
from django_tables2.utils import A
from nautobot.apps.tables import BaseTable, BooleanColumn, ButtonsColumn, StatusTableMixin, TagColumn, ToggleColumn

from nautobot_device_lifecycle_mgmt.models import (
    CVELCM,
    ContractLCM,
    DeviceHardwareNoticeResult,
    DeviceSoftwareValidationResult,
    HardwareLCM,
    InventoryItemSoftwareValidationResult,
    ProviderLCM,
    ValidatedSoftwareLCM,
    VulnerabilityLCM,
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
        "plugins:nautobot_device_lifecycle_mgmt:hardwarelcm",
        text=lambda record: record,
        args=[A("pk")],
        orderable=False,
    )
    reference_item = tables.TemplateColumn(
        template_code="""{% if record.device_type %}
                    <a href="{% url 'dcim:devicetype' pk=record.device_type.pk %}">{{ record.device_type }}</a>
                    {% elif record.inventory_item %}
                    {{ record.inventory_item }}
                    {% endif %}""",
        verbose_name="Reference",
        orderable=False,
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

    class Meta(BaseTable.Meta):
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

    class Meta(BaseTable.Meta):
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


class DeviceHardwareNoticeResultTable(BaseTable):
    """Table for device hardware notice report."""

    name = tables.TemplateColumn(
        template_code='<a href="/plugins/nautobot-device-lifecycle-mgmt/hardware-notice-device-report/'
        '?&device_type={{ record.device__device_type__model }}">{{ record.device__device_type__model }}</a>',
        orderable=True,
        accessor="device__device_type__model",
    )
    total = tables.TemplateColumn(
        template_code='<a href="/plugins/nautobot-device-lifecycle-mgmt/hardware-notice-device-report/'
        '?&device_type={{ record.device__device_type__model }}">{{ record.total }}</a>'
    )
    valid = tables.TemplateColumn(
        template_code='<a href="/plugins/nautobot-device-lifecycle-mgmt/hardware-notice-device-report/'
        '?&device_type={{ record.device__device_type__model }}&supported=True">{{ record.valid }}</a>',
        verbose_name="Supported",
    )
    invalid = tables.TemplateColumn(
        template_code='<a href="/plugins/nautobot-device-lifecycle-mgmt/hardware-notice-device-report/'
        '?&device_type={{ record.device__device_type__model }}&supported=False">{{ record.invalid }}</a>',
        verbose_name="Unsupported",
    )
    valid_percent = PercentageColumn(accessor="valid_percent", verbose_name="Support (%)")
    actions = tables.TemplateColumn(
        template_name="nautobot_device_lifecycle_mgmt/inc/validated_hw_notice_report_actions.html",
        orderable=False,
        verbose_name="Export Data",
    )

    class Meta(BaseTable.Meta):
        """Metaclass attributes of DeviceHardwareNoticeResultTable."""

        model = DeviceHardwareNoticeResult
        fields = ["name", "total", "valid", "invalid", "valid_percent"]
        default_columns = [
            "name",
            "total",
            "valid",
            "invalid",
            "valid_percent",
            "actions",
        ]


class DeviceHardwareNoticeResultListTable(BaseTable):  # pylint: disable=nb-sub-class-name
    """Table for a list of device to hardware notice report."""

    device = tables.Column(accessor="device", verbose_name="Device", linkify=True)
    hardware_notice = tables.Column(accessor="hardware_notice", verbose_name="Hardware Notice", linkify=True)
    valid = tables.Column(accessor="is_supported", verbose_name="Supported")
    last_run = tables.Column(accessor="last_run", verbose_name="Last Run")
    run_type = tables.Column(accessor="run_type", verbose_name="Run Type")

    class Meta(BaseTable.Meta):
        """Metaclass attributes of DeviceHardwareNoticeResultListTable."""

        model = DeviceSoftwareValidationResult
        fields = ["device", "hardware_notice", "valid", "last_run", "run_type"]
        default_columns = [
            "device",
            "hardware_notice",
            "valid",
            "last_run",
            "run_type",
        ]


class DeviceSoftwareValidationResultTable(BaseTable):
    """Table for device software validation report."""

    name = tables.TemplateColumn(
        template_code='<a href="/plugins/nautobot-device-lifecycle-mgmt/device-validated-software-result/'
        '?&device_type={{ record.device__device_type__model }}">{{ record.device__device_type__model }}</a>',
        orderable=True,
        accessor="device__device_type__model",
    )
    total = tables.TemplateColumn(
        template_code='<a href="/plugins/nautobot-device-lifecycle-mgmt/device-validated-software-result/'
        '?&device_type={{ record.device__device_type__model }}">{{ record.total }}</a>'
    )
    valid = tables.TemplateColumn(
        template_code='<a href="/plugins/nautobot-device-lifecycle-mgmt/device-validated-software-result/'
        '?&device_type={{ record.device__device_type__model }}&valid=True&exclude_sw_missing=True">{{ record.valid }}</a>'
    )
    invalid = tables.TemplateColumn(
        template_code='<a href="/plugins/nautobot-device-lifecycle-mgmt/device-validated-software-result/'
        '?&device_type={{ record.device__device_type__model }}&valid=False&exclude_sw_missing=True">{{ record.invalid }}</a>'
    )
    no_software = tables.TemplateColumn(
        template_code='<a href="/plugins/nautobot-device-lifecycle-mgmt/device-validated-software-result/'
        '?&device_type={{ record.device__device_type__model }}&sw_missing_only=True">{{ record.no_software }}</a>'
    )
    valid_percent = PercentageColumn(accessor="valid_percent", verbose_name="Compliance (%)")
    actions = tables.TemplateColumn(
        template_name="nautobot_device_lifecycle_mgmt/inc/validated_report_actions.html",
        orderable=False,
        verbose_name="Export Data",
    )

    class Meta(BaseTable.Meta):
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
            "actions",
        ]


class DeviceSoftwareValidationResultListTable(BaseTable):  # pylint: disable='nb-sub-class-name'
    """Table for a list of device to software validation report."""

    device = tables.Column(accessor="device", verbose_name="Device", linkify=True)
    software = tables.Column(accessor="software", verbose_name="Current Software", linkify=True)
    valid = tables.Column(accessor="is_validated", verbose_name="Valid")
    last_run = tables.Column(accessor="last_run", verbose_name="Last Run")
    run_type = tables.Column(accessor="run_type", verbose_name="Run Type")
    valid_software = tables.TemplateColumn(
        template_code="""{% for valid_software in record.valid_software.all %}
                    <a href="/plugins/nautobot-device-lifecycle-mgmt/validated-software/{{ valid_software.id }}"
                         %}">{{ valid_software }}
                    </a>
                    <br>
                    {% endfor %}""",
        verbose_name="Approved Software",
        orderable=True,
    )

    class Meta(BaseTable.Meta):
        """Metaclass attributes of DeviceSoftwareValidationResultTable."""

        model = DeviceSoftwareValidationResult
        fields = ["device", "software", "valid", "last_run", "run_type", "valid_software"]
        default_columns = [
            "device",
            "software",
            "valid",
            "last_run",
            "run_type",
            "valid_software",
        ]


class InventoryItemSoftwareValidationResultTable(BaseTable):
    """Table for InventoryItemSoftwareValidationResultTable."""

    part_id = tables.TemplateColumn(
        template_code="""{% if record.inventory_item__part_id  %}
        <a href="/plugins/nautobot-device-lifecycle-mgmt/inventory-item-validated-software-result/?&part_id={{ record.inventory_item__part_id }}">{{ record.inventory_item__part_id }}</a>
        {% else %}
        Please assign Part ID value to Inventory Item
        {% endif %}""",
        orderable=True,
        accessor="inventory_item__part_id",
    )
    item_name = tables.TemplateColumn(
        template_code="""<a href='/dcim/inventory-items/{{ record.inventory_item__pk }}'>{{ record.inventory_item__name }}</a>""",
        verbose_name="Item Name",
        accessor="inventory_item__name",
        orderable=True,
    )
    device = tables.TemplateColumn(
        template_code="""<a href='/dcim/devices/{{ record.inventory_item__device__pk }}'>
                        {{ record.inventory_item__device__name }}</a>""",
        orderable=True,
        accessor="inventory_item__device__pk",
        verbose_name="Device",
    )
    total = tables.TemplateColumn(
        template_code='<a href="/plugins/nautobot-device-lifecycle-mgmt/inventory-item-validated-software-result/'
        '?&part_id={{ record.inventory_item__part_id }}">{{ record.total }}</a>'
    )
    valid = tables.TemplateColumn(
        template_code='<a href="/plugins/nautobot-device-lifecycle-mgmt/inventory-item-validated-software-result/'
        '?&part_id=={{ record.inventory_item__part_id }}&valid=True&exclude_sw_missing=True">{{ record.valid }}</a>'
    )
    invalid = tables.TemplateColumn(
        template_code='<a href="/plugins/nautobot-device-lifecycle-mgmt/inventory-item-validated-software-result/'
        '?&part_id={{ record.inventory_item__part_id }}&valid=False&exclude_sw_missing=True">{{ record.invalid }}</a>'
    )
    no_software = tables.TemplateColumn(
        template_code='<a href="/plugins/nautobot-device-lifecycle-mgmt/inventory-item-validated-software-result/'
        '?&part_id={{ record.inventory_item__part_id }}&sw_missing_only=True">{{ record.no_software }}</a>'
    )
    valid_percent = PercentageColumn(accessor="valid_percent", verbose_name="Compliance (%)")
    actions = tables.TemplateColumn(
        template_name="nautobot_device_lifecycle_mgmt/inc/validated_report_actions.html",
        orderable=False,
        verbose_name="Export Data",
    )

    class Meta(BaseTable.Meta):
        """Metaclass attributes of InventoryItemSoftwareValidationResultTable."""

        model = InventoryItemSoftwareValidationResult
        fields = ["part_id", "item_name", "device", "total", "valid", "invalid", "no_software", "valid_percent"]
        default_columns = [
            "part_id",
            "item_name",
            "device",
            "total",
            "valid",
            "invalid",
            "no_software",
            "valid_percent",
            "actions",
        ]


class InventoryItemSoftwareValidationResultListTable(BaseTable):  # pylint: disable='nb-sub-class-name'
    """Table for a list of intenotry items to software validation report."""

    part_id = tables.Column(
        accessor="inventory_item__part_id",
        verbose_name="Part ID",
        default="Please assign Part ID value to Inventory Item",
    )
    item_name = tables.TemplateColumn(
        template_code="""<a href='/dcim/inventory-items/{{ record.inventory_item.pk }}'>
                        {{ record.inventory_item.name }}</a>""",
        verbose_name="Item Name",
        accessor="inventory_item__name",
        orderable=True,
    )
    device_name = tables.TemplateColumn(
        template_code="""<a href='/dcim/devices/{{ record.inventory_item.device.pk }}'>
                        {{ record.inventory_item.device.name }}</a>""",
        orderable=True,
        accessor="inventory_item__device__pk",
        verbose_name="Device",
    )
    software = tables.Column(accessor="software", verbose_name="Current Software", linkify=True)
    valid = tables.Column(accessor="is_validated", verbose_name="Valid")
    last_run = tables.Column(accessor="last_run", verbose_name="Last Run")
    run_type = tables.Column(accessor="run_type", verbose_name="Run Type")
    valid_software = tables.TemplateColumn(
        template_code="""{% for valid_software in record.valid_software.all %}
                    <a href="/plugins/nautobot-device-lifecycle-mgmt/validated-software/{{ valid_software.id }}"
                         %}">{{ valid_software }}
                    </a>
                    <br>
                    {% endfor %}""",
        verbose_name="Approved Software",
        orderable=True,
    )

    class Meta(BaseTable.Meta):
        """Metaclass attributes of InventoryItemSoftwareValidationResultTable."""

        model = InventoryItemSoftwareValidationResult
        fields = ["part_id", "item_name", "device_name", "software", "valid", "last_run", "run_type", "valid_software"]
        default_columns = [
            "part_id",
            "item_name",
            "device_name",
            "software",
            "valid",
            "last_run",
            "run_type",
            "valid_software",
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
    active = BooleanColumn(verbose_name="Active", orderable=False)
    expired = BooleanColumn(verbose_name="Expired", orderable=False)
    actions = ButtonsColumn(ContractLCM, buttons=("changelog", "edit", "delete"))
    tags = TagColumn(url_name="plugins:nautobot_device_lifecycle_mgmt:contractlcm_list")

    class Meta(BaseTable.Meta):
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
            "devices",
            "provider",
            "expired",
            "active",
            "tags",
            "actions",
        )

        default_columns = (
            "name",
            "start",
            "end",
            "cost",
            "support_level",
            "contract_type",
            "provider",
            "active",
            "tags",
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

    class Meta(BaseTable.Meta):
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


class CVELCMTable(StatusTableMixin, BaseTable):
    """Table for list view."""

    model = CVELCM
    pk = ToggleColumn()
    name = tables.LinkColumn(
        "plugins:nautobot_device_lifecycle_mgmt:cvelcm", text=lambda record: record, args=[A("pk")]
    )
    link = tables.TemplateColumn(
        template_code="""{% if record.link %}
                    <a href="{{ record.link }}" target="_blank" data-toggle="tooltip" data-placement="left" title="{{ record.link }}">
                        <span class="mdi mdi-open-in-new"></span>
                    </a>
                    {% else %}
                    —
                    {% endif %}""",
        verbose_name="Link",
    )
    tags = TagColumn()
    actions = ButtonsColumn(CVELCM, buttons=("changelog", "edit", "delete"))

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = CVELCM
        fields = (
            "pk",
            "name",
            "published_date",
            "last_modified_date",
            "link",
            "severity",
            "cvss",
            "cvss_v2",
            "cvss_v3",
            "affected_softwares",
            "status",
            "tags",
            "actions",
        )
        default_columns = (
            "pk",
            "name",
            "published_date",
            "last_modified_date",
            "link",
            "severity",
            "cvss",
            "cvss_v2",
            "cvss_v3",
            "status",
            "actions",
        )


class VulnerabilityLCMTable(StatusTableMixin, BaseTable):
    """Table for list view."""

    model = VulnerabilityLCM
    pk = ToggleColumn()
    name = tables.LinkColumn(
        "plugins:nautobot_device_lifecycle_mgmt:vulnerabilitylcm", text=lambda record: record, args=[A("pk")]
    )
    cve = tables.LinkColumn(verbose_name="CVE")
    software = tables.LinkColumn()
    device = tables.LinkColumn()
    inventory_item = tables.LinkColumn(verbose_name="Inventory Item")
    tags = TagColumn()
    actions = ButtonsColumn(VulnerabilityLCM, buttons=("changelog", "edit", "delete"))

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = VulnerabilityLCM
        fields = (
            "pk",
            "name",
            "cve",
            "software",
            "device",
            "inventory_item",
            "status",
            "tags",
            "actions",
        )
        default_columns = (
            "pk",
            "name",
            "cve",
            "software",
            "device",
            "inventory_item",
            "status",
            "actions",
        )

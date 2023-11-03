"""Tables implementation for the Lifecycle Management plugin."""

from django.urls import reverse
from django.utils.safestring import mark_safe
import django_tables2 as tables
from django_tables2.utils import A
from nautobot.utilities.tables import (
    BaseTable,
    ButtonsColumn,
    BooleanColumn,
    LinkedCountColumn,
    TagColumn,
    ToggleColumn,
)
from nautobot.extras.tables import StatusTableMixin
from nautobot_device_lifecycle_mgmt.models import (
    HardwareLCM,
    SoftwareLCM,
    ValidatedSoftwareLCM,
    ContractLCM,
    ProviderLCM,
    ContactLCM,
    CVELCM,
    VulnerabilityLCM,
    DeviceSoftwareValidationResult,
    InventoryItemSoftwareValidationResult,
    SoftwareImageLCM,
)


class M2MLinkedCountColumn(LinkedCountColumn):
    """Linked count column supporting many-to-many fields."""

    def render(self, record, value):
        """Render the resulting URL."""
        if value:
            url = reverse(self.viewname, kwargs=self.view_kwargs)
            if self.url_params:
                url += "?"
                for key, kval in self.url_params.items():
                    if isinstance(kval, tuple):
                        values = getattr(record, kval[0]).values(kval[1])
                        url += "&".join([f"{key}={val[key]}" for val in values])
                    else:
                        url += f"&{key}={getattr(record, kval)}"
            return mark_safe(f'<a href="{url}">{value}</a>')  # nosec
        return value


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
        default_columns = (
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


class SoftwareImageLCMTable(BaseTable):
    """Table for SoftwareImageLCM."""

    pk = ToggleColumn()
    name = tables.LinkColumn(
        "plugins:nautobot_device_lifecycle_mgmt:softwareimagelcm",
        text=lambda record: record,
        args=[A("pk")],
        orderable=False,
    )
    software = tables.LinkColumn(verbose_name="Software")
    device_type_count = M2MLinkedCountColumn(
        viewname="dcim:devicetype_list", url_params={"model": ("device_types", "model")}, verbose_name="Device Types"
    )
    object_tag_count = M2MLinkedCountColumn(
        viewname="extras:tag_list", url_params={"slug": ("object_tags", "slug")}, verbose_name="Object Tags"
    )
    default_image = BooleanColumn()
    actions = ButtonsColumn(SoftwareImageLCM, buttons=("edit", "delete"))
    download_url = tables.TemplateColumn(
        template_code="""{% if record.download_url %}
                    <a href="{{ record.download_url }}" target="_blank" data-toggle="tooltip" data-placement="left" title="{{ record.download_url }}">
                        <span class="mdi mdi-open-in-new"></span>
                    </a>{% else %} — {% endif %}""",
        verbose_name="Download URL",
    )

    class Meta(BaseTable.Meta):  # pylint: disable=too-few-public-methods
        """Meta attributes."""

        model = SoftwareImageLCM
        fields = (
            "pk",
            "name",
            "software",
            "device_type_count",
            "object_tag_count",
            "default_image",
            "download_url",
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
            "actions",
        ]


class DeviceSoftwareValidationResultListTable(BaseTable):
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

    class Meta(BaseTable.Meta):  # pylint: disable=too-few-public-methods
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

    class Meta(BaseTable.Meta):  # pylint: disable=too-few-public-methods
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


class InventoryItemSoftwareValidationResultListTable(BaseTable):
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

    class Meta(BaseTable.Meta):  # pylint: disable=too-few-public-methods
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
    actions = ButtonsColumn(ContractLCM, buttons=("changelog", "edit", "delete"))

    class Meta(BaseTable.Meta):  # pylint: disable=too-few-public-methods
        """Meta attributes."""

        model = ContractLCM
        fields = (
            "pk",
            "name",
            "number",
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

    class Meta(BaseTable.Meta):  # pylint: disable=too-few-public-methods
        """Meta attributes."""

        model = CVELCM
        fields = (
            "pk",
            "name",
            "published_date",
            "link",
            "severity",
            "cvss",
            "cvss_v2",
            "cvss_v3",
            "status",
            "tags",
            "actions",
        )
        default_columns = (
            "pk",
            "name",
            "published_date",
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

    class Meta(BaseTable.Meta):  # pylint: disable=too-few-public-methods
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

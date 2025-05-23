"""Extended core templates for the Lifecycle Management app."""

from abc import ABCMeta

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.urls import reverse
from django.utils.html import format_html
from nautobot.apps.ui import TemplateExtension

from nautobot_device_lifecycle_mgmt.models import ContractLCM, HardwareLCM, ValidatedSoftwareLCM
from nautobot_device_lifecycle_mgmt.software import DeviceSoftware, InventoryItemSoftware
from nautobot_device_lifecycle_mgmt.tables import ContractLCMTable, ValidatedSoftwareLCMTable


class DeviceTypeHWLCM(TemplateExtension, metaclass=ABCMeta):
    """Class to add table for HardwareLCM related to device type."""

    model = "dcim.devicetype"

    def right_page(self):
        """Display table on right side of page."""
        devtype_obj = self.context["object"]

        return self.render(
            "nautobot_device_lifecycle_mgmt/inc/general_notice.html",
            extra_context={"hw_notices": HardwareLCM.objects.filter(device_type=devtype_obj.pk)},
        )


class DeviceTypeValidatedSoftwareLCM(
    TemplateExtension,
):  # pylint: disable=abstract-method
    """Class to add table for ValidatedSoftwareLCM related to device type."""

    model = "dcim.devicetype"

    def __init__(self, context):
        """Init setting up the DeviceTypeValidatedSoftwareLCM object."""
        super().__init__(context)
        self.device_type_validated_software = ValidatedSoftwareLCM.objects.get_for_object(self.context["object"])
        self.validated_software_table = ValidatedSoftwareLCMTable(
            list(self.device_type_validated_software),
            orderable=False,
            exclude=(
                "software",
                "start",
                "actions",
            ),
        )

    def right_page(self):
        """Display table on right side of page."""
        extra_context = {
            "validsoft_table": self.validated_software_table,
        }

        return self.render(
            "nautobot_device_lifecycle_mgmt/inc/validatedsoftware_info.html",
            extra_context=extra_context,
        )


class DeviceHWLCM(TemplateExtension, metaclass=ABCMeta):
    """Class to add table for DeviceHWLCM related to device type."""

    model = "dcim.device"

    def right_page(self):
        """Display table on right side of page."""
        dev_obj = self.context["object"]
        part_ids = dev_obj.inventory_items.exclude(part_id=None).values_list("part_id", flat=True)
        # order HardwareLCM queryset by field configured in expired_field setting first
        order_fields = ["end_of_security_patches", "end_of_sw_releases", "end_of_support", "end_of_sale"]
        expired_field = settings.PLUGINS_CONFIG["nautobot_device_lifecycle_mgmt"].get("expired_field", "end_of_support")
        order_fields.remove(expired_field)
        order_fields.insert(0, expired_field)

        hw_notices = HardwareLCM.objects.filter(
            Q(device_type=dev_obj.device_type) | Q(inventory_item__in=part_ids)
        ).order_by("device_type", *order_fields)

        return self.render(
            "nautobot_device_lifecycle_mgmt/inc/device_notice.html",
            extra_context={
                "hw_notices": hw_notices,
            },
        )


class InventoryItemHWLCM(TemplateExtension, metaclass=ABCMeta):
    """Class to add table for InventoryItemHWLCM related to inventory items."""

    model = "dcim.inventoryitem"

    def right_page(self):
        """Display table on right side of page."""
        inv_item_obj = self.context["object"]

        return self.render(
            "nautobot_device_lifecycle_mgmt/inc/general_notice.html",
            extra_context={"hw_notices": HardwareLCM.objects.filter(inventory_item=inv_item_obj.part_id)},
        )


class DeviceValidatedSoftwareLCM(
    TemplateExtension,
):  # pylint: disable=abstract-method
    """Class to add table for ValidatedSoftwareLCM related to device."""

    model = "dcim.device"

    def __init__(self, context):
        """Init setting up the DeviceValidatedSoftwareLCM object."""
        super().__init__(context)
        self.device_software = DeviceSoftware(item_obj=self.context["object"])

    def right_page(self):
        """Display table on right side of page."""
        extra_context = {
            "validsoft_table": self.device_software.get_validated_software_table(),
            "obj_soft_valid": self.device_software.validate_software(),
        }

        return self.render(
            "nautobot_device_lifecycle_mgmt/inc/validatedsoftware_info.html",
            extra_context=extra_context,
        )


class InventoryItemValidatedSoftwareLCM(
    TemplateExtension,
):  # pylint: disable=abstract-method
    """Class to add table for ValidatedSoftwareLCM related to inventory item."""

    model = "dcim.inventoryitem"

    def __init__(self, context):
        """Init setting up the InventoryItemValidatedSoftwareLCM object."""
        super().__init__(context)
        self.inventory_item_software = InventoryItemSoftware(item_obj=self.context["object"])

    def right_page(self):
        """Display table on right side of page."""
        extra_context = {
            "validsoft_table": self.inventory_item_software.get_validated_software_table(),
            "obj_soft_valid": self.inventory_item_software.validate_software(),
        }

        return self.render(
            "nautobot_device_lifecycle_mgmt/inc/validatedsoftware_info.html",
            extra_context=extra_context,
        )


class DeviceContractLCM(
    TemplateExtension,
):  # pylint: disable=abstract-method
    """Class to add table for ContractLCM related to device."""

    model = "dcim.device"

    def __init__(self, context):
        """Init setting up the ContractLCM object."""
        super().__init__(context)
        self.device_contracts = (
            ContractLCM.objects.get_for_object(self.context["object"]).order_by("name").order_by("-end")[:5]
        )
        self.device_contracts_table = ContractLCMTable(
            list(self.device_contracts),
            orderable=False,
            exclude=(
                "actions",
                "cost",
                "contract_type",
                "devices",
                "provider",
                "support_level",
                "cr_contractlcm_to_inventoryitem_src",
            ),
        )

    def right_page(self):
        """Display table on right side of page."""
        extra_context = {
            "contracts_table": self.device_contracts_table,
        }
        return self.render(
            "nautobot_device_lifecycle_mgmt/inc/contract_info.html",
            extra_context=extra_context,
        )


class SoftwareVersionRelatedCVELCMTab(TemplateExtension):  # pylint: disable=abstract-method
    """Class to add new tab with related CVE table to the SoftwareVersion display."""

    model = "dcim.softwareversion"

    @property
    def software(self):
        """Set software as the referenced variable."""
        return self.context["object"]

    def detail_tabs(self):
        """Create new detail tab on SoftwareVersion for Related CVEs."""
        try:
            return [
                {
                    "title": "Related CVEs",
                    "url": reverse(
                        "plugins:nautobot_device_lifecycle_mgmt:softwareversion_related_cves",
                        kwargs={"pk": self.software.pk},
                    ),
                },
            ]
        except ObjectDoesNotExist:
            return []


# pylint: disable=abstract-method
class ValidatedSoftwareLCMTab(TemplateExtension):
    """Template extension to add tabs to the Validated Software detail view."""

    model = "nautobot_device_lifecycle_mgmt.validatedsoftwarelcm"

    def detail_tabs(self):
        """Add tabs to the Validated Software detail view."""
        device_count = self.context["object"].devices.count()
        device_type_count = self.context["object"].device_types.count()
        device_role_count = self.context["object"].device_roles.count()
        inventory_item_count = self.context["object"].inventory_items.count()
        object_tags_count = self.context["object"].object_tags.count()
        return [
            {
                "title": (
                    "Devices"
                    if not device_count
                    else format_html(
                        'Devices <span class="badge">{count}</span>',
                        count=device_count,
                    )
                ),
                "url": reverse(
                    "plugins:nautobot_device_lifecycle_mgmt:validatedsoftware_devices_tab",
                    args=[self.context["object"].pk],
                ),
            },
            {
                "title": (
                    "Device Types"
                    if not device_type_count
                    else format_html(
                        'Device Types <span class="badge">{count}</span>',
                        count=device_type_count,
                    )
                ),
                "url": reverse(
                    "plugins:nautobot_device_lifecycle_mgmt:validatedsoftware_device_types_tab",
                    args=[self.context["object"].pk],
                ),
            },
            {
                "title": (
                    "Device Roles"
                    if not device_role_count
                    else format_html(
                        'Device Roles <span class="badge">{count}</span>',
                        count=device_role_count,
                    )
                ),
                "url": reverse(
                    "plugins:nautobot_device_lifecycle_mgmt:validatedsoftware_device_roles_tab",
                    args=[self.context["object"].pk],
                ),
            },
            {
                "title": (
                    "Inventory Items"
                    if not inventory_item_count
                    else format_html(
                        'Inventory Items <span class="badge">{count}</span>',
                        count=inventory_item_count,
                    )
                ),
                "url": reverse(
                    "plugins:nautobot_device_lifecycle_mgmt:validatedsoftware_inventory_items_tab",
                    args=[self.context["object"].pk],
                ),
            },
            {
                "title": (
                    "Object Tags"
                    if not object_tags_count
                    else format_html(
                        'Object Tags <span class="badge">{count}</span>',
                        count=object_tags_count,
                    )
                ),
                "url": reverse(
                    "plugins:nautobot_device_lifecycle_mgmt:validatedsoftware_object_tags_tab",
                    args=[self.context["object"].pk],
                ),
            },
        ]


template_extensions = [
    DeviceContractLCM,
    DeviceTypeHWLCM,
    DeviceTypeValidatedSoftwareLCM,
    DeviceHWLCM,
    InventoryItemHWLCM,
    DeviceValidatedSoftwareLCM,
    InventoryItemValidatedSoftwareLCM,
    SoftwareVersionRelatedCVELCMTab,
    ValidatedSoftwareLCMTab,
]

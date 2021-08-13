"""Extended core templates for the LifeCycle Management plugin."""
from abc import ABCMeta
from django.db.models import Q
from nautobot.extras.plugins import PluginTemplateExtension
from nautobot.dcim.models import InventoryItem
from .models import HardwareLCM


class DeviceTypeHWLCMNotice(PluginTemplateExtension, metaclass=ABCMeta):
    """Class to add table for HardwareLCMNotice related to device type."""

    model = "dcim.devicetype"

    def right_page(self):
        """Display table on right side of page."""
        devtype_obj = self.context["object"]

        return self.render(
            "nautobot_device_lifecycle_mgmt/inc/general_notice.html",
            extra_context={"hw_notices": HardwareLCM.objects.filter(device_type=devtype_obj.pk)},
        )


class DeviceHWLCMNotice(PluginTemplateExtension, metaclass=ABCMeta):
    """Class to add table for HardwareLCMNotice related to device type."""

    model = "dcim.device"

    def right_page(self):
        """Display table on right side of page."""
        dev_obj = self.context["object"]

        return self.render(
            "nautobot_device_lifecycle_mgmt/inc/device_notice.html",
            extra_context={
                "hw_notices": HardwareLCM.objects.filter(
                    Q(device_type=dev_obj.device_type)
                    | Q(
                        inventory_item__in=[
                            i.part_id for i in InventoryItem.objects.filter(device__pk=dev_obj.pk) if i.part_id
                        ]
                    )
                )
            },
        )


class InventoryItemHWLCMNotice(PluginTemplateExtension, metaclass=ABCMeta):
    """Class to add table for HardwareLCMNotice related to inventory items."""

    model = "dcim.inventoryitem"

    def right_page(self):
        """Display table on right side of page."""
        inv_item_obj = self.context["object"]

        return self.render(
            "nautobot_device_lifecycle_mgmt/inc/general_notice.html",
            extra_context={"hw_notices": HardwareLCM.objects.filter(inventory_item=inv_item_obj.part_id)},
        )


template_extensions = [DeviceTypeHWLCMNotice, DeviceHWLCMNotice, InventoryItemHWLCMNotice]

"""Extended core templates for nautobot_plugin_device_lifecycle_mgmt."""
from abc import ABCMeta

from nautobot.extras.plugins import PluginTemplateExtension
from .models import HardwareLCM


class DeviceTypeHWLCMNotice(PluginTemplateExtension, metaclass=ABCMeta):
    """Class to add table for HardwareLCMNotice related to device type."""

    model = "dcim.devicetype"

    def right_page(self):
        """Display table on right side of page."""
        devtype_obj = self.context["object"]
        try:
            notice = HardwareLCM.objects.get(device_type=devtype_obj.pk)
        except HardwareLCM.DoesNotExist:
            notice = None

        return self.render(
            "nautobot_plugin_device_lifecycle_mgmt/inc/general_notice.html", extra_context={"notice": notice}
        )


class DeviceHWLCMNotice(PluginTemplateExtension, metaclass=ABCMeta):
    """Class to add table for HardwareLCMNotice related to device type."""

    model = "dcim.device"

    def right_page(self):
        """Display table on right side of page."""
        dev_obj = self.context["object"]
        try:
            notice = HardwareLCM.objects.get(device_type=dev_obj.device_type)
        except HardwareLCM.DoesNotExist:
            notice = None

        return self.render(
            "nautobot_plugin_device_lifecycle_mgmt/inc/general_notice.html", extra_context={"notice": notice}
        )


template_extensions = [DeviceTypeHWLCMNotice, DeviceHWLCMNotice]

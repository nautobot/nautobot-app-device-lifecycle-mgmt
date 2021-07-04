"""Extended core templates for eox_notices."""

from nautobot.extras.plugins import PluginTemplateExtension
from .models import EoxNotice


class DeviceEoxNotice(PluginTemplateExtension):
    """Class to add table for EoxNotice related to device."""

    model = "dcim.device"

    def right_page(self):
        """Display table on right side of page."""
        dev_obj = self.context["object"]
        try:
            notice = EoxNotice.objects.get(device_type=dev_obj.device_type.pk)
        except EoxNotice.DoesNotExist:
            notice = None

        return self.render("eox_notices/inc/general_notice.html", extra_context={"notice": notice})


class DeviceTypeEoxNotice(PluginTemplateExtension):
    """Class to add table for EoxNotice related to device type."""

    model = "dcim.devicetype"

    def right_page(self):
        """Display table on right side of page."""
        devtype_obj = self.context["object"]
        try:
            notice = EoxNotice.objects.get(device_type=devtype_obj.pk)
        except EoxNotice.DoesNotExist:
            notice = None

        return self.render("eox_notices/inc/general_notice.html", extra_context={"notice": notice})


template_extensions = [DeviceEoxNotice, DeviceTypeEoxNotice]

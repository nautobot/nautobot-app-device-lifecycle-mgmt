"""Extended core templates for eox_notices."""

from datetime import date

from nautobot.extras.plugins import PluginTemplateExtension
from .models import EoxNotice


def past_due(end_of):
    """Determine if EoxNotice is past due to change HTML to danger."""
    today = date.today()
    if end_of is None:
        return False
    if today >= end_of:
        return True


class DeviceEoxNotice(PluginTemplateExtension):
    """Class to add table for EoxNotice related to device."""

    model = "dcim.device"

    def right_page(self):
        """Display table on right side of page."""
        expired = False
        dev_obj = self.context["object"]
        try:
            notice = EoxNotice.objects.get(device_type=dev_obj.device_type.pk)
        except EoxNotice.DoesNotExist:
            notice = None

        # Determine if any of the fields are expired to turn the EoX Notice table in the view red if so.
        if notice is not None:
            if list(
                filter(
                    past_due,
                    [
                        notice.end_of_sale,
                        notice.end_of_support,
                        notice.end_of_sw_releases,
                        notice.end_of_security_patches,
                    ],
                )
            ):
                expired = True

        return self.render("eox_notices/inc/general_notice.html", extra_context={"notice": notice, "expired": expired})


class DeviceTypeEoxNotice(PluginTemplateExtension):
    """Class to add table for EoxNotice related to device type."""

    model = "dcim.devicetype"

    def right_page(self):
        """Display table on right side of page."""
        expired = False
        devtype_obj = self.context["object"]
        try:
            notice = EoxNotice.objects.get(device_type=devtype_obj.pk)
        except EoxNotice.DoesNotExist:
            notice = None

        # Determine if any of the fields are expired to turn the EoX Notice table in the view red if so.
        if notice is not None:
            if list(
                filter(
                    past_due,
                    [
                        notice.end_of_sale,
                        notice.end_of_support,
                        notice.end_of_sw_releases,
                        notice.end_of_security_patches,
                    ],
                )
            ):
                expired = True

        return self.render("eox_notices/inc/general_notice.html", extra_context={"notice": notice, "expired": expired})


template_extensions = [DeviceEoxNotice, DeviceTypeEoxNotice]

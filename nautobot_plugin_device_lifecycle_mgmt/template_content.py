"""Extended core templates for nautobot_plugin_device_lifecycle_mgmt."""

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from nautobot.dcim.models import Device
from nautobot.extras.models import RelationshipAssociation
from nautobot.extras.plugins import PluginTemplateExtension
from .models import EoxNotice, SoftwareLCM, ValidatedSoftwareLCM
from .tables import ValidatedSoftwareLCMTable


class DeviceEoxNotice(PluginTemplateExtension):  # pylint: disable=abstract-method
    """Class to add table for EoxNotice related to device."""

    model = "dcim.device"

    def right_page(self):
        """Display table on right side of page."""
        dev_obj = self.context["object"]
        try:
            notice = EoxNotice.objects.get(device_type=dev_obj.device_type.pk)
        except EoxNotice.DoesNotExist:
            notice = None

        return self.render(
            "nautobot_plugin_device_lifecycle_mgmt/inc/general_notice.html", extra_context={"notice": notice}
        )


class DeviceTypeEoxNotice(PluginTemplateExtension):  # pylint: disable=abstract-method
    """Class to add table for EoxNotice related to device type."""

    model = "dcim.devicetype"

    def right_page(self):
        """Display table on right side of page."""
        devtype_obj = self.context["object"]
        try:
            notice = EoxNotice.objects.get(device_type=devtype_obj.pk)
        except EoxNotice.DoesNotExist:
            notice = None

        return self.render(
            "nautobot_plugin_device_lifecycle_mgmt/inc/general_notice.html", extra_context={"notice": notice}
        )


class DeviceSoftwareLCMAndValidatedSoftwareLCM(PluginTemplateExtension):  # pylint: disable=abstract-method
    """Class to add table for ValidatedSoftwareLCM related to device."""

    model = "dcim.device"

    def right_page(self):
        """Display table on right side of page."""
        dev_obj = self.context["object"]
        validsoft_list = ValidatedSoftwareLCM.objects.filter(
            Q(
                assigned_to_content_type=ContentType.objects.get(app_label="dcim", model="device"),
                assigned_to_object_id=dev_obj.pk,
            )
            | Q(
                assigned_to_content_type=ContentType.objects.get(app_label="dcim", model="devicetype"),
                assigned_to_object_id=dev_obj.device_type.pk,
            )
        )
        if validsoft_list.exists():
            validsoft_table = ValidatedSoftwareLCMTable(
                list(validsoft_list),
                orderable=False,
                exclude=(
                    "name",
                    "actions",
                ),
            )
        else:
            validsoft_list = None
            validsoft_table = None

        try:
            device_soft_relation = RelationshipAssociation.objects.get(
                relationship__slug="device_soft",
                destination_type=ContentType.objects.get_for_model(Device),
                destination_id=dev_obj.pk,
            )
            device_soft = SoftwareLCM.objects.get(id=device_soft_relation.source_id)
        except (RelationshipAssociation.DoesNotExist, SoftwareLCM.DoesNotExist):
            device_soft = None

        if validsoft_list and device_soft:
            is_device_soft_valid = validsoft_list.filter(software_id=device_soft).exists()
        else:
            is_device_soft_valid = False

        extra_context = {
            "validsoft_list": validsoft_list,
            "validsoft_table": validsoft_table,
            "device_soft": device_soft,
            "is_device_soft_valid": is_device_soft_valid,
        }

        return self.render(
            "nautobot_plugin_device_lifecycle_mgmt/inc/validatedsoftware_info.html",
            extra_context=extra_context,
        )


template_extensions = [DeviceEoxNotice, DeviceTypeEoxNotice, DeviceSoftwareLCMAndValidatedSoftwareLCM]

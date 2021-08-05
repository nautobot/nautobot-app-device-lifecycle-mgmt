"""Views for nautobot_plugin_device_lifecycle_mgmt."""

from nautobot.core.views import generic
from nautobot.dcim.models import Device
from nautobot_plugin_device_lifecycle_mgmt.models import HardwareLCM
from nautobot_plugin_device_lifecycle_mgmt.tables import HardwareLCMNoticesTable
from nautobot_plugin_device_lifecycle_mgmt.forms import (
    HardwareLCMNoticeForm,
    HardwareLCMNoticeBulkEditForm,
    HardwareLCMNoticeFilterForm,
    HardwareLCMNoticeCSVForm,
)
from nautobot_plugin_device_lifecycle_mgmt.filters import HardwareLCMNoticeFilter


class HardwareLCMNoticesListView(generic.ObjectListView):
    """List view."""

    queryset = HardwareLCM.objects.prefetch_related("device_type")
    filterset = HardwareLCMNoticeFilter
    filterset_form = HardwareLCMNoticeFilterForm
    table = HardwareLCMNoticesTable


class HardwareLCMNoticeView(generic.ObjectView):
    """Detail view."""

    queryset = HardwareLCM.objects.prefetch_related("device_type")

    def get_extra_context(self, request, instance):
        """Return any additional context data for the template.

        request: The current request
        instance: The object being viewed
        """
        if instance.device_type:
            return {"devices": Device.objects.restrict(request.user, "view").filter(device_type=instance.device_type)}
        if instance.inventory_item:
            return {
                "devices": Device.objects.restrict(request.user, "view").filter(
                    inventoryitems__part_id=instance.inventory_item
                )
            }
        return {"devices": []}


class HardwareLCMNoticeCreateView(generic.ObjectEditView):
    """Create view."""

    model = HardwareLCM
    queryset = HardwareLCM.objects.prefetch_related("device_type")
    model_form = HardwareLCMNoticeForm
    default_return_url = "plugins:nautobot_plugin_device_lifecycle_mgmt:hardwarelcm_list"


class HardwareLCMNoticeDeleteView(generic.ObjectDeleteView):
    """Delete view."""

    model = HardwareLCM
    queryset = HardwareLCM.objects.prefetch_related("device_type")
    default_return_url = "plugins:nautobot_plugin_device_lifecycle_mgmt:hardwarelcm_list"


class HardwareLCMNoticeEditView(generic.ObjectEditView):
    """Edit view."""

    model = HardwareLCM
    queryset = HardwareLCM.objects.prefetch_related("device_type")
    model_form = HardwareLCMNoticeForm
    default_return_url = "plugins:nautobot_plugin_device_lifecycle_mgmt:hardwarelcm"


class HardwareLCMNoticeBulkImportView(generic.BulkImportView):
    """View for bulk import of hardware lcm."""

    queryset = HardwareLCM.objects.prefetch_related("device_type")
    model_form = HardwareLCMNoticeCSVForm
    table = HardwareLCMNoticesTable
    default_return_url = "plugins:nautobot_plugin_device_lifecycle_mgmt:hardwarelcm_list"


class HardwareLCMNoticeBulkDeleteView(generic.BulkDeleteView):
    """View for deleting one or more HardwareLCM records."""

    queryset = HardwareLCM.objects.prefetch_related("device_type")
    table = HardwareLCMNoticesTable
    bulk_delete_url = "plugins:nautobot_plugin_device_lifecycle_mgmt.hardwarelcm_bulk_delete"
    default_return_url = "plugins:nautobot_plugin_device_lifecycle_mgmt:hardwarelcm_list"


class HardwareLCMNoticeBulkEditView(generic.BulkEditView):
    """View for editing one or more HardwareLCM records."""

    queryset = HardwareLCM.objects.prefetch_related("device_type")
    filterset = HardwareLCMNoticeFilter
    table = HardwareLCMNoticesTable
    form = HardwareLCMNoticeBulkEditForm
    bulk_edit_url = "plugins:nautobot_plugin_device_lifecycle_mgmt.hardwarelcm_bulk_edit"

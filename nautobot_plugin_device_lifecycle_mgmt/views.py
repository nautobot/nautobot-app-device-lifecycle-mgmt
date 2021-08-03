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
from nautobot_plugin_device_lifecycle_mgmt.const import Permissions, URL


class HardwareLCMNoticesListView(generic.ObjectListView):
    """List view."""

    queryset = HardwareLCM.objects.prefetch_related("device_type")
    filterset = HardwareLCMNoticeFilter
    filterset_form = HardwareLCMNoticeFilterForm
    table = HardwareLCMNoticesTable

    def get_required_permission(self):
        """Return required view permission."""
        return Permissions.HardwareLCM.Read


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
            return {"devices": [instance.inventory_item.device]}
        return {"devices": []}

    def get_required_permission(self):
        """Return required view permission."""
        return Permissions.HardwareLCM.Read


class HardwareLCMNoticeCreateView(generic.ObjectEditView):
    """Create view."""

    model = HardwareLCM
    queryset = HardwareLCM.objects.prefetch_related("device_type")
    model_form = HardwareLCMNoticeForm
    default_return_url = URL.HardwareLCM.List

    def get_required_permission(self):
        """Return required add permission."""
        return Permissions.HardwareLCM.Create


class HardwareLCMNoticeDeleteView(generic.ObjectDeleteView):
    """Delete view."""

    model = HardwareLCM
    queryset = HardwareLCM.objects.prefetch_related("device_type")
    default_return_url = URL.HardwareLCM.List

    def get_required_permission(self):
        """Return required delete permission."""
        return Permissions.HardwareLCM.Delete


class HardwareLCMNoticeEditView(generic.ObjectEditView):
    """Edit view."""

    model = HardwareLCM
    queryset = HardwareLCM.objects.prefetch_related("device_type")
    model_form = HardwareLCMNoticeForm
    default_return_url = URL.HardwareLCM.View

    def get_required_permission(self):
        """Return required change permission."""
        return Permissions.HardwareLCM.Update


class HardwareLCMNoticeBulkImportView(generic.BulkImportView):
    """View for bulk import of hardware lcm."""

    queryset = HardwareLCM.objects.prefetch_related("device_type")
    model_form = HardwareLCMNoticeCSVForm
    table = HardwareLCMNoticesTable
    default_return_url = URL.HardwareLCM.List


class HardwareLCMNoticeBulkDeleteView(generic.BulkDeleteView):
    """View for deleting one or more HardwareLCM records."""

    queryset = HardwareLCM.objects.prefetch_related("device_type")
    table = HardwareLCMNoticesTable
    bulk_delete_url = URL.HardwareLCM.BulkDelete
    default_return_url = URL.HardwareLCM.List

    def get_required_permission(self):
        """Return required delete permission."""
        return Permissions.HardwareLCM.Delete


class HardwareLCMNoticeBulkEditView(generic.BulkEditView):
    """View for editing one or more HardwareLCM records."""

    queryset = HardwareLCM.objects.prefetch_related("device_type")
    filterset = HardwareLCMNoticeFilter
    table = HardwareLCMNoticesTable
    form = HardwareLCMNoticeBulkEditForm
    bulk_edit_url = URL.HardwareLCM.BulkEdit

    def get_required_permission(self):
        """Return required change permission."""
        return Permissions.HardwareLCM.Update

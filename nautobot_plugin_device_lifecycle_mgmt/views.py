"""Views for nautobot_plugin_device_lifecycle_mgmt."""

from nautobot.core.views import generic
from .models import EoxNotice
from .tables import EoxNoticesTable
from .forms import EoxNoticeForm, EoxNoticeBulkEditForm, EoxNoticeFilterForm, EoxNoticeCSVForm
from .filters import EoxNoticeFilter


class EoxNoticesListView(generic.ObjectListView):
    """List view."""

    queryset = EoxNotice.objects.prefetch_related("devices", "device_type")
    filterset = EoxNoticeFilter
    filterset_form = EoxNoticeFilterForm
    table = EoxNoticesTable

    def get_required_permission(self):
        """Return required view permission."""
        return "nautobot_plugin_device_lifecycle_mgmt.view_devicelifecycle"


class EoxNoticeView(generic.ObjectView):
    """Detail view."""

    queryset = EoxNotice.objects.prefetch_related("devices", "device_type")

    def get_required_permission(self):
        """Return required view permission."""
        return "nautobot_plugin_device_lifecycle_mgmt.view_devicelifecycle"


class EoxNoticeCreateView(generic.ObjectEditView):
    """Create view."""

    model = EoxNotice
    queryset = EoxNotice.objects.prefetch_related("devices", "device_type")
    model_form = EoxNoticeForm
    default_return_url = "plugins:nautobot_plugin_device_lifecycle_mgmt:devicelifecycle_list"

    def get_required_permission(self):
        """Return required add permission."""
        return "nautobot_plugin_device_lifecycle_mgmt.add_devicelifecycle"


class EoxNoticeDeleteView(generic.ObjectDeleteView):
    """Delete view."""

    model = EoxNotice
    queryset = EoxNotice.objects.prefetch_related("devices", "device_type")
    default_return_url = "plugins:nautobot_plugin_device_lifecycle_mgmt:devicelifecycle_list"

    def get_required_permission(self):
        """Return required delete permission."""
        return "nautobot_plugin_device_lifecycle_mgmt.delete_devicelifecycle"


class EoxNoticeEditView(generic.ObjectEditView):
    """Edit view."""

    model = EoxNotice
    queryset = EoxNotice.objects.prefetch_related("devices", "device_type")
    model_form = EoxNoticeForm
    default_return_url = "plugins:nautobot_plugin_device_lifecycle_mgmt:devicelifecycle"

    def get_required_permission(self):
        """Return required change permission."""
        return "nautobot_plugin_device_lifecycle_mgmt.change_devicelifecycle"


class EoxNoticeBulkImportView(generic.BulkImportView):
    """View for bulk import of eox notices."""

    queryset = EoxNotice.objects.prefetch_related("devices", "device_type")
    model_form = EoxNoticeCSVForm
    table = EoxNoticesTable
    default_return_url = "plugins:nautobot_plugin_device_lifecycle_mgmt:devicelifecycle_list"


class EoxNoticeBulkDeleteView(generic.BulkDeleteView):
    """View for deleting one or more EoxNotice records."""

    queryset = EoxNotice.objects.prefetch_related("devices", "device_type")
    table = EoxNoticesTable
    bulk_delete_url = "plugins:nautobot_plugin_device_lifecycle_mgmt.devicelifecycle_bulk_delete"
    default_return_url = "plugins:nautobot_plugin_device_lifecycle_mgmt:devicelifecycle_list"

    def get_required_permission(self):
        """Return required delete permission."""
        return "nautobot_plugin_device_lifecycle_mgmt.delete_devicelifecycle"


class EoxNoticeBulkEditView(generic.BulkEditView):
    """View for editing one or more EoxNotice records."""

    queryset = EoxNotice.objects.prefetch_related("devices", "device_type")
    filterset = EoxNoticeFilter
    table = EoxNoticesTable
    form = EoxNoticeBulkEditForm
    bulk_edit_url = "plugins:nautobot_plugin_device_lifecycle_mgmt.devicelifecycle_bulk_edit"

    def get_required_permission(self):
        """Return required change permission."""
        return "nautobot_plugin_device_lifecycle_mgmt.change_devicelifecycle"

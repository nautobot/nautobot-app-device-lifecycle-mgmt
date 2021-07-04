"""Views for eox_notices."""

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
        return "eox_notices.view_eoxnotice"


class EoxNoticeView(generic.ObjectView):
    """Detail view."""

    queryset = EoxNotice.objects.prefetch_related("devices", "device_type")

    def get_required_permission(self):
        """Return required view permission."""
        return "eox_notices.view_eoxnotice"


class EoxNoticeCreateView(generic.ObjectEditView):
    """Create view."""

    model = EoxNotice
    queryset = EoxNotice.objects.prefetch_related("devices", "device_type")
    model_form = EoxNoticeForm
    default_return_url = "plugins:eox_notices:eoxnotice_list"

    def get_required_permission(self):
        """Return required add permission."""
        return "eox_notices.add_eoxnotice"


class EoxNoticeDeleteView(generic.ObjectDeleteView):
    """Delete view."""

    model = EoxNotice
    queryset = EoxNotice.objects.prefetch_related("devices", "device_type")
    default_return_url = "plugins:eox_notices:eoxnotice_list"

    def get_required_permission(self):
        """Return required delete permission."""
        return "eox_notices.delete_eoxnotice"


class EoxNoticeEditView(generic.ObjectEditView):
    """Edit view."""

    model = EoxNotice
    queryset = EoxNotice.objects.prefetch_related("devices", "device_type")
    model_form = EoxNoticeForm
    default_return_url = "plugins:eox_notices:eoxnotice"

    def get_required_permission(self):
        """Return required change permission."""
        return "eox_notices.change_eoxnotice"


class EoxNoticeBulkImportView(generic.BulkImportView):
    """View for bulk import of eox notices."""

    queryset = EoxNotice.objects.prefetch_related("devices", "device_type")
    model_form = EoxNoticeCSVForm
    table = EoxNoticesTable
    default_return_url = "plugins:eox_notices:eoxnotice_list"


class EoxNoticeBulkDeleteView(generic.BulkDeleteView):
    """View for deleting one or more EoxNotice records."""

    queryset = EoxNotice.objects.prefetch_related("devices", "device_type")
    table = EoxNoticesTable
    bulk_delete_url = "plugins:eox_notices.eoxnotice_bulk_delete"
    default_return_url = "plugins:eox_notices:eoxnotice_list"

    def get_required_permission(self):
        """Return required delete permission."""
        return "eox_notices.delete_eoxnotice"


class EoxNoticeBulkEditView(generic.BulkEditView):
    """View for editing one or more EoxNotice records."""

    queryset = EoxNotice.objects.prefetch_related("devices", "device_type")
    filterset = EoxNoticeFilter
    table = EoxNoticesTable
    form = EoxNoticeBulkEditForm
    bulk_edit_url = "plugins:eox_notices.eoxnotice_bulk_edit"

    def get_required_permission(self):
        """Return required change permission."""
        return "eox_notices.change_eoxnotice"

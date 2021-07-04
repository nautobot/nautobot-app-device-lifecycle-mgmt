"""Views for eox_notices."""

from nautobot.core.views.generic import (
    BulkDeleteView,
    BulkEditView,
    ObjectDeleteView,
    ObjectEditView,
    ObjectListView,
    ObjectView,
)
from .models import EoxNotice
from .tables import EoxNoticesTable
from .forms import EoxNoticeForm, EoxNoticeBulkEditForm, EoxNoticeFilterForm
from .filters import EoxNoticeFilter


class EoxNoticesListView(ObjectListView):
    """List view."""

    queryset = EoxNotice.objects.prefetch_related("devices", "device_type")
    filterset = EoxNoticeFilter
    filterset_form = EoxNoticeFilterForm
    table = EoxNoticesTable
    action_buttons = ("add",)

    def get_required_permission(self):
        """Return required view permission."""
        return "eox_notices.view_eoxnotice"


class EoxNoticeView(ObjectView):
    """Detail view."""

    queryset = EoxNotice.objects.prefetch_related("devices", "device_type")

    def get_required_permission(self):
        """Return required view permission."""
        return "eox_notices.view_eoxnotice"


class EoxNoticeCreateView(ObjectEditView):
    """Create view."""

    model = EoxNotice
    queryset = EoxNotice.objects.prefetch_related("devices", "device_type")
    model_form = EoxNoticeForm
    default_return_url = "plugins:eox_notices:eoxnotice_list"

    def get_required_permission(self):
        """Return required add permission."""
        return "eox_notices.add_eoxnotice"


class EoxNoticeDeleteView(ObjectDeleteView):
    """Delete view."""

    model = EoxNotice
    queryset = EoxNotice.objects.prefetch_related("devices", "device_type")
    default_return_url = "plugins:eox_notices:eoxnotice_list"

    def get_required_permission(self):
        """Return required delete permission."""
        return "eox_notices.delete_eoxnotice"


class EoxNoticeEditView(ObjectEditView):
    """Edit view."""

    model = EoxNotice
    queryset = EoxNotice.objects.prefetch_related("devices", "device_type")
    model_form = EoxNoticeForm
    default_return_url = "plugins:eox_notices:eoxnotice"

    def get_required_permission(self):
        """Return required delete permission."""
        return "eox_notices.change_eoxnotice"


class EoxNoticeBulkDeleteView(BulkDeleteView):
    """View for deleting one or more EoxNotice records."""

    queryset = EoxNotice.objects.prefetch_related("devices", "device_type")
    table = EoxNoticesTable
    bulk_delete_url = "plugins:eox_notices.eoxnotice_bulk_delete"
    default_return_url = "plugins:eox_notices:eoxnotice_list"

    def get_required_permission(self):
        """Return required delete permission."""
        return "eox_notices.delete_eoxnotice"


class EoxNoticeBulkEditView(BulkEditView):
    """View for editing one or more EoxNotice records."""

    queryset = EoxNotice.objects.prefetch_related("devices", "device_type")
    filterset = EoxNoticeFilter
    table = EoxNoticesTable
    form = EoxNoticeBulkEditForm
    bulk_edit_url = "plugins:eox_notices.eoxnotice_bulk_edit"

    def get_required_permission(self):
        """Return required change permission."""
        return "eox_notices.change_eoxnotice"

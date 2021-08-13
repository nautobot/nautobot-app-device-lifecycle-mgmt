"""Views for nautobot_plugin_device_lifecycle_mgmt."""

from nautobot.core.views import generic
from nautobot_plugin_device_lifecycle_mgmt.models import EoxNotice, SoftwareLCM, ValidatedSoftwareLCM
from nautobot_plugin_device_lifecycle_mgmt.tables import EoxNoticesTable, SoftwareLCMTable, ValidatedSoftwareLCMTable
from nautobot_plugin_device_lifecycle_mgmt.forms import (
    EoxNoticeForm,
    EoxNoticeBulkEditForm,
    EoxNoticeFilterForm,
    EoxNoticeCSVForm,
    SoftwareLCMForm,
    SoftwareLCMFilterForm,
    ValidatedSoftwareLCMForm,
    ValidatedSoftwareLCMFilterForm,
)
from nautobot_plugin_device_lifecycle_mgmt.filters import (
    EoxNoticeFilter,
    SoftwareLCMFilterSet,
    ValidatedSoftwareLCMFilterSet,
)
from nautobot_plugin_device_lifecycle_mgmt.const import Permissions, URL


class EoxNoticesListView(generic.ObjectListView):
    """List view."""

    queryset = EoxNotice.objects.prefetch_related("devices", "device_type")
    filterset = EoxNoticeFilter
    filterset_form = EoxNoticeFilterForm
    table = EoxNoticesTable
    # template_name = "nautobot_plugin_device_lifecycle_mgmt/eoxnotice.html"

    def get_required_permission(self):
        """Return required view permission."""
        return Permissions.EoX.Read


class EoxNoticeView(generic.ObjectView):
    """Detail view."""

    queryset = EoxNotice.objects.prefetch_related("devices", "device_type")

    def get_required_permission(self):
        """Return required view permission."""
        return Permissions.EoX.Read


class EoxNoticeCreateView(generic.ObjectEditView):
    """Create view."""

    model = EoxNotice
    queryset = EoxNotice.objects.prefetch_related("devices", "device_type")
    model_form = EoxNoticeForm
    default_return_url = URL.EoX.List

    def get_required_permission(self):
        """Return required add permission."""
        return Permissions.EoX.Create


class EoxNoticeDeleteView(generic.ObjectDeleteView):
    """Delete view."""

    model = EoxNotice
    queryset = EoxNotice.objects.prefetch_related("devices", "device_type")
    default_return_url = URL.EoX.List

    def get_required_permission(self):
        """Return required delete permission."""
        return Permissions.EoX.Delete


class EoxNoticeEditView(generic.ObjectEditView):
    """Edit view."""

    model = EoxNotice
    queryset = EoxNotice.objects.prefetch_related("devices", "device_type")
    model_form = EoxNoticeForm
    default_return_url = URL.EoX.View

    def get_required_permission(self):
        """Return required change permission."""
        return Permissions.EoX.Update


class EoxNoticeBulkImportView(generic.BulkImportView):
    """View for bulk import of eox notices."""

    queryset = EoxNotice.objects.prefetch_related("devices", "device_type")
    model_form = EoxNoticeCSVForm
    table = EoxNoticesTable
    default_return_url = URL.EoX.List


class EoxNoticeBulkDeleteView(generic.BulkDeleteView):
    """View for deleting one or more EoxNotice records."""

    queryset = EoxNotice.objects.prefetch_related("devices", "device_type")
    table = EoxNoticesTable
    bulk_delete_url = URL.EoX.BulkDelete
    default_return_url = URL.EoX.List

    def get_required_permission(self):
        """Return required delete permission."""
        return Permissions.EoX.Delete


class EoxNoticeBulkEditView(generic.BulkEditView):
    """View for editing one or more EoxNotice records."""

    queryset = EoxNotice.objects.prefetch_related("devices", "device_type")
    filterset = EoxNoticeFilter
    table = EoxNoticesTable
    form = EoxNoticeBulkEditForm
    bulk_edit_url = URL.EoX.BulkEdit

    def get_required_permission(self):
        """Return required change permission."""
        return Permissions.EoX.Update


class SoftwareLCMListView(generic.ObjectListView):
    """SoftwareLCM List view."""

    queryset = SoftwareLCM.objects.prefetch_related("device_platform")
    filterset = SoftwareLCMFilterSet
    filterset_form = SoftwareLCMFilterForm
    table = SoftwareLCMTable
    action_buttons = (
        "add",
        "delete",
    )


class SoftwareLCMView(generic.ObjectView):
    """SoftwareLCM Detail view."""

    queryset = SoftwareLCM.objects.prefetch_related("device_platform")


class SoftwareLCMCreateView(generic.ObjectEditView):
    """SoftwareLCM Create view."""

    model = SoftwareLCM
    queryset = SoftwareLCM.objects.prefetch_related("device_platform")
    model_form = SoftwareLCMForm
    default_return_url = URL.SoftwareLCM.List


class SoftwareLCMDeleteView(generic.ObjectDeleteView):
    """SoftwareLCM Delete view."""

    model = SoftwareLCM
    queryset = SoftwareLCM.objects.prefetch_related("device_platform")
    default_return_url = URL.SoftwareLCM.List
    template_name = "nautobot_plugin_device_lifecycle_mgmt/softwarelcm_delete.html"


class SoftwareLCMEditView(generic.ObjectEditView):
    """SoftwareLCM Edit view."""

    model = SoftwareLCM
    queryset = SoftwareLCM.objects.prefetch_related("device_platform")
    model_form = SoftwareLCMForm
    default_return_url = URL.SoftwareLCM.View


class ValidatedSoftwareLCMListView(generic.ObjectListView):
    """ValidatedSoftware List view."""

    queryset = ValidatedSoftwareLCM.objects.all()
    filterset = ValidatedSoftwareLCMFilterSet
    filterset_form = ValidatedSoftwareLCMFilterForm
    table = ValidatedSoftwareLCMTable
    action_buttons = (
        "add",
        "delete",
    )


class ValidatedSoftwareLCMView(generic.ObjectView):
    """ValidatedSoftware Detail view."""

    queryset = ValidatedSoftwareLCM.objects.all()


class ValidatedSoftwareLCMEditView(generic.ObjectEditView):
    """ValidatedSoftware Create view."""

    # model = ValidatedSoftwareLCM
    queryset = ValidatedSoftwareLCM.objects.all()
    model_form = ValidatedSoftwareLCMForm
    template_name = "nautobot_plugin_device_lifecycle_mgmt/validatedsoftwarelcm_edit.html"
    default_return_url = URL.ValidatedSoftwareLCM.List


class ValidatedSoftwareLCMDeleteView(generic.ObjectDeleteView):
    """SoftwareLCM Delete view."""

    model = ValidatedSoftwareLCM
    queryset = ValidatedSoftwareLCM.objects.all()
    default_return_url = URL.ValidatedSoftwareLCM.List
    template_name = "nautobot_plugin_device_lifecycle_mgmt/validatedsoftwarelcm_delete.html"

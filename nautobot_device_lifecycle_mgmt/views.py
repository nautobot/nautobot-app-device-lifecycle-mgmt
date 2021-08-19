<<<<<<< HEAD
"""Views implementation for the LifeCycle Management plugin."""
from nautobot.core.views import generic
from nautobot.dcim.models import Device
from nautobot_device_lifecycle_mgmt.models import HardwareLCM
from nautobot_device_lifecycle_mgmt.tables import HardwareLCMTable
from nautobot_device_lifecycle_mgmt.forms import (
    HardwareLCMForm,
    HardwareLCMBulkEditForm,
    HardwareLCMFilterForm,
    HardwareLCMCSVForm,
)
from nautobot_device_lifecycle_mgmt.filters import HardwareLCMFilterSet

# ---------------------------------------------------------------------------------
#  Hardware LifeCycle Management Views
# ---------------------------------------------------------------------------------


class HardwareLCMListView(generic.ObjectListView):
    """List view."""

    queryset = HardwareLCM.objects.prefetch_related("device_type")
    filterset = HardwareLCMFilterSet
    filterset_form = HardwareLCMFilterForm
    table = HardwareLCMTable


class HardwareLCMView(generic.ObjectView):
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


class HardwareLCMCreateView(generic.ObjectEditView):
    """Create view."""

    model = HardwareLCM
    queryset = HardwareLCM.objects.prefetch_related("device_type")
    model_form = HardwareLCMForm
    default_return_url = "plugins:nautobot_device_lifecycle_mgmt:hardwarelcm_list"


class HardwareLCMDeleteView(generic.ObjectDeleteView):
    """Delete view."""

    model = HardwareLCM
    queryset = HardwareLCM.objects.prefetch_related("device_type")
    default_return_url = "plugins:nautobot_device_lifecycle_mgmt:hardwarelcm_list"


class HardwareLCMEditView(generic.ObjectEditView):
    """Edit view."""

    model = HardwareLCM
    queryset = HardwareLCM.objects.prefetch_related("device_type")
    model_form = HardwareLCMForm
    default_return_url = "plugins:nautobot_device_lifecycle_mgmt:hardwarelcm"


class HardwareLCMBulkImportView(generic.BulkImportView):
    """View for bulk import of hardware lcm."""

    queryset = HardwareLCM.objects.prefetch_related("device_type")
    model_form = HardwareLCMCSVForm
    table = HardwareLCMTable
    default_return_url = "plugins:nautobot_device_lifecycle_mgmt:hardwarelcm_list"


class HardwareLCMBulkDeleteView(generic.BulkDeleteView):
    """View for deleting one or more HardwareLCM records."""

    queryset = HardwareLCM.objects.prefetch_related("device_type")
    table = HardwareLCMTable
    bulk_delete_url = "plugins:nautobot_device_lifecycle_mgmt.hardwarelcm_bulk_delete"
    default_return_url = "plugins:nautobot_device_lifecycle_mgmt:hardwarelcm_list"


class HardwareLCMBulkEditView(generic.BulkEditView):
    """View for editing one or more HardwareLCM records."""

    queryset = HardwareLCM.objects.prefetch_related("device_type")
    filterset = HardwareLCMFilterSet
    table = HardwareLCMTable
    form = HardwareLCMBulkEditForm
    bulk_edit_url = "plugins:nautobot_device_lifecycle_mgmt.hardwarelcm_bulk_edit"
=======
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
>>>>>>> c9c3a9d (Rename plugin)

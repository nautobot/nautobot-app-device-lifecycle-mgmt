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

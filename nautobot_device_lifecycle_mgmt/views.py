"""Views implementation for the LifeCycle Management plugin."""
from nautobot.core.views import generic
from nautobot.dcim.models import Device
from nautobot_device_lifecycle_mgmt.models import (
    HardwareLCM,
    SoftwareLCM,
    ContactLCM,
    ValidatedSoftwareLCM,
    ContractLCM,
    ProviderLCM,
)
from nautobot_device_lifecycle_mgmt.tables import (
    HardwareLCMTable,
    SoftwareLCMTable,
    ValidatedSoftwareLCMTable,
    ContractLCMTable,
    ProviderLCMTable,
    ContactLCMTable,
)
from nautobot_device_lifecycle_mgmt.forms import (
    HardwareLCMForm,
    HardwareLCMBulkEditForm,
    HardwareLCMFilterForm,
    HardwareLCMCSVForm,
    SoftwareLCMForm,
    SoftwareLCMFilterForm,
    SoftwareLCMCSVForm,
    ValidatedSoftwareLCMForm,
    ValidatedSoftwareLCMFilterForm,
    ValidatedSoftwareLCMCSVForm,
    ContractLCMForm,
    ContractLCMBulkEditForm,
    ContractLCMFilterForm,
    ContractLCMCSVForm,
    ProviderLCMForm,
    ProviderLCMBulkEditForm,
    ProviderLCMFilterForm,
    ProviderLCMCSVForm,
    ContactLCMForm,
    ContactLCMBulkEditForm,
    ContactLCMFilterForm,
    ContactLCMCSVForm,
)
from nautobot_device_lifecycle_mgmt.filters import (
    HardwareLCMFilterSet,
    ContractLCMFilterSet,
    ProviderLCMFilterSet,
    ContactLCMFilterSet,
    SoftwareLCMFilterSet,
    ValidatedSoftwareLCMFilterSet,
)

from nautobot_device_lifecycle_mgmt.const import URL

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


class SoftwareLCMListView(generic.ObjectListView):
    """SoftwareLCM List view."""

    queryset = SoftwareLCM.objects.prefetch_related("device_platform")
    filterset = SoftwareLCMFilterSet
    filterset_form = SoftwareLCMFilterForm
    table = SoftwareLCMTable
    action_buttons = (
        "add",
        "delete",
        "import",
        "export",
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
    template_name = "nautobot_device_lifecycle_mgmt/softwarelcm_delete.html"


class SoftwareLCMEditView(generic.ObjectEditView):
    """SoftwareLCM Edit view."""

    model = SoftwareLCM
    queryset = SoftwareLCM.objects.prefetch_related("device_platform")
    model_form = SoftwareLCMForm
    default_return_url = URL.SoftwareLCM.View


class SoftwareLCMBulkImportView(generic.BulkImportView):
    """View for bulk import of SoftwareLCM."""

    queryset = SoftwareLCM.objects.prefetch_related("device_platform")
    model_form = SoftwareLCMCSVForm
    table = SoftwareLCMTable
    default_return_url = "plugins:nautobot_device_lifecycle_mgmt:softwarelcm_list"


class ValidatedSoftwareLCMListView(generic.ObjectListView):
    """ValidatedSoftware List view."""

    queryset = ValidatedSoftwareLCM.objects.all()
    filterset = ValidatedSoftwareLCMFilterSet
    filterset_form = ValidatedSoftwareLCMFilterForm
    table = ValidatedSoftwareLCMTable
    action_buttons = (
        "add",
        "delete",
        "import",
        "export",
    )


class ValidatedSoftwareLCMView(generic.ObjectView):
    """ValidatedSoftware Detail view."""

    queryset = ValidatedSoftwareLCM.objects.all()


class ValidatedSoftwareLCMEditView(generic.ObjectEditView):
    """ValidatedSoftware Create view."""

    # model = ValidatedSoftwareLCM
    queryset = ValidatedSoftwareLCM.objects.all()
    model_form = ValidatedSoftwareLCMForm
    template_name = "nautobot_device_lifecycle_mgmt/validatedsoftwarelcm_edit.html"
    default_return_url = URL.ValidatedSoftwareLCM.List


class ValidatedSoftwareLCMDeleteView(generic.ObjectDeleteView):
    """SoftwareLCM Delete view."""

    model = ValidatedSoftwareLCM
    queryset = ValidatedSoftwareLCM.objects.all()
    default_return_url = URL.ValidatedSoftwareLCM.List
    template_name = "nautobot_device_lifecycle_mgmt/validatedsoftwarelcm_delete.html"


class ValidatedSoftwareLCMBulkImportView(generic.BulkImportView):
    """View for bulk import of ValidatedSoftwareLCM."""

    queryset = ValidatedSoftwareLCM.objects.all()
    model_form = ValidatedSoftwareLCMCSVForm
    table = ValidatedSoftwareLCMTable
    default_return_url = "plugins:nautobot_device_lifecycle_mgmt:validatedsoftwarelcm_list"


# ---------------------------------------------------------------------------------
#  Contract LifeCycle Management Views
# ---------------------------------------------------------------------------------


class ContractLCMListView(generic.ObjectListView):
    """List view."""

    queryset = ContractLCM.objects.all()
    filterset = ContractLCMFilterSet
    filterset_form = ContractLCMFilterForm
    table = ContractLCMTable


class ContractLCMView(generic.ObjectView):
    """Detail view."""

    queryset = ContractLCM.objects.all()

    def get_extra_context(self, request, instance):
        """Return any additional context data for the template.

        request: The current request
        instance: The object being viewed
        """
        return {
            "contacts": ContactLCM.objects.restrict(request.user, "view")
            .filter(contract=instance)
            .exclude(type="Owner")
            .order_by("type", "priority"),
            "owners": ContactLCM.objects.restrict(request.user, "view")
            .filter(contract=instance, type="Owner")
            .order_by("type", "priority"),
        }


class ContractLCMCreateView(generic.ObjectEditView):
    """Create view."""

    model = ContractLCM
    queryset = ContractLCM.objects.all()
    model_form = ContractLCMForm
    default_return_url = "plugins:nautobot_device_lifecycle_mgmt:contractlcm_list"


class ContractLCMDeleteView(generic.ObjectDeleteView):
    """Delete view."""

    model = ContractLCM
    queryset = ContractLCM.objects.all()
    default_return_url = "plugins:nautobot_device_lifecycle_mgmt:contractlcm_list"


class ContractLCMEditView(generic.ObjectEditView):
    """Edit view."""

    model = ContractLCM
    queryset = ContractLCM.objects.all()
    model_form = ContractLCMForm
    default_return_url = "plugins:nautobot_device_lifecycle_mgmt:contractlcm"


class ContractLCMBulkImportView(generic.BulkImportView):
    """View for bulk import of hardware lcm."""

    queryset = ContractLCM.objects.all()
    model_form = ContractLCMCSVForm
    table = ContractLCMTable
    default_return_url = "plugins:nautobot_device_lifecycle_mgmt:contractlcm_list"


class ContractLCMBulkDeleteView(generic.BulkDeleteView):
    """View for deleting one or more HardwareLCM records."""

    queryset = ContractLCM.objects.all()
    table = ContractLCMTable
    bulk_delete_url = "plugins:nautobot_device_lifecycle_mgmt.contractlcm_bulk_delete"
    default_return_url = "plugins:nautobot_device_lifecycle_mgmt:contractlcm_list"


class ContractLCMBulkEditView(generic.BulkEditView):
    """View for editing one or more HardwareLCM records."""

    queryset = ContractLCM.objects.all()
    filterset = ContractLCMFilterSet
    table = ContractLCMTable
    form = ContractLCMBulkEditForm
    bulk_edit_url = "plugins:nautobot_device_lifecycle_mgmt.contractlcm_bulk_edit"


# ---------------------------------------------------------------------------------
#  Contract Provider LifeCycle Management Views
# ---------------------------------------------------------------------------------


class ProviderLCMListView(generic.ObjectListView):
    """List view."""

    queryset = ProviderLCM.objects.all()
    filterset = ProviderLCMFilterSet
    filterset_form = ProviderLCMFilterForm
    table = ProviderLCMTable


class ProviderLCMView(generic.ObjectView):
    """Detail view."""

    queryset = ProviderLCM.objects.all()

    def get_extra_context(self, request, instance):
        """Return any additional context data for the template.

        request: The current request
        instance: The object being viewed
        """
        return {"contracts": ContractLCM.objects.restrict(request.user, "view").filter(provider=instance)}


class ProviderLCMCreateView(generic.ObjectEditView):
    """Create view."""

    model = ProviderLCM
    queryset = ProviderLCM.objects.all()
    model_form = ProviderLCMForm
    default_return_url = "plugins:nautobot_device_lifecycle_mgmt:providerlcm_list"


class ProviderLCMDeleteView(generic.ObjectDeleteView):
    """Delete view."""

    model = ProviderLCM
    queryset = ProviderLCM.objects.all()
    default_return_url = "plugins:nautobot_device_lifecycle_mgmt:providerlcm_list"


class ProviderLCMEditView(generic.ObjectEditView):
    """Edit view."""

    model = ProviderLCM
    queryset = ProviderLCM.objects.all()
    model_form = ProviderLCMForm
    default_return_url = "plugins:nautobot_device_lifecycle_mgmt:providerlcm"


class ProviderLCMBulkImportView(generic.BulkImportView):
    """Bulk import view."""

    queryset = ProviderLCM.objects.all()
    model_form = ProviderLCMCSVForm
    table = ProviderLCMTable
    default_return_url = "plugins:nautobot_device_lifecycle_mgmt:providerlcm_list"


class ProviderLCMBulkDeleteView(generic.BulkDeleteView):
    """View for deleting one or more HardwareLCM records."""

    queryset = ProviderLCM.objects.all()
    table = ProviderLCMTable
    bulk_delete_url = "plugins:nautobot_device_lifecycle_mgmt.providerlcm_bulk_delete"
    default_return_url = "plugins:nautobot_device_lifecycle_mgmt:providerlcm_list"


class ProviderLCMBulkEditView(generic.BulkEditView):
    """View for editing one or more HardwareLCM records."""

    queryset = ProviderLCM.objects.all()
    filterset = ProviderLCMFilterSet
    table = ProviderLCMTable
    form = ProviderLCMBulkEditForm
    bulk_edit_url = "plugins:nautobot_device_lifecycle_mgmt.providerlcm_bulk_edit"


# ---------------------------------------------------------------------------------
#  Contact POC LifeCycle Management Views
# ---------------------------------------------------------------------------------


class ContactLCMListView(generic.ObjectListView):
    """List view."""

    queryset = ContactLCM.objects.all()
    filterset = ContactLCMFilterSet
    filterset_form = ContactLCMFilterForm
    table = ContactLCMTable


class ContactLCMView(generic.ObjectView):
    """Detail view."""

    queryset = ContactLCM.objects.all()


class ContactLCMCreateView(generic.ObjectEditView):
    """Create view."""

    model = ContactLCM
    queryset = ContactLCM.objects.all()
    model_form = ContactLCMForm
    default_return_url = "plugins:nautobot_device_lifecycle_mgmt:contactlcm_list"


class ContactLCMDeleteView(generic.ObjectDeleteView):
    """Delete view."""

    model = ContactLCM
    queryset = ContactLCM.objects.all()
    default_return_url = "plugins:nautobot_device_lifecycle_mgmt:contactlcm_list"


class ContactLCMEditView(generic.ObjectEditView):
    """Edit view."""

    model = ContactLCM
    queryset = ContactLCM.objects.all()
    model_form = ContactLCMForm
    default_return_url = "plugins:nautobot_device_lifecycle_mgmt:contactlcm"


class ContactLCMBulkImportView(generic.BulkImportView):
    """Bulk import view."""

    queryset = ContactLCM.objects.all()
    model_form = ContactLCMCSVForm
    table = ContactLCMTable
    default_return_url = "plugins:nautobot_device_lifecycle_mgmt:contactlcm_list"


class ContactLCMBulkDeleteView(generic.BulkDeleteView):
    """View for deleting one or more records."""

    queryset = ContactLCM.objects.all()
    table = ContactLCMTable
    bulk_delete_url = "plugins:nautobot_device_lifecycle_mgmt.contactlcm_bulk_delete"
    default_return_url = "plugins:nautobot_device_lifecycle_mgmt:contactlcm_list"


class ContactLCMBulkEditView(generic.BulkEditView):
    """View for editing one or more records."""

    queryset = ContactLCM.objects.all()
    filterset = ContactLCMFilterSet
    table = ContactLCMTable
    form = ContactLCMBulkEditForm
    bulk_edit_url = "plugins:nautobot_device_lifecycle_mgmt.contactlcm_bulk_edit"

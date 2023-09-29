"""Nautobot UI Viewsets."""

from nautobot.apps.views import NautobotUIViewSet
from nautobot.core.forms.search import SearchForm
from nautobot.dcim.models import Device

from nautobot_device_lifecycle_mgmt import filters, forms, models, tables
from nautobot_device_lifecycle_mgmt.api import serializers


class HardwareLCMUIViewSet(NautobotUIViewSet):
    """HardwareLCM UI ViewSet."""

    bulk_update_form_class = forms.HardwareLCMBulkEditForm
    filterset_class = filters.HardwareLCMFilterSet
    filterset_form_class = forms.HardwareLCMFilterForm
    form_class = forms.HardwareLCMForm
    queryset = models.HardwareLCM.objects.prefetch_related("device_type")
    serializer_class = serializers.HardwareLCMSerializer
    table_class = tables.HardwareLCMTable

    def get_extra_context(self, request, instance):  # pylint: disable=signature-differs
        """Return any additional context data for the template.

        request: The current request
        instance: The object being viewed
        """
        if not instance:
            return {}
        if instance.device_type:
            return {"devices": Device.objects.restrict(request.user, "view").filter(device_type=instance.device_type)}
        if instance.inventory_item:
            return {
                "devices": Device.objects.restrict(request.user, "view").filter(
                    inventory_items__part_id=instance.inventory_item
                )
            }
        return {"devices": []}


class SoftwareLCMUIViewSet(NautobotUIViewSet):
    """SoftwareLCM UI ViewSet."""

    # TODO: Add bulk edit form
    # bulk_update_form_class = forms.SoftwareLCMBulkEditForm
    filterset_class = filters.SoftwareLCMFilterSet
    filterset_form_class = forms.SoftwareLCMFilterForm
    form_class = forms.SoftwareLCMForm
    queryset = models.SoftwareLCM.objects.prefetch_related("device_platform")
    serializer_class = serializers.SoftwareLCMSerializer
    table_class = tables.SoftwareLCMTable

    def get_extra_context(self, request, instance):  # pylint: disable=signature-differs
        """Changes "Softwares" => "Software"."""
        search_form = SearchForm(data=self.request.GET)

        return {
            "search_form": search_form,
            "title": "Software",
            "verbose_name_plural": "Software",
        }


class SoftwareImageLCMUIViewSet(NautobotUIViewSet):
    """SoftwareImageLCM UI ViewSet."""

    # TODO: Add bulk edit form
    # bulk_update_form_class = forms.SoftwareImageLCMBulkEditForm
    filterset_class = filters.SoftwareImageLCMFilterSet
    filterset_form_class = forms.SoftwareImageLCMFilterForm
    form_class = forms.SoftwareImageLCMForm
    queryset = models.SoftwareImageLCM.objects.all()
    serializer_class = serializers.SoftwareImageLCMSerializer
    table_class = tables.SoftwareImageLCMTable


class ValidatedSoftwareLCMUIViewSet(NautobotUIViewSet):
    """ValidatedSoftwareLCM UI ViewSet."""

    # TODO: Add bulk edit form
    # bulk_update_form_class = forms.ValidatedSoftwareLCMBulkEditForm
    filterset_class = filters.ValidatedSoftwareLCMFilterSet
    filterset_form_class = forms.ValidatedSoftwareLCMFilterForm
    form_class = forms.ValidatedSoftwareLCMForm
    queryset = models.ValidatedSoftwareLCM.objects.all()
    serializer_class = serializers.ValidatedSoftwareLCMSerializer
    table_class = tables.ValidatedSoftwareLCMTable


class ContractLCMUIViewSet(NautobotUIViewSet):
    """ContractLCM UI ViewSet."""

    bulk_update_form_class = forms.ContractLCMBulkEditForm
    filterset_class = filters.ContractLCMFilterSet
    filterset_form_class = forms.ContractLCMFilterForm
    form_class = forms.ContractLCMForm
    queryset = models.ContractLCM.objects.all()
    serializer_class = serializers.ContractLCMSerializer
    table_class = tables.ContractLCMTable

    def get_extra_context(self, request, instance):  # pylint: disable=signature-differs
        """Return any additional context data for the template.

        request: The current request
        instance: The object being viewed
        """
        return {
            "contacts": models.ContactLCM.objects.restrict(request.user, "view")
            .filter(contract=instance)
            .exclude(type="Owner")
            .order_by("type", "priority"),
            "owners": models.ContactLCM.objects.restrict(request.user, "view")
            .filter(contract=instance, type="Owner")
            .order_by("type", "priority"),
        }


class ProviderLCMUIViewSet(NautobotUIViewSet):
    """ProviderLCM UI ViewSet."""

    bulk_update_form_class = forms.ProviderLCMBulkEditForm
    filterset_class = filters.ProviderLCMFilterSet
    filterset_form_class = forms.ProviderLCMFilterForm
    form_class = forms.ProviderLCMForm
    queryset = models.ProviderLCM.objects.all()
    serializer_class = serializers.ProviderLCMSerializer
    table_class = tables.ProviderLCMTable

    def get_extra_context(self, request, instance):  # pylint: disable=signature-differs
        """Return any additional context data for the template.

        request: The current request
        instance: The object being viewed
        """
        return {"contracts": models.ContractLCM.objects.restrict(request.user, "view").filter(provider=instance)}


class ContactLCMUIViewSet(NautobotUIViewSet):
    """ContactLCM UI ViewSet."""

    bulk_update_form_class = forms.ContactLCMBulkEditForm
    filterset_class = filters.ContactLCMFilterSet
    filterset_form_class = forms.ContactLCMFilterForm
    form_class = forms.ContactLCMForm
    queryset = models.ContactLCM.objects.all()
    serializer_class = serializers.ContactLCMSerializer
    table_class = tables.ContactLCMTable


class CVELCMUIViewSet(NautobotUIViewSet):
    """CVELCM UI ViewSet."""

    bulk_update_form_class = forms.CVELCMBulkEditForm
    filterset_class = filters.CVELCMFilterSet
    filterset_form_class = forms.CVELCMFilterForm
    form_class = forms.CVELCMForm
    queryset = models.CVELCM.objects.all()
    serializer_class = serializers.CVELCMSerializer
    table_class = tables.CVELCMTable


class VulnerabilityLCMUIViewSet(NautobotUIViewSet):
    """VulnerabilityLCM UI ViewSet."""

    bulk_update_form_class = forms.VulnerabilityLCMBulkEditForm
    filterset_class = filters.VulnerabilityLCMFilterSet
    filterset_form_class = forms.VulnerabilityLCMFilterForm
    form_class = forms.VulnerabilityLCMForm
    queryset = models.VulnerabilityLCM.objects.all()
    serializer_class = serializers.VulnerabilityLCMSerializer
    table_class = tables.VulnerabilityLCMTable

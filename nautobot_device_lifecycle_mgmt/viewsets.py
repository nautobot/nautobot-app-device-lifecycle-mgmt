"""Nautobot UI Viewsets."""

from django_tables2 import RequestConfig

from nautobot.apps.views import NautobotUIViewSet
from nautobot.core.forms import SearchForm
from nautobot.core.views.paginator import EnhancedPaginator, get_paginate_count
from nautobot.dcim.models import Device

from nautobot_device_lifecycle_mgmt import forms, models, filters, tables
from nautobot_device_lifecycle_mgmt.api import serializers
from nautobot_device_lifecycle_mgmt.utils import count_related_m2m


class HardwareLCMUIViewSet(NautobotUIViewSet):
    """HardwareLCM UI ViewSet."""

    bulk_update_form_class = forms.HardwareLCMBulkEditForm
    filterset_class = filters.HardwareLCMFilterSet
    filterset_form_class = forms.HardwareLCMFilterForm
    form_class = forms.HardwareLCMForm
    queryset = models.HardwareLCM.objects.prefetch_related("device_type")
    serializer_class = serializers.HardwareLCMSerializer
    table_class = tables.HardwareLCMTable

    def get_extra_context(self, request, instance):
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
                    inventoryitems__part_id=instance.inventory_item
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

    def get_extra_context(self, request, instance):
        """Changes "Softwares" => "Software"."""
        search_form = SearchForm(data=self.request.GET)
        if not instance:
            return {
                "search_form": search_form,
                "title": "Software",
                "verbose_name_plural": "Software",
            }
        softwareimages = instance.software_images.restrict(request.user, "view")
        if softwareimages.exists():
            softwareimages_table = tables.SoftwareImageLCMTable(data=softwareimages, user=request.user, orderable=False)
        else:
            softwareimages_table = None

        return {
            "softwareimages_table": softwareimages_table,
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

    def get_extra_context(self, request, instance):
        """Adds Software Images table."""
        if not instance:
            return {}
        softwareimages = (
            instance.software_images.annotate(
                device_type_count=count_related_m2m(models.SoftwareImageLCM, "device_types")
            )
            .annotate(object_tag_count=count_related_m2m(models.SoftwareImageLCM, "object_tags"))
            .restrict(request.user, "view")
        )

        softwareimages_table = tables.SoftwareImageLCMTable(data=softwareimages, user=request.user, orderable=False)

        paginate = {
            "paginator_class": EnhancedPaginator,
            "per_page": get_paginate_count(request),
        }
        RequestConfig(request, paginate).configure(softwareimages_table)

        return {
            "softwareimages_table": softwareimages_table,
            "active_tab": "software-images",
        }


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

    def get_extra_context(self, request, instance):
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

    def get_extra_context(self, request, instance):
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
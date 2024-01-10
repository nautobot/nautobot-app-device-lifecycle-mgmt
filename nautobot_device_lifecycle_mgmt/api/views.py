"""API Views implementation for the Lifecycle Management app."""
from nautobot.apps.api import NautobotModelViewSet

from nautobot_device_lifecycle_mgmt.filters import (
    ContactLCMFilterSet,
    ContractLCMFilterSet,
    CVELCMFilterSet,
    DeviceSoftwareValidationResultFilterSet,
    HardwareLCMFilterSet,
    InventoryItemSoftwareValidationResultFilterSet,
    ProviderLCMFilterSet,
    SoftwareImageLCMFilterSet,
    SoftwareLCMFilterSet,
    ValidatedSoftwareLCMFilterSet,
    VulnerabilityLCMFilterSet,
)
from nautobot_device_lifecycle_mgmt.models import (
    CVELCM,
    ContactLCM,
    ContractLCM,
    DeviceSoftwareValidationResult,
    HardwareLCM,
    InventoryItemSoftwareValidationResult,
    ProviderLCM,
    SoftwareImageLCM,
    SoftwareLCM,
    ValidatedSoftwareLCM,
    VulnerabilityLCM,
)

from .serializers import (
    ContactLCMSerializer,
    ContractLCMSerializer,
    CVELCMSerializer,
    DeviceSoftwareValidationResultSerializer,
    HardwareLCMSerializer,
    InventoryItemSoftwareValidationResultSerializer,
    ProviderLCMSerializer,
    SoftwareImageLCMSerializer,
    SoftwareLCMSerializer,
    ValidatedSoftwareLCMSerializer,
    VulnerabilityLCMSerializer,
)


class HardwareLCMView(NautobotModelViewSet):
    """CRUD operations set for the Hardware Lifecycle Management view."""

    queryset = HardwareLCM.objects.all()
    filterset_class = HardwareLCMFilterSet
    serializer_class = HardwareLCMSerializer


class ContractLCMView(NautobotModelViewSet):
    """CRUD operations set for the Contract Lifecycle Management view."""

    queryset = ContractLCM.objects.all()
    filterset_class = ContractLCMFilterSet
    serializer_class = ContractLCMSerializer


class ProviderLCMView(NautobotModelViewSet):
    """CRUD operations set for the Contract Provider Lifecycle Management view."""

    queryset = ProviderLCM.objects.all()
    filterset_class = ProviderLCMFilterSet
    serializer_class = ProviderLCMSerializer


class ContactLCMView(NautobotModelViewSet):
    """CRUD operations set for the Contact Lifecycle Management view."""

    queryset = ContactLCM.objects.all()
    filterset_class = ContactLCMFilterSet
    serializer_class = ContactLCMSerializer


class SoftwareLCMViewSet(NautobotModelViewSet):
    """REST API viewset for SoftwareLCM records."""

    queryset = SoftwareLCM.objects.prefetch_related("software_images")
    serializer_class = SoftwareLCMSerializer
    filterset_class = SoftwareLCMFilterSet


class SoftwareImageLCMViewSet(NautobotModelViewSet):
    """REST API viewset for SoftwareImageLCM records."""

    queryset = SoftwareImageLCM.objects.prefetch_related("software")
    serializer_class = SoftwareImageLCMSerializer
    filterset_class = SoftwareImageLCMFilterSet


class ValidatedSoftwareLCMViewSet(NautobotModelViewSet):
    """REST API viewset for ValidatedSoftwareLCM records."""

    queryset = ValidatedSoftwareLCM.objects.all()
    serializer_class = ValidatedSoftwareLCMSerializer
    filterset_class = ValidatedSoftwareLCMFilterSet


class CVELCMViewSet(NautobotModelViewSet):
    """REST API viewset for CVELCM records."""

    queryset = CVELCM.objects.all()
    serializer_class = CVELCMSerializer
    filterset_class = CVELCMFilterSet


class VulnerabilityLCMViewSet(NautobotModelViewSet):
    """REST API viewset for VulnerabilityLCM records."""

    queryset = VulnerabilityLCM.objects.all()
    serializer_class = VulnerabilityLCMSerializer
    filterset_class = VulnerabilityLCMFilterSet

    # Disabling POST as these should only be created via Job.
    http_method_names = ["get", "put", "patch", "delete", "head", "options"]


class DeviceSoftwareValidationResultListViewSet(NautobotModelViewSet):
    """REST API viewset for DeviceSoftwareValidationResult records."""

    queryset = DeviceSoftwareValidationResult.objects.all()
    serializer_class = DeviceSoftwareValidationResultSerializer
    filterset_class = DeviceSoftwareValidationResultFilterSet

    # Disabling POST as these should only be created via Job.
    http_method_names = ["get", "head", "options"]


class InventoryItemSoftwareValidationResultListViewSet(NautobotModelViewSet):
    """REST API viewset for DeviceSoftwareValidationResult records."""

    queryset = InventoryItemSoftwareValidationResult.objects.all()
    serializer_class = InventoryItemSoftwareValidationResultSerializer
    filterset_class = InventoryItemSoftwareValidationResultFilterSet

    # Disabling POST as these should only be created via Job.
    http_method_names = ["get", "head", "options"]

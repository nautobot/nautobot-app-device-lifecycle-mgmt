"""API Views implementation for the Lifecycle Management app."""

from nautobot.apps.api import NautobotModelViewSet

from nautobot_device_lifecycle_mgmt.filters import (
    ContractLCMFilterSet,
    CVELCMFilterSet,
    DeviceHardwareNoticeResultFilterSet,
    DeviceSoftwareValidationResultFilterSet,
    HardwareLCMFilterSet,
    InventoryItemSoftwareValidationResultFilterSet,
    ProviderLCMFilterSet,
    SoftwareNoticeFilterSet,
    ValidatedSoftwareLCMFilterSet,
    VulnerabilityLCMFilterSet,
)
from nautobot_device_lifecycle_mgmt.models import (
    CVELCM,
    ContractLCM,
    DeviceHardwareNoticeResult,
    DeviceSoftwareValidationResult,
    HardwareLCM,
    InventoryItemSoftwareValidationResult,
    ProviderLCM,
    SoftwareNotice,
    ValidatedSoftwareLCM,
    VulnerabilityLCM,
)

from .serializers import (
    ContractLCMSerializer,
    CVELCMSerializer,
    DeviceHardwareNoticeResultSerializer,
    DeviceSoftwareValidationResultSerializer,
    HardwareLCMSerializer,
    InventoryItemSoftwareValidationResultSerializer,
    ProviderLCMSerializer,
    SoftwareNoticeSerializer,
    ValidatedSoftwareLCMSerializer,
    VulnerabilityLCMSerializer,
)


class HardwareLCMView(NautobotModelViewSet):
    """CRUD operations set for the Hardware Lifecycle Management view."""

    queryset = HardwareLCM.objects.all()
    filterset_class = HardwareLCMFilterSet
    serializer_class = HardwareLCMSerializer


class SoftwareNoticeView(NautobotModelViewSet):
    """CRUD operations set for the Software Notice Lifecycle Management view."""

    queryset = SoftwareNotice.objects.all()
    filterset_class = SoftwareNoticeFilterSet
    serializer_class = SoftwareNoticeSerializer


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


class DeviceHardwareNoticeResultListViewSet(NautobotModelViewSet):
    """REST API viewset for DeviceHardwareNoticeResult records."""

    queryset = DeviceHardwareNoticeResult.objects.all()
    serializer_class = DeviceHardwareNoticeResultSerializer
    filterset_class = DeviceHardwareNoticeResultFilterSet

    # Disabling POST as these should only be created via Job.
    http_method_names = ["get", "head", "options"]


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

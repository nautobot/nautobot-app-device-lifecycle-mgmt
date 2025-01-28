"""API views for nautobot_device_lifecycle_mgmt."""

from nautobot.apps.api import NautobotModelViewSet

from nautobot_device_lifecycle_mgmt import filters, models
from nautobot_device_lifecycle_mgmt.api import serializers


class HardwareLCMView(NautobotModelViewSet):
    """CRUD operations set for the Hardware Lifecycle Management view."""

    queryset = models.HardwareLCM.objects.all()
    filterset_class = filters.HardwareLCMFilterSet
    serializer_class = serializers.HardwareLCMSerializer


class ContractLCMView(NautobotModelViewSet):
    """CRUD operations set for the Contract Lifecycle Management view."""

    queryset = models.ContractLCM.objects.all()
    filterset_class = filters.ContractLCMFilterSet
    serializer_class = serializers.ContractLCMSerializer


class ProviderLCMView(NautobotModelViewSet):
    """CRUD operations set for the Contract Provider Lifecycle Management view."""

    queryset = models.ProviderLCM.objects.all()
    filterset_class = filters.ProviderLCMFilterSet
    serializer_class = serializers.ProviderLCMSerializer


class ContactLCMView(NautobotModelViewSet):
    """CRUD operations set for the Contact Lifecycle Management view."""

    queryset = models.ContactLCM.objects.all()
    filterset_class = filters.ContactLCMFilterSet
    serializer_class = serializers.ContactLCMSerializer


class SoftwareLCMViewSet(NautobotModelViewSet):
    """REST API viewset for SoftwareLCM records."""

    queryset = models.SoftwareLCM.objects.prefetch_related("software_images")
    serializer_class = serializers.SoftwareLCMSerializer
    filterset_class = filters.SoftwareLCMFilterSet


class SoftwareImageLCMViewSet(NautobotModelViewSet):
    """REST API viewset for SoftwareImageLCM records."""

    queryset = models.SoftwareImageLCM.objects.prefetch_related("software")
    serializer_class = serializers.SoftwareImageLCMSerializer
    filterset_class = filters.SoftwareImageLCMFilterSet


class ValidatedSoftwareLCMViewSet(NautobotModelViewSet):
    """REST API viewset for ValidatedSoftwareLCM records."""

    queryset = models.ValidatedSoftwareLCM.objects.all()
    serializer_class = serializers.ValidatedSoftwareLCMSerializer
    filterset_class = filters.ValidatedSoftwareLCMFilterSet


class CVELCMViewSet(NautobotModelViewSet):
    """REST API viewset for CVELCM records."""

    queryset = models.CVELCM.objects.all()
    serializer_class = serializers.CVELCMSerializer
    filterset_class = filters.CVELCMFilterSet


class VulnerabilityLCMViewSet(NautobotModelViewSet):
    """REST API viewset for VulnerabilityLCM records."""

    queryset = models.VulnerabilityLCM.objects.all()
    serializer_class = serializers.VulnerabilityLCMSerializer
    filterset_class = filters.VulnerabilityLCMFilterSet

    # Disabling POST as these should only be created via Job.
    http_method_names = ["get", "put", "patch", "delete", "head", "options"]


class DeviceHardwareNoticeResultListViewSet(NautobotModelViewSet):
    """REST API viewset for DeviceHardwareNoticeResult records."""

    queryset = models.DeviceHardwareNoticeResult.objects.all()
    serializer_class = serializers.DeviceHardwareNoticeResultSerializer
    filterset_class = filters.DeviceHardwareNoticeResultFilterSet

    # Disabling POST as these should only be created via Job.
    http_method_names = ["get", "head", "options"]


class DeviceSoftwareValidationResultListViewSet(NautobotModelViewSet):
    """REST API viewset for DeviceSoftwareValidationResult records."""

    queryset = models.DeviceSoftwareValidationResult.objects.all()
    serializer_class = serializers.DeviceSoftwareValidationResultSerializer
    filterset_class = filters.DeviceSoftwareValidationResultFilterSet

    # Disabling POST as these should only be created via Job.
    http_method_names = ["get", "head", "options"]


class InventoryItemSoftwareValidationResultListViewSet(NautobotModelViewSet):
    """REST API viewset for DeviceSoftwareValidationResult records."""

    queryset = models.InventoryItemSoftwareValidationResult.objects.all()
    serializer_class = serializers.InventoryItemSoftwareValidationResultSerializer
    filterset_class = filters.InventoryItemSoftwareValidationResultFilterSet

    # Disabling POST as these should only be created via Job.
    http_method_names = ["get", "head", "options"]

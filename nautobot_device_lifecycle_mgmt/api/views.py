"""API Views implementation for the Lifecycle Management plugin."""

from nautobot.core.api.views import ModelViewSet
from nautobot.extras.api.views import CustomFieldModelViewSet

from nautobot_device_lifecycle_mgmt.models import (
    HardwareLCM,
    ContractLCM,
    ProviderLCM,
    ContactLCM,
    SoftwareImageLCM,
    SoftwareLCM,
    ValidatedSoftwareLCM,
    CVELCM,
    VulnerabilityLCM,
)
from nautobot_device_lifecycle_mgmt.filters import (
    HardwareLCMFilterSet,
    ContractLCMFilterSet,
    ProviderLCMFilterSet,
    ContactLCMFilterSet,
    SoftwareImageLCMFilterSet,
    SoftwareLCMFilterSet,
    ValidatedSoftwareLCMFilterSet,
    CVELCMFilterSet,
    VulnerabilityLCMFilterSet,
)

from .serializers import (
    HardwareLCMSerializer,
    ContractLCMSerializer,
    ProviderLCMSerializer,
    ContactLCMSerializer,
    SoftwareImageLCMSerializer,
    SoftwareLCMSerializer,
    ValidatedSoftwareLCMSerializer,
    CVELCMSerializer,
    VulnerabilityLCMSerializer,
)


class HardwareLCMView(ModelViewSet):
    """CRUD operations set for the Hardware Lifecycle Management view."""

    queryset = HardwareLCM.objects.all()
    filterset_class = HardwareLCMFilterSet
    serializer_class = HardwareLCMSerializer


class ContractLCMView(ModelViewSet):
    """CRUD operations set for the Contract Lifecycle Management view."""

    queryset = ContractLCM.objects.all()
    filterset_class = ContractLCMFilterSet
    serializer_class = ContractLCMSerializer


class ProviderLCMView(ModelViewSet):
    """CRUD operations set for the Contract Provider Lifecycle Management view."""

    queryset = ProviderLCM.objects.all()
    filterset_class = ProviderLCMFilterSet
    serializer_class = ProviderLCMSerializer


class ContactLCMView(ModelViewSet):
    """CRUD operations set for the Contact Lifecycle Management view."""

    queryset = ContactLCM.objects.all()
    filterset_class = ContactLCMFilterSet
    serializer_class = ContactLCMSerializer


class SoftwareLCMViewSet(CustomFieldModelViewSet):
    """REST API viewset for SoftwareLCM records."""

    queryset = SoftwareLCM.objects.prefetch_related("software_images")
    serializer_class = SoftwareLCMSerializer
    filterset_class = SoftwareLCMFilterSet


class SoftwareImageLCMViewSet(CustomFieldModelViewSet):
    """REST API viewset for SoftwareImageLCM records."""

    queryset = SoftwareImageLCM.objects.prefetch_related("software")
    serializer_class = SoftwareImageLCMSerializer
    filterset_class = SoftwareImageLCMFilterSet


class ValidatedSoftwareLCMViewSet(CustomFieldModelViewSet):
    """REST API viewset for ValidatedSoftwareLCM records."""

    queryset = ValidatedSoftwareLCM.objects.all()
    serializer_class = ValidatedSoftwareLCMSerializer
    filterset_class = ValidatedSoftwareLCMFilterSet


class CVELCMViewSet(CustomFieldModelViewSet):
    """REST API viewset for CVELCM records."""

    queryset = CVELCM.objects.all()
    serializer_class = CVELCMSerializer
    filterset_class = CVELCMFilterSet


class VulnerabilityLCMViewSet(CustomFieldModelViewSet):
    """REST API viewset for VulnerabilityLCM records."""

    queryset = VulnerabilityLCM.objects.all()
    serializer_class = VulnerabilityLCMSerializer
    filterset_class = VulnerabilityLCMFilterSet

    # Disabling POST as these should only be created via Job.
    http_method_names = ["get", "put", "patch", "delete", "head", "options"]

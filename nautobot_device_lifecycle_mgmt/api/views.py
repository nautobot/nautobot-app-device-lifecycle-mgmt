"""API Views implementation for the LifeCycle Management plugin."""

from nautobot.core.api.views import ModelViewSet
from nautobot.extras.api.views import CustomFieldModelViewSet

from nautobot_device_lifecycle_mgmt.models import (
    HardwareLCM,
    ContractLCM,
    ProviderLCM,
    ContactLCM,
    SoftwareLCM,
    ValidatedSoftwareLCM,
)
from nautobot_device_lifecycle_mgmt.filters import (
    HardwareLCMFilterSet,
    ContractLCMFilterSet,
    ProviderLCMFilterSet,
    ContactLCMFilterSet,
    SoftwareLCMFilterSet,
    ValidatedSoftwareLCMFilterSet,
)

from .serializers import (
    HardwareLCMSerializer,
    ContractLCMSerializer,
    ProviderLCMSerializer,
    ContactLCMSerializer,
    SoftwareLCMSerializer,
    ValidatedSoftwareLCMSerializer,
)


class HardwareLCMView(ModelViewSet):  # pylint: disable=too-many-ancestors
    """CRUD operations set for the Hardware LifeCycle Management view."""

    queryset = HardwareLCM.objects.all()
    filterset_class = HardwareLCMFilterSet
    serializer_class = HardwareLCMSerializer


class ContractLCMView(ModelViewSet):  # pylint: disable=too-many-ancestors
    """CRUD operations set for the Contract LifeCycle Management view."""

    queryset = ContractLCM.objects.all()
    filterset_class = ContractLCMFilterSet
    serializer_class = ContractLCMSerializer


class ProviderLCMView(ModelViewSet):  # pylint: disable=too-many-ancestors
    """CRUD operations set for the Contract Provider LifeCycle Management view."""

    queryset = ProviderLCM.objects.all()
    filterset_class = ProviderLCMFilterSet
    serializer_class = ProviderLCMSerializer


class ContactLCMView(ModelViewSet):  # pylint: disable=too-many-ancestors
    """CRUD operations set for the Contact LifeCycle Management view."""

    queryset = ContactLCM.objects.all()
    filterset_class = ContactLCMFilterSet
    serializer_class = ContactLCMSerializer


class SoftwareLCMViewSet(CustomFieldModelViewSet):  # pylint: disable=too-many-ancestors
    """REST API viewset for SoftwareLCM records."""

    queryset = SoftwareLCM.objects.all()
    serializer_class = SoftwareLCMSerializer
    filterset_class = SoftwareLCMFilterSet


class ValidatedSoftwareLCMViewSet(CustomFieldModelViewSet):  # pylint: disable=too-many-ancestors
    """REST API viewset for ValidatedSoftwareLCM records."""

    queryset = ValidatedSoftwareLCM.objects.all()
    serializer_class = ValidatedSoftwareLCMSerializer
    filterset_class = ValidatedSoftwareLCMFilterSet

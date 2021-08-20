"""API Views implementation for the LifeCycle Management plugin."""

from nautobot.core.api.views import ModelViewSet
from nautobot.extras.api.views import CustomFieldModelViewSet

from nautobot_device_lifecycle_mgmt.models import HardwareLCM, SoftwareLCM, ValidatedSoftwareLCM
from nautobot_device_lifecycle_mgmt.filters import (
    HardwareLCMFilterSet,
    SoftwareLCMFilterSet,
    ValidatedSoftwareLCMFilterSet,
)

from .serializers import HardwareLCMSerializer, SoftwareLCMSerializer, ValidatedSoftwareLCMSerializer


class HardwareLCMView(ModelViewSet):  # pylint: disable=too-many-ancestors
    """CRUD operations set for the Hardware LifeCycle Management view."""

    queryset = HardwareLCM.objects.all()
    filterset_class = HardwareLCMFilterSet
    serializer_class = HardwareLCMSerializer


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

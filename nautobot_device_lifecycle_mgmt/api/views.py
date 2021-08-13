"""API Views implementation for the LifeCycle Management plugin."""

from nautobot.core.api.views import ModelViewSet

from nautobot_device_lifecycle_mgmt.models import HardwareLCM
from nautobot_device_lifecycle_mgmt.filters import HardwareLCMFilterSet

from .serializers import HardwareLCMSerializer


class HardwareLCMView(ModelViewSet):  # pylint: disable=too-many-ancestors
    """CRUD operations set for the Hardware LifeCycle Management view."""

    queryset = HardwareLCM.objects.all()
    filterset_class = HardwareLCMFilterSet
    serializer_class = HardwareLCMSerializer

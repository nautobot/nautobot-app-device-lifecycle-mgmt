"""API Views implementation for the LifeCycle Management plugin."""

from nautobot.core.api.views import ModelViewSet

from nautobot_plugin_device_lifecycle_mgmt.models import HardwareLCM
from nautobot_plugin_device_lifecycle_mgmt.filters import HardwareLCMFilter

from .serializers import HardwareLCMSerializer


class HardwareLCMView(ModelViewSet):  # pylint: disable=too-many-ancestors
    """CRUD operations set for the Hardware LifeCycle Management view."""

    queryset = HardwareLCM.objects.all()
    filterset_class = HardwareLCMFilter
    serializer_class = HardwareLCMSerializer

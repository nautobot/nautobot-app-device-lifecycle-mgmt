"""API Views for nautobot_plugin_device_lifecycle_mgmt."""

from nautobot.core.api.views import ModelViewSet

from nautobot_plugin_device_lifecycle_mgmt.models import HardwareLCM
from nautobot_plugin_device_lifecycle_mgmt.filters import HardwareLCMNoticeFilter

from .serializers import HardwareLCMNoticeSerializer


class HardwareLCMNoticeView(ModelViewSet):  # pylint: disable=too-many-ancestors
    """CRUD operations set for HardwareLCMNotice view."""

    queryset = HardwareLCM.objects.all()
    filterset_class = HardwareLCMNoticeFilter
    serializer_class = HardwareLCMNoticeSerializer

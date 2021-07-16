"""API Views for nautobot_plugin_device_lifecycle_mgmt."""

from nautobot.core.api.views import ModelViewSet

from nautobot_plugin_device_lifecycle_mgmt.models import EoxNotice
from nautobot_plugin_device_lifecycle_mgmt.filters import EoxNoticeFilter

from .serializers import EoxNoticeSerializer


class EoxNoticeView(ModelViewSet):
    """CRUD operations set for EoxNotice view."""

    queryset = EoxNotice.objects.all()
    filterset_class = EoxNoticeFilter
    serializer_class = EoxNoticeSerializer

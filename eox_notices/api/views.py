"""API Views for eox_notices."""

from nautobot.core.api.views import ModelViewSet

from eox_notices.models import EoxNotice
from eox_notices.filters import EoxNoticeFilter

from .serializers import EoxNoticeSerializer


class EoxNoticeView(ModelViewSet):
    """CRUD operations set for EoxNotice view."""

    queryset = EoxNotice.objects.all()
    filterset_class = EoxNoticeFilter
    serializer_class = EoxNoticeSerializer

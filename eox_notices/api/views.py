"""API Views for eox_notices."""

from rest_framework import mixins, viewsets

from eox_notices.models import EoxNotice
from eox_notices.filters import EoxNoticeFilter

from .serializers import EoxNoticeSerializer


class EoxNoticeView(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """CRUD operations set for EoxNotice view."""

    queryset = EoxNotice.objects.all()
    filterset_class = EoxNoticeFilter
    serializer_class = EoxNoticeSerializer

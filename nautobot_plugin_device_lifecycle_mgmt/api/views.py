"""API Views for nautobot_plugin_device_lifecycle_mgmt."""

from nautobot.core.api.views import ModelViewSet
from nautobot.extras.api.views import CustomFieldModelViewSet

from nautobot_plugin_device_lifecycle_mgmt.models import EoxNotice, SoftwareLCM, ValidatedSoftwareLCM
from nautobot_plugin_device_lifecycle_mgmt.filters import (
    EoxNoticeFilter,
    SoftwareLCMFilterSet,
    ValidatedSoftwareLCMFilterSet,
)

from .serializers import EoxNoticeSerializer, SoftwareLCMSerializer, ValidatedSoftwareLCMSerializer


class EoxNoticeView(ModelViewSet):  # pylint: disable=too-many-ancestors
    """CRUD operations set for EoxNotice view."""

    queryset = EoxNotice.objects.all()
    filterset_class = EoxNoticeFilter
    serializer_class = EoxNoticeSerializer


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

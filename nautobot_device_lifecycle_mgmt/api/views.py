<<<<<<< HEAD
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
=======
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
>>>>>>> c9c3a9d (Rename plugin)

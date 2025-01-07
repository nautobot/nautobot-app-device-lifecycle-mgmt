"""API views for nautobot_device_lifecycle_mgmt."""

from nautobot.apps.api import NautobotModelViewSet

from nautobot_device_lifecycle_mgmt import filters, models
from nautobot_device_lifecycle_mgmt.api import serializers


class HardwareLCMViewSet(NautobotModelViewSet):  # pylint: disable=too-many-ancestors
    """HardwareLCM viewset."""

    queryset = models.HardwareLCM.objects.all()
    serializer_class = serializers.HardwareLCMSerializer
    filterset_class = filters.HardwareLCMFilterSet

    # Option for modifying the default HTTP methods:
    # http_method_names = ["get", "post", "put", "patch", "delete", "head", "options", "trace"]

"""API serializers for nautobot_device_lifecycle_mgmt."""

from nautobot.apps.api import NautobotModelSerializer, TaggedModelSerializerMixin

from nautobot_device_lifecycle_mgmt import models


class HardwareLCMSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):  # pylint: disable=too-many-ancestors
    """HardwareLCM Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.HardwareLCM
        fields = "__all__"

        # Option for disabling write for certain fields:
        # read_only_fields = []

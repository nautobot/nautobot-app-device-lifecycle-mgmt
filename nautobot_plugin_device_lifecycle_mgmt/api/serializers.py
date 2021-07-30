"""API serializers for nautobot_plugin_device_lifecycle_mgmt."""

from nautobot.core.api.serializers import ValidatedModelSerializer

from nautobot.dcim.api.nested_serializers import NestedDeviceSerializer, NestedDeviceTypeSerializer

from nautobot_plugin_device_lifecycle_mgmt.models import EoxNotice


class EoxNoticeSerializer(ValidatedModelSerializer):
    """API serializer."""

    device_type = NestedDeviceTypeSerializer(
        many=False, read_only=False, required=True, help_text="Device Type to attach EoX Notice to"
    )
    devices = NestedDeviceSerializer(many=True, read_only=True, required=False, help_text="Devices tied to Device Type")

    class Meta:
        """Meta attributes."""

        model = EoxNotice
        fields = [
            "id",
            "expired",
            "devices",
        ] + EoxNotice.csv_headers

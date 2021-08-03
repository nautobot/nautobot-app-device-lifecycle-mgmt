"""API serializers for nautobot_plugin_device_lifecycle_mgmt."""

from nautobot.core.api.serializers import ValidatedModelSerializer

from nautobot.dcim.api.nested_serializers import NestedDeviceSerializer, NestedDeviceTypeSerializer

from nautobot_plugin_device_lifecycle_mgmt.models import HardwareLCM


class HardwareLCMNoticeSerializer(ValidatedModelSerializer):
    """API serializer."""

    device_type = NestedDeviceTypeSerializer(
        many=False, read_only=False, required=True, help_text="Device Type to attach Hardware LCM Notice to"
    )
    devices = NestedDeviceSerializer(many=True, read_only=True, required=False, help_text="Devices tied to Device Type")

    class Meta:
        """Meta attributes."""

        model = HardwareLCM
        fields = [
            "id",
            "expired",
            "devices",
            "device_type",
            "release_date",
            "end_of_sale",
            "end_of_support",
            "end_of_sw_releases",
            "end_of_security_patches",
            "documentation_url",
        ]

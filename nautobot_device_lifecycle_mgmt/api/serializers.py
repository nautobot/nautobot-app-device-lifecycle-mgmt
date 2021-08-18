"""API serializers implementation for the LifeCycle Management plugin."""

from nautobot.core.api.serializers import ValidatedModelSerializer

from nautobot.dcim.api.nested_serializers import NestedDeviceSerializer, NestedDeviceTypeSerializer

from nautobot_device_lifecycle_mgmt.models import HardwareLCM


class HardwareLCMSerializer(ValidatedModelSerializer):
    """API serializer."""

    device_type = NestedDeviceTypeSerializer(
        many=False, read_only=False, required=True, help_text="Device Type to attach the Hardware LCM to"
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
            "inventory_item",
            "release_date",
            "end_of_sale",
            "end_of_support",
            "end_of_sw_releases",
            "end_of_security_patches",
            "documentation_url",
        ]

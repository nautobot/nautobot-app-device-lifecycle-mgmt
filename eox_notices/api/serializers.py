"""API serializers for eox_notices."""

from rest_framework import serializers

from nautobot.dcim.api.nested_serializers import NestedDeviceSerializer, NestedDeviceTypeSerializer

from eox_notices.models import EoxNotice


class EoxNoticeSerializer(serializers.ModelSerializer):
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
            "devices",
            "device_type",
            "end_of_sale",
            "end_of_support",
            "end_of_sw_releases",
            "end_of_security_patches",
            "notice_url",
        ]

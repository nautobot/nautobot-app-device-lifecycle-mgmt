"""API serializers implementation for the LifeCycle Management plugin."""

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from nautobot.core.api import ContentTypeField
from nautobot.core.api.serializers import ValidatedModelSerializer

from nautobot.dcim.api.nested_serializers import (
    NestedDeviceSerializer,
    NestedDeviceTypeSerializer,
    NestedPlatformSerializer,
)
from nautobot.extras.api.customfields import CustomFieldModelSerializer
from nautobot.extras.api.serializers import TaggedObjectSerializer
from nautobot.utilities.api import get_serializer_for_model

from nautobot_device_lifecycle_mgmt.models import HardwareLCM, SoftwareLCM, ValidatedSoftwareLCM

from .nested_serializers import NestedSoftwareLCMSerializer


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


class SoftwareLCMSerializer(CustomFieldModelSerializer, TaggedObjectSerializer):  # pylint: disable=too-many-ancestors
    """REST API serializer for SoftwareLCM records."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_plugin_device_lifecycle_mgmt-api:softwarelcm-detail"
    )
    device_platform = NestedPlatformSerializer(required=False, read_only=True)

    class Meta:
        model = SoftwareLCM
        fields = [
            "id",
            "url",
            "device_platform",
            "version",
            "alias",
            "end_of_support",
            "documentation_url",
            "download_url",
            "image_file_name",
            "image_file_checksum",
            "long_term_support",
            "pre_release",
        ]


class ValidatedSoftwareLCMSerializer(CustomFieldModelSerializer, TaggedObjectSerializer):  # pylint: disable=too-many-ancestors
    """REST API serializer for ValidatedSoftwareLCM records."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_plugin_device_lifecycle_mgmt-api:validatedsoftwarelcm-detail"
    )
    softwarelcm = NestedSoftwareLCMSerializer()

    assigned_to_content_type = ContentTypeField(
        queryset=ContentType.objects.filter(
            Q(
                app_label="dcim",
                model__in=(
                    "device",
                    "device_type",
                    "inventory_item",
                ),
            )
        ),
    )
    assigned_to = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ValidatedSoftwareLCM
        fields = [
            "id",
            "url",
            "softwarelcm",
            "assigned_to_content_type",
            "assigned_to_object_id",
            "assigned_to",
            "start",
            "end",
            "primary",
        ]

    @swagger_serializer_method(serializer_or_field=serializers.DictField)
    def get_assigned_to(self, obj):
        """Serializer method for 'assigned_to' GenericForeignKey field."""
        if obj.assigned_to is None:
            return None
        serializer = get_serializer_for_model(obj.assigned_to, prefix="Nested")
        context = {"request": self.context["request"]}
        return serializer(obj.assigned_to, context=context).data

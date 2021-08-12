"""Nested/brief alternate REST API serializers for nautobot_plugin_device_lifecycle_mgmt models."""

from rest_framework import serializers

from nautobot.core.api import WritableNestedSerializer

from nautobot_plugin_device_lifecycle_mgmt import models


class NestedSoftwareLCMSerializer(WritableNestedSerializer):
    """Nested/brief serializer for SoftwareLCM."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_plugin_device_lifecycle_mgmt-api:softwarelcm-detail"
    )

    class Meta:
        model = models.SoftwareLCM
        fields = ["id", "url", "device_platform", "version", "end_of_support"]

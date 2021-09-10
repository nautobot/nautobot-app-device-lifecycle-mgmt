"""Nested/brief alternate REST API serializers for nautobot_device_lifecycle_mgmt models."""

from rest_framework import serializers

from nautobot.core.api import WritableNestedSerializer

from nautobot_device_lifecycle_mgmt import models


class NestedSoftwareLCMSerializer(WritableNestedSerializer):
    """Nested/brief serializer for SoftwareLCM."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_device_lifecycle_mgmt-api:softwarelcm-detail"
    )

    class Meta:
        """Meta attributes."""

        model = models.SoftwareLCM
        fields = ["id", "url", "device_platform", "version", "end_of_support"]
        read_only_fields = ["device_platform"]


class NestedProviderLCMSerializer(WritableNestedSerializer):
    """Nested serializer for the provider class."""

    class Meta:
        """Meta magic method for the Provider nested serializer."""

        model = models.ProviderLCM
        fields = [
            "id",
            "name",
            "description",
            "physical_address",
            "phone",
            "email",
            "comments",
        ]


class NestedContractLCMSerializer(WritableNestedSerializer):
    """API serializer."""

    provider = NestedProviderLCMSerializer(many=False, read_only=False, required=True, help_text="Contract Provider")

    class Meta:
        """Meta attributes."""

        model = models.ContractLCM
        fields = [
            "id",
            "provider",
            "name",
            "start",
            "end",
            "cost",
            "support_level",
            "contract_type",
            "expired",
        ]

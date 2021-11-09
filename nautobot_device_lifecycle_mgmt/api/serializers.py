"""API serializers implementation for the LifeCycle Management plugin."""
from rest_framework import serializers

from nautobot.dcim.api.nested_serializers import (
    NestedDeviceSerializer,
    NestedDeviceTypeSerializer,
    NestedPlatformSerializer,
)
from nautobot.extras.api.customfields import CustomFieldModelSerializer
from nautobot.extras.api.serializers import TaggedObjectSerializer

from nautobot_device_lifecycle_mgmt.models import (
    HardwareLCM,
    SoftwareLCM,
    ContactLCM,
    ValidatedSoftwareLCM,
    ContractLCM,
    ProviderLCM,
)

from .nested_serializers import (
    NestedSoftwareLCMSerializer,
    NestedProviderLCMSerializer,
    NestedContractLCMSerializer,
)


class HardwareLCMSerializer(CustomFieldModelSerializer, TaggedObjectSerializer):  # pylint: disable=R0901
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
            "custom_fields",
            "tags",
        ]


class ProviderLCMSerializer(CustomFieldModelSerializer, TaggedObjectSerializer):  # pylint: disable=R0901
    """API serializer."""

    class Meta:
        """Meta attributes."""

        model = ProviderLCM
        fields = [
            "id",
            "name",
            "description",
            "physical_address",
            "phone",
            "email",
            "comments",
            "custom_fields",
            "tags",
        ]


class ContractLCMSerializer(CustomFieldModelSerializer, TaggedObjectSerializer):  # pylint: disable=R0901
    """API serializer."""

    provider = NestedProviderLCMSerializer(many=False, read_only=False, required=True, help_text="Vendor")

    class Meta:
        """Meta attributes."""

        model = ContractLCM
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
            "custom_fields",
            "tags",
        ]


class ContactLCMSerializer(CustomFieldModelSerializer, TaggedObjectSerializer):  # pylint: disable=R0901
    """API serializer."""

    contract = NestedContractLCMSerializer(many=False, read_only=False, required=True, help_text="Associated Contract")

    class Meta:
        """Meta attributes."""

        model = ContactLCM
        fields = [
            "name",
            "address",
            "phone",
            "email",
            "comments",
            "priority",
            "contract",
            "custom_fields",
            "tags",
        ]


class SoftwareLCMSerializer(CustomFieldModelSerializer, TaggedObjectSerializer):  # pylint: disable=too-many-ancestors
    """REST API serializer for SoftwareLCM records."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_device_lifecycle_mgmt-api:softwarelcm-detail"
    )
    device_platform = NestedPlatformSerializer()

    class Meta:
        """Meta attributes."""

        model = SoftwareLCM
        fields = [
            "id",
            "url",
            "device_platform",
            "version",
            "alias",
            "release_date",
            "end_of_support",
            "documentation_url",
            "download_url",
            "image_file_name",
            "image_file_checksum",
            "long_term_support",
            "pre_release",
            "custom_fields",
            "tags",
        ]


class ValidatedSoftwareLCMSerializer(
    CustomFieldModelSerializer, TaggedObjectSerializer
):  # pylint: disable=too-many-ancestors
    """REST API serializer for ValidatedSoftwareLCM records."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_device_lifecycle_mgmt-api:validatedsoftwarelcm-detail"
    )
    software = NestedSoftwareLCMSerializer()

    class Meta:
        """Meta attributes."""

        model = ValidatedSoftwareLCM
        fields = [
            "id",
            "url",
            "software",
            "devices",
            "device_types",
            "device_roles",
            "inventory_items",
            "object_tags",
            "start",
            "end",
            "preferred",
            "valid",
            "custom_fields",
            "tags",
        ]

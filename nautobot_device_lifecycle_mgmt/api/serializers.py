"""API serializers implementation for the LifeCycle Management plugin."""
from nautobot.core.api import ChoiceField, SerializedPKRelatedField
from nautobot.dcim.api.nested_serializers import (
    NestedDeviceSerializer,
    NestedDeviceTypeSerializer,
    NestedInventoryItemSerializer,
    NestedPlatformSerializer,
)
from nautobot.extras.api.customfields import CustomFieldModelSerializer
from nautobot.extras.api.serializers import (
    StatusModelSerializerMixin,
    StatusSerializerField,
    TaggedObjectSerializer,
)
from rest_framework import serializers

# Nautobot 1.4 introduced RelationshipModelSerializerMixin
# TODO: Remove this once plugin drops support for Nautobot < 1.4
try:
    from nautobot.extras.api.relationships import RelationshipModelSerializerMixin  # pylint: disable=ungrouped-imports

    serializer_base_classes = [
        RelationshipModelSerializerMixin,
        TaggedObjectSerializer,
        CustomFieldModelSerializer,
    ]  # pylint: disable=invalid-name
except ImportError:
    serializer_base_classes = [TaggedObjectSerializer, CustomFieldModelSerializer]  # pylint: disable=invalid-name

from nautobot.extras.models import Status

from nautobot_device_lifecycle_mgmt import choices
from nautobot_device_lifecycle_mgmt.models import (
    CVELCM,
    ContactLCM,
    ContractLCM,
    HardwareLCM,
    ProviderLCM,
    SoftwareImageLCM,
    SoftwareLCM,
    ValidatedSoftwareLCM,
    VulnerabilityLCM,
)

from .nested_serializers import (
    NestedContractLCMSerializer,
    NestedCVELCMSerializer,
    NestedProviderLCMSerializer,
    NestedSoftwareImageLCMSerializer,
    NestedSoftwareLCMSerializer,
)


class HardwareLCMSerializer(*serializer_base_classes):  # pylint: disable=R0901,too-few-public-methods
    """API serializer."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_device_lifecycle_mgmt-api:hardwarelcm-detail"
    )
    device_type = NestedDeviceTypeSerializer(
        many=False, read_only=False, required=True, help_text="Device Type to attach the Hardware LCM to"
    )
    devices = NestedDeviceSerializer(many=True, read_only=True, required=False, help_text="Devices tied to Device Type")

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta attributes."""

        model = HardwareLCM
        fields = [
            "url",
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


class ProviderLCMSerializer(*serializer_base_classes):  # pylint: disable=R0901,too-few-public-methods
    """API serializer."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_device_lifecycle_mgmt-api:providerlcm-detail"
    )

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta attributes."""

        model = ProviderLCM
        fields = [
            "url",
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


class ContractLCMSerializer(*serializer_base_classes):  # pylint: disable=R0901,too-few-public-methods
    """API serializer."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_device_lifecycle_mgmt-api:contractlcm-detail"
    )
    provider = NestedProviderLCMSerializer(many=False, read_only=False, required=True, help_text="Vendor")

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta attributes."""

        model = ContractLCM
        fields = [
            "url",
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


class ContactLCMSerializer(*serializer_base_classes):  # pylint: disable=R0901,too-few-public-methods
    """API serializer."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_device_lifecycle_mgmt-api:contactlcm-detail"
    )
    contract = NestedContractLCMSerializer(many=False, read_only=False, required=True, help_text="Associated Contract")

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta attributes."""

        model = ContactLCM
        fields = [
            "url",
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


class SoftwareLCMSerializer(*serializer_base_classes):  # pylint: disable=too-few-public-methods
    """REST API serializer for SoftwareLCM records."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_device_lifecycle_mgmt-api:softwarelcm-detail"
    )
    device_platform = NestedPlatformSerializer()
    software_images = SerializedPKRelatedField(
        queryset=SoftwareImageLCM.objects.all(),
        serializer=NestedSoftwareImageLCMSerializer,
        required=False,
        many=True,
    )

    class Meta:  # pylint: disable=too-few-public-methods
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
            "software_images",
            "long_term_support",
            "pre_release",
            "custom_fields",
            "tags",
        ]


class SoftwareImageLCMSerializer(*serializer_base_classes):  # pylint: disable=too-few-public-methods
    """REST API serializer for SoftwareImageLCM records."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_device_lifecycle_mgmt-api:softwareimagelcm-detail"
    )
    software = NestedSoftwareLCMSerializer()

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta attributes."""

        model = SoftwareImageLCM
        fields = [
            "id",
            "url",
            "image_file_name",
            "software",
            "device_types",
            "inventory_items",
            "object_tags",
            "download_url",
            "image_file_checksum",
            "default_image",
            "custom_fields",
            "tags",
        ]


class ValidatedSoftwareLCMSerializer(*serializer_base_classes):  # pylint: disable=too-few-public-methods
    """REST API serializer for ValidatedSoftwareLCM records."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_device_lifecycle_mgmt-api:validatedsoftwarelcm-detail"
    )
    software = NestedSoftwareLCMSerializer()

    class Meta:  # pylint: disable=too-few-public-methods
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


class CVELCMSerializer(*serializer_base_classes, StatusModelSerializerMixin):  # pylint: disable=abstract-method
    """REST API serializer for CVELCM records."""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:nautobot_device_lifecycle_mgmt-api:cvelcm-detail")
    status = StatusSerializerField(required=False, queryset=Status.objects.all())
    severity = ChoiceField(choices=choices.CVESeverityChoices, required=False)

    class Meta:
        """Meta attributes."""

        model = CVELCM
        fields = [
            "id",
            "url",
            "name",
            "published_date",
            "link",
            "status",
            "description",
            "severity",
            "cvss",
            "cvss_v2",
            "cvss_v3",
            "fix",
            "comments",
            "custom_fields",
            "tags",
        ]


class VulnerabilityLCMSerializer(
    *serializer_base_classes, StatusModelSerializerMixin
):  # pylint: disable=abstract-method
    """REST API serializer for VulnerabilityLCM records."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_device_lifecycle_mgmt-api:vulnerabilitylcm-detail"
    )
    cve = NestedCVELCMSerializer(read_only=True)
    software = NestedSoftwareLCMSerializer(read_only=True)
    device = NestedDeviceSerializer(read_only=True)
    inventory_item = NestedInventoryItemSerializer(read_only=True)

    class Meta:
        """Meta attributes."""

        model = VulnerabilityLCM
        fields = [
            "id",
            "display",
            "url",
            "cve",
            "software",
            "device",
            "inventory_item",
            "status",
            "custom_fields",
            "tags",
        ]
        read_only_fields = [
            "id",
            "display",
            "url",
            "cve",
            "software",
            "device",
            "inventory_item",
        ]

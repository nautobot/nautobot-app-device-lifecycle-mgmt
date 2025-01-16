"""API serializers implementation for the LifeCycle Management app."""

from nautobot.apps.api import NautobotModelSerializer, TaggedModelSerializerMixin

from nautobot_device_lifecycle_mgmt.models import (
    CVELCM,
    ContractLCM,
    DeviceHardwareNoticeResult,
    DeviceSoftwareValidationResult,
    HardwareLCM,
    InventoryItemSoftwareValidationResult,
    ProviderLCM,
    SoftwareNotice,
    ValidatedSoftwareLCM,
    VulnerabilityLCM,
)


class HardwareLCMSerializer(NautobotModelSerializer):  # pylint: disable=R0901,too-few-public-methods
    """API serializer."""

    class Meta:
        """Meta attributes."""

        model = HardwareLCM
        fields = "__all__"


class SoftwareNoticeSerializer(NautobotModelSerializer):  # pylint: disable=R0901,too-few-public-methods
    """SoftwareNotice API serializer."""

    class Meta:
        """Meta attributes."""

        model = SoftwareNotice
        fields = "__all__"


class ProviderLCMSerializer(NautobotModelSerializer):  # pylint: disable=R0901,too-few-public-methods
    """API serializer."""

    class Meta:
        """Meta attributes."""

        model = ProviderLCM
        fields = "__all__"


class ContractLCMSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):  # pylint: disable=R0901,too-few-public-methods
    """API serializer."""

    class Meta:
        """Meta attributes."""

        model = ContractLCM
        fields = "__all__"


class ValidatedSoftwareLCMSerializer(NautobotModelSerializer):
    """REST API serializer for ValidatedSoftwareLCM records."""

    class Meta:
        """Meta attributes."""

        model = ValidatedSoftwareLCM
        fields = "__all__"


class CVELCMSerializer(NautobotModelSerializer):  # pylint: disable=abstract-method,too-few-public-methods
    """REST API serializer for CVELCM records."""

    class Meta:
        """Meta attributes."""

        model = CVELCM
        fields = "__all__"


class VulnerabilityLCMSerializer(NautobotModelSerializer):  # pylint: disable=abstract-method,too-few-public-methods
    """REST API serializer for VulnerabilityLCM records."""

    class Meta:
        """Meta attributes."""

        model = VulnerabilityLCM
        fields = "__all__"
        read_only_fields = [
            "id",
            "display",
            "url",
            "cve",
            "software",
            "device",
            "inventory_item",
        ]


class DeviceSoftwareValidationResultSerializer(NautobotModelSerializer):
    """REST API serializer for DeviceSoftwareValidationResult records."""

    class Meta:
        """Meta attributes."""

        model = DeviceSoftwareValidationResult
        fields = "__all__"


class DeviceHardwareNoticeResultSerializer(NautobotModelSerializer):
    """REST API serializer for DeviceHardwareNoticeResult records."""

    class Meta:
        """Meta attributes."""

        model = DeviceHardwareNoticeResult
        fields = "__all__"


class InventoryItemSoftwareValidationResultSerializer(NautobotModelSerializer):
    """REST API serializer for InventoryItemSoftwareValidationResult records."""

    class Meta:
        """Meta attributes."""

        model = InventoryItemSoftwareValidationResult
        fields = "__all__"

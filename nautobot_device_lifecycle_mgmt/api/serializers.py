"""API serializers implementation for the LifeCycle Management app."""
from nautobot.apps.api import NautobotModelSerializer

from nautobot_device_lifecycle_mgmt.models import (
    CVELCM,
    ContactLCM,
    ContractLCM,
    DeviceSoftwareValidationResult,
    HardwareLCM,
    InventoryItemSoftwareValidationResult,
    ProviderLCM,
    SoftwareImageLCM,
    SoftwareLCM,
    ValidatedSoftwareLCM,
    VulnerabilityLCM,
)


class HardwareLCMSerializer(NautobotModelSerializer):  # pylint: disable=R0901,too-few-public-methods
    """API serializer."""

    class Meta:
        """Meta attributes."""

        model = HardwareLCM
        fields = "__all__"


class ProviderLCMSerializer(NautobotModelSerializer):  # pylint: disable=R0901,too-few-public-methods
    """API serializer."""

    class Meta:
        """Meta attributes."""

        model = ProviderLCM
        fields = "__all__"


class ContractLCMSerializer(NautobotModelSerializer):  # pylint: disable=R0901,too-few-public-methods
    """API serializer."""

    class Meta:
        """Meta attributes."""

        model = ContractLCM
        fields = "__all__"


class ContactLCMSerializer(NautobotModelSerializer):  # pylint: disable=R0901,too-few-public-methods
    """API serializer."""

    class Meta:
        """Meta attributes."""

        model = ContactLCM
        fields = "__all__"


class SoftwareLCMSerializer(NautobotModelSerializer):
    """REST API serializer for SoftwareLCM records."""

    class Meta:
        """Meta attributes."""

        model = SoftwareLCM
        fields = "__all__"


class SoftwareImageLCMSerializer(NautobotModelSerializer):
    """REST API serializer for SoftwareImageLCM records."""

    class Meta:
        """Meta attributes."""

        model = SoftwareImageLCM
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


class InventoryItemSoftwareValidationResultSerializer(NautobotModelSerializer):
    """REST API serializer for InventoryItemSoftwareValidationResult records."""

    class Meta:
        """Meta attributes."""

        model = InventoryItemSoftwareValidationResult
        fields = "__all__"

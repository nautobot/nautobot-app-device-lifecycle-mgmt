"""API serializers implementation for the LifeCycle Management plugin."""
from nautobot.core.api import ChoiceField, SerializedPKRelatedField
from nautobot.apps.api import NautobotModelSerializer
from nautobot.extras.models import Status
from rest_framework import serializers

from nautobot_device_lifecycle_mgmt import choices
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

    # url = serializers.HyperlinkedIdentityField(
    #     view_name="plugins-api:nautobot_device_lifecycle_mgmt-api:hardwarelcm-detail"
    # )

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta attributes."""

        model = HardwareLCM
        fields = "__all__"


class ProviderLCMSerializer(NautobotModelSerializer):  # pylint: disable=R0901,too-few-public-methods
    """API serializer."""

    # url = serializers.HyperlinkedIdentityField(
    #     view_name="plugins-api:nautobot_device_lifecycle_mgmt-api:providerlcm-detail"
    # )

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta attributes."""

        model = ProviderLCM
        fields = "__all__"


class ContractLCMSerializer(NautobotModelSerializer):  # pylint: disable=R0901,too-few-public-methods
    """API serializer."""

    # url = serializers.HyperlinkedIdentityField(
    #     view_name="plugins-api:nautobot_device_lifecycle_mgmt-api:contractlcm-detail"
    # )

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta attributes."""

        model = ContractLCM
        fields = "__all__"


class ContactLCMSerializer(NautobotModelSerializer):  # pylint: disable=R0901,too-few-public-methods
    """API serializer."""

    # url = serializers.HyperlinkedIdentityField(
    #     view_name="plugins-api:nautobot_device_lifecycle_mgmt-api:contactlcm-detail"
    # )

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta attributes."""

        model = ContactLCM
        fields = "__all__"


class SoftwareLCMSerializer(NautobotModelSerializer):  # pylint: disable=too-few-public-methods
    """REST API serializer for SoftwareLCM records."""

    # url = serializers.HyperlinkedIdentityField(
    #     view_name="plugins-api:nautobot_device_lifecycle_mgmt-api:softwarelcm-detail"
    # )

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta attributes."""

        model = SoftwareLCM
        fields = "__all__"


class SoftwareImageLCMSerializer(NautobotModelSerializer):  # pylint: disable=too-few-public-methods
    """REST API serializer for SoftwareImageLCM records."""

    # url = serializers.HyperlinkedIdentityField(
    #     view_name="plugins-api:nautobot_device_lifecycle_mgmt-api:softwareimagelcm-detail"
    # )

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta attributes."""

        model = SoftwareImageLCM
        fields = "__all__"


class ValidatedSoftwareLCMSerializer(NautobotModelSerializer):  # pylint: disable=too-few-public-methods
    """REST API serializer for ValidatedSoftwareLCM records."""

    # url = serializers.HyperlinkedIdentityField(
    #     view_name="plugins-api:nautobot_device_lifecycle_mgmt-api:validatedsoftwarelcm-detail"
    # )

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta attributes."""

        model = ValidatedSoftwareLCM
        fields = "__all__"


class CVELCMSerializer(NautobotModelSerializer):  # pylint: disable=abstract-method,too-few-public-methods
    """REST API serializer for CVELCM records."""

    # url = serializers.HyperlinkedIdentityField(view_name="plugins-api:nautobot_device_lifecycle_mgmt-api:cvelcm-detail")

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta attributes."""

        model = CVELCM
        fields = "__all__"


class VulnerabilityLCMSerializer(NautobotModelSerializer):  # pylint: disable=abstract-method,too-few-public-methods
    """REST API serializer for VulnerabilityLCM records."""

    # url = serializers.HyperlinkedIdentityField(
    #     view_name="plugins-api:nautobot_device_lifecycle_mgmt-api:vulnerabilitylcm-detail"
    # )

    class Meta:  # pylint: disable=too-few-public-methods
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


class DeviceSoftwareValidationResultSerializer(NautobotModelSerializer):  # pylint: disable=too-few-public-methods
    """REST API serializer for DeviceSoftwareValidationResult records."""

    # url = serializers.HyperlinkedIdentityField(
    #     view_name="plugins-api:nautobot_device_lifecycle_mgmt-api:devicesoftwarevalidationresult-detail"
    # )

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta attributes."""

        model = DeviceSoftwareValidationResult
        fields = "__all__"


class InventoryItemSoftwareValidationResultSerializer(
    NautobotModelSerializer
):  # pylint: disable=too-few-public-methods
    """REST API serializer for InventoryItemSoftwareValidationResult records."""

    # url = serializers.HyperlinkedIdentityField(
    #     view_name="plugins-api:nautobot_device_lifecycle_mgmt-api:inventoryitemsoftwarevalidationresult-detail"
    # )

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta attributes."""

        model = InventoryItemSoftwareValidationResult
        fields = "__all__"

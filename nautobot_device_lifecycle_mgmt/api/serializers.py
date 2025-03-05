"""API serializers for nautobot_device_lifecycle_mgmt."""

from nautobot.apps.api import NautobotModelSerializer, TaggedModelSerializerMixin

from nautobot_device_lifecycle_mgmt import models


class HardwareLCMSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):  # pylint: disable=too-many-ancestors
    """HardwareLCM Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.HardwareLCM
        fields = "__all__"

        # Option for disabling write for certain fields:
        # read_only_fields = []


class ProviderLCMSerializer(NautobotModelSerializer):  # pylint: disable=too-many-ancestors
    """ProviderLCM Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.ProviderLCM
        fields = "__all__"


class ContractLCMSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):  # pylint: disable=too-many-ancestors
    """ContractLCM Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.ContractLCM
        fields = "__all__"


class ContactLCMSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):  # pylint: disable=too-many-ancestors
    """ContactLCM Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.ContactLCM
        fields = "__all__"


class SoftwareLCMSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):  # pylint: disable=too-many-ancestors
    """SoftwareLCM Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.SoftwareLCM
        fields = "__all__"


class SoftwareImageLCMSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):  # pylint: disable=too-many-ancestors
    """SoftwareImageLCM Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.SoftwareImageLCM
        fields = "__all__"


class ValidatedSoftwareLCMSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):  # pylint: disable=too-many-ancestors
    """ValidatedSoftwareLCM Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.ValidatedSoftwareLCM
        fields = "__all__"


class CVELCMSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):  # pylint: disable=too-many-ancestors
    """CVELCM Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.CVELCM
        fields = "__all__"


class VulnerabilityLCMSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):  # pylint: disable=too-many-ancestors
    """VulnerabilityLCM Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.VulnerabilityLCM
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


class DeviceSoftwareValidationResultSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):  # pylint: disable=too-many-ancestors
    """DeviceSoftwareValidationResult Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.DeviceSoftwareValidationResult
        fields = "__all__"


class DeviceHardwareNoticeResultSerializer(NautobotModelSerializer):
    """REST API serializer for DeviceHardwareNoticeResult records."""

    class Meta:
        """Meta attributes."""

        model = models.DeviceHardwareNoticeResult
        fields = "__all__"


class InventoryItemSoftwareValidationResultSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):  # pylint: disable=too-many-ancestors
    """InventoryItemSoftwareValidationResult Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.InventoryItemSoftwareValidationResult
        fields = "__all__"

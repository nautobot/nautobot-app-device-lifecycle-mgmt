"""Django classes and functions handling Software Lifecycle related functionality."""

from nautobot.dcim.models import Device, InventoryItem

from nautobot_device_lifecycle_mgmt.filters import ValidatedSoftwareLCMFilterSet
from nautobot_device_lifecycle_mgmt.models import ValidatedSoftwareLCM
from nautobot_device_lifecycle_mgmt.tables import ValidatedSoftwareLCMTable


class ItemSoftware:
    """Base class providing functions for computing ValidatedSoftwareLCM related objects."""

    soft_obj_model = None

    def __init__(self, item_obj):
        """Initalize ItemSoftware object."""
        self.item_obj = item_obj
        self.validated_software_qs = ValidatedSoftwareLCM.objects.get_for_object(self.item_obj)
        self.software = self.item_obj.software_version

    def get_validated_software_table(self):
        """Returns table of validated software linked to the object."""
        if not self.validated_software_qs:
            return None

        return ValidatedSoftwareLCMTable(
            list(self.validated_software_qs),
            orderable=False,
            exclude=(
                "software",
                "start",
                "actions",
            ),
        )

    def validate_software(self, preferred_only=False):
        """Validate software against the validated software objects."""
        if not (self.software and self.validated_software_qs.exists()):
            return False

        validated_software_versions = ValidatedSoftwareLCMFilterSet(
            {"valid": True}, self.validated_software_qs.filter(software=self.software)
        ).qs
        if preferred_only:
            validated_software_versions = validated_software_versions.filter(preferred_only=True)

        return validated_software_versions.exists()


class DeviceSoftware(ItemSoftware):
    """Computes validated software objects for Device objects."""

    soft_obj_model = Device


class InventoryItemSoftware(ItemSoftware):
    """Computes validated software objects for InventoryItem objects."""

    soft_obj_model = InventoryItem

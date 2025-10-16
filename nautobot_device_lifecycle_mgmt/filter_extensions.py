"""Extensions to core filters."""

from django_filters import BooleanFilter
from nautobot.apps.filters import FilterExtension, NaturalKeyOrPKMultipleChoiceFilter
from nautobot.apps.forms import DynamicModelMultipleChoiceField

from nautobot_device_lifecycle_mgmt.models import ContractLCM, ValidatedSoftwareLCM


def distinct_filter(queryset, _, value):
    """Returns distinct Inventory Items by part_id."""
    if value:
        return queryset.without_tree_fields().order_by().distinct("part_id")
    return queryset


#
# INVENTORY ITEM FILTER EXTENSION
#
class InventoryItemFilterExtension(FilterExtension):
    """Extends Inventory Item Filters."""

    model = "dcim.inventoryitem"

    filterset_fields = {
        "nautobot_device_lifecycle_mgmt_distinct_part_id": BooleanFilter(
            method=distinct_filter, label="_dpid_dlm_app_internal_use_only"
        ),
        "nautobot_device_lifecycle_mgmt_validatedsoftware_inventory_items": NaturalKeyOrPKMultipleChoiceFilter(
            field_name="validatedsoftware_inventory_items_tab",
            queryset=ValidatedSoftwareLCM.objects.all(),
            label="Validated Software",
        ),
    }

    filterform_fields = {
        "nautobot_device_lifecycle_mgmt_validatedsoftware_inventory_items": DynamicModelMultipleChoiceField(
            queryset=ValidatedSoftwareLCM.objects.all(),
            label="Validated Software",
            required=False,
        ),
    }


#
# DEVICE FILTER EXTENSION
#
class DeviceFilterExtension(FilterExtension):
    """Extends Device Filters."""

    model = "dcim.device"

    filterset_fields = {
        "nautobot_device_lifecycle_mgmt_device_contracts": NaturalKeyOrPKMultipleChoiceFilter(
            field_name="device_contracts",
            queryset=ContractLCM.objects.all(),
            label="Contracts",
        ),
        "nautobot_device_lifecycle_mgmt_validatedsoftware_devices": NaturalKeyOrPKMultipleChoiceFilter(
            field_name="validatedsoftware_devices_tab",
            queryset=ValidatedSoftwareLCM.objects.all(),
            label="Validated Software",
        ),
    }

    filterform_fields = {
        "nautobot_device_lifecycle_mgmt_device_contracts": DynamicModelMultipleChoiceField(
            queryset=ContractLCM.objects.all(),
            label="Contracts",
            required=False,
        ),
        "nautobot_device_lifecycle_mgmt_validatedsoftware_devices": DynamicModelMultipleChoiceField(
            queryset=ValidatedSoftwareLCM.objects.all(),
            label="Validated Software",
            required=False,
        ),
    }


#
# ROLE FILTER EXTENSION
#
class RoleFilterExtension(FilterExtension):
    """Extends Role Filters."""

    model = "extras.role"

    filterset_fields = {
        "nautobot_device_lifecycle_mgmt_validatedsoftware_device_roles": NaturalKeyOrPKMultipleChoiceFilter(
            field_name="validatedsoftware_device_roles_tab",
            queryset=ValidatedSoftwareLCM.objects.all(),
            label="Validated Software",
        ),
    }

    filterform_fields = {
        "nautobot_device_lifecycle_mgmt_validatedsoftware_device_roles": DynamicModelMultipleChoiceField(
            queryset=ValidatedSoftwareLCM.objects.all(),
            label="Validated Software",
            required=False,
        ),
    }


#
# DEVICE TYPE FILTER EXTENSION
#
class DeviceTypeFilterExtension(FilterExtension):
    """Extends Device Type Filters."""

    model = "dcim.devicetype"

    filterset_fields = {
        "nautobot_device_lifecycle_mgmt_validatedsoftware_device_types": NaturalKeyOrPKMultipleChoiceFilter(
            field_name="validatedsoftware_device_types_tab",
            queryset=ValidatedSoftwareLCM.objects.all(),
            label="Validated Software",
        ),
    }

    filterform_fields = {
        "nautobot_device_lifecycle_mgmt_validatedsoftware_device_types": DynamicModelMultipleChoiceField(
            queryset=ValidatedSoftwareLCM.objects.all(),
            label="Validated Software",
            required=False,
        ),
    }


#
# TAG FILTER EXTENSION
#
class TagFilterExtension(FilterExtension):
    """Extends Tag Filters."""

    model = "extras.tag"

    filterset_fields = {
        "nautobot_device_lifecycle_mgmt_validatedsoftware_tags": NaturalKeyOrPKMultipleChoiceFilter(
            field_name="validatedsoftware_object_tags_tab",
            queryset=ValidatedSoftwareLCM.objects.all(),
            label="Validated Software",
        ),
    }

    filterform_fields = {
        "nautobot_device_lifecycle_mgmt_validatedsoftware_tags": DynamicModelMultipleChoiceField(
            queryset=ValidatedSoftwareLCM.objects.all(),
            label="Validated Software",
            required=False,
        ),
    }


#
# REGISTER ALL EXTENSIONS
#
filter_extensions = [
    InventoryItemFilterExtension,
    DeviceFilterExtension,
    RoleFilterExtension,
    DeviceTypeFilterExtension,
    TagFilterExtension,
]

"""Extensions to core filters."""

from django_filters import BooleanFilter
from nautobot.apps.filters import FilterExtension, NaturalKeyOrPKMultipleChoiceFilter
from nautobot.apps.forms import DynamicModelMultipleChoiceField

from nautobot_device_lifecycle_mgmt.models import ContractLCM


def distinct_filter(queryset, _, value):
    """Returns distinct Inventory Items by part_id."""
    if value:
        return queryset.without_tree_fields().order_by().distinct("part_id")
    return queryset


class InventoryItemFilterExtension(FilterExtension):
    """Extends Inventory Item Filters."""

    model = "dcim.inventoryitem"

    filterset_fields = {
        "nautobot_device_lifecycle_mgmt_distinct_part_id": BooleanFilter(
            method=distinct_filter, label="_dpid_dlm_app_internal_use_only"
        )
    }


class DeviceFilterExtension(FilterExtension):
    """Extends Device Filters."""

    model = "dcim.device"

    filterset_fields = {
        "nautobot_device_lifecycle_mgmt_device_contracts": NaturalKeyOrPKMultipleChoiceFilter(
            field_name="device_contracts",
            queryset=ContractLCM.objects.all(),
            label="Contracts",
        )
    }

    filterform_fields = {
        "nautobot_device_lifecycle_mgmt_device_contracts": DynamicModelMultipleChoiceField(
            queryset=ContractLCM.objects.all(),
            label="Contracts",
            required=False,
        )
    }


filter_extensions = [InventoryItemFilterExtension, DeviceFilterExtension]

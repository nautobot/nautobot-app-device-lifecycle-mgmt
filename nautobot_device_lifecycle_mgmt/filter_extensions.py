"""Extensions to core filters."""

from django_filters import BooleanFilter
from nautobot.apps.filters import FilterExtension


def distinct_filter(queryset, _, value):
    """Returns distinct Inventory Items by part_id."""
    if value:
        return queryset.exclude(part_id__exact="").without_tree_fields().order_by().distinct("part_id")
    return queryset


class InventoryItemFilterExtension(FilterExtension):
    """Extends Inventory Item Filters."""

    model = "dcim.inventoryitem"

    filterset_fields = {
        "nautobot_device_lifecycle_mgmt_distinct_part_id": BooleanFilter(
            method=distinct_filter, label="Distinct Part ID"
        )
    }


filter_extensions = [InventoryItemFilterExtension]

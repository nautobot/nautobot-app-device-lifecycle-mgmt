"""Nautobot Lifecycle Management plugin application level metrics ."""
from django.db.models import Count, F, OuterRef, Q, Subquery, Value
from django.db.models.functions import Coalesce
from nautobot.dcim.models import DeviceType, InventoryItem
from prometheus_client.core import GaugeMetricFamily

from nautobot_device_lifecycle_mgmt.models import DeviceSoftwareValidationResult, InventoryItemSoftwareValidationResult


def metrics_lcm_validation_report_device_type():
    """Calculate number of devices with valid/invalid software by device_type.

    Yields:
        GaugeMetricFamily: Prometheus Metrics
    """
    device_software_compliance_gauge = GaugeMetricFamily(
        "nautobot_lcm_software_compliance_per_device_type",
        "Number of devices that have valid/invalid software by device_type",
        labels=["device_type", "is_valid"],
    )

    device_types = DeviceType.objects.values("model")

    # Annotate DeviceSoftwareValidationResult with counts for valid and invalid software per device type
    validation_counts = (
        DeviceSoftwareValidationResult.objects.order_by()
        .values(model=F("device__device_type__model"))
        .annotate(
            invalid_count=Count("device__device_type__model", filter=Q(is_validated=False)),
            valid_count=Count("device__device_type__model", filter=Q(is_validated=True)),
        )
        .values("model", "invalid_count", "valid_count")
    )

    # Set valid and invalid software validation counts to 0 for device types that don't have DeviceSoftwareValidationResult entry
    validation_counts_final = device_types.annotate(
        valid_count=Coalesce(
            Subquery(validation_counts.filter(model=OuterRef("model")).values("valid_count")), Value(0)
        ),
        invalid_count=Coalesce(
            Subquery(validation_counts.filter(model=OuterRef("model")).values("invalid_count")), Value(0)
        ),
    ).values_list("model", "valid_count", "invalid_count")

    for model, valid_count, invalid_count in validation_counts_final:
        device_software_compliance_gauge.add_metric(
            labels=[model, "True"],
            value=valid_count,
        )
        device_software_compliance_gauge.add_metric(
            labels=[model, "False"],
            value=invalid_count,
        )

    yield device_software_compliance_gauge


def metrics_lcm_validation_report_inventory_item():
    """Calculate number of inventory items with valid/invalid software.

    InventoryItem objects missing part_id are excluded.

    Yields:
        GaugeMetricFamily: Prometheus Metrics
    """
    inventory_item_software_compliance_gauge = GaugeMetricFamily(
        "nautobot_lcm_software_compliance_per_inventory_item",
        "Number of devices that have valid/invalid software by inventory item",
        labels=["inventory_item", "is_valid"],
    )
    inventory_item_part_ids = InventoryItem.objects.exclude(part_id="").order_by().values("part_id").distinct()

    # Annotate InventoryItemSoftwareValidationResult with counts for valid and invalid software per part id
    validation_counts = (
        InventoryItemSoftwareValidationResult.objects.exclude(part_id="")
        .order_by()
        .values(part_id=F("inventory_item__part_id"))
        .annotate(
            invalid_count=Count("inventory_item__part_id", filter=Q(is_validated=False)),
            valid_count=Count("inventory_item__part_id", filter=Q(is_validated=True)),
        )
        .values("part_id", "invalid_count", "valid_count")
    )

    # Set valid and invalid software validation counts to 0 for part ids that don't have InventoryItemSoftwareValidationResult entry
    validation_counts_final = inventory_item_part_ids.annotate(
        valid_count=Coalesce(
            Subquery(validation_counts.filter(part_id=OuterRef("part_id")).values("valid_count")), Value(0)
        ),
        invalid_count=Coalesce(
            Subquery(validation_counts.filter(part_id=OuterRef("part_id")).values("invalid_count")), Value(0)
        ),
    ).values_list("part_id", "valid_count", "invalid_count")

    for part_id, valid_count, invalid_count in validation_counts_final:
        inventory_item_software_compliance_gauge.add_metric(
            labels=[part_id, "True"],
            value=valid_count,
        )
        inventory_item_software_compliance_gauge.add_metric(
            labels=[part_id, "False"],
            value=invalid_count,
        )

    yield inventory_item_software_compliance_gauge


metrics = [
    metrics_lcm_validation_report_device_type,
    metrics_lcm_validation_report_inventory_item,
]

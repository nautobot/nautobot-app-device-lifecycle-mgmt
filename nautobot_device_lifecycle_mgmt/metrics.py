"""Nautobot Lifecycle Management plugin application level metrics ."""
from prometheus_client.core import GaugeMetricFamily

from nautobot_device_lifecycle_mgmt.models import DeviceSoftwareValidationResult, InventoryItemSoftwareValidationResult


def metrics_lcm_validation_report_device_type():
    """Calculate number of devices with valid software by device_type.

    Yields:
        GaugeMetricFamily: Prometheus Metrics
    """
    device_validation_model = (
        DeviceSoftwareValidationResult.objects.values_list("device__device_type__model", flat=True)
        .distinct()
        .order_by()
    )

    device_software_compliance_gauge = GaugeMetricFamily(
        "nautobot_lcm_compliance_by_device_type_total",
        "Number of devices that have valid/invalid software by device_type",
        labels=["device_type", "is_valid"],
    )

    # If there is available data a metric gauge will be created if not no gauge will be created.
    for model in device_validation_model:
        device_software_compliance_gauge.add_metric(
            labels=[model, "True"],
            value=(
                DeviceSoftwareValidationResult.objects.filter(
                    device__device_type__model=model, is_validated=True
                ).count()
            ),
        )
        device_software_compliance_gauge.add_metric(
            labels=[model, "False"],
            value=(
                DeviceSoftwareValidationResult.objects.filter(
                    device__device_type__model=model, is_validated=False
                ).count()
            ),
        )

    yield device_software_compliance_gauge


def metrics_lcm_validation_report_inventory_item():
    """Calculate number of inventory items with valid/invalid software.

    Yields:
        GaugeMetricFamily: Prometheus Metrics
    """
    inventory_item_validation = (
        InventoryItemSoftwareValidationResult.objects.values_list("inventory_item__part_id", flat=True)
        .distinct()
        .order_by()
    )

    item_software_compliance_gauge = GaugeMetricFamily(
        "nautobot_lcm_valid_by_inventory_item_total",
        "Number of devices that have valid/invalid software by inventory item",
        labels=["inventory_item"],
    )

    # If there is available data a metric gauge will be created if not no gauge will be created.
    for model in inventory_item_validation:
        item_software_compliance_gauge.add_metric(
            labels=[model, "True"],
            value=(
                InventoryItemSoftwareValidationResult.objects.filter(
                    inventory_item__part_id=model, is_validated=True
                ).count()
            ),
        )
        item_software_compliance_gauge.add_metric(
            labels=[model, "False"],
            value=(
                InventoryItemSoftwareValidationResult.objects.filter(
                    inventory_item__part_id=model, is_validated=False
                ).count()
            ),
        )

    yield item_software_compliance_gauge


metrics = [
    metrics_lcm_validation_report_device_type,
    metrics_lcm_validation_report_inventory_item,
]

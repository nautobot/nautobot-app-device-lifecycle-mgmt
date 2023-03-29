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

    valid_device_software_gauge = GaugeMetricFamily(
        "nautobot_lcm_valid_by_device_type_total",
        "Number of devices that have valid software by device_type",
        labels=["device_type"],
    )

    invalid_device_software_gauge = GaugeMetricFamily(
        "nautobot_lcm_invalid_by_device_type_total",
        "Number of devices that have invalid software by device_type",
        labels=["device_type"],
    )

    # If there is available data a metric gauge will be created if not no gauge will be created.
    for model in device_validation_model:
        valid_device_software_gauge.add_metric(
            labels=[model],
            value=(
                DeviceSoftwareValidationResult.objects.filter(
                    device__device_type__model=model, is_validated=True
                ).count()
            ),
        )
        invalid_device_software_gauge.add_metric(
            labels=[model],
            value=(
                DeviceSoftwareValidationResult.objects.filter(
                    device__device_type__model=model, is_validated=False
                ).count()
            ),
        )

    yield valid_device_software_gauge
    yield invalid_device_software_gauge


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

    valid_item_software_gauge = GaugeMetricFamily(
        "nautobot_lcm_valid_by_inventory_item_total",
        "Number of devices that have valid software by inventory item",
        labels=["inventory_item"],
    )

    invalid_item_software_gauge = GaugeMetricFamily(
        "nautobot_lcm_invalid_by_inventory_item_total",
        "Number of devices that have invalid software by inventory item",
        labels=["inventory_item"],
    )

    # If there is available data a metric gauge will be created if not no gauge will be created.
    for model in inventory_item_validation:
        valid_item_software_gauge.add_metric(
            labels=[model],
            value=(
                InventoryItemSoftwareValidationResult.objects.filter(
                    inventory_item__part_id=model, is_validated=True
                ).count()
            ),
        )
        invalid_item_software_gauge.add_metric(
            labels=[model],
            value=(
                InventoryItemSoftwareValidationResult.objects.filter(
                    inventory_item__part_id=model, is_validated=False
                ).count()
            ),
        )

    yield valid_item_software_gauge

    yield invalid_item_software_gauge


def metrics_lcm_validation_report_totals():
    """Gather total lifecycle management report counts.
    Yields:
        GaugeMetricFamily: Prometheus Metrics
    """
    total_device_software_gauge = GaugeMetricFamily(
        "nautobot_lcm_device_result_total",
        "Number of devices that are in lifecycle management report",
        labels=["devices"],
    )

    total_device_software_gauge.add_metric(
        labels=["Total LCM Validated Device Count"],
        value=(DeviceSoftwareValidationResult.objects.all().count()),
    )

    yield total_device_software_gauge

    total_inventory_item_software_gauge = GaugeMetricFamily(
        "nautobot_lcm_inventory_result_total",
        "Number of inventory items that are in lifecycle management report",
        labels=["inventory_items"],
    )

    total_inventory_item_software_gauge.add_metric(
        labels=["Total LCM Validated Inventory Item Count"],
        value=(InventoryItemSoftwareValidationResult.objects.all().count()),
    )

    yield total_inventory_item_software_gauge


metrics = [
    metrics_lcm_validation_report_device_type,
    metrics_lcm_validation_report_inventory_item,
    metrics_lcm_validation_report_totals,
]

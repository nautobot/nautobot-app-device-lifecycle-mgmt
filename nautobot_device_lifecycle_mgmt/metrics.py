"""Nautobot Lifecycle Management plugin application level metrics ."""
from prometheus_client.core import GaugeMetricFamily

from nautobot_device_lifecycle_mgmt import DeviceSoftwareValidationResult


def metric_():
    """Calculate number of devices with valid software by device_type.

    Yields:
        GaugeMetricFamily: Prometheus Metrics
    """
    models = DeviceSoftwareValidationResult.objects.values("device__device_type__model").distinct()

    valid_software_gauge = GaugeMetricFamily(
        "nautobot_device_lifecycle_compliant_by_device_type_total",
        "Number of devices that have valid software by device_type",
        labels=["device_type"],
    )

    for model in models:
        valid_software_gauge.add_metric(
            labels=[model],
            value=(
                DeviceSoftwareValidationResult.objects.filter(
                    device__device_type__model=model, is_validated=True
                ).count()
            ),
        )

    yield valid_software_gauge

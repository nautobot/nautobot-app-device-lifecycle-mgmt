# Metrics

!!! warning
    Metrics will only work with Nautobot Version 1.5.13 and newer.

The Software Lifecycle applicaiton has the following metrics included.

```
# HELP nautobot_lcm_compliance_by_device_type_total Number of devices that have valid/invalid software by device_type
# TYPE nautobot_lcm_compliance_by_device_type_total gauge
nautobot_lcm_compliance_by_device_type_total{device_type="ASR-9903",is_valid="True"} 3.0
nautobot_lcm_compliance_by_device_type_total{device_type="ASR-9903",is_valid="False"} 1.0
nautobot_lcm_compliance_by_device_type_total{device_type="IntelServer",is_valid="True"} 2.0
nautobot_lcm_compliance_by_device_type_total{device_type="IntelServer",is_valid="False"} 2.0
# HELP nautobot_lcm_valid_by_inventory_item_total Number of devices that have valid/invalid software by inventory item
# TYPE nautobot_lcm_valid_by_inventory_item_total gauge
nautobot_lcm_valid_by_inventory_item_total{inventory_item="Cisco-FEX-port1",is_valid="True"} 0.0
nautobot_lcm_valid_by_inventory_item_total{inventory_item="Cisco-FEX-port1",is_valid="False"} 1.0
```

## Enabling Metrics
Metrics are not exposed by default. Metric exposition can be toggled with the [`METRICS_ENABLED`](https://docs.nautobot.com/projects/core/en/stable/configuration/optional-settings/?h=metrics#metrics_enabled) configuration setting which exposes metrics at the `/metrics` HTTP endpoint, e.g. `https://nautobot.local/metrics`.

## Nautobot Configuration Guide for Prometheus Metrics
Please follow this [Guide](https://docs.nautobot.com/projects/core/en/stable/additional-features/prometheus-metrics/?h=metrics) to extend Nautobot Lifecycle metric data.

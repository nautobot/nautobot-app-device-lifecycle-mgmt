# Metrics

!!! warning
    Metrics will only work with Nautobot Version 1.5.13 and newer.

The Software Lifecycle applicaiton has the following metrics included.

```
# HELP Nautobot LCM Hardware End of Support per Part Number
# TYPE nautobot_lcm_hw_end_of_support_per_part_number gauge
nautobot_lcm_devices_eos_per_part_number{part_number="WS-SUP720-3BXL"} 38.0
nautobot_lcm_devices_eos_per_part_number{part_number="dcs-7048-t"} 0.0
nautobot_lcm_devices_eos_per_part_number{part_number="DCS-7150S-24"} 0.0
nautobot_lcm_devices_eos_per_part_number{part_number="DCS-7280CR2-60"} 0.0
nautobot_lcm_devices_eos_per_part_number{part_number="veos"} 0.0
nautobot_lcm_devices_eos_per_part_number{part_number="CSR1000V"} 0.0
# HELP Nautobot LCM Hardware End of Support per Site
# TYPE nautobot_lcm_devices_eos_per_site gauge
nautobot_lcm_devices_eos_per_site{site="ams01"} 1.0
nautobot_lcm_devices_eos_per_site{site="ang01"} 1.0
nautobot_lcm_devices_eos_per_site{site="atl01"} 1.0
nautobot_lcm_devices_eos_per_site{site="atl02"} 1.0
nautobot_lcm_devices_eos_per_site{site="azd01"} 1.0
nautobot_lcm_devices_eos_per_site{site="bkk01"} 1.0
nautobot_lcm_devices_eos_per_site{site="bre01"} 1.0
nautobot_lcm_devices_eos_per_site{site="can01"} 1.0
nautobot_lcm_devices_eos_per_site{site="cdg01"} 1.0
nautobot_lcm_devices_eos_per_site{site="cdg02"} 1.0
nautobot_lcm_devices_eos_per_site{site="del01"} 1.0
nautobot_lcm_devices_eos_per_site{site="den01"} 1.0
nautobot_lcm_devices_eos_per_site{site="dfw"} 0.0
nautobot_lcm_devices_eos_per_site{site="dfw01"} 1.0
nautobot_lcm_devices_eos_per_site{site="dfw02"} 1.0
nautobot_lcm_devices_eos_per_site{site="dxb01"} 1.0
```

## Enabling Metrics
Metrics are not exposed by default. Metric exposition can be toggled with the [`METRICS_ENABLED`](https://docs.nautobot.com/projects/core/en/stable/configuration/optional-settings/?h=metrics#metrics_enabled) configuration setting which exposes metrics at the `/metrics` HTTP endpoint, e.g. `https://nautobot.local/metrics`.

## Nautobot Configuration Guide for Prometheus Metrics
Please follow this [Guide](https://docs.nautobot.com/projects/core/en/stable/additional-features/prometheus-metrics/?h=metrics) to extend Nautobot Lifecycle metric data.

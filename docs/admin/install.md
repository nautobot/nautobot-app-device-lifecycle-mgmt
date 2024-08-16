# Installing the App in Nautobot

## Prerequisites

- The plugin is compatible with Nautobot 1.1.6 and higher.
- Databases supported: PostgreSQL, MySQL

!!! note
    Please check the [dedicated page](compatibility_matrix.md) for a full compatibility matrix and the deprecation policy.

### Access Requirements

This plugin can be run with no additional access requirements, however there are extended services such as CVSS / NIST integration which depends on integration to the NIST public api service.  Other examples would include access to the Cisco EoX api service which can be used to enrich data based on devices under contract coverage.  Please leverage the documentation pages for the specific plugin integrations for details.

## Install Guide

!!! note
    Plugins can be installed manually or using Python's `pip`. See the [nautobot documentation](https://nautobot.readthedocs.io/en/latest/plugins/#install-the-package) for more details. The pip package name for this plugin is [`nautobot-device-lifecycle-mgmt`](https://pypi.org/project/nautobot-device-lifecycle-mgmt/).

The plugin is available as a Python package via PyPI and can be installed with `pip`:

```shell
pip install nautobot-device-lifecycle-mgmt
```

To ensure Device Lifecycle Management is automatically re-installed during future upgrades, create a file named `local_requirements.txt` (if not already existing) in the Nautobot root directory (alongside `requirements.txt`) and list the `nautobot-device-lifecycle-mgmt` package:

```shell
echo nautobot-device-lifecycle-mgmt >> local_requirements.txt
```

Once installed, the plugin needs to be enabled in your Nautobot configuration. The following block of code below shows the additional configuration required to be added to your `nautobot_config.py` file:

- Append `"nautobot_device_lifecycle_mgmt"` to the `PLUGINS` list.
- Append the `"nautobot_device_lifecycle_mgmt"` dictionary to the `PLUGINS_CONFIG` dictionary and override any defaults.

```python
# In your nautobot_config.py
PLUGINS = ["nautobot_device_lifecycle_mgmt"]

# Optionally you can override default settings for config items in the device lifecylce plugin (as seen in this example)
PLUGINS_CONFIG = {
    "nautobot_device_lifecycle_mgmt": {
        "barchart_bar_width": float(os.environ.get("BARCHART_BAR_WIDTH", 0.1)),
        "barchart_width": int(os.environ.get("BARCHART_WIDTH", 12)),
        "barchart_height": int(os.environ.get("BARCHART_HEIGHT", 5)),
        "enabled_metrics": [x for x in os.environ.get("NAUTOBOT_DLM_ENABLED_METRICS", "").split(",") if x],
    },
}
```

Once the Nautobot configuration is updated, run the Post Upgrade command (`nautobot-server post_upgrade`) to run migrations and clear any cache.

```shell
nautobot-server post_upgrade
```

Then restart (if necessary) the Nautobot services which may include:

- Nautobot
- Nautobot Workers
- Nautobot Scheduler

```shell
sudo systemctl restart nautobot nautobot-worker nautobot-scheduler
```

!!! note
    If you are on Nautobot >= 1.1.0 and have the RQ worker continuing on, also restart the RQ worker service: `sudo systemctl restart nautobot-rq-worker`.


## App Configuration

The plugin behavior can be controlled with the following list of settings.

| Key     | ENV VAR | Example | Default | Description                          |
| ------- | ------ |  ------ | -------- | ------------------------------------- |
| barchart_bar_width | BARCHART_BAR_WIDTH | 0.15 | 0.1 | The width of the table bar within the overview report. |
| barchart_width | BARCHART_WIDTH | 15 | 12 | The width of the barchart within the overview report. |
| barchart_height | BARCHART_HEIGHT | 8 | 5 | The height of the barchart within the overview report. |
| enabled_metrics | NAUTOBOT_DLM_ENABLED_METRICS | `["nautobot_metrics_lcm_hw_end_of_support_site"]` | `[]` | Enables metrics corresponding to the provided, comma separated, entries. |

### Available Metric Names

Following are the metric names that can be defined in `enabled_metrics`:

- `nautobot_lcm_software_compliance_per_device_type`: Number of devices with valid/invalid software by device_type.

- `nautobot_lcm_software_compliance_per_inventory_item`: Number of inventory items with valid/invalid software.

- `nautobot_lcm_hw_end_of_support_per_part_number`: Number of End of Support devices and inventory items per Part Number.

- `nautobot_metrics_lcm_hw_end_of_support_site`: Number of End of Support devices and inventory items per Site.

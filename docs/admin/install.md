# Installing the App in Nautobot

Here you will find detailed instructions on how to **install** and **configure** the App within your Nautobot environment.

## Prerequisites

- The app is compatible with Nautobot 2.2.0 and higher.
- Databases supported: PostgreSQL, MySQL

!!! note
    Please check the [dedicated page](compatibility_matrix.md) for a full compatibility matrix and the deprecation policy.

### Access Requirements

This app can be run with no additional access requirements, however there are extended services such as CVSS / NIST integration which depends on integration to the NIST public api service.  Other examples would include access to the Cisco EoX api service which can be used to enrich data based on devices under contract coverage.  Please leverage the documentation pages for the specific app integrations for details.

## Install Guide

!!! note
    Apps can be installed from the [Python Package Index](https://pypi.org/) or locally. See the [Nautobot documentation](https://docs.nautobot.com/projects/core/en/stable/user-guide/administration/installation/app-install/) for more details. The pip package name for this app is [`nautobot-device-lifecycle-mgmt`](https://pypi.org/project/nautobot-device-lifecycle-mgmt/).

The app is available as a Python package via PyPI and can be installed with `pip`:

```shell
pip install nautobot-device-lifecycle-mgmt
```

To ensure Device Lifecycle Management is automatically re-installed during future upgrades, create a file named `local_requirements.txt` (if not already existing) in the Nautobot root directory (alongside `requirements.txt`) and list the `nautobot-device-lifecycle-mgmt` package:

```shell
echo nautobot-device-lifecycle-mgmt >> local_requirements.txt
```

Once installed, the app needs to be enabled in your Nautobot configuration. The following block of code below shows the additional configuration required to be added to your `nautobot_config.py` file:

- Append `"nautobot_device_lifecycle_mgmt"` to the `PLUGINS` list.
- Append the `"nautobot_device_lifecycle_mgmt"` dictionary to the `PLUGINS_CONFIG` dictionary and override any defaults.

```python
# In your nautobot_config.py
PLUGINS = ["nautobot_device_lifecycle_mgmt"]

# Optionally you can override default settings for config items in the device lifecycle app (as seen in this example)
PLUGINS_CONFIG = {
    "nautobot_device_lifecycle_mgmt": {
        "barchart_bar_width": float(os.environ.get("BARCHART_BAR_WIDTH", 0.1)),
        "barchart_width": int(os.environ.get("BARCHART_WIDTH", 12)),
        "barchart_height": int(os.environ.get("BARCHART_HEIGHT", 5)),
        "enabled_metrics": [x for x in os.environ.get("NAUTOBOT_DLM_ENABLED_METRICS", "").split(",") if x],
    },
}
```

Once the Nautobot configuration is updated, run the Post Upgrade command (`nautobot-server post_upgrade`) to run migrations and clear any cache:

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

## App Configuration

The app behavior can be controlled with the following list of settings:
| Key                  | Example                                                             | Default            | Description                                                          |
| -------------------- | ------------------------------------------------------------------- | ------------------ | -------------------------------------------------------------------- |
| `barchart_bar_width` | `0.1`                                                               | `0.15`             | The width of the table bar within the overview report.               |
| `barchart_width`     | `12`                                                                | `12`               | The width of the barchart within the overview report.                |
| `barchart_height`    | `5`                                                                 | `5`                | The height of the barchart within the overview report.               |
| `enabled_metrics`    | `["metrics_lcm_hw_end_of_support_location"]`                        | `[]`               | Enables metrics corresponding to the provided entries.               |

### Available Metric Names

Following are the metric names that can be defined in `enabled_metrics`:

- `nautobot_lcm_software_compliance_per_device_type`: Number of devices with valid/invalid software by device_type.

- `nautobot_lcm_software_compliance_per_inventory_item`: Number of inventory items with valid/invalid software.

- `nautobot_lcm_hw_end_of_support_per_part_number`: Number of End of Support devices and inventory items per Part Number.

- `nautobot_lcm_hw_end_of_support_per_location`: Number of End of Support devices and inventory items per Location.

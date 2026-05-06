# Installing the App in Nautobot

Here you will find detailed instructions on how to **install** and **configure** the App within your Nautobot environment.

## Prerequisites

- The app is compatible with Nautobot 3.0.0 and higher.
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
| `multi_tenant_mode`  | `True` or `False`                                                   | `False`            | Enable tenant-aware software filtering. See [Multi-Tenant Mode](#multi-tenant-mode) below. |

### Available Metric Names

Following are the metric names that can be defined in `enabled_metrics`:

- `nautobot_lcm_software_compliance_per_device_type`: Number of devices with valid/invalid software by device_type.

- `nautobot_lcm_software_compliance_per_inventory_item`: Number of inventory items with valid/invalid software.

- `nautobot_lcm_hw_end_of_support_per_part_number`: Number of End of Support devices and inventory items per Part Number.

- `nautobot_lcm_hw_end_of_support_per_location`: Number of End of Support devices and inventory items per Location.

## Multi-Tenant Mode

The `multi_tenant_mode` setting controls which ValidatedSoftware records are considered when evaluating software compliance for a given device.

### Default Behavior (Legacy Mode - `multi_tenant_mode = False`)

**All devices** (whether assigned to a tenant or not) use legacy filtering logic:

- Filter software by **direct device assignment**, **device type**, **device role**, and **tags**
- ValidatedSoftware records with a `device_tenants` assignment are excluded; only untenanted records are considered
- The device's own tenant is ignored — all devices see the same pool of untenanted records

**Use case:** Existing deployments with tenant-assigned devices that don't need per-tenant software isolation.

### Multi-Tenant Mode (`multi_tenant_mode = True`)

Enables **tenant-aware software filtering**:

**For devices WITH a tenant assigned:**

A `ValidatedSoftware` record matches if **any one** of the following applies:

- The device is directly listed in the record's `devices` field (evaluated regardless of whether the record has `device_tenants` set)
- The record's `device_tenants` includes the device's tenant, AND:
    - Both `device_types` and `device_roles` are set and match the device
    - Only `device_types` is set and matches the device's type
    - Only `device_roles` is set and matches the device's role
    - Neither `device_types` nor `device_roles` is set (tenant-only record)
- The record's `object_tags` intersects the device's tags (evaluated regardless of whether the record has `device_tenants` set)

**For devices WITHOUT a tenant assigned:**

- See only ValidatedSoftware records with **no tenant** assigned, matched by direct device assignment, device type, device role, or tags
- Filtering is based on:
    - Direct device assignments (software must have no tenant)
    - Device type and role matches (software must have no tenant)
    - Device tags (software must have no tenant)

**Use case:** Multi-tenant environments where each tenant has different software requirements and needs isolated software catalogs.

### Configuration

To enable multi-tenant mode, add the following to your `nautobot_config.py`:

```python
PLUGINS_CONFIG = {
    "nautobot_device_lifecycle_mgmt": {
        "multi_tenant_mode": True,  # Enable tenant-aware filtering
    },
}
```

### Examples

#### Example 1: Legacy Mode (Default)

- Device "rtr1" assigned to **Tenant A**
- Global software "IOS 17.3.3" configured for device type "ASR-1000"
- **Result:** Device "rtr1" **CAN** see the global software (legacy behavior)

#### Example 2: Multi-Tenant Mode

- Device "rtr1" assigned to **Tenant A**
- Global software "IOS 17.3.3" configured for device type "ASR-1000" (no tenant)
- ValidatedSoftware for same version configured for **Tenant A**
- **Result:** Device "rtr1" **CANNOT** see the global software, only the Tenant A version

### Switching Modes

To switch between modes, simply update the `multi_tenant_mode` setting in your `nautobot_config.py` and restart Nautobot services:

```shell
sudo systemctl restart nautobot nautobot-worker nautobot-scheduler
```

!!! note
    No database migrations are required when changing this setting - it is purely logical and doesn't affect how software is stored.

!!! warning
    Switching modes in either direction affects compliance results immediately after restart.
    Enabling `multi_tenant_mode` without tenant-scoped Validated Software records will cause
    tenanted devices to show zero matching validations. Disabling it will revert tenanted
    devices to global-only matching; if those devices have no global Validated Software records,
    compliance will also drop to zero until the setting is re-enabled.

!!! warning
    `ValidatedSoftwareLCM` records that have **only** `device_tenants` set, with no
    `device_types`, `device_roles`, `devices`, `inventory_items`, or `object_tags`
    assigned, will fail form validation after disabling `multi_tenant_mode`. In legacy
    mode, `device_tenants` does not count toward the required "at least one object"
    assignment, so these records cannot be saved in their current state. Before
    disabling the flag, either add a second assignment criterion to any tenant-only
    records, or accept that they will need to be updated before they can be edited.
    These records will also have no compliance effect while the flag is off.

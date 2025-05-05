# v3.0 Release Notes

This document describes all new features and changes in the release. The format is based on [Keep a
Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic
Versioning](https://semver.org/spec/v2.0.0.html).

!!! warning
    Please do not install version 3.0.0 and instead upgrade directly to version 3.0.1. Version 3.0.1 fixes a bug in the migrations introduced in version 3.0.0 that could prevent Nautobot from starting for certain combinations of DLM objects.

## Release Overview

**Device Lifecycle Management App** version 3.0 now supports these core Nautobot models: SoftwareVersion, SoftwareImageFile, and Contact.

These models were introduced in Nautobot 2.2.0 as functional equivalents to the now deprecated DLM models. **DLM models will be removed in version 4.2**. The table below shows the corresponding model in core that matches each DLM model.

| Core model | DLM model |
| :---- | :---- |
| SoftwareVersion | SoftwareLCM |
| SoftwareImageFile | SoftwareImageLCM |
| Contact | ContactLCM |

The DLM models and their instances will remain in place to ensure a smooth migration and prevent data loss.

!!! note
    After installing app version 3.0, all existing instances of these models must be moved to the core models. This will enable full DLM app functionality. The migration process is outlined in the [Migrating to DLM app version 3.0](../migrating_to_v3.md) guide.

!!! warning
    Ensure that the DLM app is at least version 3.0.1 and Nautobot is version 2.2.0 or later before starting migration.


### Added

#### Device Hardware Notice Reporting

A new reporting type, **Device Hardware Notice Report**, has been introduced. This report identifies affected device types and the quantity of device instances impacted by hardware notices. This functionality mirrors the existing validated software reporting.

### Device View with Contracts

The device detail page will display up to five contracts, sorted by end date (latest first). Inventory item detail pages will also display contract information for associated items.

<!-- towncrier release notes start -->

## [v3.0.1 (2025-04-24)](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/releases/tag/v3.0.1)

### Fixed

- [#450](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/450) - Fixed invalid uniqueness constraints on ValidatedSoftwareLCM and VulnerabilityLCM models in 3.0 database migrations.


## [v3.0.0 (2025-04-03)](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/releases/tag/v3.0.0)

No changes from the beta. DLM app v3.0.0 is now considered stable.

## [v3.0.0b1 (2025-03-18)](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/releases/tag/v3.0.0b1)

### Added

- [#404](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/404) - Added a note to the placeholder software image files for Nautobot v2.2.0-v2.3.0.
- [#405](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/405) - Added a banner to all device lifecycle management views if any of the SoftwareLCM, SoftwareImageLCM or ContactLCM models have not been migrated to core models.

### Fixed

- [#290](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/290) - Updated HardwareLCMFilterSet filter field names for compatibility with nautobot-ansible plugin module.

### Housekeeping

- [#430](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/430) - The CHANGELOG.md file has been deprecated in favor of project release notes located in /docs.
- [#423](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/pull/423) - Rebaked from the cookie `nautobot-app-v2.4.0`.
- [#401](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/pull/401) - Rebaked from the cookie `nautobot-app-v2.4.1`.
- [#381](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/pull/381) - Rebaked from the cookie `nautobot-app-v2.4.2`.

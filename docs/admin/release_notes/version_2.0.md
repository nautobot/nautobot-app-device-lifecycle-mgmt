# v2.0 Release Notes

This document describes all new features and changes in the release `2.0`. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Release Overview

This release adds support for [Nautobot v2.0.0](https://github.com/nautobot/nautobot/releases/tag/v2.0.0).

## [v2.0.0] - 2023-09-29

### Added

- [#207](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/207) - Add support for Python 3.11.
- [#207](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/207) - Add uniqueness constraints to `ValidatedSoftwareLCM` and `VulnerabilityLCM` models.

### Changed

- [#207](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/207) - Metric `hw_end_of_support_site_gauge` has been renamed to `hw_end_of_support_location_gauge`. This now uses `location` label instead of `site`.
- [#207](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/207) - `CVELCM` to `SoftwareLCM` relationship is now represented by `affected_softwares` M2M field on the `CVELCM` model. Reverse relationships on the `SoftwareLCM` model is accessed via `corresponding_cves` field.
- [#207](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/207) - `ContractLCM` to `Device` relationship is now represented by `devices` M2M field on the `ContractLCM` model. Reverse relationships on the `Device` model is accessed via `device_contracts` field.
- [#207](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/207) - Replace all references to `slug` field with the primary key for each relevant model.
- [#207](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/207) - Replace all references to `device_role` field with `role` when working with `Device` model.
- [#207](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/207) - Replace references to `Site` model with `Location` model.
- [#207](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/207) - Simplify serializers. All serializers now inherit from `NautobotModelSerializer`.
- [#207](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/207) - All forms now inherit from `NautobotModelForm`.
- [#207](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/207) - Migrate jobs to Nautobot 2.0 standard.
- [#207](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/207) - Update tests for Nautobot 2.0.
- [#207](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/207) - Migrate `View` classes to use `ViewSet`.
- [#207](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/207) - Model fields of type `TextField` and `CharField` that allowed Null values no longer do so and default to an empty string "".
- [#207](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/207) - `ContractLCM` to `InventoryItem` relationship key renamed from `contractlcm-to-inventoryitem` to `contractlcm_to_inventoryitem`. This is enforced by Nautobot 2.0.
- [#207](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/207) - Validated Software Device report url changed from `validated-software/device-report/` to `validated-software-device-report/` due to viewset routing changes.
- [#207](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/207) - Validated Software Inventory Items report url changed from `validated-software/inventoryitem-report/` to `validated-software-inventoryitem-report/` due to viewset routing changes.

### Removed

- [#207](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/207) - Remove support for Python 3.7.
- [#207](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/207) - Remove nested serializers.
- [#207](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/207) - Remove `to_csv()` csv export method from model classes. Rely on default csv export provided by Nautobot 2.0.
- [#207](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/207) - Remove unused dry-run option from jobs.

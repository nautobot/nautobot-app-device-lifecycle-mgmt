# CHANGELOG

## [v1.6.1] - 2024-02-04
### Added
- [#287](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/pull/287) - Adds support for Python 3.11

## [v1.6.0] - 2024-01-26
### Added
- [#217](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/pull/217) - Adds new tab "Contract devices" to the Contract details view. Adds "Contract devices" export feature to the Contract details view. Adds new tab "Contract inventory items" to the Contract details view. Adds "Contract inventory items" export feature to the Contract details view. Linting targeting Python 3.8

### Fixed
- [#275](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/pull/275) - Updated in cve_tracking.py job in order to get the Related Software Relationships fetched from the CVELVM database query. That way we reduce the DB queries and the overall execution time of the Job.
- [#248](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/pull/248) - Fixes issue with number field not showing up in UI and API. Fixes model validation to match UI validation. This ensures provider and contract_type fields are set. Adds missing tests. Addresses #242.
- [#259](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/pull/259) - Fixes incorrect query used to generate nautobot_lcm_hw_end_of_support_per_part_number metric.


## [v1.3.3] - 2023-09-29

### Changed
- [#157](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/157) Changes development use of `docker-compose` as standalone to Docker's built-in `docker compose`.


## [v1.3.2] - 2023-08-02
### Changed
- [#200](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/200) Provides more clarity by adding in device and inventory item name to help identify. Fix API name and making columns sortable.

## [v1.3.1] - 2023-07-29

### Added
- [#196](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/196) Adds reverse relationship from device type to software image.
- [#194](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/194) Adds table with matching ValidatedSoftware objects to the DeviceType detailed view in GUI.

### Removed
- [#197](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/197) Removes compatibility code for Nautobot versions < 1.4


## [v1.3.0] - 2023-06-17

### Added
- [#165](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/165) Add Portal URL to API and Template.
- [#170](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/170) Add download url column to SoftwareImage table.
- [#166](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/166) Add Hashing Algorithm to Image Model.
- [#151](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/151) Hacky friday DLCM metrics.
- [#176](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/176) Rewrite software validation metric generation using queries with annotations.
- [#148](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/148) Prometheus Metrics.
- [#175](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/175) Add Notes urls to all models.
- [#156](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/156) Add functionality summary page.

### Removed
- [#168](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/168) Delete unused admin interface.

### Changed
- [#161](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/161) Update the debug env variable name to NAUTOBOT_DEBUG.
- [#178](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/178) Make HW End Of Support metric names consistent.

### Fixed
- [#184](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/pull/184) address docker compose development environment.

## v1.2.0 - 18-04-2023

### Added

- #137: Add testing against the upstream version of Nautobot.
- #140: Add progress info log messages to the Generate Vulnerabilities job.

### Changed

- #130: Change plural for Software and Validated Software models. Use generic template as the base for details templates.
- #131: Update documentation.
- #160: Define default columns for the Software list view.

**!!! NOTE**

- This release increases minimum supported Nautobot version to 1.4.0.

## v1.1.2 - 12-07-2022

### Fixed

- #123: Fixed CustomFieldModelFilterSet import source
- #124: Remove testing of permissions on plugin

## v1.1.1 - 11-22-2022

### Fixed

- PR#119 - remove requirement for `["barchart_bar_width", "barchart_width", "barchart_height"]` settings to be in `nautobot_config.py` (honoring sane defaults from PR#83)

**!!! NOTE**

- This version also addresses some CI issues with the latest version of Nautobot Core around tests for bulk CSV.

## v1.1.0 - 11-04-2022

- PR#111: Fixes project reference URLs displayed on PyPi package page.
- PR#109: Fixes Hardware Notices Table sorting bug.
- PR#108: Fixes missing view GUI errors for some of the list views.
- PR#100: Adds compatibility for Nautobot 1.4. Fixes to pipeline, API serializers, filters and unit tests.
- PR#90: Fixes Validate Software logic for computing `valid since` attribute.
- PR#84: Add to defaults, and document, settings needed for report generation.

**!!! NOTE**

- This release increases minimum supported Nautobot version to 1.2.0.
- Support for Python 3.6 has been removed. Minimum supported Python version is 3.7.

## v1.0.2 - 03-10-2022

### Fixed

- PR#76: Fixes data migration bug, between Software and Software Image, when upgrading from version < v1.0.0.

## v1.0.1 - 03-09-2022

### Fixed

- PR#72: Fixes Software Images tab rendering error in the Software details view when Software does not have Software Images linked.
- PR#73: Fixes occasional post migrate signal failure.

## v1.0.0 - 03-02-2022

### Added

- PR#55: Added Software Image model.

### Removed

- PR#55: Removed image related fields from Software model.

**!!! NOTE** This release contains backwards incompatible changes. Software model fields `image_file_name`, `download_url` and `image_file_checksum` have been removed.

As part of the migrations to v1.0.0, a Software Image object, linked to relevant Software object, will be automatically created for each Software that had software image defined.

## v0.4.1 - 02-18-2022

- PR#65: Fixed buttons for non-superuser on many model Detail views

## v0.4.0 - 02-08-2022

- PR#47: Added Plugin Upgrade Guide to the README
- PR#50: Fixed view permissions for Device Notices
- PR#57: Added CVE Tracking model and Vulnerability model

## v0.3.0 - 12-14-2021

- PR#39: Adds feature-rich reporting functionality for Software Validation.
- PR#37: Fixes GraphQL incompatibility with Nautobot >= 1.2.0.
- PR#36: Adds documentation for the Software Lifecycle part of the plugin.
- PR#33: Updates Hardware LCM to support MySQL Compliant Queries.
- PR#32: Refactors ValidatedSoftwareLCM model to support assignment to multiple objects.

## v0.2.2 - 10-07-2021

- PR#30: Documentation updates for initial release.
- PR#29: Updates case on LifeCycle to be Lifecycle.
- PR#29: Changes visual representation of Providers to be Vendors.
- PR#29: Updates documentation image for Hardware Notices.

## v0.2.1 - 10-24-2021

- PR#26: Sets view permissions on all models in the navigation menu.
- PR#26: Fixes navigation menu for Contract Imports.
- PR#25: Add documentation for use-cases and plugin info to repo.
- PR#20: Adds `valid` property to the validated software serializers.
- PR#18: Adds CSV export option to software and validated software models.

## v0.2.0 - 09-22-2021

- **Adds Maintenance/Service Contracts to the Lifecycle Plugin.**
- **Adds Software and Validated Software tracking to the Lifecycle Plugin.**

## v0.1.0 - 08-05-2021

- Initial fork and rename of project from [Nautobot EoX Notices](https://github.com/FragmentedPacket/nautobot-eox-notices)
- Rename model and related references to the Device Lifecycle Management naming scheme.
- Add comments and documentation URL to the hardware model.
- Remove devices relationship to the hardware model.
- Add `expired` as a filter on to the REST API.
- Add travis.yml and associated pipeline.
- Set bulk import device_type to use the model instead of the slug.
- Adds dynamic menu depending on the version of nautobot running.
- Handles table not existing prior to migrations.
- Add GraphQL endpoint for the Device Lifecycle Hardware model.
- Add `InventoryItem.part_id` field to the Hardware model association options.
- Add shell_plus and ipython to dev dependencies.

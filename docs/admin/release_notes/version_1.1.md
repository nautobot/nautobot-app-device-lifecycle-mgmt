# v1.1 Release Notes

This document describes all new features and changes in the release `1.1.X`. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Release Overview
This release includes some of the following highlights:

 - New mixin name from Nautobot version 1.5.2 that can cause issues with post_upgrade tasks (related to CustomFieldModelFilterSet).  Additionally, the testing of permissions on the plugin were modified slightly for features not in use.
 - Modifies the barchart dimension default behavior and removes the requirement for barchart details to be included in the `nautobot_config.py` file.
 - Addresses some CI issues with the latest version of Nautobot Core around tests for bulk CSV.
 - Addresses a new mixin name from Nautobot version 1.5.2 that can cause issues with post_upgrade tasks (related to CustomFieldModelFilterSet).  Additionally, the testing of permissions on the plugin were modified slightly for features not in use.


## [v1.1.2] - 2022-12-07

### Added

### Changed

### Fixed

- [#123](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/issues/123) Fixed CustomFieldModelFilterSet import source
- [#123](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/issues/124) Remove testing of permissions on plugin


## [v1.1.1] - 2022-11-04
!!! warning "Note - change in plugin default config!"
    v1.1.1 Modifies the barchart dimension default behavior and **removes** the requirement for barchart details to be included in the `nautobot_config.py` file.
    - details can be found in PR [#119](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/issues/119)

### Added

### Changed
 - [#119](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/issues/119) remove requirement for `["barchart_bar_width", "barchart_width", "barchart_height"]` settings to be in `nautobot_config.py` (honoring sane defaults from [#83](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/issues/83))

### Fixed


## [v1.1.0] - 2022-12-07

### Added
- [#84](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/issues/84) Add to defaults, and document, settings needed for report generation.
- [#100](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/issues/100) Adds compatibility for Nautobot 1.4. Fixes to pipeline, API serializers, filters and unit tests.

### Changed

### Fixed
- [#111](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/issues/111) Fixes project reference URLs displayed on PyPi package page.
- [#109](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/issues/109) Fixes Hardware Notices Table sorting bug.
- [#108](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/issues/108) Fixes missing view GUI errors for some of the list views.
- [#90](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/issues/90) Fixes Validate Software logic for computing `valid since` attribute.

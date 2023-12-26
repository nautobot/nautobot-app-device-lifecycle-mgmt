# v1.3 Release Notes

This document describes all new features and changes in the release `1.3.X`. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Release Overview
This release includes some of the following highlights:

 - improved software reporting with new functional summary page and links
 - Application level prometheus metrics
 - Nautobot "Notes" feature added to all models
 - Removed unused admin interface
 - Updates to development env standards
 - Adds table for matching ValidatedSoftware objects
 - Removes compatibility code for Nautobot versions <1.4

## [v1.3.2] - 2023-08-02
### Changed
- [#200](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/pull/200) Provides more clarity by adding in device and inventory item name to help identify. Fix API name and making columns sortable.


## [v1.3.1] - 2023-07-29

### Added
- [#196](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/pull/196) Adds reverse relationship from device type to software image.
- [#194](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/pull/194) Adds table with matching ValidatedSoftware objects to the DeviceType detailed view in GUI.


### Removed
- [#197](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/pull/197) Removes compatibility code for Nautobot versions < 1.4

## [v1.3.0] - 2023-06-17

### Added
- [#165](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/pull/165) Add Portal URL to API and Template.
- [#170](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/pull/170) Add download url column to SoftwareImage table.
- [#166](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/pull/166) Add Hashing Algorithm to Image Model.
- [#151](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/pull/151) Hacky friday DLCM metrics.
- [#176](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/pull/176) Rewrite software validation metric generation using queries with annotations.
- [#148](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/pull/148) Prometheus Metrics.
- [#175](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/pull/175) Add Notes urls to all models.
- [#156](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/pull/156) Add functionality summary page.

### Removed
- [#168](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/pull/168) Delete unused admin interface.

### Changed
- [#161](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/pull/161) Update the debug env variable name to NAUTOBOT_DEBUG.
- [#178](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/pull/178) Make HW End Of Support metric names consistent.

### Fixed
- [#184](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/pull/184) address docker compose development environment.

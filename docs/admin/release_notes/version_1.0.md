# v1.0 Release Notes

This document describes all new features and changes in the release `1.0.X`. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Release Overview
This release includes some of the following highlights:
 - Fixes a data migration bug when upgrading from versions older than 1.0.0
 - Fixes tab rendering for software details pages when no software images are linked
 - Fixes intermittent post migrate signal failure
 - Removed image related fields from software model (back compatibility references listed below)

- Major features or milestones
- Achieved in this `x.y` release
- Changes to compatibility with Nautobot and/or other apps, libraries etc.

## [v1.0.1] - 2021-09-08

### Added

### Changed

### Fixed

- [#123](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/123) Fixed Tag filtering not working in job launch form


## [v1.0.1] - 2022-03-09

### Added

### Changed

### Fixed

- [#72](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/72) Fixes Software Images tab rendering error in the Software details view when Software does not have Software Images linked.
- [#73](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/73) Fixes occasional post migrate signal failure.


## [v1.0.0] - 2022-03-02
!!! warning "Note: - This release contains backwards incompatible changes."
    - Software model fields `image_file_name`, `download_url` and `image_file_checksum` have been removed.

### Added
- [#55](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/55) Added Software Image model.

### Changed
- [#55](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/55) Removed image related fields from Software model.

### Fixed



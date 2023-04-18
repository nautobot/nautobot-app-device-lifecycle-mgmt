# v1.2 Release Notes

This document describes all new features and changes in the release `1.2.X`. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Release Overview
This release includes some of the following highlights:

 - Adds progress log messages to the Generate Vulnerabilities job.
 - Defines columns visible by default in the Software list view. The custom relationships columns are now hidden by the default.
 - Changes plural form used Software and Validated Software models.
 - Improves documentation and updates the documentation layout to the latest Nautobot standard.
 - Changes base template used by detail templates to the template provided by the core Nautobot.
 - Adds compatibility testing with the latest Nautobot releases.
 - Updates development environment to the latest Nautobot standard.


## [v1.2.0] - 2023-04-18
!!! warning "Note: - This release increases minimum supported Nautobot version to 1.4.0."

### Added
- [#137](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/issues/137) Add testing against the upstream version of Nautobot.
- [#140](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/issues/140) Add progress info log messages to the Generate Vulnerabilities job.

### Changed

- [#130](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/issues/130): Change plural for Software and Validated Software models. Use generic template as the base for details templates.
- [#131](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/issues/131): Update documentation.
- [#160](https://github.com/nautobot/nautobot-plugin-device-lifecycle-mgmt/issues/160): Define default columns for the Software list view.

### Fixed

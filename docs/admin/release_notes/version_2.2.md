# v2.2 Release Notes

This document describes all new features and changes in the release `2.2`. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Release Overview

This release adds support for Python 3.12 and Django 4.

## [v2.2.0 (2024-09-06)](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/releases/tag/v2.2.0)

### Added

- [#325](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/325) - Added `enabled_metrics` setting to allow selective enabling of metrics.
- [#328](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/328) - Updated the max character length on majority of text fields.
- [#344](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/344) - Added number field to Contract retrieve template.
- [#348](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/348) - Updated Device Software Validation Reports Bar Graph x-axis label modification.
- [#353](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/353) - Added Tag column to Contract list view
- [#353](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/353) - Added the ability to filter Contracts based on Tags
- [#360](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/360) - Added support for Django 4.
- [#367](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/367) - Added support for Python 3.12.

### Changed

- [#325](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/325) - DLM metrics are now disabled by default.

### Fixed

- [#343](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/343) - Fix logic populating the "Inventory Part ID" drop-down in the create/edit form for the Hardware Notice.
- [#353](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/353) - Fixed exporting of Contracts to include Tags.
- [#360](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/360) - Fixed Nautobot v2.3 incompatibility.

### Documentation

- [#346](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/346) - Updated documentation pages to be populated.

### Housekeeping

- [#323](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/323) - prepare for 2.1.1 release and fix doc builds.
- [#366](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/366) - Rebake with the 2.3 release of Nautobot-App-Cookiecutter.
- [#371](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/371) - Rebaked from the cookie `nautobot-app-v2.3.2`.

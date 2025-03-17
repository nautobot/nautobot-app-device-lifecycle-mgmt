# v2.2 Release Notes

This document describes all new features and changes in the release `2.2`. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Release Overview

This release adds support for Python 3.12 and Django 4.

## [v2.2.1 (2025-01-29)](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/releases/tag/v2.2.1)

This version includes UI template updates, CVE status filter fixes, and adds Tags to APIs. 

### Changed

- [#261](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/261) - Updated template extensions to align with standard Nautobot UI views.

### Fixed

- [#255](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/255) - Added status to bulk update for CVE. Fixed CVE status filter.
- [#392](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/392) - Added Tags to the appropriate APIs.

### Housekeeping

- [#261](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/261) - Added management command `generate_app_test_data` to generate sample data for development environments.
- [#385](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/385) - Changed `model_class_name` in `.cookiecutter.json` to a valid model to help with drift management.
- [#410](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/410) - Fixed mysql tests and reenabled mysql tests in CI.


## [v2.2.0 (2024-09-07)](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/releases/tag/v2.2.0)

### Added

- [#367](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/367) - Added support for Python 3.12.

### Fixed

- [#343](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/343) - Fix logic populating the "Inventory Part ID" drop-down in the create/edit form for the Hardware Notice.

### Housekeeping

- [#366](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/366) - Rebake with the 2.3 release of Nautobot-App-Cookiecutter.
- [#371](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/371) - Rebaked from the cookie `nautobot-app-v2.3.2`.

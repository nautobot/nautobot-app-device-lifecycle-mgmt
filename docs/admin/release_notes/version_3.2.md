
# v3.2 Release Notes

This document describes all new features and changes in the release. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Release Overview

Device Lifecycle Management App version 3.2.0 adds support for ArubaOS and PanOS in NIST CVE discovery and several UI and backend improvements.

## [v3.2.0 (2025-10-24)](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/releases/tag/v3.2.0)

!!! warning
    This release increases the minimum supported Nautobot version to 2.4.20.

!!! warning
    This release drops support for Python 3.9. Python 3.10 is now the minimum required version.

### Added

- [#483](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/483) - Added support for ArubaOS and PanOS in NIST CVE with netutils update 1.14.1.

### Fixed

- [#468](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/468) - Update the netutils version to be minimum of 1.14.1 to fix the cisco_nxos scan in NIST.
- [#479](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/479) - Restore the Software valid/invalid panel for Device and InventoryItem objects with an assigned Software version, which was erroneously removed in version 3.0.
- [#481](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/481) - Fixes UI forms that displayed fields linked to the deprecated DLM models.

### Documentation

- [#459](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/459) - Adds an entry to the FAQ explaining the solution to the DLM 3.x `AttributeError` when navigating to the Device and Inventory Item list views.
- [#477](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/477) - Updates multiple screenshots to reflect changes to the UI and show core model references.
- [#485](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/485) - Added Analytics GTM template override only to the public ReadTheDocs build.

### Housekeeping

- [#495](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/495) - Fixed template linting issues identified by Django Lint.
- Rebaked from the cookie `nautobot-app-v2.5.1`.
- Rebaked from the cookie `nautobot-app-v2.6.0`.

# v4.0 Release Notes

This document describes all new features and changes in the release. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Release Overview

This major release marks the compatibility of the Device Lifecycle Management App with Nautobot 3.0.0. Check out the [full details](https://docs.nautobot.com/projects/core/en/stable/release-notes/version-3.0/) of the changes included in this new major release of Nautobot. Highlights:

* Minimum Nautobot version supported is 3.0.
* Added support for Python 3.13 and removed support for 3.9.
* Updated UI framework to use latest Bootstrap 5.3.

We will continue to support the previous major release for users of Nautobot LTM 2.4 only with critical bug and security fixes as per the [Software Lifecycle Policy](https://networktocode.com/company/legal/software-lifecycle-policy/).

<!-- towncrier release notes start -->
## [v4.0.1 (2026-02-18)](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/releases/tag/v4.0.1)

### Changed

- [#512](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/512) - Allowed cloning of validated software objects.

### Fixed

- [#529](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/529) - Fixed global search for Vendors.
- [#533](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/533) - Fixed duplicate "Software Version" column labels on the Devices and Inventory Items list views.
- [#554](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/554) - Fixed an issue rendering Validated Software in the UI before running the job to migrate to the core models.

### Documentation

- [#540](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/540) - Updated documentation to include 3.0 screenshots.

### Housekeeping

- [#490](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/490) - Refactored DeviceHardwareNoticeResult, DeviceSoftwareValidationResult, InventoryItemSoftwareValidationResult model related UI views to use `NautobotUIViewSet`.
- [#494](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/494) - Refactored HardwareLCM,ValidatedSoftwareLCM,ContractLCM,ProviderLCM,CVELCM,VulnerabilityLCM model related UI views to use `UI component framework`.
- [#498](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/498) - Updated generate_dlm_test_data management command for DLM v3.
- [#498](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/498) - Added --flush argument to generate_dlm_test_data management command.
- [#498](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/498) - Added change logging to generate_dlm_test_data management command.
- [#506](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/506) - Update any call to `get_extra_context` to call super of the method first.
- [#539](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/539) - Refactored imports to use `nautobot.apps` and simplified existing import statements.
- Rebaked from the cookie `nautobot-app-v2.7.0`.
- Rebaked from the cookie `nautobot-app-v2.7.1`.
- Rebaked from the cookie `nautobot-app-v3.0.0`.

## [v4.0.0 (2025-11-17)](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/releases/tag/v4.0.0)

### Added

- Added support for Python 3.13.
- Added support for Nautobot 3.0.

### Changed

- [#514](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/514) - Updated navigation menu icon and weights to match Nautobot standard.

## [v4.0.0a2 (2025-11-06)](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/releases/tag/v4.0.0a2)

## [v4.0.0a1 (2025-11-04)](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/releases/tag/v4.0.0a1)

# v4.1 Release Notes

This document describes all new features and changes in the release. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Release Overview

- Added a Status field to the ContractLCM model.
- Added Python 3.14 support.

<!-- towncrier release notes start -->

## [v4.1.1 (2026-04-10)](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/releases/tag/v4.1.1)

### Added

- [#576](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/576) - Added `nautobot_device_lifecycle_mgmt_hardware_end_of_sale` Device filter extension.
- [#576](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/576) - Added `nautobot_device_lifecycle_mgmt_hardware_end_of_software_releases` Device filter extension.
- [#576](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/576) - Added `nautobot_device_lifecycle_mgmt_hardware_end_of_security_patches` Device filter extension.
- [#576](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/576) - Added `nautobot_device_lifecycle_mgmt_hardware_end_of_support` Device filter extension.
- [#576](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/576) - Added `nautobot_device_lifecycle_mgmt_software_version_end_of_support_date` Device filter extension.
- [#576](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/576) - Added `nautobot_device_lifecycle_mgmt_has_cves` Software Version filter extension.

### Housekeeping

- Rebaked from the cookie `nautobot-app-v3.1.3`.

## [v4.1.0 (2026-03-20)](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/releases/tag/v4.1.0)

### Added

- Added Python 3.14 support.
- [#337](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/337) - Added a Status field to ContractLCM for lifecycle purposes.

### Fixed

- [#557](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/557) - Corrected typo `unsuported` in "Device Hardware Notice Report" graph.

### Dependencies

- [#557](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/557) - Widened range of permitted versions of `numpy` dependency to permit 2.x versions as well.

### Housekeeping

- Rebaked from the cookie `nautobot-app-v3.1.2`.

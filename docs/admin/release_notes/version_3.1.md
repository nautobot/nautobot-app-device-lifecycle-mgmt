# v3.1 Release Notes

This document describes all new features and changes in the release. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Release Overview

Device Lifecycle Management App version 3.1.0 introduces automated CVE discovery and several UI and backend improvements.

- The new NIST integration allows you to automatically discover and associate CVEs to all software versions in Nautobot that are known to NIST.
- No special upgrade steps are required from 3.0.X, but it is recommended to review the [upgrade guide](../upgrade.md) for general instructions if you are coming from earlier versions.

## [v3.1.1 (2025-06-03)](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/releases/tag/v3.1.1)

### Fixed

- [#465](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/465) - Fixed large traceback being generated in the logs when a 404 was raised.

## [v3.1.0 (2025-05-24)](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/releases/tag/v3.1.0)

### Added

- [#80](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/80) - Added a field in the CVE model for last_modified_date.
- [#440](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/440) - Added job that will automatically obtain and associate CVEs to all software versions in Nautobot that are known to NIST.

### Changed

- [#439](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/439) - Changed the Device list on an individual Contract's view to a count of devices with a link to the Device list filtered by the Contract.
- [#441](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/441) - Changed the Validated Software detail view to move the lists of assigned items to separate tabs.

### Fixed

- [#462](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/462) - Improved error handling and logging for version-related issues in jobs.

### Housekeeping

- Rebaked from the cookie `nautobot-app-v2.5.0`.

# v4.1 Release Notes

This document describes all new features and changes in the release. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Release Overview

- Major features or milestones
- Changes to compatibility with Nautobot and/or other apps, libraries etc.

<!-- towncrier release notes start -->

## [v4.1.0 (2026-03-17)](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/releases/tag/v4.1.0)

### Added

- [#337](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/337) - Added a Status Field to ContractLCM for lifecycle purposes.

### Fixed

- [#557](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/557) - Corrected typo `unsuported` in "Device Hardware Notice Report" graph.

### Dependencies

- [#557](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/557) - Widened range of permitted versions of `numpy` dependency to permit 2.x versions as well.

### Housekeeping

- Rebaked from the cookie `nautobot-app-v3.1.2`.

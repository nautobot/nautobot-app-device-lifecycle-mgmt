# v2.1 Release Notes

This document describes all new features and changes in the release `2.0`. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Release Overview

This release adds support for various improvements, bug fixes, and performance improvements.

## [v2.1.1] - 2024-03-12

### Fixed
- [#313](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/pull/313) - Fixes bug that could lead to InventoryItem metric queries erroring out.

## [v2.1.0] - 2024-01-26

### Changed
- [#269](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/pull/269) - Renaming effort to standardize on Nautobot terminology for Apps/Plugins.

### Fixed
- [#277](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/pull/277) - Updated cve_tracking.py job in order to reduce the DB queries and the overall execution time of the Job. 
- [#265](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/pull/265) - Fixed incorrect query used to generate nautobot_lcm_hw_end_of_support_per_part_number metric.

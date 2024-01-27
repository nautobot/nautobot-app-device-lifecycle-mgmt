# v1.6 Release Notes

This document describes all new features and changes in the release `1.6.X`. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Release Overview
This release includes ltm1.6 support and some of the following highlights:

 - Adds new tab "Contract devices" to the Contract details view.
 - Adds "Contract devices" export feature to the Contract details view.
 - Adds new tab "Contract inventory items" to the Contract details view.
 - Adds "Contract inventory items" export feature to the Contract details view.
 - Linting targeting Python 3.8
 - Updated in cve_tracking.py job in order to get the Related Software Relationships fetched from the CVELVM database query. That way we reduce the DB queries and the overall execution time of the Job.
 - Fixes issue with number field not showing up in UI and API. Fixes model validation to match UI validation. This ensures provider and contract_type fields are set. Adds missing tests. Addresses #242.
 - Fixes incorrect query used to generate nautobot_lcm_hw_end_of_support_per_part_number metric.


## [v1.6.0] - 2024-01-26
### Added
- [#217](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/pull/217) - Adds new tab "Contract devices" to the Contract details view. Adds "Contract devices" export feature to the Contract details view. Adds new tab "Contract inventory items" to the Contract details view. Adds "Contract inventory items" export feature to the Contract details view. Linting targeting Python 3.8

### Fixed
- [#275](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/pull/275) - Updated in cve_tracking.py job in order to get the Related Software Relationships fetched from the CVELVM database query. That way we reduce the DB queries and the overall execution time of the Job.
- [#248](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/pull/248) - Fixes issue with number field not showing up in UI and API. Fixes model validation to match UI validation. This ensures provider and contract_type fields are set. Adds missing tests. Addresses #242.
- [#259](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/pull/259) - Fixes incorrect query used to generate nautobot_lcm_hw_end_of_support_per_part_number metric.

# Device Lifecycle Management 3.1.0 Release Notes

**Release Date:** May 23, 2025

## Overview
This release introduces new features, improvements, and bug fixes for the Device Lifecycle Management plugin. It is compatible with Nautobot versions 2.2.0 through 3.1.99.

## Notable Changes
- Added TypeError exception handling to provide logging on what version needs attention. The job continues after logging. ([#462](https://github.com/your-org/nautobot-plugin-device-lifecycle-mgmt/pull/462))
- Changed the Device list on an individual Contract's view to a count of devices with a link to the Device list filtered by the Contract. ([#439](https://github.com/your-org/nautobot-plugin-device-lifecycle-mgmt/pull/439))
- Changed the Validated Software detail view to move the lists of assigned items to separate tabs. ([#441](https://github.com/your-org/nautobot-plugin-device-lifecycle-mgmt/pull/441))
- Rebaked from the cookie `nautobot-app-v2.5.0`.

## Features
- Added job that will automatically obtain and associate CVEs to all software versions in Nautobot that are known to NIST. ([#440](https://github.com/your-org/nautobot-plugin-device-lifecycle-mgmt/pull/440))

## Improvements
- Improved error handling and logging for version-related issues in jobs. ([#462](https://github.com/your-org/nautobot-plugin-device-lifecycle-mgmt/pull/462))
- Added a field in the CVE model for last_modified_date. ([#80](https://github.com/your-org/nautobot-plugin-device-lifecycle-mgmt/pull/80))

## Bug Fixes
- None specifically noted for this release.

## Upgrade Notes
- No special upgrade steps required from 3.0.X.
- Review the [upgrade guide](../upgrade.md) for general instructions.

## Acknowledgements
Thanks to all contributors and testers for their feedback and support.

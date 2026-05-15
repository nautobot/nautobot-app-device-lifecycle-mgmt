# v4.2 Release Notes

This document describes all new features and changes in the release. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Release Overview

- Added opt-in multi_tenant_mode app setting (default False). When enabled, Validated Software matching becomes tenant-scoped via the device_tenants M2M on ValidatedSoftwareLCM, so a device only matches Validated Software records associated with its tenant. When left disabled, matching behavior is unchanged from prior releases — no migration or configuration changes are required for existing deployments.
- Added Tenant filtering to the Hardware Notice and Validated Software reports. Administrators managing multi-tenant environments can now scope report output to a specific tenant (or set of tenants) when auditing hardware end-of-life exposure and software compliance.

<!-- towncrier release notes start -->

## [v4.2.0 (2026-05-15)](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/releases/tag/v4.2.0)

### Added

- [#573](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/573) - Added opt-in `multi_tenant_mode` app setting (default `False`) that enables tenant-scoped Validated Software matching via the `device_tenants` M2M on `ValidatedSoftwareLCM`. When disabled, matching behavior is identical to pre-tenancy releases.
- [#573](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/573) - Added Tenant filtering to Hardware Notice and Validated Software reports.

### Changed

- [#552](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/552) - Made a few minor wording/grammar changes to docs/user/app_use_cases.md.

### Dependencies

- [#589](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/589) - Raised pycountry upper bound to 25.0.0 to resolve deprecated pkg_resources API usage.

### Documentation

- [#573](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/573) - Documented the `multi_tenant_mode` setting and added a matching-workflow diagram to the Software Lifecycle user guide covering legacy and multi-tenant modes for tenanted and non-tenanted devices.

### Housekeeping

- [#589](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/issues/589) - Formatted release notes MD files to prevent markdown linter errors.
- Updated the CODEOWNERS file.
- Updated the `poetry.lock` file to include the latest dependencies for development.

# v0.1 Release Notes

This document describes all new features and changes in the release `0.1.X`. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Release Overview

- Initial fork and rename of project from [Nautobot EoX Notices](https://github.com/FragmentedPacket/nautobot-eox-notices)
- Rename model and related references to the Device Lifecycle Management naming scheme.
- Add comments and documentation URL to the hardware model.
- Remove devices relationship to the hardware model.
- Add `expired` as a filter on to the REST API.
- Add travis.yml and associated pipeline.
- Set bulk import device_type to use the model instead of the slug.
- Adds dynamic menu depending on the version of nautobot running.
- Handles table not existing prior to migrations.
- Add GraphQL endpoint for the Device Lifecycle Hardware model.
- Add `InventoryItem.part_id` field to the Hardware model association options.
- Add shell_plus and ipython to dev dependencies.

## [v0.1.0] - 2021-08-05
Initial release

### Added

### Changed

### Fixed


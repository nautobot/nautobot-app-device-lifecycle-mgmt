# CHANGELOG

## v0.2.1 - 10-24-2021
- Fixes navigation menu for Contract Imports.
- PR#25: Add documentation for use-cases and plugin info to repo.
- PR#20: Adds `valid` property to the validated software serializers. 
- PR#18: Adds CSV export option to software and validated software models.

## v0.2.0 - 09-22-2021
- **Adds Maintenance/Service Contracts to the LifeCycle Plugin.**
- **Adds Software and Validated Software tracking to the LifeCycle Plugin.**


## v0.1.0 - 08-05-2021
- Initial fork and rename of project from [Nautobot EoX Notices](https://github.com/FragmentedPacket/nautobot-eox-notices)
- Rename model and related references to the Device LifeCycle Management naming scheme. 
- Add comments and documentation URL to the hardware model.
- Remove devices relationship to the hardware model.
- Add `expired` as a filter on to the REST API.
- Add travis.yml and associated pipeline.
- Set bulk import device_type to use the model instead of the slug.
- Adds dynamic menu depending on the version of nautobot running.
- Handles table not existing prior to migrations.
- Add GraphQL endpoint for the Device LifeCycle Hardware model.
- Add `InventoryItem.part_id` field to the Hardware model association options.
- Add shell_plus and ipython to dev dependencies. 


# CHANGELOG

## 1.0.0-beta.0 - 08-05-2021
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
- Add `InventoryItem.part_id` custom relationship to the Hardware model.
- Add shell_plus and ipython to dev dependencies. 


# Adding Data to Device Life Cycle Plugin

To add data into the Device Life Cycle Plugin, you need to either add it manually throught the UI, or through the REST API endpoint. In this current version there is no synchronization of data from a vendor API endpoint, but this may be a feature request in the future.

## Plugin API Definition

To add information via the REST API, please look at the Swagger API docs for the plugin once installed. This will provide you the same documentation for working with other devices.

## UI - Additions

### Hardware Lifecycle

When running Nautobot 1.1.0 or later, there is a separate menu added named `Device Lifecycle`. This will be seen on the top menu bar. From here you will find the typical navigation for the addition of items. For example, to add a Hardware Notice for end of life, select `Device LifeCycle` -> Plus sign next to `Hardware Notices`. This will bring up the new Hardware notice page. In this page, fill out the appropriate information from the drop down menus to create the hardware notice.

> In order for a hardware notice to be created, there must be either an existing Device Type or Inventory Item that can be found in the database. Without these data points, the data cannot be added, as a relationship is built to the particular items.

### Software

Software follows the same methodology. First you add Software that is applicable for a particular platform. Then fill in the required fields of Version and add the corresponding relationships.

### Maintenance Contracts

The maintenance contracts has a similar feel as the Circuit Providers as part of the core of Nautobot. There is a `Vendor` that provides the particular maintenance contract. Then individual `Contracts` are associated with the vendor. As an optional add on a Point of Contact can be made to associate with the contract and named escalation tree if required.

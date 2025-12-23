# Using the App

This document describes common use-cases and scenarios for this App.

## General Usage

### Adding Information into the App

To add data into the Device Life Cycle App, you need to either add it manually throughout the UI, or through the REST API endpoint. In this current version there is no synchronization of data from a vendor API endpoint, but this may be a feature request in the future.

#### App API Definition

To add information via the REST API, please look at the Swagger API docs for the app once installed. This will provide you the same documentation for working with other devices.

#### Hardware Lifecycle

When running Nautobot 1.1.0 or later, there is a separate menu added named `Device Lifecycle`. This will be seen on the top menu bar. From here you will find the typical navigation for the addition of items. For example, to add a Hardware Notice for end of life, select `Device Lifecycle` -> Plus sign next to `Hardware Notices`. This will bring up the new Hardware notice page. In this page, fill out the appropriate information from the drop down menus to create the hardware notice.

!!! note
    In order for a hardware notice to be created, there must be either an existing Device Type or Inventory Item that can be found in the database. Without these data points, the data cannot be added, as a relationship is built to the particular items.

#### Maintenance Contracts

The maintenance contracts has a similar feel as the Circuit Providers as part of the core of Nautobot. There is a `Vendor` that provides the particular maintenance contract. Then individual `Contracts` are associated with the vendor.

#### Validated Software

To track software for organizationally approved devices or inventory items in Nautobot, you can utilize the Validated Software feature. Begin by adding the Software Version applicable to the specific platform within the core Nautobot framework. Subsequently, create a Validated Software entry linked to the Software Version, specifying the conditions that determine software approval within your operational environment..

### CVE Tracking

Read more about [CVE Tracking](cve_tracking.md).

## Use-cases and common workflows

Read more about [Software Lifecycle](software_lifecycle.md) use-cases.

## Screenshots

### Hardware: Device Lifecycle Management List View

You can view the list of Hardware/Software notices as well as filter the table.

![](../images/ss_lcm_hardware_list_view_light.png#only-light){ .on-glb }
![](../images/ss_lcm_hardware_list_view_dark.png#only-dark){ .on-glb }
[//]: # "`https://next.demo.nautobot.com/plugins/nautobot-device-lifecycle-mgmt/hardware/`"


### Hardware: Device Lifecycle Management Detail View

You can also click a Hardware/Software Notice and see the detail view. This view provides links to the devices that are part affected by this EoX notice due to their device type.

![](../images/ss_lcm_hardware_detail_view_light.png#only-light){ .on-glb }
![](../images/ss_lcm_hardware_detail_view_dark.png#only-dark){ .on-glb }
[//]: # "`https://next.demo.nautobot.com/plugins/nautobot-device-lifecycle-mgmt/hardware/ed2aaf82-972d-57d0-9acc-c57bc30cc497/`"

### Device View

You can also view the associated Hardware notice from the device. If the device is end of life or end of support the notice will be red.

![](../images/ss_lcm_hardware_device_view_light.png#only-light){ .on-glb }
![](../images/ss_lcm_hardware_device_view_dark.png#only-dark){ .on-glb }
[//]: # "`https://next.demo.nautobot.com/dcim/devices/9a91f27d-ee91-52f5-9756-d662091b7261/`"

### Device Type View

This provides the same UI element as the device view, but within the specific device type's view.

![](../images/ss_lcm_hardware_device_type_view_light.png#only-light){ .on-glb }
![](../images/ss_lcm_hardware_device_type_view_dark.png#only-dark){ .on-glb }
[//]: # "`https://next.demo.nautobot.com/dcim/device-types/6b82c333-18b4-5f37-b58f-3705fb580c6d/`"

### Contracts: Device Lifecycle Management Contract Detail View

You can view the details of a contract along with the primary and escalation contacts. This view will also give you an association to the devices under this contract.

![](../images/ss_lcm_contract_detail_light.png#only-light){ .on-glb }
![](../images/ss_lcm_contract_detail_dark.png#only-dark){ .on-glb }
[//]: # "`https://next.demo.nautobot.com/plugins/nautobot-device-lifecycle-mgmt/contract/bf7fc26a-2b49-5231-a622-a0de6c9e76e9/`"

### Contracts: Device Lifecycle Management Contract Provider View

You can view the details of a provider, along with a listing of the service contracts associated to the provider. Contracts that are expired will display in red.

![](../images/ss_lcm_contract_provider_detail_light.png#only-light){ .on-glb }
![](../images/ss_lcm_contract_provider_detail_dark.png#only-dark){ .on-glb }
[//]: # "`https://next.demo.nautobot.com/plugins/nautobot-device-lifecycle-mgmt/provider/18b96c29-59a1-5ffa-806b-87a4baae3d57/`"

### Contracts: Device View with Contracts

Contracts associated with devices will appear on the device detail page. Five contracts at most will be displayed here, listed in order of end date (latest date first). The same information will also be displayed on inventory item detail pages for contracts associated with inventory items.

![](../images/ss_lcm_contract_device_view_light.png#only-light){ .on-glb }
![](../images/ss_lcm_contract_device_view_dark.png#only-dark){ .on-glb }
[//]: # "`https://next.demo.nautobot.com/dcim/devices/43e0c7a2-3939-5fcf-bc2f-c659f1c40d46/`"


### Software: Validated Software Lifecycle Management List View

You can view the list of Validated Software versions as well as filter the table.

![](../images/ss_lcm_validated_software_list_view_light.png#only-light){ .on-glb }
![](../images/ss_lcm_validated_software_list_view_dark.png#only-dark){ .on-glb }
[//]: # "`https://next.demo.nautobot.com/plugins/nautobot-device-lifecycle-mgmt/validated-software/`"

### Software: Validated Software Lifecycle Detail View

You can also click a Validated Software version and see the detail view. This view provides view of the device and inventory item attributes this validated software applies to.

![](../images/ss_lcm_validated_software_detail_view_light.png#only-light){ .on-glb }
![](../images/ss_lcm_validated_software_detail_view_dark.png#only-dark){ .on-glb }
[//]: # "`https://next.demo.nautobot.com/plugins/nautobot-device-lifecycle-mgmt/validated-software/13fe164e-bf1f-4419-afe5-93d6a6dc0f48/`"

### Software: Device View

You can also view the associated Software and Validated Software versions from the device. If the Software assigned to the device matches Validated Software for this device, the Software will be displayed in green. If it's invalid it will be displayed in red.

**Valid software:**

![](../images/ss_lcm_software_device_view_valid_light.png#only-light){ .on-glb }
![](../images/ss_lcm_software_device_view_valid_dark.png#only-dark){ .on-glb }
[//]: # "`https://next.demo.nautobot.com/dcim/devices/dd76f581-51cc-43b6-876a-3f90ebf93108/`"

**Invalid software:**

![](../images/ss_lcm_software_device_view_invalid_light.png#only-light){ .on-glb }
![](../images/ss_lcm_software_device_view_invalid_dark.png#only-dark){ .on-glb }
[//]: # "`https://next.demo.nautobot.com/dcim/devices/43e0c7a2-3939-5fcf-bc2f-c659f1c40d46/`"

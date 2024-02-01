# App Overview

This document provides an overview of the App including critical information and import considerations when applying it to your Nautobot environment.

The Device Lifecycle Management app aims to help in managing the lifecycle of the device hardware and software components.

!!! note
    Throughout this documentation, the terms "app" and "plugin" will be used interchangeably.

## Description

Devices and their components, both hardware, and software, have fixed-period vendor support related to updates and availability. These are also often associated with several maintenance contracts. Managing these relationships is often complex and engineering teams may lack visibility into the processes involved.

With the Device Lifecycle Management app, you can capture the processes related to the device's lifecycle in Nautobot, alongside existing device data. Lifecycle information that you can record includes:

- Hardware EOL and end-of-support dates
- Software and software image information
- Software version present on the device
- Organizationally approved software versions
- Software and hardware support contracts
- Common Vulnerabilities and Exposures (CVEs)
- Vulnerabilities affecting devices

Additionally, you can run jobs allowing you to:

- Generate a report showing whether devices are running approved software version
- Generate a report showing whether inventory items are running approved software version
- Map recorded CVEs to affected devices, which creates corresponding vulnerability objects

## Audience (User Personas) - Who should use this App?

- Organizations that want to track software running on their device.
- Organizations that want to have a centralized place for managing device and software End of Life and End Of Support notices.
- Organizations that want to manage vulnerabilities affecting their networking estate.

## Authors and Maintainers

Nautobot Device Lifecycle App is maintained by Network to Code and members of the Nautobot community.  Anyone is welcome to contribute code, issues, feature requests, etc...  

## Extras

!!! warning "Developer Note - Remove Me!"
    What is shown today in the Installed Apps page in Nautobot. What parts of Nautobot does it interact with, what does it add etc. ?

- **Software on Device** - links Software version to Device
- **Software on InventoryItem** - links Software version to Inventory Item
- **Contract to dcim.Device** - links contract to Device
- **Contract to dcim.InventoryItem** - links contract to Inventory Item
- **Software to CVE** - links Software to CVE

This app provides the following jobs:

- **Device Software Validation Report** - generates a report showing the summary of devices running valid/invalid software version
- **Inventory Item Software Validation Report** - generates a report showing the summary of inventory items running valid/invalid software version
- **Generate Vulnerabilities** - links CVEs to devices and generates vulnerability objects

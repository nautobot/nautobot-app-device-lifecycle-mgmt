# Device Lifecycle Management

<p align="center">
  <img src="https://raw.githubusercontent.com/nautobot/nautobot-app-device-lifecycle-mgmt/develop/docs/images/icon-DeviceLifecycle.png" class="logo" height="200px">
  <br>
  <a href="https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/actions"><img src="https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/actions/workflows/ci.yml/badge.svg?branch=main"></a>
  <a href="https://docs.nautobot.com/projects/device-lifecycle/en/latest/"><img src="https://readthedocs.org/projects/nautobot-plugin-device-lifecycle-mgmt/badge/"></a>
  <a href="https://pypi.org/project/nautobot-device-lifecycle-mgmt/"><img src="https://img.shields.io/pypi/v/nautobot-device-lifecycle-mgmt"></a>
  <a href="https://pypi.org/project/nautobot-device-lifecycle-mgmt/"><img src="https://img.shields.io/pypi/dm/nautobot-device-lifecycle-mgmt"></a>
  <br>
  An <a href="https://networktocode.com/nautobot-apps/">App</a> for <a href="https://nautobot.com/">Nautobot</a>.
</p>

## Overview

An app for [Nautobot](https://github.com/nautobot/nautobot) to manage device lifecycles. This app works by making related associations to Devices, Device Types, and Inventory Items to help provide data about the hardware end of life notices, appropriate software versions to be running on the devices, and the maintenance contracts associated with devices. This will help with the various aspects of planning Lifecycle events, and provides quick access to ancillary data about the devices in Nautobot.

## Key Features

    - Hardware and software lifecycle tracking for devices, device types, and inventory items.
    - Maintenance contract management and reporting.
    - **Automated CVE Discovery and NIST Integration:**
        - Automatically discover and associate CVEs to software versions in Nautobot using the NIST NVD API 2.0 ([#440](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/pull/440)).
        - Configure an External Integration and Secret for your NIST API key, then run the "NIST - Software CVE Search" job to keep your CVE data up to date.
        - See the [CVE Tracking documentation](docs/user/cve_tracking.md) for setup and usage details.

### Screenshots

More screenshots can be found in the [Using the App](https://docs.nautobot.com/projects/device-lifecycle/en/latest/user/app_use_cases/) page in the documentation. Here's a quick overview of some of the app's added functionality:

**Device Lifecycle Management List View**

You can view the list of Hardware/Software notices as well as filter the table.

![](https://raw.githubusercontent.com/nautobot/nautobot-app-device-lifecycle-mgmt/develop/docs/images/lcm_hardware_list_view.png)

**Device Lifecycle Management Detail View**

You can also click a Hardware/Software Notice and see the detail view. This view provides links to the devices that are part affected by this EoX notice due to their device type.

![](https://raw.githubusercontent.com/nautobot/nautobot-app-device-lifecycle-mgmt/develop/docs/images/lcm_hardware_detail_view.png)

**Software Lifecycle Reporting**

Reports can be created from the Nautobot's software validation jobs **Device Software Validation - Report** or **Inventory Item Software Validation - Report**.

![](https://raw.githubusercontent.com/nautobot/nautobot-app-device-lifecycle-mgmt/develop/docs/images/lcm_software_validation_report_run_graph.png)

Individual CSV files can be exported per platform or inventory item.

![](https://raw.githubusercontent.com/nautobot/nautobot-app-device-lifecycle-mgmt/develop/docs/images/lcm_software_validation_report_run_detailed_summary.png)

Sample CSV.

![](https://raw.githubusercontent.com/nautobot/nautobot-app-device-lifecycle-mgmt/develop/docs/images/lcm_software_validation_report_csv_small.png)

You can also view validation results as a list from the Nautobot GUI.

![](https://raw.githubusercontent.com/nautobot/nautobot-app-device-lifecycle-mgmt/develop/docs/images/lcm_software_validation_report_run_results_list.png)

## Try it out!

This App is installed in the Nautobot Community Sandbox found over at [demo.nautobot.com](https://demo.nautobot.com/)!

> For a full list of all the available always-on sandbox environments, head over to the main page on [networktocode.com](https://www.networktocode.com/nautobot/sandbox-environments/).

## Documentation

Full web-based HTML documentation for this app can be found over on the [Nautobot Docs](https://docs.nautobot.com) website:

- [User Guide](https://docs.nautobot.com/projects/device-lifecycle/en/latest/user/app_overview/) - Overview, Using the App, Getting Started.
- [Administrator Guide](https://docs.nautobot.com/projects/device-lifecycle/en/latest/admin/install/) - How to Install, Configure, Upgrade, or Uninstall the App.
- [Developer Guide](https://docs.nautobot.com/projects/device-lifecycle/en/latest/dev/contributing/) - Extending the App, Code Reference, Contribution Guide.
- [Release Notes / Changelog](https://docs.nautobot.com/projects/device-lifecycle/en/latest/admin/release_notes/).
- [Frequently Asked Questions](https://docs.nautobot.com/projects/device-lifecycle/en/latest/user/faq/).

### Contributing to the Docs

You can find all the Markdown source for the App documentation under the [docs](https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt/tree/develop/docs) folder in this repository. For simple edits, a Markdown capable editor is sufficient - clone the repository and edit away.

If you need to view the fully generated documentation site, you can build it with [mkdocs](https://www.mkdocs.org/). A container hosting the docs will be started using the invoke commands (details in the [Development Environment Guide](https://docs.nautobot.com/projects/device-lifecycle/en/latest/dev/dev_environment/#docker-development-environment)) on [http://localhost:8001](http://localhost:8001). As your changes are saved, the live docs will be automatically reloaded.

Any PRs with fixes or improvements are very welcome!

## Questions

For any questions or comments, please check the [FAQ](https://docs.nautobot.com/projects/device-lifecycle/en/latest/user/faq/) first. Feel free to also swing by the [Network to Code Slack](https://networktocode.slack.com/) (channel `#nautobot`), sign up [here](http://slack.networktocode.com/) if you don't have an account.

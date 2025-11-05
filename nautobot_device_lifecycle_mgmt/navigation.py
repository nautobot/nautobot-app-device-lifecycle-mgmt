"""Menu items for the Lifecycle Management app."""

from nautobot.apps.ui import NavigationWeightChoices, NavMenuGroup, NavMenuItem, NavMenuTab

menu_items = (
    NavMenuTab(
        name="Device Lifecycle",
        weight=NavigationWeightChoices.DESIGN + 50,
        groups=(
            NavMenuGroup(
                name="Hardware Notices",
                weight=100,
                items=(
                    NavMenuItem(
                        link="plugins:nautobot_device_lifecycle_mgmt:hardwarelcm_list",
                        name="Hardware Notices",
                        weight=100,
                        permissions=[
                            "nautobot_device_lifecycle_mgmt.view_hardwarelcm",
                        ],
                    ),
                ),
            ),
            NavMenuGroup(
                name="Software Lifecycle",
                weight=200,
                items=(
                    NavMenuItem(
                        link="plugins:nautobot_device_lifecycle_mgmt:validatedsoftwarelcm_list",
                        name="Validated Software",
                        weight=100,
                        permissions=[
                            "nautobot_device_lifecycle_mgmt.view_validatedsoftwarelcm",
                        ],
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_device_lifecycle_mgmt:cvelcm_list",
                        name="CVE",
                        weight=200,
                        permissions=[
                            "nautobot_device_lifecycle_mgmt.view_cvelcm",
                        ],
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_device_lifecycle_mgmt:vulnerabilitylcm_list",
                        name="Vulnerability",
                        weight=300,
                        permissions=[
                            "nautobot_device_lifecycle_mgmt.view_vulnerabilitylcm",
                        ],
                    ),
                ),
            ),
            NavMenuGroup(
                name="Contracts",
                weight=300,
                items=(
                    NavMenuItem(
                        link="plugins:nautobot_device_lifecycle_mgmt:contractlcm_list",
                        name="Contracts",
                        weight=100,
                        permissions=[
                            "nautobot_device_lifecycle_mgmt.view_contractlcm",
                        ],
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_device_lifecycle_mgmt:providerlcm_list",
                        name="Vendors",
                        weight=200,
                        permissions=[
                            "nautobot_device_lifecycle_mgmt.view_providerlcm",
                        ],
                    ),
                ),
            ),
            NavMenuGroup(
                name="Reports",
                weight=400,
                items=(
                    NavMenuItem(
                        link="plugins:nautobot_device_lifecycle_mgmt:hardwarenotice_device_report_list",
                        name="Device Hardware Notice - Report",
                        weight=100,
                        permissions=[
                            "nautobot_device_lifecycle_mgmt.view_devicehardwarenoticeresult",
                        ],
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_device_lifecycle_mgmt:devicehardwarenoticeresult_list",
                        name="Device Hardware Notice - List",
                        weight=200,
                        permissions=[
                            "nautobot_device_lifecycle_mgmt.view_devicehardwarenoticeresult",
                        ],
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_device_lifecycle_mgmt:validatedsoftware_device_report_list",
                        name="Device Software Validation - Report",
                        weight=300,
                        permissions=[
                            "nautobot_device_lifecycle_mgmt.view_validatedsoftwarelcm",
                        ],
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_device_lifecycle_mgmt:devicesoftwarevalidationresult_list",
                        name="Device Software Validation - List",
                        weight=400,
                        permissions=[
                            "nautobot_device_lifecycle_mgmt.view_devicesoftwarevalidationresult",
                        ],
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_device_lifecycle_mgmt:validatedsoftware_inventoryitem_report_list",
                        name="Inventory Item Software Validation - Report",
                        weight=500,
                        permissions=[
                            "nautobot_device_lifecycle_mgmt.view_validatedsoftwarelcm",
                        ],
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_device_lifecycle_mgmt:inventoryitemsoftwarevalidationresult_list",
                        name="Inventory Item Software Validation - List",
                        weight=600,
                        permissions=[
                            "nautobot_device_lifecycle_mgmt.view_inventoryitemsoftwarevalidationresult",
                        ],
                    ),
                ),
            ),
        ),
    ),
)

"""Menu items for the LifeCycle Management plugin."""
# pylint: disable=C0412
from nautobot.utilities.choices import ButtonColorChoices

try:
    from nautobot.core.apps import NavMenuTab, NavMenuGroup, NavMenuItem, NavMenuButton

    menu_items = (
        NavMenuTab(
            name="Device LifeCycle",
            weight=600,
            groups=(
                NavMenuGroup(
                    name="Hardware Notices",
                    weight=100,
                    items=(
                        NavMenuItem(
                            link="plugins:nautobot_device_lifecycle_mgmt:hardwarelcm_list",
                            name="Hardware Notices",
                            buttons=(
                                NavMenuButton(
                                    link="plugins:nautobot_device_lifecycle_mgmt:hardwarelcm_add",
                                    title="Add",
                                    icon_class="mdi mdi-plus-thick",
                                    button_class=ButtonColorChoices.GREEN,
                                    permissions=[
                                        "nautobot_device_lifecycle_mgmt.add_hardwarelcm",
                                    ],
                                ),
                                NavMenuButton(
                                    link="plugins:nautobot_device_lifecycle_mgmt:hardwarelcm_import",
                                    title="Import",
                                    icon_class="mdi mdi-database-import-outline",
                                    button_class=ButtonColorChoices.BLUE,
                                    permissions=[
                                        "nautobot_device_lifecycle_mgmt.add_hardwarelcm",
                                    ],
                                ),
                            ),
                            permissions=[
                                "nautobot_device_lifecycle_mgmt.view_hardwarelcm",
                            ],
                        ),
                    ),
                ),
                NavMenuGroup(
                    name="Software Lifecycle",
                    weight=100,
                    items=(
                        NavMenuItem(
                            link="plugins:nautobot_device_lifecycle_mgmt:softwarelcm_list",
                            name="Software",
                            buttons=(
                                NavMenuButton(
                                    link="plugins:nautobot_device_lifecycle_mgmt:softwarelcm_add",
                                    title="Add",
                                    icon_class="mdi mdi-plus-thick",
                                    button_class=ButtonColorChoices.GREEN,
                                    permissions=[
                                        "nautobot_device_lifecycle_mgmt.add_softwarelcm",
                                    ],
                                ),
                                NavMenuButton(
                                    link="plugins:nautobot_device_lifecycle_mgmt:softwarelcm_import",
                                    title="Import",
                                    icon_class="mdi mdi-database-import-outline",
                                    button_class=ButtonColorChoices.BLUE,
                                    permissions=["nautobot_device_lifecycle_mgmt.add_softwarelcm"],
                                ),
                            ),
                            permissions=[
                                "nautobot_device_lifecycle_mgmt.view_softwarelcm",
                            ],
                        ),
                        NavMenuItem(
                            link="plugins:nautobot_device_lifecycle_mgmt:validatedsoftwarelcm_list",
                            name="Validated Software",
                            buttons=(
                                NavMenuButton(
                                    link="plugins:nautobot_device_lifecycle_mgmt:validatedsoftwarelcm_add",
                                    title="Add",
                                    icon_class="mdi mdi-plus-thick",
                                    button_class=ButtonColorChoices.GREEN,
                                    permissions=[
                                        "nautobot_device_lifecycle_mgmt.add_validatedsoftwarelcm",
                                    ],
                                ),
                                NavMenuButton(
                                    link="plugins:nautobot_device_lifecycle_mgmt:validatedsoftwarelcm_import",
                                    title="Import",
                                    icon_class="mdi mdi-database-import-outline",
                                    button_class=ButtonColorChoices.BLUE,
                                    permissions=["nautobot_device_lifecycle_mgmt.add_validatedsoftwarelcm"],
                                ),
                            ),
                            permissions=[
                                "nautobot_device_lifecycle_mgmt.view_validatedsoftwarelcm",
                            ],
                        ),
                    ),
                ),
                NavMenuGroup(
                    name="Contracts",
                    weight=100,
                    items=(
                        NavMenuItem(
                            link="plugins:nautobot_device_lifecycle_mgmt:contractlcm_list",
                            name="Contracts",
                            buttons=(
                                NavMenuButton(
                                    link="plugins:nautobot_device_lifecycle_mgmt:contractlcm_add",
                                    title="Add",
                                    icon_class="mdi mdi-plus-thick",
                                    button_class=ButtonColorChoices.GREEN,
                                    permissions=[
                                        "nautobot_device_lifecycle_mgmt.add_contractlcm",
                                    ],
                                ),
                                NavMenuButton(
                                    link="plugins:nautobot_device_lifecycle_mgmt:contractlcm_import",
                                    title="Import",
                                    icon_class="mdi mdi-database-import-outline",
                                    button_class=ButtonColorChoices.BLUE,
                                    permissions=[
                                        "nautobot_device_lifecycle_mgmt.add_contractlcm",
                                    ],
                                ),
                            ),
                            permissions=[
                                "nautobot_device_lifecycle_mgmt.view_contractlcm",
                            ],
                        ),
                        NavMenuItem(
                            link="plugins:nautobot_device_lifecycle_mgmt:providerlcm_list",
                            name="Contract Providers",
                            buttons=(
                                NavMenuButton(
                                    link="plugins:nautobot_device_lifecycle_mgmt:providerlcm_add",
                                    title="Add",
                                    icon_class="mdi mdi-plus-thick",
                                    button_class=ButtonColorChoices.GREEN,
                                    permissions=[
                                        "nautobot_device_lifecycle_mgmt.add_providerlcm",
                                    ],
                                ),
                                NavMenuButton(
                                    link="plugins:nautobot_device_lifecycle_mgmt:providerlcm_import",
                                    title="Import",
                                    icon_class="mdi mdi-database-import-outline",
                                    button_class=ButtonColorChoices.BLUE,
                                    permissions=[
                                        "nautobot_device_lifecycle_mgmt.add_providerlcm",
                                    ],
                                ),
                            ),
                            permissions=[
                                "nautobot_device_lifecycle_mgmt.view_providerlcm",
                            ],
                        ),
                        NavMenuItem(
                            link="plugins:nautobot_device_lifecycle_mgmt:contactlcm_list",
                            name="Contract POC",
                            buttons=(
                                NavMenuButton(
                                    link="plugins:nautobot_device_lifecycle_mgmt:contactlcm_add",
                                    title="Add",
                                    icon_class="mdi mdi-plus-thick",
                                    button_class=ButtonColorChoices.GREEN,
                                    permissions=[
                                        "nautobot_device_lifecycle_mgmt.add_contactlcm",
                                    ],
                                ),
                                NavMenuButton(
                                    link="plugins:nautobot_device_lifecycle_mgmt:contactlcm_import",
                                    title="Import",
                                    icon_class="mdi mdi-database-import-outline",
                                    button_class=ButtonColorChoices.BLUE,
                                    permissions=[
                                        "nautobot_device_lifecycle_mgmt.add_contactlcm",
                                    ],
                                ),
                            ),
                            permissions=[
                                "nautobot_device_lifecycle_mgmt.view_contactlcm",
                            ],
                        ),
                    ),
                ),
            ),
        ),
    )
except ModuleNotFoundError:
    from nautobot.extras.plugins import PluginMenuItem, PluginMenuButton

    menu_items = (
        PluginMenuItem(
            link="plugins:nautobot_device_lifecycle_mgmt:hardwarelcm_list",
            link_text="Hardware Notices",
            buttons=(
                PluginMenuButton(
                    link="plugins:nautobot_device_lifecycle_mgmt:hardwarelcm_add",
                    title="Add",
                    icon_class="mdi mdi-plus-thick",
                    color=ButtonColorChoices.GREEN,
                    permissions=["nautobot_device_lifecycle_mgmt.add_hardwarelcm"],
                ),
                PluginMenuButton(
                    link="plugins:nautobot_device_lifecycle_mgmt:hardwarelcm_import",
                    title="Import",
                    icon_class="mdi mdi-database-import-outline",
                    color=ButtonColorChoices.BLUE,
                    permissions=["nautobot_device_lifecycle_mgmt.add_hardwarelcm"],
                ),
            ),
        ),
        PluginMenuItem(
            link="plugins:nautobot_device_lifecycle_mgmt:contractlcm_list",
            link_text="Contracts",
            buttons=(
                PluginMenuButton(
                    link="plugins:nautobot_device_lifecycle_mgmt:contractlcm_add",
                    title="Add",
                    icon_class="mdi mdi-plus-thick",
                    color=ButtonColorChoices.GREEN,
                    permissions=["nautobot_device_lifecycle_mgmt.add_contractlcm"],
                ),
                PluginMenuButton(
                    link="plugins:nautobot_device_lifecycle_mgmt:contractlcm_import",
                    title="Import",
                    icon_class="mdi mdi-database-import-outline",
                    color=ButtonColorChoices.BLUE,
                    permissions=["nautobot_device_lifecycle_mgmt.add_contractlcm"],
                ),
            ),
        ),
        PluginMenuItem(
            link="plugins:nautobot_device_lifecycle_mgmt:providerlcm_list",
            link_text="Contract Providers",
            buttons=(
                PluginMenuButton(
                    link="plugins:nautobot_device_lifecycle_mgmt:providerlcm_add",
                    title="Add",
                    icon_class="mdi mdi-plus-thick",
                    color=ButtonColorChoices.GREEN,
                    permissions=["nautobot_device_lifecycle_mgmt.add_providerlcm"],
                ),
                PluginMenuButton(
                    link="plugins:nautobot_device_lifecycle_mgmt:providerlcm_import",
                    title="Import",
                    icon_class="mdi mdi-database-import-outline",
                    color=ButtonColorChoices.BLUE,
                    permissions=["nautobot_device_lifecycle_mgmt.add_providerlcm"],
                ),
            ),
        ),
        PluginMenuItem(
            link="plugins:nautobot_device_lifecycle_mgmt:contactlcm_list",
            link_text="Contract POC",
            buttons=(
                PluginMenuButton(
                    link="plugins:nautobot_device_lifecycle_mgmt:contactlcm_add",
                    title="Add",
                    icon_class="mdi mdi-plus-thick",
                    color=ButtonColorChoices.GREEN,
                    permissions=["nautobot_device_lifecycle_mgmt.add_contactlcm"],
                ),
                PluginMenuButton(
                    link="plugins:nautobot_device_lifecycle_mgmt:contactlcm_import",
                    title="Import",
                    icon_class="mdi mdi-database-import-outline",
                    color=ButtonColorChoices.BLUE,
                    permissions=["nautobot_device_lifecycle_mgmt.add_contactlcm"],
                ),
            ),
        ),
        PluginMenuItem(
            link="plugins:nautobot_device_lifecycle_mgmt:softwarelcm_list",
            link_text="Software",
            buttons=(
                PluginMenuButton(
                    link="plugins:nautobot_device_lifecycle_mgmt:softwarelcm_add",
                    title="Add",
                    icon_class="mdi mdi-plus-thick",
                    color=ButtonColorChoices.GREEN,
                    permissions=["nautobot_device_lifecycle_mgmt.add_softwarelcm"],
                ),
                PluginMenuButton(
                    link="plugins:nautobot_device_lifecycle_mgmt:softwarelcm_import",
                    title="Import",
                    icon_class="mdi mdi-database-import-outline",
                    color=ButtonColorChoices.BLUE,
                    permissions=["nautobot_device_lifecycle_mgmt.add_softwarelcm"],
                ),
            ),
        ),
        PluginMenuItem(
            link="plugins:nautobot_device_lifecycle_mgmt:validatedsoftwarelcm_list",
            link_text="Validated Software",
            buttons=(
                PluginMenuButton(
                    link="plugins:nautobot_device_lifecycle_mgmt:validatedsoftwarelcm_add",
                    title="Add",
                    icon_class="mdi mdi-plus-thick",
                    color=ButtonColorChoices.GREEN,
                    permissions=["nautobot_device_lifecycle_mgmt.add_validatedsoftwarelcm"],
                ),
                PluginMenuButton(
                    link="plugins:nautobot_device_lifecycle_mgmt:validatedsoftwarelcm_import",
                    title="Import",
                    icon_class="mdi mdi-database-import-outline",
                    color=ButtonColorChoices.BLUE,
                    permissions=["nautobot_device_lifecycle_mgmt.add_validatedsoftwarelcm"],
                ),
            ),
        ),
    )

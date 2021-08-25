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
                            permissions=["view"],
                            buttons=(
                                NavMenuButton(
                                    link="plugins:nautobot_device_lifecycle_mgmt:hardwarelcm_add",
                                    title="Add",
                                    icon_class="mdi mdi-plus-thick",
                                    button_class=ButtonColorChoices.GREEN,
                                    permissions=["add"],
                                ),
                                NavMenuButton(
                                    link="plugins:nautobot_device_lifecycle_mgmt:hardwarelcm_import",
                                    title="Import",
                                    icon_class="mdi mdi-database-import-outline",
                                    button_class=ButtonColorChoices.BLUE,
                                    permissions=["add"],
                                ),
                            ),
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
                            link="plugins:nautobot_plugin_device_lifecycle_mgmt:contractlcm_list",
                            name="Contracts",
                            permissions=["view"],
                            buttons=(
                                NavMenuButton(
                                    link="plugins:nautobot_plugin_device_lifecycle_mgmt:contractlcm_add",
                                    title="Add",
                                    icon_class="mdi mdi-plus-thick",
                                    button_class=ButtonColorChoices.GREEN,
                                    permissions=["add"],
                                ),
                                NavMenuButton(
                                    link="plugins:nautobot_plugin_device_lifecycle_mgmt:contractlcm_import",
                                    title="Import",
                                    icon_class="mdi mdi-database-import-outline",
                                    button_class=ButtonColorChoices.BLUE,
                                    permissions=["add"],
                                ),
                            ),
                        ),
                        NavMenuItem(
                            link="plugins:nautobot_plugin_device_lifecycle_mgmt:providerlcm_list",
                            name="Contract Providers",
                            permissions=["view"],
                            buttons=(
                                NavMenuButton(
                                    link="plugins:nautobot_plugin_device_lifecycle_mgmt:providerlcm_add",
                                    title="Add",
                                    icon_class="mdi mdi-plus-thick",
                                    button_class=ButtonColorChoices.GREEN,
                                    permissions=["add"],
                                ),
                                NavMenuButton(
                                    link="plugins:nautobot_plugin_device_lifecycle_mgmt:providerlcm_import",
                                    title="Import",
                                    icon_class="mdi mdi-database-import-outline",
                                    button_class=ButtonColorChoices.BLUE,
                                    permissions=["add"],
                                ),
                            ),
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
                    permissions=["add"],
                ),
                PluginMenuButton(
                    link="plugins:nautobot_device_lifecycle_mgmt:hardwarelcm_import",
                    title="Import",
                    icon_class="mdi mdi-database-import-outline",
                    color=ButtonColorChoices.BLUE,
                    permissions=["add"],
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
            ),
        ),
    )

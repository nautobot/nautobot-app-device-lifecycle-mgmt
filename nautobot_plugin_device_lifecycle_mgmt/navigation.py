"""Menu items."""
from packaging.version import Version
from nautobot import __version__
from nautobot.utilities.choices import ButtonColorChoices

if Version(__version__) >= Version("1.1.0a"):
    from nautobot.core.apps import NavMenuTab, NavMenuGroup, NavMenuItem, NavMenuButton

    menu_items = (
        NavMenuTab(
            name="Device LifeCycle",
            weight=600,
            groups=(
                NavMenuGroup(
                    name="EoX Notices",
                    weight=100,
                    items=(
                        NavMenuItem(
                            link="plugins:nautobot_plugin_device_lifecycle_mgmt:eoxnotice_list",
                            name="EoX Notices",
                            permissions=[
                                "nautobot_plugin_chatops_nso.command_filter",
                            ],
                            buttons=(
                                NavMenuButton(
                                    link="plugins:nautobot_plugin_device_lifecycle_mgmt:eoxnotice_add",
                                    title="Add",
                                    icon_class="mdi mdi-plus-thick",
                                    button_class=ButtonColorChoices.GREEN,
                                    permissions=[
                                        "nautobot_plugin_chatops_nso.command_filter_create",
                                    ],
                                ),
                                NavMenuButton(
                                    link="plugins:nautobot_plugin_device_lifecycle_mgmt:eoxnotice_import",
                                    title="Import",
                                    icon_class="mdi mdi-database-import-outline",
                                    button_class=ButtonColorChoices.BLUE,
                                    permissions=[
                                        "nautobot_plugin_chatops_nso.command_filter_create",
                                    ],
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )
else:
    from nautobot.extras.plugins import PluginMenuItem, PluginMenuButton

    menu_items = (
        PluginMenuItem(
            link="plugins:nautobot_plugin_device_lifecycle_mgmt:eoxnotice_list",
            link_text="EoX Notices",
            buttons=(
                PluginMenuButton(
                    link="plugins:nautobot_plugin_device_lifecycle_mgmt:eoxnotice_add",
                    title="Add",
                    icon_class="mdi mdi-plus-thick",
                    color=ButtonColorChoices.GREEN,
                    permissions=["nautobot_plugin_device_lifecycle_mgmt.add_notice"],
                ),
                PluginMenuButton(
                    link="plugins:nautobot_plugin_device_lifecycle_mgmt:eoxnotice_import",
                    title="Import",
                    icon_class="mdi mdi-database-import-outline",
                    color=ButtonColorChoices.BLUE,
                    permissions=["nautobot_plugin_device_lifecycle_mgmt.add_notice"],
                ),
            ),
        ),
    )

"""Menu items."""

from nautobot.extras.plugins import PluginMenuItem, PluginMenuButton
from nautobot.utilities.choices import ButtonColorChoices

menu_items = (
    PluginMenuItem(
        link="plugins:nautobot_plugin_device_lifecycle_mgmt:devicelifecycle_list",
        link_text="EoX Notices",
        buttons=(
            PluginMenuButton(
                link="plugins:nautobot_plugin_device_lifecycle_mgmt:devicelifecycle_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
                permissions=["nautobot_plugin_device_lifecycle_mgmt.add_notice"],
            ),
            PluginMenuButton(
                link="plugins:nautobot_plugin_device_lifecycle_mgmt:devicelifecycle_import",
                title="Import",
                icon_class="mdi mdi-database-import-outline",
                color=ButtonColorChoices.BLUE,
                permissions=["nautobot_plugin_device_lifecycle_mgmt.add_notice"],
            ),
        ),
    ),
)

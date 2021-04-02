"""Menu items."""

from nautobot.extras.plugins import PluginMenuItem, PluginMenuButton
from nautobot.utilities.choices import ButtonColorChoices

menu_items = (
    PluginMenuItem(
        link="plugins:eox_notices:eoxnotice_list",
        link_text="EoX Notices",
        buttons=(
            PluginMenuButton(
                link="plugins:eox_notices:eoxnotice_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
                permissions=["eox_notices.add_notice"],
            ),
        ),
    ),
)

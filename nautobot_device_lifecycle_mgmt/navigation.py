"""Menu items."""

from nautobot.apps.ui import NavMenuAddButton, NavMenuGroup, NavMenuItem, NavMenuTab

items = (
    NavMenuItem(
        link="plugins:nautobot_device_lifecycle_mgmt:hardwarelcm_list",
        name="Device Lifecycle Management",
        permissions=["nautobot_device_lifecycle_mgmt.view_hardwarelcm"],
        buttons=(
            NavMenuAddButton(
                link="plugins:nautobot_device_lifecycle_mgmt:hardwarelcm_add",
                permissions=["nautobot_device_lifecycle_mgmt.add_hardwarelcm"],
            ),
        ),
    ),
)

menu_items = (
    NavMenuTab(
        name="Apps",
        groups=(NavMenuGroup(name="Device Lifecycle Management", items=tuple(items)),),
    ),
)

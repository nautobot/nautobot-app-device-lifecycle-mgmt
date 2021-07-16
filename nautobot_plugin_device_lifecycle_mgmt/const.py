"""Device Lifecycle Objects."""


class Permissions:
    """Constant permissions tied to functions throughout the device lifecycle."""

    class EoX:
        """Permissions associated with the EoX portion of device lifecycle."""

        Create = "nautobot_plugin_device_lifecycle_mgmt.add_eoxnotice"
        Read = "nautobot_plugin_device_lifecycle_mgmt.view_eoxnotice"
        Update = "nautobot_plugin_device_lifecycle_mgmt.change_eoxnotice"
        Delete = "nautobot_plugin_device_lifecycle_mgmt.delete_eoxnotice"


class URL:
    """Constant URLs tied to functions throughout the device lifecycle."""

    class EoX:
        """URLs associated with the EoX portion of device lifecycle."""

        List = "plugins:nautobot_plugin_device_lifecycle_mgmt:eoxnotice_list"
        View = "plugins:nautobot_plugin_device_lifecycle_mgmt:eoxnotice"
        BulkDelete = "plugins:nautobot_plugin_device_lifecycle_mgmt.eoxnotice_bulk_delete"
        BulkEdit = "plugins:nautobot_plugin_device_lifecycle_mgmt.eoxnotice_bulk_edit"

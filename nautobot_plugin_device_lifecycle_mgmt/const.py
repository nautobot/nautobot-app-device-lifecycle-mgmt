"""Device Lifecycle Objects."""


class Permissions:  # pylint: disable=too-few-public-methods
    """Constant permissions tied to functions throughout the device lifecycle."""

    class HardwareLCM:  # pylint: disable=too-few-public-methods
        """Permissions associated with the HardwareLCM portion of device lifecycle."""

        Create = "nautobot_plugin_device_lifecycle_mgmt.hardwarelcm_add"
        Read = "nautobot_plugin_device_lifecycle_mgmt.hardwarelcm_view"
        Update = "nautobot_plugin_device_lifecycle_mgmt.hardwarelcm_edit"
        Delete = "nautobot_plugin_device_lifecycle_mgmt.hardwarelcm_delete"


class URL:  # pylint: disable=too-few-public-methods
    """Constant URLs tied to functions throughout the device lifecycle."""

    class HardwareLCM:  # pylint: disable=too-few-public-methods
        """URLs associated with the HardwareLCM portion of device lifecycle."""

        List = "plugins:nautobot_plugin_device_lifecycle_mgmt:hardwarelcm_list"
        View = "plugins:nautobot_plugin_device_lifecycle_mgmt:hardwarelcm"
        BulkDelete = "plugins:nautobot_plugin_device_lifecycle_mgmt.hardwarelcm_bulk_delete"
        BulkEdit = "plugins:nautobot_plugin_device_lifecycle_mgmt.hardwarelcm_bulk_edit"

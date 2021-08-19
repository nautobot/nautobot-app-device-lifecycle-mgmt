"""Device Lifecycle Objects."""


class Permissions:  # pylint: disable=too-few-public-methods
    """Constant permissions tied to functions throughout the device lifecycle."""

    class EoX:  # pylint: disable=too-few-public-methods
        """Permissions associated with the EoX portion of device lifecycle."""

        Create = "nautobot_plugin_device_lifecycle_mgmt.add_eoxnotice"
        Read = "nautobot_plugin_device_lifecycle_mgmt.view_eoxnotice"
        Update = "nautobot_plugin_device_lifecycle_mgmt.change_eoxnotice"
        Delete = "nautobot_plugin_device_lifecycle_mgmt.delete_eoxnotice"


class URL:  # pylint: disable=too-few-public-methods
    """Constant URLs tied to functions throughout the device lifecycle."""

    class EoX:  # pylint: disable=too-few-public-methods
        """URLs associated with the EoX portion of device lifecycle."""

        List = "plugins:nautobot_plugin_device_lifecycle_mgmt:eoxnotice_list"
        View = "plugins:nautobot_plugin_device_lifecycle_mgmt:eoxnotice"
        BulkDelete = "plugins:nautobot_plugin_device_lifecycle_mgmt.eoxnotice_bulk_delete"
        BulkEdit = "plugins:nautobot_plugin_device_lifecycle_mgmt.eoxnotice_bulk_edit"

    class SoftwareLCM:  # pylint: disable=too-few-public-methods
        """URLs associated with the SoftwareLCM portion of device lifecycle."""

        List = "plugins:nautobot_plugin_device_lifecycle_mgmt:softwarelcm_list"
        View = "plugins:nautobot_plugin_device_lifecycle_mgmt:softwarelcm"

    class ValidatedSoftwareLCM:  # pylint: disable=too-few-public-methods
        """URLs associated with the ValidatedSoftwareLCM portion of device lifecycle."""

        List = "plugins:nautobot_plugin_device_lifecycle_mgmt:validatedsoftwarelcm_list"
        View = "plugins:nautobot_plugin_device_lifecycle_mgmt:validatedsoftwarelcm"

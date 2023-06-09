"""Device Lifecycle Objects."""
from django.conf import settings


PLUGIN_CFG = settings.PLUGINS_CONFIG["nautobot_device_lifecycle_mgmt"]


class URL:  # pylint: disable=too-few-public-methods
    """Constant URLs tied to functions throughout the device lifecycle."""

    class SoftwareLCM:  # pylint: disable=too-few-public-methods
        """URLs associated with the SoftwareLCM portion of device lifecycle."""

        List = "plugins:nautobot_device_lifecycle_mgmt:softwarelcm_list"
        View = "plugins:nautobot_device_lifecycle_mgmt:softwarelcm"

    class SoftwareImageLCM:  # pylint: disable=too-few-public-methods
        """URLs associated with the SoftwareImageLCM portion of device lifecycle."""

        List = "plugins:nautobot_device_lifecycle_mgmt:softwareimagelcm_list"
        View = "plugins:nautobot_device_lifecycle_mgmt:softwareimagelcm"

    class ValidatedSoftwareLCM:  # pylint: disable=too-few-public-methods
        """URLs associated with the ValidatedSoftwareLCM portion of device lifecycle."""

        List = "plugins:nautobot_device_lifecycle_mgmt:validatedsoftwarelcm_list"
        View = "plugins:nautobot_device_lifecycle_mgmt:validatedsoftwarelcm"

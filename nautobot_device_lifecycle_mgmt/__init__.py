"""App declaration for nautobot_device_lifecycle_mgmt."""

# Metadata is inherited from Nautobot. If not including Nautobot in the environment, this should be added
from importlib import metadata

from nautobot.apps import NautobotAppConfig

__version__ = metadata.version(__name__)


class NautobotDeviceLifecycleManagementConfig(NautobotAppConfig):
    """App configuration for the nautobot_device_lifecycle_mgmt app."""

    name = "nautobot_device_lifecycle_mgmt"
    verbose_name = "Device Lifecycle Management"
    version = __version__
    author = "Network to Code, LLC"
    description = "Device Lifecycle Management."
    base_url = "nautobot-device-lifecycle-mgmt"
    required_settings = []
    min_version = "2.0.0"
    max_version = "2.9999"
    default_settings = {}
    caching_config = {}


config = NautobotDeviceLifecycleManagementConfig  # pylint:disable=invalid-name

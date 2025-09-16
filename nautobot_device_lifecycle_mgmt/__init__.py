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
    default_settings = {}
    caching_config = {}
    docs_view_name = "plugins:nautobot_device_lifecycle_mgmt:docs"
    searchable_models = ["hardwarelcm"]


config = NautobotDeviceLifecycleManagementConfig  # pylint:disable=invalid-name

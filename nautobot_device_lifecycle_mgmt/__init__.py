"""App declaration for nautobot_device_lifecycle_mgmt."""
# Metadata is inherited from Nautobot. If not including Nautobot in the environment, this should be added
from importlib import metadata

__version__ = metadata.version(__name__)

from nautobot.core.signals import nautobot_database_ready
from nautobot.extras.plugins import NautobotAppConfig


class NautobotDeviceLifecycleManagementConfig(NautobotAppConfig):
    """App configuration for the Device Lifecycle Management app."""

    name = "nautobot_device_lifecycle_mgmt"
    verbose_name = "Nautobot Device Lifecycle Management"
    version = __version__
    author = "Network to Code, LLC"
    description = "Manages device lifecycle of Nautobot Devices and Components."
    base_url = "nautobot-device-lifecycle-mgmt"
    required_settings = []
    min_version = "2.0.0"
    max_version = "2.9999"
    default_settings = {
        "expired_field": "end_of_support",
        "barchart_bar_width": 0.1,
        "barchart_width": 12,
        "barchart_height": 5,
    }
    caching_config = {}

    def ready(self):
        """Register custom signals."""
        from .signals import post_migrate_create_relationships  # pylint: disable=import-outside-toplevel

        nautobot_database_ready.connect(post_migrate_create_relationships, sender=self)

        super().ready()


config = NautobotDeviceLifecycleManagementConfig  # pylint:disable=invalid-name

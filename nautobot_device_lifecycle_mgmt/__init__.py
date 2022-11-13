"""Plugin declaration for the Device LifeCycle Management."""
try:
    from importlib import metadata
except ImportError:
    # Python version < 3.8
    import importlib_metadata as metadata

__version__ = metadata.version(__name__)

from nautobot.core.signals import nautobot_database_ready
from nautobot.extras.plugins import PluginConfig


class DeviceLifeCycleConfig(PluginConfig):
    """Plugin configuration for the Device Lifecycle Management plugin."""

    name = "nautobot_device_lifecycle_mgmt"
    verbose_name = "Nautobot Device Lifecycle Management"
    version = __version__
    author = "Network to Code"
    author_email = "opensource@networktocode.com"
    description = "Manages device lifecycle of Nautobot Devices and Components."
    base_url = "nautobot-device-lifecycle-mgmt"
    required_settings = []
    min_version = "1.2.0"
    max_version = "1.9999"
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


config = DeviceLifeCycleConfig  # pylint:disable=invalid-name

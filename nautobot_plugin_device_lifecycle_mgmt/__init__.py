"""Plugin declaration for nautobot_plugin_device_lifecycle_mgmt."""

__version__ = "0.2.0"

from nautobot.extras.plugins import PluginConfig


class DeviceLifeCycleConfig(PluginConfig):
    """Plugin configuration for the nautobot_plugin_device_lifecycle_mgmt plugin."""

    name = "nautobot_plugin_device_lifecycle_mgmt"
    verbose_name = "Nautobot Device Lifecycle"
    version = __version__
    author = "Mikhail Yohman"
    description = "Manages device lifecycle of Nautobot Devices and Components."
    base_url = "device-lifecycle"
    required_settings = []
    min_version = "1.0.0"
    max_version = "1.9999"
    default_settings = {"expired_field": "end_of_support"}
    caching_config = {}

    def ready(self):
        """Register custom signals."""
        super().ready()
        import nautobot_plugin_device_lifecycle_mgmt.signals  # pylint: disable=C0415,W0611 # noqa: F401


config = DeviceLifeCycleConfig  # pylint:disable=invalid-name

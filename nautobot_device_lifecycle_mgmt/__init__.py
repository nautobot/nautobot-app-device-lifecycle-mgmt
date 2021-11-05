"""Plugin declaration for the Device Lifecycle Management."""

__version__ = "0.1.0-beta.0"

from django.db.models.signals import post_migrate

from nautobot.extras.plugins import PluginConfig


class DeviceLifeCycleConfig(PluginConfig):
    """Plugin configuration for the Device Lifecycle Management plugin."""

    name = "nautobot_device_lifecycle_mgmt"
    verbose_name = "Nautobot Device Lifecycle Management"
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
        import nautobot_device_lifecycle_mgmt.signals  # pylint: disable=C0415,W0611 # noqa: F401

        from .signals import (  # pylint: disable=import-outside-toplevel
            post_migrate_create_relationships,
        )

        post_migrate.connect(post_migrate_create_relationships, sender=self)


config = DeviceLifeCycleConfig  # pylint:disable=invalid-name

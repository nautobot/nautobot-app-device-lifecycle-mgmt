"""App declaration for nautobot_device_lifecycle_mgmt."""

# Metadata is inherited from Nautobot. If not including Nautobot in the environment, this should be added
from importlib import metadata

from nautobot.apps import NautobotAppConfig, nautobot_database_ready

__version__ = metadata.version(__name__)


class NautobotDeviceLifecycleManagementConfig(NautobotAppConfig):
    """App configuration for the Device Lifecycle Management app."""

    name = "nautobot_device_lifecycle_mgmt"
    verbose_name = "Nautobot Device Lifecycle Management"
    version = __version__
    author = "Network to Code, LLC"
    description = "Manages device lifecycle of Nautobot Devices and Components."
    base_url = "nautobot-device-lifecycle-mgmt"
    required_settings = []
    default_settings = {
        "barchart_bar_width": 0.1,
        "barchart_width": 12,
        "barchart_height": 5,
        "enabled_metrics": [],
    }
    docs_view_name = "plugins:nautobot_device_lifecycle_mgmt:docs"
    banner_function = "banner.models_migrated_to_core_banner"
    searchable_models = ["hardwarelcm", "providerlcm"]

    def ready(self):
        """Register custom signals."""
        from .signals import (  # pylint: disable=import-outside-toplevel
            post_migrate_create_relationships,
        )

        nautobot_database_ready.connect(post_migrate_create_relationships, sender=self)

        super().ready()


config = NautobotDeviceLifecycleManagementConfig  # pylint:disable=invalid-name

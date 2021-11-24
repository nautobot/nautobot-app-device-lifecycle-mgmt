"""Plugin declaration for the Device LifeCycle Management."""
try:
    from importlib import metadata
except ImportError:
    # Python version < 3.8
    import importlib_metadata as metadata

__version__ = metadata.version(__name__)

from django.db.models.signals import post_migrate

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
    min_version = "1.0.0"
    max_version = "1.9999"
    default_settings = {"expired_field": "end_of_support"}
    caching_config = {}

    def ready(self):
        """Register custom signals."""
        import graphene  # pylint: disable=import-outside-toplevel
        from graphene_django.converter import convert_django_field  # pylint: disable=import-outside-toplevel
        from taggit.managers import TaggableManager  # pylint: disable=import-outside-toplevel
        from nautobot.extras.graphql.types import TagType  # pylint: disable=import-outside-toplevel

        import nautobot_device_lifecycle_mgmt.signals  # pylint: disable=C0415,W0611 # noqa: F401

        @convert_django_field.register(TaggableManager)
        def convert_field_to_list_tags(field, registry=None):
            """Convert TaggableManager to List of Tags."""
            return graphene.List(TagType)

        from .signals import (  # pylint: disable=import-outside-toplevel
            post_migrate_create_relationships,
        )

        post_migrate.connect(post_migrate_create_relationships, sender=self)

        super().ready()


config = DeviceLifeCycleConfig  # pylint:disable=invalid-name

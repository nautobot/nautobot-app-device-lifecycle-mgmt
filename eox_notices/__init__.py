"""Plugin declaration for eox_notices."""

__version__ = "0.1.0"

from nautobot.extras.plugins import PluginConfig


class EoxNoticesConfig(PluginConfig):
    """Plugin configuration for the eox_notices plugin."""

    name = "eox_notices"
    verbose_name = "Nautobot EoX Tracker"
    version = __version__
    author = "Network to Code, LLC"
    description = "Tracks EoX Notices for Nautobot objects.."
    base_url = "eox-notices"
    required_settings = []
    min_version = "1.0.0b1"
    max_version = "1.0.0b3"
    default_settings = {}
    caching_config = {}

    def ready(self):
        """Register custom signals."""
        super().ready()
        import eox_notices.signals  # noqa: F401


config = EoxNoticesConfig  # pylint:disable=invalid-name

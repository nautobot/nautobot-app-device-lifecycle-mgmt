"""Utility functions and classes used by the plugin."""
from django.conf import settings
from django.db.models import Count, Subquery, OuterRef
from django.db.models.functions import Coalesce

PLUGIN_SETTINGS = settings.PLUGINS_CONFIG["nautobot_device_lifecycle_mgmt"]


def count_related_m2m(model, field):
    """Return a Subquery suitable for annotating a m2m field count."""
    subquery = Subquery(model.objects.filter(**{"pk": OuterRef("pk")}).order_by().annotate(c=Count(field)).values("c"))

    return Coalesce(subquery, 0)


def add_custom_contract_types(choices):
    """Add custom defined choices to existing Contract Type choices.

    Args:
        choices (tuple): Existing Device Lifecycle Contract Type tuple.
    """
    defined_additional_contract_types = PLUGIN_SETTINGS.get("additional_contract_types", [])
    return tuple((contract_type, contract_type) for contract_type in defined_additional_contract_types) + tuple(choices)

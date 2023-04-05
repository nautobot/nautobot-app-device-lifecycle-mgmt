"""Utility functions and classes used by the plugin."""
from django.db.models import Count, Subquery, OuterRef
from django.db.models.functions import Coalesce


def count_related_m2m(model, field):
    """Return a Subquery suitable for annotating a m2m field count."""
    subquery = Subquery(model.objects.filter(**{"pk": OuterRef("pk")}).order_by().annotate(c=Count(field)).values("c"))

    return Coalesce(subquery, 0)

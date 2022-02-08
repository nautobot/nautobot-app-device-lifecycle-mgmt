"""Utility functions and classes used by the plugin."""


from django.db.models import Count, Subquery, OuterRef
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils.safestring import mark_safe

from nautobot.utilities.tables import LinkedCountColumn


class M2MLinkedCountColumn(LinkedCountColumn):
    """Linked count column supporting many-to-many fields."""

    def render(self, record, value):
        """Render the resulting URL."""
        if value:
            url = reverse(self.viewname, kwargs=self.view_kwargs)
            if self.url_params:
                url += "?"
                for k, v in self.url_params.items():
                    if isinstance(v, tuple):
                        values = getattr(record, v[0]).values(v[1])
                        url += "&".join([f"{k}={val[k]}" for val in values])
                    else:
                        url += f"&{k}={getattr(record, v)}"
            return mark_safe(f'<a href="{url}">{value}</a>')
        return value


def count_related_m2m(model, field):
    """
    Return a Subquery suitable for annotating a m2m field count.
    """
    subquery = Subquery(model.objects.filter(**{"pk": OuterRef("pk")}).order_by().annotate(c=Count(field)).values("c"))

    return Coalesce(subquery, 0)

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
                for key, kval in self.url_params.items():
                    if isinstance(kval, tuple):
                        values = getattr(record, kval[0]).values(kval[1])
                        url += "&".join([f"{key}={val[key]}" for val in values])
                    else:
                        url += f"&{key}={getattr(record, kval)}"
            return mark_safe(f'<a href="{url}">{value}</a>')  # nosec
        return value


def count_related_m2m(model, field):
    """Return a Subquery suitable for annotating a m2m field count."""
    subquery = Subquery(model.objects.filter(**{"pk": OuterRef("pk")}).order_by().annotate(c=Count(field)).values("c"))

    return Coalesce(subquery, 0)

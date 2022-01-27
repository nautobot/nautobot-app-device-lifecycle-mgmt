"""Utility functions and classes used by the plugin."""

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

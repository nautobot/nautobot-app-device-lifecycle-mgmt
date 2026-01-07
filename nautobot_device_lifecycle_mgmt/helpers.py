"""Utility filters and helpers for templates."""

from django import template
from django.utils.html import format_html
from django_jinja import library
from nautobot.core.templatetags.helpers import placeholder

register = template.Library()


@library.filter()
@register.filter()
def hyperlink_url_new_tab(value):
    """Render a plain string URL as a safe hyperlink that opens in a new tab."""
    if not value:
        return placeholder(None)
    return format_html('<a href="{}" target="_blank" rel="noreferrer">{}</a>', value, value)

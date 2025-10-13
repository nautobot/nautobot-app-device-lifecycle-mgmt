"""Utility filters and helpers for templates."""

from urllib.parse import quote_plus

from django import template
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from django_jinja import library

HTML_NONE = mark_safe('<span class="text-muted">&mdash;</span>')  # noqa: S308 - safe static HTML

register = template.Library()


@library.filter()
@register.filter()
def hyperlinked_email(value):
    """Render an email address as a `mailto:` hyperlink."""
    if not value:
        return placeholder(value)
    return format_html('<a href="mailto:{}">{}</a>', value, value)


@library.filter()
@register.filter()
def hyperlinked_phone_number(value):
    """Render a phone number as a `tel:` hyperlink."""
    if not value:
        return placeholder(value)
    return format_html('<a href="tel:{}">{}</a>', value, value)


@library.filter()
@register.filter()
def hyperlink_url_new_tab(value):
    """Render a plain string URL as a safe hyperlink that opens in a new tab."""
    if not value:
        return "—"
    return format_html('<a href="{}" target="_blank" rel="noreferrer">{}</a>', value, value)


@library.filter()
@register.filter()
def placeholder(value):
    """Render a muted placeholder if value is falsey, else render the value.

    Args:
        value (any): Input value, can be any variable.

    Returns:
        (str): Placeholder in HTML, or the string representation of the value.

    Example:
        >>> placeholder("")
        '<span class="text-muted">&mdash;</span>'
        >>> placeholder("hello")
        "hello"
    """
    if value:
        return value
    return HTML_NONE


@library.filter()
@register.filter()
def render_address(address):
    """Render a multiline address with a 'Map it' button linking to Google Maps."""
    if address:
        map_link = format_html(
            '<a href="https://maps.google.com/?q={}" target="_blank" class="btn btn-primary btn-xs">'
            '<i class="mdi mdi-map-marker"></i> Map it</a>',
            quote_plus(address),
        )
        address = format_html_join("", "{}<br>", ((line,) for line in address.split("\n")))
        return format_html('<div class="pull-right noprint">{}</div>{}', map_link, address)
    return HTML_NONE

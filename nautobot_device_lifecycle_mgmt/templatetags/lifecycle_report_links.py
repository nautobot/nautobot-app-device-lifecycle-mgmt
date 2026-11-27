"""Template tags for the links on the report pages."""

from django import template
from django.http import QueryDict
from nautobot.apps.views import ObjectListViewMixin

register = template.Library()


@register.simple_tag(takes_context=True)
def report_link_querystring(context, **link_params):
    """Build the querystring of a link from a report page to a filtered list.

    The link keeps the report filters of the current request, without pagination, sorting or saved view
    parameters. `link_params` replace report filters of the same name.

    Args:
        context (Context): Template context. The report filters are read from its `request`, when present.
        **link_params: Filters set by the link, such as `valid=False`.

    Returns:
        (str): The querystring with a leading `?`, or an empty string when there are no parameters.
    """
    request = context.get("request")
    params = request.GET.copy() if request is not None else QueryDict(mutable=True)
    for param in ObjectListViewMixin.non_filter_params:
        params.pop(param, None)
    for param, value in link_params.items():
        params[param] = value
    querystring = params.urlencode()
    return f"?{querystring}" if querystring else ""

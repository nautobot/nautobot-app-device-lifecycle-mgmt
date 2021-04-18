"""Filtering for eox_notices UI."""

import django_filters
from django.db.models import Q

from nautobot.dcim.models import Device, DeviceType
from .models import EoxNotice


class EoxNoticeFilter(django_filters.FilterSet):
    """Filter for EoxNotice."""

    q = django_filters.CharFilter(method="search", label="Search")

    device_type = django_filters.ModelMultipleChoiceFilter(
        field_name="device_type__slug",
        queryset=DeviceType.objects.all(),
        to_field_name="slug",
        label="Device Type (Slug)",
    )
    device_type_id = django_filters.ModelMultipleChoiceFilter(
        field_name="device_type", queryset=DeviceType.objects.all(), label="Device Type"
    )
    devices = django_filters.ModelMultipleChoiceFilter(
        field_name="devices__name", queryset=Device.objects.all(), to_field_name="name", label="Device",
    )
    device_id = django_filters.ModelMultipleChoiceFilter(
        field_name="devices", queryset=Device.objects.all(), label="Device"
    )

    class Meta:
        """Meta attributes for filter."""

        model = EoxNotice

        fields = ["end_of_sale", "end_of_support", "end_of_sw_releases", "end_of_security_patches", "notice_url"]

    def search(self, queryset, name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = Q(end_of_sale__icontains=value) | Q(end_of_support__icontains=value)
        return queryset.filter(qs_filter)

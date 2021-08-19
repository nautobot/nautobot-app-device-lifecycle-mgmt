<<<<<<< HEAD
"""Filtering implementation for the LifeCycle Management plugin."""
=======
"""Filtering for nautobot_plugin_device_lifecycle_mgmt UI."""
>>>>>>> c9c3a9d (Rename plugin)
import datetime
import django_filters
from django.db.models import Q

<<<<<<< HEAD
from nautobot.dcim.models import DeviceType
from nautobot_device_lifecycle_mgmt.models import HardwareLCM


class HardwareLCMFilterSet(django_filters.FilterSet):
    """Filter for HardwareLCM."""
=======
from nautobot.dcim.models import Device, DeviceType, Platform
from nautobot_plugin_device_lifecycle_mgmt.models import EoxNotice, SoftwareLCM, ValidatedSoftwareLCM


class EoxNoticeFilter(django_filters.FilterSet):
    """Filter for EoxNotice."""
>>>>>>> c9c3a9d (Rename plugin)

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
<<<<<<< HEAD

    inventory_item = django_filters.ModelMultipleChoiceFilter(
        queryset=HardwareLCM.objects.exclude(inventory_item__isnull=True),
        to_field_name="inventory_item",
        field_name="inventory_item",
        label="Inventory Part ID",
    )

    end_of_support = django_filters.DateFilter()
    end_of_support__gte = django_filters.DateFilter(field_name="end_of_support", lookup_expr="gte")
    end_of_support__lte = django_filters.DateFilter(field_name="end_of_support", lookup_expr="lte")

    end_of_sale = django_filters.DateFilter()
    end_of_sale__gte = django_filters.DateFilter(field_name="end_of_sale", lookup_expr="gte")
    end_of_sale__lte = django_filters.DateFilter(field_name="end_of_sale", lookup_expr="lte")

    end_of_security_patches = django_filters.DateFilter()
    end_of_security_patches__gte = django_filters.DateFilter(field_name="end_of_security_patches", lookup_expr="gte")
    end_of_security_patches__lte = django_filters.DateFilter(field_name="end_of_security_patches", lookup_expr="lte")

    end_of_sw_releases = django_filters.DateFilter()
    end_of_sw_releases__gte = django_filters.DateFilter(field_name="end_of_sw_releases", lookup_expr="gte")
    end_of_sw_releases__lte = django_filters.DateFilter(field_name="end_of_sw_releases", lookup_expr="lte")
=======
    devices = django_filters.ModelMultipleChoiceFilter(
        field_name="devices__name",
        queryset=Device.objects.all(),
        to_field_name="name",
        label="Device",
    )
    device_id = django_filters.ModelMultipleChoiceFilter(
        field_name="devices", queryset=Device.objects.all(), label="Device"
    )
>>>>>>> c9c3a9d (Rename plugin)

    expired = django_filters.BooleanFilter(method="expired_search", label="Expired")

    class Meta:
        """Meta attributes for filter."""

<<<<<<< HEAD
        model = HardwareLCM
=======
        model = EoxNotice
>>>>>>> c9c3a9d (Rename plugin)

        fields = [
            "end_of_sale",
            "end_of_support",
            "end_of_sw_releases",
            "end_of_security_patches",
<<<<<<< HEAD
            "inventory_item",
            "documentation_url",
=======
            "notice_url",
>>>>>>> c9c3a9d (Rename plugin)
            "expired",
        ]

    def search(self, queryset, name, value):  # pylint: disable=unused-argument, no-self-use
        """Perform the filtered search."""
        if not value.strip():
            return queryset

        qs_filter = Q(end_of_sale__icontains=value) | Q(end_of_support__icontains=value)
        return queryset.filter(qs_filter)

    def expired_search(self, queryset, name, value):  # pylint: disable=unused-argument, no-self-use
        """Perform the filtered search."""
        today = datetime.datetime.today().date()
        lookup = "gte" if not value else "lt"

        qs_filter = Q(**{f"end_of_sale__{lookup}": today}) | Q(**{f"end_of_support__{lookup}": today})
        return queryset.filter(qs_filter)
<<<<<<< HEAD
=======


class SoftwareLCMFilterSet(django_filters.FilterSet):
    """Filter for SoftwareLCM."""

    q = django_filters.CharFilter(method="search", label="Search")

    device_platform = django_filters.ModelMultipleChoiceFilter(
        field_name="device_platform__slug",
        queryset=Platform.objects.all(),
        to_field_name="slug",
        label="Device Platform (Slug)",
    )

    class Meta:
        """Meta attributes for filter."""

        model = SoftwareLCM

        fields = [
            "version",
            "alias",
            "end_of_support",
            "end_of_security_patches",
            "documentation_url",
            "download_url",
            "image_file_name",
            "image_file_checksum",
            "long_term_support",
            "pre_release",
        ]

    def search(self, queryset, name, value):  # pylint: disable=unused-argument, no-self-use
        """Perform the filtered search."""
        if not value.strip():
            return queryset

        qs_filter = (
            Q(version__icontains=value)
            | Q(alias__icontains=value)
            | Q(end_of_support__icontains=value)
            | Q(end_of_security_patches__icontains=value)
        )
        return queryset.filter(qs_filter)


class ValidatedSoftwareLCMFilterSet(django_filters.FilterSet):
    """Filter for ValidatedSoftwareLCM."""

    q = django_filters.CharFilter(method="search", label="Search")

    software = django_filters.ModelMultipleChoiceFilter(
        queryset=SoftwareLCM.objects.all(),
        label="Software",
    )

    # expired = django_filters.BooleanFilter(method="expired_search", label="Expired")

    class Meta:
        """Meta attributes for filter."""

        model = ValidatedSoftwareLCM

        fields = [
            "software",
            "start",
            "end",
            "preferred",
        ]

    def search(self, queryset, name, value):  # pylint: disable=unused-argument, no-self-use
        """Perform the filtered search."""
        if not value.strip():
            return queryset

        qs_filter = Q(start__icontains=value) | Q(end__icontains=value)
        return queryset.filter(qs_filter)
>>>>>>> c9c3a9d (Rename plugin)

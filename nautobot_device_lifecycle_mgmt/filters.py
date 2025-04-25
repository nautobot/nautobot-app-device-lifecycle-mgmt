"""Filtering implementation for the Lifecycle Management app."""

import datetime

import django_filters
from django.db.models import Q
from nautobot.apps.filters import NautobotFilterSet, SearchFilter, StatusModelFilterSetMixin
from nautobot.dcim.models import Device, DeviceType, InventoryItem, Location, Manufacturer, Platform, SoftwareVersion
from nautobot.extras.filters.mixins import StatusFilter
from nautobot.extras.models import Role, Status, Tag

from nautobot_device_lifecycle_mgmt.choices import CVESeverityChoices
from nautobot_device_lifecycle_mgmt.models import (
    CVELCM,
    ContactLCM,
    ContractLCM,
    DeviceHardwareNoticeResult,
    DeviceSoftwareValidationResult,
    HardwareLCM,
    InventoryItemSoftwareValidationResult,
    ProviderLCM,
    SoftwareImageLCM,
    SoftwareLCM,
    ValidatedSoftwareLCM,
    VulnerabilityLCM,
)


class HardwareLCMFilterSet(NameSearchFilterSet, NautobotFilterSet):  # pylint: disable=too-many-ancestors
    """Filter for HardwareLCM."""

    q = SearchFilter(
        filter_predicates={
            "device_type__model": {
                "lookup_expr": "icontains",
                "preprocessor": str.strip,
            },
            "device_type__part_number": {
                "lookup_expr": "icontains",
                "preprocessor": str.strip,
            },
            "inventory_item": {
                "lookup_expr": "icontains",
                "preprocessor": str.strip,
            },
            "comments": {
                "lookup_expr": "icontains",
                "preprocessor": str.strip,
            },
            "documentation_url": {
                "lookup_expr": "icontains",
                "preprocessor": str.strip,
            },
            "release_date": {
                "lookup_expr": "icontains",
                "preprocessor": str.strip,
            },
            "end_of_sale": {
                "lookup_expr": "icontains",
                "preprocessor": str.strip,
            },
            "end_of_support": {
                "lookup_expr": "icontains",
                "preprocessor": str.strip,
            },
            "end_of_sw_releases": {
                "lookup_expr": "icontains",
                "preprocessor": str.strip,
            },
            "end_of_security_patches": {
                "lookup_expr": "icontains",
                "preprocessor": str.strip,
            },
        }
    )
    device_type_id = django_filters.ModelMultipleChoiceFilter(
        field_name="device_type",
        queryset=DeviceType.objects.all(),
        label="Device Type",
    )
    device_type = django_filters.ModelMultipleChoiceFilter(
        field_name="device_type", queryset=DeviceType.objects.all(), label="Device Type"
    )

    device_type_model = django_filters.ModelMultipleChoiceFilter(
        field_name="device_type__model",
        queryset=DeviceType.objects.all(),
        to_field_name="model",
        label="Device Type (Model)",
    )

    inventory_item = django_filters.ModelMultipleChoiceFilter(
        queryset=HardwareLCM.objects.exclude(inventory_item__isnull=True),
        to_field_name="inventory_item",
        field_name="inventory_item",
        label="Inventory Part ID",
    )

    documentation_url = django_filters.CharFilter(
        lookup_expr="contains",
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

    expired = django_filters.BooleanFilter(method="_expired_search", label="Support Expired")

    class Meta:
        """Meta attributes for filter."""

        model = HardwareLCM

        # add any fields from the model that you would like to filter your searches by using those
        fields = "__all__"

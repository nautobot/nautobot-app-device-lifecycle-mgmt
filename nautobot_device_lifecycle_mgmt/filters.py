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


class HardwareLCMFilterSet(NautobotFilterSet):
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

        fields = "__all__"

    def _expired_search(self, queryset, name, value):  # pylint: disable=unused-argument
        """Perform the filtered search."""
        today = datetime.datetime.today().date()
        # End of support dates less than today are expired.
        # End of support dates greater than or equal to today are not expired.
        # If the end of support date is null, the notice will never be expired.
        qs_filter = None
        if value:
            qs_filter = Q(**{"end_of_support__lt": today})
        if not value:
            qs_filter = Q(**{"end_of_support__gte": today}) | Q(**{"end_of_support__isnull": True})
        return queryset.filter(qs_filter)


class SoftwareLCMFilterSet(NautobotFilterSet):
    """Filter for SoftwareLCM."""

    q = django_filters.CharFilter(method="search", label="Search")

    device_platform = django_filters.ModelMultipleChoiceFilter(
        field_name="device_platform__name",
        queryset=Platform.objects.all(),
        to_field_name="name",
        label="Device Platform (Name)",
    )

    documentation_url = django_filters.CharFilter(
        lookup_expr="contains",
    )
    release_date = django_filters.DateTimeFromToRangeFilter()
    end_of_support = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        """Meta attributes for filter."""

        model = SoftwareLCM

        fields = "__all__"

    def search(self, queryset, name, value):  # pylint: disable=unused-argument
        """Perform the filtered search."""
        if not value.strip():
            return queryset

        qs_filter = (
            Q(version__icontains=value)
            | Q(alias__icontains=value)
            | Q(release_date__icontains=value)
            | Q(end_of_support__icontains=value)
        )
        return queryset.filter(qs_filter)


class SoftwareImageLCMFilterSet(NautobotFilterSet):
    """Filter for SoftwareImageLCM."""

    q = django_filters.CharFilter(method="search", label="Search")

    software = django_filters.ModelMultipleChoiceFilter(
        queryset=SoftwareLCM.objects.all(),
        label="Software",
    )
    software_version = django_filters.ModelMultipleChoiceFilter(
        field_name="software__version",
        queryset=SoftwareLCM.objects.all(),
        to_field_name="version",
        label="Software (version)",
    )
    device_types_id = django_filters.ModelMultipleChoiceFilter(
        field_name="device_types",
        queryset=DeviceType.objects.all(),
        label="Device Types",
    )
    device_types = django_filters.ModelMultipleChoiceFilter(
        field_name="device_types__model",
        queryset=DeviceType.objects.all(),
        to_field_name="model",
        label="Device Types (model)",
    )
    inventory_items_id = django_filters.ModelMultipleChoiceFilter(
        field_name="inventory_items",
        queryset=InventoryItem.objects.all(),
        label="Inventory Items",
    )
    inventory_items = django_filters.ModelMultipleChoiceFilter(
        field_name="inventory_items__id",
        queryset=InventoryItem.objects.all(),
        to_field_name="id",
        label="Inventory Items (name)",
    )
    object_tags_id = django_filters.ModelMultipleChoiceFilter(
        field_name="object_tags",
        queryset=Tag.objects.all(),
        label="Object Tags",
    )
    object_tags = django_filters.ModelMultipleChoiceFilter(
        field_name="object_tags__name",
        queryset=Tag.objects.all(),
        to_field_name="name",
        label="Object Tags (name)",
    )
    device_name = django_filters.CharFilter(method="device", label="Device Name")
    device_id = django_filters.CharFilter(method="device", label="Device ID")
    inventory_item_id = django_filters.CharFilter(method="inventory_item", label="InventoryItem ID")

    class Meta:
        """Meta attributes for filter."""

        model = SoftwareImageLCM

        fields = "__all__"

    def search(self, queryset, name, value):  # pylint: disable=unused-argument
        """Perform the filtered search."""
        if not value.strip():
            return queryset

        qs_filter = Q(image_file_name__icontains=value) | Q(software__version__icontains=value)
        return queryset.filter(qs_filter)

    def device(self, queryset, name, value):
        """Search for software image for a given device."""
        value = value.strip()
        if not value:
            return queryset

        if name == "device_name":
            devices = Device.objects.filter(name=value)
        elif name == "device_id":
            devices = Device.objects.filter(id=value)
        else:
            devices = Device.objects.none()

        if devices.count() != 1:
            return queryset.none()

        device = devices.first()

        return queryset.filter(id__in=SoftwareImageLCM.objects.get_for_object(device).values("id"))

    def inventory_item(self, queryset, name, value):  # pylint: disable=unused-argument
        """Search for software image for a given inventory item."""
        value = value.strip()
        if not value:
            return queryset

        inventory_items = InventoryItem.objects.filter(id=value)

        if inventory_items.count() != 1:
            return queryset.none()

        inventory_item = inventory_items.first()

        return queryset.filter(id__in=SoftwareImageLCM.objects.get_for_object(inventory_item).values("id"))


class ValidatedSoftwareLCMFilterSet(NautobotFilterSet):
    """Filter for ValidatedSoftwareLCM."""

    q = django_filters.CharFilter(method="search", label="Search")

    software = django_filters.ModelMultipleChoiceFilter(
        queryset=SoftwareVersion.objects.all(),
        label="Software",
    )
    devices_id = django_filters.ModelMultipleChoiceFilter(
        field_name="devices",
        queryset=Device.objects.all(),
        label="Devices",
    )
    devices = django_filters.ModelMultipleChoiceFilter(
        field_name="devices__name",
        queryset=Device.objects.all(),
        to_field_name="name",
        label="Devices (name)",
    )
    device_types_id = django_filters.ModelMultipleChoiceFilter(
        field_name="device_types",
        queryset=DeviceType.objects.all(),
        label="Device Types",
    )
    device_types = django_filters.ModelMultipleChoiceFilter(
        field_name="device_types__model",
        queryset=DeviceType.objects.all(),
        to_field_name="model",
        label="Device Types (model)",
    )
    device_roles_id = django_filters.ModelMultipleChoiceFilter(
        field_name="device_roles",
        queryset=Role.objects.all(),
        label="Device Roles",
    )
    device_roles = django_filters.ModelMultipleChoiceFilter(
        field_name="device_roles__name",
        queryset=Role.objects.all(),
        to_field_name="name",
        label="Device Roles (name)",
    )
    inventory_items_id = django_filters.ModelMultipleChoiceFilter(
        field_name="inventory_items",
        queryset=InventoryItem.objects.all(),
        label="Inventory Items",
    )
    inventory_items = django_filters.ModelMultipleChoiceFilter(
        field_name="inventory_items__name",
        queryset=InventoryItem.objects.all(),
        to_field_name="name",
        label="Inventory Items (name)",
    )
    object_tags_id = django_filters.ModelMultipleChoiceFilter(
        field_name="object_tags",
        queryset=Tag.objects.all(),
        label="Object Tags",
    )
    object_tags = django_filters.ModelMultipleChoiceFilter(
        field_name="object_tags__name",
        queryset=Tag.objects.all(),
        to_field_name="name",
        label="Object Tags (name)",
    )
    device_name = django_filters.CharFilter(method="device", label="Device Name")
    device_id = django_filters.CharFilter(method="device", label="Device ID")
    inventory_item_id = django_filters.CharFilter(method="inventory_item", label="InventoryItem ID")
    start = django_filters.DateTimeFromToRangeFilter()
    end = django_filters.DateTimeFromToRangeFilter()
    valid = django_filters.BooleanFilter(method="valid_search", label="Currently valid")

    class Meta:
        """Meta attributes for filter."""

        model = ValidatedSoftwareLCM

        fields = "__all__"

    def search(self, queryset, name, value):  # pylint: disable=unused-argument
        """Perform the filtered search."""
        if not value.strip():
            return queryset

        qs_filter = Q(start__icontains=value) | Q(end__icontains=value)
        return queryset.filter(qs_filter)

    def valid_search(self, queryset, name, value):  # pylint: disable=unused-argument
        """Perform the valid_search search."""
        today = datetime.date.today()
        if value is True:
            qs_filter = Q(start__lte=today, end=None) | Q(start__lte=today, end__gte=today)
        else:
            qs_filter = Q(start__gt=today) | Q(end__lt=today)
        return queryset.filter(qs_filter)

    def device(self, queryset, name, value):
        """Search for validated software for a given device."""
        value = value.strip()
        if not value:
            return queryset

        if name == "device_name":
            devices = Device.objects.filter(name=value)
        elif name == "device_id":
            devices = Device.objects.filter(id=value)
        else:
            devices = Device.objects.none()

        if devices.count() != 1:
            return queryset.none()

        device = devices.first()

        return ValidatedSoftwareLCM.objects.get_for_object(device)

    def inventory_item(self, queryset, name, value):  # pylint: disable=unused-argument
        """Search for validated software for a given inventory item."""
        value = value.strip()
        if not value:
            return queryset

        inventory_items = InventoryItem.objects.filter(id=value)

        if inventory_items.count() != 1:
            return queryset.none()

        inventory_item = inventory_items.first()

        return ValidatedSoftwareLCM.objects.get_for_object(inventory_item)


class DeviceHardwareNoticeResultFilterSet(NautobotFilterSet):
    """Filter for DeviceHardwareNoticeResult."""

    hardware_notice_available = django_filters.BooleanFilter(
        method="_hardware_notice_available_search",
        label="Hardware Notice Available",
    )
    supported = django_filters.BooleanFilter(
        label="Supported",
        field_name="is_supported",
    )
    platform = django_filters.ModelMultipleChoiceFilter(
        field_name="device__platform",
        queryset=Platform.objects.all(),
        label="Platform",
    )
    location_id = django_filters.ModelMultipleChoiceFilter(
        field_name="device__location",
        queryset=Location.objects.all(),
        label="Location",
    )
    location = django_filters.ModelMultipleChoiceFilter(
        field_name="device__location__name",
        queryset=Location.objects.all(),
        to_field_name="name",
        label="Location (name)",
    )
    device_id = django_filters.ModelMultipleChoiceFilter(
        field_name="device",
        queryset=Device.objects.all(),
        label="Device",
    )
    device = django_filters.ModelMultipleChoiceFilter(
        field_name="device__name",
        queryset=Device.objects.all(),
        to_field_name="name",
        label="Device (name)",
    )
    device_status = django_filters.ModelMultipleChoiceFilter(
        field_name="device__status",
        queryset=Status.objects.all(),
        label="Device Status",
    )
    device_type_id = django_filters.ModelMultipleChoiceFilter(
        field_name="device__device_type",
        queryset=DeviceType.objects.all(),
        label="Device Type",
    )
    device_type = django_filters.ModelMultipleChoiceFilter(
        field_name="device__device_type__model",
        queryset=DeviceType.objects.all(),
        to_field_name="model",
        label="Device Type (model)",
    )
    device_role_id = django_filters.ModelMultipleChoiceFilter(
        field_name="device__role",
        queryset=Role.objects.all(),
        label="Device Role",
    )
    device_role = django_filters.ModelMultipleChoiceFilter(
        field_name="device__role__name",
        queryset=Role.objects.all(),
        to_field_name="name",
        label="Device Role (name)",
    )
    manufacturer_id = django_filters.ModelMultipleChoiceFilter(
        field_name="device__device_type__manufacturer",
        queryset=Role.objects.all(),
        label="Manufacturer",
    )
    manufacturer = django_filters.ModelMultipleChoiceFilter(
        field_name="device__device_type__manufacturer__name",
        queryset=Manufacturer.objects.all(),
        to_field_name="name",
        label="Manufacturer (name)",
    )
    end_of_sale = SearchFilter(
        filter_predicates={
            "hardware_notice__end_of_sale": {
                "lookup_expr": "icontains",
                "preprocessor": str.strip,
            },
        }
    )
    end_of_support = SearchFilter(
        filter_predicates={
            "hardware_notice__end_of_support": {
                "lookup_expr": "icontains",
                "preprocessor": str.strip,
            },
        }
    )
    end_of_sw_releases = SearchFilter(
        filter_predicates={
            "hardware_notice__end_of_sw_releases": {
                "lookup_expr": "icontains",
                "preprocessor": str.strip,
            },
        }
    )
    end_of_security_patches = SearchFilter(
        filter_predicates={
            "hardware_notice__end_of_security_patches": {
                "lookup_expr": "icontains",
                "preprocessor": str.strip,
            },
        }
    )

    class Meta:
        """Meta attributes for filter."""

        model = DeviceHardwareNoticeResult

        fields = "__all__"

    def _hardware_notice_available_search(self, queryset, name, value):  # pylint: disable=unused-argument
        """Perform the filtered search."""
        value = not value  # invert boolean for use in django filter
        return queryset.filter(hardware_notice__isnull=value)


class DeviceSoftwareValidationResultFilterSet(NautobotFilterSet):
    """Filter for DeviceSoftwareValidationResult."""

    q = django_filters.CharFilter(method="search", label="Search")

    software = django_filters.ModelMultipleChoiceFilter(
        field_name="software__version",
        to_field_name="version",
        queryset=SoftwareVersion.objects.all(),
        label="Software",
    )
    valid = django_filters.BooleanFilter(
        label="Valid",
        field_name="is_validated",
    )
    platform = django_filters.ModelMultipleChoiceFilter(
        field_name="device__platform",
        queryset=Platform.objects.all(),
        label="Platform",
    )
    location_id = django_filters.ModelMultipleChoiceFilter(
        field_name="device__location",
        queryset=Location.objects.all(),
        label="Location",
    )
    location = django_filters.ModelMultipleChoiceFilter(
        field_name="device__location__name",
        queryset=Location.objects.all(),
        to_field_name="name",
        label="Location (name)",
    )
    device_id = django_filters.ModelMultipleChoiceFilter(
        field_name="device",
        queryset=Device.objects.all(),
        label="Device",
    )
    device = django_filters.ModelMultipleChoiceFilter(
        field_name="device__name",
        queryset=Device.objects.all(),
        to_field_name="name",
        label="Device (name)",
    )
    device_type_id = django_filters.ModelMultipleChoiceFilter(
        field_name="device__device_type",
        queryset=DeviceType.objects.all(),
        label="Device Type",
    )
    device_type = django_filters.ModelMultipleChoiceFilter(
        field_name="device__device_type__model",
        queryset=DeviceType.objects.all(),
        to_field_name="model",
        label="Device Type (model)",
    )
    device_role_id = django_filters.ModelMultipleChoiceFilter(
        field_name="device__role",
        queryset=Role.objects.all(),
        label="Device Role",
    )
    device_role = django_filters.ModelMultipleChoiceFilter(
        field_name="device__role__name",
        queryset=Role.objects.all(),
        to_field_name="name",
        label="Device Role (name)",
    )
    exclude_sw_missing = django_filters.BooleanFilter(
        method="_exclude_sw_missing",
        label="Exclude missing software",
    )
    sw_missing_only = django_filters.BooleanFilter(
        method="_sw_missing_only",
        label="Show only missing software",
    )

    class Meta:
        """Meta attributes for filter."""

        model = DeviceSoftwareValidationResult

        fields = "__all__"

    def search(self, queryset, name, value):  # pylint: disable=unused-argument
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = Q(device__name__icontains=value) | Q(software__version__icontains=value)
        return queryset.filter(qs_filter)

    def _exclude_sw_missing(self, queryset, name, value):  # pylint: disable=unused-argument
        """Exclude devices with missing software."""
        if value:
            return queryset.filter(~Q(software=None))

        return queryset

    def _sw_missing_only(self, queryset, name, value):  # pylint: disable=unused-argument
        """Only show devices with missing software."""
        if value:
            return queryset.filter(Q(software=None))

        return queryset


class InventoryItemSoftwareValidationResultFilterSet(NautobotFilterSet):
    """Filter for InventoryItemSoftwareValidationResult."""

    q = django_filters.CharFilter(method="search", label="Search")

    software = django_filters.ModelMultipleChoiceFilter(
        field_name="software__version",
        to_field_name="version",
        queryset=SoftwareVersion.objects.all(),
        label="Software",
    )
    valid = django_filters.BooleanFilter(
        label="Valid",
        field_name="is_validated",
    )
    manufacturer = django_filters.ModelMultipleChoiceFilter(
        field_name="inventory_item__manufacturer",
        queryset=Manufacturer.objects.all(),
        label="Manufacturer",
    )
    location_id = django_filters.ModelMultipleChoiceFilter(
        field_name="inventory_item__device__location",
        queryset=Location.objects.all(),
        label="Location",
    )
    location = django_filters.ModelMultipleChoiceFilter(
        field_name="inventory_item__device__location__name",
        queryset=Location.objects.all(),
        to_field_name="name",
        label="Location (name)",
    )
    inventory_item_id = django_filters.ModelMultipleChoiceFilter(
        field_name="inventory_item",
        queryset=InventoryItem.objects.all(),
        label="Inventory Item",
    )
    inventory_item = django_filters.ModelMultipleChoiceFilter(
        field_name="inventory_item__name",
        queryset=InventoryItem.objects.all(),
        to_field_name="name",
        label="Inventory Item (name)",
    )
    part_id = django_filters.CharFilter(method="search_part_id", label="Part ID")
    device_id = django_filters.ModelMultipleChoiceFilter(
        field_name="inventory_item__device",
        queryset=Device.objects.all(),
        label="Device",
    )
    device = django_filters.ModelMultipleChoiceFilter(
        field_name="inventory_item__device__name",
        queryset=Device.objects.all(),
        to_field_name="name",
        label="Device (name)",
    )
    device_type_id = django_filters.ModelMultipleChoiceFilter(
        field_name="inventory_item__device__device_type",
        queryset=DeviceType.objects.all(),
        label="Device Type",
    )
    device_type = django_filters.ModelMultipleChoiceFilter(
        field_name="inventory_item__device__device_type__model",
        queryset=DeviceType.objects.all(),
        to_field_name="model",
        label="Device Type (model)",
    )
    device_role_id = django_filters.ModelMultipleChoiceFilter(
        field_name="inventory_item__device__role",
        queryset=Role.objects.all(),
        label="Device Role",
    )
    device_role = django_filters.ModelMultipleChoiceFilter(
        field_name="inventory_item__device__role__name",
        queryset=Role.objects.all(),
        to_field_name="name",
        label="Device Role (name)",
    )
    exclude_sw_missing = django_filters.BooleanFilter(
        method="_exclude_sw_missing",
        label="Exclude missing software",
    )
    sw_missing_only = django_filters.BooleanFilter(
        method="_sw_missing_only",
        label="Show only missing software",
    )

    class Meta:
        """Meta attributes for filter."""

        model = InventoryItemSoftwareValidationResult

        fields = "__all__"

    def search(self, queryset, name, value):  # pylint: disable=unused-argument
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = (
            Q(inventory_item__name__icontains=value)
            | Q(inventory_item__device__name__icontains=value)
            | Q(software__version__icontains=value)
        )
        return queryset.filter(qs_filter)

    def search_part_id(self, queryset, name, value):  # pylint: disable=unused-argument
        """Filter on the inventory item part ID."""
        if not value.strip():
            return queryset
        qs_filter = Q(inventory_item__part_id__icontains=value)
        return queryset.filter(qs_filter)

    def _exclude_sw_missing(self, queryset, name, value):  # pylint: disable=unused-argument
        """Exclude devices with missing software."""
        if value:
            return queryset.filter(~Q(software=None))

        return queryset

    def _sw_missing_only(self, queryset, name, value):  # pylint: disable=unused-argument
        """Only show devices with missing software."""
        if value:
            return queryset.filter(Q(software=None))

        return queryset


class ContractLCMFilterSet(NautobotFilterSet):
    """Filter for ContractLCM."""

    q = SearchFilter(
        filter_predicates={
            "name": {
                "lookup_expr": "icontains",
                "preprocessor": str.strip,
            },
            "number": {
                "lookup_expr": "icontains",
                "preprocessor": str.strip,
            },
            "support_level": {
                "lookup_expr": "icontains",
                "preprocessor": str.strip,
            },
            "comments": {
                "lookup_expr": "icontains",
                "preprocessor": str.strip,
            },
            "start": {
                "lookup_expr": "icontains",
                "preprocessor": str.strip,
            },
            "end": {
                "lookup_expr": "icontains",
                "preprocessor": str.strip,
            },
            "cost": {
                "lookup_expr": "icontains",
                "preprocessor": str.strip,
            },
            "contract_type": {
                "lookup_expr": "icontains",
                "preprocessor": str.strip,
            },
            "currency": {
                "lookup_expr": "icontains",
                "preprocessor": str.strip,
            },
        }
    )
    expired = django_filters.BooleanFilter(method="_expired_search", label="Expired")
    provider_id = django_filters.ModelMultipleChoiceFilter(
        field_name="provider",
        queryset=ProviderLCM.objects.all(),
        label="Provider",
    )
    provider = django_filters.ModelMultipleChoiceFilter(
        field_name="provider__name",
        queryset=ProviderLCM.objects.all(),
        to_field_name="name",
        label="Provider (name)",
    )

    class Meta:
        """Meta attributes for filter."""

        model = ContractLCM

        fields = "__all__"

    def _expired_search(self, queryset, name, value):  # pylint: disable=unused-argument
        """Perform the filtered search."""
        today = datetime.datetime.today().date()
        # Contract end dates less than today are expired.
        # Contract end dates greater than or equal to today, are not expired.
        # If the end date is null, the contract will never be expired.
        qs_filter = None
        if value:
            qs_filter = Q(**{"end__lt": today})
        if not value:
            qs_filter = Q(**{"end__gte": today}) | Q(**{"end__isnull": True})
        return queryset.filter(qs_filter)


class ProviderLCMFilterSet(NautobotFilterSet):
    """Filter for ProviderLCM."""

    q = SearchFilter(
        filter_predicates={
            "name": {
                "lookup_expr": "icontains",
                "preprocessor": str.strip,
            },
            "description": {
                "lookup_expr": "icontains",
                "preprocessor": str.strip,
            },
            "physical_address": {
                "lookup_expr": "icontains",
                "preprocessor": str.strip,
            },
            "country": {
                "lookup_expr": "icontains",
                "preprocessor": str.strip,
            },
            "phone": {
                "lookup_expr": "icontains",
                "preprocessor": str.strip,
            },
            "email": {
                "lookup_expr": "icontains",
                "preprocessor": str.strip,
            },
            "portal_url": {
                "lookup_expr": "icontains",
                "preprocessor": str.strip,
            },
            "comments": {
                "lookup_expr": "icontains",
                "preprocessor": str.strip,
            },
        }
    )

    class Meta:
        """Meta attributes for filter."""

        model = ProviderLCM

        fields = "__all__"


class ContactLCMFilterSet(NautobotFilterSet):
    """Filter for ContactLCMFilterSet."""

    q = django_filters.CharFilter(method="search", label="Search")

    class Meta:
        """Meta attributes for filter."""

        model = ContactLCM

        fields = "__all__"

    def search(self, queryset, name, value):  # pylint: disable=unused-argument
        """Perform the filtered search."""
        if not value.strip():
            return queryset

        qs_filter = (
            Q(name__icontains=value)
            | Q(email__icontains=value)
            | Q(phone__icontains=value)
            | Q(address__icontains=value)
        )
        return queryset.filter(qs_filter)


class CVELCMFilterSet(NautobotFilterSet, StatusModelFilterSetMixin):  # , CustomFieldModelFilterSet):
    """Filter for CVELCMFilterSet."""

    q = django_filters.CharFilter(method="search", label="Search")

    published_date = django_filters.DateTimeFromToRangeFilter()
    published_date__gte = django_filters.DateFilter(field_name="published_date", lookup_expr="gte")
    published_date__lte = django_filters.DateFilter(field_name="published_date", lookup_expr="lte")

    last_modified_date = django_filters.DateTimeFromToRangeFilter()
    last_modified_date__gte = django_filters.DateFilter(field_name="last_modified_date", lookup_expr="gte")
    last_modified_date__lte = django_filters.DateFilter(field_name="last_modified_date", lookup_expr="lte")

    cvss__gte = django_filters.NumberFilter(field_name="cvss", lookup_expr="gte")
    cvss__lte = django_filters.NumberFilter(field_name="cvss", lookup_expr="lte")

    cvss_v2__gte = django_filters.NumberFilter(field_name="cvss_v2", lookup_expr="gte")
    cvss_v2__lte = django_filters.NumberFilter(field_name="cvss_v2", lookup_expr="lte")

    cvss_v3__gte = django_filters.NumberFilter(field_name="cvss_v3", lookup_expr="gte")
    cvss_v3__lte = django_filters.NumberFilter(field_name="cvss_v3", lookup_expr="lte")
    exclude_status = StatusFilter(field_name="status", exclude=True)

    class Meta:
        """Meta attributes for filter."""

        model = CVELCM

        fields = "__all__"

    def search(self, queryset, name, value):  # pylint: disable=unused-argument
        """Perform the filtered search."""
        if not value.strip():
            return queryset

        qs_filter = Q(name__icontains=value) | Q(link__icontains=value)
        return queryset.filter(qs_filter)


class VulnerabilityLCMFilterSet(NautobotFilterSet, StatusModelFilterSetMixin):  # , CustomFieldModelFilterSet):
    """Filter for VulnerabilityLCMFilterSet."""

    q = django_filters.CharFilter(method="search", label="Search")

    cve__published_date = django_filters.DateTimeFromToRangeFilter()
    cve__published_date__gte = django_filters.DateFilter(field_name="cve__published_date", lookup_expr="gte")
    cve__published_date__lte = django_filters.DateFilter(field_name="cve__published_date", lookup_expr="lte")
    cve__severity = django_filters.ChoiceFilter(field_name="cve__severity", choices=CVESeverityChoices)

    class Meta:
        """Meta attributes for filter."""

        model = VulnerabilityLCM

        fields = "__all__"

    def search(self, queryset, name, value):  # pylint: disable=unused-argument
        """Perform the filtered search."""
        if not value.strip():
            return queryset

        # Searching all of the items that make up the __str__ method.
        qs_filter = (
            Q(cve__name__icontains=value)
            | Q(software__platform__name__icontains=value)
            | Q(software__version__icontains=value)
            | Q(device__name__icontains=value)
            | Q(inventory_item__name__icontains=value)
        )
        return queryset.filter(qs_filter)

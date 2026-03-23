"""Extensions to core filters."""

from django.db.models import Q
from django.utils import timezone
from django_filters import BooleanFilter, ModelMultipleChoiceFilter
from nautobot.apps.filters import (
    FilterExtension,
    MultiValueDateFilter,
    NaturalKeyOrPKMultipleChoiceFilter,
    RelatedMembershipBooleanFilter,
)
from nautobot.apps.forms import DynamicModelMultipleChoiceField
from nautobot.dcim.models import Platform

from nautobot_device_lifecycle_mgmt.models import ContractLCM, HardwareLCM, ValidatedSoftwareLCM


def distinct_filter(queryset, _, value):
    """Returns distinct Inventory Items by part_id."""
    if value:
        return queryset.without_tree_fields().order_by().distinct("part_id")
    return queryset


def _filter_by_lcm_validity(queryset, value, lookup_prefix):
    """Base filter that returns records based on whether their associated software is currently valid."""
    if value is None:
        return queryset

    today = timezone.now().date()
    if value:
        qs_filter = Q(**{f"{lookup_prefix}start__lte": today}) & (
            Q(**{f"{lookup_prefix}end__gte": today}) | Q(**{f"{lookup_prefix}end__isnull": True})
        )
    else:
        qs_filter = Q(**{f"{lookup_prefix}start__gt": today}) | (Q(**{f"{lookup_prefix}end__lt": today}))

    return queryset.filter(qs_filter).distinct()


def filter_software_image_files_by_validity(queryset, name, value):  # pylint: disable=unused-argument
    """Filter SoftwareImageFile records based on whether their associated software is currently valid."""
    return _filter_by_lcm_validity(
        queryset=queryset, value=value, lookup_prefix="software_version__validatedsoftwarelcm__"
    )


def filter_software_versions_by_validity(queryset, name, value):  # pylint: disable=unused-argument
    """Filter SoftwareVersion records based on whether their associated software is currently valid."""
    return _filter_by_lcm_validity(queryset=queryset, value=value, lookup_prefix="validatedsoftwarelcm__")


#
# INVENTORY ITEM FILTER EXTENSION
#
class InventoryItemFilterExtension(FilterExtension):
    """Extends Inventory Item Filters."""

    model = "dcim.inventoryitem"

    filterset_fields = {
        "nautobot_device_lifecycle_mgmt_distinct_part_id": BooleanFilter(
            method=distinct_filter, label="_dpid_dlm_app_internal_use_only"
        ),
        "nautobot_device_lifecycle_mgmt_validated_software": NaturalKeyOrPKMultipleChoiceFilter(
            field_name="validated_software",
            queryset=ValidatedSoftwareLCM.objects.all(),
            to_field_name="pk",
            label="Validated Software",
        ),
    }

    filterform_fields = {
        "nautobot_device_lifecycle_mgmt_validated_software": DynamicModelMultipleChoiceField(
            queryset=ValidatedSoftwareLCM.objects.all(),
            label="Validated Software",
            required=False,
        ),
    }


#
# DEVICE FILTER EXTENSION
#
class DeviceFilterExtension(FilterExtension):
    """Extends Device Filters."""

    model = "dcim.device"

    filterset_fields = {
        "nautobot_device_lifecycle_mgmt_device_contracts": NaturalKeyOrPKMultipleChoiceFilter(
            field_name="device_contracts",
            queryset=ContractLCM.objects.all(),
            label="Contracts",
        ),
        "nautobot_device_lifecycle_mgmt_validated_software": NaturalKeyOrPKMultipleChoiceFilter(
            field_name="validated_software",
            queryset=ValidatedSoftwareLCM.objects.all(),
            to_field_name="pk",
            label="Validated Software",
        ),
        "nautobot_device_lifecycle_mgmt_hardware_reports": ModelMultipleChoiceFilter(
            field_name="device_type__hardwarelcm",
            queryset=HardwareLCM.objects.all(),
            label="Hardware Reports",
        ),
        "nautobot_device_lifecycle_mgmt_hardware_end_of_sale": MultiValueDateFilter(
            field_name="device_type__hardwarelcm__end_of_sale",
            label="Hardware End of Sale Date",
        ),
        "nautobot_device_lifecycle_mgmt_hardware_end_of_software_releases": MultiValueDateFilter(
            field_name="device_type__hardwarelcm__end_of_sw_releases",
            label="Hardware End of Software Releases Date",
        ),
        "nautobot_device_lifecycle_mgmt_hardware_end_of_security_patches": MultiValueDateFilter(
            field_name="device_type__hardwarelcm__end_of_security_patches",
            label="Hardware End of Security Patches Date",
        ),
        "nautobot_device_lifecycle_mgmt_hardware_end_of_support": MultiValueDateFilter(
            field_name="device_type__hardwarelcm__end_of_support",
            label="Hardware End of Support Date",
        ),
        "nautobot_device_lifecycle_mgmt_software_version_end_of_support_date": MultiValueDateFilter(
            field_name="software_version__end_of_support_date",
            label="Software End of Support Date",
        ),
    }

    filterform_fields = {
        "nautobot_device_lifecycle_mgmt_device_contracts": DynamicModelMultipleChoiceField(
            queryset=ContractLCM.objects.all(),
            label="Contracts",
            required=False,
        ),
        "nautobot_device_lifecycle_mgmt_validated_software": DynamicModelMultipleChoiceField(
            queryset=ValidatedSoftwareLCM.objects.all(),
            label="Validated Software",
            required=False,
        ),
        "nautobot_device_lifecycle_mgmt_hardware_reports": DynamicModelMultipleChoiceField(
            queryset=HardwareLCM.objects.all(),
            label="Hardware Reports",
            required=False,
        ),
    }


#
# ROLE FILTER EXTENSION
#
class RoleFilterExtension(FilterExtension):
    """Extends Role Filters."""

    model = "extras.role"

    filterset_fields = {
        "nautobot_device_lifecycle_mgmt_validated_software": NaturalKeyOrPKMultipleChoiceFilter(
            field_name="validated_software",
            queryset=ValidatedSoftwareLCM.objects.all(),
            to_field_name="pk",
            label="Validated Software",
        ),
    }

    filterform_fields = {
        "nautobot_device_lifecycle_mgmt_validated_software": DynamicModelMultipleChoiceField(
            queryset=ValidatedSoftwareLCM.objects.all(),
            label="Validated Software",
            required=False,
        ),
    }


#
# DEVICE TYPE FILTER EXTENSION
#
class DeviceTypeFilterExtension(FilterExtension):
    """Extends Device Type Filters."""

    model = "dcim.devicetype"

    filterset_fields = {
        "nautobot_device_lifecycle_mgmt_validated_software": NaturalKeyOrPKMultipleChoiceFilter(
            field_name="validated_software",
            queryset=ValidatedSoftwareLCM.objects.all(),
            to_field_name="pk",
            label="Validated Software",
        ),
    }

    filterform_fields = {
        "nautobot_device_lifecycle_mgmt_validated_software": DynamicModelMultipleChoiceField(
            queryset=ValidatedSoftwareLCM.objects.all(),
            label="Validated Software",
            required=False,
        ),
    }


#
# TAG FILTER EXTENSION
#
class TagFilterExtension(FilterExtension):
    """Extends Tag Filters."""

    model = "extras.tag"

    filterset_fields = {
        "nautobot_device_lifecycle_mgmt_validated_software": NaturalKeyOrPKMultipleChoiceFilter(
            field_name="validated_software",
            queryset=ValidatedSoftwareLCM.objects.all(),
            to_field_name="pk",
            label="Validated Software",
        ),
    }

    filterform_fields = {
        "nautobot_device_lifecycle_mgmt_validated_software": DynamicModelMultipleChoiceField(
            queryset=ValidatedSoftwareLCM.objects.all(),
            label="Validated Software",
            required=False,
        ),
    }


#
# SOFTWARE IMGAE EXTENSION
#
class SoftwareImageFileFilterExtension(FilterExtension):
    """SoftwareImageFile Filter Extension."""

    model = "dcim.softwareimagefile"

    filterset_fields = {
        "nautobot_device_lifecycle_mgmt_software_version_is_valid": BooleanFilter(
            method=filter_software_image_files_by_validity,
            label="Software Version is valid",
        ),
        "nautobot_device_lifecycle_mgmt_platform": NaturalKeyOrPKMultipleChoiceFilter(
            field_name="software_version__platform",
            queryset=Platform.objects.all(),
            to_field_name="name",
            label="Software version platform (name or ID)",
        ),
    }


#
# SOFTWAREVERSION FILTER EXTENSION
#
class SoftwareVersionFilterExtension(FilterExtension):  # pylint: disable=too-few-public-methods
    """Extends SoftwareVersion Filters."""

    model = "dcim.softwareversion"

    filterset_fields = {
        "nautobot_device_lifecycle_mgmt_has_cves": RelatedMembershipBooleanFilter(
            field_name="corresponding_cves",
            label="Has CVEs",
        ),
    }

    filterset_fields = {
        "nautobot_device_lifecycle_mgmt_software_version_is_valid": BooleanFilter(
            method=filter_software_versions_by_validity,
            label="Software Version is valid",
        ),
    }


#
# REGISTER ALL EXTENSIONS
#
filter_extensions = [
    InventoryItemFilterExtension,
    DeviceFilterExtension,
    RoleFilterExtension,
    DeviceTypeFilterExtension,
    TagFilterExtension,
    SoftwareImageFileFilterExtension,
    SoftwareVersionFilterExtension,
]

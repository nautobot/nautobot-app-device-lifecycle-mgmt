"""Extensions to core filters."""

from django_filters import BooleanFilter, ModelMultipleChoiceFilter
from nautobot.apps.filters import (
    FilterExtension,
    MultiValueDateFilter,
    NaturalKeyOrPKMultipleChoiceFilter,
    RelatedMembershipBooleanFilter,
)
from nautobot.apps.forms import DynamicModelMultipleChoiceField

from nautobot_device_lifecycle_mgmt.models import ContractLCM, HardwareLCM, ValidatedSoftwareLCM


def distinct_filter(queryset, _, value):
    """Returns distinct Inventory Items by part_id."""
    if value:
        return queryset.without_tree_fields().order_by().distinct("part_id")
    return queryset


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
# TENANT FILTER EXTENSION
#
class TenantFilterExtension(FilterExtension):
    """Extends Tenant Filters."""

    model = "tenancy.tenant"

    filterset_fields = {
        "nautobot_device_lifecycle_mgmt_validated_software": NaturalKeyOrPKMultipleChoiceFilter(
            field_name="validated_software_tenants",
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


#
# REGISTER ALL EXTENSIONS
#
filter_extensions = [
    InventoryItemFilterExtension,
    DeviceFilterExtension,
    RoleFilterExtension,
    DeviceTypeFilterExtension,
    TagFilterExtension,
    TenantFilterExtension,
    SoftwareVersionFilterExtension,
]

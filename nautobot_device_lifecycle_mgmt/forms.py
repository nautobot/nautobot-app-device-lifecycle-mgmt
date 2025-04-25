"""Forms implementation for the Lifecycle Management app."""

import logging

from django import forms
from nautobot.apps.forms import (
    CustomFieldModelBulkEditFormMixin,
    DatePicker,
    DynamicModelChoiceField,
    DynamicModelChoiceMixin,
    DynamicModelMultipleChoiceField,
    NautobotBulkEditForm,
    NautobotFilterForm,
    NautobotModelForm,
    NullableDateField,
    StaticSelect2,
    StaticSelect2Multiple,
    TagFilterField,
    add_blank_choice,
)
from nautobot.core.forms.constants import BOOLEAN_WITH_BLANK_CHOICES
from nautobot.dcim.models import Device, DeviceType, InventoryItem, Location, Manufacturer, Platform, SoftwareVersion
from nautobot.extras.models import Role, Status, Tag

from nautobot_device_lifecycle_mgmt.choices import (
    ContractTypeChoices,
    CountryCodes,
    CurrencyChoices,
    CVESeverityChoices,
)
from nautobot_device_lifecycle_mgmt.models import (
    CVELCM,
    ContractLCM,
    DeviceHardwareNoticeResult,
    DeviceSoftwareValidationResult,
    HardwareLCM,
    InventoryItemSoftwareValidationResult,
    ProviderLCM,
    ValidatedSoftwareLCM,
    VulnerabilityLCM,
)

logger = logging.getLogger("nautobot_device_lifecycle_mgmt")


class CSVMultipleModelChoiceField(forms.ModelMultipleChoiceField):
    """Reference a list of PKs."""

    def prepare_value(self, value):
        """Parse a comma-separated string of PKs into a list of PKs."""
        pk_list = []
        if isinstance(value, str):
            pk_list = [val.strip() for val in value.split(",") if val]

        return super().prepare_value(pk_list)


class HardwareLCMDynamicModelChoiceField(DynamicModelChoiceMixin, forms.ModelChoiceField):
    """DynamicModelChoiceField used for 'inventory_item' field in HardwareLCMForm."""

    def to_python(self, value):
        """Overload 'to_python' in forms.ModelChoiceField to force returning 'part_id' as the field value."""
        if value in self.empty_values:
            return None
        if self.to_field_name == "part_id":
            return value
        return super().to_python(value)


class HardwareLCMForm(NautobotModelForm):
    """Hardware Device Lifecycle creation/edit form."""

    device_type = DynamicModelChoiceField(queryset=DeviceType.objects.all(), required=False)
    inventory_item = HardwareLCMDynamicModelChoiceField(
        queryset=InventoryItem.objects.without_tree_fields().order_by().distinct("part_id"),
        query_params={"part_id__nre": "^$", "nautobot_device_lifecycle_mgmt_distinct_part_id": "true"},
        label="Inventory Part ID",
        display_field="part_id",
        to_field_name="part_id",
        required=False,
    )

    class Meta:
        """Meta attributes for the HardwareLCMForm class."""

        model = models.HardwareLCM
        fields = "__all__"


class HardwareLCMBulkEditForm(NautobotBulkEditForm):
    """Hardware Device Lifecycle bulk edit form."""

    pk = forms.ModelMultipleChoiceField(queryset=HardwareLCM.objects.all(), widget=forms.MultipleHiddenInput)
    release_date = forms.DateField(widget=DatePicker(), required=False)
    end_of_sale = forms.DateField(widget=DatePicker(), required=False)
    end_of_support = forms.DateField(widget=DatePicker(), required=False)
    end_of_sw_releases = forms.DateField(widget=DatePicker(), required=False)
    end_of_security_patches = forms.DateField(widget=DatePicker(), required=False)
    documentation_url = forms.URLField(required=False)
    comments = forms.CharField(required=False)

    class Meta:
        """Meta attributes for the HardwareLCMBulkEditForm class."""

        nullable_fields = [
            "release_date",
            "end_of_sale",
            "end_of_support",
            "end_of_sw_releases",
            "end_of_security_patches",
            "documentation_url",
            "comments",
        ]


class HardwareLCMFilterForm(NautobotFilterForm):
    """Filter form for filtering HardwareLCM objects."""

    model = HardwareLCM
    field_order = [
        "q",
        "expired",
        "device_type",
        "inventory_item",
        "release_date",
        "end_of_sale",
        "end_of_support",
        "end_of_sw_releases",
        "end_of_security_patches",
        "documentation_url",
    ]
    q = forms.CharField(required=False, label="Search")
    expired = forms.BooleanField(
        required=False,
        label="Support Expired",
        widget=StaticSelect2(choices=BOOLEAN_WITH_BLANK_CHOICES),
    )

    device_type = DynamicModelMultipleChoiceField(required=False, queryset=DeviceType.objects.all())

    inventory_item = DynamicModelMultipleChoiceField(
        queryset=HardwareLCM.objects.exclude(inventory_item__isnull=True).exclude(inventory_item__exact=""),
        label="Inventory Part ID",
        display_field="inventory_item",
        to_field_name="inventory_item",
        required=False,
        widget=StaticSelect2Multiple(),
    )
    release_date = NullableDateField(required=False, widget=DatePicker(), label="Release date")
    end_of_sale = NullableDateField(required=False, widget=DatePicker(), label="End of sale")
    end_of_support = NullableDateField(required=False, widget=DatePicker(), label="End of support")
    end_of_sw_releases = NullableDateField(required=False, widget=DatePicker(), label="End of software releases")
    end_of_security_patches = NullableDateField(required=False, widget=DatePicker(), label="End of security patches")
    documentation_url = forms.CharField(required=False, label="Documentation URL")


class ValidatedSoftwareLCMForm(NautobotModelForm):
    """ValidatedSoftwareLCM creation/edit form."""

    software = DynamicModelChoiceField(queryset=SoftwareVersion.objects.all(), required=True)
    devices = DynamicModelMultipleChoiceField(queryset=Device.objects.all(), required=False)
    device_types = DynamicModelMultipleChoiceField(queryset=DeviceType.objects.all(), required=False)
    device_roles = DynamicModelMultipleChoiceField(
        queryset=Role.objects.all(), query_params={"content_types": "dcim.device"}, required=False
    )

    inventory_items = DynamicModelMultipleChoiceField(queryset=InventoryItem.objects.all(), required=False)
    object_tags = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)

    tags = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)

    class Meta:
        """Meta attributes."""

        model = ValidatedSoftwareLCM
        fields = "__all__"

        widgets = {
            "start": DatePicker(),
            "end": DatePicker(),
        }

    def clean(self):
        """Custom validation of the ValidatedSoftwareLCMForm."""
        super().clean()

        devices = self.cleaned_data.get("devices")
        device_types = self.cleaned_data.get("device_types")
        device_roles = self.cleaned_data.get("device_roles")
        inventory_items = self.cleaned_data.get("inventory_items")
        object_tags = self.cleaned_data.get("object_tags")

        if sum(obj.count() for obj in (devices, device_types, device_roles, inventory_items, object_tags)) == 0:
            msg = "You need to assign to at least one object."
            self.add_error(None, msg)


class ValidatedSoftwareLCMFilterForm(NautobotFilterForm):
    """Filter form to filter searches for SoftwareLCM."""

    model = ValidatedSoftwareLCM
    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search within Name.",
    )
    name = forms.CharField(required=False, label="Name")
    cost = forms.FloatField(required=False, label="Cost")
    start = NullableDateField(required=False, widget=DatePicker(), label="Contract Start Date")
    end = NullableDateField(required=False, widget=DatePicker(), label="Contract End Date")
    currency = forms.MultipleChoiceField(
        required=False, choices=CurrencyChoices.CHOICES, widget=StaticSelect2Multiple()
    )
    support_level = forms.CharField(required=False, label="Suport Level")
    contract_type = forms.ChoiceField(
        required=False, widget=StaticSelect2, choices=add_blank_choice(ContractTypeChoices.CHOICES)
    )
    tags = TagFilterField(model)


class ProviderLCMForm(NautobotModelForm):
    """Device Lifecycle Contract Providers creation/edit form."""

    tags = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)
    country = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(CountryCodes.CHOICES),
    )

    class Meta:
        """Meta attributes for the ProviderLCMForm class."""

        model = ProviderLCM
        fields = "__all__"


class ProviderLCMBulkEditForm(NautobotBulkEditForm):
    """Device Lifecycle Contract Providers bulk edit form."""

    pk = forms.ModelMultipleChoiceField(queryset=ProviderLCM.objects.all(), widget=forms.MultipleHiddenInput)
    description = forms.CharField(required=False)
    physical_address = forms.CharField(required=False)
    name = forms.CharField(required=False)
    phone = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    comments = forms.CharField(required=False)

    class Meta:
        """Meta attributes for the ProviderLCMBulkEditForm class."""

        nullable_fields = [
            "description",
            "physical_address",
            "country",
            "name",
            "phone",
            "email",
            "comments",
        ]


class ProviderLCMFilterForm(NautobotFilterForm):
    """Filter form for filtering ProviderLCM objects."""

    model = ProviderLCM
    field_order = [
        "q",
        "name",
        "description",
        "physical_address",
        "country",
        "phone",
        "email",
        "portal_url",
    ]
    q = forms.CharField(required=False, label="Search")
    name = forms.CharField(required=False, label="Name")
    description = forms.CharField(required=False, label="Description")
    physical_address = forms.CharField(required=False, label="Physical address")
    country = forms.MultipleChoiceField(
        choices=CountryCodes.CHOICES, label="Country", required=False, widget=StaticSelect2Multiple()
    )
    phone = forms.CharField(required=False, label="Phone")
    email = forms.CharField(required=False, label="E-mail")
    portal_url = forms.CharField(required=False, label="Portal URL")


class CVELCMForm(NautobotModelForm):
    """CVE Lifecycle Management creation/edit form."""

    published_date = forms.DateField(widget=DatePicker())
    severity = forms.ChoiceField(choices=CVESeverityChoices.CHOICES, label="Severity", required=False)
    tags = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)
    affected_softwares = DynamicModelMultipleChoiceField(queryset=SoftwareVersion.objects.all(), required=False)

    class Meta:
        """Meta attributes for the CVELCMForm class."""

        model = CVELCM

        fields = "__all__"

        widgets = {
            "published_date": DatePicker(),
        }


class CVELCMBulkEditForm(NautobotBulkEditForm, CustomFieldModelBulkEditFormMixin):
    """CVE Lifecycle Management bulk edit form."""

    model = CVELCM
    pk = forms.ModelMultipleChoiceField(queryset=CVELCM.objects.all(), widget=forms.MultipleHiddenInput)
    description = forms.CharField(required=False)
    comments = forms.CharField(required=False)
    tags = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)
    status = DynamicModelChoiceField(
        queryset=Status.objects.all(), required=False, query_params={"content_types": model._meta.label_lower}
    )

    class Meta:
        """Meta attributes for the CVELCMBulkEditForm class."""

        nullable_fields = [
            "description",
            "comments",
            "status",
            "tags",
        ]


class CVELCMFilterForm(NautobotFilterForm):
    """Filter form to filter searches for CVELCM."""

    model = CVELCM
    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search for name or link.",
    )
    severity = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(CVESeverityChoices.CHOICES),
    )

    published_date_before = forms.DateField(label="Published Date Before", required=False, widget=DatePicker())
    published_date_after = forms.DateField(label="Published Date After", required=False, widget=DatePicker())

    cvss__gte = forms.FloatField(label="CVSS Score Above", required=False)
    cvss__lte = forms.FloatField(label="CVSS Score Below", required=False)

    cvss_v2__gte = forms.FloatField(label="CVSSv2 Score Above", required=False)
    cvss_v2__lte = forms.FloatField(label="CVSSv2 Score Below", required=False)

    cvss_v3__gte = forms.FloatField(label="CVSSv3 Score Above", required=False)
    cvss_v3__lte = forms.FloatField(label="CVSSv3 Score Below", required=False)
    affected_softwares = forms.ModelMultipleChoiceField(queryset=SoftwareVersion.objects.all(), required=False)

    status = DynamicModelMultipleChoiceField(
        queryset=Status.objects.all(),
        required=False,
        query_params={"content_types": model._meta.label_lower},
        to_field_name="name",
    )
    exclude_status = DynamicModelMultipleChoiceField(
        label="Exclude Status",
        required=False,
        queryset=Status.objects.all(),
        query_params={"content_types": model._meta.label_lower},  # pylint: disable=protected-access, no-member
        to_field_name="name",
    )
    tag = TagFilterField(model)

    class Meta:
        """Meta attributes."""

        model = CVELCM
        fields = [
            "q",
            "published_date_before",
            "published_date_after",
            "severity",
            "status",
            "affected_softwares",
        ]


class VulnerabilityLCMForm(NautobotModelForm):
    """Vulnerability Lifecycle Management creation/edit form."""

    tags = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)

    class Meta:
        """Meta attributes for the VulnerabilityLCMForm class."""

        model = VulnerabilityLCM

        fields = "__all__"


class VulnerabilityLCMBulkEditForm(NautobotBulkEditForm, CustomFieldModelBulkEditFormMixin):
    """Vulnerability Lifecycle Management bulk edit form."""

    pk = forms.ModelMultipleChoiceField(queryset=VulnerabilityLCM.objects.all(), widget=forms.MultipleHiddenInput)
    tags = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)

    class Meta:
        """Meta attributes for the VulnerabilityLCMBulkEditForm class."""

        model = VulnerabilityLCM
        nullable_fields = [
            "status",
            "tags",
        ]


class VulnerabilityLCMFilterForm(NautobotFilterForm):
    """Filter form to filter searches for VulnerabilityLCM."""

    model = VulnerabilityLCM
    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search for name or link.",
    )
    cve = DynamicModelMultipleChoiceField(required=False, queryset=CVELCM.objects.all(), label="CVE")
    cve__published_date__lte = forms.DateField(label="CVE Published Date Before", required=False, widget=DatePicker())
    cve__published_date__gte = forms.DateField(label="CVE Published Date After", required=False, widget=DatePicker())
    cve__severity = forms.ChoiceField(
        label="CVE Severity",
        required=False,
        choices=add_blank_choice(CVESeverityChoices.CHOICES),
    )
    software = DynamicModelMultipleChoiceField(required=False, queryset=SoftwareVersion.objects.all())
    device = DynamicModelMultipleChoiceField(required=False, queryset=Device.objects.all())
    inventory_item = DynamicModelMultipleChoiceField(required=False, queryset=InventoryItem.objects.all())
    status = DynamicModelMultipleChoiceField(queryset=Status.objects.all(), required=False, to_field_name="name")
    exclude_status = DynamicModelMultipleChoiceField(
        label="Exclude Status",
        required=False,
        queryset=Status.objects.all(),
        query_params={"content_types": model._meta.label_lower},  # pylint: disable=protected-access, no-member
        to_field_name="name",
    )
    tag = TagFilterField(model)

    class Meta:
        """Meta attributes."""

        model = VulnerabilityLCM
        fields = [
            "q",
            "cve",
            "software",
            "device",
            "inventory_item",
            "status",
            "tags",
        ]

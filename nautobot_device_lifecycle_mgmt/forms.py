"""Forms implementation for the Lifecycle Management plugin."""
import logging
from django import forms

from nautobot.dcim.models import Device, DeviceRole, DeviceType, InventoryItem, Platform, Region, Site
from nautobot.extras.forms import (
    CustomFieldModelCSVForm,
    CustomFieldModelForm,
    RelationshipModelForm,
)
from nautobot.extras.models import Tag
from nautobot.utilities.forms import (
    BootstrapMixin,
    BulkEditForm,
    DatePicker,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    StaticSelect2,
    BOOLEAN_WITH_BLANK_CHOICES,
    add_blank_choice,
    CSVModelChoiceField,
)
from nautobot_device_lifecycle_mgmt.choices import ContractTypeChoices, CurrencyChoices, PoCTypeChoices, CountryCodes
from nautobot_device_lifecycle_mgmt.models import (
    HardwareLCM,
    InventoryItemSoftwareValidationResult,
    SoftwareLCM,
    ValidatedSoftwareLCM,
    DeviceSoftwareValidationResult,
    ContractLCM,
    ProviderLCM,
    ContactLCM,
)

logger = logging.getLogger("nautobot_device_lifecycle_mgmt")


class HardwareLCMForm(BootstrapMixin, CustomFieldModelForm, RelationshipModelForm):
    """Hardware Device Lifecycle creation/edit form."""

    inventory_item = forms.ModelChoiceField(
        queryset=InventoryItem.objects.exclude(part_id__exact="")
        .distinct()
        .order_by("part_id")
        .values_list("part_id", flat=True),
        label="Inventory Part ID",
        to_field_name="part_id",
        required=False,
    )

    class Meta:
        """Meta attributes for the HardwareLCMForm class."""

        model = HardwareLCM
        fields = HardwareLCM.csv_headers

        widgets = {
            "release_date": DatePicker(),
            "end_of_sale": DatePicker(),
            "end_of_support": DatePicker(),
            "end_of_sw_releases": DatePicker(),
            "end_of_security_patches": DatePicker(),
        }


class HardwareLCMBulkEditForm(BootstrapMixin, BulkEditForm):
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


class HardwareLCMFilterForm(BootstrapMixin, forms.ModelForm):
    """Filter form to filter searches."""

    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Select a date that will be used to search end_of_support and end_of_sale",
    )
    device_type = forms.ModelMultipleChoiceField(
        required=False, queryset=DeviceType.objects.all(), to_field_name="slug"
    )

    inventory_item = forms.ModelMultipleChoiceField(
        queryset=HardwareLCM.objects.exclude(inventory_item__isnull=True)
        .exclude(inventory_item__exact="")
        .values_list("inventory_item", flat=True),
        label="Inventory Part ID",
        required=False,
    )

    class Meta:
        """Meta attributes for the HardwareLCMFilterForm class."""

        model = HardwareLCM
        # Define the fields above for ordering and widget purposes
        fields = [
            "q",
            "device_type",
            "inventory_item",
            "end_of_sale",
            "end_of_support",
            "end_of_sw_releases",
            "end_of_security_patches",
            "documentation_url",
        ]

        widgets = {
            "end_of_sale": DatePicker(),
            "end_of_support": DatePicker(),
            "end_of_sw_releases": DatePicker(),
            "end_of_security_patches": DatePicker(),
        }


class HardwareLCMCSVForm(CustomFieldModelCSVForm):
    """Form for creating bulk Hardware Device Lifecycle notices."""

    device_type = forms.ModelChoiceField(
        required=False, queryset=DeviceType.objects.all(), to_field_name="model", label="Device type"
    )

    inventory_item = forms.ModelChoiceField(
        required=False,
        queryset=InventoryItem.objects.exclude(part_id__exact="")
        .distinct()
        .order_by("part_id")
        .values_list("part_id", flat=True),
        to_field_name="part_id",
        label="Inventory Item",
    )

    class Meta:
        """Meta attributes for the HardwareLCMCSVForm class."""

        model = HardwareLCM
        fields = HardwareLCM.csv_headers


class SoftwareLCMForm(BootstrapMixin, CustomFieldModelForm, RelationshipModelForm):
    """SoftwareLCM creation/edit form."""

    tags = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)

    class Meta:
        """Meta attributes."""

        model = SoftwareLCM
        fields = (
            *SoftwareLCM.csv_headers,
            "tags",
        )

        widgets = {
            "release_date": DatePicker(),
            "end_of_support": DatePicker(),
        }


class SoftwareLCMFilterForm(BootstrapMixin, forms.ModelForm):
    """Filter form to filter searches for SoftwareLCM."""

    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search for version, alias, or date for release_date or end_of_support.",
    )
    version = forms.CharField(required=False)
    device_platform = forms.ModelMultipleChoiceField(
        required=False, queryset=Platform.objects.all(), to_field_name="slug"
    )
    release_date_before = forms.DateField(label="Release Date Before", required=False, widget=DatePicker())
    release_date_after = forms.DateField(label="Release Date After", required=False, widget=DatePicker())
    end_of_support_before = forms.DateField(label="End of Software Support Before", required=False, widget=DatePicker())
    end_of_support_after = forms.DateField(label="End of Software Support After", required=False, widget=DatePicker())

    class Meta:
        """Meta attributes."""

        model = SoftwareLCM
        fields = [
            "q",
            "version",
            "device_platform",
            "release_date_before",
            "release_date_after",
            "end_of_support_before",
            "end_of_support_after",
            "documentation_url",
            "download_url",
            "image_file_name",
            "image_file_checksum",
            "long_term_support",
            "pre_release",
        ]

        widgets = {
            "long_term_support": StaticSelect2(choices=BOOLEAN_WITH_BLANK_CHOICES),
            "pre_release": StaticSelect2(choices=BOOLEAN_WITH_BLANK_CHOICES),
        }


class SoftwareLCMCSVForm(CustomFieldModelCSVForm):
    """Form for bulk creating SoftwareLCM objects."""

    device_platform = CSVModelChoiceField(
        queryset=Platform.objects.all(),
        required=True,
        to_field_name="slug",
        help_text="Device platform",
    )

    class Meta:
        """Meta attributes for the SoftwareLCMCSVForm class."""

        model = SoftwareLCM
        fields = SoftwareLCM.csv_headers


class ValidatedSoftwareLCMForm(BootstrapMixin, CustomFieldModelForm, RelationshipModelForm):
    """ValidatedSoftwareLCM creation/edit form."""

    software = DynamicModelChoiceField(queryset=SoftwareLCM.objects.all(), required=True)
    devices = DynamicModelMultipleChoiceField(queryset=Device.objects.all(), required=False)
    device_types = DynamicModelMultipleChoiceField(queryset=DeviceType.objects.all(), required=False)
    device_roles = DynamicModelMultipleChoiceField(queryset=DeviceRole.objects.all(), required=False)
    inventory_items = DynamicModelMultipleChoiceField(queryset=InventoryItem.objects.all(), required=False)
    object_tags = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)

    tags = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)

    class Meta:
        """Meta attributes."""

        model = ValidatedSoftwareLCM
        fields = (
            "software",
            "devices",
            "device_types",
            "device_roles",
            "inventory_items",
            "object_tags",
            "start",
            "end",
            "preferred",
            "tags",
        )

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


class ValidatedSoftwareLCMFilterForm(BootstrapMixin, CustomFieldModelForm, RelationshipModelForm):
    """Filter form to filter searches for SoftwareLCM."""

    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search for start or end date of validity.",
    )
    software = DynamicModelChoiceField(required=False, queryset=SoftwareLCM.objects.all())
    devices = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        to_field_name="name",
        required=False,
    )
    device_types = DynamicModelMultipleChoiceField(
        queryset=DeviceType.objects.all(),
        to_field_name="model",
        required=False,
    )
    device_roles = DynamicModelMultipleChoiceField(
        queryset=DeviceRole.objects.all(),
        to_field_name="slug",
        required=False,
    )
    inventory_items = DynamicModelMultipleChoiceField(
        queryset=InventoryItem.objects.all(),
        to_field_name="name",
        required=False,
    )
    object_tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        to_field_name="slug",
        required=False,
    )
    start_before = forms.DateField(label="Valid Since Date Before", required=False, widget=DatePicker())
    start_after = forms.DateField(label="Valid Since Date After", required=False, widget=DatePicker())
    preferred = forms.BooleanField(required=False, widget=StaticSelect2(choices=BOOLEAN_WITH_BLANK_CHOICES))
    valid = forms.BooleanField(
        label="Valid Now", required=False, widget=StaticSelect2(choices=BOOLEAN_WITH_BLANK_CHOICES)
    )

    class Meta:
        """Meta attributes."""

        model = ValidatedSoftwareLCM
        fields = [
            "q",
            "software",
            "devices",
            "device_types",
            "device_roles",
            "inventory_items",
            "object_tags",
            "preferred",
            "valid",
            "start_before",
            "start_after",
        ]


class DeviceSoftwareValidationResultFilterForm(BootstrapMixin, CustomFieldModelForm, RelationshipModelForm):
    """Filter form to filter searches for DeviceSoftwareValidationResult."""

    q = forms.CharField(
        required=False,
        label="Search",
    )
    software = DynamicModelMultipleChoiceField(
        queryset=SoftwareLCM.objects.all(),
        to_field_name="version",
        required=False,
    )
    site = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        to_field_name="slug",
        required=False,
    )
    region = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        to_field_name="slug",
        required=False,
    )
    device = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        to_field_name="name",
        required=False,
    )
    device_type = DynamicModelMultipleChoiceField(
        queryset=DeviceType.objects.all(),
        to_field_name="model",
        required=False,
    )
    device_role = DynamicModelMultipleChoiceField(
        queryset=DeviceRole.objects.all(),
        to_field_name="slug",
        required=False,
    )
    exclude_sw_missing = forms.BooleanField(
        required=False,
        widget=StaticSelect2(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label="Exclude missing software",
    )

    class Meta:
        """Meta attributes."""

        model = DeviceSoftwareValidationResult
        fields = ["q", "software", "site", "region", "device", "device_type", "device_role", "exclude_sw_missing"]


class InventoryItemSoftwareValidationResultFilterForm(BootstrapMixin, CustomFieldModelForm, RelationshipModelForm):
    """Filter form to filter searches for InventoryItemSoftwareValidationResult."""

    q = forms.CharField(
        required=False,
        label="Search",
    )
    software = DynamicModelMultipleChoiceField(
        queryset=SoftwareLCM.objects.all(),
        to_field_name="version",
        required=False,
    )
    site = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        to_field_name="slug",
        required=False,
    )
    region = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        to_field_name="slug",
        required=False,
    )
    inventory_item = DynamicModelMultipleChoiceField(
        queryset=InventoryItem.objects.all(),
        to_field_name="name",
        required=False,
    )
    part_id = forms.CharField(
        required=False,
        label="Part ID",
    )
    device = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        to_field_name="name",
        required=False,
    )
    device_type = DynamicModelMultipleChoiceField(
        queryset=DeviceType.objects.all(),
        to_field_name="model",
        required=False,
    )
    device_role = DynamicModelMultipleChoiceField(
        queryset=DeviceRole.objects.all(),
        to_field_name="slug",
        required=False,
    )
    exclude_sw_missing = forms.BooleanField(
        required=False,
        widget=StaticSelect2(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label="Exclude missing software",
    )

    class Meta:
        """Meta attributes."""

        model = InventoryItemSoftwareValidationResult
        fields = [
            "q",
            "software",
            "site",
            "region",
            "inventory_item",
            "part_id",
            "device",
            "device_type",
            "device_role",
            "exclude_sw_missing",
        ]


class CSVMultipleModelChoiceField(forms.ModelMultipleChoiceField):
    """Reference a list of PKs."""

    def prepare_value(self, value):
        """Parse a comma-separated string of PKs into a list of PKs."""
        pk_list = []
        if isinstance(value, str):
            pk_list = [val.strip() for val in value.split(",") if val]

        return super().prepare_value(pk_list)


class ValidatedSoftwareLCMCSVForm(CustomFieldModelCSVForm):
    """Form for bulk creating ValidatedSoftwareLCM objects."""

    devices = CSVMultipleModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        to_field_name="name",
        help_text="Comma-separated list of Device Names",
    )
    devices = CSVMultipleModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        to_field_name="name",
        help_text="Comma-separated list of Device Names",
    )
    device_types = CSVMultipleModelChoiceField(
        queryset=DeviceType.objects.all(),
        required=False,
        to_field_name="model",
        help_text="Comma-separated list of DeviceType Models",
    )
    device_roles = CSVMultipleModelChoiceField(
        queryset=DeviceRole.objects.all(),
        required=False,
        to_field_name="slug",
        help_text="Comma-separated list of DeviceRole Slugs",
    )
    inventory_items = CSVMultipleModelChoiceField(
        queryset=InventoryItem.objects.all(),
        required=False,
        to_field_name="name",
        help_text="Comma-separated list of InventoryItem Names",
    )
    object_tags = CSVMultipleModelChoiceField(
        queryset=Tag.objects.all(), required=False, to_field_name="slug", help_text="Comma-separated list of Tag Slugs"
    )

    class Meta:
        """Meta attributes for the ValidatedSoftwareLCM class."""

        model = ValidatedSoftwareLCM
        fields = ValidatedSoftwareLCM.csv_headers


class ContractLCMForm(BootstrapMixin, CustomFieldModelForm, RelationshipModelForm):
    """Device Lifecycle Contracts creation/edit form."""

    provider = forms.ModelChoiceField(
        queryset=ProviderLCM.objects.all(),
        label="Vendor",
        to_field_name="pk",
        required=True,
    )
    contract_type = forms.ChoiceField(choices=add_blank_choice(ContractTypeChoices.CHOICES), label="Contract Type")
    currency = forms.ChoiceField(
        required=False, widget=StaticSelect2, choices=add_blank_choice(CurrencyChoices.CHOICES)
    )
    tags = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)

    class Meta:
        """Meta attributes for the ContractLCMForm class."""

        model = ContractLCM
        fields = [
            "provider",
            "name",
            "number",
            "start",
            "end",
            "cost",
            "currency",
            "support_level",
            "contract_type",
            "comments",
            "tags",
        ]

        widgets = {
            "end": DatePicker(),
            "start": DatePicker(),
        }

    def get_form_kwargs(self):
        """Get from kwargs override to capture the query params sent from other pages withing the LCM project."""
        return {"provider": self.request.GET.get("provider")}  # pylint: disable=E1101


class ContractLCMBulkEditForm(BootstrapMixin, BulkEditForm):
    """Device Lifecycle Contrcts bulk edit form."""

    pk = forms.ModelMultipleChoiceField(queryset=ContractLCM.objects.all(), widget=forms.MultipleHiddenInput)
    provider = forms.ModelMultipleChoiceField(queryset=ProviderLCM.objects.all(), required=False)
    start = forms.DateField(widget=DatePicker(), required=False)
    end = forms.DateField(widget=DatePicker(), required=False)
    cost = forms.FloatField(required=False)
    currency = forms.ChoiceField(required=False, choices=CurrencyChoices.CHOICES)
    contract_type = forms.ChoiceField(choices=ContractTypeChoices.CHOICES, required=False)
    support_level = forms.CharField(required=False)

    class Meta:
        """Meta attributes for the ContractLCMBulkEditForm class."""

        nullable_fields = [
            "start",
            "end",
            "cost",
            "currency",
            "support_level",
            "contract_type",
        ]


class ContractLCMFilterForm(BootstrapMixin, forms.ModelForm):
    """Filter form to filter searches."""

    q = forms.CharField(required=False, label="Search")
    provider = forms.ModelMultipleChoiceField(required=False, queryset=ProviderLCM.objects.all(), to_field_name="pk")
    currency = forms.ChoiceField(required=False, widget=StaticSelect2, choices=CurrencyChoices.CHOICES)
    name = forms.CharField(required=False)

    class Meta:
        """Meta attributes for the ContractLCMFilterForm class."""

        model = ContractLCM
        # Define the fields above for ordering and widget purposes
        fields = [
            "q",
            "provider",
            "name",
            "start",
            "end",
            "cost",
            "currency",
            "support_level",
            "contract_type",
        ]

        widgets = {
            "start": DatePicker(),
            "end": DatePicker(),
        }


class ContractLCMCSVForm(CustomFieldModelCSVForm):
    """Form for creating bulk Device Lifecycle contracts."""

    provider = forms.ModelChoiceField(
        required=True, queryset=ProviderLCM.objects.all(), to_field_name="name", label="Contract Provider"
    )

    class Meta:
        """Meta attributes for the ContractLCMCSVForm class."""

        model = ContractLCM
        fields = ContractLCM.csv_headers


class ProviderLCMForm(BootstrapMixin, CustomFieldModelForm, RelationshipModelForm):
    """Device Lifecycle Contract Providers creation/edit form."""

    tags = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)
    country = forms.ChoiceField(
        widget=StaticSelect2,
        required=False,
        choices=add_blank_choice(CountryCodes.CHOICES),
    )

    class Meta:
        """Meta attributes for the ProviderLCMForm class."""

        model = ProviderLCM
        fields = [
            "name",
            "description",
            "physical_address",
            "country",
            "phone",
            "email",
            "portal_url",
            "comments",
            "tags",
        ]


class ProviderLCMBulkEditForm(BootstrapMixin, BulkEditForm):
    """Device Lifecycle Contract Providers bulk edit form."""

    pk = forms.ModelMultipleChoiceField(queryset=ProviderLCM.objects.all(), widget=forms.MultipleHiddenInput)
    description = forms.CharField(required=False)
    physical_address = forms.CharField(required=False)
    contact_name = forms.CharField(required=False)
    contact_phone = forms.CharField(required=False)
    contact_email = forms.EmailField(required=False)
    comments = forms.CharField(required=False)

    class Meta:
        """Meta attributes for the ProviderLCMBulkEditForm class."""

        nullable_fields = [
            "description",
            "physical_address",
            "country",
            "contact_name",
            "contact_phone",
            "contact_email",
            "comments",
        ]


class ProviderLCMFilterForm(BootstrapMixin, forms.ModelForm):
    """Filter form to filter searches."""

    q = forms.CharField(required=False, label="Search")
    name = forms.CharField(required=False)
    country = forms.ChoiceField(
        widget=StaticSelect2,
        required=False,
        choices=add_blank_choice(CountryCodes.CHOICES),
    )

    class Meta:
        """Meta attributes for the ProviderLCMFilterForm class."""

        model = ProviderLCM
        # Define the fields above for ordering and widget purposes
        fields = [
            "q",
            "name",
            "description",
            "physical_address",
            "country",
            "phone",
            "email",
            "comments",
        ]


class ProviderLCMCSVForm(CustomFieldModelCSVForm):
    """Form for creating bulk Device Lifecycle providers."""

    class Meta:
        """Meta attributes for the ProviderLCMCSVForm class."""

        model = ProviderLCM
        fields = ProviderLCM.csv_headers


class ContactLCMForm(BootstrapMixin, CustomFieldModelForm, RelationshipModelForm):
    """Device Lifecycle Contract Resources creation/edit form."""

    type = forms.ChoiceField(choices=PoCTypeChoices.CHOICES, required=False)
    tags = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)

    class Meta:
        """Meta attributes for the ContactLCMForm class."""

        model = ContactLCM
        fields = [
            "contract",
            "name",
            "address",
            "phone",
            "email",
            "comments",
            "type",
            "priority",
            "tags",
        ]

    def get_form_kwargs(self):
        """Get from kwargs override to capture the query params sent from other pages withing the LCM project."""
        return {
            "type": self.request.GET.get("type"),  # pylint: disable=E1101
            "contract": self.request.GET.get("contract"),  # pylint: disable=E1101
        }


class ContactLCMBulkEditForm(BootstrapMixin, BulkEditForm):
    """Device Lifecycle Contract Resources bulk edit form."""

    pk = forms.ModelMultipleChoiceField(queryset=ContractLCM.objects.all(), widget=forms.MultipleHiddenInput)
    address = forms.CharField(required=False)
    phone = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    priority = forms.IntegerField(required=False)
    comments = forms.CharField(required=False)
    contract = forms.ModelChoiceField(queryset=ContractLCM.objects.all())

    class Meta:
        """Meta attributes for the ContactLCMBulkEditForm class."""

        nullable_fields = ["address", "phone", "email", "comments", "priority", "contract"]


class ContactLCMFilterForm(BootstrapMixin, forms.ModelForm):
    """Filter form to filter searches."""

    q = forms.CharField(required=False, label="Search")
    name = forms.CharField(required=False)
    contract = forms.ModelChoiceField(queryset=ContractLCM.objects.all(), required=False)
    priority = forms.IntegerField(required=False)

    class Meta:
        """Meta attributes for the ContactLCMFilterForm class."""

        model = ContactLCM
        # Define the fields above for ordering and widget purposes
        fields = [
            "q",
            "contract",
            "name",
            "address",
            "phone",
            "email",
            "priority",
        ]


class ContactLCMCSVForm(CustomFieldModelCSVForm):
    """Form for creating bulk Device Lifecycle resources/contacts."""

    contract = forms.ModelChoiceField(
        required=True, queryset=ContractLCM.objects.all(), to_field_name="name", label="Contract Name"
    )
    type = forms.ChoiceField(choices=PoCTypeChoices.CHOICES, label="PoC Type")

    class Meta:
        """Meta attributes for the ContactLCMCSVForm class."""

        model = ContactLCM
        fields = ContactLCM.csv_headers

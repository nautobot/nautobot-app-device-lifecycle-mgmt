"""Forms implementation for the LifeCycle Management plugin."""
import logging
from django import forms
from django.contrib.contenttypes.models import ContentType

from nautobot.utilities.forms import BootstrapMixin, DatePicker, DynamicModelMultipleChoiceField
from nautobot.dcim.models import Device, DeviceType, InventoryItem, Platform
from nautobot.extras.forms import (
    CustomFieldModelCSVForm,
    CustomFieldModelForm,
    RelationshipModelForm,
)
from nautobot.extras.models import Tag
from nautobot.utilities.forms import (
    BulkEditForm,
    DynamicModelChoiceField,
    StaticSelect2,
    BOOLEAN_WITH_BLANK_CHOICES,
    add_blank_choice,
    CSVModelChoiceField,
)
from nautobot_device_lifecycle_mgmt.choices import ContractTypeChoices, CurrencyChoices, PoCTypeChoices, CountryCodes
from nautobot_device_lifecycle_mgmt.models import (
    HardwareLCM,
    SoftwareLCM,
    ValidatedSoftwareLCM,
    ContractLCM,
    ProviderLCM,
    ContactLCM,
)

logger = logging.getLogger("nautobot_device_lifecycle_mgmt")


class HardwareLCMForm(BootstrapMixin, CustomFieldModelForm, RelationshipModelForm):
    """Hardware Device LifeCycle creation/edit form."""

    inventory_item = forms.ModelChoiceField(
        queryset=InventoryItem.objects.exclude(part_id__exact="")
        .distinct("part_id")
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
    """Hardware Device LifeCycle bulk edit form."""

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
        .distinct("part_id")
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

    assigned_to_device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        query_params={"id": "$assigned_to_device"},
        label="Assigned To",
    )
    assigned_to_device_type = DynamicModelChoiceField(
        queryset=DeviceType.objects.all(),
        required=False,
        query_params={"id": "$assigned_to_device_type"},
        label="Assigned To",
    )
    assigned_to_inventory_item = DynamicModelChoiceField(
        queryset=InventoryItem.objects.all(),
        required=False,
        query_params={"id": "$assigned_to_inventory_item"},
        label="Assigned To",
    )

    tags = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)

    class Meta:
        """Meta attributes."""

        model = ValidatedSoftwareLCM
        fields = (
            "software",
            "assigned_to_device",
            "assigned_to_device_type",
            "assigned_to_inventory_item",
            "start",
            "end",
            "preferred",
            "tags",
        )

        widgets = {
            "start": DatePicker(),
            "end": DatePicker(),
        }

    def __init__(self, *args, **kwargs):
        """Set up initial data for this form."""
        instance = kwargs.get("instance")
        initial = kwargs.get("initial", {}).copy()

        if instance:
            if isinstance(instance.assigned_to, Device):
                initial["assigned_to_device"] = instance.assigned_to
            elif isinstance(instance.assigned_to, DeviceType):
                initial["assigned_to_device_type"] = instance.assigned_to
            elif isinstance(instance.assigned_to, InventoryItem):
                initial["assigned_to_inventory_item"] = instance.assigned_to

        kwargs["initial"] = initial

        super().__init__(*args, **kwargs)

    def clean(self):
        """Form validation logic."""
        super().clean()

        if (
            sum(
                1
                for data in (
                    self.cleaned_data.get("assigned_to_device"),
                    self.cleaned_data.get("assigned_to_device_type"),
                    self.cleaned_data.get("assigned_to_inventory_item"),
                )
                if data
            )
            > 1
        ):
            raise forms.ValidationError(
                "Cannot assign to more than one object. Choose either device, device type or inventory item."
            )

        if self.cleaned_data.get("assigned_to_device"):
            self.instance.assigned_to = self.cleaned_data.get("assigned_to_device")
        elif self.cleaned_data.get("assigned_to_device_type"):
            self.instance.assigned_to = self.cleaned_data.get("assigned_to_device_type")
        elif self.cleaned_data.get("assigned_to_inventory_item"):
            self.instance.assigned_to = self.cleaned_data.get("assigned_to_inventory_item")
        else:
            raise forms.ValidationError("A device, device type or inventory item must be selected.")


class ValidatedSoftwareLCMFilterForm(BootstrapMixin, CustomFieldModelForm, RelationshipModelForm):
    """Filter form to filter searches for SoftwareLCM."""

    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search for start or end date of validity.",
    )
    software = forms.ModelChoiceField(required=False, queryset=SoftwareLCM.objects.all())
    start = forms.DateField(required=False, widget=DatePicker())
    end = forms.DateField(required=False, widget=DatePicker())
    preferred = forms.BooleanField(required=False, widget=StaticSelect2(choices=BOOLEAN_WITH_BLANK_CHOICES))

    class Meta:
        """Meta attributes."""

        model = ValidatedSoftwareLCM
        fields = [
            "q",
            "software",
            "start",
            "end",
            "preferred",
        ]


class ValidatedSoftwareLCMCSVForm(CustomFieldModelCSVForm):
    """Form for bulk creating ValidatedSoftwareLCM objects."""

    assigned_to_content_type = CSVModelChoiceField(
        queryset=ContentType.objects.all(),
        required=True,
        to_field_name="model",
        help_text="Assigned to object type",
    )

    class Meta:
        """Meta attributes for the ValidatedSoftwareLCM class."""

        model = ValidatedSoftwareLCM
        fields = ValidatedSoftwareLCM.csv_headers


class ContractLCMForm(BootstrapMixin, CustomFieldModelForm, RelationshipModelForm):
    """Device LifeCycle Contracts creation/edit form."""

    provider = forms.ModelChoiceField(
        queryset=ProviderLCM.objects.all(),
        label="Contract Provider",
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
    """Device LifeCycle Contrcts bulk edit form."""

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
    """Device LifeCycle Contract Providers creation/edit form."""

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
    """Device LifeCycle Contract Providers bulk edit form."""

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
    """Device LifeCycle Contract Resources creation/edit form."""

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
    """Device LifeCycle Contract Resources bulk edit form."""

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

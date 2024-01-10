"""Forms implementation for the Lifecycle Management app."""
import logging

from django import forms
from django.db.models import Q
from nautobot.apps.forms import (
    add_blank_choice,
    DatePicker,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    NautobotBulkEditForm,
    NautobotModelForm,
    StaticSelect2,
    StaticSelect2Multiple,
    TagFilterField,
)
from nautobot.core.forms.constants import BOOLEAN_WITH_BLANK_CHOICES
from nautobot.dcim.models import Device, DeviceType, InventoryItem, Location, Manufacturer, Platform
from nautobot.extras.forms import CustomFieldModelBulkEditFormMixin, NautobotFilterForm
from nautobot.extras.models import Role, Status, Tag

from nautobot_device_lifecycle_mgmt.choices import (
    ContractTypeChoices,
    CountryCodes,
    CurrencyChoices,
    CVESeverityChoices,
    PoCTypeChoices,
)
from nautobot_device_lifecycle_mgmt.models import (
    CVELCM,
    ContactLCM,
    ContractLCM,
    DeviceSoftwareValidationResult,
    HardwareLCM,
    InventoryItemSoftwareValidationResult,
    ProviderLCM,
    SoftwareImageLCM,
    SoftwareLCM,
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


class HardwareLCMForm(NautobotModelForm):
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
        fields = [
            "device_type",
            "inventory_item",
            "release_date",
            "end_of_sale",
            "end_of_support",
            "end_of_sw_releases",
            "end_of_security_patches",
            "documentation_url",
            "comments",
        ]

        widgets = {
            "release_date": DatePicker(),
            "end_of_sale": DatePicker(),
            "end_of_support": DatePicker(),
            "end_of_sw_releases": DatePicker(),
            "end_of_security_patches": DatePicker(),
        }


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
    """Filter form to filter searches."""

    model = HardwareLCM
    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Select a date that will be used to search end_of_support and end_of_sale",
    )
    device_type = forms.ModelMultipleChoiceField(
        required=False, queryset=DeviceType.objects.all(), to_field_name="model"
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

        # Define the fields above for ordering and widget purposes
        model = HardwareLCM
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


class SoftwareLCMForm(NautobotModelForm):
    """SoftwareLCM creation/edit form."""

    tags = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)

    class Meta:
        """Meta attributes."""

        model = SoftwareLCM
        fields = [
            "device_platform",
            "version",
            "alias",
            "release_date",
            "end_of_support",
            "documentation_url",
            "long_term_support",
            "pre_release",
            "tags",
        ]

        widgets = {
            "release_date": DatePicker(),
            "end_of_support": DatePicker(),
        }


class SoftwareLCMFilterForm(NautobotFilterForm):
    """Filter form to filter searches for SoftwareLCM."""

    model = SoftwareLCM
    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search for version, alias, or date for release_date or end_of_support.",
    )
    version = forms.CharField(required=False)
    device_platform = forms.ModelMultipleChoiceField(
        required=False, queryset=Platform.objects.all(), to_field_name="name"
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
            "long_term_support",
            "pre_release",
        ]


class SoftwareImageLCMForm(NautobotModelForm):
    """SoftwareImageLCM creation/edit form."""

    software = DynamicModelChoiceField(queryset=SoftwareLCM.objects.all(), required=True)
    device_types = DynamicModelMultipleChoiceField(queryset=DeviceType.objects.all(), required=False)
    inventory_items = DynamicModelMultipleChoiceField(queryset=InventoryItem.objects.all(), required=False)
    object_tags = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)

    tags = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)

    class Meta:
        """Meta attributes."""

        model = SoftwareImageLCM
        fields = [
            "image_file_name",
            "software",
            "device_types",
            "inventory_items",
            "object_tags",
            "download_url",
            "image_file_checksum",
            "hashing_algorithm",
            "default_image",
            "tags",
        ]

    def clean(self):  # pylint: disable=too-many-locals,too-many-branches
        """Custom validation of the SoftwareImageLCMForm."""
        super().clean()
        device_types = self.cleaned_data.get("device_types")
        inventory_items = self.cleaned_data.get("inventory_items")
        object_tags = self.cleaned_data.get("object_tags")
        default_image = self.cleaned_data.get("default_image")
        software = self.cleaned_data.get("software")

        if software:
            software_images = SoftwareImageLCM.objects.filter(software=software)
            software_default_image = software_images.filter(default_image=True)
            if self.instance is not None and self.instance.pk is not None:
                software_images = software_images.filter(~Q(pk=self.instance.pk))
                software_default_image = software_default_image.filter(~Q(pk=self.instance.pk))

        if software and default_image and software_default_image.exists():
            msg = "Only one default Software Image is allowed for each Software."
            self.add_error("default_image", msg)

        assigned_objects_count = sum(obj.count() for obj in (device_types, inventory_items, object_tags))
        if default_image and assigned_objects_count > 0:
            msg = "Default image cannot be assigned to any objects."
            self.add_error("default_image", msg)
            if device_types.count() > 0:
                self.add_error("device_types", msg)
            if inventory_items.count() > 0:
                self.add_error("inventory_items", msg)
            if object_tags.count() > 0:
                self.add_error("object_tags", msg)

        if software and assigned_objects_count > 0:
            software_manufacturer = software.device_platform.manufacturer
            for device_type in device_types:
                if device_type.manufacturer != software_manufacturer:
                    msg = f"Manufacturer for {device_type.model} doesn't match the Software Platform Manufacturer."
                    self.add_error("device_types", msg)

                software_img_for_dt = software_images.filter(device_types__in=[device_type])
                if software_img_for_dt.exists():
                    msg = f"Device Type {device_type.model} already assigned to another Software Image."
                    self.add_error("device_types", msg)
                    self.add_error(None, msg)

            for object_tag in object_tags:
                software_img_for_tag = software_images.filter(object_tags__in=[object_tag])
                if software_img_for_tag.exists():
                    msg = f"Object Tag {object_tag.name} already assigned to another Software Image."
                    self.add_error("object_tags", msg)
                    self.add_error(None, msg)

            for inventory_item in inventory_items:
                software_img_for_invitem = software_images.filter(inventory_items__in=[inventory_item])
                if software_img_for_invitem.exists():
                    msg = f"Inventory Item {inventory_item.name} already assigned to another Software Image."
                    self.add_error("inventory_items", msg)
                    self.add_error(None, msg)


class SoftwareImageLCMFilterForm(NautobotFilterForm):
    """Filter form to filter searches for SoftwareImageLCM."""

    model = SoftwareImageLCM
    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search for image name or software version.",
    )
    software = DynamicModelMultipleChoiceField(required=False, queryset=SoftwareLCM.objects.all())
    image_file_name = forms.CharField(
        required=False,
        label="Image File name",
    )
    device_types = DynamicModelMultipleChoiceField(
        queryset=DeviceType.objects.all(),
        to_field_name="model",
        required=False,
    )
    inventory_items = DynamicModelMultipleChoiceField(
        queryset=InventoryItem.objects.all(),
        to_field_name="id",
        required=False,
    )
    object_tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        to_field_name="name",
        required=False,
    )
    hashing_algorithm = forms.CharField(
        required=False,
        label="Hashing Algorithm",
    )

    class Meta:
        """Meta attributes."""

        model = SoftwareImageLCM
        fields = [
            "q",
            "software",
            "image_file_name",
            "image_file_checksum",
            "hashing_algorithm",
            "download_url",
            "device_types",
            "inventory_items",
            "object_tags",
            "default_image",
        ]


class ValidatedSoftwareLCMForm(NautobotModelForm):
    """ValidatedSoftwareLCM creation/edit form."""

    software = DynamicModelChoiceField(queryset=SoftwareLCM.objects.all(), required=True)
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
        fields = [
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
        ]

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
        help_text="Search for start or end date of validity.",
    )
    software = DynamicModelChoiceField(required=False, queryset=SoftwareLCM.objects.all())
    devices = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
    )
    device_types = DynamicModelMultipleChoiceField(
        queryset=DeviceType.objects.all(),
        to_field_name="model",
        required=False,
    )
    device_roles = DynamicModelMultipleChoiceField(
        queryset=Role.objects.all(),
        query_params={"content_types": "dcim.device"},
        to_field_name="name",
        required=False,
    )
    inventory_items = DynamicModelMultipleChoiceField(
        queryset=InventoryItem.objects.all(),
        required=False,
    )
    object_tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
    )
    start_before = forms.DateField(label="Valid Since Date Before", required=False, widget=DatePicker())
    start_after = forms.DateField(label="Valid Since Date After", required=False, widget=DatePicker())

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


class DeviceSoftwareValidationResultFilterForm(NautobotFilterForm):
    """Filter form to filter searches for DeviceSoftwareValidationResult."""

    model = DeviceSoftwareValidationResult
    q = forms.CharField(
        required=False,
        label="Search",
    )
    software = DynamicModelMultipleChoiceField(
        queryset=SoftwareLCM.objects.all(),
        to_field_name="version",
        required=False,
    )
    platform = DynamicModelMultipleChoiceField(
        queryset=Platform.objects.all(),
        label="Platform",
        required=False,
    )
    valid = forms.BooleanField(
        required=False,
        widget=StaticSelect2(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label="Valid",
    )
    location = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        to_field_name="name",
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
        queryset=Role.objects.all(), query_params={"content_types": "dcim.device"}, to_field_name="name", required=False
    )
    exclude_sw_missing = forms.BooleanField(
        required=False,
        widget=StaticSelect2(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label="Exclude missing software",
    )
    sw_missing_only = forms.BooleanField(
        required=False,
        widget=StaticSelect2(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label="Show only missing software",
    )

    class Meta:
        """Meta attributes."""

        model = DeviceSoftwareValidationResult
        fields = [
            "q",
            "software",
            "valid",
            "platform",
            "location",
            "device",
            "device_type",
            "device_role",
            "exclude_sw_missing",
            "sw_missing_only",
        ]


class InventoryItemSoftwareValidationResultFilterForm(NautobotFilterForm):
    """Filter form to filter searches for InventoryItemSoftwareValidationResult."""

    model = InventoryItemSoftwareValidationResult
    q = forms.CharField(
        required=False,
        label="Search",
    )
    software = DynamicModelMultipleChoiceField(
        queryset=SoftwareLCM.objects.all(),
        to_field_name="version",
        required=False,
    )
    valid = forms.BooleanField(
        required=False,
        widget=StaticSelect2(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label="Valid",
    )
    manufacturer = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        label="Manufacturer",
        required=False,
    )
    location = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        to_field_name="name",
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
        queryset=Role.objects.all(), query_params={"content_types": "dcim.device"}, to_field_name="name", required=False
    )
    exclude_sw_missing = forms.BooleanField(
        required=False,
        widget=StaticSelect2(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label="Exclude missing software",
    )
    sw_missing_only = forms.BooleanField(
        required=False,
        widget=StaticSelect2(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label="Show only missing software",
    )

    class Meta:
        """Meta attributes."""

        model = InventoryItemSoftwareValidationResult
        fields = [
            "q",
            "software",
            "valid",
            "manufacturer",
            "location",
            "inventory_item",
            "part_id",
            "device",
            "device_type",
            "device_role",
            "exclude_sw_missing",
            "sw_missing_only",
        ]


class ContractLCMForm(NautobotModelForm):
    """Device Lifecycle Contracts creation/edit form."""

    provider = forms.ModelChoiceField(
        queryset=ProviderLCM.objects.all(),
        label="Vendor",
        to_field_name="pk",
        required=True,
    )
    contract_type = forms.ChoiceField(choices=add_blank_choice(ContractTypeChoices.CHOICES), label="Contract Type")
    currency = forms.ChoiceField(required=False, choices=add_blank_choice(CurrencyChoices.CHOICES))
    tags = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)
    devices = DynamicModelMultipleChoiceField(queryset=Device.objects.all(), required=False)

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
            "devices",
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


class ContractLCMBulkEditForm(NautobotBulkEditForm):
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


class ContractLCMFilterForm(NautobotFilterForm):
    """Filter form to filter searches."""

    model = ContractLCM
    q = forms.CharField(required=False, label="Search")
    provider = forms.ModelMultipleChoiceField(required=False, queryset=ProviderLCM.objects.all(), to_field_name="pk")
    currency = forms.MultipleChoiceField(
        required=False, choices=CurrencyChoices.CHOICES, widget=StaticSelect2Multiple()
    )
    contract_type = forms.ChoiceField(
        required=False, widget=StaticSelect2, choices=add_blank_choice(ContractTypeChoices.CHOICES)
    )
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
            "devices",
        ]

        widgets = {
            "start": DatePicker(),
            "end": DatePicker(),
        }


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


class ProviderLCMBulkEditForm(NautobotBulkEditForm):
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


class ProviderLCMFilterForm(NautobotFilterForm):
    """Filter form to filter searches."""

    model = ProviderLCM
    q = forms.CharField(required=False, label="Search")
    name = forms.CharField(required=False)
    country = forms.MultipleChoiceField(required=False, choices=CountryCodes.CHOICES, widget=StaticSelect2Multiple())

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


class ContactLCMForm(NautobotModelForm):
    """Device Lifecycle Contact Resources creation/edit form."""

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


class ContactLCMBulkEditForm(NautobotBulkEditForm):
    """Device Lifecycle Contact Resources bulk edit form."""

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


class ContactLCMFilterForm(NautobotFilterForm):
    """Filter form to filter searches."""

    model = ContactLCM
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


class CVELCMForm(NautobotModelForm):
    """CVE Lifecycle Management creation/edit form."""

    published_date = forms.DateField(widget=DatePicker())
    severity = forms.ChoiceField(choices=CVESeverityChoices.CHOICES, label="Severity", required=False)
    tags = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)
    affected_softwares = DynamicModelMultipleChoiceField(queryset=SoftwareLCM.objects.all(), required=False)

    class Meta:
        """Meta attributes for the CVELCMForm class."""

        model = CVELCM

        fields = [
            "name",
            "published_date",
            "link",
            "status",
            "description",
            "severity",
            "cvss",
            "cvss_v2",
            "cvss_v3",
            "fix",
            "affected_softwares",
            "comments",
            "tags",
        ]

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
    affected_softwares = forms.ModelMultipleChoiceField(queryset=SoftwareLCM.objects.all(), required=False)

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

        fields = [
            "status",
            "tags",
        ]


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
    software = DynamicModelMultipleChoiceField(required=False, queryset=SoftwareLCM.objects.all())
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

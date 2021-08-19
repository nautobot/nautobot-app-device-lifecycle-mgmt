"""Forms implementation for the LifeCycle Management plugin."""
import logging
from django import forms
from nautobot.utilities.forms import BootstrapMixin, DatePicker, DynamicModelMultipleChoiceField
from nautobot.dcim.models import Device, DeviceType, InventoryItem, Platform
from nautobot.extras.forms import CustomFieldModelCSVForm, CustomFieldModelForm, RelationshipModelForm
from nautobot.extras.models import Tag
from nautobot.utilities.forms import BulkEditForm, DynamicModelChoiceField, StaticSelect2, BOOLEAN_WITH_BLANK_CHOICES

from nautobot_device_lifecycle_mgmt.models import HardwareLCM, SoftwareLCM, ValidatedSoftwareLCM

logger = logging.getLogger("nautobot_device_lifecycle_mgmt")


class HardwareLCMForm(BootstrapMixin, forms.ModelForm):
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
            "end_of_support": DatePicker(),
            "end_of_security_patches": DatePicker(),
        }


class SoftwareLCMFilterForm(BootstrapMixin, forms.ModelForm):
    """Filter form to filter searches for SoftwareLCM."""

    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search for version, alias, or date for end_of_support or end_of_security_patches.",
    )
    version = forms.CharField(required=False)
    device_platform = forms.ModelMultipleChoiceField(
        required=False, queryset=Platform.objects.all(), to_field_name="slug"
    )

    class Meta:
        """Meta attributes."""

        model = SoftwareLCM
        fields = [
            "q",
            "version",
            "device_platform",
            "end_of_support",
            "end_of_security_patches",
            "documentation_url",
            "download_url",
            "image_file_name",
            "image_file_checksum",
            "long_term_support",
            "pre_release",
        ]

        widgets = {
            "end_of_support": DatePicker(),
            "end_of_security_patches": DatePicker(),
            "long_term_support": StaticSelect2(choices=BOOLEAN_WITH_BLANK_CHOICES),
            "pre_release": StaticSelect2(choices=BOOLEAN_WITH_BLANK_CHOICES),
        }


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

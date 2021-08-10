"""Forms for nautobot_plugin_device_lifecycle_mgmt."""

from django import forms


from nautobot.utilities.forms import BootstrapMixin, DatePicker
from nautobot.dcim.models import Device, DeviceType, InventoryItem, Platform
from nautobot.extras.forms import CustomFieldModelCSVForm, CustomFieldModelForm, RelationshipModelForm
from nautobot.utilities.forms import BulkEditForm, DynamicModelChoiceField, StaticSelect2, BOOLEAN_WITH_BLANK_CHOICES

from nautobot_plugin_device_lifecycle_mgmt.models import EoxNotice, SoftwareLCM, ValidatedSoftwareLCM


class EoxNoticeForm(BootstrapMixin, forms.ModelForm):
    """EoxNotice creation/edit form."""

    class Meta:
        """Meta attributes."""

        model = EoxNotice
        fields = EoxNotice.csv_headers

        widgets = {
            "end_of_sale": DatePicker(),
            "end_of_support": DatePicker(),
            "end_of_sw_releases": DatePicker(),
            "end_of_security_patches": DatePicker(),
        }


class EoxNoticeBulkEditForm(BootstrapMixin, BulkEditForm):
    """EoxNotice bulk edit form."""

    pk = forms.ModelMultipleChoiceField(queryset=EoxNotice.objects.all(), widget=forms.MultipleHiddenInput)
    end_of_sale = forms.DateField(widget=DatePicker(), required=False)
    end_of_support = forms.DateField(widget=DatePicker(), required=False)
    end_of_sw_releases = forms.DateField(widget=DatePicker(), required=False)
    end_of_security_patches = forms.DateField(widget=DatePicker(), required=False)
    notice_url = forms.URLField(required=False)

    class Meta:
        """Meta attributes."""

        nullable_fields = [
            "end_of_sale",
            "end_of_support",
            "end_of_sw_releases",
            "end_of_security_patches",
            "notice_url",
        ]


class EoxNoticeFilterForm(BootstrapMixin, forms.ModelForm):
    """Filter form to filter searches."""

    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Select a date that will be used to search end_of_support and end_of_sale",
    )
    device_type = forms.ModelMultipleChoiceField(
        required=False, queryset=DeviceType.objects.all(), to_field_name="slug"
    )
    devices = forms.ModelMultipleChoiceField(required=False, queryset=Device.objects.all(), to_field_name="name")

    class Meta:
        """Meta attributes."""

        model = EoxNotice
        # Define the fields above for ordering and widget purposes
        fields = [
            "q",
            "device_type",
            "end_of_sale",
            "end_of_support",
            "end_of_sw_releases",
            "end_of_security_patches",
            "notice_url",
        ]

        widgets = {
            "end_of_sale": DatePicker(),
            "end_of_support": DatePicker(),
            "end_of_sw_releases": DatePicker(),
            "end_of_security_patches": DatePicker(),
        }


class EoxNoticeCSVForm(CustomFieldModelCSVForm):
    """Form for creating bulk eox notices."""

    device_type = forms.ModelChoiceField(
        required=True, queryset=DeviceType.objects.all(), to_field_name="model", label="Device type"
    )

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        model = EoxNotice
        fields = EoxNotice.csv_headers


class SoftwareLCMForm(BootstrapMixin, forms.ModelForm):
    """SoftwareLCM creation/edit form."""

    class Meta:
        """Meta attributes."""

        model = SoftwareLCM
        fields = SoftwareLCM.csv_headers

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

    # assigned_to_type =
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

    class Meta:
        """Meta attributes."""

        model = ValidatedSoftwareLCM
        fields = (
            "softwarelcm",
            "assigned_to_device",
            "assigned_to_device_type",
            "assigned_to_inventory_item",
            "start",
            "end",
            "primary",
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
    start = forms.DateField(required=False, widget=DatePicker())
    end = forms.DateField(required=False, widget=DatePicker())
    primary = forms.BooleanField(required=False, widget=StaticSelect2(choices=BOOLEAN_WITH_BLANK_CHOICES))

    class Meta:
        """Meta attributes."""

        model = ValidatedSoftwareLCM
        fields = [
            "q",
            "softwarelcm",
            "start",
            "end",
            "primary",
        ]

"""Forms for eox_notices."""

from django import forms

from nautobot.utilities.forms import BootstrapMixin, DatePicker
from nautobot.dcim.models import Device, DeviceType
from nautobot.extras.forms import CustomFieldModelCSVForm
from nautobot.utilities.forms import BulkEditForm

from .models import EoxNotice


class EoxNoticeForm(BootstrapMixin, forms.ModelForm):
    """EoxNotice creation/edit form."""

    class Meta:
        """Meta attributes."""

        model = EoxNotice
        fields = [
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
            "devices",
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
        required=True, queryset=DeviceType.objects.all(), to_field_name="slug", label="Device type"
    )

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        model = EoxNotice
        fields = EoxNotice.csv_headers

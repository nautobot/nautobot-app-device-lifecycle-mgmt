"""Forms implementation for the LifeCycle Management plugin."""

from django import forms

from nautobot.utilities.forms import BootstrapMixin, DatePicker, add_blank_choice
from nautobot.dcim.models import DeviceType, InventoryItem
from nautobot.extras.forms import CustomFieldModelCSVForm
from nautobot.utilities.forms import BulkEditForm

from nautobot_plugin_device_lifecycle_mgmt.models import HardwareLCM


class HardwareLCMNoticeForm(BootstrapMixin, forms.ModelForm):
    """HardwareLCM creation/edit form."""

    inventory_item = forms.ChoiceField(
        choices=add_blank_choice(
            (i, i)
            for i in InventoryItem.objects.distinct("part_id").order_by("part_id").values_list("part_id", flat=True)
        ),
        label="Inventory Part ID",
        required=False,
    )

    class Meta:
        """Meta attributes for the HardwareLCMNoticeForm class."""

        model = HardwareLCM
        fields = HardwareLCM.csv_headers

        widgets = {
            "release_date": DatePicker(),
            "end_of_sale": DatePicker(),
            "end_of_support": DatePicker(),
            "end_of_sw_releases": DatePicker(),
            "end_of_security_patches": DatePicker(),
        }


class HardwareLCMNoticeBulkEditForm(BootstrapMixin, BulkEditForm):
    """HardwareLCMNotice bulk edit form."""

    pk = forms.ModelMultipleChoiceField(queryset=HardwareLCM.objects.all(), widget=forms.MultipleHiddenInput)
    release_date = forms.DateField(widget=DatePicker(), required=False)
    end_of_sale = forms.DateField(widget=DatePicker(), required=False)
    end_of_support = forms.DateField(widget=DatePicker(), required=False)
    end_of_sw_releases = forms.DateField(widget=DatePicker(), required=False)
    end_of_security_patches = forms.DateField(widget=DatePicker(), required=False)
    documentation_url = forms.URLField(required=False)
    comments = forms.CharField(required=False)

    class Meta:
        """Meta attributes for the HardwareLCMNoticeBulkEditForm class."""

        nullable_fields = [
            "release_date",
            "end_of_sale",
            "end_of_support",
            "end_of_sw_releases",
            "end_of_security_patches",
            "documentation_url",
            "comments",
        ]


class HardwareLCMNoticeFilterForm(BootstrapMixin, forms.ModelForm):
    """Filter form to filter searches."""

    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Select a date that will be used to search end_of_support and end_of_sale",
    )
    device_type = forms.ModelMultipleChoiceField(
        required=False, queryset=DeviceType.objects.all(), to_field_name="slug"
    )

    class Meta:
        """Meta attributes for the HardwareLCMNoticeFilterForm class."""

        model = HardwareLCM
        # Define the fields above for ordering and widget purposes
        fields = [
            "q",
            "device_type",
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


class HardwareLCMNoticeCSVForm(CustomFieldModelCSVForm):
    """Form for creating bulk eox notices."""

    device_type = forms.ModelChoiceField(
        required=True, queryset=DeviceType.objects.all(), to_field_name="model", label="Device type"
    )

    class Meta:
        """Meta attributes for the HardwareLCMNoticeCSVForm class."""

        model = HardwareLCM
        fields = HardwareLCM.csv_headers

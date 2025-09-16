"""Forms for nautobot_device_lifecycle_mgmt."""

from django import forms
from nautobot.apps.constants import CHARFIELD_MAX_LENGTH
from nautobot.apps.forms import NautobotBulkEditForm, NautobotFilterForm, NautobotModelForm, TagsBulkEditFormMixin

from nautobot_device_lifecycle_mgmt import models


class HardwareLCMForm(NautobotModelForm):  # pylint: disable=too-many-ancestors
    """HardwareLCM creation/edit form."""

    class Meta:
        """Meta attributes."""

        model = models.HardwareLCM
        fields = "__all__"


class HardwareLCMBulkEditForm(TagsBulkEditFormMixin, NautobotBulkEditForm):  # pylint: disable=too-many-ancestors
    """HardwareLCM bulk edit form."""

    pk = forms.ModelMultipleChoiceField(queryset=models.HardwareLCM.objects.all(), widget=forms.MultipleHiddenInput)
    description = forms.CharField(required=False, max_length=CHARFIELD_MAX_LENGTH)

    class Meta:
        """Meta attributes."""

        nullable_fields = [
            "description",
        ]


class HardwareLCMFilterForm(NautobotFilterForm):
    """Filter form to filter searches."""

    model = models.HardwareLCM
    field_order = ["q", "name"]

    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search within Name.",
    )
    name = forms.CharField(required=False, label="Name")

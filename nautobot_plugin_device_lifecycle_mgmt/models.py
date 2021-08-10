"""Django models for nautobot_plugin_device_lifecycle_mgmt plugin."""

from datetime import datetime

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from nautobot.extras.models.change_logging import ChangeLoggedModel
from nautobot.extras.utils import extras_features
from nautobot.core.models import BaseModel
from nautobot.core.models.generics import PrimaryModel
from nautobot.dcim.models import Device


class EoxNotice(BaseModel, ChangeLoggedModel):
    """EoxNotice model for plugin."""

    # Set model columns
    devices = models.ManyToManyField(Device)
    device_type = models.ForeignKey(to="dcim.DeviceType", on_delete=models.CASCADE, verbose_name="Device Type")
    end_of_sale = models.DateField(null=True, blank=True, verbose_name="End of Sale")
    end_of_support = models.DateField(null=True, blank=True, verbose_name="End of Support")
    end_of_sw_releases = models.DateField(null=True, blank=True, verbose_name="End of Software Releases")
    end_of_security_patches = models.DateField(null=True, blank=True, verbose_name="End of Security Patches")
    notice_url = models.URLField(blank=True, verbose_name="Notice URL")

    csv_headers = [
        "device_type",
        "end_of_sale",
        "end_of_support",
        "end_of_sw_releases",
        "end_of_security_patches",
        "notice_url",
    ]

    class Meta:
        """Meta attributes for DeviceLifeCycleEoX."""

        ordering = ("end_of_support", "end_of_sale")
        constraints = [models.UniqueConstraint(fields=["device_type"], name="unique_device_type")]

    def __str__(self):
        """String representation of DeviceLifeCycleEoXs."""
        if self.end_of_support:
            msg = f"{self.device_type} - End of support: {self.end_of_support}"
        else:
            msg = f"{self.device_type} - End of sale: {self.end_of_sale}"
        return msg

    def get_absolute_url(self):
        """Returns the Detail view for DeviceLifeCycleEoX models."""
        return reverse("plugins:nautobot_plugin_device_lifecycle_mgmt:eoxnotice", kwargs={"pk": self.pk})

    @property
    def expired(self):
        """Return True or False if chosen field is expired."""
        expired_field = settings.PLUGINS_CONFIG["nautobot_plugin_device_lifecycle_mgmt"].get(
            "expired_field", "end_of_support"
        )

        # If the chosen or default field does not exist, default to one of the required fields that are present
        if not getattr(self, expired_field) and not getattr(self, "end_of_support"):
            expired_field = "end_of_sale"
        elif not getattr(self, expired_field) and not getattr(self, "end_of_sale"):
            expired_field = "end_of_support"

        today = datetime.today().date()
        return today >= getattr(self, expired_field)

    def save(self, *args, **kwargs):
        """Override save to add devices to DeviceLifeCycleEoX found that match the device-type.

        Args:
            signal (bool): Whether the save is being called from a signal.
        """
        # Update the model with related devices that are of the specific device type
        if not kwargs.get("signal"):
            related_devices = Device.objects.filter(device_type=self.device_type)
            self.devices.add(*related_devices)

        # Attempt to pop signal if it exists before passing to super().save()
        kwargs.pop("signal", None)

        # Full clean to assert custom validation in clean() for ORM, etc.
        super().full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        """Override clean to do custom validation."""
        super().clean()

        if not self.end_of_sale and not self.end_of_support:
            raise ValidationError(_("End of Sale or End of Support must be specified."))

    def to_csv(self):
        """Return fields for bulk view."""
        return (
            self.devices,
            self.device_type,
            self.end_of_sale,
            self.end_of_support,
            self.end_of_sw_releases,
            self.end_of_security_patches,
            self.notice_url,
        )


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "relationships",
    "statuses",
    "webhooks",
)
class SoftwareLCM(PrimaryModel):
    """Software Life-Cycle Management model"""

    device_platform = models.ForeignKey(to="dcim.Platform", on_delete=models.CASCADE, verbose_name="Device Platform")
    version = models.CharField(max_length=50)
    alias = models.CharField(max_length=50, blank=True, null=True)
    end_of_support = models.DateField(null=True, blank=True, verbose_name="End of Software Support")
    end_of_security_patches = models.DateField(null=True, blank=True, verbose_name="End of Security Patches")
    documentation_url = models.URLField(blank=True, verbose_name="Documentation URL")
    download_url = models.URLField(blank=True, verbose_name="Download URL")
    image_file_name = models.CharField(null=True, blank=True, max_length=100, verbose_name="Image File Name")
    image_file_checksum = models.CharField(null=True, blank=True, max_length=256, verbose_name="Image File Checksum")
    long_term_support = models.BooleanField(verbose_name="Long Term Support")
    pre_release = models.BooleanField(verbose_name="Pre-Release")

    csv_headers = [
        "device_platform",
        "version",
        "alias",
        "end_of_support",
        "end_of_security_patches",
        "documentation_url",
        "download_url",
        "image_file_name",
        "image_file_checksum",
        "long_term_support",
        "pre_release",
    ]

    class Meta:
        """Meta attributes for SoftwareLCM."""

        verbose_name = "Software LCM"
        ordering = ("end_of_support", "end_of_security_patches")

    def __str__(self):
        """String representation of SoftwareLCM."""
        return f"{self.device_platform} - {self.version}"

    def get_absolute_url(self):
        """Returns the Detail view for SoftwareLCM models."""
        return reverse("plugins:nautobot_plugin_device_lifecycle_mgmt:softwarelcm", kwargs={"pk": self.pk})

    def to_csv(self):
        """Return fields for bulk view."""
        return (
            self.device_platform,
            self.version,
            self.alias,
            self.end_of_support,
            self.end_of_security_patches,
            self.documentation_url,
            self.download_url,
            self.image_file_name,
            self.image_file_checksum,
            self.long_term_support,
            self.pre_release,
        )


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "relationships",
    "statuses",
    "webhooks",
)
class ValidatedSoftwareLCM(PrimaryModel):
    """ValidatedSoftwareLCM model"""

    softwarelcm = models.ForeignKey(to="SoftwareLCM", on_delete=models.CASCADE, verbose_name="Related SoftwareLCM")
    assigned_to_content_type = models.ForeignKey(
        to=ContentType,
        limit_choices_to=Q(
            app_label="dcim",
            model__in=(
                "device",
                "device_type",
                "inventory_item",
            ),
        ),
        on_delete=models.PROTECT,
        related_name="+",
    )
    assigned_to_object_id = models.UUIDField()
    assigned_to = GenericForeignKey(ct_field="assigned_to_content_type", fk_field="assigned_to_object_id")
    start = models.DateField(verbose_name="Valid Since")
    end = models.DateField(verbose_name="Valid Until")
    primary = models.BooleanField(verbose_name="Primary Version")

    csv_headers = [
        "softwarelcm",
        "assigned_to_content_type",
        "assigned_to_object_id",
        "start",
        "end",
        "primary",
    ]

    class Meta:
        """Meta attributes for ValidatedSoftwareLCM."""

        verbose_name = "Validated SoftwareLCM"
        ordering = ("softwarelcm", "primary", "start")

    def __str__(self):
        """String representation of ValidatedSoftwareLCM."""
        msg = f"{self.softwarelcm} - Valid: {self.start} - {self.end}"
        return msg

    def get_absolute_url(self):
        """Returns the Detail view for ValidatedSoftwareLCM models."""
        return reverse("plugins:nautobot_plugin_device_lifecycle_mgmt:validatedsoftwarelcm", kwargs={"pk": self.pk})

    def to_csv(self):
        """Return fields for bulk view."""
        return (
            self.softwarelcm,
            self.assigned_to_content_type,
            self.assigned_to_object_id,
            self.start,
            self.end,
            self.primary,
        )

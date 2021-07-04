"""Django models for eox_notices plugin."""

from datetime import datetime

from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from nautobot.extras.models.change_logging import ChangeLoggedModel
from nautobot.core.models import BaseModel
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
        """Meta attributes for EoxNotice."""

        ordering = ("end_of_support", "end_of_sale")
        constraints = [models.UniqueConstraint(fields=["device_type"], name="unique_device_type")]

    def __str__(self):
        """String representation of EoxNotices."""
        if self.end_of_support:
            msg = f"{self.device_type} - End of support: {self.end_of_support}"
        else:
            msg = f"{self.device_type} - End of sale: {self.end_of_sale}"
        return msg

    def get_absolute_url(self):
        """Returns the Detail view for EoxNotice models."""
        return reverse("plugins:eox_notices:eoxnotice", kwargs={"pk": self.pk})

    @property
    def expired(self):
        """Return True or False if chosen field is expired."""
        expired_field = settings.PLUGINS_CONFIG["eox_notices"].get("expired_field", "end_of_support")

        # If the chosen or default field does not exist, default to one of the required fields that are present
        if not getattr(self, expired_field) and not getattr(self, "end_of_support"):
            expired_field = "end_of_sale"
        elif not getattr(self, expired_field) and not getattr(self, "end_of_sale"):
            expired_field = "end_of_support"

        today = datetime.today().date()
        return today >= getattr(self, expired_field)

    def save(self, *args, **kwargs):
        """Override save to add devices to EoxNotice found that match the device-type.

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

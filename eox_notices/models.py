"""Django models for eox_notices plugin."""

from django.db import models
from django.urls import reverse, resolve, Resolver404
from django.core.signals import request_started
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from nautobot.utilities.querysets import RestrictedQuerySet
from nautobot.extras.models import ChangeLoggedModel
from nautobot.core.models import BaseModel
from nautobot.dcim.models import Device


@receiver(request_started)
def add_devices_m2m_get_detail(sender, environ, **kwargs):
    """Used to add devices to eox notice.

    This will only happen when detail views get instantiated
    """
    # Obtain match info for path to determine if necessary actions need to be
    # taken to update the devices m2m relationship on the eox notice instance
    try:
        match = resolve(environ["PATH_INFO"])
    except Resolver404:
        return

    # Exit out of signal if not a detail GET of an eox notice
    if not environ["REQUEST_METHOD"] == "GET" or not match.url_name in ["eoxnotice", "eoxnotice-detail"]:
        return

    try:
        notice = EoxNotice.objects.get(pk=match.kwargs["pk"])
    except EoxNotice.DoesNotExist:
        return
    updated_devices = Device.objects.filter(device_type=notice.device_type)

    # Set vars to tell if devices exists
    notice_exists = notice.devices.exists()
    updated_exists = updated_devices.exists()

    existing_devices = set(notice.devices.all())
    new_devices = set(updated_devices)

    # If existing devices attached to notice are the same as fetch of devices, then no update required
    if not notice_exists and not updated_exists:
        return
    elif existing_devices == new_devices:
        return

    # If no devices existed previously, but do now, iterate and add new devices
    if not notice_exists and updated_exists:
        for device in updated_devices:
            notice.devices.add(device)
    # If both exist, compare and add/remove as needed
    elif notice_exists and updated_exists:
        add_devices = new_devices.difference(existing_devices)
        # Don't think I need delete as these are taken care of naturally
        # delete_devices = existing_devices.difference(new_devices)
        if add_devices:
            for dev in add_devices:
                notice.devices.add(dev)
        # if delete_devices:
        #     for dev in delete_devices:
        #         notice.devices.remove(dev)

    # Save the instance now that all updates have been completed
    notice.save(signal=True)


class EoxNotice(ChangeLoggedModel, BaseModel):
    # Assign permissions to model
    objects = RestrictedQuerySet.as_manager()

    # Set model columns
    devices = models.ManyToManyField(Device)
    device_type = models.ForeignKey(to="dcim.DeviceType", on_delete=models.CASCADE, verbose_name="Device Type")
    end_of_sale = models.DateField(null=True, blank=True, verbose_name="End of Sale")
    end_of_support = models.DateField(null=True, blank=True, verbose_name="End of Support")
    end_of_sw_releases = models.DateField(null=True, blank=True, verbose_name="End of Software Releases")
    end_of_security_patches = models.DateField(null=True, blank=True, verbose_name="End of Security Patches")
    notice_url = models.URLField(blank=True, verbose_name="Notice URL")

    class Meta:
        ordering = ("end_of_support", "end_of_sale")
        constraints = [models.UniqueConstraint(fields=["device_type"], name="unique_device_type")]

    def __str__(self):
        if self.end_of_support:
            msg = f"{self.device_type} - End of support: {self.end_of_support}"
        else:
            msg = f"{self.device_type} - End of sale: {self.end_of_sale}"
        return msg

    def get_absolute_url(self):
        return reverse("plugins:eox_notices:eoxnotice", kwargs={"pk": self.pk})

    def save(self, signal=False):
        # Update the model with related devices that are of the specific device type
        if not signal:
            related_devices = Device.objects.filter(device_type=self.device_type)
            for device in related_devices:
                self.devices.add(device)
        super().save()

    def clean(self):
        super().clean()

        if not self.end_of_sale and not self.end_of_support:
            raise ValidationError(_("End of Sale or End of Support must be specified."))

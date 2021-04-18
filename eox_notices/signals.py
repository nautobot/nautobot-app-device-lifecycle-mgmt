"""Custom signals for eox_notices."""

from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save

from nautobot.dcim.models import Device

from .models import EoxNotice


@receiver(post_save, sender=Device)
def add_new_device_to_notice(sender, instance, **kwargs):
    """Add/Remove Devices from EoXNotices when device is either updated or created."""
    # Attempt to obtain EoxNotice for the device's device type
    try:
        dt_notice = EoxNotice.objects.get(device_type=instance.device_type)
    except EoxNotice.DoesNotExist:
        return

    # If the device has been created go ahead and add it to the devices relationship on EoxNotice
    if kwargs["created"]:
        dt_notice.devices.add(instance)
        dt_notice.save(signal=True)


@receiver(pre_save, sender=Device)
def update_existing_device_to_notice(sender, instance, **kwargs):
    """Check to see if device_type has changed on device and update EoxNotice as necessary."""
    # If device does not exist yet, skip logic to update
    if instance.id is None:
        return

    # Attempt to fetch EoxNotice that the device is part of
    try:
        notice = EoxNotice.objects.get(devices=instance)
    except EoxNotice.DoesNotExist:
        notice = None

    if notice:
        # Do not do anything if device_type didn't change on device
        if notice.device_type == instance.device_type:
            return
        # Remove Device from the notice that it's device_type no longer matches
        notice.devices.remove(instance)
        notice.save(signal=True)

    # Attempt to fetch EoxNotice that device's device type is tied to
    try:
        dt_notice = EoxNotice.objects.get(device_type=instance.device_type)
    except EoxNotice.DoesNotExist:
        return

    # Add device to EoxNotice
    dt_notice.devices.add(instance)
    dt_notice.save(signal=True)

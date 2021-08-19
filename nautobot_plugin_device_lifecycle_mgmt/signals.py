"""Custom signals for nautobot_plugin_device_lifecycle_mgmt."""

from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save

from nautobot.dcim.models import Device
from nautobot.extras.choices import RelationshipTypeChoices

from nautobot_plugin_device_lifecycle_mgmt.models import EoxNotice


@receiver(post_save, sender=Device)
def add_new_device_to_notice(sender, instance, **kwargs):  # pylint: disable=unused-argument
    """Add/Remove Devices from EoxNotices when device is either updated or created."""
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
def update_existing_device_to_notice(sender, instance, **kwargs):  # pylint: disable=unused-argument
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


def post_migrate_create_relationships(sender, apps, **kwargs):  # pylint: disable=unused-argument
    """Callback function for post_migrate() -- create Relationship records."""
    # pylint: disable=invalid-name
    SoftwareLCM = sender.get_model("SoftwareLCM")
    ContentType = apps.get_model("contenttypes", "ContentType")
    _Device = apps.get_model("dcim", "Device")
    InventoryItem = apps.get_model("dcim", "InventoryItem")
    Relationship = apps.get_model("extras", "Relationship")

    for relationship_dict in [
        {
            "name": "Software on Device",
            "slug": "device_soft",
            "type": RelationshipTypeChoices.TYPE_ONE_TO_MANY,
            "source_type": ContentType.objects.get_for_model(SoftwareLCM),
            "source_label": "Running on Devices",
            "destination_type": ContentType.objects.get_for_model(_Device),
            "destination_label": "Software Version",
        },
        {
            "name": "Software on InventoryItem",
            "slug": "inventory_item_soft",
            "type": RelationshipTypeChoices.TYPE_ONE_TO_MANY,
            "source_type": ContentType.objects.get_for_model(SoftwareLCM),
            "source_label": "Running on Inventory Items",
            "destination_type": ContentType.objects.get_for_model(InventoryItem),
            "destination_label": "Software Version",
        },
    ]:
        Relationship.objects.get_or_create(name=relationship_dict["name"], defaults=relationship_dict)

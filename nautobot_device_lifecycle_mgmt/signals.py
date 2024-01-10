"""Custom signals for the Lifecycle Management app."""

from django.apps import apps as global_apps
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from nautobot.extras.choices import RelationshipTypeChoices
from nautobot.extras.models import Relationship, RelationshipAssociation


def post_migrate_create_relationships(sender, apps=global_apps, **kwargs):  # pylint: disable=unused-argument
    """Callback function for post_migrate() -- create Relationship records."""
    # pylint: disable=invalid-name
    SoftwareLCM = sender.get_model("SoftwareLCM")
    ContentType = apps.get_model("contenttypes", "ContentType")
    _Device = apps.get_model("dcim", "Device")
    InventoryItem = apps.get_model("dcim", "InventoryItem")
    _Relationship = apps.get_model("extras", "Relationship")

    contract_lcm = sender.get_model("ContractLCM")

    for relationship_dict in [
        {
            "label": "Software on Device",
            "key": "device_soft",
            "type": RelationshipTypeChoices.TYPE_ONE_TO_MANY,
            "source_type": ContentType.objects.get_for_model(SoftwareLCM),
            "source_label": "Running on Devices",
            "destination_type": ContentType.objects.get_for_model(_Device),
            "destination_label": "Software Version",
        },
        {
            "label": "Software on InventoryItem",
            "key": "inventory_item_soft",
            "type": RelationshipTypeChoices.TYPE_ONE_TO_MANY,
            "source_type": ContentType.objects.get_for_model(SoftwareLCM),
            "source_label": "Running on Inventory Items",
            "destination_type": ContentType.objects.get_for_model(InventoryItem),
            "destination_label": "Software Version",
        },
        {
            "label": "Contract to dcim.InventoryItem",
            "key": "contractlcm_to_inventoryitem",
            "type": RelationshipTypeChoices.TYPE_ONE_TO_MANY,
            "source_type": ContentType.objects.get_for_model(contract_lcm),
            "source_label": "Inventory Items",
            "destination_type": ContentType.objects.get_for_model(InventoryItem),
            "destination_label": "Contract",
        },
    ]:
        _Relationship.objects.get_or_create(label=relationship_dict["label"], defaults=relationship_dict)


@receiver(pre_delete, sender="nautobot_device_lifecycle_mgmt.SoftwareLCM")
def delete_softwarelcm_relationships(sender, instance, **kwargs):  # pylint: disable=unused-argument
    """Delete all SoftwareLCM relationships to Device and InventoryItem objects."""
    soft_relationships = Relationship.objects.filter(key__in=("device_soft", "inventory_item_soft"))
    RelationshipAssociation.objects.filter(relationship__in=soft_relationships, source_id=instance.pk).delete()


@receiver(pre_delete, sender="dcim.Device")
def delete_device_software_relationship(sender, instance, **kwargs):  # pylint: disable=unused-argument
    """Delete Device relationship to SoftwareLCM object."""
    soft_relationships = Relationship.objects.filter(key__in=("device_soft", "inventory_item_soft"))
    RelationshipAssociation.objects.filter(relationship__in=soft_relationships, destination_id=instance.pk).delete()


@receiver(pre_delete, sender="dcim.InventoryItem")
def delete_inventory_item_software_relationship(sender, instance, **kwargs):  # pylint: disable=unused-argument
    """Delete InventoryItem relationship to SoftwareLCM object."""
    soft_relationships = Relationship.objects.filter(key__in=("device_soft", "inventory_item_soft"))
    RelationshipAssociation.objects.filter(relationship__in=soft_relationships, destination_id=instance.pk).delete()

"""Custom signals for the Lifecycle Management app."""

from django.apps import apps as global_apps
from nautobot.extras.choices import RelationshipTypeChoices


def post_migrate_create_relationships(sender, apps=global_apps, **kwargs):  # pylint: disable=unused-argument
    """Callback function for post_migrate() -- create Relationship records."""
    # pylint: disable=invalid-name
    ContentType = apps.get_model("contenttypes", "ContentType")
    InventoryItem = apps.get_model("dcim", "InventoryItem")
    Relationship = apps.get_model("extras", "Relationship")

    ContractLCM = sender.get_model("ContractLCM")

    Relationship.objects.get_or_create(
        label="Contract to dcim.InventoryItem",
        defaults={
            "key": "contractlcm_to_inventoryitem",
            "type": RelationshipTypeChoices.TYPE_ONE_TO_MANY,
            "source_type": ContentType.objects.get_for_model(ContractLCM),
            "source_label": "Inventory Items",
            "destination_type": ContentType.objects.get_for_model(InventoryItem),
            "destination_label": "Contract",
        },
    )

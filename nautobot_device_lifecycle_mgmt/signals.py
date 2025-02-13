"""Custom signals for the Lifecycle Management app."""

from django.apps import apps as global_apps
from nautobot.extras.choices import RelationshipTypeChoices


def post_migrate_create_relationships(sender, apps=global_apps, **kwargs):  # pylint: disable=unused-argument
    """Callback function for post_migrate() -- create Relationship records."""
    # pylint: disable=invalid-name
    ContactAssociation = apps.get_model("extras", "ContactAssociation")
    ContentType = apps.get_model("contenttypes", "ContentType")
    InventoryItem = apps.get_model("dcim", "InventoryItem")
    Relationship = apps.get_model("extras", "Relationship")
    Role = apps.get_model("extras", "Role")

    ContractLCM = sender.get_model("ContractLCM")

    # Hide obsolete device_soft and inventory_item_soft relationships
    Relationship.objects.filter(key__in=("device_soft", "inventory_item_soft")).update(
        destination_hidden=True, source_hidden=True
    )

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

    # Migrate old contact choices to ipam roles
    contact_roles = ("DLM Primary", "DLM Tier 1", "DLM Tier 2", "DLM Tier 3", "DLM Owner", "DLM Unassigned")
    contact_association_ct = ContentType.objects.get_for_model(ContactAssociation)
    for contact_role in contact_roles:
        role, _ = Role.objects.get_or_create(name=contact_role)
        role.content_types.add(contact_association_ct)

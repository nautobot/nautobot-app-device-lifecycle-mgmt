"""Custom signals for the Lifecycle Management app."""

from django.apps import apps as global_apps
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from nautobot.extras.choices import RelationshipTypeChoices
from nautobot.extras.models import ExternalIntegration, Secret, SecretsGroup


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


@receiver(post_migrate)
def create_nist_objects(sender, apps=global_apps, **kwargs):  # pylint: disable=unused-argument
    """Create default objects after database migrations."""
    # Only run this for our app
    if sender.name != "nautobot_device_lifecycle_mgmt":
        return
    # Ensure a Secret exists for the NAUTOBOT_DLM_NIST_API_KEY
    nist_api_key, _ = Secret.objects.get_or_create(
        name="NAUTOBOT DLM NIST API KEY",
        defaults={
            "provider": "environment-variable",
            "description": "API key for NIST CVE Database",
            "parameters": {
                "variable": "NAUTOBOT_DLM_NIST_API_KEY",
            },
        },
    )

    # Ensure a SecretsGroup exists and is using the NAUTOBOT_DLM_NIST_API_KEY Secret
    nist_secrets_group, _ = SecretsGroup.objects.get_or_create(
        name="NAUTOBOT DLM NIST SECRETS GROUP",
        defaults={
            "description": "Secrets group for NIST API integration",
        },
    )

    # Add secret with specific access type and secret type
    nist_secrets_group.secrets.add(
        nist_api_key,
        through_defaults={
            "access_type": "HTTP_HEADER",
            "secret_type": "apiKey",  # Match the NIST expected header key
        },
    )

    # Ensure an ExternalIntegration exists for NIST API Integration
    ExternalIntegration.objects.get_or_create(
        name="NAUTOBOT DLM NIST EXTERNAL INTEGRATION",  # Required
        defaults={
            "remote_url": "https://services.nvd.nist.gov/rest/json/cves/2.0",
            "http_method": "GET",
            "secrets_group": nist_secrets_group,
            "verify_ssl": True,
            "timeout": 60,
            "headers": {"Content-Type": "application/json"},
            "extra_config": {
                "api_call_delay": 6,
                "retries": {
                    "max_attempts": 3,
                    "backoff": 2,
                },
            },
        },
    )

import uuid

from django.db import migrations

from nautobot.apps.choices import (
    ObjectChangeActionChoices,
    ObjectChangeEventContextChoices,
)
from nautobot.apps.models import serialize_object, serialize_object_v2, TagsManager
from nautobot.apps.utils import migrate_content_type_references_to_new_model
from nautobot.extras import models as extras_models
from nautobot.extras.constants import CHANGELOG_MAX_OBJECT_REPR

common_objectchange_request_id = uuid.uuid4()


def migrate_dlm_contact_model_to_core(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    DLMContact = apps.get_model("nautobot_device_lifecycle_mgmt", "ContactLCM")
    CoreContact = apps.get_model("extras", "Contact")

    dlm_contact_ct = ContentType.objects.get_for_model(DLMContact)
    core_contact_ct = ContentType.objects.get_for_model(CoreContact)

    # Migrate content types for all related extras models
    migrate_content_type_references_to_new_model(apps, dlm_contact_ct, core_contact_ct)

    for dlm_contact in DLMContact.objects.all():
        _migrate_contact(apps, dlm_contact)

    # Delete DLM ContactLCM instance
    DLMContact.objects.all().delete()


def _migrate_contact(apps, dlm_contact):
    ContentType = apps.get_model("contenttypes", "ContentType")
    DLMContact = apps.get_model("nautobot_device_lifecycle_mgmt", "ContactLCM")
    DLMContract = apps.get_model("nautobot_device_lifecycle_mgmt", "ContractLCM")
    CoreContact = apps.get_model("extras", "Contact")
    ContactAssociation = apps.get_model("extras", "ContactAssociation")
    Role = apps.get_model("extras", "Role")
    ObjectChange = apps.get_model("extras", "ObjectChange")
    Status = apps.get_model("extras", "Status")

    dlm_contact_ct = ContentType.objects.get_for_model(DLMContact)
    dlm_contract_ct = ContentType.objects.get_for_model(DLMContract)
    core_contact_ct = ContentType.objects.get_for_model(CoreContact)
    contact_association_ct = ContentType.objects.get_for_model(ContactAssociation)

    status_active = Status.objects.get(name="Active")

    core_contact = CoreContact(
        id=dlm_contact.id,
        name=dlm_contact.name,
        address=dlm_contact.address,
        phone=dlm_contact.phone,
        email=dlm_contact.email,
        comments=dlm_contact.comments,
        _custom_field_data=dlm_contact._custom_field_data,
    )
    core_contact.save()

    ca_role, _ = Role.objects.get_or_create(name=dlm_contact.type)
    ca_role.content_types.add(contact_association_ct)
    contact_association = ContactAssociation(
        contact=core_contact,
        associated_object_id=dlm_contact.contract.id,
        associated_object_type=dlm_contract_ct,
        role=ca_role,
        status=status_active,
    )
    contact_association.save()

    # Work around created field's auto_now_add behavior
    CoreContact.objects.filter(id=core_contact.id).update(created=dlm_contact.created)
    core_contact.refresh_from_db()

    # make tag manager available in migration for nautobot.core.models.utils.serialize_object
    # https://github.com/jazzband/django-taggit/issues/101
    # https://github.com/jazzband/django-taggit/issues/454
    core_contact.tags = TagsManager(
        through=extras_models.TaggedItem,
        model=CoreContact,
        instance=core_contact,
        prefetch_cache_name="tags",
    )

    def contact_repr(contact):
        result = contact.name
        if contact.phone:
            result += f" ({contact.phone})"
        if contact.email:
            result += f" ({contact.email})"
        return result

    # Create an object change to document migration
    ObjectChange.objects.create(
        action=ObjectChangeActionChoices.ACTION_UPDATE,
        change_context=ObjectChangeEventContextChoices.CONTEXT_ORM,
        change_context_detail="Migrated from Nautobot App Device Lifecycle Management",
        changed_object_id=core_contact.id,
        changed_object_type=core_contact_ct,
        object_data=serialize_object(core_contact),
        object_data_v2=serialize_object_v2(core_contact),
        object_repr=contact_repr(core_contact)[:CHANGELOG_MAX_OBJECT_REPR],
        related_object_id=dlm_contact.id,
        related_object_type=dlm_contact_ct,
        request_id=common_objectchange_request_id,
        user=None,
        user_name="Undefined",
    )


class Migration(migrations.Migration):
    dependencies = [
        ("extras", "0104_contact_contactassociation_team"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("extras", "0057_jobbutton"),
        ("nautobot_device_lifecycle_mgmt", "0021_migrate_to_core_software_models"),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(migrate_dlm_contact_model_to_core, migrations.RunPython.noop),
    ]

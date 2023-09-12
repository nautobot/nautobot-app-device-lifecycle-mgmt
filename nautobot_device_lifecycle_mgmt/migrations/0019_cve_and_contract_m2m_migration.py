from django.db import migrations


def migrate_cve_affected_software(apps, schema_editor):
    """
    Migrate CVE affected software from custom relationship to m2m field on CVELCM model.
    """
    Relationship = apps.get_model("extras", "Relationship")
    RelationshipAssociation = apps.get_model("extras", "RelationshipAssociation")
    CVELCM = apps.get_model("nautobot_device_lifecycle_mgmt", "CVELCM")
    SoftwareLCM = apps.get_model("nautobot_device_lifecycle_mgmt", "SoftwareLCM")

    try:
        soft_cve_relationship = Relationship.objects.get(key="soft_cve")
    except Relationship.DoesNotExist:
        pass
        return

    soft_cve_relationship_associations = RelationshipAssociation.objects.filter(
        relationship_id=soft_cve_relationship.id
    )

    for relationship_association in soft_cve_relationship_associations:
        cve = CVELCM.objects.get(id=relationship_association.destination_id)
        software = SoftwareLCM.objects.get(id=relationship_association.source_id)
        cve.affected_softwares.add(software)
        cve.save()

    soft_cve_relationship.delete()


def migrate_contract_devices(apps, schema_editor):
    """
    Migrate devices linked to contract from custom relationship to m2m field on ContractLCM model.
    """
    Device = apps.get_model("dcim", "Device")
    Relationship = apps.get_model("extras", "Relationship")
    RelationshipAssociation = apps.get_model("extras", "RelationshipAssociation")
    ContractLCM = apps.get_model("nautobot_device_lifecycle_mgmt", "ContractLCM")

    try:
        contract_devices_relationship = Relationship.objects.get(key="contractlcm-to-device")
    except Relationship.DoesNotExist:
        pass
        return

    contract_devices_relationship_associations = RelationshipAssociation.objects.filter(
        relationship_id=contract_devices_relationship.id
    )

    for contract_devices_relationship_association in contract_devices_relationship_associations:
        contract = ContractLCM.objects.get(id=contract_devices_relationship_association.source_id)
        device = Device.objects.get(id=contract_devices_relationship_association.destination_id)
        contract.devices.add(device)
        contract.save()

    contract_devices_relationship.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("nautobot_device_lifecycle_mgmt", "0018_cve_and_contract_cust_rels_to_m2m"),
    ]

    operations = [
        migrations.RunPython(migrate_cve_affected_software),
        migrations.RunPython(migrate_contract_devices),
    ]

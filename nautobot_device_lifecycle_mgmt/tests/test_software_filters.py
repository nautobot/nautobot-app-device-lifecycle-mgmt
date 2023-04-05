"""nautobot_device_lifecycle_mgmt test class for software queryset filters."""
from django.test import TestCase

from nautobot.dcim.models import Device, DeviceRole, DeviceType, InventoryItem, Manufacturer, Platform, Site
from nautobot.extras.models import Relationship, RelationshipAssociation, Tag

from nautobot_device_lifecycle_mgmt.models import (
    SoftwareLCM,
    SoftwareImageLCM,
)

from nautobot_device_lifecycle_mgmt.software_filters import DeviceSoftwareImageFilter, InventoryItemSoftwareImageFilter


class DeviceSoftwareImageFilterTestCase(TestCase):  # pylint: disable=too-many-instance-attributes
    """Tests for DeviceSoftwareImageFilter."""

    def setUp(self):
        manufacturer_arista, _ = Manufacturer.objects.get_or_create(name="Arista", slug="arista")
        device_platform_arista, _ = Platform.objects.get_or_create(
            name="Arista EOS", slug="arista_eos", manufacturer=manufacturer_arista
        )

        self.software = SoftwareLCM.objects.create(
            device_platform=device_platform_arista,
            version="4.25M",
            release_date="2021-01-10",
        )

        self.devicetype_1, _ = DeviceType.objects.get_or_create(
            manufacturer=manufacturer_arista, model="7124", slug="7124"
        )
        self.devicetype_2, _ = DeviceType.objects.get_or_create(
            manufacturer=manufacturer_arista, model="7150S", slug="7150s"
        )
        self.devicetype_3, _ = DeviceType.objects.get_or_create(
            manufacturer=manufacturer_arista, model="7500", slug="7500"
        )
        devicerole = DeviceRole.objects.create(name="Switch", slug="switch", color="ff0000")
        site = Site.objects.create(name="Site1", slug="site1")
        self.tag_1, _ = Tag.objects.get_or_create(name="lcm", slug="lcm")
        self.tag_2, _ = Tag.objects.get_or_create(name="lcm2", slug="lcm2")
        device_soft_rel = Relationship.objects.get(slug="device_soft")

        self.device_1 = Device(
            name="Device1",
            device_type=self.devicetype_1,
            device_role=devicerole,
            site=site,
        )
        self.device_1.tags.add(self.tag_1)
        self.device_1.save()
        RelationshipAssociation.objects.create(
            source=self.software,
            destination=self.device_1,
            relationship=device_soft_rel,
        )

        self.device_2 = Device(
            name="Device2",
            device_type=self.devicetype_2,
            device_role=devicerole,
            site=site,
        )
        self.device_2.save()
        RelationshipAssociation.objects.create(
            source=self.software,
            destination=self.device_2,
            relationship=device_soft_rel,
        )

        self.device_3 = Device(
            name="Device3",
            device_type=self.devicetype_1,
            device_role=devicerole,
            site=site,
        )
        self.device_3.save()
        RelationshipAssociation.objects.create(
            source=self.software,
            destination=self.device_3,
            relationship=device_soft_rel,
        )

        self.device_4 = Device(
            name="Device4",
            device_type=self.devicetype_3,
            device_role=devicerole,
            site=site,
        )
        self.device_4.tags.add(self.tag_2)
        self.device_4.save()
        RelationshipAssociation.objects.create(
            source=self.software,
            destination=self.device_4,
            relationship=device_soft_rel,
        )

        self.soft_image_ot = SoftwareImageLCM(
            image_file_name="eos4.25ot.swi",
            software=self.software,
            default_image=False,
        )
        self.soft_image_ot.object_tags.set([self.tag_1.pk])
        self.soft_image_ot.save()

        self.soft_image_dt = SoftwareImageLCM(
            image_file_name="eos4.25dt.swi",
            software=self.software,
            default_image=False,
        )
        self.soft_image_dt.device_types.set([self.devicetype_2.pk])
        self.soft_image_dt.save()

        self.soft_image_def = SoftwareImageLCM(
            image_file_name="eos4.25def.swi",
            software=self.software,
            default_image=True,
        )
        self.soft_image_def.save()

        self.soft_image_ot_win = SoftwareImageLCM(
            image_file_name="eos4.25ot_win.swi",
            software=self.software,
            default_image=False,
        )
        self.soft_image_ot_win.object_tags.set([self.tag_2.pk])
        self.soft_image_ot_win.save()

        self.soft_image_dt_lose = SoftwareImageLCM(
            image_file_name="eos4.25dt_lose.swi",
            software=self.software,
            default_image=False,
        )
        self.soft_image_dt_lose.device_types.set([self.devicetype_3.pk])
        self.soft_image_dt_lose.save()

    def test_soft_image_for_device_match_tag(self):
        software_image_qs = SoftwareImageLCM.objects.all()
        soft_image_filtered_qs = DeviceSoftwareImageFilter(software_image_qs, self.device_1).filter_qs()

        self.assertEqual(soft_image_filtered_qs.count(), 1)
        self.assertEqual(soft_image_filtered_qs[0], self.soft_image_ot)

    def test_soft_image_for_device_match_device_type(self):
        software_image_qs = SoftwareImageLCM.objects.all()
        soft_image_filtered_qs = DeviceSoftwareImageFilter(software_image_qs, self.device_2).filter_qs()

        self.assertEqual(soft_image_filtered_qs.count(), 1)
        self.assertEqual(soft_image_filtered_qs[0], self.soft_image_dt)

    def test_soft_image_for_device_match_default(self):
        software_image_qs = SoftwareImageLCM.objects.all()
        soft_image_filtered_qs = DeviceSoftwareImageFilter(software_image_qs, self.device_3).filter_qs()

        self.assertEqual(soft_image_filtered_qs.count(), 1)
        self.assertEqual(soft_image_filtered_qs[0], self.soft_image_def)

    def test_soft_image_for_device_tag_wins_over_device_type(self):
        software_image_qs = SoftwareImageLCM.objects.all()
        soft_image_filtered_qs = DeviceSoftwareImageFilter(software_image_qs, self.device_4).filter_qs()

        self.assertEqual(soft_image_filtered_qs.count(), 1)
        self.assertEqual(soft_image_filtered_qs[0], self.soft_image_ot_win)


class InventoryItemSoftwareImageFilterTestCase(TestCase):  # pylint: disable=too-many-instance-attributes
    """Tests for InventoryItemSoftwareImageFilter."""

    def setUp(self):
        manufacturer_arista, _ = Manufacturer.objects.get_or_create(name="Arista", slug="arista")
        device_platform_arista, _ = Platform.objects.get_or_create(
            name="Arista EOS", slug="arista_eos", manufacturer=manufacturer_arista
        )

        self.software = SoftwareLCM.objects.create(
            device_platform=device_platform_arista,
            version="4.25M",
            release_date="2021-01-10",
        )

        self.devicetype_1, _ = DeviceType.objects.get_or_create(
            manufacturer=manufacturer_arista, model="7124", slug="7124"
        )
        devicerole = DeviceRole.objects.create(name="Switch", slug="switch", color="ff0000")
        site = Site.objects.create(name="Site1", slug="site1")
        self.tag_1, _ = Tag.objects.get_or_create(name="lcm", slug="lcm")
        self.tag_2, _ = Tag.objects.get_or_create(name="lcm2", slug="lcm2")
        invitem_soft_rel = Relationship.objects.get(slug="inventory_item_soft")

        self.device_1 = Device.objects.create(
            name="Device1",
            device_type=self.devicetype_1,
            device_role=devicerole,
            site=site,
        )

        self.inventoryitem_1 = InventoryItem.objects.create(device=self.device_1, name="SwitchModule1")
        self.inventoryitem_1.tags.add(self.tag_1)
        self.inventoryitem_1.save()
        RelationshipAssociation.objects.create(
            source=self.software,
            destination=self.inventoryitem_1,
            relationship=invitem_soft_rel,
        )

        self.inventoryitem_2 = InventoryItem.objects.create(device=self.device_1, name="SwitchModule2")
        RelationshipAssociation.objects.create(
            source=self.software,
            destination=self.inventoryitem_2,
            relationship=invitem_soft_rel,
        )

        self.inventoryitem_3 = InventoryItem.objects.create(device=self.device_1, name="SwitchModule3")
        RelationshipAssociation.objects.create(
            source=self.software,
            destination=self.inventoryitem_3,
            relationship=invitem_soft_rel,
        )

        self.inventoryitem_4 = InventoryItem.objects.create(device=self.device_1, name="SwitchModule4")
        self.inventoryitem_4.tags.add(self.tag_2)
        self.inventoryitem_4.save()
        RelationshipAssociation.objects.create(
            source=self.software,
            destination=self.inventoryitem_4,
            relationship=invitem_soft_rel,
        )

        self.soft_image_ot = SoftwareImageLCM(
            image_file_name="eos4.25ot.swi",
            software=self.software,
            default_image=False,
        )
        self.soft_image_ot.object_tags.set([self.tag_1.pk])
        self.soft_image_ot.save()

        self.soft_image_invitem = SoftwareImageLCM(
            image_file_name="eos4.25invitem.swi",
            software=self.software,
            default_image=False,
        )
        self.soft_image_invitem.inventory_items.set([self.inventoryitem_2.pk])
        self.soft_image_invitem.save()

        self.soft_image_def = SoftwareImageLCM(
            image_file_name="eos4.25def.swi",
            software=self.software,
            default_image=True,
        )
        self.soft_image_def.save()

        self.soft_image_ot_win = SoftwareImageLCM(
            image_file_name="eos4.25ot_win.swi",
            software=self.software,
            default_image=False,
        )
        self.soft_image_ot_win.object_tags.set([self.tag_2.pk])
        self.soft_image_ot_win.save()

        self.soft_image_spec_assgmt_lose = SoftwareImageLCM(
            image_file_name="eos4.25dt_lose.swi",
            software=self.software,
            default_image=False,
        )
        self.soft_image_spec_assgmt_lose.inventory_items.set([self.inventoryitem_4.pk])
        self.soft_image_spec_assgmt_lose.save()

    def test_soft_image_for_invitem_match_tag(self):
        software_image_qs = SoftwareImageLCM.objects.all()
        soft_image_filtered_qs = InventoryItemSoftwareImageFilter(software_image_qs, self.inventoryitem_1).filter_qs()

        self.assertEqual(soft_image_filtered_qs.count(), 1)
        self.assertEqual(soft_image_filtered_qs[0], self.soft_image_ot)

    def test_soft_image_for_invitem_match_invitem(self):
        software_image_qs = SoftwareImageLCM.objects.all()
        soft_image_filtered_qs = InventoryItemSoftwareImageFilter(software_image_qs, self.inventoryitem_2).filter_qs()

        self.assertEqual(soft_image_filtered_qs.count(), 1)
        self.assertEqual(soft_image_filtered_qs[0], self.soft_image_invitem)

    def test_soft_image_for_invitem_match_default(self):
        software_image_qs = SoftwareImageLCM.objects.all()
        soft_image_filterd_qs = InventoryItemSoftwareImageFilter(software_image_qs, self.inventoryitem_3).filter_qs()

        self.assertEqual(soft_image_filterd_qs.count(), 1)
        self.assertEqual(soft_image_filterd_qs[0], self.soft_image_def)

    def test_soft_image_for_invitem_match_tag_wins_over_specific_assignment(self):
        software_image_qs = SoftwareImageLCM.objects.all()
        soft_image_filterd_qs = InventoryItemSoftwareImageFilter(software_image_qs, self.inventoryitem_4).filter_qs()

        self.assertEqual(soft_image_filterd_qs.count(), 1)
        self.assertEqual(soft_image_filterd_qs[0], self.soft_image_ot_win)

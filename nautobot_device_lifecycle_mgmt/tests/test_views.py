"""Unit tests for views."""
import datetime

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from nautobot.dcim.models import Device, DeviceType, InventoryItem, Manufacturer
from nautobot.extras.models import Relationship, RelationshipAssociation, Status
from nautobot.users.models import ObjectPermission
from nautobot.utilities.testing import TestCase, ViewTestCases

from nautobot_device_lifecycle_mgmt.models import (
    CVELCM,
    ContractLCM,
    DeviceSoftwareValidationResult,
    HardwareLCM,
    InventoryItemSoftwareValidationResult,
    ProviderLCM,
    SoftwareImageLCM,
    VulnerabilityLCM,
)

from .conftest import create_cves, create_devices, create_inventory_items, create_softwares

User = get_user_model()


class HardwareLCMViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    """Test the HardwareLCM views."""

    model = HardwareLCM
    bulk_edit_data = {"documentation_url": "https://cisco.com/eox"}

    def _get_base_url(self):
        return "plugins:{}:{}_{{}}".format(  # pylint: disable=consider-using-f-string
            self.model._meta.app_label, self.model._meta.model_name
        )

    @classmethod
    def setUpTestData(cls):
        """Create a superuser and token for API calls."""
        manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        device_types = tuple(
            DeviceType.objects.create(model=model, slug=model, manufacturer=manufacturer)
            for model in ["c9300-24", "c9300-48", "c9500-24", "c9500-48", "c9200-24", "c9200-48"]
        )

        HardwareLCM.objects.create(device_type=device_types[0], end_of_sale=datetime.date(2021, 4, 1))
        HardwareLCM.objects.create(device_type=device_types[1], end_of_sale=datetime.date(2021, 4, 1))
        HardwareLCM.objects.create(device_type=device_types[2], end_of_sale=datetime.date(2021, 4, 1))

        cls.form_data = {
            "device_type": device_types[3].id,
            "end_of_sale": datetime.date(2021, 4, 1),
            "end_of_support": datetime.date(2024, 4, 1),
        }
        cls.csv_data = (
            "device_type,end_of_sale,end_of_support,end_of_sw_releases,end_of_security_patches,documentation_url",
            "c9500-48, 2021-10-06, 2022-10-06, 2025-10-06, 2026-10-06, https://cisco.com/eox",
            "c9200-24, 2022-10-06, 2023-10-06, 2025-10-06, 2026-10-06, https://cisco.com/eox",
            "c9200-48, 2023-10-06, 2024-10-06, 2025-10-06, 2026-10-06, https://cisco.com/eox",
        )

    def test_has_advanced_tab(self):
        pass

    def test_get_object_notes(self):
        pass

    def test_list_objects_with_permission(self):
        pass


class ValidatedSoftwareDeviceReportViewTest(ViewTestCases.ListObjectsViewTestCase):
    """Test ValidatedSoftwareDeviceReportView"""

    model = DeviceSoftwareValidationResult

    def _get_base_url(self):
        return "plugins:nautobot_device_lifecycle_mgmt:validatedsoftware_device_report"

    @classmethod
    def setUpTestData(cls):
        """Set up test objects."""
        device_1, device_2, _ = create_devices()
        DeviceSoftwareValidationResult.objects.create(
            device=device_1,
            software=None,
            is_validated=False,
        )
        DeviceSoftwareValidationResult.objects.create(
            device=device_2,
            software=None,
            is_validated=False,
        )

    def test_validation_report_view_without_permission(self):
        """Test the SoftwareReportOverview."""

        self.assertHttpStatus(
            self.client.get(
                reverse(
                    "plugins:nautobot_device_lifecycle_mgmt:validatedsoftware_device_report",
                )
            ),
            403,
        )

    def test_validation_report_view_with_permission(self):
        """Test the SoftwareReportOverview."""
        obj_perm = ObjectPermission(name="Test permission", actions=["view"])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))
        self.assertHttpStatus(
            self.client.get(
                reverse(
                    "plugins:nautobot_device_lifecycle_mgmt:validatedsoftware_device_report",
                )
            ),
            200,
        )

    def test_get_object_notes(self):
        pass

    def test_list_objects_unknown_filter_no_strict_filtering(self):
        pass

    def test_list_objects_with_permission(self):
        pass

    # Disable Temp until we get headers fixed for csv
    def test_queryset_to_csv(self):
        pass


class ValidatedSoftwareInventoryItemReportViewTest(ViewTestCases.ListObjectsViewTestCase):
    """Test ValidatedSoftwareInventoryItemReportView"""

    model = InventoryItemSoftwareValidationResult

    def _get_base_url(self):
        return "plugins:nautobot_device_lifecycle_mgmt:validatedsoftware_inventoryitem_report"

    @classmethod
    def setUpTestData(cls):
        """Set up test objects."""
        inventory_items = create_inventory_items()
        InventoryItemSoftwareValidationResult.objects.create(
            inventory_item=inventory_items[0],
            software=None,
            is_validated=False,
        )
        InventoryItemSoftwareValidationResult.objects.create(
            inventory_item=inventory_items[1],
            software=None,
            is_validated=False,
        )
        InventoryItemSoftwareValidationResult.objects.create(
            inventory_item=inventory_items[2],
            software=None,
            is_validated=False,
        )

    def test_validation_report_view_without_permission(self):
        """Test the SoftwareReportOverview."""

        self.assertHttpStatus(
            self.client.get(
                reverse(
                    "plugins:nautobot_device_lifecycle_mgmt:validatedsoftware_inventoryitem_report",
                )
            ),
            403,
        )

    def test_validation_report_view_with_permission(self):
        """Test the SoftwareReportOverview."""
        obj_perm = ObjectPermission(name="Test permission", actions=["view"])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))
        self.assertHttpStatus(
            self.client.get(
                reverse(
                    "plugins:nautobot_device_lifecycle_mgmt:validatedsoftware_inventoryitem_report",
                )
            ),
            200,
        )

    def test_get_object_notes(self):
        pass

    def test_list_objects_unknown_filter_no_strict_filtering(self):
        pass

    def test_list_objects_with_permission(self):
        pass

    # Disable Temp until we get headers fixed for csv
    def test_queryset_to_csv(self):
        pass


class CVELCMViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    """Test the CVELCM views."""

    model = CVELCM
    bulk_edit_data = {"description": "Bulk edit views"}

    form_data = {
        "name": "Test 1",
        "slug": "test-1",
        "published_date": datetime.date(2022, 1, 1),
        "link": "https://www.cvedetails.com/cve/CVE-2022-0001/",
    }

    @classmethod
    def setUpTestData(cls):
        create_cves()

    def test_bulk_import_objects_with_constrained_permission(self):
        pass

    def test_bulk_import_objects_with_permission(self):
        pass

    def test_bulk_import_objects_without_permission(self):
        pass

    def test_bulk_import_objects_with_permission_csv_file(self):
        pass

    def test_has_advanced_tab(self):
        pass

    def test_get_object_notes(self):
        pass

    def test_list_objects_with_permission(self):
        pass


class VulnerabilityLCMViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    """Test the VulnerabilityLCM views."""

    model = VulnerabilityLCM

    @classmethod
    def setUpTestData(cls):
        devices = create_devices()
        softwares = create_softwares()
        cves = create_cves()

        vuln_ct = ContentType.objects.get_for_model(VulnerabilityLCM)

        exempt_status = Status.objects.create(
            name="Exempt", slug="exempt", color="4caf50", description="This unit is exempt."
        )
        exempt_status.content_types.set([vuln_ct])
        cls.bulk_edit_data = {"status": exempt_status.id}

        forced_status = Status.objects.create(
            name="Forced", slug="forced", color="4caf50", description="This unit is forced."
        )
        forced_status.content_types.set([vuln_ct])

        for i, cve in enumerate(cves):
            VulnerabilityLCM.objects.create(cve=cve, software=softwares[i], device=devices[i], status=forced_status)

    def test_bulk_import_objects_with_constrained_permission(self):
        pass

    def test_bulk_import_objects_with_permission(self):
        pass

    def test_bulk_import_objects_without_permission(self):
        pass

    # Disabling create view as these models are generated via Job.
    def test_create_object_with_constrained_permission(self):
        pass

    # Disabling create view as these models are generated via Job.
    def test_create_object_with_permission(self):
        pass

    # Disabling create view as these models are generated via Job.
    def test_create_object_without_permission(self):
        pass

    def test_has_advanced_tab(self):
        pass

    def test_get_object_notes(self):
        pass

    def test_bulk_import_objects_with_permission_csv_file(self):
        pass

    def test_list_objects_with_permission(self):
        pass


class SoftwareImageLCMViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    """Test the SoftwareImageLCM views."""

    model = SoftwareImageLCM

    @classmethod
    def setUpTestData(cls):
        softwares = create_softwares()
        manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        device_type1 = DeviceType.objects.create(manufacturer=manufacturer, model="6509", slug="6509")
        device_type2 = DeviceType.objects.create(manufacturer=manufacturer, model="6509-E", slug="6509-e")

        softimage = SoftwareImageLCM.objects.create(
            image_file_name="ios15.1.2m.img",
            software=softwares[0],
            download_url="ftp://images.local/cisco/ios15.1.2m.img",
            image_file_checksum="441rfabd75b0512r7fde7a7a66faa596",
            default_image=True,
        )
        softimage.device_types.set([device_type1, device_type2])
        SoftwareImageLCM.objects.create(
            image_file_name="ios4.22.9m.img",
            software=softwares[1],
            download_url="ftp://images.local/cisco/ios4.22.9m.img",
            image_file_checksum="58arfabd75b051fr7fde7a7ac6faa3fv",
            default_image=False,
        )

        cls.form_data = {
            "image_file_name": "eos_4.21m.swi",
            "software": softwares[-1].id,
            "download_url": "ftp://images.local/arista/eos_4.21m.swi",
            "image_file_checksum": "78arfabd75b0fa2vzas1e7a7ac6faa3fc",
            "default_image": True,
        }
        cls.csv_data = (
            "image_file_name,software",
            f"ios11.7.0m.img,{softwares[0].id}",
            f"ios16.3.1t.img,{softwares[0].id}",
            f"eos_4.21m.swi,{softwares[-1].id}",
        )

    def test_bulk_edit_objects_with_constrained_permission(self):
        pass

    def test_bulk_edit_objects_with_permission(self):
        pass

    def test_bulk_edit_objects_without_permission(self):
        pass

    def test_bulk_edit_form_contains_all_pks(self):
        pass

    def test_has_advanced_tab(self):
        pass

    def test_get_object_notes(self):
        pass

    def test_bulk_import_objects_with_permission_csv_file(self):
        pass

    def test_list_objects_with_permission(self):
        pass


class DeviceSoftwareValidationResultListViewTest(ViewTestCases.ListObjectsViewTestCase):
    """Test DeviceSoftwareValidationResultListView"""

    model = DeviceSoftwareValidationResult

    def _get_base_url(self):
        return "plugins:nautobot_device_lifecycle_mgmt:devicesoftwarevalidationresult_list"

    @classmethod
    def setUpTestData(cls):
        """Set up test objects."""
        device_1, device_2, _ = create_devices()
        DeviceSoftwareValidationResult.objects.create(
            device=device_1,
            software=None,
            is_validated=False,
        )
        DeviceSoftwareValidationResult.objects.create(
            device=device_2,
            software=None,
            is_validated=False,
        )

    def test_device_software_list_view_without_permission(self):
        """Test the SoftwareReportOverview."""

        self.assertHttpStatus(
            self.client.get(
                reverse(
                    "plugins:nautobot_device_lifecycle_mgmt:devicesoftwarevalidationresult_list",
                )
            ),
            403,
        )

    def test_device_software_list_view_with_permission(self):
        """Test the SoftwareReportOverview."""
        obj_perm = ObjectPermission(name="Test permission", actions=["view"])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))
        self.assertHttpStatus(
            self.client.get(
                reverse(
                    "plugins:nautobot_device_lifecycle_mgmt:devicesoftwarevalidationresult_list",
                )
            ),
            200,
        )

    def test_bulk_edit_objects_with_constrained_permission(self):
        pass

    def test_bulk_edit_objects_with_permission(self):
        pass

    def test_bulk_edit_objects_without_permission(self):
        pass

    def test_bulk_edit_form_contains_all_pks(self):
        pass

    def test_has_advanced_tab(self):
        pass

    def test_get_object_notes(self):
        pass

    def test_bulk_import_objects_with_permission_csv_file(self):
        pass

    def test_list_objects_with_permission(self):
        pass


class InventoryItemSoftwareValidationResultListViewTest(ViewTestCases.ListObjectsViewTestCase):
    """Test InventoryItemSoftwareValidationResultListView"""

    model = InventoryItemSoftwareValidationResult

    def _get_base_url(self):
        return "plugins:nautobot_device_lifecycle_mgmt:inventoryitemsoftwarevalidationresult_list"

    @classmethod
    def setUpTestData(cls):
        """Set up test objects."""
        inventory_items = create_inventory_items()
        InventoryItemSoftwareValidationResult.objects.create(
            inventory_item=inventory_items[0],
            software=None,
            is_validated=False,
        )
        InventoryItemSoftwareValidationResult.objects.create(
            inventory_item=inventory_items[1],
            software=None,
            is_validated=False,
        )
        InventoryItemSoftwareValidationResult.objects.create(
            inventory_item=inventory_items[2],
            software=None,
            is_validated=False,
        )

    def test_inventoryitem_software_list_view_without_permission(self):
        """Test the SoftwareReportOverview."""

        self.assertHttpStatus(
            self.client.get(
                reverse(
                    "plugins:nautobot_device_lifecycle_mgmt:inventoryitemsoftwarevalidationresult_list",
                )
            ),
            403,
        )

    def test_inventoryitem_software_list_view_with_permission(self):
        """Test the SoftwareReportOverview."""
        obj_perm = ObjectPermission(name="Test permission", actions=["view"])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))
        self.assertHttpStatus(
            self.client.get(
                reverse(
                    "plugins:nautobot_device_lifecycle_mgmt:inventoryitemsoftwarevalidationresult_list",
                )
            ),
            200,
        )

    def test_bulk_edit_objects_with_constrained_permission(self):
        pass

    def test_bulk_edit_objects_with_permission(self):
        pass

    def test_bulk_edit_objects_without_permission(self):
        pass

    def test_bulk_edit_form_contains_all_pks(self):
        pass

    def test_has_advanced_tab(self):
        pass

    def test_get_object_notes(self):
        pass

    def test_bulk_import_objects_with_permission_csv_file(self):
        pass

    def test_list_objects_with_permission(self):
        pass


class ContractLCMExportLinkedObjectsTest(TestCase):
    """Test Contract Devices and Contract Inventory Items CSV exports."""

    @classmethod
    def setUpTestData(cls):
        """Set up test objects."""
        devices = create_devices()
        inventoryitems = create_inventory_items()
        provider1 = ProviderLCM(name="Cisco")
        provider1.validated_save()
        provider2 = ProviderLCM(name="Arista")
        provider2.validated_save()
        contract1 = ContractLCM(provider=provider1, name="CiscoHW1", contract_type="Hardware")
        contract1.validated_save()
        contract2 = ContractLCM(provider=provider2, name="AristaHW1", contract_type="Hardware")
        contract2.validated_save()

        dev_contract_rel = Relationship.objects.get(slug="contractlcm-to-device")
        RelationshipAssociation.objects.create(
            source=contract1,
            destination=devices[0],
            relationship=dev_contract_rel,
        )
        RelationshipAssociation.objects.create(
            source=contract1,
            destination=devices[1],
            relationship=dev_contract_rel,
        )
        RelationshipAssociation.objects.create(
            source=contract2,
            destination=devices[2],
            relationship=dev_contract_rel,
        )

        inv_item_contract_rel = Relationship.objects.get(slug="contractlcm-to-inventoryitem")
        RelationshipAssociation.objects.create(
            source=contract1,
            destination=inventoryitems[0],
            relationship=inv_item_contract_rel,
        )
        RelationshipAssociation.objects.create(
            source=contract2,
            destination=inventoryitems[1],
            relationship=inv_item_contract_rel,
        )
        RelationshipAssociation.objects.create(
            source=contract2,
            destination=inventoryitems[2],
            relationship=inv_item_contract_rel,
        )

    def test_contract_devices_export(self):
        """Test CSV export for Devices connected to Contract."""
        # Add model-level permission
        obj_perm = ObjectPermission(name="Test permission", actions=["view"])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(ContractLCM))
        obj_perm.object_types.add(ContentType.objects.get_for_model(Device))

        contract1 = ContractLCM.objects.filter(name="CiscoHW1").first()
        response = self.client.get(f"{contract1.get_absolute_url()}?export_contract=devices")
        self.assertHttpStatus(response, [200])
        self.assertEqual(response.get("Content-Type"), "text/csv")
        response_body = response.content.decode(response.charset)
        self.assertEqual(
            response_body,
            "Contract Name,Contract Type,Device Name,Device Serial,Device Manufacturer,Device Site"
            "\nCiscoHW1,Hardware,sw1,,Cisco,Test 1"
            "\nCiscoHW1,Hardware,sw2,,Cisco,Test 1",
        )

        contract2 = ContractLCM.objects.filter(name="AristaHW1").first()
        response = self.client.get(f"{contract2.get_absolute_url()}?export_contract=devices")
        self.assertHttpStatus(response, [200])
        self.assertEqual(response.get("Content-Type"), "text/csv")
        response_body = response.content.decode(response.charset)
        self.assertEqual(
            response_body,
            "Contract Name,Contract Type,Device Name,Device Serial,Device Manufacturer,Device Site"
            "\nAristaHW1,Hardware,sw3,,Cisco,Test 1",
        )

    def test_contract_inventoryitems_export(self):
        """Test CSV export for InventoryItems connected to Contract."""
        # Add model-level permission
        obj_perm = ObjectPermission(name="Test permission", actions=["view"])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(ContractLCM))
        obj_perm.object_types.add(ContentType.objects.get_for_model(InventoryItem))

        contract1 = ContractLCM.objects.filter(name="CiscoHW1").first()
        response = self.client.get(f"{contract1.get_absolute_url()}?export_contract=inventoryitems")
        self.assertHttpStatus(response, [200])
        self.assertEqual(response.get("Content-Type"), "text/csv")
        response_body = response.content.decode(response.charset)
        self.assertEqual(
            response_body,
            "Contract Name,Contract Type,Item Name,Item Part ID,Item Serial,Item Manufacturer,Item Parent Device,Item Site"
            "\nCiscoHW1,Hardware,SUP2T Card,VS-S2T-10G,,Cisco,sw1,Test 1",
        )

        contract2 = ContractLCM.objects.filter(name="AristaHW1").first()
        response = self.client.get(f"{contract2.get_absolute_url()}?export_contract=inventoryitems")
        self.assertHttpStatus(response, [200])
        self.assertEqual(response.get("Content-Type"), "text/csv")
        response_body = response.content.decode(response.charset)
        self.assertEqual(
            response_body,
            "Contract Name,Contract Type,Item Name,Item Part ID,Item Serial,Item Manufacturer,Item Parent Device,Item Site"
            "\nAristaHW1,Hardware,100GBASE-SR4 QSFP Transceiver,QSFP-100G-SR4-S,,Cisco,sw2,Test 1"
            "\nAristaHW1,Hardware,48x RJ-45 Line Card,WS-X6548-GE-TX,,Cisco,sw3,Test 1",
        )


class ContractLCMViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    """Test the ContractLCM views."""

    model = ContractLCM

    def _get_base_url(self):
        return "plugins:{}:{}_{{}}".format(  # pylint: disable=consider-using-f-string
            self.model._meta.app_label, self.model._meta.model_name
        )

    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        provider = ProviderLCM.objects.create(name="Cisco")

        ContractLCM.objects.create(name="Cisco Support - Hardware Routers", provider=provider, contract_type="Hardware")
        ContractLCM.objects.create(
            name="Cisco Support - Hardware Switches", provider=provider, contract_type="Hardware"
        )
        ContractLCM.objects.create(name="Cisco Support - Software", provider=provider, contract_type="Software")

        cls.form_data = {
            "name": "Cisco Support - Software - Line Cards",
            "provider": provider.id,
            "contract_type": "Software",
        }
        cls.csv_data = (
            "name,provider,contract_type",
            f"Cisco Support - Hardware1, {provider.id}, Hardware",
            f"Cisco Support - Hardware2, {provider.id}, Hardware",
            f"Cisco Support - Software, {provider.id}, Software",
        )

    def test_has_advanced_tab(self):
        pass

    def test_get_object_notes(self):
        pass

    def test_list_objects_with_permission(self):
        pass

    def test_bulk_import_objects_with_permission_csv_file(self):
        pass

    def test_bulk_import_objects_with_constrained_permission(self):
        pass

    def test_bulk_import_objects_with_permission(self):
        pass

    def test_bulk_edit_objects_with_constrained_permission(self):
        pass

    def test_bulk_edit_objects_with_permission(self):
        pass

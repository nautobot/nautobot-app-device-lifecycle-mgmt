# pylint: disable=no-member
"""nautobot_device_lifecycle_mgmt test class for models."""
from datetime import date

import time_machine
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.test import TestCase
from nautobot.dcim.models import DeviceType, Manufacturer, Platform
from nautobot.extras.choices import RelationshipTypeChoices
from nautobot.extras.models import Relationship, RelationshipAssociation, Status, Tag

from nautobot_device_lifecycle_mgmt.models import (
    CVELCM,
    ContractLCM,
    DeviceSoftwareValidationResult,
    HardwareLCM,
    InventoryItemSoftwareValidationResult,
    ProviderLCM,
    SoftwareImageLCM,
    SoftwareLCM,
    ValidatedSoftwareLCM,
    VulnerabilityLCM,
)

from .conftest import create_cves, create_devices, create_inventory_items, create_softwares, create_validated_softwares


class HardwareLCMTestCase(TestCase):
    """Tests for the HardwareLCM models."""

    def setUp(self):
        """Set up base objects."""
        self.manufacturer, _ = Manufacturer.objects.get_or_create(name="Cisco")
        self.device_type, _ = DeviceType.objects.get_or_create(model="c9300-24", manufacturer=self.manufacturer)

    def test_create_hwlcm_success_eo_sale(self):
        """Successfully create basic notice with end_of_sale."""
        hwlcm_obj = HardwareLCM.objects.create(device_type=self.device_type, end_of_sale=date(2023, 4, 1))

        self.assertEqual(hwlcm_obj.device_type, self.device_type)
        self.assertEqual(str(hwlcm_obj.end_of_sale), "2023-04-01")
        self.assertEqual(str(hwlcm_obj), "Device Type: c9300-24 - End of sale: 2023-04-01")

    def test_create_hwlcm_notice_success_eo_support(self):
        """Successfully create basic notice with end_of_support."""
        hwlcm_obj = HardwareLCM.objects.create(device_type=self.device_type, end_of_support=date(2022, 4, 1))

        self.assertEqual(hwlcm_obj.device_type, self.device_type)
        self.assertEqual(str(hwlcm_obj.end_of_support), "2022-04-01")
        self.assertEqual(str(hwlcm_obj), "Device Type: c9300-24 - End of support: 2022-04-01")

    def test_create_hwlcm_success_eo_sale_inventory_item(self):
        """Successfully create basic notice with end_of_sale."""
        inventory_item = "WS-X6848-TX-2T"
        hwlcm_obj = HardwareLCM.objects.create(inventory_item=inventory_item, end_of_sale=date(2023, 4, 1))

        self.assertEqual(hwlcm_obj.inventory_item, inventory_item)
        self.assertEqual(str(hwlcm_obj.end_of_sale), "2023-04-01")
        self.assertEqual(str(hwlcm_obj), f"Inventory Part: {inventory_item} - End of sale: 2023-04-01")

    def test_create_hwlcm_notice_success_eo_all(self):
        """Successfully create basic notice."""
        hwlcm_obj = HardwareLCM.objects.create(
            device_type=self.device_type,
            end_of_sale=date(2022, 4, 1),
            end_of_support=date(2023, 4, 1),
            end_of_sw_releases=date(2024, 4, 1),
            end_of_security_patches=date(2025, 4, 1),
            documentation_url="https://test.com",
        )

        self.assertEqual(hwlcm_obj.device_type, self.device_type)
        self.assertEqual(str(hwlcm_obj.end_of_sale), "2022-04-01")
        self.assertEqual(str(hwlcm_obj.end_of_support), "2023-04-01")
        self.assertEqual(str(hwlcm_obj.end_of_sw_releases), "2024-04-01")
        self.assertEqual(str(hwlcm_obj.end_of_security_patches), "2025-04-01")
        self.assertEqual(hwlcm_obj.documentation_url, "https://test.com")
        self.assertEqual(str(hwlcm_obj), "Device Type: c9300-24 - End of support: 2023-04-01")

    def test_create_hwlcm_notice_failed_missing_one_of(self):
        """Successfully create basic notice."""
        with self.assertRaises(ValidationError) as failure_exception:
            HardwareLCM.objects.create(device_type=self.device_type)
        self.assertEqual(failure_exception.exception.messages[0], "End of Sale or End of Support must be specified.")

    def test_create_hwlcm_notice_failed_validation_documentation_url(self):
        """Successfully create basic notice."""
        with self.assertRaises(ValidationError) as failure_exception:
            HardwareLCM.objects.create(
                device_type=self.device_type, end_of_support=date(2023, 4, 1), documentation_url="test.com"
            )
        self.assertEqual(failure_exception.exception.messages[0], "Enter a valid URL.")

    def test_create_hwlcm_notice_failed_validation_date(self):
        """Successfully create basic notice."""
        with self.assertRaises(ValidationError) as failure_exception:
            HardwareLCM.objects.create(device_type=self.device_type, end_of_support="April 1st 2022")
        self.assertIn("invalid date format. It must be in YYYY-MM-DD format.", failure_exception.exception.messages[0])

    def test_expired_property_end_of_support_expired(self):
        """Test expired property is expired with end_of_support."""
        hwlcm_obj = HardwareLCM.objects.create(device_type=self.device_type, end_of_support=date(2021, 4, 1))
        self.assertTrue(hwlcm_obj.expired)

    def test_expired_property_end_of_support_not_expired(self):
        """Test expired property is NOT expired with end_of_support."""
        hwlcm_obj = HardwareLCM.objects.create(device_type=self.device_type, end_of_support=date(2099, 4, 1))
        self.assertFalse(hwlcm_obj.expired)

    def test_expired_property_end_of_sale_expired(self):
        """Test expired property is expired with end_of_sale."""
        hwlcm_obj = HardwareLCM.objects.create(device_type=self.device_type, end_of_sale=date(2021, 4, 1))
        self.assertTrue(hwlcm_obj.expired)

    def test_expired_property_end_of_sale_not_expired(self):
        """Test expired property is NOT expired with end_of_sale."""
        hwlcm_obj = HardwareLCM.objects.create(device_type=self.device_type, end_of_sale=date(2999, 4, 1))
        self.assertFalse(hwlcm_obj.expired)

    def test_expired_field_setting_end_of_sale_expired(self):
        """Test expired property is expired with end_of_sale when set within plugin settings."""
        settings.PLUGINS_CONFIG["nautobot_device_lifecycle_mgmt"]["expired_field"] = "end_of_sale"
        hwlcm_obj = HardwareLCM.objects.create(
            device_type=self.device_type, end_of_sale=date(2021, 4, 1), end_of_support=date(2999, 4, 1)
        )
        self.assertTrue(hwlcm_obj.expired)

    def test_expired_field_setting_end_of_sale_not_expired(self):
        """Test expired property is NOT expired with end_of_sale not existing but plugin setting set to end_of_sale."""
        settings.PLUGINS_CONFIG["nautobot_device_lifecycle_mgmt"]["expired_field"] = "end_of_sale"
        hwlcm_obj = HardwareLCM.objects.create(device_type=self.device_type, end_of_support=date(2999, 4, 1))
        self.assertFalse(hwlcm_obj.expired)


class SoftwareLCMTestCase(TestCase):
    """Tests for the SoftwareLCM model."""

    def setUp(self):
        """Set up base objects."""
        self.device_platform, _ = Platform.objects.get_or_create(name="cisco_ios")

    def test_create_softwarelcm_required_only(self):
        """Successfully create SoftwareLCM with required fields only."""
        softwarelcm = SoftwareLCM.objects.create(device_platform=self.device_platform, version="4.21.3F")

        self.assertEqual(softwarelcm.device_platform, self.device_platform)
        self.assertEqual(softwarelcm.version, "4.21.3F")

    def test_create_softwarelcm_all(self):
        """Successfully create SoftwareLCM with all fields."""
        softwarelcm_full = SoftwareLCM.objects.create(
            device_platform=self.device_platform,
            version="17.3.3 MD",
            alias="Amsterdam-17.3.3 MD",
            release_date=date(2019, 1, 10),
            end_of_support=date(2022, 5, 15),
            documentation_url="https://www.cisco.com/c/en/us/support/ios-nx-os-software/ios-15-4m-t/series.html",
            long_term_support=False,
            pre_release=True,
        )

        self.assertEqual(softwarelcm_full.device_platform, self.device_platform)
        self.assertEqual(softwarelcm_full.version, "17.3.3 MD")
        self.assertEqual(softwarelcm_full.alias, "Amsterdam-17.3.3 MD")
        self.assertEqual(str(softwarelcm_full.release_date), "2019-01-10")
        self.assertEqual(str(softwarelcm_full.end_of_support), "2022-05-15")
        self.assertEqual(
            softwarelcm_full.documentation_url,
            "https://www.cisco.com/c/en/us/support/ios-nx-os-software/ios-15-4m-t/series.html",
        )
        self.assertEqual(softwarelcm_full.long_term_support, False)
        self.assertEqual(softwarelcm_full.pre_release, True)
        self.assertEqual(str(softwarelcm_full), f"{self.device_platform.name} - {softwarelcm_full.version}")


class ValidatedSoftwareLCMTestCase(TestCase):  # pylint: disable=too-many-instance-attributes
    """Tests for the ValidatedSoftwareLCM model."""

    def setUp(self):
        """Set up base objects."""
        device_platform, _ = Platform.objects.get_or_create(name="cisco_ios")
        self.software = SoftwareLCM.objects.create(
            device_platform=device_platform,
            version="17.3.3 MD",
            release_date=date(2019, 1, 10),
        )
        manufacturer, _ = Manufacturer.objects.get_or_create(name="Cisco")
        self.device_type_1, _ = DeviceType.objects.get_or_create(manufacturer=manufacturer, model="ASR-1000")
        self.device_type_2, _ = DeviceType.objects.get_or_create(manufacturer=manufacturer, model="CAT-3750")
        self.content_type_devicetype = ContentType.objects.get(app_label="dcim", model="devicetype")
        self.device_1, self.device_2 = create_devices()[:2]
        self.inventoryitem_1, self.inventoryitem_2 = create_inventory_items()[:2]

    def test_create_validatedsoftwarelcm_required_only(self):
        """Successfully create ValidatedSoftwareLCM with required fields only."""

        validatedsoftwarelcm = ValidatedSoftwareLCM(
            software=self.software,
            start=date(2019, 1, 10),
        )
        validatedsoftwarelcm.device_types.set([self.device_type_1])
        validatedsoftwarelcm.save()

        self.assertEqual(validatedsoftwarelcm.software, self.software)
        self.assertEqual(str(validatedsoftwarelcm.start), "2019-01-10")
        self.assertEqual(list(validatedsoftwarelcm.device_types.all()), [self.device_type_1])

    def test_create_validatedsoftwarelcm_all(self):
        """Successfully create ValidatedSoftwareLCM with all fields."""
        validatedsoftwarelcm = ValidatedSoftwareLCM(
            software=self.software,
            start=date(2020, 4, 15),
            end=date(2022, 11, 1),
            preferred=False,
        )
        validatedsoftwarelcm.device_types.set([self.device_type_1])
        validatedsoftwarelcm.save()

        self.assertEqual(validatedsoftwarelcm.software, self.software)
        self.assertEqual(str(validatedsoftwarelcm.start), "2020-04-15")
        self.assertEqual(str(validatedsoftwarelcm.end), "2022-11-01")
        self.assertEqual(list(validatedsoftwarelcm.device_types.all()), [self.device_type_1])
        self.assertEqual(validatedsoftwarelcm.preferred, False)
        self.assertEqual(str(validatedsoftwarelcm), f"{self.software} - Valid since: {validatedsoftwarelcm.start}")

    def test_validatedsoftwarelcm_valid_property(self):
        """Test behavior of the 'valid' property."""
        validatedsoftwarelcm_start_only = ValidatedSoftwareLCM(
            software=self.software,
            start=date(2020, 4, 15),
            preferred=False,
        )
        validatedsoftwarelcm_start_only.device_types.set([self.device_type_1])
        validatedsoftwarelcm_start_only.save()

        validatedsoftwarelcm_start_end = ValidatedSoftwareLCM(
            software=self.software,
            start=date(2020, 4, 15),
            end=date(2022, 11, 1),
            preferred=False,
        )
        validatedsoftwarelcm_start_end.device_types.set([self.device_type_2])
        validatedsoftwarelcm_start_end.save()

        date_valid = date(2021, 6, 11)
        date_before_valid_start = date(2018, 9, 26)
        date_after_valid_end = date(2023, 1, 4)
        date_start_valid = date(2020, 4, 15)

        with time_machine.travel(date_valid):
            self.assertEqual(validatedsoftwarelcm_start_only.valid, True)
            self.assertEqual(validatedsoftwarelcm_start_end.valid, True)

        with time_machine.travel(date_before_valid_start):
            self.assertEqual(validatedsoftwarelcm_start_only.valid, False)
            self.assertEqual(validatedsoftwarelcm_start_end.valid, False)

        with time_machine.travel(date_after_valid_end):
            self.assertEqual(validatedsoftwarelcm_start_only.valid, True)
            self.assertEqual(validatedsoftwarelcm_start_end.valid, False)

        with time_machine.travel(date_start_valid):
            self.assertEqual(validatedsoftwarelcm_start_only.valid, True)
            self.assertEqual(validatedsoftwarelcm_start_end.valid, True)

    def test_get_for_object_device(self):
        validatedsoftwarelcm_1 = ValidatedSoftwareLCM(
            software=self.software,
            start=date(2019, 1, 10),
        )
        validatedsoftwarelcm_1.devices.set([self.device_1])
        validatedsoftwarelcm_1.save()

        validatedsoftwarelcm_2 = ValidatedSoftwareLCM(
            software=self.software,
            start=date(2018, 1, 10),
        )
        validatedsoftwarelcm_2.devices.set([self.device_2])
        validatedsoftwarelcm_2.save()

        validated_software_for_device = ValidatedSoftwareLCM.objects.get_for_object(self.device_1)
        self.assertEqual(validated_software_for_device.count(), 1)
        self.assertTrue(self.device_1 in validated_software_for_device.first().devices.all())

    def test_get_for_object_devicetype(self):
        validatedsoftwarelcm_1 = ValidatedSoftwareLCM(
            software=self.software,
            start=date(2019, 1, 10),
        )
        validatedsoftwarelcm_1.device_types.set([self.device_type_1])
        validatedsoftwarelcm_1.save()

        validatedsoftwarelcm_2 = ValidatedSoftwareLCM(
            software=self.software,
            start=date(2018, 1, 10),
        )
        validatedsoftwarelcm_2.device_types.set([self.device_type_2])
        validatedsoftwarelcm_2.save()

        validated_software_for_device_type = ValidatedSoftwareLCM.objects.get_for_object(self.device_type_1)
        self.assertEqual(validated_software_for_device_type.count(), 1)
        self.assertTrue(self.device_type_1 in validated_software_for_device_type.first().device_types.all())

    def test_get_for_object_inventoryitem(self):
        validatedsoftwarelcm_1 = ValidatedSoftwareLCM(
            software=self.software,
            start=date(2019, 1, 10),
        )
        validatedsoftwarelcm_1.inventory_items.set([self.inventoryitem_1])
        validatedsoftwarelcm_1.save()

        validatedsoftwarelcm_2 = ValidatedSoftwareLCM(
            software=self.software,
            start=date(2018, 1, 10),
        )
        validatedsoftwarelcm_2.inventory_items.set([self.inventoryitem_2])
        validatedsoftwarelcm_2.save()

        validated_software_for_inventoryitem = ValidatedSoftwareLCM.objects.get_for_object(self.inventoryitem_1)
        self.assertEqual(validated_software_for_inventoryitem.count(), 1)
        self.assertTrue(self.inventoryitem_1 in validated_software_for_inventoryitem.first().inventory_items.all())


class DeviceSoftwareValidationResultTestCase(TestCase):  # pylint: disable=too-many-instance-attributes
    """Tests for the DeviceSoftwareValidationResult model."""

    def setUp(self):
        """Set up test objects."""
        self.device = create_devices()[0]
        self.platform = Platform.objects.all().first()
        (
            self.software_one,
            self.software_two,
            self.validatedsoftwarelcm,
            self.validatedsoftwarelcm_two,
        ) = create_validated_softwares()
        self.validated_software_qs = ValidatedSoftwareLCM.objects.get_for_object(self.validatedsoftwarelcm)
        self.validated_software_qs_two = ValidatedSoftwareLCM.objects.get_for_object(self.validatedsoftwarelcm_two)

    def test_create_devicesoftwarevalidationresult(self):
        """Successfully create SoftwareLCM with required fields only."""
        validation_result = DeviceSoftwareValidationResult.objects.create(
            device=self.device,
            software=self.software_one,
            is_validated=True,
        )

        self.assertEqual(validation_result.device, self.device)
        self.assertEqual(validation_result.software, self.software_one)
        self.assertEqual(validation_result.is_validated, True)

    def test_create_devicesoftwarevalidationresult_one_valid_software(self):
        """Successfully create DeviceSoftwareValidationResult with one valid software."""
        validation_result = DeviceSoftwareValidationResult.objects.create(
            device=self.device,
            software=self.software_one,
            is_validated=True,
        )
        validation_result.valid_software.set(self.validated_software_qs)
        self.assertEqual(validation_result.valid_software.values()[0]["software_id"], self.software_one.id)

    def test_create_devicesoftwarevalidationresult_two_valid_softwares(self):
        """Successfully create DeviceSoftwareValidationResult with two valid software."""
        validation_result = DeviceSoftwareValidationResult.objects.create(
            device=self.device,
            software=self.software_one,
            is_validated=True,
        )
        validation_result.valid_software.set(self.validated_software_qs)
        validation_result.valid_software.set(self.validated_software_qs_two)
        self.assertEqual(validation_result.valid_software.values()[0]["software_id"], self.software_one.id)
        self.assertEqual(validation_result.valid_software.values()[1]["software_id"], self.software_two.id)


class InventoryItemSoftwareValidationResultTestCase(TestCase):  # pylint: disable=too-many-instance-attributes
    """Tests for the DeviceSoftwareValidationResult model."""

    def setUp(self):
        """Set up test objects."""
        self.inventory_item = create_inventory_items()[0]
        self.platform = Platform.objects.all().first()
        self.platform = Platform.objects.all().first()
        (
            self.software_one,
            self.software_two,
            self.validatedsoftwarelcm,
            self.validatedsoftwarelcm_two,
        ) = create_validated_softwares()
        self.validated_software_qs = ValidatedSoftwareLCM.objects.get_for_object(self.validatedsoftwarelcm)
        self.validated_software_qs_two = ValidatedSoftwareLCM.objects.get_for_object(self.validatedsoftwarelcm_two)

    def test_create_itemsoftwarevalidationresult(self):
        """Successfully create SoftwareLCM with required fields only."""
        validation_result = InventoryItemSoftwareValidationResult.objects.create(
            inventory_item=self.inventory_item,
            software=self.software_one,
            is_validated=True,
        )

        self.assertEqual(validation_result.inventory_item, self.inventory_item)
        self.assertEqual(validation_result.software, self.software_one)
        self.assertEqual(validation_result.is_validated, True)

    def test_create_itemsoftwarevalidationresult_one_valid_software(self):
        """Successfully create InventoryItemSoftwareValidationResult with one valid software."""
        validation_result = InventoryItemSoftwareValidationResult.objects.create(
            inventory_item=self.inventory_item,
            software=self.software_one,
            is_validated=True,
        )
        validation_result.valid_software.set(self.validated_software_qs)
        self.assertEqual(validation_result.valid_software.values()[0]["software_id"], self.software_one.id)

    def test_create_itemsoftwarevalidationresult_two_valid_softwares(self):
        """Successfully create InventoryItemSoftwareValidationResult with two valid software."""
        validation_result = InventoryItemSoftwareValidationResult.objects.create(
            inventory_item=self.inventory_item,
            software=self.software_one,
            is_validated=True,
        )
        validation_result.valid_software.set(self.validated_software_qs)
        validation_result.valid_software.set(self.validated_software_qs_two)
        self.assertEqual(validation_result.valid_software.values()[0]["software_id"], self.software_one.id)
        self.assertEqual(validation_result.valid_software.values()[1]["software_id"], self.software_two.id)


class CVELCMTestCase(TestCase):
    """Tests for the CVELCM model."""

    def setUp(self):
        """Set up the test objects."""
        self.device_platform, _ = Platform.objects.get_or_create(name="cisco_ios")
        self.softwarelcm = SoftwareLCM.objects.create(device_platform=self.device_platform, version="15.2(5)e")
        self.cve_ct = ContentType.objects.get_for_model(CVELCM)
        self.software_ct = ContentType.objects.get_for_model(SoftwareLCM)
        self.relationship = Relationship.objects.get_or_create(
            label="CVE to Software",
            defaults={
                "label": "CVE to Software",
                "key": "cve_soft",
                "type": RelationshipTypeChoices.TYPE_MANY_TO_MANY,
                "source_type": ContentType.objects.get_for_model(CVELCM),
                "source_label": "Affected Softwares",
                "destination_type": ContentType.objects.get_for_model(SoftwareLCM),
                "destination_label": "Corresponding CVEs",
            },
        )[0]
        self.status, _ = Status.objects.get_or_create(name="Fixed", color="4caf50", description="Unit has been fixed")
        self.status.content_types.set([self.cve_ct])

    def test_create_cvelcm_required_only(self):
        """Successfully create CVELCM with required fields only."""
        cvelcm = CVELCM.objects.create(
            name="CVE-2021-1391", published_date="2021-03-24", link="https://www.cvedetails.com/cve/CVE-2021-1391/"
        )

        self.assertEqual(cvelcm.name, "CVE-2021-1391")
        self.assertEqual(cvelcm.published_date, "2021-03-24")
        self.assertEqual(cvelcm.link, "https://www.cvedetails.com/cve/CVE-2021-1391/")

    def test_create_cvelcm_all(self):
        """Successfully create CVELCM with all fields."""
        cvelcm = CVELCM.objects.create(
            name="CVE-2021-34699",
            published_date="2021-09-23",
            link="https://www.cvedetails.com/cve/CVE-2021-34699/",
            status=self.status,
            description="Thanos",
            severity="High",
            cvss=6.8,
            cvss_v2=6.9,
            cvss_v3=6.7,
            fix="Avengers",
            comments="This is very bad juju.",
        )

        self.assertEqual(cvelcm.name, "CVE-2021-34699")
        self.assertEqual(cvelcm.published_date, "2021-09-23")
        self.assertEqual(cvelcm.link, "https://www.cvedetails.com/cve/CVE-2021-34699/")
        self.assertEqual(cvelcm.status, self.status)
        self.assertEqual(cvelcm.description, "Thanos")
        self.assertEqual(cvelcm.severity, "High")
        self.assertEqual(cvelcm.cvss, 6.8)
        self.assertEqual(cvelcm.cvss_v2, 6.9)
        self.assertEqual(cvelcm.cvss_v3, 6.7)
        self.assertEqual(cvelcm.fix, "Avengers")
        self.assertEqual(cvelcm.comments, "This is very bad juju.")

    def test_create_cve_soft_relationship_association(self):
        """Successfully create a relationship between CVE and Software."""
        cvelcm = CVELCM.objects.create(
            name="CVE-2021-1391", published_date="2021-03-24", link="https://www.cvedetails.com/cve/CVE-2021-1391/"
        )

        association = RelationshipAssociation.objects.create(
            relationship_id=self.relationship.id,
            source_id=cvelcm.id,
            source_type_id=self.cve_ct.id,
            destination_id=self.softwarelcm.id,
            destination_type_id=self.software_ct.id,
        )

        cve_rels = cvelcm.get_relationships()

        self.assertEqual(cve_rels["source"][self.relationship].first(), association)


class VulnerabilityLCMTestCase(TestCase):
    """Tests for the VulnerabilityLCM model."""

    def setUp(self):
        """Set up the test objects."""
        self.inv_items = create_inventory_items()
        self.devices = [inv_item.device for inv_item in self.inv_items]
        self.cves = create_cves()
        self.softwares = create_softwares()
        vuln_ct = ContentType.objects.get_for_model(VulnerabilityLCM)
        self.status = Status.objects.create(name="Exempt", color="4caf50", description="This unit is exempt.")
        self.status.content_types.set([vuln_ct])

    def test_create_vulnerabilitylcm_device_required_only(self):
        """Successfully create VulnerabilityLCM for device with required fields only."""
        vulnerability = VulnerabilityLCM.objects.create(
            cve=self.cves[0], software=self.softwares[0], device=self.devices[0]
        )

        self.assertEqual(str(vulnerability), "Device: sw1 - Software: cisco_ios - 15.1(2)M - CVE: CVE-2021-1391")
        self.assertEqual(vulnerability.cve, self.cves[0])
        self.assertEqual(vulnerability.software, self.softwares[0])
        self.assertEqual(vulnerability.device, self.devices[0])

    def test_create_vulnerabilitylcm_inventory_item_required_only(self):
        """Successfully create VulnerabilityLCM for inventory item with required fields only."""
        vulnerability = VulnerabilityLCM.objects.create(
            cve=self.cves[1], software=self.softwares[1], inventory_item=self.inv_items[1]
        )

        self.assertEqual(
            str(vulnerability),
            "Inventory Part: 100GBASE-SR4 QSFP Transceiver - Software: cisco_ios - 4.22.9M - CVE: CVE-2021-44228",
        )
        self.assertEqual(vulnerability.cve, self.cves[1])
        self.assertEqual(vulnerability.software, self.softwares[1])
        self.assertEqual(vulnerability.inventory_item, self.inv_items[1])

    def test_create_vulnerabilitylcm_all(self):
        """Successfully create VulnerabilityLCM with all fields."""
        vulnerability = VulnerabilityLCM.objects.create(
            cve=self.cves[2], software=self.softwares[2], device=self.devices[2], status=self.status
        )

        self.assertEqual(str(vulnerability), "Device: sw3 - Software: cisco_ios - 21.4R3 - CVE: CVE-2020-27134")
        self.assertEqual(vulnerability.cve, self.cves[2])
        self.assertEqual(vulnerability.software, self.softwares[2])
        self.assertEqual(vulnerability.device, self.devices[2])
        self.assertEqual(vulnerability.status, self.status)


class SoftwareImageLCMTestCase(TestCase):
    """Tests for the SoftwareImageLCM model."""

    def setUp(self):
        """Set up base objects."""
        device_platform, _ = Platform.objects.get_or_create(name="cisco_ios")
        self.software = SoftwareLCM.objects.create(
            device_platform=device_platform,
            version="17.3.3 MD",
            release_date=date(2019, 1, 10),
        )
        manufacturer, _ = Manufacturer.objects.get_or_create(name="Cisco")
        self.device_type_1, _ = DeviceType.objects.get_or_create(manufacturer=manufacturer, model="ASR-1000")
        self.device_type_2, _ = DeviceType.objects.get_or_create(manufacturer=manufacturer, model="CAT-3750")
        self.inventory_item = create_inventory_items()[0]
        self.tag = Tag.objects.create(name="asr")

    def test_create_softwareimage_required_only(self):
        """Successfully create SoftwareImageLCM with required fields only."""
        softwareimage = SoftwareImageLCM(image_file_name="ios17.3.3md.img", software=self.software)
        softwareimage.device_types.set([self.device_type_1])
        softwareimage.save()

        self.assertEqual(softwareimage.image_file_name, "ios17.3.3md.img")
        self.assertEqual(softwareimage.software, self.software)
        self.assertEqual(list(softwareimage.device_types.all()), [self.device_type_1])

    def test_create_softwareimage_all(self):
        """Successfully create SoftwareImageLCM with all fields."""
        softwareimage = SoftwareImageLCM(
            image_file_name="ios17.3.3md.img",
            software=self.software,
            download_url="ftp://images.local/cisco/ios17.3.3md.img",
            image_file_checksum="441rfabd75b0512r7fde7a7a66faa596",
            default_image=True,
        )
        softwareimage.device_types.set([self.device_type_1])
        softwareimage.inventory_items.set([self.inventory_item])
        softwareimage.object_tags.set([self.tag])
        softwareimage.save()

        self.assertEqual(softwareimage.image_file_name, "ios17.3.3md.img")
        self.assertEqual(softwareimage.software, self.software)
        self.assertEqual(softwareimage.download_url, "ftp://images.local/cisco/ios17.3.3md.img")
        self.assertEqual(softwareimage.image_file_checksum, "441rfabd75b0512r7fde7a7a66faa596")
        self.assertEqual(softwareimage.default_image, True)
        self.assertEqual(list(softwareimage.device_types.all()), [self.device_type_1])
        self.assertEqual(list(softwareimage.inventory_items.all()), [self.inventory_item])
        self.assertEqual(list(softwareimage.object_tags.all()), [self.tag])
        self.assertEqual(str(softwareimage), f"{softwareimage.image_file_name}")

    def test_get_software_images_for_device_type(self):
        """Test related reverse relationship from device type to software image"""
        softwareimage = SoftwareImageLCM(
            image_file_name="ios17.3.3md.img",
            software=self.software,
            download_url="ftp://images.local/cisco/ios17.3.3md.img",
            image_file_checksum="441rfabd75b0512r7fde7a7a66faa596",
            default_image=False,
        )
        softwareimage.device_types.set([self.device_type_1])
        softwareimage.save()

        self.assertEqual(list(self.device_type_1.software_images.all()), [softwareimage])


class ProviderLCMTestCase(TestCase):
    """Tests for the HardwareLCM models."""

    def test_provider_creation(self):
        provider = ProviderLCM.objects.create(
            name="Cisco",
            description="Cisco Support",
            physical_address="123 Cisco Way, San Jose, CA",
            country="USA",
            phone="(123) 456-7890",
            email="email@cisco.com",
            portal_url="https://www.cisco.com/",
            comments="Test Comment",
        )
        self.assertEqual(provider.name, "Cisco")
        self.assertEqual(provider.description, "Cisco Support")
        self.assertEqual(provider.physical_address, "123 Cisco Way, San Jose, CA")
        self.assertEqual(provider.country, "USA")
        self.assertEqual(provider.phone, "(123) 456-7890")
        self.assertEqual(provider.email, "email@cisco.com")
        self.assertEqual(provider.portal_url, "https://www.cisco.com/")
        self.assertEqual(provider.comments, "Test Comment")

    def test_provider_assignment(self):
        ProviderLCM.objects.create(
            name="Cisco",
            description="Cisco Support",
            physical_address="123 Cisco Way, San Jose, CA",
            country="USA",
            phone="(123) 456-7890",
            email="email@cisco.com",
            portal_url="https://www.cisco.com/",
            comments="Test Comment",
        )
        cisco_contract = ContractLCM.objects.create(
            provider=ProviderLCM.objects.get(name="Cisco"),
            name="Cisco Contract",
            number="888-8888",
            start=date(2020, 4, 1),
            end=date(2025, 4, 15),
            cost=10.00,
            support_level="Tier 1",
            currency="USD",
            contract_type="Hardware",
            comments="Cisco gave us discount",
        )
        self.assertEqual(cisco_contract.provider, ProviderLCM.objects.get(name="Cisco"))
        self.assertEqual(cisco_contract.name, "Cisco Contract")
        self.assertEqual(cisco_contract.number, "888-8888")
        self.assertEqual(str(cisco_contract.start), "2020-04-01")
        self.assertEqual(str(cisco_contract.end), "2025-04-15")
        self.assertEqual(cisco_contract.cost, 10.00)
        self.assertEqual(cisco_contract.support_level, "Tier 1")
        self.assertEqual(cisco_contract.currency, "USD")
        self.assertEqual(cisco_contract.contract_type, "Hardware")
        self.assertEqual(cisco_contract.comments, "Cisco gave us discount")

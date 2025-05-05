"""Test forms."""

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from nautobot.dcim.models import (
    Device,
    DeviceType,
    InventoryItem,
    Location,
    LocationType,
    Manufacturer,
    Platform,
    SoftwareVersion,
)
from nautobot.extras.models import Role, Status

from nautobot_device_lifecycle_mgmt.forms import CVELCMForm, HardwareLCMForm, ValidatedSoftwareLCMForm
from nautobot_device_lifecycle_mgmt.models import CVELCM


class HardwareLCMFormTest(TestCase):
    """Test class for Device Lifecycle forms."""

    def setUp(self):
        """Create necessary objects."""
        self.manufacturer, _ = Manufacturer.objects.get_or_create(name="Cisco")
        self.device_type, _ = DeviceType.objects.get_or_create(model="c9300-24", manufacturer=self.manufacturer)
        self.devicerole, _ = Role.objects.get_or_create(name="backbone-switch")
        self.devicerole.content_types.add(ContentType.objects.get_for_model(Device))
        location_type_location_a, _ = LocationType.objects.get_or_create(name="LocationA")
        location_type_location_a.content_types.add(
            ContentType.objects.get_for_model(Device),
        )
        active_status, _ = Status.objects.get_or_create(name="Active")
        active_status.content_types.add(ContentType.objects.get_for_model(Location))
        active_status.content_types.add(ContentType.objects.get_for_model(Device))
        self.location1, _ = Location.objects.get_or_create(
            name="Location1", location_type=location_type_location_a, status=active_status
        )
        self.device = Device.objects.create(
            name="Test-9300-Switch",
            device_type=self.device_type,
            role=self.devicerole,
            location=self.location1,
            status=active_status,
        )
        self.inventory_item = InventoryItem.objects.create(
            device=self.device,
            manufacturer=self.manufacturer,
            name="SUP2T Card",
            part_id="VS-S2T-10G",
        )

    def test_specifying_all_fields(self):
        form = HardwareLCMForm(
            data={
                "device_type": self.device_type,
                "end_of_sale": "2021-04-01",
                "end_of_support": "2022-04-01",
                "end_of_sw_releases": "2023-04-01",
                "end_of_security_patches": "2024-04-01",
                "documentation_url": "https://cisco.com",
            }
        )
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_one_of_eo_sale(self):
        form = HardwareLCMForm(data={"device_type": self.device_type, "end_of_sale": "2021-04-01"})
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_one_of_eo_support(self):
        form = HardwareLCMForm(data={"device_type": self.device_type, "end_of_support": "2021-04-01"})
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_required_fields_missing(self):
        form = HardwareLCMForm(
            data={
                "end_of_sale": "2021-04-01",
                "end_of_support": "2022-04-01",
                "end_of_sw_releases": "2023-04-01",
                "end_of_security_patches": "2024-04-01",
                "documentation_url": "https://cisco.com",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertDictEqual(
            {
                "inventory_item": ["One and only one of `Inventory Item` OR `Device Type` must be specified."],
                "device_type": ["One and only one of `Inventory Item` OR `Device Type` must be specified."],
            },
            form.errors,
        )

    def test_eo_sale_support_fields_missing(self):
        form = HardwareLCMForm(data={"device_type": self.device_type})
        self.assertFalse(form.is_valid())
        self.assertIn("End of Sale or End of Support must be specified.", form.errors["end_of_sale"][0])

    def test_device_type_and_inventory_item_error(self):
        form = HardwareLCMForm(data={"device_type": self.device_type, "inventory_item": "VS-S2T-10G"})
        self.assertFalse(form.is_valid())
        self.assertIn(
            "One and only one of `Inventory Item` OR `Device Type` must be specified.", form.errors["inventory_item"][0]
        )

    def test_validation_error_end_of_sale(self):
        form = HardwareLCMForm(data={"device_type": self.device_type, "end_of_sale": "April 1st, 2021"})
        self.assertFalse(form.is_valid())
        self.assertIn("end_of_sale", form.errors)
        self.assertIn("Enter a valid date.", form.errors["end_of_sale"])

    def test_validation_error_end_of_support(self):
        form = HardwareLCMForm(
            data={"device_type": self.device_type, "end_of_sale": "2021-04-01", "end_of_support": "April 1st, 2022"}
        )
        self.assertFalse(form.is_valid())
        self.assertIn("end_of_support", form.errors)
        self.assertIn("Enter a valid date.", form.errors["end_of_support"])

    def test_validation_error_end_of_sw_releases(self):
        form = HardwareLCMForm(
            data={
                "device_type": self.device_type,
                "end_of_sale": "2021-04-01",
                "end_of_support": "2021-04-01",
                "end_of_sw_releases": "April 1st, 2022",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("end_of_sw_releases", form.errors)
        self.assertIn("Enter a valid date.", form.errors["end_of_sw_releases"])

    def test_validation_error_end_of_security_patches(self):
        form = HardwareLCMForm(
            data={
                "device_type": self.device_type,
                "end_of_sale": "2021-04-01",
                "end_of_support": "2022-04-01",
                "end_of_sw_releases": "2023-04-01",
                "end_of_security_patches": "April 1st, 2022",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("end_of_security_patches", form.errors)
        self.assertIn("Enter a valid date.", form.errors["end_of_security_patches"])

    def test_validation_error_documentation_url(self):
        form = HardwareLCMForm(
            data={
                "device_type": self.device_type,
                "end_of_sale": "2021-04-01",
                "end_of_support": "2022-04-01",
                "end_of_sw_releases": "2023-04-01",
                "end_of_security_patches": "2024-04-01",
                "documentation_url": "htttps://cisco.com",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("documentation_url", form.errors)
        self.assertIn("Enter a valid URL.", form.errors["documentation_url"])


class ValidatedSoftwareLCMFormTest(TestCase):  # pylint: disable=no-member
    """Test class for ValidatedSoftwareLCMForm forms."""

    form_class = ValidatedSoftwareLCMForm

    def setUp(self):
        """Create necessary objects."""
        device_platform, _ = Platform.objects.get_or_create(name="cisco_ios")
        active_status, _ = Status.objects.get_or_create(name="Active")
        active_status.content_types.add(ContentType.objects.get_for_model(SoftwareVersion))
        active_status.content_types.add(ContentType.objects.get_for_model(Device))
        active_status.content_types.add(ContentType.objects.get_for_model(Location))
        self.software = SoftwareVersion.objects.create(
            **{
                "platform": device_platform,
                "version": "17.3.3 MD",
                "alias": "Amsterdam-17.3.3 MD",
                "end_of_support_date": "2022-05-15",
                "documentation_url": "https://www.cisco.com/c/en/us/support/ios-nx-os-software/ios-15-4m-t/series.html",
                "long_term_support": True,
                "pre_release": False,
                "status": active_status,
            }
        )

        manufacturer, _ = Manufacturer.objects.get_or_create(name="Cisco")
        location_type_location_a, _ = LocationType.objects.get_or_create(name="LocationA")
        location_type_location_a.content_types.add(
            ContentType.objects.get_for_model(Device),
        )
        location1, _ = Location.objects.get_or_create(
            name="Location1", location_type=location_type_location_a, status=active_status
        )
        devicerole, _ = Role.objects.get_or_create(name="router")
        self.devicetype_1, _ = DeviceType.objects.get_or_create(manufacturer=manufacturer, model="ASR-1000")
        self.device_1 = Device.objects.create(
            device_type=self.devicetype_1, role=devicerole, name="Device 1", location=location1, status=active_status
        )
        self.inventoryitem_1 = InventoryItem.objects.create(device=self.device_1, name="SwitchModule1")

    def test_specifying_all_fields_w_devices(self):
        data = {
            "software": self.software,
            "devices": [self.device_1],
            "start": "2021-06-06",
            "end": "2023-08-31",
            "preferred": False,
        }
        form = self.form_class(data)
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_specifying_all_fields_w_device_type(self):
        data = {
            "software": self.software,
            "device_types": [self.devicetype_1],
            "start": "2021-06-06",
            "end": "2023-08-31",
            "preferred": False,
        }
        form = self.form_class(data)
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_specifying_all_fields_w_inventory_item_type(self):
        data = {
            "software": self.software,
            "inventory_items": [self.inventoryitem_1],
            "start": "2021-06-06",
            "end": "2023-08-31",
            "preferred": False,
        }
        form = self.form_class(data)
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_software_missing(self):
        data = {
            "end": "2023-08-31",
            "preferred": False,
        }
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertIn("software", form.errors)
        self.assertSequenceEqual(["This field is required."], form.errors["software"])

    def test_validation_error_start(self):
        data = {
            "software": self.software,
            "devices": [self.device_1],
            "start": "2020 May 15th",
        }
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertIn("start", form.errors)
        self.assertIn("Enter a valid date.", form.errors["start"])

    def test_validation_error_end(self):
        data = {
            "software": self.software,
            "devices": [self.device_1],
            "start": "2021-06-06",
            "end": "2024 June 2nd",
        }
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertIn("end", form.errors)
        self.assertIn("Enter a valid date.", form.errors["end"])

    def test_assigned_to_must_specify_at_least_one_object(self):
        """ValidatedSoftwareLCM must be assigned to at least one object."""
        data = {
            "software": self.software,
            "start": "2021-06-06",
        }
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            "You need to assign to at least one object.",
            form.errors["__all__"][0],
        )


class CVELCMFormTest(TestCase):
    """Test class for Device Lifecycle forms."""

    def setUp(self):
        """Create necessary objects."""
        self.cve_ct = ContentType.objects.get_for_model(CVELCM)
        self.status = Status.objects.create(name="Fixed", color="4caf50", description="Unit has been fixed")
        self.status.content_types.set([self.cve_ct])

    def test_specifying_all_fields(self):
        form = CVELCMForm(
            data={
                "name": "CVE-2021-34699",
                "published_date": "2021-09-23",
                "link": "https://www.cvedetails.com/cve/CVE-2021-34699/",
                "status": self.status,
                "description": "Thanos",
                "severity": "High",
                "cvss": 6.8,
                "cvss_v2": 6.9,
                "cvss_v3": 6.7,
                "fix": "Avengers",
                "comments": "This is very bad juju.",
            }
        )
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_required_fields_missing(self):
        form = CVELCMForm(data={"name": "CVE-2022-0002"})
        self.assertFalse(form.is_valid())
        self.assertDictEqual(
            {
                "published_date": ["This field is required."],
                "link": ["This field is required."],
            },
            form.errors,
        )

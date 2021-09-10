"""Test forms."""
from django.test import TestCase

from nautobot.dcim.models import DeviceType, Manufacturer, Device, DeviceRole, Site, InventoryItem, Platform
from nautobot.extras.models import Status

from nautobot_device_lifecycle_mgmt.forms import HardwareLCMForm, SoftwareLCMForm, ValidatedSoftwareLCMForm
from nautobot_device_lifecycle_mgmt.models import SoftwareLCM


class HardwareLCMFormTest(TestCase):
    """Test class for Device Lifecycle forms."""

    def setUp(self):
        """Create necessary objects."""
        self.manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        self.device_type = DeviceType.objects.create(model="c9300-24", slug="c9300-24", manufacturer=self.manufacturer)
        self.device_role = DeviceRole.objects.create(name="Backbone Switch", slug="backbone-switch")
        self.site = Site.objects.create(name="Test 1", slug="test-1")
        self.device = Device.objects.create(
            name="Test-9300-Switch",
            device_type=self.device_type,
            device_role=self.device_role,
            site=self.site,
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


class SoftwareLCMFormTest(TestCase):  # pylint: disable=no-member
    """Test class for SoftwareLCM forms."""

    form_class = SoftwareLCMForm

    def setUp(self):
        """Create necessary objects."""
        self.device_platform = Platform.objects.create(name="Cisco IOS", slug="cisco_ios")

    def test_specifying_all_fields(self):
        data = {
            "device_platform": self.device_platform,
            "version": "17.3.3 MD",
            "alias": "Amsterdam-17.3.3 MD",
            "end_of_support": "2022-05-15",
            "documentation_url": "https://www.cisco.com/c/en/us/support/ios-nx-os-software/ios-15-4m-t/series.html",
            "download_url": "ftp://device-images.local.com/cisco/asr1001x-universalk9.17.03.03.SPA.bin",
            "image_file_name": "asr1001x-universalk9.17.03.03.SPA.bin",
            "image_file_checksum": "9cf2e09b59207a4d8ea40886fbbe5b4b68e19e58a8f96b34240e4cea9971f6ae6facab9a1855a34e1ed8755f3ffe4c969cf6e6ef1df95d42a91540a44d4b9e14",
            "long_term_support": True,
            "pre_release": False,
        }
        form = self.form_class(data)
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_one_of_eo_support(self):
        data = {"device_platform": self.device_platform, "version": "17.3.3 MD", "end_of_support": "2022-05-15"}
        form = self.form_class(data)
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_required_fields_missing(self):
        data = {
            "end_of_support": "2022-05-15",
            "documentation_url": "https://www.cisco.com/c/en/us/support/ios-nx-os-software/ios-15-4m-t/series.html",
            "download_url": "ftp://device-images.local.com/cisco/asr1001x-universalk9.17.03.03.SPA.bin",
            "image_file_name": "asr1001x-universalk9.17.03.03.SPA.bin",
        }
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertDictEqual(
            {"device_platform": ["This field is required."], "version": ["This field is required."]},
            form.errors,
        )

    def test_validation_error_end_of_support(self):
        data = {"device_platform": self.device_platform, "version": "17.3.3 MD", "end_of_support": "2022 May 5th"}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertIn("end_of_support", form.errors)
        self.assertIn("Enter a valid date.", form.errors["end_of_support"])

    def test_validation_error_documentation_url(self):
        data = {
            "device_platform": self.device_platform,
            "version": "17.3.3 MD",
            "end_of_support": "2022-05-15",
            "documentation_url": "httpss://www.cisco.com/",
        }
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertIn("documentation_url", form.errors)
        self.assertIn("Enter a valid URL.", form.errors["documentation_url"])

    def test_validation_error_download_url(self):
        data = {
            "device_platform": self.device_platform,
            "version": "17.3.3 MD",
            "end_of_support": "2022-05-15",
            "download_url": "ftppp://images.local.my.org/",
        }
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertIn("download_url", form.errors)
        self.assertIn("Enter a valid URL.", form.errors["download_url"])


class ValidatedSoftwareLCMFormTest(TestCase):  # pylint: disable=no-member
    """Test class for ValidatedSoftwareLCMForm forms."""

    form_class = ValidatedSoftwareLCMForm

    def setUp(self):
        """Create necessary objects."""
        device_platform = Platform.objects.create(name="Cisco IOS", slug="cisco_ios")
        self.software = SoftwareLCM.objects.create(
            **{
                "device_platform": device_platform,
                "version": "17.3.3 MD",
                "alias": "Amsterdam-17.3.3 MD",
                "end_of_support": "2022-05-15",
                "documentation_url": "https://www.cisco.com/c/en/us/support/ios-nx-os-software/ios-15-4m-t/series.html",
                "download_url": "ftp://device-images.local.com/cisco/asr1001x-universalk9.17.03.03.SPA.bin",
                "image_file_name": "asr1001x-universalk9.17.03.03.SPA.bin",
                "image_file_checksum": "9cf2e09b59207a4d8ea40886fbbe5b4b68e19e58a8f96b34240e4cea9971f6ae6facab9a1855a34e1ed8755f3ffe4c969cf6e6ef1df95d42a91540a44d4b9e14",
                "long_term_support": True,
                "pre_release": False,
            }
        )

        status_active = Status.objects.get(slug="active")
        manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        site = Site.objects.create(name="Site 1", slug="site-1")
        devicerole = DeviceRole.objects.create(name="Router", slug="router", color="ff0000")
        self.devicetype_1 = DeviceType.objects.create(manufacturer=manufacturer, model="ASR-1000", slug="asr-1000")
        self.device_1 = Device.objects.create(
            device_type=self.devicetype_1, device_role=devicerole, name="Device 1", site=site, status=status_active
        )
        self.inventoryitem_1 = InventoryItem.objects.create(device=self.device_1, name="SwitchModule1")

    def test_specifying_all_fields_w_device(self):
        data = {
            "software": self.software,
            "assigned_to_device": self.device_1,
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
            "assigned_to_device_type": self.devicetype_1,
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
            "assigned_to_inventory_item": self.inventoryitem_1,
            "start": "2021-06-06",
            "end": "2023-08-31",
            "preferred": False,
        }
        form = self.form_class(data)
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_required_fields_missing(self):
        data = {
            "end": "2023-08-31",
            "preferred": False,
        }
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertDictEqual(
            {
                "__all__": ["A device, device type or inventory item must be selected."],
                "software": ["This field is required."],
                "start": ["This field is required."],
            },
            form.errors,
        )

    def test_validation_error_start(self):
        data = {
            "software": self.software,
            "assigned_to_device": self.device_1,
            "start": "2020 May 15th",
        }
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertIn("start", form.errors)
        self.assertIn("Enter a valid date.", form.errors["start"])

    def test_validation_error_end(self):
        data = {
            "software": self.software,
            "assigned_to_device": self.device_1,
            "start": "2021-06-06",
            "end": "2024 June 2nd",
        }
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertIn("end", form.errors)
        self.assertIn("Enter a valid date.", form.errors["end"])

    def test_assigned_to_cannot_be_more_than_one(self):
        """Assigned to cannot be more than one of Device, DeviceType or InventoryItem"""
        data = {
            "software": self.software,
            "assigned_to_device": self.device_1,
            "assigned_to_device_type": self.devicetype_1,
            "assigned_to_inventory_item": self.inventoryitem_1,
            "start": "2021-06-06",
        }
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            "Cannot assign to more than one object. Choose either device, device type or inventory item.",
            form.errors["__all__"][0],
        )

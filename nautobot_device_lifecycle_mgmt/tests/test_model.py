"""nautobot_device_lifecycle_mgmt test class for models."""
from datetime import date
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

import time_machine

from nautobot.dcim.models import DeviceType, Manufacturer, Platform

from nautobot_device_lifecycle_mgmt.models import HardwareLCM, SoftwareLCM, ValidatedSoftwareLCM


class TestModelBasic(TestCase):
    """Tests for the HardwareLCM models."""

    def setUp(self):
        """Set up base objects."""
        self.manufacturer = Manufacturer.objects.create(name="Cisco")
        self.device_type = DeviceType.objects.create(model="c9300-24", slug="c9300-24", manufacturer=self.manufacturer)

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
        self.device_platform = Platform.objects.create(name="Cisco IOS", slug="cisco_ios")

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
            download_url="ftp://device-images.local.com/cisco/asr1001x-universalk9.17.03.03.SPA.bin",
            image_file_name="asr1001x-universalk9.17.03.03.SPA.bin",
            image_file_checksum="9cf2e09b59207a4d8ea40886fbbe5b4b68e19e58a8f96b34240e4cea9971f6ae6facab9a1855a34e1ed8755f3ffe4c969cf6e6ef1df95d42a91540a44d4b9e14",
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
        self.assertEqual(
            softwarelcm_full.download_url, "ftp://device-images.local.com/cisco/asr1001x-universalk9.17.03.03.SPA.bin"
        )
        self.assertEqual(softwarelcm_full.image_file_name, "asr1001x-universalk9.17.03.03.SPA.bin")
        self.assertEqual(
            softwarelcm_full.image_file_checksum,
            "9cf2e09b59207a4d8ea40886fbbe5b4b68e19e58a8f96b34240e4cea9971f6ae6facab9a1855a34e1ed8755f3ffe4c969cf6e6ef1df95d42a91540a44d4b9e14",
        )
        self.assertEqual(softwarelcm_full.long_term_support, False)
        self.assertEqual(softwarelcm_full.pre_release, True)
        self.assertEqual(str(softwarelcm_full), f"{self.device_platform.name} - {softwarelcm_full.version}")


class ValidatedSoftwareLCMTestCase(TestCase):
    """Tests for the ValidatedSoftwareLCM model."""

    def setUp(self):
        """Set up base objects."""
        device_platform = Platform.objects.create(name="Cisco IOS", slug="cisco_ios")
        self.software = SoftwareLCM.objects.create(
            device_platform=device_platform,
            version="17.3.3 MD",
            release_date=date(2019, 1, 10),
        )
        manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        self.device_type_1 = DeviceType.objects.create(manufacturer=manufacturer, model="ASR-1000", slug="asr-1000")
        self.device_type_2 = DeviceType.objects.create(manufacturer=manufacturer, model="CAT-3750", slug="cat-3750")
        self.content_type_devicetype = ContentType.objects.get(app_label="dcim", model="devicetype")

    def test_create_validatedsoftwarelcm_required_only(self):
        """Successfully create ValidatedSoftwareLCM with required fields only."""

        validatedsoftwarelcm = ValidatedSoftwareLCM.objects.create(
            software=self.software,
            start=date(2019, 1, 10),
            assigned_to_content_type=self.content_type_devicetype,
            assigned_to_object_id=self.device_type_1.id,
        )

        self.assertEqual(validatedsoftwarelcm.software, self.software)
        self.assertEqual(str(validatedsoftwarelcm.start), "2019-01-10")
        self.assertEqual(validatedsoftwarelcm.assigned_to, self.device_type_1)

    def test_create_validatedsoftwarelcm_all(self):
        """Successfully create ValidatedSoftwareLCM with all fields."""
        validatedsoftwarelcm = ValidatedSoftwareLCM.objects.create(
            software=self.software,
            start=date(2020, 4, 15),
            end=date(2022, 11, 1),
            preferred=False,
            assigned_to_content_type=self.content_type_devicetype,
            assigned_to_object_id=self.device_type_1.id,
        )

        self.assertEqual(validatedsoftwarelcm.software, self.software)
        self.assertEqual(str(validatedsoftwarelcm.start), "2020-04-15")
        self.assertEqual(str(validatedsoftwarelcm.end), "2022-11-01")
        self.assertEqual(validatedsoftwarelcm.assigned_to, self.device_type_1)
        self.assertEqual(validatedsoftwarelcm.preferred, False)
        self.assertEqual(str(validatedsoftwarelcm), f"{self.software} - Valid since: {validatedsoftwarelcm.start}")

    def test_validatedsoftwarelcm_valid_property(self):
        """Test behavior of the 'valid' property."""
        validatedsoftwarelcm_start_only = ValidatedSoftwareLCM.objects.create(
            software=self.software,
            start=date(2020, 4, 15),
            preferred=False,
            assigned_to_content_type=self.content_type_devicetype,
            assigned_to_object_id=self.device_type_1.id,
        )
        validatedsoftwarelcm_start_end = ValidatedSoftwareLCM.objects.create(
            software=self.software,
            start=date(2020, 4, 15),
            end=date(2022, 11, 1),
            preferred=False,
            assigned_to_content_type=self.content_type_devicetype,
            assigned_to_object_id=self.device_type_2.id,
        )

        date_valid = date(2021, 6, 11)
        date_before_valid_start = date(2018, 9, 26)
        date_after_valid_end = date(2023, 1, 4)

        with time_machine.travel(date_valid):
            self.assertEqual(validatedsoftwarelcm_start_only.valid, True)
            self.assertEqual(validatedsoftwarelcm_start_end.valid, True)

        with time_machine.travel(date_before_valid_start):
            self.assertEqual(validatedsoftwarelcm_start_only.valid, False)
            self.assertEqual(validatedsoftwarelcm_start_end.valid, False)

        with time_machine.travel(date_after_valid_end):
            self.assertEqual(validatedsoftwarelcm_start_only.valid, True)
            self.assertEqual(validatedsoftwarelcm_start_end.valid, False)

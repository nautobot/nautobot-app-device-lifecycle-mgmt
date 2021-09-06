"""Test filters for lifecycle management."""
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from nautobot.dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site, Platform

from nautobot_device_lifecycle_mgmt.models import HardwareLCM, SoftwareLCM, ValidatedSoftwareLCM
from nautobot_device_lifecycle_mgmt.filters import (
    HardwareLCMFilterSet,
    SoftwareLCMFilterSet,
    ValidatedSoftwareLCMFilterSet,
)


class HardwareLCMTestCase(TestCase):
    """Tests for HardwareLCMFilter."""

    queryset = HardwareLCM.objects.all()
    filterset = HardwareLCMFilterSet

    def setUp(self):
        self.manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        self.device_types = (
            DeviceType.objects.create(model="c9300-24", slug="c9300-24", manufacturer=self.manufacturer),
            DeviceType.objects.create(model="c9300-48", slug="c9300-48", manufacturer=self.manufacturer),
        )
        self.device_role = DeviceRole.objects.create(name="Core Switch", slug="core-switch")
        self.site = Site.objects.create(name="Test 1", slug="test-1")
        self.devices = (
            Device.objects.create(
                name="r1",
                device_type=self.device_types[0],
                device_role=self.device_role,
                site=self.site,
            ),
            Device.objects.create(
                name="r2",
                device_type=self.device_types[1],
                device_role=self.device_role,
                site=self.site,
            ),
        )
        self.notices = (
            HardwareLCM.objects.create(
                device_type=self.device_types[0],
                end_of_sale="2022-04-01",
                end_of_support="2023-04-01",
                end_of_sw_releases="2024-04-01",
                end_of_security_patches="2025-04-01",
                documentation_url="https://cisco.com/c9300-24",
            ),
            HardwareLCM.objects.create(
                device_type=self.device_types[1],
                end_of_sale="2024-04-01",
                end_of_support="2025-05-01",
                end_of_sw_releases="2026-05-01",
                end_of_security_patches="2027-05-01",
                documentation_url="https://cisco.com/c9300-48",
            ),
        )

    def test_q_one_eo_sale(self):
        """Test q filter to find single record based on end_of_sale."""
        params = {"q": "2022"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_one_eo_support(self):
        """Test q filter to find single record based on end_of_support."""
        params = {"q": "2024"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_both_eo_sale_support(self):
        """Test q filter to both records."""
        params = {"q": "04-01"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_eo_sale(self):
        """Test end_of_sale filter."""
        params = {"end_of_sale": "2022-04-01"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_eo_support(self):
        """Test end_of_support filter."""
        params = {"end_of_support": "2025-05-01"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_eo_sw_releases(self):
        """Test end_of_sw_releases filter."""
        params = {"end_of_sw_releases": "2024-04-01"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_eo_security_patches(self):
        """Test end_of_security_patches filter."""
        params = {"end_of_security_patches": "2027-05-01"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_documentation_url(self):
        """Test notice filter."""
        params = {"documentation_url": "https://cisco.com/c9300-48"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_device_type_slug_single(self):
        """Test device_type filter."""
        params = {"device_type": ["c9300-24"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_device_types_slug_all(self):
        """Test device_type filter."""
        params = {"device_type": ["c9300-24", "c9300-48"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device_types_id_single(self):
        """Test device_type_id filter."""
        params = {"device_type_id": [self.device_types[0].id]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_device_types_id_all(self):
        """Test device_type_id filter."""
        params = {"device_type_id": [self.device_types[0].id, self.device_types[1].id]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_devices_name_all(self):
        """Test devices filter."""
        params = {"devices": ["r1", "r2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device_id_all(self):
        """Test device_id filter."""
        params = {"device_id": [self.devices[0].id, self.devices[1].id]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class SoftwareLCMFilterSetTestCase(TestCase):
    """Tests for SoftwareLCMFilterSet."""

    queryset = SoftwareLCM.objects.all()
    filterset = SoftwareLCMFilterSet

    def setUp(self):
        device_platforms = (
            Platform.objects.create(name="Cisco IOS", slug="cisco_ios"),
            Platform.objects.create(name="Arista EOS", slug="arista_eos"),
        )

        self.softwares = (
            SoftwareLCM.objects.create(
                device_platform=device_platforms[0],
                version="17.3.3 MD",
                alias="Amsterdam-17.3.3 MD",
                release_date="2019-01-10",
                end_of_support="2022-05-15",
                documentation_url="https://www.cisco.com/c/en/us/support/ios-nx-os-software/ios-15-4m-t/series.html",
                download_url="ftp://device-images.local.com/cisco/asr1001x-universalk9.17.03.03.SPA.bin",
                image_file_name="asr1001x-universalk9.17.03.03.SPA.bin",
                image_file_checksum="9cf2e09b59207a4d8ea40886fbbe5b4b68e19e58a8f96b34240e4cea9971f6ae6facab9a1855a34e1ed8755f3ffe4c969cf6e6ef1df95d42a91540a44d4b9e14",
                long_term_support=False,
                pre_release=True,
            ),
            SoftwareLCM.objects.create(
                device_platform=device_platforms[1],
                version="4.25M",
                alias="EOS 4.25M",
                release_date="2021-01-10",
                end_of_support="2026-05-13",
                documentation_url="https://www.arista.com/softdocs",
                download_url="ftp://device-images.local.com/arista/arista-4.25m.img",
                image_file_name="arista-4.25m.img",
                image_file_checksum="34e61320b5518a2954b2a307b7e6a018",
                long_term_support=True,
                pre_release=False,
            ),
        )

    def test_q_one_release_date(self):
        """Test q filter to find single record based on release_date."""
        params = {"q": "2021"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_one_eo_support(self):
        """Test q filter to find single record based on end_of_support."""
        params = {"q": "2022"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_one_version(self):
        """Test q filter to find single record based on version."""
        params = {"q": "4.25M"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_documentation_url(self):
        """Test documentation_url filter."""
        params = {"documentation_url": "https://www.arista.com/softdocs"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_download_url(self):
        """Test download_url filter."""
        params = {"download_url": "ftp://device-images.local.com/arista/arista-4.25m.img"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_image_file_name(self):
        """Test image_file_name filter."""
        params = {"image_file_name": "asr1001x-universalk9.17.03.03.SPA.bin"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_image_file_checksum(self):
        """Test image_file_checksum filter."""
        params = {"image_file_checksum": "34e61320b5518a2954b2a307b7e6a018"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_long_term_support(self):
        """Test long_term_support filter."""
        params = {"long_term_support": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_pre_release(self):
        """Test pre_release filter."""
        params = {"pre_release": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)


class ValidatedSoftwareLCMFilterSetTestCase(TestCase):
    """Tests for ValidatedSoftwareLCMFilterSet."""

    queryset = ValidatedSoftwareLCM.objects.all()
    filterset = ValidatedSoftwareLCMFilterSet

    def setUp(self):
        device_platforms = (
            Platform.objects.create(name="Cisco IOS", slug="cisco_ios"),
            Platform.objects.create(name="Arista EOS", slug="arista_eos"),
        )

        self.softwares = (
            SoftwareLCM.objects.create(
                device_platform=device_platforms[0],
                version="17.3.3 MD",
                release_date="2019-01-10",
            ),
            SoftwareLCM.objects.create(
                device_platform=device_platforms[1],
                version="4.25M",
                release_date="2021-01-10",
            ),
        )

        manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model="ASR-1000", slug="asr-1000")
        content_type_devicetype = ContentType.objects.get(app_label="dcim", model="devicetype")

        self.validated_softwares = (
            ValidatedSoftwareLCM.objects.create(
                software=self.softwares[0],
                start="2019-01-10",
                end="2023-05-14",
                preferred=True,
                assigned_to_content_type=content_type_devicetype,
                assigned_to_object_id=device_type.id,
            ),
            ValidatedSoftwareLCM.objects.create(
                software=self.softwares[1],
                start="2020-04-15",
                end="2022-11-01",
                preferred=False,
                assigned_to_content_type=content_type_devicetype,
                assigned_to_object_id=device_type.id,
            ),
        )

    def test_q_one_start(self):
        """Test q filter to find single record based on start date."""
        params = {"q": "2019"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_one_end(self):
        """Test q filter to find single record based on end date."""
        params = {"q": "2022"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_software(self):
        """Test software filter."""
        params = {"software": [self.softwares[0].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_preferred(self):
        """Test preferred filter."""
        params = {"preferred": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

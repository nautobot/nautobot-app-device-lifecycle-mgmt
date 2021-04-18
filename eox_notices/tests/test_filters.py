"""Test filters for eox notices."""

from django.test import TestCase

from nautobot.dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site

from eox_notices.models import EoxNotice
from eox_notices.filters import EoxNoticeFilter


class EoxNoticeTestCase(TestCase):
    """Tests for EoxNoticeFilter."""

    queryset = EoxNotice.objects.all()
    filterset = EoxNoticeFilter

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
                name="r1", device_type=self.device_types[0], device_role=self.device_role, site=self.site,
            ),
            Device.objects.create(
                name="r2", device_type=self.device_types[1], device_role=self.device_role, site=self.site,
            ),
        )
        self.notices = (
            EoxNotice.objects.create(
                device_type=self.device_types[0],
                end_of_sale="2022-04-01",
                end_of_support="2023-04-01",
                end_of_sw_releases="2024-04-01",
                end_of_security_patches="2025-04-01",
                notice_url="https://cisco.com/c9300-24",
            ),
            EoxNotice.objects.create(
                device_type=self.device_types[1],
                end_of_sale="2024-04-01",
                end_of_support="2025-05-01",
                end_of_sw_releases="2026-05-01",
                end_of_security_patches="2027-05-01",
                notice_url="https://cisco.com/c9300-48",
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

    def test_notice_url(self):
        """Test notice filter."""
        params = {"notice_url": "https://cisco.com/c9300-48"}
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

    def test_devices_name_single(self):
        """Test devices filter."""
        params = {"devices": ["r1"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_devices_name_all(self):
        """Test devices filter."""
        params = {"devices": ["r1", "r2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device_id_single(self):
        """Test device_id filter."""
        params = {"device_id": [self.devices[0].id]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_device_id_all(self):
        """Test device_id filter."""
        params = {"device_id": [self.devices[0].id, self.devices[1].id]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

# pylint: disable=no-member,too-many-lines
"""Test filters for lifecycle management."""

from datetime import date, datetime, timedelta

import time_machine
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from nautobot.dcim.models import Device, DeviceType, Location, LocationType, Manufacturer, Platform, SoftwareVersion
from nautobot.extras.models import Role, Status

from nautobot_device_lifecycle_mgmt.choices import ContractTypeChoices, CurrencyChoices, CVESeverityChoices
from nautobot_device_lifecycle_mgmt.filters import (
    ContractLCMFilterSet,
    CVELCMFilterSet,
    DeviceHardwareNoticeResultFilterSet,
    DeviceSoftwareValidationResultFilterSet,
    HardwareLCMFilterSet,
    InventoryItemSoftwareValidationResultFilterSet,
    ProviderLCMFilterSet,
    ValidatedSoftwareLCMFilterSet,
    VulnerabilityLCMFilterSet,
)
from nautobot_device_lifecycle_mgmt.models import (
    CVELCM,
    ContractLCM,
    DeviceHardwareNoticeResult,
    DeviceSoftwareValidationResult,
    HardwareLCM,
    InventoryItemSoftwareValidationResult,
    ProviderLCM,
    ValidatedSoftwareLCM,
    VulnerabilityLCM,
)

from .conftest import create_cves, create_devices, create_inventory_items, create_softwares


class HardwareLCMTestCase(TestCase):
    """Tests for HardwareLCMFilter."""

    queryset = HardwareLCM.objects.all()
    filterset = HardwareLCMFilterSet

    def setUp(self):
        self.manufacturer, _ = Manufacturer.objects.get_or_create(name="Cisco")
        self.device_types = (
            DeviceType.objects.get_or_create(model="c9300-24", manufacturer=self.manufacturer)[0],
            DeviceType.objects.get_or_create(model="c9300-48", manufacturer=self.manufacturer)[0],
            DeviceType.objects.get_or_create(model="c9300-16", manufacturer=self.manufacturer)[0],
        )
        self.devicerole, _ = Role.objects.get_or_create(name="switch", color="ff0000")
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
        self.devices = (
            Device.objects.create(
                name="r1",
                device_type=self.device_types[0],
                role=self.devicerole,
                location=self.location1,
                status=active_status,
            ),
            Device.objects.create(
                name="r2",
                device_type=self.device_types[1],
                role=self.devicerole,
                location=self.location1,
                status=active_status,
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
                end_of_sale="2020-04-01",
                end_of_support="2021-05-01",
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
        """Test q filter to find single record based on end_of_security_patches."""
        params = {"q": "2027"}
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
        params = {"end_of_support": "2021-05-01"}
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

    def test_device_type_name_single(self):
        """Test device_type filter."""
        params = {"device_type_model": ["c9300-24"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_device_types_name_all(self):
        """Test device_type filter."""
        params = {"device_type_model": ["c9300-24", "c9300-48"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device_types_id_single(self):
        """Test device_type_id filter."""
        params = {"device_type": [self.device_types[0].id]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_device_types_id_all(self):
        """Test device_type_id filter."""
        params = {"device_type": [self.device_types[0].id, self.device_types[1].id]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_devices_name_all(self):
        """Test devices filter."""
        params = {"devices": ["r1", "r2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device_id_all(self):
        """Test device_id filter."""
        params = {"device_id": [self.devices[0].id, self.devices[1].id]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_expired_search(self):
        """Test returned devices are either end of sale or end of support."""
        test_year = (datetime.today() + timedelta(days=365)).year
        test_month = datetime.today().month
        test_day = datetime.today().day

        HardwareLCM.objects.get_or_create(
            device_type=self.device_types[2],
            end_of_sale=f"{test_year}-{test_month}-{test_day}",
            end_of_support=f"{test_year}-{test_month}-{test_day}",
        )
        params = {"expired": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class ContractLCMTestCase(TestCase):
    """Tests for ContractLCMFilter."""

    queryset = ContractLCM.objects.all()
    filterset = ContractLCMFilterSet

    def setUp(self):
        self.manufacturer, _ = Manufacturer.objects.get_or_create(name="Cisco")
        self.device_types = (
            DeviceType.objects.get_or_create(model="c9300-24", manufacturer=self.manufacturer)[0],
            DeviceType.objects.get_or_create(model="c9300-48", manufacturer=self.manufacturer)[0],
            DeviceType.objects.get_or_create(model="c9300-16", manufacturer=self.manufacturer)[0],
        )
        self.devicerole, _ = Role.objects.get_or_create(name="switch", color="ff0000")
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
        self.devices = (
            Device.objects.get_or_create(
                name="r1",
                device_type=self.device_types[0],
                role=self.devicerole,
                location=self.location1,
                status=active_status,
            )[0],
            Device.objects.get_or_create(
                name="r2",
                device_type=self.device_types[1],
                role=self.devicerole,
                location=self.location1,
                status=active_status,
            )[0],
        )
        self.providers = (
            ProviderLCM.objects.get_or_create(
                name="Test Vendor 1",
                description="this vendor supplies routers",
                physical_address="123 vendor 1 street",
                country="USA",
                phone="123-4567",
                email="vendor1@email.com",
                portal_url="https://vendor1.portal.net",
                comments="123-abc unique comment about vendor 1",
            )[0],
            ProviderLCM.objects.get_or_create(
                name="Test Vendor 2",
                description="this vendor supplies switches",
                physical_address="ABC vendor 2 street",
                country="CAN",
                phone="555-1234",
                email="vendor2@email.com",
                portal_url="https://vendor2.portal.net",
                comments="456-xyz unique comment about vendor 2",
            )[0],
        )
        self.contracts = (
            ContractLCM.objects.get_or_create(
                provider=self.providers[0],
                name="Contract 123456789-A",
                number=123456789 - 111,
                start="2020-01-01",
                end="2020-12-31",
                cost=100,
                support_level="high",
                currency=CurrencyChoices.USD,
                contract_type=ContractTypeChoices.HARDWARE,
                comments="ABCDEF-A unique comment about contract 1",
            )[0],
            ContractLCM.objects.get_or_create(
                provider=self.providers[1],
                name="Contract 987654321-Z",
                number=987654321 - 222,
                start="2022-02-01",
                end="2023-01-31",
                cost=200,
                support_level="low",
                currency=CurrencyChoices.CAD,
                contract_type=ContractTypeChoices.SOFTWARE,
                comments="FEDCBA-Z unique comment about contract 1",
            )[0],
        )
        self.contracts[0].devices.add(self.devices[0])
        self.contracts[0].save()
        self.contracts[1].devices.add(self.devices[1])
        self.contracts[1].save()

    def test_q_name(self):
        """Test q filter to find single record based on name."""
        params = {"q": "123456789-A"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_number(self):
        """Test q filter to find single record based on number"""
        params = {"q": 123456789 - 111}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_devices_one(self):
        """Test devices filter to find single record based on device id"""
        params = {"devices": [self.devices[0].id]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_devices_two(self):
        """Test devices filter to find multiple records based on device id"""
        params = {"devices": [self.devices[0].id, self.devices[1].id]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_provider_one(self):
        """Test providers filter to find single record based on provider id"""
        params = {"provider": ["Test Vendor 1"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_provider_two(self):
        """Test providers filter to find multiple records based on provider id"""
        params = {"provider": ["Test Vendor 1", "Test Vendor 2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_name(self):
        """Test name filter."""
        params = {"name": "Contract 123456789-A"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_start(self):
        """Test start filter."""
        params = {"start": "2020-01-01"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_end(self):
        """Test end filter."""
        params = {"end": "2020-12-31"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_cost(self):
        """Test cost filter."""
        params = {"cost": 100}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_support_level(self):
        """Test support level filter."""
        params = {"support_level": "high"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_contract_type(self):
        """Test contract type filter."""
        params = {"contract_type": "Hardware"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_expired(self):
        """Test exipired filter."""
        test_year = (datetime.today() + timedelta(days=365)).year
        test_month = datetime.today().month
        test_day = datetime.today().day

        ContractLCM.objects.get_or_create(
            provider=self.providers[0],
            name="Contract is Valid",
            number=123,
            start="2019-01-01",
            end=f"{test_year}-{test_month}-{test_day}",
            comments="Contract is Valid",
        )
        params = {"expired": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class ProviderLCMTestCase(TestCase):
    """Tests for ProviderLCMFilter."""

    queryset = ProviderLCM.objects.all()
    filterset = ProviderLCMFilterSet

    def setUp(self):
        self.providers = (
            ProviderLCM.objects.get_or_create(
                name="Test Vendor 1",
                description="this vendor supplies routers",
                physical_address="123 vendor 1 street",
                country="USA",
                phone="123-4567",
                email="vendor1@email.com",
                portal_url="https://vendor1.portal.net",
                comments="123-abc unique comment about vendor 1",
            )[0],
            ProviderLCM.objects.get_or_create(
                name="Test Vendor 2",
                description="this vendor supplies switches",
                physical_address="ABC vendor 2 street",
                country="CAN",
                phone="555-1234",
                email="vendor2@email.com",
                portal_url="https://vendor2.portal.net",
                comments="456-xyz unique comment about vendor 2",
            )[0],
        )

    def test_q_name(self):
        """Test q filter to find single record based on name."""
        params = {"q": "Test Vendor 1"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_description(self):
        """Test q filter to find single record based on description"""
        params = {"q": "routers"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_physical_address(self):
        """Test q filter to find single record based on physical address"""
        params = {"q": "123 vendor 1"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_country(self):
        """Test q filter to find single record based on country"""
        params = {"q": "USA"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_phone(self):
        """Test q filter to find single record based on phone"""
        params = {"q": "123-4567"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_email(self):
        """Test q filter to find single record based on email"""
        params = {"q": "vendor1@"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_comments(self):
        """Test q filter to find single record based on comments"""
        params = {"q": "123-abc"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_portal_url(self):
        """Test q filter to find single record based on portal_url"""
        params = {"q": "vendor2.portal.net"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        """Test name filter."""
        params = {"name": "Test Vendor 2"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_country(self):
        """Test country filter."""
        params = {"country": "USA"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_phone(self):
        """Test phone filter."""
        params = {"phone": "555-1234"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_email(self):
        """Test email filter."""
        params = {
            "email": "vendor1@email.com",
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_portal_url(self):
        """Test portal url filter."""
        params = {"portal_url": "https://vendor1.portal.net"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)


class ValidatedSoftwareLCMFilterSetTestCase(TestCase):
    """Tests for ValidatedSoftwareLCMFilterSet."""

    queryset = ValidatedSoftwareLCM.objects.all()
    filterset = ValidatedSoftwareLCMFilterSet

    def setUp(self):
        device_role_router, _ = Role.objects.get_or_create(name="router")
        device_role_router.content_types.add(ContentType.objects.get_for_model(Device))
        device_platforms = (
            Platform.objects.get_or_create(name="cisco_ios")[0],
            Platform.objects.get_or_create(name="arista_eos")[0],
        )

        active_status, _ = Status.objects.get_or_create(name="Active")
        active_status.content_types.add(ContentType.objects.get_for_model(SoftwareVersion))
        self.softwares = (
            SoftwareVersion.objects.create(
                platform=device_platforms[0],
                version="17.3.3 MD",
                release_date="2019-01-10",
                status=active_status,
            ),
            SoftwareVersion.objects.create(
                platform=device_platforms[1],
                version="4.25M",
                release_date="2021-01-10",
                status=active_status,
            ),
        )

        manufacturer, _ = Manufacturer.objects.get_or_create(name="Cisco")
        device_type, _ = DeviceType.objects.get_or_create(manufacturer=manufacturer, model="ASR-1000")

        validated_software = ValidatedSoftwareLCM(
            software=self.softwares[0],
            start="2019-01-10",
            end="2023-05-14",
            preferred=True,
        )
        validated_software.save()
        validated_software.device_types.set([device_type.pk])

        validated_software = ValidatedSoftwareLCM(
            software=self.softwares[1],
            start="2020-04-15",
            end="2022-11-01",
            preferred=False,
        )
        validated_software.save()
        validated_software.device_types.set([device_type.pk])

        validated_software = ValidatedSoftwareLCM(
            software=self.softwares[1],
            start="2020-01-15",
            end="2025-11-01",
            preferred=False,
        )
        validated_software.save()
        validated_software.device_roles.set([device_role_router.pk])

    def test_q_one_start(self):
        """Test q filter to find single record based on start date."""
        params = {"q": "2019"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_one_end(self):
        """Test q filter to find single record based on end date."""
        params = {"q": "2022"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_device_roles_name(self):
        """Test device_roles filter."""
        params = {"device_roles": ["router"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_software(self):
        """Test software filter."""
        params = {"software": [self.softwares[0].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_preferred(self):
        """Test preferred filter."""
        params = {"preferred": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_valid(self):
        """Test valid filter."""
        date_valid_and_invalid = date(2019, 6, 11)
        date_three_valid = date(2021, 1, 4)
        date_two_invalid = date(2024, 1, 4)

        with time_machine.travel(date_valid_and_invalid):
            params = {"valid": True}
            self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
            params = {"valid": False}
            self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

        with time_machine.travel(date_three_valid):
            params = {"valid": True}
            self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
            params = {"valid": False}
            self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)

        with time_machine.travel(date_two_invalid):
            params = {"valid": True}
            self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
            params = {"valid": False}
            self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class DeviceSoftwareValidationResultFilterSetTestCase(TestCase):
    """Tests for the DeviceSoftwareValidationResult model."""

    queryset = DeviceSoftwareValidationResult.objects.all()
    filterset = DeviceSoftwareValidationResultFilterSet

    def setUp(self):
        """Set up test objects."""
        self.device_1, self.device_2, self.device_3 = create_devices()
        self.location = self.device_1.location
        self.platform = Platform.objects.all().first()
        active_status, _ = Status.objects.get_or_create(name="Active")
        active_status.content_types.add(ContentType.objects.get_for_model(SoftwareVersion))
        self.software = SoftwareVersion.objects.create(
            platform=self.platform,
            version="17.3.3 MD",
            release_date="2019-01-10",
            status=active_status,
        )

        DeviceSoftwareValidationResult.objects.create(
            device=self.device_1,
            software=self.software,
            is_validated=True,
        )
        DeviceSoftwareValidationResult.objects.create(
            device=self.device_2,
            software=self.software,
            is_validated=False,
        )
        DeviceSoftwareValidationResult.objects.create(
            device=self.device_3,
            software=None,
            is_validated=False,
        )

    def test_devices_name_one(self):
        """Test devices filter."""
        params = {"device": ["sw1"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_devices_name_all(self):
        """Test devices filter."""
        params = {"device": ["sw1", "sw2", "sw3"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_device_type_name(self):
        """Test device_type filter."""
        params = {"device_type": ["6509-E"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_device_role_name(self):
        """Test device_role filter."""
        params = {"device_role": ["router"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_device_type_id(self):
        """Test device_type_id filter."""
        device_type = DeviceType.objects.get(model="6509-E")
        params = {"device_type_id": [device_type.id]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_device_role_id(self):
        """Test device_role_id filter."""
        device_role = Role.objects.get(name="core-switch")
        params = {"device_role_id": [device_role.id]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device_id_all(self):
        """Test device_id filter."""
        params = {"device_id": [self.device_1.id, self.device_2.id, self.device_3.id]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_software(self):
        """Test software version filter."""
        params = {"software": ["17.3.3 MD"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_sw_missing(self):
        """Test sw_missing filter."""
        params = {"exclude_sw_missing": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_platform(self):
        """Test software version filter."""
        params = {"platform": [self.platform]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_sw_missing_only(self):
        """Test sw_missing filter."""
        params = {"sw_missing_only": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_location(self):
        """Test location filter."""
        params = {"location": [self.location.name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class InventoryItemSoftwareValidationResultFilterSetTestCase(TestCase):
    """Tests for the DeviceSoftwareValidationResult model."""

    queryset = InventoryItemSoftwareValidationResult.objects.all()
    filterset = InventoryItemSoftwareValidationResultFilterSet

    def setUp(self):
        """Set up test objects."""
        self.inventory_items = create_inventory_items()
        self.location = self.inventory_items[0].device.location
        self.platform = Platform.objects.all().first()
        active_status, _ = Status.objects.get_or_create(name="Active")
        active_status.content_types.add(ContentType.objects.get_for_model(SoftwareVersion))
        self.software = SoftwareVersion.objects.create(
            platform=self.platform,
            version="17.3.3 MD",
            release_date="2019-01-10",
            status=active_status,
        )

        InventoryItemSoftwareValidationResult.objects.create(
            inventory_item=self.inventory_items[0],
            software=self.software,
            is_validated=True,
        )
        InventoryItemSoftwareValidationResult.objects.create(
            inventory_item=self.inventory_items[1],
            software=self.software,
            is_validated=False,
        )
        InventoryItemSoftwareValidationResult.objects.create(
            inventory_item=self.inventory_items[2],
            software=None,
            is_validated=False,
        )

    def test_inventory_item_name_one(self):
        """Test inventory items filter."""
        params = {"inventory_item": ["SUP2T Card"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_inventory_items_name_all(self):
        """Test devices filter."""
        params = {"inventory_item": ["SUP2T Card", "100GBASE-SR4 QSFP Transceiver", "48x RJ-45 Line Card"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_inventory_items_device_type_name(self):
        """Test device_type filter."""
        params = {"device_type": ["6509-E"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_inventory_items_device_role_name(self):
        """Test device_role filter."""
        params = {"device_role": ["core-switch"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_inventory_items_device_type_id(self):
        """Test device_type_id filter."""
        device_type = DeviceType.objects.get(model="6509-E")
        params = {"device_type_id": [device_type.id]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_inventory_items_device_role_id(self):
        """Test device_role_id filter."""
        device_role = Role.objects.get(name="core-switch")
        params = {"device_role_id": [device_role.id]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_inventory_items_part_id(self):
        """Test device_type filter."""
        params = {"part_id": "WS-X6548-GE-TX"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_software(self):
        """Test software version filter."""
        params = {"software": ["17.3.3 MD"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_sw_missing(self):
        """Test sw_missing filter."""
        params = {"exclude_sw_missing": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_platform(self):
        """Test software version filter."""
        params = {"platform": [self.platform]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_sw_missing_only(self):
        """Test sw_missing filter."""
        params = {"sw_missing_only": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_location(self):
        """Test location filter."""
        params = {"location": [self.location.name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class DeviceHardwareNoticeResultFilterSetTestCase(TestCase):  # pylint: disable=too-many-instance-attributes
    """Tests for the DeviceHardwareNoticeResultFilterSet."""

    queryset = DeviceHardwareNoticeResult.objects.all()
    filterset = DeviceHardwareNoticeResultFilterSet

    def setUp(self):
        self.manufacturer, _ = Manufacturer.objects.get_or_create(name="Cisco")
        self.device_type_1, _ = DeviceType.objects.get_or_create(model="c9300-24", manufacturer=self.manufacturer)
        self.device_type_2, _ = DeviceType.objects.get_or_create(model="c9300-48", manufacturer=self.manufacturer)
        self.devicerole_1, _ = Role.objects.get_or_create(name="switch", color="ff0000")
        self.devicerole_1.content_types.add(ContentType.objects.get_for_model(Device))
        self.devicerole_2, _ = Role.objects.get_or_create(name="router", color="ff0000")
        self.devicerole_2.content_types.add(ContentType.objects.get_for_model(Device))
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
        self.device_1, _ = Device.objects.get_or_create(
            name="r1",
            device_type=self.device_type_1,
            role=self.devicerole_1,
            location=self.location1,
            status=active_status,
        )
        self.device_2, _ = Device.objects.get_or_create(
            name="r2",
            device_type=self.device_type_2,
            role=self.devicerole_2,
            location=self.location1,
            status=active_status,
        )
        self.notice_1, _ = HardwareLCM.objects.get_or_create(
            device_type=self.device_type_1,
            end_of_sale="2022-04-01",
            end_of_support="2023-04-01",
            end_of_sw_releases="2024-04-01",
            end_of_security_patches="2025-04-01",
            documentation_url="https://cisco.com/c9300-24",
        )
        self.notice_2, _ = HardwareLCM.objects.get_or_create(
            device_type=self.device_type_2,
            end_of_sale="2024-04-01",
            end_of_support="2025-05-01",
            end_of_sw_releases="2026-05-01",
            end_of_security_patches="2027-05-01",
            documentation_url="https://cisco.com/c9300-48",
        )
        DeviceHardwareNoticeResult.objects.get_or_create(
            device=self.device_1,
            hardware_notice=self.notice_1,
            is_supported=True,
        )
        DeviceHardwareNoticeResult.objects.get_or_create(
            device=self.device_2,
            hardware_notice=self.notice_2,
            is_supported=False,
        )

    def test_devices_name_one(self):
        """Test devices filter."""
        params = {"device": ["r1"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_devices_name_all(self):
        """Test devices filter."""
        params = {"device": ["r1", "r2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device_type_name(self):
        """Test device_type filter."""
        params = {"device_type": ["c9300-24"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_device_role_name(self):
        """Test device_role filter."""
        params = {"device_role": ["switch"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_device_type_id(self):
        """Test device_type_id filter."""
        params = {"device_type_id": [self.device_type_1.id]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_device_role_id(self):
        """Test device_role_id filter."""
        params = {"device_role_id": [self.devicerole_1.id]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_device_id_all(self):
        """Test device_id filter."""
        params = {"device_id": [self.device_1.id, self.device_2.id]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_location(self):
        """Test location filter."""
        params = {"location": [self.location1.name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_manufacturer(self):
        """Test manufacturer filter."""
        params = {"manufacturer": [self.manufacturer.name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_end_of_sale_search(self):
        """Test searching for a string within the end of sale field."""
        params = {"end_of_sale": "2022-04-01"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_end_of_support_search(self):
        """Test searching for a string within the end of support field."""
        params = {"end_of_support": "2025-05-01"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_end_of_sw_releases_search(self):
        """Test searching for a string within the end of software releases field."""
        params = {"end_of_sw_releases": "2024-04-01"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_end_of_security_patches_search(self):
        """Test searching for a string within the end of security patches field."""
        params = {"end_of_security_patches": "2027-05-01"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)


class CVELCMTestCase(TestCase):
    """Tests for CVELCMFilter."""

    queryset = CVELCM.objects.all()
    filterset = CVELCMFilterSet

    def setUp(self):
        cve_ct = ContentType.objects.get_for_model(CVELCM)
        fixed = Status.objects.create(name="Fixed", color="4caf50", description="Unit has been fixed")
        fixed.content_types.set([cve_ct])
        not_fixed = Status.objects.create(name="Not Fixed", color="f44336", description="Unit is not fixed")
        not_fixed.content_types.set([cve_ct])

        CVELCM.objects.create(
            name="CVE-2021-1391",
            published_date="2021-03-24",
            link="https://www.cvedetails.com/cve/CVE-2021-1391/",
            cvss=3.0,
            cvss_v2=3.0,
            cvss_v3=3.0,
        )
        CVELCM.objects.create(
            name="CVE-2021-44228",
            published_date="2021-12-10",
            link="https://www.cvedetails.com/cve/CVE-2021-44228/",
            status=not_fixed,
            cvss=5.0,
            cvss_v2=5.0,
            cvss_v3=5.0,
        )
        CVELCM.objects.create(
            name="CVE-2020-27134",
            published_date="2020-12-11",
            link="https://www.cvedetails.com/cve/CVE-2020-27134/",
            severity=CVESeverityChoices.CRITICAL,
            status=fixed,
            cvss=7,
            cvss_v2=7,
            cvss_v3=7,
        )

    def test_q_one_year(self):
        """Test q filter to find single record based on year."""
        params = {"q": "2020"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_two_year(self):
        """Test q filter to find two records based on year."""
        params = {"q": "2021"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_q_link(self):
        """Test q filter to all records from link."""
        params = {"q": "cvedetails"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_status(self):
        """Test status filter."""
        params = {"status": ["Fixed"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_exclude_status(self):
        """Test exclude_status filter."""
        params = {"exclude_status": ["Fixed"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_severity(self):
        """Test severity filter."""
        params = {"severity": [CVESeverityChoices.CRITICAL]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_published_date_before(self):
        """Test published_date_before filter."""
        params = {"published_date_before": "2021-01-01"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_published_date_after(self):
        """Test published_date_after filter."""
        params = {"published_date_after": "2021-01-01"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_cvss_gte(self):
        """Test cvss__gte filter."""
        params = {"cvss__gte": "1"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"cvss__gte": "4"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"cvss__gte": "6"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"cvss__gte": "9"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)

    def test_cvss_lte(self):
        """Test cvss__lte filter."""
        params = {"cvss__lte": "1"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)
        params = {"cvss__lte": "4"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"cvss__lte": "6"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"cvss__lte": "9"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_cvss_v2_gte(self):
        """Test cvss_v2__gte filter."""
        params = {"cvss_v2__gte": "1"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"cvss_v2__gte": "4"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"cvss_v2__gte": "6"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"cvss_v2__gte": "9"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)

    def test_cvss_v2_lte(self):
        """Test cvss_v2__lte filter."""
        params = {"cvss_v2__lte": "1"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)
        params = {"cvss_v2__lte": "4"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"cvss_v2__lte": "6"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"cvss_v2__lte": "9"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_cvss_v3_gte(self):
        """Test cvss_v3__gte filter."""
        params = {"cvss_v3__gte": "1"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"cvss_v3__gte": "4"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"cvss_v3__gte": "6"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"cvss_v3__gte": "9"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)

    def test_cvss_v3_lte(self):
        """Test cvss_v3__lte filter."""
        params = {"cvss_v3__lte": "1"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)
        params = {"cvss_v3__lte": "4"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"cvss_v3__lte": "6"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"cvss_v3__lte": "9"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)


class VulnerabilityLCMTestCase(TestCase):
    """Tests for VulnerabilityLCMFilter."""

    queryset = VulnerabilityLCM.objects.all()
    filterset = VulnerabilityLCMFilterSet

    def setUp(self):
        inventory_items = create_inventory_items()
        cves = create_cves()
        softwares = create_softwares()
        vuln_ct = ContentType.objects.get_for_model(VulnerabilityLCM)
        fix_me = Status.objects.create(name="Fix Me", color="4caf50", description="Please fix me.")
        fix_me.content_types.set([vuln_ct])

        VulnerabilityLCM.objects.create(
            cve=cves[0],
            device=inventory_items[0].device,
            software=softwares[0],
        )
        VulnerabilityLCM.objects.create(
            cve=cves[1],
            device=inventory_items[1].device,
            software=softwares[1],
            status=fix_me,
        )
        VulnerabilityLCM.objects.create(
            cve=cves[2],
            inventory_item=inventory_items[2],
            software=softwares[2],
            status=fix_me,
        )

    def test_q_cve(self):
        """Test q filter to find single record based on CVE name."""
        params = {"q": "2020"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_device(self):
        """Test q filter to find single record based on Device name."""
        params = {"q": "sw1"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_inventory_item(self):
        """Test q filter to find single record based on Inventory Item name."""
        params = {"q": "48x RJ-45"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_software_device_platform(self):
        """Test q filter to find single record based on Software Device Platform name."""
        params = {"q": "cisco_ios"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_q_software_version(self):
        """Test q filter to find single record based on Software version."""
        params = {"q": "4.22.9M"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

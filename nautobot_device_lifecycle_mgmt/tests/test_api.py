# pylint: disable=no-member
"""Unit tests for nautobot_device_lifecycle_mgmt."""

import datetime
from unittest import skip

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from nautobot.apps.testing import APIViewTestCases
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

from nautobot_device_lifecycle_mgmt.models import (
    CVELCM,
    ContractLCM,
    HardwareLCM,
    ProviderLCM,
    ValidatedSoftwareLCM,
    VulnerabilityLCM,
)
from nautobot_device_lifecycle_mgmt.tests.conftest import create_cves, create_devices, create_softwares

User = get_user_model()


class HardwareLCMAPITest(APIViewTestCases.APIViewTestCase):
    """Test the HardwareLCM API."""

    model = HardwareLCM
    bulk_update_data = {"documentation_url": "https://cisco.com/eox"}
    brief_fields = [
        "custom_fields",
        "device_type",
        "display",
        "documentation_url",
        "end_of_sale",
        "end_of_security_patches",
        "end_of_support",
        "end_of_sw_releases",
        "expired",
        "id",
        "inventory_item",
        "release_date",
        "tags",
        "url",
    ]

    @classmethod
    def setUpTestData(cls):  # pylint: disable=invalid-name
        """Create a superuser and token for API calls."""
        manufacturer = Manufacturer.objects.create(name="Cisco")
        device_types = (
            DeviceType.objects.get_or_create(model="c9300-24", manufacturer=manufacturer)[0],
            DeviceType.objects.get_or_create(model="c9300-48", manufacturer=manufacturer)[0],
            DeviceType.objects.get_or_create(model="c9500-24", manufacturer=manufacturer)[0],
            DeviceType.objects.get_or_create(model="c9500-48", manufacturer=manufacturer)[0],
            DeviceType.objects.get_or_create(model="c9407", manufacturer=manufacturer)[0],
            DeviceType.objects.get_or_create(model="c9410", manufacturer=manufacturer)[0],
        )

        HardwareLCM.objects.create(device_type=device_types[3], end_of_sale=datetime.date(2021, 4, 1))
        HardwareLCM.objects.create(device_type=device_types[4], end_of_sale=datetime.date(2021, 4, 1))
        HardwareLCM.objects.create(device_type=device_types[5], end_of_sale=datetime.date(2021, 4, 1))

        cls.create_data = [
            # Setting end_of_sale as datetime.date for proper comparison
            {"device_type": device_types[0].id, "end_of_sale": datetime.date(2021, 4, 1)},
            {"device_type": device_types[1].id, "end_of_sale": datetime.date(2021, 4, 1)},
            {"device_type": device_types[2].id, "end_of_sale": datetime.date(2021, 4, 1)},
        ]

    @skip("Not implemented")
    def test_bulk_delete_objects(self):
        pass

    @skip("Not implemented")
    def test_bulk_update_objects(self):
        pass


class ContractLCMAPITest(APIViewTestCases.APIViewTestCase):
    """Test the ContractLCM API."""

    model = ContractLCM
    bulk_update_data = {"documentation_url": "https://cisco.com/eox"}
    brief_fields = [
        "contract_type",
        "cost",
        "display",
        "end",
        "expired",
        "id",
        "name",
        "provider",
        "devices",
        "start",
        "support_level",
    ]

    @classmethod
    def setUpTestData(cls):  # pylint: disable=invalid-name
        """Create a superuser and token for API calls."""
        devices = create_devices()
        provider = ProviderLCM.objects.create(
            name="Cisco",
            description="Cisco Support",
            physical_address="123 Cisco Way, San Jose, CA",
            phone="(123) 456-7890",
            email="email@cisco.com",
            portal_url="https://www.cisco.com/",
            comments="Test Comment",
        )
        cls.create_data = [
            {
                "name": "Nexus Support - Hardware",
                "start": datetime.date(2021, 4, 1),
                "end": datetime.date(2022, 4, 1),
                "support_level": "24/7",
                "contract_type": "Hardware",
                "provider": provider.id,
                "devices": [device.pk for device in devices],
            },
            {
                "name": "Nexus Support - Software",
                "start": datetime.date(2021, 4, 1),
                "end": datetime.date(2022, 4, 1),
                "support_level": "8-5, M-F",
                "contract_type": "Software",
                "provider": provider.id,
            },
            {
                "name": "ASA Support - Hardware",
                "start": datetime.date(2021, 4, 1),
                "end": datetime.date(2022, 4, 1),
                "support_level": "24/7",
                "contract_type": "Hardware",
                "provider": provider.id,
            },
        ]

        ContractLCM.objects.create(
            name="Meraki Hardware Support",
            number="MERK00001",
            start=datetime.date(2021, 4, 1),
            end=datetime.date(2022, 4, 1),
            provider=provider,
        )
        ContractLCM.objects.create(
            name="Meraki Software Support",
            number="MERK00002",
            start=datetime.date(2021, 4, 1),
            end=datetime.date(2022, 4, 1),
            provider=provider,
        )
        ContractLCM.objects.create(
            name="Juniper Hardware Support",
            number="CSCO0000001",
            start=datetime.date(2021, 4, 1),
            end=datetime.date(2022, 4, 1),
            provider=provider,
        )

    @skip("Not implemented")
    def test_bulk_delete_objects(self):
        """Currently don't support bulk operations."""

    @skip("Not implemented")
    def test_bulk_update_objects(self):
        pass


class ValidatedSoftwareLCMAPITest(APIViewTestCases.APIViewTestCase):
    """Test the SoftwareLCM API."""

    model = ValidatedSoftwareLCM
    brief_fields = [
        "custom_fields",
        "device_roles",
        "device_types",
        "devices",
        "display",
        "end",
        "id",
        "inventory_items",
        "object_tags",
        "preferred",
        "software",
        "start",
        "tags",
        "url",
        "valid",
    ]

    @classmethod
    def setUpTestData(cls):  # pylint: disable=invalid-name
        """Create a superuser and token for API calls."""
        device_platform, _ = Platform.objects.get_or_create(name="cisco_ios")
        active_status, _ = Status.objects.get_or_create(name="Active")
        active_status.content_types.add(ContentType.objects.get_for_model(SoftwareVersion))
        active_status.content_types.add(ContentType.objects.get_for_model(Location))
        active_status.content_types.add(ContentType.objects.get_for_model(Device))
        softwares = (
            SoftwareVersion.objects.create(
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
            ),
            SoftwareVersion.objects.create(
                **{
                    "platform": device_platform,
                    "version": "15.5(1)SY",
                    "alias": "Catalyst-15.5(1)SY",
                    "end_of_support_date": "2019-02-5",
                    "documentation_url": "https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst6500/ios/15-1SY/config_guide/sup2T/15_1_sy_swcg_2T/cef.html",
                    "long_term_support": False,
                    "pre_release": True,
                    "status": active_status,
                }
            ),
        )

        manufacturer = Manufacturer.objects.create(name="Cisco")
        location_type_location_a, _ = LocationType.objects.get_or_create(name="LocationA")
        location_type_location_a.content_types.add(
            ContentType.objects.get_for_model(Device),
        )
        location1, _ = Location.objects.get_or_create(
            name="Location1", location_type=location_type_location_a, status=active_status
        )
        deviceroles = (
            Role.objects.get_or_create(name="router", color="ff0000")[0],
            Role.objects.get_or_create(name="switch", color="ffff00")[0],
        )
        for devicerole in deviceroles:
            devicerole.content_types.add(ContentType.objects.get_for_model(Device))
        devicetypes = (
            DeviceType.objects.create(manufacturer=manufacturer, model="ASR-1000"),
            DeviceType.objects.create(manufacturer=manufacturer, model="Catalyst 6500"),
        )
        devices = (
            Device.objects.create(
                device_type=devicetypes[0],
                role=deviceroles[0],
                name="Device 1",
                location=location1,
                status=active_status,
            ),
            Device.objects.create(
                device_type=devicetypes[1],
                role=deviceroles[1],
                name="Device 2",
                location=location1,
                status=active_status,
            ),
        )
        inventoryitems = (
            InventoryItem.objects.create(device=devices[0], name="SwitchModule1"),
            InventoryItem.objects.create(device=devices[1], name="Supervisor Engine 720"),
        )

        cls.create_data = [
            {
                "software": softwares[0].id,
                "devices": [device.pk for device in devices],
                "start": datetime.date(2020, 1, 14),
                "end": datetime.date(2024, 10, 18),
                "preferred": False,
            },
            {
                "software": softwares[0].id,
                "device_types": [devicetype.pk for devicetype in devicetypes],
                "start": datetime.date(2021, 6, 4),
                "end": datetime.date(2025, 1, 8),
                "preferred": True,
            },
            {
                "software": softwares[0].id,
                "device_roles": [devicerole.pk for devicerole in deviceroles],
                "start": datetime.date(2019, 3, 6),
                "end": datetime.date(2023, 6, 1),
                "preferred": False,
            },
            {
                "software": softwares[0].id,
                "inventory_items": [inventoryitem.pk for inventoryitem in inventoryitems],
                "start": datetime.date(2019, 5, 4),
                "end": datetime.date(2023, 9, 15),
                "preferred": False,
            },
        ]

        validated_software = ValidatedSoftwareLCM(
            software=softwares[1],
            start=datetime.date(2021, 6, 4),
            end=datetime.date(2025, 1, 8),
            preferred=True,
        )
        validated_software.save()
        validated_software.devices.set([device.pk for device in devices])

        validated_software = ValidatedSoftwareLCM(
            software=softwares[1],
            start=datetime.date(2018, 2, 23),
            end=datetime.date(2019, 6, 12),
            preferred=False,
        )
        validated_software.save()
        validated_software.device_types.set([devicetype.pk for devicetype in devicetypes])

        validated_software = ValidatedSoftwareLCM(
            software=softwares[1],
            start=datetime.date(2019, 11, 19),
            end=datetime.date(2030, 7, 30),
            preferred=False,
        )
        validated_software.save()
        validated_software.device_roles.set([devicerole.pk for devicerole in deviceroles])

        ValidatedSoftwareLCM(
            software=softwares[1],
            start=datetime.date(2020, 10, 9),
            end=datetime.date(2025, 1, 16),
            preferred=False,
        )
        validated_software.save()
        validated_software.inventory_items.set([inventoryitem.pk for inventoryitem in inventoryitems])

    @skip("Not implemented")
    def test_bulk_delete_objects(self):
        pass


class CVELCMAPITest(APIViewTestCases.APIViewTestCase):
    """Test the CVELCM API."""

    model = CVELCM
    brief_fields = [
        "comments",
        "cvss",
        "cvss_v2",
        "cvss_v3",
        "description",
        "display",
        "fix",
        "id",
        "link",
        "name",
        "published_date",
        "severity",
        "status",
        "url",
        "affected_softwares",
    ]

    choices_fields = ["severity"]

    @classmethod
    def setUpTestData(cls):  # pylint: disable=invalid-name
        """Set up test objects."""
        softwares = create_softwares()
        cls.create_data = [
            {
                "name": "CVE-2021-40128",
                "published_date": datetime.date(2021, 11, 4),
                "link": "https://www.cvedetails.com/cve/CVE-2021-40128/",
                "affected_softwares": [software.pk for software in softwares],
            },
            {
                "name": "CVE-2021-40126",
                "published_date": datetime.date(2021, 11, 4),
                "link": "https://www.cvedetails.com/cve/CVE-2021-40126/",
                "affected_softwares": [software.pk for software in softwares],
            },
            {
                "name": "CVE-2021-40125",
                "published_date": datetime.date(2021, 10, 27),
                "link": "https://www.cvedetails.com/cve/CVE-2021-40125/",
                "affected_softwares": [software.pk for software in softwares],
            },
        ]

        CVELCM.objects.create(
            name="CVE-2021-1391",
            published_date="2021-03-24",
            link="https://www.cvedetails.com/cve/CVE-2021-1391/",
        )
        CVELCM.objects.create(
            name="CVE-2021-44228",
            published_date="2021-12-10",
            link="https://www.cvedetails.com/cve/CVE-2021-44228/",
        )
        CVELCM.objects.create(
            name="CVE-2020-27134",
            published_date="2020-12-11",
            link="https://www.cvedetails.com/cve/CVE-2020-27134/",
        )

    @skip("Not implemented")
    def test_bulk_delete_objects(self):
        pass


class VulnerabilityLCMAPITest(
    # Not inheriting CreateObjectViewTestCase
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    """Test the VulnerabilityLCM API."""

    model = VulnerabilityLCM
    brief_fields = [
        "custom_fields",
        "cve",
        "device",
        "display",
        "id",
        "inventory_item",
        "software",
        "status",
        "tags",
        "url",
    ]
    validation_excluded_fields = ["status"]

    @classmethod
    def setUpTestData(cls):  # pylint: disable=invalid-name
        """Set up test objects."""
        devices = create_devices()
        cves = create_cves()
        softwares = create_softwares()

        for i, cve in enumerate(cves):
            VulnerabilityLCM.objects.create(cve=cve, device=devices[i], software=softwares[i])

        vuln_ct = ContentType.objects.get_for_model(VulnerabilityLCM)
        status = Status.objects.create(name="Exempt", color="4caf50", description="This unit is exempt.")
        status.content_types.set([vuln_ct])
        cls.create_data = [{"status": {"name": "Exempt"}}]

    @skip("Not implemented")
    def test_bulk_delete_objects(self):
        pass

    @skip("Not implemented")
    def test_bulk_update_objects(self):
        pass

    @skip("Not implemented")
    def test_options_returns_expected_choices(self):
        pass


class ProviderLCMAPITest(APIViewTestCases.APIViewTestCase):
    """Test the ProviderLCMLCM API."""

    model = ProviderLCM
    brief_fields = [
        "name",
        "description",
        "physical_address",
        "phone",
        "email",
        "portal_url",
        "comments",
    ]

    @classmethod
    def setUpTestData(cls):  # pylint: disable=invalid-name
        """Create a Provider for API calls."""

        cls.create_data = [
            {
                "name": "Arista",
                "description": "Arista Support",
                "physical_address": "123 Arista Way, San Jose, CA",
                "country": "USA",
                "phone": "(123) 456-7890",
                "email": "email@Arista.com",
                "portal_url": "https://www.Arista.com/",
                "comments": "Test Comment",
            },
            {
                "name": "Erricson",
                "description": "Erricson Support",
                "physical_address": "123 Erricson Way, San Jose, CA",
                "country": "USA",
                "phone": "(123) 456-7890",
                "email": "email@Erricson.com",
                "portal_url": "https://www.Erricson.com/",
                "comments": "Test Comment",
            },
            {
                "name": "Linksys",
                "description": "Linksys Support",
                "physical_address": "123 Linksys Way, San Jose, CA",
                "country": "USA",
                "phone": "(123) 456-7890",
                "email": "email@Linksys.com",
                "portal_url": "https://www.Linksys.com/",
                "comments": "Test Comment",
            },
        ]

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
        ProviderLCM.objects.create(
            name="HP",
            description="HP Support",
            physical_address="123 HP Way, San Jose, CA",
            country="USA",
            phone="(123) 456-0000",
            email="email@HP.com",
            portal_url="https://www.HP.com/",
            comments="Test Comment",
        )
        ProviderLCM.objects.create(
            name="Juniper",
            description="Juniper Support",
            physical_address="123 Juniper Way, San Jose, CA",
            country="USA",
            phone="(123) 456-5890",
            email="email@Juniper.com",
            portal_url="https://www.Juniper.com/",
            comments="Test Comment",
        )

    @skip("Not implemented")
    def test_bulk_delete_objects(self):
        pass

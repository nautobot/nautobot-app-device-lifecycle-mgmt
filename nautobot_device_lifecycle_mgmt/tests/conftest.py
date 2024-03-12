"""Params for testing."""
from datetime import date
from nautobot.dcim.models import (
    DeviceType,
    Manufacturer,
    Platform,
    Site,
    Device,
    DeviceRole,
    InventoryItem,
)
from nautobot.extras.models import Status

from nautobot_device_lifecycle_mgmt.models import CVELCM, HardwareLCM, SoftwareLCM, ValidatedSoftwareLCM


def create_devices():
    """Create devices for tests."""
    device_platform, _ = Platform.objects.get_or_create(name="Cisco IOS", slug="cisco_ios")
    manufacturer, _ = Manufacturer.objects.get_or_create(name="Cisco", slug="cisco")
    device_type, _ = DeviceType.objects.get_or_create(manufacturer=manufacturer, model="6509-E", slug="6509-e")
    device_role, _ = DeviceRole.objects.get_or_create(name="Core Switch", slug="core-switch")
    site1, _ = Site.objects.get_or_create(name="TestSite 1", slug="testsite-1")
    site2, _ = Site.objects.get_or_create(name="TestSite 2", slug="testsite-2")
    status_active = Status.objects.get(slug="active")

    return (
        Device.objects.create(
            name="sw1",
            platform=device_platform,
            device_type=device_type,
            device_role=device_role,
            site=site1,
            status=status_active,
        ),
        Device.objects.create(
            name="sw2",
            platform=device_platform,
            device_type=device_type,
            device_role=device_role,
            site=site1,
            status=status_active,
        ),
        Device.objects.create(
            name="sw3",
            platform=device_platform,
            device_type=device_type,
            device_role=device_role,
            site=site2,
            status=status_active,
        ),
    )


def create_inventory_items():
    """Create inventory items for tests."""
    devices = create_devices()
    manufacturer, _ = Manufacturer.objects.get_or_create(slug="cisco")

    return (
        InventoryItem.objects.create(
            device=devices[0],
            manufacturer=manufacturer,
            name="SUP2T Card",
            part_id="VS-S2T-10G",
        ),
        InventoryItem.objects.create(
            device=devices[1],
            manufacturer=manufacturer,
            name="100GBASE-SR4 QSFP Transceiver",
            part_id="QSFP-100G-SR4-S",
        ),
        InventoryItem.objects.create(
            device=devices[2],
            manufacturer=manufacturer,
            name="48x RJ-45 Line Card",
            part_id="WS-X6548-GE-TX",
        ),
    )


def create_cves():
    """Create CVELCM items for tests."""
    cves = (
        CVELCM.objects.create(
            name="CVE-2021-1391",
            published_date="2021-03-24",
            link="https://www.cvedetails.com/cve/CVE-2021-1391/",
            description="A vulnerability in the dragonite debugger of Cisco IOS XE Software",
        ),
        CVELCM.objects.create(
            name="CVE-2021-44228",
            published_date="2021-12-10",
            link="https://www.cvedetails.com/cve/CVE-2021-44228/",
            description="Apache Log4j2 2.0-beta9 through 2.15.0",
        ),
        CVELCM.objects.create(
            name="CVE-2020-27134",
            published_date="2020-12-11",
            link="https://www.cvedetails.com/cve/CVE-2020-27134/",
            description="Multiple vulnerabilities in Cisco Jabber",
        ),
    )
    return cves


def create_softwares():
    """Create SoftwareLCM items for tests."""
    device_platform_ios, _ = Platform.objects.get_or_create(name="Cisco IOS", slug="cisco_ios")
    device_platform_eos, _ = Platform.objects.get_or_create(name="Arista EOS", slug="arista_eos")
    softwares = (
        SoftwareLCM.objects.create(device_platform=device_platform_ios, version="15.1(2)M"),
        SoftwareLCM.objects.create(device_platform=device_platform_ios, version="4.22.9M"),
        SoftwareLCM.objects.create(device_platform=device_platform_ios, version="21.4R3"),
        SoftwareLCM.objects.create(device_platform=device_platform_eos, version="4.17.1M"),
        SoftwareLCM.objects.create(device_platform=device_platform_eos, version="4.25.1F"),
    )
    return softwares


def create_validated_softwares():
    """Create ValidatedSoftwareLCM"""
    manufacturer, _ = Manufacturer.objects.get_or_create(slug="cisco")
    device_platform_ios, _ = Platform.objects.get_or_create(name="Cisco IOS", slug="cisco_ios")
    device_type = DeviceType.objects.create(manufacturer=manufacturer, model="ASR-1000", slug="asr-1000")
    software_one = SoftwareLCM.objects.create(
        device_platform=device_platform_ios,
        version="17.3.3 MD",
        release_date="2019-01-10",
    )
    validatedsoftwarelcm = ValidatedSoftwareLCM(
        software=software_one,
        start=date(2019, 1, 10),
    )
    validatedsoftwarelcm.device_types.set([device_type])
    validatedsoftwarelcm.save()
    software_two = SoftwareLCM.objects.create(
        device_platform=device_platform_ios,
        version="20.0.0 MD",
        release_date="2019-01-10",
    )
    validatedsoftwarelcm_two = ValidatedSoftwareLCM(
        software=software_two,
        start=date(2019, 1, 10),
    )
    validatedsoftwarelcm_two.device_types.set([device_type])
    validatedsoftwarelcm_two.save()

    validated_items = (
        software_one,
        software_two,
        validatedsoftwarelcm,
        validatedsoftwarelcm_two,
    )

    return validated_items


def create_inventory_item_hardware_notices():
    """Create inventory item hardware notices for tests."""

    return (
        HardwareLCM.objects.create(
            inventory_item="VS-S2T-10G",
            end_of_sale=date(2022, 4, 1),
            end_of_support=date(2023, 4, 1),
            end_of_sw_releases=date(2024, 4, 1),
            end_of_security_patches=date(2025, 4, 1),
            documentation_url="https://test.com",
        ),
        HardwareLCM.objects.create(
            inventory_item="QSFP-100G-SR4-S",
            end_of_sale=date(2022, 4, 1),
            end_of_support=date(2024, 1, 1),
            end_of_sw_releases=date(2024, 4, 1),
            end_of_security_patches=date(2025, 4, 1),
            documentation_url="https://test.com",
        ),
        HardwareLCM.objects.create(
            inventory_item="WS-X6548-GE-TX",
            end_of_sale=date(2022, 4, 1),
            end_of_support=date(2999, 1, 1),
            end_of_sw_releases=date(2024, 4, 1),
            end_of_security_patches=date(2025, 4, 1),
            documentation_url="https://test.com",
        ),
    )

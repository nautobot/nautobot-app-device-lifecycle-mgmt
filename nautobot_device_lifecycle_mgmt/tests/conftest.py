"""Params for testing."""
from datetime import date

from django.contrib.contenttypes.models import ContentType
from nautobot.dcim.models import Device, DeviceType, InventoryItem, Location, LocationType, Manufacturer, Platform
from nautobot.extras.models import Role, Status

from nautobot_device_lifecycle_mgmt.models import CVELCM, SoftwareLCM, ValidatedSoftwareLCM


def create_devices():
    """Create devices for tests."""
    device_platform, _ = Platform.objects.get_or_create(name="cisco_ios")
    manufacturer, _ = Manufacturer.objects.get_or_create(name="Cisco")
    device_type, _ = DeviceType.objects.get_or_create(manufacturer=manufacturer, model="6509-E")
    device_role_switch, _ = Role.objects.get_or_create(name="core-switch")
    device_role_router, _ = Role.objects.get_or_create(name="router")
    device_role_switch.content_types.add(ContentType.objects.get_for_model(Device))
    device_role_router.content_types.add(ContentType.objects.get_for_model(Device))
    location_type_location_a, _ = LocationType.objects.get_or_create(name="LocationA")
    location_type_location_a.content_types.add(
        ContentType.objects.get_for_model(Device),
    )
    location_status = Status.objects.get_for_model(Location).first()
    location1, _ = Location.objects.get_or_create(
        name="Location1", location_type=location_type_location_a, status=location_status
    )
    location2, _ = Location.objects.get_or_create(
        name="Location2", location_type=location_type_location_a, status=location_status
    )
    device_status = Status.objects.get_for_model(Device).first()

    return (
        Device.objects.create(
            name="sw1",
            platform=device_platform,
            device_type=device_type,
            role=device_role_switch,
            location=location1,
            status=device_status,
        ),
        Device.objects.create(
            name="sw2",
            platform=device_platform,
            device_type=device_type,
            role=device_role_switch,
            location=location1,
            status=device_status,
        ),
        Device.objects.create(
            name="sw3",
            platform=device_platform,
            device_type=device_type,
            role=device_role_router,
            location=location2,
            status=device_status,
        ),
    )


def create_inventory_items():
    """Create inventory items for tests."""
    devices = create_devices()
    manufacturer, _ = Manufacturer.objects.get_or_create(name="Cisco")

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
    device_platform_ios, _ = Platform.objects.get_or_create(name="cisco_ios")
    device_platform_eos, _ = Platform.objects.get_or_create(name="arista_eos")
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
    manufacturer, _ = Manufacturer.objects.get_or_create(name="Cisco")
    device_platform_ios, _ = Platform.objects.get_or_create(name="cisco_ios")
    device_type, _ = DeviceType.objects.get_or_create(manufacturer=manufacturer, model="ASR-1000")
    software_one = SoftwareLCM.objects.create(
        device_platform=device_platform_ios,
        version="17.3.3 MD",
        release_date="2019-01-10",
    )
    validatedsoftwarelcm = ValidatedSoftwareLCM(
        software=software_one,
        start=date(2019, 1, 10),
    )
    validatedsoftwarelcm.device_types.set([device_type])  # pylint: disable=no-member
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
    validatedsoftwarelcm_two.device_types.set([device_type])  # pylint: disable=no-member
    validatedsoftwarelcm_two.save()

    validated_items = (
        software_one,
        software_two,
        validatedsoftwarelcm,
        validatedsoftwarelcm_two,
    )

    return validated_items

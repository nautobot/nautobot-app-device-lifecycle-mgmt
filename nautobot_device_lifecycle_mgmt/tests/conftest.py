"""Params for testing."""
from nautobot.dcim.models import DeviceType, Manufacturer, Platform, Site, Device, DeviceRole, InventoryItem
from nautobot.extras.models import Status


def create_devices():
    """Create devices for tests."""
    device_platform = Platform.objects.create(name="Cisco IOS", slug="cisco_ios")
    manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
    device_type = DeviceType.objects.create(manufacturer=manufacturer, model="6509-E", slug="6509-e")
    device_role = DeviceRole.objects.create(name="Core Switch", slug="core-switch")
    site = Site.objects.create(name="Test 1", slug="test-1")
    status_active = Status.objects.get(slug="active")

    return (
        Device.objects.create(
            name="sw1",
            platform=device_platform,
            device_type=device_type,
            device_role=device_role,
            site=site,
            status=status_active,
        ),
        Device.objects.create(
            name="sw2",
            platform=device_platform,
            device_type=device_type,
            device_role=device_role,
            site=site,
            status=status_active,
        ),
        Device.objects.create(
            name="sw3",
            platform=device_platform,
            device_type=device_type,
            device_role=device_role,
            site=site,
            status=status_active,
        ),
    )


def create_inventory_items():
    """Create inventory items for tests."""
    devices = create_devices()
    manufacturer = Manufacturer.objects.get(slug="cisco")

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

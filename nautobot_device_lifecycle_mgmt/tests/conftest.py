"""Params for testing."""
from nautobot.dcim.models import DeviceType, Manufacturer, Platform, Site, Device, DeviceRole


def create_devices():
    """Create devices for tests."""
    device_platform = Platform.objects.create(name="Cisco IOS", slug="cisco_ios")
    manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
    device_type = DeviceType.objects.create(manufacturer=manufacturer, model="ASR-1000", slug="asr-1000")
    device_role = DeviceRole.objects.create(name="Core Switch", slug="core-switch")
    site = Site.objects.create(name="Test 1", slug="test-1")
    return (
        Device.objects.create(
            name="r1",
            platform=device_platform,
            device_type=device_type,
            device_role=device_role,
            site=site,
        ),
        Device.objects.create(
            name="r2",
            platform=device_platform,
            device_type=device_type,
            device_role=device_role,
            site=site,
        ),
        Device.objects.create(
            name="r3",
            platform=device_platform,
            device_type=device_type,
            device_role=device_role,
            site=site,
        ),
    )

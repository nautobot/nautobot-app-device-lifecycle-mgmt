"""Create fixtures for tests."""

from nautobot_device_lifecycle_mgmt.models import HardwareLCM


def create_hardwarelcm():
    """Fixture to create necessary number of HardwareLCM for tests."""
    HardwareLCM.objects.create(name="Test One")
    HardwareLCM.objects.create(name="Test Two")
    HardwareLCM.objects.create(name="Test Three")

"""Unit tests for nautobot_device_lifecycle_mgmt."""

from nautobot.apps.testing import APIViewTestCases

from nautobot_device_lifecycle_mgmt import models
from nautobot_device_lifecycle_mgmt.tests import fixtures


class HardwareLCMAPIViewTest(APIViewTestCases.APIViewTestCase):
    # pylint: disable=too-many-ancestors
    """Test the API viewsets for HardwareLCM."""

    model = models.HardwareLCM
    create_data = [
        {
            "name": "Test Model 1",
            "description": "test description",
        },
        {
            "name": "Test Model 2",
        },
    ]
    bulk_update_data = {"description": "Test Bulk Update"}

    @classmethod
    def setUpTestData(cls):
        fixtures.create_hardwarelcm()

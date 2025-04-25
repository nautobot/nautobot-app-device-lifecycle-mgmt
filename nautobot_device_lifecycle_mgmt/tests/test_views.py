"""Unit tests for views."""

from nautobot.apps.testing import ViewTestCases

from nautobot_device_lifecycle_mgmt import models
from nautobot_device_lifecycle_mgmt.tests import fixtures


class HardwareLCMViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    # pylint: disable=too-many-ancestors
    """Test the HardwareLCM views."""

    model = models.HardwareLCM
    bulk_edit_data = {"description": "Bulk edit views"}
    form_data = {
        "name": "Test 1",
        "description": "Initial model",
    }

    update_data = {
        "name": "Test 2",
        "description": "Updated model",
    }

    @classmethod
    def setUpTestData(cls):
        fixtures.create_hardwarelcm()

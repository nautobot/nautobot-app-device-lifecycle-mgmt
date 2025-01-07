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
    csv_data = (
        "name",
        "Test csv1",
        "Test csv2",
        "Test csv3",
    )

    @classmethod
    def setUpTestData(cls):
        fixtures.create_hardwarelcm()

"""Test HardwareLCM Filter."""

from nautobot.apps.testing import FilterTestCases

from nautobot_device_lifecycle_mgmt import filters, models
from nautobot_device_lifecycle_mgmt.tests import fixtures


class HardwareLCMFilterTestCase(FilterTestCases.FilterTestCase):
    """HardwareLCM Filter Test Case."""

    queryset = models.HardwareLCM.objects.all()
    filterset = filters.HardwareLCMFilterSet
    generic_filter_tests = (
        ("id",),
        ("created",),
        ("last_updated",),
        ("name",),
    )

    @classmethod
    def setUpTestData(cls):
        """Setup test data for HardwareLCM Model."""
        fixtures.create_hardwarelcm()

    def test_q_search_name(self):
        """Test using Q search with name of HardwareLCM."""
        params = {"q": "Test One"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_invalid(self):
        """Test using invalid Q search for HardwareLCM."""
        params = {"q": "test-five"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)

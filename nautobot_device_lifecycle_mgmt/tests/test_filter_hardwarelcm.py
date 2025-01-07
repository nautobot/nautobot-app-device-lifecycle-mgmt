"""Test HardwareLCM Filter."""

from django.test import TestCase

from nautobot_device_lifecycle_mgmt import filters, models
from nautobot_device_lifecycle_mgmt.tests import fixtures


class HardwareLCMFilterTestCase(TestCase):
    """HardwareLCM Filter Test Case."""

    queryset = models.HardwareLCM.objects.all()
    filterset = filters.HardwareLCMFilterSet

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

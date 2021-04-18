"""Unit tests for eox_notices."""
# from django.contrib.auth import get_user_model
#
# from nautobot.utilities.testing import APIViewTestCases
# from nautobot.dcim.models import DeviceType, Manufacturer
#
# from eox_notices.models import EoxNotice
#
# User = get_user_model()


# class EoxNoticeAPITest(APIViewTestCases.APIViewTestCase):
#    """Test the EoxNotices API."""
#
#    model = EoxNotice
#    bulk_update_data = {"notice_url": "https://cisco.com/eox"}
#
#    def setUp(self):
#        """Create a superuser and token for API calls."""
#        self.manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
#        self.device_types = (
#            DeviceType.objects.create(model="c9300-24", slug="c9300-24", manufacturer=self.manufacturer),
#            DeviceType.objects.create(model="c9300-48", slug="c9300-48", manufacturer=self.manufacturer),
#            DeviceType.objects.create(model="c9500-24", slug="c9500-24", manufacturer=self.manufacturer),
#        )
#
#        EoxNotice.objects.create(device_type=self.device_types[0], end_of_sale="2021-04-01")
#        EoxNotice.objects.create(device_type=self.device_types[1], end_of_sale="2021-04-01")
#        EoxNotice.objects.create(device_type=self.device_types[2], end_of_sale="2021-04-01")

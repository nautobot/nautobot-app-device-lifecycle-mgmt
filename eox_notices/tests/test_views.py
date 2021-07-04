"""Unit tests for views."""
import datetime
from django.contrib.auth import get_user_model

from nautobot.utilities.testing import ViewTestCases
from nautobot.dcim.models import DeviceType, Manufacturer

from eox_notices.models import EoxNotice

User = get_user_model()


class EoxNoticeViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    """Test the EoxNotices views."""

    model = EoxNotice
    bulk_edit_data = {"notice_url": "https://cisco.com/eox"}

    def _get_base_url(self):
        return "plugins:{}:{}_{{}}".format(self.model._meta.app_label, self.model._meta.model_name)

    @classmethod
    def setUpTestData(cls):
        """Create a superuser and token for API calls."""
        manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        device_types = (
            DeviceType.objects.create(model="c9300-24", slug="c9300-24", manufacturer=manufacturer),
            DeviceType.objects.create(model="c9300-48", slug="c9300-48", manufacturer=manufacturer),
            DeviceType.objects.create(model="c9500-24", slug="c9500-24", manufacturer=manufacturer),
            DeviceType.objects.create(model="c9200-24", slug="c9200-24", manufacturer=manufacturer),
            DeviceType.objects.create(model="c9200-48", slug="c9200-48", manufacturer=manufacturer),
        )

        EoxNotice.objects.create(device_type=device_types[0], end_of_sale=datetime.date(2021, 4, 1))
        EoxNotice.objects.create(device_type=device_types[1], end_of_sale=datetime.date(2021, 4, 1))

        cls.form_data = {
            "device_type": device_types[2].id,
            "end_of_sale": datetime.date(2021, 4, 1),
            "end_of_support": datetime.date(2024, 4, 1),
        }
        cls.csv_data = (
            "device_type,end_of_sale,end_of_support,end_of_sw_releases,end_of_security_patches,notice_url",
            "c9500-24, 2021-10-06, 2022-10-06, 2025-10-06, 2026-10-06, https://cisco.com/eox",
            "c9200-24, 2022-10-06, 2023-10-06, 2025-10-06, 2026-10-06, https://cisco.com/eox",
            "c9200-48, 2023-10-06, 2024-10-06, 2025-10-06, 2026-10-06, https://cisco.com/eox",
        )

    # The following tests are being passed due to import not being implemented at this time
    # def test_bulk_import_object_with_constrained_permission(self):
    #     pass

    # def test_bulk_import_objects_with_permission(self):
    #     pass

    # def test_bulk_import_objects_without_permission(self):
    #     pass

    # def test_bulk_import_objects_with_constrained_permission(self):
    #     pass

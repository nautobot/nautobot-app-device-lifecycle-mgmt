"""Unit tests for views."""
import datetime
from django.contrib.auth import get_user_model

from nautobot.utilities.testing import ViewTestCases
from nautobot.dcim.models import DeviceType, Manufacturer

from nautobot_device_lifecycle_mgmt.models import HardwareLCM

User = get_user_model()


class HardwareLCMViewTest(ViewTestCases.PrimaryObjectViewTestCase):  # pylint: disable=too-many-ancestors
    """Test the HardwareLCM views."""

    model = HardwareLCM
    bulk_edit_data = {"documentation_url": "https://cisco.com/eox"}

    def _get_base_url(self):
        return "plugins:{}:{}_{{}}".format(  # pylint: disable=consider-using-f-string
            self.model._meta.app_label, self.model._meta.model_name
        )

    @classmethod
    def setUpTestData(cls):
        """Create a superuser and token for API calls."""
        manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        device_types = tuple(
            DeviceType.objects.create(model=model, slug=model, manufacturer=manufacturer)
            for model in ["c9300-24", "c9300-48", "c9500-24", "c9200-24", "c9200-48"]
        )

        HardwareLCM.objects.create(device_type=device_types[0], end_of_sale=datetime.date(2021, 4, 1))
        HardwareLCM.objects.create(device_type=device_types[1], end_of_sale=datetime.date(2021, 4, 1))

        cls.form_data = {
            "device_type": device_types[2].id,
            "end_of_sale": datetime.date(2021, 4, 1),
            "end_of_support": datetime.date(2024, 4, 1),
        }
        cls.csv_data = (
            "device_type,end_of_sale,end_of_support,end_of_sw_releases,end_of_security_patches,documentation_url",
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

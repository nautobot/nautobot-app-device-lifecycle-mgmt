# pylint: disable=no-member
"""Unit tests for views."""

import datetime
from unittest import skip

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from nautobot.apps.testing import ViewTestCases
from nautobot.dcim.models import DeviceType, Manufacturer
from nautobot.extras.models import Status
from nautobot.users.models import ObjectPermission

from nautobot_device_lifecycle_mgmt.models import (
    CVELCM,
    DeviceSoftwareValidationResult,
    HardwareLCM,
    InventoryItemSoftwareValidationResult,
    VulnerabilityLCM,
)

from .conftest import create_cves, create_devices, create_inventory_items, create_softwares

User = get_user_model()


class HardwareLCMViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    """Test the HardwareLCM views."""

    model = HardwareLCM
    bulk_edit_data = {"documentation_url": "https://cisco.com/eox"}

    def _get_base_url(self):
        return "plugins:{}:{}_{{}}".format(  # pylint: disable=consider-using-f-string
            self.model._meta.app_label,
            self.model._meta.model_name,  # pylint: disable=protected-access
        )

    @classmethod
    def setUpTestData(cls):  # pylint: disable=invalid-name
        """Create a superuser and token for API calls."""
        manufacturer, _ = Manufacturer.objects.get_or_create(name="Cisco")
        device_types = tuple(
            DeviceType.objects.get_or_create(model=model, manufacturer=manufacturer)[0]
            for model in ["c9300-24", "c9300-48", "c9500-24", "c9500-48", "c9200-24", "c9200-48"]
        )

        HardwareLCM.objects.create(device_type=device_types[0], end_of_sale=datetime.date(2021, 4, 1))
        HardwareLCM.objects.create(device_type=device_types[1], end_of_sale=datetime.date(2021, 4, 1))
        HardwareLCM.objects.create(device_type=device_types[2], end_of_sale=datetime.date(2021, 4, 1))

        cls.form_data = {
            "device_type": device_types[3].id,
            "end_of_sale": datetime.date(2021, 4, 1),
            "end_of_support": datetime.date(2024, 4, 1),
        }
        cls.csv_data = (
            "device_type,end_of_sale,end_of_support,end_of_sw_releases,end_of_security_patches,documentation_url",
            f"{device_types[3].composite_key},2021-10-06,2022-10-06,2025-10-06,2026-10-06,https://cisco.com/eox",
            f"{device_types[4].composite_key},2022-10-06,2023-10-06,2025-10-06,2026-10-06,https://cisco.com/eox",
            f"{device_types[5].composite_key},2023-10-06,2024-10-06,2025-10-06,2026-10-06,https://cisco.com/eox",
        )


class ValidatedSoftwareDeviceReportViewTest(ViewTestCases.ListObjectsViewTestCase):
    """Test ValidatedSoftwareDeviceReportView"""

    model = DeviceSoftwareValidationResult

    def _get_base_url(self):
        return "plugins:nautobot_device_lifecycle_mgmt:validatedsoftware_device_report"

    @classmethod
    def setUpTestData(cls):  # pylint: disable=invalid-name
        """Set up test objects."""
        device_1, device_2, _ = create_devices()
        DeviceSoftwareValidationResult.objects.create(
            device=device_1,
            software=None,
            is_validated=False,
        )
        DeviceSoftwareValidationResult.objects.create(
            device=device_2,
            software=None,
            is_validated=False,
        )

    def test_validation_report_view_without_permission(self):
        """Test the SoftwareReportOverview."""

        self.assertHttpStatus(
            self.client.get(
                reverse(
                    "plugins:nautobot_device_lifecycle_mgmt:validatedsoftware_device_report",
                )
            ),
            403,
        )

    @skip("needs more testing")
    def test_validation_report_view_with_permission(self):
        """Test the SoftwareReportOverview."""
        obj_perm = ObjectPermission(name="Test permission", actions=["view"])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))
        self.assertHttpStatus(
            self.client.get(
                reverse(
                    "plugins:nautobot_device_lifecycle_mgmt:validatedsoftware_device_report",
                )
            ),
            200,
        )

    @skip("not implemented")
    def test_list_objects_unknown_filter_no_strict_filtering(self):
        pass

    @skip("not implemented")
    def test_list_objects_unknown_filter_strict_filtering(self):
        pass

    @skip("not implemented")
    def test_list_objects_with_permission(self):
        pass

    @skip("not implemented")
    def test_list_objects_filtered(self):
        pass

    @skip("not implemented")
    def test_list_objects_with_constrained_permission(self):
        pass

    @skip("not implemented")
    def test_list_objects_anonymous(self):
        pass


class ValidatedSoftwareInventoryItemReportViewTest(ViewTestCases.ListObjectsViewTestCase):
    """Test ValidatedSoftwareInventoryItemReportView"""

    model = InventoryItemSoftwareValidationResult

    def _get_base_url(self):
        return "plugins:nautobot_device_lifecycle_mgmt:validatedsoftware_inventoryitem_report"

    @classmethod
    def setUpTestData(cls):  # pylint: disable=invalid-name
        """Set up test objects."""
        inventory_items = create_inventory_items()
        InventoryItemSoftwareValidationResult.objects.create(
            inventory_item=inventory_items[0],
            software=None,
            is_validated=False,
        )
        InventoryItemSoftwareValidationResult.objects.create(
            inventory_item=inventory_items[1],
            software=None,
            is_validated=False,
        )
        InventoryItemSoftwareValidationResult.objects.create(
            inventory_item=inventory_items[2],
            software=None,
            is_validated=False,
        )

    def test_validation_report_view_without_permission(self):
        """Test the SoftwareReportOverview."""

        self.assertHttpStatus(
            self.client.get(
                reverse(
                    "plugins:nautobot_device_lifecycle_mgmt:validatedsoftware_inventoryitem_report",
                )
            ),
            403,
        )

    @skip("Needs more testing")
    def test_validation_report_view_with_permission(self):
        """Test the SoftwareReportOverview."""
        obj_perm = ObjectPermission(name="Test permission", actions=["view"])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))
        self.assertHttpStatus(
            self.client.get(
                reverse(
                    "plugins:nautobot_device_lifecycle_mgmt:validatedsoftware_inventoryitem_report",
                )
            ),
            200,
        )

    @skip("Not implemented")
    def test_list_objects_filtered(self):
        pass

    @skip("Not implemented")
    def test_list_objects_unknown_filter_no_strict_filtering(self):
        pass

    @skip("Not implemented")
    def test_list_objects_unknown_filter_strict_filtering(self):
        pass

    @skip("Not implemented")
    def test_list_objects_with_permission(self):
        pass

    @skip("Not implemented")
    def test_list_objects_with_constrained_permission(self):
        pass

    @skip("Not implemented")
    def test_list_objects_anonymous(self):
        pass


class CVELCMViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    """Test the CVELCM views."""

    model = CVELCM

    @classmethod
    def setUpTestData(cls):  # pylint: disable=invalid-name
        """Set up test objects."""
        create_cves()
        cls.bulk_edit_data = {
            "description": "Bulk edit views",
            "comments": "New",
            "status": Status.objects.get_for_model(CVELCM).first().pk,
        }

        cls.form_data = {
            "name": "Test 1",
            "published_date": datetime.date(2022, 1, 1),
            "link": "https://www.cvedetails.com/cve/CVE-2022-0001/",
        }

    @skip("Not implemented")
    def test_bulk_import_objects_with_permission(self):
        pass

    @skip("Not implemented")
    def test_bulk_import_objects_with_permission_csv_file(self):
        pass

    @skip("Not implemented")
    def test_create_object_with_constrained_permission(self):
        pass

    @skip("Not implemented")
    def test_bulk_import_objects_with_constrained_permission(self):
        pass


class VulnerabilityLCMViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    """Test the VulnerabilityLCM views."""

    model = VulnerabilityLCM

    @classmethod
    def setUpTestData(cls):  # pylint: disable=invalid-name
        """Set up test objects."""
        devices = create_devices()
        softwares = create_softwares()
        cves = create_cves()

        vuln_ct = ContentType.objects.get_for_model(VulnerabilityLCM)

        exempt_status, _ = Status.objects.get_or_create(
            name="Exempt", color="4caf50", description="This unit is exempt."
        )
        exempt_status.content_types.set([vuln_ct])
        cls.bulk_edit_data = {"status": exempt_status.pk}

        forced_status, _ = Status.objects.get_or_create(
            name="Forced", color="4caf50", description="This unit is forced."
        )
        forced_status.content_types.set([vuln_ct])

        for i, cve in enumerate(cves):
            VulnerabilityLCM.objects.create(cve=cve, software=softwares[i], device=devices[i], status=forced_status)

    @skip("Not implemented")
    def test_bulk_import_objects_with_constrained_permission(self):
        pass

    @skip("Not implemented")
    def test_bulk_import_objects_with_permission(self):
        pass

    @skip("Generated via job")
    def test_create_object_with_constrained_permission(self):
        pass

    @skip("Generated via job")
    def test_create_object_with_permission(self):
        pass

    @skip("Generated via job")
    def test_create_object_without_permission(self):
        pass

    @skip("Not implemented")
    def test_bulk_import_objects_with_permission_csv_file(self):
        pass

    @skip("Not implemented")
    def test_bulk_edit_objects_with_permission(self):
        pass

    @skip("Not implemented")
    def test_bulk_edit_objects_with_constrained_permission(self):
        pass


class DeviceSoftwareValidationResultListViewTest(ViewTestCases.ListObjectsViewTestCase):
    """Test DeviceSoftwareValidationResultListView"""

    model = DeviceSoftwareValidationResult

    def _get_base_url(self):
        return "plugins:nautobot_device_lifecycle_mgmt:devicesoftwarevalidationresult_list"

    @classmethod
    def setUpTestData(cls):  # pylint: disable=invalid-name
        """Set up test objects."""
        device_1, device_2, _ = create_devices()
        DeviceSoftwareValidationResult.objects.create(
            device=device_1,
            software=None,
            is_validated=False,
        )
        DeviceSoftwareValidationResult.objects.create(
            device=device_2,
            software=None,
            is_validated=False,
        )

    def test_device_software_list_view_without_permission(self):
        """Test the SoftwareReportOverview."""

        self.assertHttpStatus(
            self.client.get(
                reverse(
                    "plugins:nautobot_device_lifecycle_mgmt:devicesoftwarevalidationresult_list",
                )
            ),
            403,
        )

    def test_device_software_list_view_with_permission(self):
        """Test the SoftwareReportOverview."""
        obj_perm = ObjectPermission(name="Test permission", actions=["view"])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))
        self.assertHttpStatus(
            self.client.get(
                reverse(
                    "plugins:nautobot_device_lifecycle_mgmt:devicesoftwarevalidationresult_list",
                )
            ),
            200,
        )

    @skip("Not implemented")
    def test_list_objects_with_permission(self):
        pass

    @skip("Not implemented")
    def test_list_objects_with_constrained_permission(self):
        pass

    @skip("Not implemented")
    def test_list_objects_unknown_filter_no_strict_filtering(self):
        pass

    @skip("Not implemented")
    def test_list_objects_filtered(self):
        pass


class InventoryItemSoftwareValidationResultListViewTest(ViewTestCases.ListObjectsViewTestCase):
    """Test InventoryItemSoftwareValidationResultListView"""

    model = InventoryItemSoftwareValidationResult

    def _get_base_url(self):
        return "plugins:nautobot_device_lifecycle_mgmt:inventoryitemsoftwarevalidationresult_list"

    @classmethod
    def setUpTestData(cls):  # pylint: disable=invalid-name
        """Set up test objects."""
        inventory_items = create_inventory_items()
        InventoryItemSoftwareValidationResult.objects.create(
            inventory_item=inventory_items[0],
            software=None,
            is_validated=False,
        )
        InventoryItemSoftwareValidationResult.objects.create(
            inventory_item=inventory_items[1],
            software=None,
            is_validated=False,
        )
        InventoryItemSoftwareValidationResult.objects.create(
            inventory_item=inventory_items[2],
            software=None,
            is_validated=False,
        )

    def test_inventoryitem_software_list_view_without_permission(self):
        """Test the SoftwareReportOverview."""

        self.assertHttpStatus(
            self.client.get(
                reverse(
                    "plugins:nautobot_device_lifecycle_mgmt:inventoryitemsoftwarevalidationresult_list",
                )
            ),
            403,
        )

    def test_inventoryitem_software_list_view_with_permission(self):
        """Test the SoftwareReportOverview."""
        obj_perm = ObjectPermission(name="Test permission", actions=["view"])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))
        self.assertHttpStatus(
            self.client.get(
                reverse(
                    "plugins:nautobot_device_lifecycle_mgmt:inventoryitemsoftwarevalidationresult_list",
                )
            ),
            200,
        )

    @skip("Not implemented")
    def test_list_objects_with_permission(self):
        pass

    @skip("Not implemented")
    def test_list_objects_with_constrained_permission(self):
        pass

    @skip("Not implemented")
    def test_list_objects_unknown_filter_no_strict_filtering(self):
        pass

    @skip("Not implemented")
    def test_list_objects_filtered(self):
        pass

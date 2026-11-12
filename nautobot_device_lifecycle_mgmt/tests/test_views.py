# pylint: disable=no-member
"""Unit tests for views."""

import datetime
import html
import re
from unittest import skip
from urllib.parse import parse_qs, urlsplit

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from nautobot.apps.testing import TestCase, ViewTestCases
from nautobot.dcim.models import DeviceType, Manufacturer
from nautobot.extras.models import Status, Tag
from nautobot.users.models import ObjectPermission

from nautobot_device_lifecycle_mgmt.choices import ReportRunTypeChoices
from nautobot_device_lifecycle_mgmt.models import (
    CVELCM,
    DeviceHardwareNoticeResult,
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

        # Including tags in form_data makes the generic create/edit tests assert that they are persisted.
        tag = Tag.objects.create(name="Hardware Notice Tag")
        tag.content_types.add(ContentType.objects.get_for_model(HardwareLCM))

        cls.form_data = {
            "device_type": device_types[3].id,
            "end_of_sale": datetime.date(2021, 4, 1),
            "end_of_support": datetime.date(2024, 4, 1),
            "tags": [tag.pk],
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
        return "plugins:nautobot_device_lifecycle_mgmt:validatedsoftware_device_report_list"

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
                    "plugins:nautobot_device_lifecycle_mgmt:validatedsoftware_device_report_list",
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
                    "plugins:nautobot_device_lifecycle_mgmt:validatedsoftware_device_report_list",
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

    @skip("not implemented")
    def test_list_objects_anonymous_with_exempt_permission_for_one_view_only(self):
        pass


class ValidatedSoftwareInventoryItemReportViewTest(ViewTestCases.ListObjectsViewTestCase):
    """Test ValidatedSoftwareInventoryItemReportView"""

    model = InventoryItemSoftwareValidationResult

    def _get_base_url(self):
        return "plugins:nautobot_device_lifecycle_mgmt:validatedsoftware_inventoryitem_report_list"

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
                    "plugins:nautobot_device_lifecycle_mgmt:validatedsoftware_inventoryitem_report_list",
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
                    "plugins:nautobot_device_lifecycle_mgmt:validatedsoftware_inventoryitem_report_list",
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

        # Including tags in form_data makes the generic create/edit tests assert that they are persisted.
        tag = Tag.objects.create(name="CVE Tag")
        tag.content_types.add(ContentType.objects.get_for_model(CVELCM))

        cls.form_data = {
            "name": "Test 1",
            "published_date": datetime.date(2022, 1, 1),
            "link": "https://www.cvedetails.com/cve/CVE-2022-0001/",
            "tags": [tag.pk],
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


class HardwareNoticeBadgeTest(TestCase):
    """Test the hardware notice badges on core object pages."""

    def test_expiring_soon_badge(self):
        device = create_devices()[0]
        HardwareLCM.objects.create(
            device_type=device.device_type, end_of_support=datetime.date.today() + datetime.timedelta(days=30)
        )
        self.add_permissions(
            "dcim.view_device", "dcim.view_devicetype", "nautobot_device_lifecycle_mgmt.view_hardwarelcm"
        )
        for url in (device.get_absolute_url(), device.device_type.get_absolute_url()):
            with self.subTest(url=url):
                self.assertContains(self.client.get(url), "Expiring Soon")


class ReportCountLinkTest(TestCase):
    """Test that the count links on the report pages keep the report filters."""

    def get_report(self, view_name, status_filter):
        """Get the report filtered by location and `status_filter`, with the device type table rendered.

        The `HX-Request` header renders the table rows, as the HTMX request of a list view does.
        """
        return self.client.get(
            reverse(view_name),
            {"location": "Location1", **status_filter, "per_page": "10"},
            headers={"HX-Request": "true"},
        )

    def get_link_queries(self, response, view_name):
        """Return the query parameters of each link on the page to the given view."""
        url = reverse(view_name)
        hrefs = re.findall(f'href="{re.escape(url)}([^"]*)"', response.content.decode())
        return [parse_qs(urlsplit(html.unescape(href)).query) for href in hrefs]

    def assert_links_keep_location(self, links, expected_links):
        """Assert that each expected link exists with the location filter and without `per_page`."""
        for expected_link in expected_links:
            with self.subTest(link=expected_link):
                self.assertIn({"location": ["Location1"], **expected_link}, links)

    def test_device_software_report_links_keep_the_report_filters(self):
        devices = create_devices()
        software = create_softwares()[0]
        for device, device_software, is_validated in (
            (devices[0], software, True),
            (devices[1], software, False),
            (devices[2], None, False),
        ):
            DeviceSoftwareValidationResult(
                device=device,
                software=device_software,
                is_validated=is_validated,
                run_type=ReportRunTypeChoices.REPORT_FULL_RUN,
            ).validated_save()
        self.add_permissions("nautobot_device_lifecycle_mgmt.view_devicesoftwarevalidationresult")

        response = self.get_report(
            "plugins:nautobot_device_lifecycle_mgmt:validatedsoftware_device_report_list", {"valid": "True"}
        )

        self.assertHttpStatus(response, 200)
        links = self.get_link_queries(
            response, "plugins:nautobot_device_lifecycle_mgmt:devicesoftwarevalidationresult_list"
        )
        self.assert_links_keep_location(
            links,
            (
                {"valid": ["True"]},
                {"valid": ["False"], "exclude_sw_missing": ["True"]},
                {"valid": ["True"], "sw_missing_only": ["True"]},
                {"device_type": ["6509-E"], "valid": ["False"], "exclude_sw_missing": ["True"]},
            ),
        )

    def test_inventory_item_software_report_links_keep_the_report_filters(self):
        inventory_items = create_inventory_items()
        software = create_softwares()[0]
        for inventory_item, item_software, is_validated in (
            (inventory_items[0], software, True),
            (inventory_items[1], software, False),
            (inventory_items[2], None, False),
        ):
            InventoryItemSoftwareValidationResult(
                inventory_item=inventory_item,
                software=item_software,
                is_validated=is_validated,
                run_type=ReportRunTypeChoices.REPORT_FULL_RUN,
            ).validated_save()
        self.add_permissions("nautobot_device_lifecycle_mgmt.view_inventoryitemsoftwarevalidationresult")

        response = self.get_report(
            "plugins:nautobot_device_lifecycle_mgmt:validatedsoftware_inventoryitem_report_list", {"valid": "True"}
        )

        self.assertHttpStatus(response, 200)
        links = self.get_link_queries(
            response, "plugins:nautobot_device_lifecycle_mgmt:inventoryitemsoftwarevalidationresult_list"
        )
        self.assert_links_keep_location(
            links,
            (
                {"valid": ["True"]},
                {"valid": ["False"], "exclude_sw_missing": ["True"]},
                {"valid": ["True"], "sw_missing_only": ["True"]},
                {"part_id": ["VS-S2T-10G"], "valid": ["False"], "exclude_sw_missing": ["True"]},
            ),
        )

    def test_hardware_notice_report_links_keep_the_report_filters(self):
        devices = create_devices()
        hardware_notice = HardwareLCM(device_type=devices[0].device_type, end_of_support=datetime.date(2030, 1, 1))
        hardware_notice.validated_save()
        for device, is_supported in ((devices[0], True), (devices[1], False), (devices[2], False)):
            DeviceHardwareNoticeResult(
                device=device,
                hardware_notice=hardware_notice,
                is_supported=is_supported,
                run_type=ReportRunTypeChoices.REPORT_FULL_RUN,
            ).validated_save()
        self.add_permissions("nautobot_device_lifecycle_mgmt.view_devicehardwarenoticeresult")

        response = self.get_report(
            "plugins:nautobot_device_lifecycle_mgmt:hardwarenotice_device_report_list", {"supported": "True"}
        )

        self.assertHttpStatus(response, 200)
        summary_links = self.get_link_queries(
            response, "plugins:nautobot_device_lifecycle_mgmt:devicehardwarenoticeresult_list"
        )
        self.assert_links_keep_location(summary_links, ({"supported": ["True"]}, {"supported": ["False"]}))
        device_type_links = self.get_link_queries(
            response, "plugins:nautobot_device_lifecycle_mgmt:hardwarenotice_device_report_list"
        )
        self.assert_links_keep_location(device_type_links, ({"device_type": ["6509-E"], "supported": ["False"]},))

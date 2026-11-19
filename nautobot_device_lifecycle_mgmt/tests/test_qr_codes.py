"""Tests for the device QR codes and printable labels."""

from unittest import mock
from urllib.parse import unquote

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory, override_settings
from django.urls import reverse
from nautobot.apps.testing import TestCase
from nautobot.dcim.models import Device
from nautobot.extras.models import SavedView
from nautobot.users.models import ObjectPermission

from nautobot_device_lifecycle_mgmt import qr_codes
from nautobot_device_lifecycle_mgmt.views import DeviceLabelsView

from .conftest import create_devices


def app_settings(**overrides):
    """Return `PLUGINS_CONFIG` with the given app settings overridden."""
    app_config = {**settings.PLUGINS_CONFIG["nautobot_device_lifecycle_mgmt"], **overrides}
    return {**settings.PLUGINS_CONFIG, "nautobot_device_lifecycle_mgmt": app_config}


@override_settings(PLUGINS_CONFIG=app_settings(enable_qr_codes=True))
class DeviceQRCodeTest(TestCase):
    """Test the QR code button, the QR code download and the label sheet."""

    @classmethod
    def setUpTestData(cls):
        cls.sw1, cls.sw2, cls.sw3 = create_devices()
        cls.sw1.serial = "FOC1234X0AB"
        cls.sw1.asset_tag = "ASSET-0001"
        cls.sw1.validated_save()
        cls.labels_url = reverse("plugins:nautobot_device_lifecycle_mgmt:device_labels")

    def get_label_names(self, query_string=""):
        """Return the names of the devices on the label sheet for the given query string."""
        response = self.client.get(f"{self.labels_url}?{query_string}")
        self.assertHttpStatus(response, 200)
        return [label["device"].name for label in response.context["labels"]]

    def test_qr_code_encodes_absolute_device_url(self):
        request = RequestFactory().get("/")
        self.assertEqual(qr_codes.get_device_url(request, self.sw1), f"http://testserver/dcim/devices/{self.sw1.pk}/")

    def test_qr_code_has_white_background(self):
        request = RequestFactory().get("/")
        self.assertIn("fill='#fff'", unquote(qr_codes.get_device_qr_code_data_uri(request, self.sw1)))
        svg_file = qr_codes.get_device_qr_code_file(request, self.sw1, "svg")[0]
        self.assertIn(b'fill="#fff"', svg_file)

    def test_device_detail_page_shows_qr_code_button(self):
        self.add_permissions("dcim.view_device")
        response = self.client.get(self.sw1.get_absolute_url())
        self.assertHttpStatus(response, 200)
        self.assertContains(response, "data:image/svg+xml")
        self.assertContains(response, f"{self.labels_url}?id={self.sw1.pk}")

    def test_device_list_print_labels_button_keeps_filters(self):
        self.add_permissions("dcim.view_device")
        response = self.client.get(f"{reverse('dcim:device_list')}?location=Location1")
        self.assertHttpStatus(response, 200)
        self.assertContains(response, f"{self.labels_url}?location=Location1")

    def test_download_qr_code(self):
        url = reverse("plugins:nautobot_device_lifecycle_mgmt:device_qr_code", kwargs={"pk": self.sw1.pk})
        self.add_permissions("dcim.view_device")
        for query_string, content_type, file_name, magic in (
            ("", "image/svg+xml", "sw1-qr.svg", b"<?xml"),
            ("?format=png", "image/png", "sw1-qr.png", b"\x89PNG"),
        ):
            with self.subTest(content_type=content_type):
                response = self.client.get(f"{url}{query_string}")
                self.assertHttpStatus(response, 200)
                self.assertEqual(response["Content-Type"], content_type)
                self.assertEqual(response["Content-Disposition"], f'attachment; filename="{file_name}"')
                self.assertTrue(response.content.startswith(magic))

    def test_download_qr_code_requires_view_permission(self):
        url = reverse("plugins:nautobot_device_lifecycle_mgmt:device_qr_code", kwargs={"pk": self.sw1.pk})
        self.assertHttpStatus(self.client.get(url), 403)

    def test_labels_require_view_permission(self):
        self.assertHttpStatus(self.client.get(self.labels_url), 403)

    def test_labels_follow_device_list_filters(self):
        self.add_permissions("dcim.view_device")
        for query_string, expected in (
            ("", ["sw1", "sw2", "sw3"]),
            ("location=Location1", ["sw1", "sw2"]),
            (f"id={self.sw3.pk}", ["sw3"]),
            ("role=router&per_page=50&sort=name", ["sw3"]),
        ):
            with self.subTest(query_string=query_string):
                self.assertEqual(self.get_label_names(query_string), expected)

    def test_labels_show_serial_and_asset_tag(self):
        self.add_permissions("dcim.view_device")
        response = self.client.get(f"{self.labels_url}?id={self.sw1.pk}")
        self.assertContains(response, "S/N: FOC1234X0AB")
        self.assertContains(response, "Asset: ASSET-0001")

    def test_labels_use_saved_view_filters(self):
        self.add_permissions("dcim.view_device")
        saved_view = SavedView.objects.create(
            name="Location2 devices",
            owner=self.user,
            view="dcim:device_list",
            config={"filter_params": {"location": ["Location2"]}},
        )
        self.assertEqual(self.get_label_names(f"saved_view={saved_view.pk}"), ["sw3"])
        self.assertEqual(self.get_label_names("saved_view=not-a-saved-view"), ["sw1", "sw2", "sw3"])

    def test_labels_only_include_permitted_devices(self):
        obj_perm = ObjectPermission.objects.create(name="View sw2 only", actions=["view"], constraints={"name": "sw2"})
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(Device))
        self.assertEqual(self.get_label_names(), ["sw2"])

    def test_labels_report_invalid_filters(self):
        self.add_permissions("dcim.view_device")
        response = self.client.get(f"{self.labels_url}?not_a_filter=1")
        self.assertHttpStatus(response, 400)
        self.assertContains(response, "The Device list filters are not valid", status_code=400)

    def test_labels_are_capped(self):
        self.add_permissions("dcim.view_device")
        with mock.patch.object(DeviceLabelsView, "max_labels", 2):
            response = self.client.get(self.labels_url)
        self.assertEqual(len(response.context["labels"]), 2)
        self.assertContains(response, "Showing the first 2 of 3 devices")


@override_settings(PLUGINS_CONFIG=app_settings(enable_qr_codes=False))
class DeviceQRCodeDisabledTest(TestCase):
    """Test that the QR code features disappear when the `enable_qr_codes` app setting is off."""

    @classmethod
    def setUpTestData(cls):
        cls.sw1 = create_devices()[0]
        cls.labels_url = reverse("plugins:nautobot_device_lifecycle_mgmt:device_labels")

    def setUp(self):
        super().setUp()
        self.add_permissions("dcim.view_device")

    def test_qr_code_buttons_are_hidden(self):
        for url in (self.sw1.get_absolute_url(), reverse("dcim:device_list")):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertHttpStatus(response, 200)
                self.assertNotContains(response, "mdi-qrcode")
                self.assertNotContains(response, self.labels_url)

    def test_qr_code_views_return_not_found(self):
        qr_code_url = reverse("plugins:nautobot_device_lifecycle_mgmt:device_qr_code", kwargs={"pk": self.sw1.pk})
        for url in (qr_code_url, self.labels_url):
            with self.subTest(url=url):
                self.assertHttpStatus(self.client.get(url), 404)

"""Test tables."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from nautobot.extras.models import Tag
from nautobot.tenancy.models import Tenant

from nautobot_device_lifecycle_mgmt.models import DeviceSoftwareValidationResult, ValidatedSoftwareLCM
from nautobot_device_lifecycle_mgmt.tables import (
    ContractLCMTable,
    CVELCMTable,
    DeviceHardwareNoticeResultTable,
    DeviceSoftwareValidationResultListTable,
    DeviceSoftwareValidationResultTable,
    HardwareLCMTable,
    InventoryItemSoftwareValidationResultTable,
    ValidatedSoftwareLCMTable,
    VulnerabilityLCMTable,
)
from nautobot_device_lifecycle_mgmt.tests.conftest import (
    create_devices,
    create_inventory_items,
    create_validated_softwares,
)


# `base_columns` is added to each table by the django-tables2 metaclass, so pylint cannot see it.
class TaggableModelTableTest(TestCase):
    """Test the tags column on the list view tables of taggable Lifecycle Management models."""

    table_classes = (
        HardwareLCMTable,
        ValidatedSoftwareLCMTable,
        ContractLCMTable,
        CVELCMTable,
        VulnerabilityLCMTable,
    )

    def test_tags_column_is_available(self):
        """The tags column must be selectable in the table configuration."""
        for table_class in self.table_classes:
            with self.subTest(table=table_class.__name__):
                self.assertIn("tags", table_class.base_columns)  # pylint: disable=no-member

    def test_tags_column_is_not_a_default_column(self):
        """The tags column must be hidden until a user opts into it."""
        for table_class in self.table_classes:
            with self.subTest(table=table_class.__name__):
                default_columns = getattr(table_class.Meta, "default_columns", [])
                # Without default_columns nothing is hidden, so every column in `fields` shows by default.
                self.assertTrue(default_columns, "default_columns must be set for tags to be hidden by default")
                self.assertNotIn("tags", default_columns)

    def test_tags_column_links_to_filtered_list_view(self):
        """Tag badges link to the list view filtered by tag, so the column needs a reversible url_name."""
        for table_class in self.table_classes:
            with self.subTest(table=table_class.__name__):
                tags_column = table_class.base_columns["tags"]  # pylint: disable=no-member
                url_name = tags_column.extra_context.get("url_name")
                self.assertIsNotNone(url_name)
                self.assertTrue(reverse(url_name))


class ReportTableLinkTest(TestCase):
    """Test the filtered links on the report tables grouped by device type or part ID."""

    def test_links_url_encode_the_filter_value(self):
        """A `+` in a model or part ID must reach the linked view as `%2B`, not be decoded as a space."""
        device_type_row = {"device__device_type__model": "C9300-24P+", "total": 2, "valid": 1, "invalid": 1}
        part_id_row = {"inventory_item__part_id": "C9300-NM-8X+", "total": 2, "valid": 1, "invalid": 1}
        cases = (
            (
                DeviceHardwareNoticeResultTable,
                device_type_row,
                "device_type=C9300-24P%2B",
                ("name", "total", "valid", "invalid", "actions"),
            ),
            (
                DeviceSoftwareValidationResultTable,
                device_type_row,
                "device_type=C9300-24P%2B",
                ("name", "total", "valid", "invalid", "no_software", "actions"),
            ),
            (
                InventoryItemSoftwareValidationResultTable,
                part_id_row,
                "part_id=C9300-NM-8X%2B",
                ("part_id", "total", "valid", "invalid", "no_software", "actions"),
            ),
        )
        for table_class, row, expected_filter, column_names in cases:
            table_row = table_class([row]).rows[0]
            for column_name in column_names:
                with self.subTest(table=table_class.__name__, column=column_name):
                    self.assertIn(expected_filter, str(table_row.get_cell(column_name)))  # pylint: disable=no-member


class DeviceSoftwareValidationResultListTableTest(TestCase):
    """Test the Location column on the device software validation result list table."""

    def test_location_column_is_not_a_default_column(self):
        """The Location column is selectable but hidden until a user opts into it."""
        self.assertIn("location", DeviceSoftwareValidationResultListTable.base_columns)  # pylint: disable=no-member
        self.assertNotIn("location", DeviceSoftwareValidationResultListTable.Meta.default_columns)

    def test_location_column_links_to_device_location(self):
        """The Location column shows the device's location as a link."""
        device = create_devices()[0]
        DeviceSoftwareValidationResult.objects.create(device=device)
        table = DeviceSoftwareValidationResultListTable(DeviceSoftwareValidationResult.objects.all())
        cell = str(table.rows[0].get_cell("location"))  # pylint: disable=no-member
        self.assertIn(device.location.get_absolute_url(), cell)
        self.assertIn(device.location.name, cell)


class ValidatedSoftwareLCMTableTest(TestCase):
    """Test the relationship columns on the Validated Software list table."""

    relationship_columns = ("device_count", "device_types", "device_roles", "inventory_item_count", "object_tags")

    def test_relationship_columns_are_not_default_columns(self):
        """The relationship columns are selectable but hidden until a user opts into them."""
        for column_name in self.relationship_columns:
            with self.subTest(column=column_name):
                self.assertIn(column_name, ValidatedSoftwareLCMTable.base_columns)  # pylint: disable=no-member
                self.assertNotIn(column_name, ValidatedSoftwareLCMTable.Meta.default_columns)

    def test_relationship_columns_link_to_related_objects(self):
        """Related objects are linked, and device and inventory item counts link to the filtered list views."""
        validated_software = create_validated_softwares()[2]
        inventory_items = create_inventory_items()[:2]
        devices = [inventory_item.device for inventory_item in inventory_items]
        tag = Tag.objects.create(name="Table Test Tag")
        tenant = Tenant.objects.create(name="Table Test Tenant")
        validated_software.devices.set(devices)
        validated_software.device_roles.set([devices[0].role])
        validated_software.inventory_items.set(inventory_items)
        validated_software.object_tags.set([tag])
        validated_software.device_tenants.set([tenant])
        user = get_user_model().objects.create_user(username="table-test-user")
        user.set_config(
            "tables.ValidatedSoftwareLCMTable.columns",
            ["name", "device_tenants", *self.relationship_columns],
            commit=True,
        )

        table = ValidatedSoftwareLCMTable(ValidatedSoftwareLCM.objects.filter(pk=validated_software.pk), user=user)
        table_row = table.rows[0]
        filter_query = f"?nautobot_device_lifecycle_mgmt_validated_software={validated_software.pk}"
        expected_links = {
            "device_count": reverse("dcim:device_list") + filter_query,
            "inventory_item_count": reverse("dcim:inventoryitem_list") + filter_query,
            "device_types": validated_software.device_types.first().get_absolute_url(),
            "device_roles": devices[0].role.get_absolute_url(),
            "object_tags": tag.get_absolute_url(),
            "device_tenants": tenant.get_absolute_url(),
        }
        for column_name, url in expected_links.items():
            with self.subTest(column=column_name):
                self.assertIn(url, str(table_row.get_cell(column_name)))  # pylint: disable=no-member

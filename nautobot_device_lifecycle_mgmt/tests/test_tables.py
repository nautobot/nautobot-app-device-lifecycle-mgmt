"""Test tables."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from nautobot.extras.models import Tag
from nautobot.tenancy.models import Tenant

from nautobot_device_lifecycle_mgmt.models import ValidatedSoftwareLCM
from nautobot_device_lifecycle_mgmt.tables import (
    ContractLCMTable,
    CVELCMTable,
    HardwareLCMTable,
    ValidatedSoftwareLCMTable,
    VulnerabilityLCMTable,
)
from nautobot_device_lifecycle_mgmt.tests.conftest import create_inventory_items, create_validated_softwares


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

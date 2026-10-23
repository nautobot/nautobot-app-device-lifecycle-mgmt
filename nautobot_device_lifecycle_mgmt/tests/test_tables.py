"""Test tables."""

from django.test import TestCase
from django.urls import reverse

from nautobot_device_lifecycle_mgmt.tables import (
    ContractLCMTable,
    CVELCMTable,
    DeviceHardwareNoticeResultTable,
    DeviceSoftwareValidationResultTable,
    HardwareLCMTable,
    InventoryItemSoftwareValidationResultTable,
    ValidatedSoftwareLCMTable,
    VulnerabilityLCMTable,
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

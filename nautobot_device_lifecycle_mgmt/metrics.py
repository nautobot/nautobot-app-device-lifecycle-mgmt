"""Nautobot Device LCM plugin application level metrics ."""
from datetime import datetime

from django.db.models import Count, F, IntegerField, OuterRef, Q, Subquery, Value
from django.db.models.functions import Coalesce
from nautobot.dcim.models import Device, DeviceType, InventoryItem, Site
from prometheus_client.core import GaugeMetricFamily

from nautobot_device_lifecycle_mgmt.models import (
    DeviceSoftwareValidationResult,
    HardwareLCM,
    InventoryItemSoftwareValidationResult,
)


def metrics_lcm_validation_report_device_type():
    """Calculate number of devices with valid/invalid software by device_type.

    Yields:
        GaugeMetricFamily: Prometheus Metrics
    """
    device_software_compliance_gauge = GaugeMetricFamily(
        "nautobot_lcm_software_compliance_per_device_type",
        "Number of devices that have valid/invalid software by device_type",
        labels=["device_type", "is_valid"],
    )

    device_types = DeviceType.objects.values("model")

    # Annotate DeviceSoftwareValidationResult with counts for valid and invalid software per device type
    validation_counts = (
        DeviceSoftwareValidationResult.objects.order_by()
        .values(model=F("device__device_type__model"))
        .annotate(
            invalid_count=Count("device__device_type__model", filter=Q(is_validated=False)),
            valid_count=Count("device__device_type__model", filter=Q(is_validated=True)),
        )
        .values("model", "invalid_count", "valid_count")
    )

    # Set valid and invalid software validation counts to 0 for device types that don't have DeviceSoftwareValidationResult entry
    validation_counts_final = device_types.annotate(
        valid_count=Coalesce(
            Subquery(validation_counts.filter(model=OuterRef("model")).values("valid_count")), Value(0)
        ),
        invalid_count=Coalesce(
            Subquery(validation_counts.filter(model=OuterRef("model")).values("invalid_count")), Value(0)
        ),
    ).values_list("model", "valid_count", "invalid_count")

    for model, valid_count, invalid_count in validation_counts_final:
        device_software_compliance_gauge.add_metric(
            labels=[model, "True"],
            value=valid_count,
        )
        device_software_compliance_gauge.add_metric(
            labels=[model, "False"],
            value=invalid_count,
        )

    yield device_software_compliance_gauge


def metrics_lcm_validation_report_inventory_item():
    """Calculate number of inventory items with valid/invalid software.

    InventoryItem objects missing part_id are excluded.

    Yields:
        GaugeMetricFamily: Prometheus Metrics
    """
    inventory_item_software_compliance_gauge = GaugeMetricFamily(
        "nautobot_lcm_software_compliance_per_inventory_item",
        "Number of devices that have valid/invalid software by inventory item",
        labels=["inventory_item", "is_valid"],
    )
    inventory_item_part_ids = InventoryItem.objects.exclude(part_id="").order_by().values("part_id").distinct()

    # Annotate InventoryItemSoftwareValidationResult with counts for valid and invalid software per part id
    validation_counts = (
        InventoryItemSoftwareValidationResult.objects.exclude(inventory_item__part_id="")
        .order_by()
        .values(part_id=F("inventory_item__part_id"))
        .annotate(
            invalid_count=Count("inventory_item__part_id", filter=Q(is_validated=False)),
            valid_count=Count("inventory_item__part_id", filter=Q(is_validated=True)),
        )
        .values("part_id", "invalid_count", "valid_count")
    )

    # Set valid and invalid software validation counts to 0 for part ids that don't have InventoryItemSoftwareValidationResult entry
    validation_counts_final = inventory_item_part_ids.annotate(
        valid_count=Coalesce(
            Subquery(validation_counts.filter(part_id=OuterRef("part_id")).values("valid_count")), Value(0)
        ),
        invalid_count=Coalesce(
            Subquery(validation_counts.filter(part_id=OuterRef("part_id")).values("invalid_count")), Value(0)
        ),
    ).values_list("part_id", "valid_count", "invalid_count")

    for part_id, valid_count, invalid_count in validation_counts_final:
        inventory_item_software_compliance_gauge.add_metric(
            labels=[part_id, "True"],
            value=valid_count,
        )
        inventory_item_software_compliance_gauge.add_metric(
            labels=[part_id, "False"],
            value=invalid_count,
        )

    yield inventory_item_software_compliance_gauge


def metrics_lcm_hw_end_of_support():  # pylint: disable=too-many-locals
    """Calculate number of End of Support devices and inventory items per Part Number and per Site.

    Yields:
        GaugeMetricFamily: Prometheus Metrics
    """
    hw_end_of_support_part_number_gauge = GaugeMetricFamily(
        "nautobot_lcm_hw_end_of_support_per_part_number",
        "Nautobot LCM Hardware End of Support per Part Number",
        labels=["part_number"],
    )
    hw_end_of_support_site_gauge = GaugeMetricFamily(
        "nautobot_lcm_hw_end_of_support_per_site", "Nautobot LCM Hardware End of Support per Site", labels=["site"]
    )

    today = datetime.today().date()
    hw_end_of_support = HardwareLCM.objects.filter(end_of_support__lt=today)
    hw_end_of_support_device_types = hw_end_of_support.exclude(device_type__isnull=True).values_list(
        "device_type", flat=True
    )
    hw_end_of_support_invitems = hw_end_of_support.exclude(inventory_item__isnull=True).values_list(
        "inventory_item", flat=True
    )

    # Generate metrics with counts for out of support devices per device type
    for part_number, model, device_count in (
        DeviceType.objects.order_by()
        .annotate(num_devices=Count("instances", filter=Q(id__in=hw_end_of_support_device_types)))
        .values_list("part_number", "model", "num_devices")
    ):
        hw_end_of_support_part_number_gauge.add_metric(
            labels=[part_number if part_number else model], value=device_count
        )

    # Generate metrics with counts for out of support inventory items per part id
    for part_id, inv_item_count in (
        InventoryItem.objects.order_by()
        .filter(part_id__in=hw_end_of_support_invitems)
        .values("part_id")
        .annotate(inv_item_count=Count("id"))
        .values_list("part_id", "inv_item_count")
    ):
        hw_end_of_support_part_number_gauge.add_metric(labels=[part_id], value=inv_item_count)

    # Set metric value to 0 for inventory items that don't have corresponding HW notice
    # Case for inventory items that have non-empty part_id attribute
    for inv_item_part_id in (
        InventoryItem.objects.order_by()
        .filter(~Q(part_id__in=hw_end_of_support_invitems) & ~Q(part_id=""))
        .values_list("part_id", flat=True)
        .distinct()
    ):
        hw_end_of_support_part_number_gauge.add_metric(labels=[inv_item_part_id], value=0)

    # Set metric value to 0 for inventory items that don't have corresponding HW notice
    # Case for inventory items that have empty part_id attribute
    for inv_item_name in (
        InventoryItem.objects.order_by()
        .filter(~Q(part_id__in=hw_end_of_support_invitems) & Q(part_id=""))
        .values_list("name", flat=True)
        .distinct()
    ):
        hw_end_of_support_part_number_gauge.add_metric(labels=[inv_item_name], value=0)

    yield hw_end_of_support_part_number_gauge

    # Initialize per site count to 0 for all sites
    init_site_counts = Site.objects.values(site_slug=F("slug")).annotate(
        site_count=Value(0, output_field=IntegerField())
    )
    # Get count of out of hw support devices per site
    hw_end_of_support_per_site_devices = (
        Device.objects.order_by()
        .filter(device_type_id__in=hw_end_of_support_device_types)
        .values(site_slug=F("site__slug"))
        .annotate(site_count=Count("id"))
    )
    # Get count of out of hw support inventory items per site
    hw_end_of_support_per_site_invitems = (
        InventoryItem.objects.order_by()
        .filter(part_id__in=hw_end_of_support_invitems)
        .values(site_slug=F("device__site__slug"))
        .annotate(site_count=Count("id"))
    )

    # Build subqueries used in the final query offloading count sum to the DB
    hw_end_of_support_per_site_devices_sq = Subquery(
        hw_end_of_support_per_site_devices.filter(site_slug=OuterRef("site_slug")).values_list("site_count")
    )
    hw_end_of_support_per_site_invitems_sq = Subquery(
        hw_end_of_support_per_site_invitems.filter(site_slug=OuterRef("site_slug")).values_list("site_count")
    )
    # Build query summing counts per site and generate corresponding metrics
    for site_slug, total_count in init_site_counts.annotate(
        total_count=F("site_count")
        + Coalesce(hw_end_of_support_per_site_devices_sq, 0)
        + Coalesce(hw_end_of_support_per_site_invitems_sq, 0)
    ).values_list("site_slug", "total_count"):
        hw_end_of_support_site_gauge.add_metric(labels=[site_slug], value=total_count)

    yield hw_end_of_support_site_gauge


metrics = [
    metrics_lcm_hw_end_of_support,
    metrics_lcm_validation_report_device_type,
    metrics_lcm_validation_report_inventory_item,
]

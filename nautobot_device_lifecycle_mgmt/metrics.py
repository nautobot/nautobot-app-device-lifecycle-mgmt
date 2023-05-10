"""Nautobot Device LCM plugin application level metrics ."""
from datetime import datetime

from django.db.models import Case, Count, F, IntegerField, Q, When, Value, OuterRef, Subquery
from django.db.models.functions import Coalesce
from nautobot.dcim.models import Device, DeviceType, InventoryItem, Site
from prometheus_client.core import GaugeMetricFamily

from nautobot_device_lifecycle_mgmt.models import HardwareLCM


def metrics_lcm_hw_end_of_support():
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
        "nautobot_lcm_devices_eos_per_site", "Nautobot LCM Hardware End of Support per Site", labels=["site"]
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
        .annotate(
            num_devices=Case(
                When(id__in=hw_end_of_support_device_types, then=Count("instances")),
                default=0,
                output_field=IntegerField(),
            )
        )
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
]

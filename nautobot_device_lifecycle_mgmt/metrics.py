"""Nautobot Device LCM  plugin application level metrics ."""
from datetime import datetime

from django.conf import settings
from nautobot.dcim.models import Device, Site, InventoryItem, DeviceType
from prometheus_client.core import GaugeMetricFamily

from nautobot_device_lifecycle_mgmt.models import HardwareLCM

PLUGIN_SETTINGS = settings.PLUGINS_CONFIG.get("nautobot_device_lifecycle_mgmt", {})


def nautobot_metrics_dlcm_eos():
    """Calculate number of End-of-Support (EOS) devices per Device Type and per Site.

    Yields:
        GaugeMetricFamily: Prometheus Metrics
    """
    current_dt = datetime.now()
    hw_eos_notices = HardwareLCM.objects.filter(end_of_support__lte=current_dt)
    hw_eos_device_types = [notice.device_type for notice in hw_eos_notices]
    hw_eos_inventoryitems = [notice.inventory_item for notice in hw_eos_notices]

    part_number_gauge = GaugeMetricFamily(
        "nautobot_lcm_devices_eos_per_part_number", "Nautobot LCM Devices EOS per Part Number", labels=["part_number"]
    )
    devices_gauge = GaugeMetricFamily(
        "nautobot_lcm_devices_eos_per_site", "Nautobot LCM Devices EOS per Site", labels=["site"]
    )
    device_type_filter, inventory_item_filter = [], []
    for notice in hw_eos_notices:
        if notice.device_type:
            part_number = notice.device_type.part_number if notice.device_type.part_number else notice.device_type.slug
            metric_value = Device.objects.filter(device_type=notice.device_type).count()
            device_type_filter.append(notice.device_type.slug)
        elif notice.inventory_item:
            part_number = notice.inventory_item
            metric_value = InventoryItem.objects.filter(part_id=notice.inventory_item).count()
            inventory_item_filter.append(notice.inventory_item)

        part_number_gauge.add_metric(labels=[part_number], value=metric_value)

    device_types = DeviceType.objects.all().exclude(slug__in=device_type_filter)
    inventory_items = InventoryItem.objects.all().exclude(part_id__in=inventory_item_filter)

    for device_type in device_types:
        metric_value = 0
        part_number = device_type.part_number if device_type.part_number else device_type.slug
        part_number_gauge.add_metric(labels=[part_number], value=metric_value)

    for inventory_item in inventory_items:
        metric_value = 0
        part_number = inventory_item.part_id if inventory_item.part_id else inventory_item.slug
        part_number_gauge.add_metric(labels=[part_number], value=metric_value)

    yield part_number_gauge

    for site in Site.objects.all():
        eos_devices_in_site = Device.objects.filter(site=site, device_type__in=hw_eos_device_types).count()
        eos_inventoryitems_in_site = InventoryItem.objects.filter(
            part_id__in=hw_eos_inventoryitems, device__site=site.id
        ).count()
        metric_value = eos_devices_in_site + eos_inventoryitems_in_site
        devices_gauge.add_metric(labels=[site.slug], value=metric_value)

    yield devices_gauge


metrics = [nautobot_metrics_dlcm_eos]

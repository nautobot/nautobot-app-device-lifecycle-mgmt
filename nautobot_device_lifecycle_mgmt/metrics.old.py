"""Nautobot Device LCM  plugin application level metrics ."""
from datetime import datetime, timedelta

from django.conf import settings
from django.db.models import Count, Q
from nautobot.dcim.models import Device, Platform, Site, DeviceType
from prometheus_client import Gauge
from prometheus_client.core import GaugeMetricFamily

from nautobot_device_lifecycle_mgmt import choices
from nautobot_device_lifecycle_mgmt.models import (
    HardwareLCM,
    SoftwareLCM,
    ContactLCM,
    ValidatedSoftwareLCM,
    DeviceSoftwareValidationResult,
    InventoryItemSoftwareValidationResult,
    ContractLCM,
    ProviderLCM,
    CVELCM,
    VulnerabilityLCM,
    SoftwareImageLCM,
)

PLUGIN_SETTINGS = settings.PLUGINS_CONFIG.get("nautobot_device_lifecycle_mgmt", {})

def nautobot_metric_dlcm_eos_by_part_number():
    """Calculate number of devices EOS on a per SKU basis.
    Yields:
        GaugeMetricFamily: Prometheus Metrics
    """
    current_dt = datetime.now()
    hw_eos = HardwareLCM.objects.filter(end_of_support__lte=current_dt)

    part_number_gauge = GaugeMetricFamily(
            "nautobot_lcm_devices_eos_per_part_number", "Nautobot LCM Devices EOS per Part Number", labels=["hw_part"]
        )

    for hw_part in hw_eos:
        hw_parts_eos = DeviceType.objects.filter(part_number=hw_part)
        if hw_parts_eos:
            part_number_gauge.add_metric(
                labels=[hw_part],
                value=(hw_parts_eos.count()),
            )
        else:
            part_number_gauge.add_metric(
                labels=[hw_part],
                value=0,
            )

    yield part_number_gauge

def nautobot_metric_dlcm_eos_by_site():
    """Calculate number of devices EOS on a per Site basis.
    Yields:
        GaugeMetricFamily: Prometheus Metrics
    """
    current_dt = datetime.now()
    hw_eos = list(HardwareLCM.objects.filter(end_of_support__lte=current_dt))

    devices_gauge = GaugeMetricFamily(
            "nautobot_lcm_devices_eos_per_site", "Nautobot LCM Devices EOS per Site", labels=["Sites"]
        )

    for site in Site.objects.all():
        if site.devices.count():
            devices_gauge.add_metric(
                labels=[f'devices_eos in {site.slug}'],
                value=(DeviceType.objects.filter(id=site.id,part_number__in=hw_eos).count())
            )
        else:
            devices_gauge.add_metric(
                labels=[f'devices_eos in {site.slug}'],
                value=0,
            )

    yield devices_gauge

metrics=[nautobot_metric_dlcm_eos_by_site]

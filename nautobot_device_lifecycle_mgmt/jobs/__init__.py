"""Nautobot Jobs for the Device Lifecycle app."""

from nautobot.core.celery import register_jobs

from .cve_tracking import GenerateVulnerabilities
from .lifecycle_reporting import (
    DeviceHardwareNoticeFullReport,
    DeviceSoftwareValidationFullReport,
    InventoryItemSoftwareValidationFullReport,
)

jobs = [
    DeviceSoftwareValidationFullReport,
    DeviceHardwareNoticeFullReport,
    InventoryItemSoftwareValidationFullReport,
    GenerateVulnerabilities,
]
register_jobs(*jobs)

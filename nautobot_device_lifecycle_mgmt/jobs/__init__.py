"""Nautobot Jobs for the Device Lifecycle app."""

from nautobot.core.celery import register_jobs

from .cve_tracking import GenerateVulnerabilities, NistCveSyncSoftware
from .lifecycle_reporting import (
    DeviceHardwareNoticeFullReport,
    DeviceSoftwareValidationFullReport,
    InventoryItemSoftwareValidationFullReport,
)

jobs = [
    DeviceHardwareNoticeFullReport,
    DeviceSoftwareValidationFullReport,
    InventoryItemSoftwareValidationFullReport,
    GenerateVulnerabilities,
    NistCveSyncSoftware,
]
register_jobs(*jobs)

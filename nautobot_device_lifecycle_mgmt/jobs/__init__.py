"""Nautobot Jobs for the Device Lifecycle app."""

from nautobot.core.celery import register_jobs

from .cve_tracking import GenerateVulnerabilities, NistCveSyncSoftware
from .lifecycle_reporting import (
    DeviceHardwareNoticeFullReport,
    DeviceSoftwareValidationFullReport,
    InventoryItemSoftwareValidationFullReport,
)
from .model_migration import DLMToNautobotCoreModelMigration

jobs = [
    DeviceHardwareNoticeFullReport,
    DeviceSoftwareValidationFullReport,
    InventoryItemSoftwareValidationFullReport,
    GenerateVulnerabilities,
    DLMToNautobotCoreModelMigration,
    NistCveSyncSoftware,
]
register_jobs(*jobs)

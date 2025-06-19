"""Nautobot Jobs for the Device Lifecycle app."""

from nautobot.core.celery import register_jobs

from .cve_tracking import GenerateVulnerabilities, NistCveSyncSoftware
from .lifecycle_reporting import (
    DeviceHardwareNoticeFullReport,
    DeviceSoftwareValidationReport,
    InventoryItemSoftwareValidationFullReport,
)
from .model_migration import DLMToNautobotCoreModelMigration

jobs = [
    DeviceHardwareNoticeFullReport,
    DeviceSoftwareValidationReport,
    InventoryItemSoftwareValidationFullReport,
    GenerateVulnerabilities,
    DLMToNautobotCoreModelMigration,
    NistCveSyncSoftware,
]
register_jobs(*jobs)

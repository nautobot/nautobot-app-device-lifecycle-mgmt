"""Nautobot Jobs for the Device Lifecycle app."""

from nautobot.core.celery import register_jobs

from .cve_tracking import GenerateVulnerabilities
from .lifecycle_reporting import DeviceSoftwareValidationFullReport, InventoryItemSoftwareValidationFullReport
from .model_migration import DLMToNautoboCoreModelMigration

jobs = [
    DeviceSoftwareValidationFullReport,
    InventoryItemSoftwareValidationFullReport,
    GenerateVulnerabilities,
    DLMToNautoboCoreModelMigration,
]
register_jobs(*jobs)

"""Nautobot Jobs for the Device Lifecycle app."""

from nautobot.core.celery import register_jobs

from .cve_tracking import GenerateVulnerabilities
from .lifecycle_reporting import DeviceSoftwareValidationFullReport, InventoryItemSoftwareValidationFullReport
from .model_migration import DLMToNautoboCoreModelMigration, ExampleJobHookReceiver, ExampleSimpleJobButtonReceiver

jobs = [
    DeviceSoftwareValidationFullReport,
    InventoryItemSoftwareValidationFullReport,
    GenerateVulnerabilities,
    DLMToNautoboCoreModelMigration,
    ExampleSimpleJobButtonReceiver,
    ExampleJobHookReceiver,
]
register_jobs(*jobs)

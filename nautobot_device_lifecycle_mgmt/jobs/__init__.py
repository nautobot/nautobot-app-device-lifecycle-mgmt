"""Nautobot Jobs for the Device Lifecycle plugin."""
from .cve_tracking import GenerateVulnerabilities
from .lifecycle_reporting import DeviceSoftwareValidationFullReport, InventoryItemSoftwareValidationFullReport

jobs = [DeviceSoftwareValidationFullReport, InventoryItemSoftwareValidationFullReport, GenerateVulnerabilities]

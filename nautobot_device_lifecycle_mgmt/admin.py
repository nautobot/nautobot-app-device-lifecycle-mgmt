"""Admin interface for eox notices."""

from django.contrib import admin
from nautobot_device_lifecycle_mgmt.models import HardwareLCM


@admin.register(HardwareLCM)
class HardwareLCMAdmin(admin.ModelAdmin):
    """Admin form/display."""

    list_display = ("device_type", "end_of_sale", "end_of_support", "documentation_url")

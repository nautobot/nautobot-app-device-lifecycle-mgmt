"""Admin interface for eox notices."""

from django.contrib import admin
from .models import EoxNotice


@admin.register(EoxNotice)
class EoxAdmin(admin.ModelAdmin):
    list_display = ("device_type", "end_of_sale", "end_of_support", "notice_url")

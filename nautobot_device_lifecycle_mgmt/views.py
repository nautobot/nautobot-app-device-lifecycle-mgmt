"""Views for nautobot_device_lifecycle_mgmt."""

from nautobot.apps.views import NautobotUIViewSet

from nautobot_device_lifecycle_mgmt import filters, forms, models, tables
from nautobot_device_lifecycle_mgmt.api import serializers


class HardwareLCMUIViewSet(NautobotUIViewSet):
    """ViewSet for HardwareLCM views."""

    bulk_update_form_class = forms.HardwareLCMBulkEditForm
    filterset_class = filters.HardwareLCMFilterSet
    filterset_form_class = forms.HardwareLCMFilterForm
    form_class = forms.HardwareLCMForm
    lookup_field = "pk"
    queryset = models.HardwareLCM.objects.all()
    serializer_class = serializers.HardwareLCMSerializer
    table_class = tables.HardwareLCMTable

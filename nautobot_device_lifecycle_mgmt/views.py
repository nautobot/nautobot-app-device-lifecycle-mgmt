"""Views for nautobot_device_lifecycle_mgmt."""

from nautobot.apps.views import NautobotUIViewSet
from nautobot.apps.ui import ObjectDetailContent, ObjectFieldsPanel, ObjectsTablePanel, SectionChoices
from nautobot.core.templatetags import helpers

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

    # Here is an example of using the UI  Component Framework for the detail view.
    # More information can be found in the Nautobot documentation:
    # https://docs.nautobot.com/projects/core/en/stable/development/core/ui-component-framework/
    object_detail_content = ObjectDetailContent(
        panels=[
            ObjectFieldsPanel(
                weight=100,
                section=SectionChoices.LEFT_HALF,
                fields="__all__",
                # Alternatively, you can specify a list of field names:
                # fields=[
                #     "name",
                #     "description",
                # ],
                # Some fields may require additional configuration, we can use value_transforms
                # value_transforms={
                #     "name": [helpers.bettertitle]
                # },
            ),
            # If there is a ForeignKey or M2M with this model we can use ObjectsTablePanel
            # to display them in a table format.
            # ObjectsTablePanel(
                # weight=200,
                # section=SectionChoices.RIGHT_HALF,
                # table_class=tables.HardwareLCMTable,
                # You will want to filter the table using the related_name
                # filter="hardwarelcms",
            # ),
        ],
    )

"""Django urlpatterns declaration for the LifeCycle Management plugin."""
from django.urls import path
from nautobot.extras.views import ObjectChangeLogView
from nautobot_device_lifecycle_mgmt import views
from nautobot_device_lifecycle_mgmt.models import HardwareLCM


urlpatterns = [
    # Hardware LifeCycle Management URLs
    path("hardware-lcm/", views.HardwareLCMListView.as_view(), name="hardwarelcm_list"),
    path("hardware-lcm/<uuid:pk>/", views.HardwareLCMView.as_view(), name="hardwarelcm"),
    path("hardware-lcm/add/", views.HardwareLCMCreateView.as_view(), name="hardwarelcm_add"),
    path("hardware-lcm/delete/", views.HardwareLCMBulkDeleteView.as_view(), name="hardwarelcm_bulk_delete"),
    path("hardware-lcm/edit/", views.HardwareLCMBulkEditView.as_view(), name="hardwarelcm_bulk_edit"),
    path("hardware-lcm/<uuid:pk>/delete/", views.HardwareLCMDeleteView.as_view(), name="hardwarelcm_delete"),
    path("hardware-lcm/<uuid:pk>/edit/", views.HardwareLCMEditView.as_view(), name="hardwarelcm_edit"),
    path(
        "hardware-lcm/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="hardwarelcm_changelog",
        kwargs={"model": HardwareLCM},
    ),
    path("hardware-lcm/import/", views.HardwareLCMBulkImportView.as_view(), name="hardwarelcm_import"),
]

"""Django urlpatterns declaration for the LifeCycle Management plugin."""
from django.urls import path
from nautobot.extras.views import ObjectChangeLogView
from nautobot_plugin_device_lifecycle_mgmt import views
from nautobot_plugin_device_lifecycle_mgmt.models import HardwareLCM


urlpatterns = [
    path("hardware-lcm/", views.HardwareLCMNoticesListView.as_view(), name="hardwarelcm_list"),
    path("hardware-lcm/<uuid:pk>/", views.HardwareLCMNoticeView.as_view(), name="hardwarelcm"),
    path("hardware-lcm/add/", views.HardwareLCMNoticeCreateView.as_view(), name="hardwarelcm_add"),
    path("hardware-lcm/delete/", views.HardwareLCMNoticeBulkDeleteView.as_view(), name="hardwarelcm_bulk_delete"),
    path("hardware-lcm/edit/", views.HardwareLCMNoticeBulkEditView.as_view(), name="hardwarelcm_bulk_edit"),
    path("hardware-lcm/<uuid:pk>/delete/", views.HardwareLCMNoticeDeleteView.as_view(), name="hardwarelcm_delete"),
    path("hardware-lcm/<uuid:pk>/edit/", views.HardwareLCMNoticeEditView.as_view(), name="hardwarelcm_edit"),
    path(
        "hardware-lcm/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="hardwarelcm_changelog",
        kwargs={"model": HardwareLCM},
    ),
    path("hardware-lcm/import/", views.HardwareLCMNoticeBulkImportView.as_view(), name="hardwarelcm_import"),
]

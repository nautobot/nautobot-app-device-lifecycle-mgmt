"""Django urlpatterns declaration for nautobot_plugin_device_lifecycle_mgmt plugin."""
from django.urls import path
from nautobot.extras.views import ObjectChangeLogView
from nautobot_plugin_device_lifecycle_mgmt import views
from nautobot_plugin_device_lifecycle_mgmt.models import EoxNotice


urlpatterns = [
    path("eox-notice/", views.EoxNoticesListView.as_view(), name="eoxnotice_list"),
    path("eox-notice/<uuid:pk>/", views.EoxNoticeView.as_view(), name="eoxnotice"),
    path("eox-notice/add/", views.EoxNoticeCreateView.as_view(), name="eoxnotice_add"),
    path("eox-notice/delete/", views.EoxNoticeBulkDeleteView.as_view(), name="eoxnotice_bulk_delete"),
    path("eox-notice/edit/", views.EoxNoticeBulkEditView.as_view(), name="eoxnotice_bulk_edit"),
    path("eox-notice/<uuid:pk>/delete/", views.EoxNoticeDeleteView.as_view(), name="eoxnotice_delete"),
    path("eox-notice/<uuid:pk>/edit/", views.EoxNoticeEditView.as_view(), name="eoxnotice_edit"),
    path(
        "eox-notice/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="eoxnotice_changelog",
        kwargs={"model": EoxNotice},
    ),
    path("eox-notice/import/", views.EoxNoticeBulkImportView.as_view(), name="eoxnotice_import"),
]

"""Django urlpatterns declaration for the LifeCycle Management plugin."""
from django.urls import path
from nautobot.extras.views import ObjectChangeLogView
from nautobot_device_lifecycle_mgmt import views
from nautobot_device_lifecycle_mgmt.models import HardwareLCM, SoftwareLCM, ValidatedSoftwareLCM


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
    # Software LifeCycle Management URLs
    path("software/", views.SoftwareLCMListView.as_view(), name="softwarelcm_list"),
    path("software/<uuid:pk>/", views.SoftwareLCMView.as_view(), name="softwarelcm"),
    path("software/add/", views.SoftwareLCMCreateView.as_view(), name="softwarelcm_add"),
    path("software/<uuid:pk>/delete/", views.SoftwareLCMDeleteView.as_view(), name="softwarelcm_delete"),
    path("software/<uuid:pk>/edit/", views.SoftwareLCMEditView.as_view(), name="softwarelcm_edit"),
    path(
        "software/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="softwarelcm_changelog",
        kwargs={"model": SoftwareLCM},
    ),
    # ValidatedSoftware
    path("validated-software/", views.ValidatedSoftwareLCMListView.as_view(), name="validatedsoftwarelcm_list"),
    path("validated-software/<uuid:pk>/", views.ValidatedSoftwareLCMView.as_view(), name="validatedsoftwarelcm"),
    path("validated-software/add/", views.ValidatedSoftwareLCMEditView.as_view(), name="validatedsoftwarelcm_add"),
    path(
        "validated-software/<uuid:pk>/delete/",
        views.ValidatedSoftwareLCMDeleteView.as_view(),
        name="validatedsoftwarelcm_delete",
    ),
    path(
        "validated-software/<uuid:pk>/edit/",
        views.ValidatedSoftwareLCMEditView.as_view(),
        name="validatedsoftwarelcm_edit",
    ),
    path(
        "validated-software/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="validatedsoftwarelcm_changelog",
        kwargs={"model": ValidatedSoftwareLCM},
    ),
]

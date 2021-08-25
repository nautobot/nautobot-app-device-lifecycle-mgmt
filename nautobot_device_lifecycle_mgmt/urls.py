"""Django urlpatterns declaration for the LifeCycle Management plugin."""
from django.urls import path
from nautobot.extras.views import ObjectChangeLogView
from nautobot_device_lifecycle_mgmt import views
from nautobot_device_lifecycle_mgmt.models import (
    HardwareLCM,
    SoftwareLCM,
    ValidatedSoftwareLCM,
    ContractLCM,
    ProviderLCM,
)


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
    # Contract LifeCycle Management URLs
    path("contract-lcm/", views.ContractLCMListView.as_view(), name="contractlcm_list"),
    path("contract-lcm/<uuid:pk>/", views.ContractLCMView.as_view(), name="contractlcm"),
    path("contract-lcm/add/", views.ContractLCMCreateView.as_view(), name="contractlcm_add"),
    path("contract-lcm/delete/", views.ContractLCMBulkDeleteView.as_view(), name="contractlcm_bulk_delete"),
    path("contract-lcm/edit/", views.ContractLCMBulkEditView.as_view(), name="contractlcm_bulk_edit"),
    path("contract-lcm/<uuid:pk>/delete/", views.ContractLCMDeleteView.as_view(), name="contractlcm_delete"),
    path("contract-lcm/<uuid:pk>/edit/", views.ContractLCMEditView.as_view(), name="contractlcm_edit"),
    path(
        "contract-lcm/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="contractlcm_changelog",
        kwargs={"model": ContractLCM},
    ),
    path("contract-lcm/import/", views.ContractLCMBulkImportView.as_view(), name="contractlcm_import"),
    # Contract Provider LifeCycle Management URLs
    path("provider-lcm/", views.ProviderLCMListView.as_view(), name="providerlcm_list"),
    path("provider-lcm/<uuid:pk>/", views.ProviderLCMView.as_view(), name="providerlcm"),
    path("provider-lcm/add/", views.ProviderLCMCreateView.as_view(), name="providerlcm_add"),
    path("provider-lcm/delete/", views.ProviderLCMBulkDeleteView.as_view(), name="providerlcm_bulk_delete"),
    path("provider-lcm/edit/", views.ProviderLCMBulkEditView.as_view(), name="providerlcm_bulk_edit"),
    path("provider-lcm/<uuid:pk>/delete/", views.ProviderLCMDeleteView.as_view(), name="providerlcm_delete"),
    path("provider-lcm/<uuid:pk>/edit/", views.ProviderLCMEditView.as_view(), name="providerlcm_edit"),
    path(
        "provider-lcm/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="providerlcm_changelog",
        kwargs={"model": ProviderLCM},
    ),
    path("contract-lcm/import/", views.ProviderLCMBulkImportView.as_view(), name="providerlcm_import"),
]

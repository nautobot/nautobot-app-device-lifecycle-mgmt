"""Django urlpatterns declaration for the Lifecycle Management plugin."""
from django.urls import path
from nautobot.extras.views import ObjectChangeLogView
from nautobot_device_lifecycle_mgmt import views
from nautobot_device_lifecycle_mgmt.models import (
    HardwareLCM,
    SoftwareImageLCM,
    SoftwareLCM,
    ValidatedSoftwareLCM,
    ContractLCM,
    ProviderLCM,
    ContactLCM,
    CVELCM,
    VulnerabilityLCM,
)


urlpatterns = [
    # Hardware Lifecycle Management URLs
    path("hardware/", views.HardwareLCMListView.as_view(), name="hardwarelcm_list"),
    path("hardware/<uuid:pk>/", views.HardwareLCMView.as_view(), name="hardwarelcm"),
    path("hardware/add/", views.HardwareLCMCreateView.as_view(), name="hardwarelcm_add"),
    path("hardware/delete/", views.HardwareLCMBulkDeleteView.as_view(), name="hardwarelcm_bulk_delete"),
    path("hardware/edit/", views.HardwareLCMBulkEditView.as_view(), name="hardwarelcm_bulk_edit"),
    path("hardware/<uuid:pk>/delete/", views.HardwareLCMDeleteView.as_view(), name="hardwarelcm_delete"),
    path("hardware/<uuid:pk>/edit/", views.HardwareLCMEditView.as_view(), name="hardwarelcm_edit"),
    path(
        "hardware/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="hardwarelcm_changelog",
        kwargs={"model": HardwareLCM},
    ),
    path("hardware/import/", views.HardwareLCMBulkImportView.as_view(), name="hardwarelcm_import"),
    # Software Lifecycle Management URLs
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
    path("software/import/", views.SoftwareLCMBulkImportView.as_view(), name="softwarelcm_import"),
    path(
        "software/<uuid:pk>/software-images/",
        views.SoftwareSoftwareImagesLCMView.as_view(),
        name="software_software_images",
    ),
    # SoftwareImage
    path("software-image/", views.SoftwareImageLCMListView.as_view(), name="softwareimagelcm_list"),
    path("software-image/<uuid:pk>/", views.SoftwareImageLCMView.as_view(), name="softwareimagelcm"),
    path("software-image/add/", views.SoftwareImageLCMEditView.as_view(), name="softwareimagelcm_add"),
    path("software-image/delete/", views.SoftwareImageLCMBulkDeleteView.as_view(), name="softwareimagelcm_bulk_delete"),
    path(
        "software-image/<uuid:pk>/delete/", views.SoftwareImageLCMDeleteView.as_view(), name="softwareimagelcm_delete"
    ),
    path("software-image/<uuid:pk>/edit/", views.SoftwareImageLCMEditView.as_view(), name="softwareimagelcm_edit"),
    path(
        "software-image/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="softwareimagelcm_changelog",
        kwargs={"model": SoftwareImageLCM},
    ),
    path(
        "software-image/import/",
        views.SoftwareImageLCMBulkImportView.as_view(),
        name="softwareimagelcm_import",
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
    path(
        "validated-software/import/",
        views.ValidatedSoftwareLCMBulkImportView.as_view(),
        name="validatedsoftwarelcm_import",
    ),
    path(
        "validated-software/device-report/",
        views.ValidatedSoftwareDeviceReportView.as_view(),
        name="validatedsoftware_device_report",
    ),
    path(
        "validated-software/inventoryitem-report/",
        views.ValidatedSoftwareInventoryItemReportView.as_view(),
        name="validatedsoftware_inventoryitem_report",
    ),
    # Contract Lifecycle Management URLs
    path("contract/", views.ContractLCMListView.as_view(), name="contractlcm_list"),
    path("contract/<uuid:pk>/", views.ContractLCMView.as_view(), name="contractlcm"),
    path("contract/add/", views.ContractLCMCreateView.as_view(), name="contractlcm_add"),
    path("contract/delete/", views.ContractLCMBulkDeleteView.as_view(), name="contractlcm_bulk_delete"),
    path("contract/edit/", views.ContractLCMBulkEditView.as_view(), name="contractlcm_bulk_edit"),
    path("contract/<uuid:pk>/delete/", views.ContractLCMDeleteView.as_view(), name="contractlcm_delete"),
    path("contract/<uuid:pk>/edit/", views.ContractLCMEditView.as_view(), name="contractlcm_edit"),
    path(
        "contract/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="contractlcm_changelog",
        kwargs={"model": ContractLCM},
    ),
    path("contract/import/", views.ContractLCMBulkImportView.as_view(), name="contractlcm_import"),
    # Contract Provider Lifecycle Management URLs
    path("provider/", views.ProviderLCMListView.as_view(), name="providerlcm_list"),
    path("provider/<uuid:pk>/", views.ProviderLCMView.as_view(), name="providerlcm"),
    path("provider/add/", views.ProviderLCMCreateView.as_view(), name="providerlcm_add"),
    path("provider/delete/", views.ProviderLCMBulkDeleteView.as_view(), name="providerlcm_bulk_delete"),
    path("provider/edit/", views.ProviderLCMBulkEditView.as_view(), name="providerlcm_bulk_edit"),
    path("provider/<uuid:pk>/delete/", views.ProviderLCMDeleteView.as_view(), name="providerlcm_delete"),
    path("provider/<uuid:pk>/edit/", views.ProviderLCMEditView.as_view(), name="providerlcm_edit"),
    path(
        "provider/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="providerlcm_changelog",
        kwargs={"model": ProviderLCM},
    ),
    path("provider/import/", views.ProviderLCMBulkImportView.as_view(), name="providerlcm_import"),
    # Contract Resources Lifecycle Management URLs
    path("contact/", views.ContactLCMListView.as_view(), name="contactlcm_list"),
    path("contact/<uuid:pk>/", views.ContactLCMView.as_view(), name="contactlcm"),
    path("contact/add/", views.ContactLCMCreateView.as_view(), name="contactlcm_add"),
    path("contact/delete/", views.ContactLCMBulkDeleteView.as_view(), name="contactlcm_bulk_delete"),
    path("contact/edit/", views.ContactLCMBulkEditView.as_view(), name="contactlcm_bulk_edit"),
    path("contact/<uuid:pk>/delete/", views.ContactLCMDeleteView.as_view(), name="contactlcm_delete"),
    path("contact/<uuid:pk>/edit/", views.ContactLCMEditView.as_view(), name="contactlcm_edit"),
    path(
        "contact/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="contactlcm_changelog",
        kwargs={"model": ContactLCM},
    ),
    path("contact/import/", views.ContactLCMBulkImportView.as_view(), name="contactlcm_import"),
    # CVE Lifecycle Management URLs
    path("cve/", views.CVELCMListView.as_view(), name="cvelcm_list"),
    path("cve/<uuid:pk>/", views.CVELCMView.as_view(), name="cvelcm"),
    path("cve/add/", views.CVELCMCreateView.as_view(), name="cvelcm_add"),
    path("cve/delete/", views.CVELCMBulkDeleteView.as_view(), name="cvelcm_bulk_delete"),
    path("cve/edit/", views.CVELCMBulkEditView.as_view(), name="cvelcm_bulk_edit"),
    path("cve/<uuid:pk>/delete/", views.CVELCMDeleteView.as_view(), name="cvelcm_delete"),
    path("cve/<uuid:pk>/edit/", views.CVELCMEditView.as_view(), name="cvelcm_edit"),
    path(
        "cve/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="cvelcm_changelog",
        kwargs={"model": CVELCM},
    ),
    path("cve/import/", views.CVELCMBulkImportView.as_view(), name="cvelcm_import"),
    # Vulnerability Lifecycle Management URLs
    path("vulnerability/", views.VulnerabilityLCMListView.as_view(), name="vulnerabilitylcm_list"),
    path("vulnerability/<uuid:pk>/", views.VulnerabilityLCMView.as_view(), name="vulnerabilitylcm"),
    path("vulnerability/delete/", views.VulnerabilityLCMBulkDeleteView.as_view(), name="vulnerabilitylcm_bulk_delete"),
    path("vulnerability/edit/", views.VulnerabilityLCMBulkEditView.as_view(), name="vulnerabilitylcm_bulk_edit"),
    path("vulnerability/<uuid:pk>/delete/", views.VulnerabilityLCMDeleteView.as_view(), name="vulnerabilitylcm_delete"),
    path("vulnerability/<uuid:pk>/edit/", views.VulnerabilityLCMEditView.as_view(), name="vulnerabilitylcm_edit"),
    path(
        "vulnerability/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="vulnerabilitylcm_changelog",
        kwargs={"model": VulnerabilityLCM},
    ),
]

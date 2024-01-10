"""Django urlpatterns declaration for the Lifecycle Management app."""
from django.urls import path
from nautobot.apps.urls import NautobotUIViewSetRouter

from nautobot_device_lifecycle_mgmt import views, viewsets

router = NautobotUIViewSetRouter()
router.register("hardware", viewset=viewsets.HardwareLCMUIViewSet)
router.register("software", viewset=viewsets.SoftwareLCMUIViewSet)
router.register("software-image", viewset=viewsets.SoftwareImageLCMUIViewSet)
router.register("validated-software", viewset=viewsets.ValidatedSoftwareLCMUIViewSet)
router.register("contract", viewset=viewsets.ContractLCMUIViewSet)
router.register("provider", viewset=viewsets.ProviderLCMUIViewSet)
router.register("contact", viewset=viewsets.ContactLCMUIViewSet)
router.register("cve", viewset=viewsets.CVELCMUIViewSet)
router.register("vulnerability", viewset=viewsets.VulnerabilityLCMUIViewSet)

urlpatterns = router.urls

urlpatterns += [
    path(
        "software/<uuid:pk>/software-images/",
        views.SoftwareSoftwareImagesLCMView.as_view(),
        name="software_software_images",
    ),
    path(
        "validated-software-device-report/",
        views.ValidatedSoftwareDeviceReportView.as_view(),
        name="validatedsoftware_device_report",
    ),
    path(
        "validated-software-inventoryitem-report/",
        views.ValidatedSoftwareInventoryItemReportView.as_view(),
        name="validatedsoftware_inventoryitem_report",
    ),
    # DeviceValidatedSoftwareResult
    path(
        "device-validated-software-result/",
        views.DeviceSoftwareValidationResultListView.as_view(),
        name="devicesoftwarevalidationresult_list",
    ),
    # InventoryItemValidatedSoftwareResult
    path(
        "inventory-item-validated-software-result/",
        views.InventoryItemSoftwareValidationResultListView.as_view(),
        name="inventoryitemsoftwarevalidationresult_list",
    ),
]

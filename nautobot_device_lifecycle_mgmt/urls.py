"""Django urlpatterns declaration for the Lifecycle Management app."""

from django.urls import path
from django.templatetags.static import static
from django.views.generic import RedirectView

from nautobot.apps.urls import NautobotUIViewSetRouter

from nautobot_device_lifecycle_mgmt import views

router = NautobotUIViewSetRouter()
router.register("hardware", viewset=views.HardwareLCMUIViewSet)
router.register("validated-software", viewset=views.ValidatedSoftwareLCMUIViewSet)
router.register("contract", viewset=views.ContractLCMUIViewSet)
router.register("provider", viewset=views.ProviderLCMUIViewSet)
router.register("cve", viewset=views.CVELCMUIViewSet)
router.register("vulnerability", viewset=views.VulnerabilityLCMUIViewSet)

urlpatterns = router.urls

urlpatterns += [
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
    path(
        "docs/",
        RedirectView.as_view(url=static("nautobot_device_lifecycle_mgmt/docs/index.html")),
        name="docs",
    ),
]

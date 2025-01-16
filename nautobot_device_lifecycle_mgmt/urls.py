"""Django urlpatterns declaration for the Lifecycle Management app."""

from django.templatetags.static import static
from django.urls import path
from django.views.generic import RedirectView
from nautobot.apps.urls import NautobotUIViewSetRouter

from nautobot_device_lifecycle_mgmt import views

router = NautobotUIViewSetRouter()
router.register("hardware", viewset=views.HardwareLCMUIViewSet)
router.register("software-notice", viewset=views.SoftwareNoticeUIViewSet)
router.register("validated-software", viewset=views.ValidatedSoftwareLCMUIViewSet)
router.register("contract", viewset=views.ContractLCMUIViewSet)
router.register("provider", viewset=views.ProviderLCMUIViewSet)
router.register("cve", viewset=views.CVELCMUIViewSet)
router.register("vulnerability", viewset=views.VulnerabilityLCMUIViewSet)

urlpatterns = router.urls

urlpatterns += [
    path(
        "hardware-notice-device-report/",
        views.HardwareNoticeDeviceReportView.as_view(),
        name="hardwarenotice_device_report",
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
    # DeviceHardwareNoticeResult
    path(
        "device-hardware-notice-result/",
        views.DeviceHardwareNoticeResultListView.as_view(),
        name="devicehardwarenoticeresult_list",
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

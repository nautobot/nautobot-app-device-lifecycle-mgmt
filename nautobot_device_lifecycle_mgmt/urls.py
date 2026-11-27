"""Django urlpatterns declaration for the Lifecycle Management app."""

from django.templatetags.static import static
from django.urls import path
from django.views.generic import RedirectView
from nautobot.apps.urls import NautobotUIViewSetRouter

from nautobot_device_lifecycle_mgmt import views

app_name = "nautobot_device_lifecycle_mgmt"
router = NautobotUIViewSetRouter()
router.register("hardware", viewset=views.HardwareLCMUIViewSet)
router.register("validated-software", viewset=views.ValidatedSoftwareLCMUIViewSet)
router.register("contract", viewset=views.ContractLCMUIViewSet)
router.register("provider", viewset=views.ProviderLCMUIViewSet)
router.register("cve", viewset=views.CVELCMUIViewSet)
router.register("vulnerability", viewset=views.VulnerabilityLCMUIViewSet)

router.register(
    "hardware-notice-device-report",
    views.HardwareNoticeDeviceReportUIViewSet,
    basename="hardwarenotice_device_report",
)
router.register(
    "validated-software-device-report",
    views.ValidatedSoftwareDeviceReportUIViewSet,
    basename="validatedsoftware_device_report",
)
router.register(
    "validated-software-inventoryitem-report",
    views.ValidatedSoftwareInventoryItemReportUIViewSet,
    basename="validatedsoftware_inventoryitem_report",
)
router.register("device-hardware-notice-result", viewset=views.DeviceHardwareNoticeResultUIViewSet)
router.register("device-validated-software-result", viewset=views.DeviceSoftwareValidationResultUIViewSet)
router.register(
    "inventory-item-validated-software-result", viewset=views.InventoryItemSoftwareValidationResultUIViewSet
)


urlpatterns = router.urls

urlpatterns += [
    path(
        "docs/",
        RedirectView.as_view(url=static("nautobot_device_lifecycle_mgmt/docs/index.html")),
        name="docs",
    ),
    # SoftwareVersionRelatedCVEResult
    path(
        "software-versions/<uuid:pk>/related-cves/",
        views.SoftwareVersionRelatedCveView.as_view(),
        name="softwareversion_related_cves",
    ),
    path(
        "docs/",
        RedirectView.as_view(url=static("nautobot_device_lifecycle_mgmt/docs/index.html")),
        name="docs",
    ),
]

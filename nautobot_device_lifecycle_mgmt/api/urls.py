"""API URLs for the Lifecycle Management app."""

from rest_framework import routers

from nautobot_device_lifecycle_mgmt.api.views import (
    ContractLCMView,
    CVELCMViewSet,
    DeviceHardwareNoticeResultListViewSet,
    DeviceSoftwareValidationResultListViewSet,
    HardwareLCMView,
    InventoryItemSoftwareValidationResultListViewSet,
    ProviderLCMView,
    SoftwareNoticeView,
    ValidatedSoftwareLCMViewSet,
    VulnerabilityLCMViewSet,
)

router = routers.DefaultRouter()

router.register("hardware", HardwareLCMView)
router.register("software-notice", SoftwareNoticeView)
router.register("contract", ContractLCMView)
router.register("provider", ProviderLCMView)
router.register("validated-software", ValidatedSoftwareLCMViewSet)
router.register("cve", CVELCMViewSet)
router.register("vulnerability", VulnerabilityLCMViewSet)
router.register("device-hardware-notice-result", DeviceHardwareNoticeResultListViewSet)
router.register("device-validated-software-result", DeviceSoftwareValidationResultListViewSet)
router.register("inventory-item-validated-software-result", InventoryItemSoftwareValidationResultListViewSet)

app_name = "nautobot_device_lifecycle_mgmt"  # pylint: disable=invalid-name

urlpatterns = router.urls

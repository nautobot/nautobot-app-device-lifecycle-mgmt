"""API URLs for the Lifecycle Management app."""

from rest_framework import routers

from nautobot_device_lifecycle_mgmt.api.views import (
    ContactLCMView,
    ContractLCMView,
    CVELCMViewSet,
    DeviceSoftwareValidationResultListViewSet,
    HardwareLCMView,
    InventoryItemSoftwareValidationResultListViewSet,
    ProviderLCMView,
    SoftwareImageLCMViewSet,
    SoftwareLCMViewSet,
    ValidatedSoftwareLCMViewSet,
    VulnerabilityLCMViewSet,
)

router = routers.DefaultRouter()

router.register("hardware", HardwareLCMView)
router.register("contract", ContractLCMView)
router.register("provider", ProviderLCMView)
router.register("contact", ContactLCMView)  # TODO: Remove. @progala
router.register("software", SoftwareLCMViewSet)  # TODO: Remove. @progala
router.register("software-image", SoftwareImageLCMViewSet)  # TODO: Remove. @progala
router.register("validated-software", ValidatedSoftwareLCMViewSet)
router.register("cve", CVELCMViewSet)
router.register("vulnerability", VulnerabilityLCMViewSet)
router.register("device-validated-software-result", DeviceSoftwareValidationResultListViewSet)
router.register("inventory-item-validated-software-result", InventoryItemSoftwareValidationResultListViewSet)

app_name = "nautobot_device_lifecycle_mgmt"  # pylint: disable=invalid-name

urlpatterns = router.urls

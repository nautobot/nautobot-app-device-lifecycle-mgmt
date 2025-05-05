"""Django API urlpatterns declaration for nautobot_device_lifecycle_mgmt app."""

from nautobot.apps.api import OrderedDefaultRouter

from nautobot_device_lifecycle_mgmt.api import views

router = OrderedDefaultRouter()
# add the name of your api endpoint, usually hyphenated model name in plural, e.g. "my-model-classes"
router.register("hardware", views.HardwareLCMView)
router.register("contract", views.ContractLCMView)
router.register("provider", views.ProviderLCMView)
router.register("contact", views.ContactLCMView)
router.register("software", views.SoftwareLCMViewSet)
router.register("software-image", views.SoftwareImageLCMViewSet)
router.register("validated-software", views.ValidatedSoftwareLCMViewSet)
router.register("cve", views.CVELCMViewSet)
router.register("vulnerability", views.VulnerabilityLCMViewSet)
router.register("device-hardware-notice-result", views.DeviceHardwareNoticeResultListViewSet)
router.register("device-validated-software-result", views.DeviceSoftwareValidationResultListViewSet)
router.register("inventory-item-validated-software-result", views.InventoryItemSoftwareValidationResultListViewSet)

app_name = "nautobot_device_lifecycle_mgmt-api"
urlpatterns = router.urls

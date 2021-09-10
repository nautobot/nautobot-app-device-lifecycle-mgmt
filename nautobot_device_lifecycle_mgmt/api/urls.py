"""API URLs for the LifeCycle Management plugin."""

from rest_framework import routers
from nautobot_device_lifecycle_mgmt.api.views import (
    HardwareLCMView,
    ContractLCMView,
    ProviderLCMView,
    ContactLCMView,
    SoftwareLCMViewSet,
    ValidatedSoftwareLCMViewSet,
)

router = routers.DefaultRouter()

router.register(r"hardware", HardwareLCMView)
router.register(r"contract", ContractLCMView)
router.register(r"provider", ProviderLCMView)
router.register(r"contact", ContactLCMView)
router.register(r"software", SoftwareLCMViewSet)
router.register(r"validated-software", ValidatedSoftwareLCMViewSet)

app_name = "nautobot_device_lifecycle_mgmt"

urlpatterns = router.urls

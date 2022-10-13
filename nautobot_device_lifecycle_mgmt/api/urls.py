"""API URLs for the Lifecycle Management plugin."""

from rest_framework import routers
from nautobot_device_lifecycle_mgmt.api.views import (
    HardwareLCMView,
    ContractLCMView,
    ProviderLCMView,
    ContactLCMView,
    SoftwareLCMViewSet,
    SoftwareImageLCMViewSet,
    ValidatedSoftwareLCMViewSet,
    CVELCMViewSet,
    VulnerabilityLCMViewSet,
)

router = routers.DefaultRouter()

router.register(r"hardware", HardwareLCMView)
router.register(r"contract", ContractLCMView)
router.register(r"provider", ProviderLCMView)
router.register(r"contact", ContactLCMView)
router.register(r"software", SoftwareLCMViewSet)
router.register(r"software-image", SoftwareImageLCMViewSet)
router.register(r"validated-software", ValidatedSoftwareLCMViewSet)
router.register(r"cve", CVELCMViewSet)
router.register(r"vulnerability", VulnerabilityLCMViewSet)

app_name = "nautobot_device_lifecycle_mgmt"

urlpatterns = router.urls

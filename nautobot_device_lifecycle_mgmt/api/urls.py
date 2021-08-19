<<<<<<< HEAD
"""API URLs for the LifeCycle Management plugin."""

from rest_framework import routers
from nautobot_device_lifecycle_mgmt.api.views import HardwareLCMView

router = routers.DefaultRouter()

router.register(r"hardware", HardwareLCMView)

app_name = "nautobot_device_lifecycle_mgmt"
=======
"""API URLs for nautobot_plugin_device_lifecycle_mgmt."""

from rest_framework import routers
from nautobot_plugin_device_lifecycle_mgmt.api.views import (
    EoxNoticeView,
    SoftwareLCMViewSet,
    ValidatedSoftwareLCMViewSet,
)

router = routers.DefaultRouter()

router.register(r"hardware", EoxNoticeView)
router.register(r"software", SoftwareLCMViewSet)
router.register(r"validated-software", ValidatedSoftwareLCMViewSet)

app_name = "nautobot_plugin_device_lifecycle_mgmt"
>>>>>>> c9c3a9d (Rename plugin)

urlpatterns = router.urls

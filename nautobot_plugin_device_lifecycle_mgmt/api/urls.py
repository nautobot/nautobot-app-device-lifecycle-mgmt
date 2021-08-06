"""API URLs for the LifeCycle Management plugin."""

from rest_framework import routers
from nautobot_plugin_device_lifecycle_mgmt.api.views import HardwareLCMView

router = routers.DefaultRouter()

router.register(r"hardware", HardwareLCMView)

app_name = "nautobot_plugin_device_lifecycle_mgmt"

urlpatterns = router.urls

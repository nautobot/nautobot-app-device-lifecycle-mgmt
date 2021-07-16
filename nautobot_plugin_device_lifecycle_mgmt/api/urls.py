"""API URLs for nautobot_plugin_device_lifecycle_mgmt."""

from rest_framework import routers
from nautobot_plugin_device_lifecycle_mgmt.api.views import EoxNoticeView

router = routers.DefaultRouter()

router.register(r"", EoxNoticeView)

app_name = "nautobot_plugin_device_lifecycle_mgmt"

urlpatterns = router.urls

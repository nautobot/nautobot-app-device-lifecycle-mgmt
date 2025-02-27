"""Django urlpatterns declaration for nautobot_device_lifecycle_mgmt app."""

from django.templatetags.static import static
from django.urls import path
from django.views.generic import RedirectView
from nautobot.apps.urls import NautobotUIViewSetRouter


from nautobot_device_lifecycle_mgmt import views


app_name = "nautobot_device_lifecycle_mgmt"
router = NautobotUIViewSetRouter()

router.register("hardwarelcm", views.HardwareLCMUIViewSet)


urlpatterns = [
    path("docs/", RedirectView.as_view(url=static("nautobot_device_lifecycle_mgmt/docs/index.html")), name="docs"),
]

urlpatterns += router.urls

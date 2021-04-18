"""API URLs for eox_notices."""

from rest_framework import routers
from .views import EoxNoticeView

router = routers.DefaultRouter()

router.register(r"", EoxNoticeView)

app_name = "eox_notices-api"

urlpatterns = router.urls

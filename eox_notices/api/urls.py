"""API URLs for eox_notices."""

from rest_framework import routers
from .views import EoxNoticeView

router = routers.DefaultRouter()

router.register("", EoxNoticeView)

urlpatterns = router.urls

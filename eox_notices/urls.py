"""Django urlpatterns declaration for eox_notices plugin."""
from django.urls import path
from nautobot.extras.views import ObjectChangeLogView
from . import views
from .models import EoxNotice


urlpatterns = [
    path("", views.EoxNoticesListView.as_view(), name="eoxnotice_list"),
    path("<uuid:pk>/", views.EoxNoticeView.as_view(), name="eoxnotice"),
    path("add/", views.EoxNoticeCreateView.as_view(), name="eoxnotice_add"),
    path("<uuid:pk>/delete/", views.EoxNoticeDeleteView.as_view(), name="eoxnotice_delete"),
    path("<uuid:pk>/edit/", views.EoxNoticeEditView.as_view(), name="eoxnotice_edit"),
    path(
        "<uuid:pk>/changelog/", ObjectChangeLogView.as_view(), name="eoxnotice_changelog", kwargs={"model": EoxNotice},
    ),
]

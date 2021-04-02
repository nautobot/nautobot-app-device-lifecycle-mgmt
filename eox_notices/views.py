"""Views for eox_notices."""

from django.contrib.auth.mixins import PermissionRequiredMixin
from nautobot.core.views.generic import ObjectView, ObjectListView, ObjectEditView, ObjectDeleteView
from .models import EoxNotice
from .tables import EoxNoticesTable
from .forms import EoxNoticeForm, EoxNoticeFilterForm
from .filters import EoxNoticeFilter


class EoxNoticesListView(PermissionRequiredMixin, ObjectListView):
    queryset = EoxNotice.objects.all()
    filterset = EoxNoticeFilter
    filterset_form = EoxNoticeFilterForm
    table = EoxNoticesTable
    template_name = "eox_notices/eoxnotice_list.html"
    permission_required = "eox_notices.view_eoxnotice"
    action_buttons = ("add",)


class EoxNoticeView(PermissionRequiredMixin, ObjectView):
    queryset = EoxNotice.objects.all()
    permission_required = "eox_notices.view_eoxnotice"


class EoxNoticeCreateView(PermissionRequiredMixin, ObjectEditView):
    model = EoxNotice
    queryset = EoxNotice.objects.all()
    model_form = EoxNoticeForm
    permission_required = "eox_notices.add_notice"
    default_return_url = "plugins:eox_notices:eoxnotice_list"


class EoxNoticeDeleteView(PermissionRequiredMixin, ObjectDeleteView):

    model = EoxNotice
    queryset = EoxNotice.objects.all()
    permission_required = "eox_notices.delete_notice"
    default_return_url = "plugins:eox_notices:eoxnotice_list"


class EoxNoticeEditView(PermissionRequiredMixin, ObjectEditView):

    model = EoxNotice
    queryset = EoxNotice.objects.all()
    model_form = EoxNoticeForm
    permission_required = "eox_notices.change_notice"
    default_return_url = "plugins:eox_notices:eoxnotice"

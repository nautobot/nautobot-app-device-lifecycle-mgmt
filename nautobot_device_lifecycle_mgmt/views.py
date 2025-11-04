# pylint: disable=too-many-lines
"""Views implementation for the Lifecycle Management app."""

import base64
import io
import logging
import urllib

import matplotlib.pyplot as plt
import nautobot.apps.views
import numpy as np
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, ExpressionWrapper, F, FloatField, Q
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django_tables2 import RequestConfig
from matplotlib.ticker import MaxNLocator
from nautobot.apps.choices import ColorChoices
from nautobot.apps.ui import Breadcrumbs, ModelBreadcrumbItem, Titles, ViewNameBreadcrumbItem
from nautobot.apps.views import NautobotUIViewSet
from nautobot.core.models.querysets import count_related
from nautobot.core.ui import object_detail
from nautobot.core.ui.choices import SectionChoices
from nautobot.core.views import generic
from nautobot.core.views.mixins import ContentTypePermissionRequiredMixin
from nautobot.core.views.paginator import EnhancedPaginator, get_paginate_count
from nautobot.dcim.models import Device, DeviceType, InventoryItem, SoftwareVersion
from nautobot.extras.models import Role, Tag

from nautobot_device_lifecycle_mgmt import choices, filters, forms, helpers, models, tables
from nautobot_device_lifecycle_mgmt.api import serializers

PLUGIN_CFG = settings.PLUGINS_CONFIG["nautobot_device_lifecycle_mgmt"]

logger = logging.getLogger("nautobot_device_lifecycle_mgmt")

GREEN, RED, GREY = (f"#{ColorChoices.COLOR_LIGHT_GREEN}", f"#{ColorChoices.COLOR_RED}", f"#{ColorChoices.COLOR_GREY}")


#
# HardwareLCM UIViewSet
#
class HardwareLCMUIViewSet(NautobotUIViewSet):
    """HardwareLCM UI ViewSet."""

    bulk_update_form_class = forms.HardwareLCMBulkEditForm
    filterset_class = filters.HardwareLCMFilterSet
    filterset_form_class = forms.HardwareLCMFilterForm
    form_class = forms.HardwareLCMForm
    queryset = models.HardwareLCM.objects.prefetch_related("device_type")
    serializer_class = serializers.HardwareLCMSerializer
    table_class = tables.HardwareLCMTable

    object_detail_content = object_detail.ObjectDetailContent(
        panels=(
            object_detail.ObjectFieldsPanel(
                label="Hardware Notice",
                weight=100,
                section=SectionChoices.LEFT_HALF,
                fields=[
                    "devices",
                    "device_type",
                    "inventory_item",
                    "end_of_sale",
                    "end_of_support",
                    "end_of_sw_releases",
                    "end_of_security_patches",
                    "documentation_url",
                ],
                value_transforms={
                    "documentation_url": [helpers.hyperlink_url_new_tab],
                },
            ),
        ),
    )

    def get_extra_context(self, request, instance=None):
        """Return any additional context data for the template.

        request: The current request
        instance: The object being viewed
        """
        context = super().get_extra_context(request, instance)
        if not instance:
            return context

        if instance.device_type:
            devices = Device.objects.restrict(request.user, "view").filter(device_type=instance.device_type)
        elif instance.inventory_item:
            devices = Device.objects.restrict(request.user, "view").filter(
                inventory_items__part_id=instance.inventory_item
            )
        else:
            devices = []

        # Attach devices to the instance so ObjectFieldsPanel can access it
        instance.devices = devices
        context["devices"] = devices
        return context


class ValidatedSoftwareLCMUIViewSet(NautobotUIViewSet):
    """ValidatedSoftwareLCM UI ViewSet."""

    bulk_update_form_class = forms.ValidatedSoftwareLCMBulkEditForm
    filterset_class = filters.ValidatedSoftwareLCMFilterSet
    filterset_form_class = forms.ValidatedSoftwareLCMFilterForm
    form_class = forms.ValidatedSoftwareLCMForm
    queryset = models.ValidatedSoftwareLCM.objects.all()
    serializer_class = serializers.ValidatedSoftwareLCMSerializer
    table_class = tables.ValidatedSoftwareLCMTable
    view_titles = Titles(titles={"list": "Validated Software List"})
    breadcrumbs = Breadcrumbs(
        items={
            "list": [ModelBreadcrumbItem(label="Validated Software List", model=models.ValidatedSoftwareLCM)],
            "retrieve": [ModelBreadcrumbItem(label="Validated Software List")],
        }
    )

    object_detail_content = object_detail.ObjectDetailContent(
        panels=(
            object_detail.ObjectFieldsPanel(
                weight=100,
                section=SectionChoices.LEFT_HALF,
                fields=["software", "start", "end", "valid", "preferred"],
            ),
            object_detail.StatsPanel(
                weight=100,
                label="Stats",
                section=SectionChoices.RIGHT_HALF,
                related_models=[
                    (Device, "validated_software__in"),
                    (DeviceType, "validated_software__in"),
                    (Role, "validated_software__in"),
                    (InventoryItem, "validated_software__in"),
                    (Tag, "validated_software__in"),
                ],
                filter_name="nautobot_device_lifecycle_mgmt_validated_software",
            ),
        ),
    )


class ContractLCMFieldsPanel(object_detail.ObjectFieldsPanel):
    """Custom fields panel for ContractLCM."""

    def render_value(self, key, value, context):
        """Render custom fields for ContractLCM."""
        instance = context.get("object")

        # Render Devices count as a link to filtered Device list
        if key == "devices":
            device_qs = Device.objects.restrict(context["request"].user, "view").filter(device_contracts=instance)
            device_count = device_qs.count()

            return format_html(
                '<a href="{}?nautobot_device_lifecycle_mgmt_device_contracts={}">{}</a>',
                reverse("dcim:device_list"),
                instance.id,
                device_count,
            )

        return super().render_value(key, value, context)


class ContractLCMUIViewSet(NautobotUIViewSet):
    """ContractLCM UI ViewSet."""

    bulk_update_form_class = forms.ContractLCMBulkEditForm
    filterset_class = filters.ContractLCMFilterSet
    filterset_form_class = forms.ContractLCMFilterForm
    form_class = forms.ContractLCMForm
    queryset = models.ContractLCM.objects.all()
    serializer_class = serializers.ContractLCMSerializer
    table_class = tables.ContractLCMTable

    object_detail_content = object_detail.ObjectDetailContent(
        panels=(
            ContractLCMFieldsPanel(
                label="Contract",
                weight=100,
                section=SectionChoices.LEFT_HALF,
                fields=[
                    "name",
                    "provider",
                    "number",
                    "start",
                    "end",
                    "cost",
                    "currency",
                    "support_level",
                    "contract_type",
                    "devices",
                ],
            ),
        ),
    )


class ProviderLCMUIViewSet(NautobotUIViewSet):
    """ProviderLCM UI ViewSet."""

    bulk_update_form_class = forms.ProviderLCMBulkEditForm
    filterset_class = filters.ProviderLCMFilterSet
    filterset_form_class = forms.ProviderLCMFilterForm
    form_class = forms.ProviderLCMForm
    queryset = models.ProviderLCM.objects.all()
    serializer_class = serializers.ProviderLCMSerializer
    table_class = tables.ProviderLCMTable

    object_detail_content = object_detail.ObjectDetailContent(
        panels=(
            object_detail.ObjectFieldsPanel(
                weight=100,
                section=SectionChoices.LEFT_HALF,
                fields=(
                    "name",
                    "description",
                    "email",
                    "phone",
                    "physical_address",
                    "country",
                    "portal_url",
                ),
                value_transforms={
                    "physical_address": [helpers.render_address],
                    "phone": [helpers.hyperlinked_phone_number],
                    "email": [helpers.hyperlinked_email],
                },
            ),
            object_detail.ObjectsTablePanel(
                weight=200,
                section=SectionChoices.RIGHT_HALF,
                table_class=tables.ContractLCMTable,
                table_filter="provider",
                related_field_name="provider_id",
                exclude_columns=["pk", "cost", "devices", "provider", "expired", "active", "tags", "actions"],
                order_by_fields=["name"],
                table_title="Service Contracts",
                show_table_config_button=None,
            ),
        ),
    )


class CVEObjectFieldsPanel(object_detail.ObjectFieldsPanel):
    """Custom fields panel for CVELCM."""

    def render_value(self, key, value, context):
        """Render affected software as clickable links."""
        if key == "affected_softwares":
            queryset = value.all() if hasattr(value, "all") else value

            if not queryset or not queryset.exists():
                return format_html("&mdash;")

            return format_html_join(
                ", ",
                '<a href="{}">{}</a>',
                ((reverse("dcim:softwareversion", args=[obj.pk]), str(obj)) for obj in queryset),
            )

        return super().render_value(key, value, context)


class CVELCMUIViewSet(NautobotUIViewSet):
    """CVELCM UI ViewSet."""

    bulk_update_form_class = forms.CVELCMBulkEditForm
    filterset_class = filters.CVELCMFilterSet
    filterset_form_class = forms.CVELCMFilterForm
    form_class = forms.CVELCMForm
    queryset = models.CVELCM.objects.all()
    serializer_class = serializers.CVELCMSerializer
    table_class = tables.CVELCMTable

    object_detail_content = object_detail.ObjectDetailContent(
        panels=(
            CVEObjectFieldsPanel(
                weight=100,
                section=SectionChoices.LEFT_HALF,
                fields=[
                    "name",
                    "published_date",
                    "link",
                    "status",
                    "description",
                    "severity",
                    "cvss",
                    "cvss_v2",
                    "cvss_v3",
                    "affected_softwares",
                    "fix",
                ],
                value_transforms={"link": [helpers.hyperlink_url_new_tab]},
            ),
        ),
    )


class VulnerabilityLCMUIViewSet(NautobotUIViewSet):
    """VulnerabilityLCM UI ViewSet."""

    bulk_update_form_class = forms.VulnerabilityLCMBulkEditForm
    filterset_class = filters.VulnerabilityLCMFilterSet
    filterset_form_class = forms.VulnerabilityLCMFilterForm
    form_class = forms.VulnerabilityLCMForm
    queryset = models.VulnerabilityLCM.objects.all()
    serializer_class = serializers.VulnerabilityLCMSerializer
    table_class = tables.VulnerabilityLCMTable

    object_detail_content = object_detail.ObjectDetailContent(
        panels=(
            object_detail.ObjectFieldsPanel(
                weight=100,
                section=SectionChoices.LEFT_HALF,
                fields="__all__",
                exclude_fields=["old_software"],
            ),
        ),
    )


class ReportOverviewHelper(ContentTypePermissionRequiredMixin, generic.View):
    """Customized overview view for reports aggregation and filterset."""

    def get_required_permission(self):
        """Manually set permission when not tied to a model for global report."""
        # TODO: more generic permission should be used here
        return "nautobot_device_lifecycle_mgmt.view_validatedsoftwarelcm"

    @staticmethod
    def url_encode_figure(figure):
        """Save graph into string buffer and convert 64 bit code into image."""
        buf = io.BytesIO()
        figure.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        string = base64.b64encode(buf.read())

        return urllib.parse.quote(string)

    @staticmethod
    def plot_piechart_visual(aggr, pie_chart_attrs):
        """Plot pie chart aggregation visual."""
        if aggr[pie_chart_attrs["aggr_labels"][0]] is None:
            return None

        colors = [GREEN, RED, GREY]
        sizes = []
        pie_chart_labels = []
        pie_chart_colors = []
        for aggr_label, chart_label, color in zip(
            pie_chart_attrs["aggr_labels"], pie_chart_attrs["chart_labels"], colors
        ):
            if aggr[aggr_label] == 0:
                continue
            sizes.append(aggr[aggr_label])
            pie_chart_labels.append(chart_label)
            pie_chart_colors.append(color)

        explode = len(sizes) * (0.1,)
        fig1, ax1 = plt.subplots()
        logging.debug(fig1)
        ax1.pie(
            sizes,
            explode=explode,
            labels=pie_chart_labels,
            autopct="%1.1f%%",
            colors=pie_chart_colors,
            shadow=True,
            startangle=90,
            normalize=True,
        )
        ax1.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.title(aggr["name"], y=-0.1)
        fig = plt.gcf()

        return ReportOverviewHelper.url_encode_figure(fig)

    @staticmethod
    def plot_barchart_visual(qs, chart_attrs):  # pylint: disable=too-many-locals, invalid-name
        """Construct report visual from queryset."""
        labels = [item[chart_attrs["label_accessor"]] for item in qs]

        label_locations = np.arange(len(labels))  # the label locations

        barchart_bar_width = PLUGIN_CFG["barchart_bar_width"]
        barchart_width = PLUGIN_CFG["barchart_width"]
        barchart_height = PLUGIN_CFG["barchart_height"]

        width = barchart_bar_width  # the width of the bars

        fig, axis = plt.subplots(figsize=(barchart_width, barchart_height))

        rects = []
        for bar_pos, chart_bar in enumerate(chart_attrs["chart_bars"]):
            bar_label_item = [item[chart_bar["data_attr"]] for item in qs]
            rects.append(
                axis.bar(
                    label_locations - width + (bar_pos * width),
                    bar_label_item,
                    width,
                    label=chart_bar["label"],
                    color=chart_bar["color"],
                )
            )

        # Add some text for labels, title and custom x-axis tick labels, etc.
        axis.set_ylabel(chart_attrs["ylabel"])
        axis.set_title(chart_attrs["title"])
        axis.set_xticks(label_locations)
        axis.set_xticklabels(labels, rotation=45, ha="right")  # Rotate x-axis labels for better readability
        # Force integer y-axis labels
        axis.yaxis.set_major_locator(MaxNLocator(integer=True))
        axis.margins(0.2, 0.2)
        axis.legend()

        def autolabel(rects):
            """Attach a text label above each bar in *rects*, displaying its height."""
            for rect in rects:
                height = rect.get_height()
                axis.annotate(
                    f"{height}",
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    rotation=90,
                )

        for rect in rects:
            autolabel(rect)

        # Adjust layout to make room for rotated labels
        fig.tight_layout()

        return ReportOverviewHelper.url_encode_figure(fig)

    @staticmethod
    def calculate_aggr_percentage(aggr):
        """Calculate percentage of validated given aggregation fields.

        Returns:
            aggr: same aggr dict given as parameter with one new key
                - valid_percent
        """
        try:
            aggr["valid_percent"] = round(aggr["valid"] / aggr["total"] * 100, 2)
        except ZeroDivisionError:
            aggr["valid_percent"] = 0
        return aggr

    @staticmethod
    def plot_barchart_visual_hardware_notice(qs, chart_attrs):  # pylint: disable=too-many-locals
        """Construct report visual from queryset."""
        barchart_bar_width_min = 0.7
        barchart_bar_width = max(barchart_bar_width_min, PLUGIN_CFG["barchart_bar_width"])
        barchart_width = PLUGIN_CFG["barchart_width"]
        barchart_height_calc = (qs.count()) * (barchart_bar_width * 0.75)
        barchart_height = max(barchart_height_calc, PLUGIN_CFG["barchart_height"])

        device_types = []
        device_counts = []
        bar_colors = []

        for device_type in qs:
            # Get the End of Support date
            try:
                hw_notice = models.HardwareLCM.objects.get(device_type__id=device_type[chart_attrs["device_type_id"]])
                eos_date = hw_notice.end_of_support
            except ObjectDoesNotExist:
                eos_date = "Never"
            # Add labels and set bar colors
            if device_type["valid"] > 0:
                device_types.append(str(device_type[chart_attrs["label_accessor"]]) + "\n" + str(eos_date))
                device_counts.append(device_type["valid"])
                bar_colors.append(GREEN)
            elif device_type["invalid"] > 0:
                device_types.append(str(device_type[chart_attrs["label_accessor"]]) + "\n" + str(eos_date))
                device_counts.append(device_type["invalid"])
                bar_colors.append(RED)
            else:
                continue

        # If no device types are returned by the filter, use None as a defult label
        if not device_types:
            device_types = ["None"]
            device_counts = [0]
            bar_colors = [RED]

        fig, axis = plt.subplots(figsize=(barchart_width, barchart_height))

        # Add device count text to top of bars
        for index, value in enumerate(device_counts):
            axis.text(x=value, y=index, s=f" {str(value)}")

        axis.barh(device_types, device_counts, color=bar_colors)
        axis.set_xlabel(chart_attrs["xlabel"])
        axis.set_title(chart_attrs["title"])
        axis.margins(
            0.1, barchart_height / ((qs.count() if qs else barchart_height) * barchart_height)
        )  # dynamic y margin based on qs counts (more results = smaller margins)
        axis.xaxis.set_major_locator(MaxNLocator(integer=True))

        legend_colors = {"supported": GREEN, "unsuported": RED}
        legend_labels = list(legend_colors.keys())
        legend_handles = [plt.Rectangle((0, 0), 1, 1, color=legend_colors[label]) for label in legend_labels]
        plt.legend(legend_handles, legend_labels)

        return ReportOverviewHelper.url_encode_figure(fig)


class HardwareNoticeDeviceReportUIViewSet(nautobot.apps.views.ObjectListViewMixin):  # pylint: disable=abstract-method
    """View for executive report on device hardware notices."""

    filterset_class = filters.DeviceHardwareNoticeResultFilterSet
    filterset_form_class = forms.DeviceHardwareNoticeResultFilterForm
    table_class = tables.DeviceHardwareNoticeResultTable
    serializer_class = serializers.DeviceHardwareNoticeResultSerializer
    action_buttons = ("export",)

    queryset = (
        models.DeviceHardwareNoticeResult.objects.values(
            "device__device_type__model",
            "device__device_type__pk",
        )
        .distinct()
        .annotate(
            total=Count("device__device_type__model"),
            valid=Count("device__device_type__model", filter=Q(is_supported=True)),
            invalid=Count("device__device_type__model", filter=Q(is_supported=False)),
            valid_percent=ExpressionWrapper(
                100 * F("valid") / F("total"),
                output_field=FloatField(),
            ),
        )
        .order_by("-valid_percent")
    )

    #
    # Template
    #
    def get_template_name(self, action=None):
        """Return the template name for the list view."""
        if action not in (None, "list"):
            raise ValueError(f"Action {action} is not supported for this viewset.")
        return "nautobot_device_lifecycle_mgmt/hardwarenotice_device_report.html"

    #
    # Aggregation
    #
    def get_global_aggr(self, request):
        """Get global aggregation of device hardware notices."""
        qs = models.DeviceHardwareNoticeResult.objects

        if self.filterset_class is not None:
            qs = self.filterset_class(request.GET, queryset=qs).qs

        device_aggr = qs.aggregate(
            total=Count("device"),
            valid=Count("device", filter=Q(is_supported=True)),
            invalid=Count("device", filter=Q(is_supported=False)),
        )
        device_aggr["name"] = "Devices"

        return ReportOverviewHelper.calculate_aggr_percentage(device_aggr)

    #
    # Extra context for template rendering
    #
    def get_extra_context(self, request, instance=None):
        """Return extra context for template rendering."""
        context = super().get_extra_context(request, instance)
        try:
            report_last_run = (
                models.DeviceHardwareNoticeResult.objects.filter(run_type=choices.ReportRunTypeChoices.REPORT_FULL_RUN)
                .latest("last_updated")
                .last_run
            )
        except models.DeviceHardwareNoticeResult.DoesNotExist:  # pylint: disable=no-member
            report_last_run = None

        device_aggr = self.get_global_aggr(request)

        device_type_qs = (
            models.DeviceHardwareNoticeResult.objects.values(
                "device__device_type__model",
                "device__device_type__id",
            )
            .distinct()
            .annotate(
                total=Count("device__device_type__model"),
                valid=Count("device__device_type__model", filter=Q(is_supported=True)),
                invalid=Count("device__device_type__model", filter=Q(is_supported=False)),
                valid_percent=ExpressionWrapper(
                    100 * F("valid") / F("total"),
                    output_field=FloatField(),
                ),
            )
            .order_by("-hardware_notice__end_of_support")
        )

        if self.filterset_class is not None:
            device_type_qs = self.filterset_class(request.GET, queryset=device_type_qs).qs

        pie_chart_attrs = {
            "aggr_labels": ["valid", "invalid"],
            "chart_labels": ["Supported", "Unsupported"],
        }

        bar_chart_attrs = {
            "device_type_id": "device__device_type__id",
            "label_accessor": "device__device_type__model",
            "xlabel": "Devices",
            "ylabel": "Device Types",
            "title": "Devices per Device Type",
            "chart_bars": [
                {"label": "Supported", "data_attr": "valid", "color": GREEN},
                {"label": "Unsupported", "data_attr": "invalid", "color": RED},
            ],
        }

        context["device_aggr"] = device_aggr
        context["device_visual"] = ReportOverviewHelper.plot_piechart_visual(device_aggr, pie_chart_attrs)
        context["bar_chart"] = ReportOverviewHelper.plot_barchart_visual_hardware_notice(
            device_type_qs, bar_chart_attrs
        )
        context["report_last_run"] = report_last_run
        return context


class ValidatedSoftwareDeviceReportUIViewSet(nautobot.apps.views.ObjectListViewMixin):  # pylint: disable=abstract-method
    """View for executive report on device software validation."""

    filterset_class = filters.DeviceSoftwareValidationResultFilterSet
    filterset_form_class = forms.DeviceSoftwareValidationResultFilterForm
    table_class = tables.DeviceSoftwareValidationResultTable
    queryset = (
        models.DeviceSoftwareValidationResult.objects.values(
            "device__device_type__model",
            "device__device_type__pk",
        )
        .distinct()
        .annotate(
            total=Count("device__device_type__model"),
            valid=Count("device__device_type__model", filter=Q(is_validated=True)),
            invalid=Count("device__device_type__model", filter=Q(is_validated=False) & ~Q(software=None)),
            no_software=Count("device__device_type__model", filter=Q(software=None)),
            valid_percent=ExpressionWrapper(100 * F("valid") / F("total"), output_field=FloatField()),
        )
        .order_by("-valid_percent")
    )
    serializer_class = serializers.DeviceSoftwareValidationResultSerializer
    action_buttons = ("export",)

    def get_template_name(self):
        """Return the template name for rendering the list view only."""
        if self.action != "list":
            raise ValueError(f"Action {self.action} is not supported")
        return "nautobot_device_lifecycle_mgmt/validatedsoftware_device_report.html"

    def get_global_aggr(self, request):
        """Get device global software validation aggregation."""
        qs = models.DeviceSoftwareValidationResult.objects

        if self.filterset_class is not None:
            filtered_qs = self.filterset_class(request.GET, queryset=qs).qs
        else:
            filtered_qs = qs

        device_aggr = filtered_qs.aggregate(
            total=Count("device"),
            valid=Count("device", filter=Q(is_validated=True)),
            invalid=Count("device", filter=Q(is_validated=False) & ~Q(software=None)),
            no_software=Count("device", filter=Q(software=None)),
        )
        device_aggr["name"] = "Devices"
        return ReportOverviewHelper.calculate_aggr_percentage(device_aggr)

    def get_extra_context(self, request, instance=None):
        """Prepare extra context for template rendering."""
        context = super().get_extra_context(request, instance)
        try:
            report_last_run = (
                models.DeviceSoftwareValidationResult.objects.filter(
                    run_type=choices.ReportRunTypeChoices.REPORT_FULL_RUN
                )
                .latest("last_updated")
                .last_run
            )
        except models.DeviceSoftwareValidationResult.DoesNotExist:  # pylint: disable=no-member
            report_last_run = None

        device_aggr = self.get_global_aggr(request)

        # Platform-level aggregation for bar chart
        platform_qs = (
            models.DeviceSoftwareValidationResult.objects.values("device__platform__name")
            .distinct()
            .annotate(
                total=Count("device__platform__name"),
                valid=Count("device__platform__name", filter=Q(is_validated=True)),
                invalid=Count("device__platform__name", filter=Q(is_validated=False) & ~Q(software=None)),
                no_software=Count("device__platform__name", filter=Q(software=None)),
            )
            .order_by("-total")
        )

        if self.filterset_class is not None:
            platform_qs = self.filterset_class(request.GET, queryset=platform_qs).qs

        pie_chart_attrs = {
            "aggr_labels": ["valid", "invalid", "no_software"],
            "chart_labels": ["Valid", "Invalid", "No Software"],
        }
        bar_chart_attrs = {
            "label_accessor": "device__platform__name",
            "ylabel": "Device",
            "title": "Valid per Platform",
            "chart_bars": [
                {"label": "Valid", "data_attr": "valid", "color": GREEN},
                {"label": "Invalid", "data_attr": "invalid", "color": RED},
                {"label": "No Software", "data_attr": "no_software", "color": GREY},
            ],
        }

        context["device_aggr"] = device_aggr
        context["device_visual"] = ReportOverviewHelper.plot_piechart_visual(device_aggr, pie_chart_attrs)
        context["bar_chart"] = ReportOverviewHelper.plot_barchart_visual(platform_qs, bar_chart_attrs)
        context["report_last_run"] = report_last_run
        return context

    def queryset_to_csv(self, request=None):
        """Export queryset of objects as comma-separated value (CSV)."""
        csv_data = []

        # Get extra context for aggregation values
        extra_content = self.get_extra_context(self.request)

        # Add summary row
        csv_data.append(",".join(["Type", "Total", "Valid", "Invalid", "No Software", "Compliance"]))
        csv_data.append(
            ",".join(
                ["Devices"]
                + [
                    f"{val:.2f} %" if key == "valid_percent" else str(val)
                    for key, val in extra_content["device_aggr"].items()
                    if key != "name"
                ]
            )
        )
        csv_data.append("")

        qs = self.queryset.values(
            "device__device_type__model", "total", "valid", "invalid", "no_software", "valid_percent"
        )

        if qs is not None and len(qs) > 0:
            # Add header row for device model details
            csv_data.append(
                ",".join(
                    [
                        "Device Model" if item == "device__device_type__model" else item.replace("_", " ").title()
                        for item in qs[0].keys()
                    ]
                )
            )

            # Add each row
            for obj in qs:
                csv_data.append(
                    ",".join([f"{val:.2f} %" if key == "valid_percent" else str(val) for key, val in obj.items()])
                )

        return "\n".join(csv_data)


class DeviceHardwareNoticeResultUIViewSet(nautobot.apps.views.ObjectListViewMixin):  # pylint: disable=abstract-method
    """DeviceHardwareNoticeResult List view."""

    filterset_class = filters.DeviceHardwareNoticeResultFilterSet
    filterset_form_class = forms.DeviceHardwareNoticeResultFilterForm
    queryset = models.DeviceHardwareNoticeResult.objects.all()
    serializer_class = serializers.DeviceHardwareNoticeResultSerializer
    table_class = tables.DeviceHardwareNoticeResultListTable
    action_buttons = ("export",)
    breadcrumbs = Breadcrumbs(
        items={
            "list": [
                ViewNameBreadcrumbItem(
                    label="Device Hardware Notice Reports",
                    view_name="plugins:nautobot_device_lifecycle_mgmt:hardwarenotice_device_report_list",
                )
            ],
        }
    )
    view_titles = Titles(titles={"list": "Device Hardware Notice List"})


class DeviceSoftwareValidationResultUIViewSet(nautobot.apps.views.ObjectListViewMixin):  # pylint: disable=abstract-method
    """DeviceSoftawareValidationResult List view."""

    filterset_class = filters.DeviceSoftwareValidationResultFilterSet
    filterset_form_class = forms.DeviceSoftwareValidationResultFilterForm
    queryset = models.DeviceSoftwareValidationResult.objects.all()
    serializer_class = serializers.DeviceSoftwareValidationResultSerializer
    table_class = tables.DeviceSoftwareValidationResultListTable
    action_buttons = ("export",)
    breadcrumbs = Breadcrumbs(
        items={
            "list": [
                ViewNameBreadcrumbItem(
                    label="Device Software Validation Reports",
                    view_name="plugins:nautobot_device_lifecycle_mgmt:validatedsoftware_device_report_list",
                )
            ],
        }
    )
    view_titles = Titles(titles={"list": "Device Software Validation List"})


class ValidatedSoftwareInventoryItemReportUIViewSet(nautobot.apps.views.ObjectListViewMixin):  # pylint: disable=abstract-method
    """View for executive report on inventory item software validation."""

    filterset_class = filters.InventoryItemSoftwareValidationResultFilterSet
    filterset_form_class = forms.InventoryItemSoftwareValidationResultFilterForm
    table_class = tables.InventoryItemSoftwareValidationResultTable
    queryset = (
        models.InventoryItemSoftwareValidationResult.objects.values(
            "inventory_item__part_id",
            "inventory_item__name",
            "inventory_item__pk",
            "inventory_item__device__name",
            "inventory_item__device__pk",
        )
        .distinct()
        .annotate(
            total=Count("inventory_item__part_id"),
            valid=Count("inventory_item__part_id", filter=Q(is_validated=True)),
            invalid=Count("inventory_item__part_id", filter=Q(is_validated=False) & ~Q(software=None)),
            no_software=Count("inventory_item__part_id", filter=Q(software=None)),
            valid_percent=ExpressionWrapper(100 * F("valid") / F("total"), output_field=FloatField()),
        )
        .order_by("-valid_percent")
    )
    serializer_class = serializers.InventoryItemSoftwareValidationResultSerializer
    action_buttons = ("export",)

    def get_template_name(self):
        """Return the template name for rendering the list view only."""
        if self.action != "list":
            raise ValueError(f"Action {self.action} is not supported")
        return "nautobot_device_lifecycle_mgmt/validatedsoftware_inventoryitem_report.html"

    def get_global_aggr(self, request):
        """Get device and inventory global reports.

        Returns:
            inventory_aggr: inventory item global report dict
        """
        qs = models.InventoryItemSoftwareValidationResult.objects
        if self.filterset_class is not None:
            filtered_qs = self.filterset_class(request.GET, queryset=qs).qs
        else:
            filtered_qs = qs

        inventory_aggr = filtered_qs.aggregate(
            total=Count("inventory_item"),
            valid=Count("inventory_item", filter=Q(is_validated=True)),
            invalid=Count("inventory_item", filter=Q(is_validated=False) & ~Q(software=None)),
            no_software=Count("inventory_item", filter=Q(software=None)),
        )
        inventory_aggr["name"] = "Inventory Items"
        return ReportOverviewHelper.calculate_aggr_percentage(inventory_aggr)

    def get_extra_context(self, request, instance=None):
        """Prepare extra context for template rendering."""
        context = super().get_extra_context(request, instance)
        # Get the last full report run
        try:
            report_last_run = (
                models.InventoryItemSoftwareValidationResult.objects.filter(
                    run_type=choices.ReportRunTypeChoices.REPORT_FULL_RUN
                )
                .latest("last_updated")
                .last_run
            )
        except models.InventoryItemSoftwareValidationResult.DoesNotExist:
            report_last_run = None

        inventory_aggr = self.get_global_aggr(request)

        # Prepare platform-level aggregation for bar chart
        platform_qs = (
            models.InventoryItemSoftwareValidationResult.objects.values("inventory_item__manufacturer__name")
            .distinct()
            .annotate(
                total=Count("inventory_item__manufacturer__name"),
                valid=Count("inventory_item__manufacturer__name", filter=Q(is_validated=True)),
                invalid=Count("inventory_item__manufacturer__name", filter=Q(is_validated=False) & ~Q(software=None)),
                no_software=Count("inventory_item__manufacturer__name", filter=Q(software=None)),
            )
            .order_by("-total")
        )

        if self.filterset_class is not None:
            platform_qs = self.filterset_class(request.GET, queryset=platform_qs).qs

        pie_chart_attrs = {
            "aggr_labels": ["valid", "invalid", "no_software"],
            "chart_labels": ["Valid", "Invalid", "No Software"],
        }
        bar_chart_attrs = {
            "label_accessor": "inventory_item__manufacturer__name",
            "ylabel": "Inventory Item",
            "title": "Valid per Manufacturer",
            "chart_bars": [
                {"label": "Valid", "data_attr": "valid", "color": GREEN},
                {"label": "Invalid", "data_attr": "invalid", "color": RED},
                {"label": "No Software", "data_attr": "no_software", "color": GREY},
            ],
        }

        context["inventory_aggr"] = inventory_aggr
        context["inventory_visual"] = ReportOverviewHelper.plot_piechart_visual(inventory_aggr, pie_chart_attrs)
        context["bar_chart"] = ReportOverviewHelper.plot_barchart_visual(platform_qs, bar_chart_attrs)
        context["report_last_run"] = report_last_run
        return context

    def queryset_to_csv(self):
        """Export queryset of objects as comma-separated value (CSV)."""
        csv_data = []
        csv_data.append(",".join(["Type", "Total", "Valid", "Invalid", "No Software", "Compliance"]))
        csv_data.append(
            ",".join(
                ["Inventory Items"]
                + [
                    f"{val:.2f} %" if key == "valid_percent" else str(val)
                    for key, val in self.get_extra_context(self.request).get("inventory_aggr", {}).items()
                    if key != "name"
                ]
            )
        )
        csv_data.append(",".join([]))

        qs = self.queryset.values(
            "inventory_item__part_id",
            "inventory_item__name",
            "inventory_item__device__name",
            "inventory_item__device__pk",
            "total",
            "valid",
            "invalid",
            "no_software",
            "valid_percent",
        )
        if qs:
            csv_data.append(
                ",".join(
                    [
                        "Part ID" if item == "inventory_item__part_id" else item.replace("_", " ").title()
                        for item in qs[0].keys()
                    ]
                )
            )
            for obj in qs:
                csv_data.append(
                    ",".join([f"{val:.2f} %" if key == "valid_percent" else str(val) for key, val in obj.items()])
                )

        return "\n".join(csv_data)


class InventoryItemSoftwareValidationResultUIViewSet(nautobot.apps.views.ObjectListViewMixin):  # pylint: disable=abstract-method
    """InvenotryItemSoftawareValidationResult List view."""

    filterset_class = filters.InventoryItemSoftwareValidationResultFilterSet
    filterset_form_class = forms.InventoryItemSoftwareValidationResultFilterForm
    queryset = models.InventoryItemSoftwareValidationResult.objects.all()
    serializer_class = serializers.InventoryItemSoftwareValidationResultSerializer
    table_class = tables.InventoryItemSoftwareValidationResultListTable
    action_buttons = ("export",)
    breadcrumbs = Breadcrumbs(
        items={
            "list": [
                ViewNameBreadcrumbItem(
                    label="Inventory Software Validation Reports",
                    view_name="plugins:nautobot_device_lifecycle_mgmt:validatedsoftware_inventoryitem_report_list",
                )
            ],
        }
    )
    view_titles = Titles(titles={"list": "Inventory Software Validation List"})


class SoftwareVersionRelatedCveView(generic.ObjectView):
    """Related CVEs tab view for SoftwareVersion."""

    queryset = SoftwareVersion.objects.all()
    template_name = "nautobot_device_lifecycle_mgmt/softwareversion_related_cves.html"

    def get_extra_context(self, request, instance):
        """Adds Relative CVEs table."""
        relatedcves = instance.corresponding_cves.annotate(
            related_cves_count=count_related(SoftwareVersion, "corresponding_cves")
        ).restrict(request.user, "view")

        relatedcves_table = tables.CVELCMTable(data=relatedcves, user=request.user, orderable=False)

        paginate = {
            "paginator_class": EnhancedPaginator,
            "per_page": get_paginate_count(request),
        }
        RequestConfig(request, paginate).configure(relatedcves_table)

        return {
            "relatedcves_table": relatedcves_table,
            "active_tab": request.GET.get("tab", "main"),
        }

"""Views implementation for the Lifecycle Management app."""
import base64
import io
import logging
import urllib

import matplotlib.pyplot as plt
import numpy as np
from django.conf import settings
from django.db.models import Count, ExpressionWrapper, F, FloatField, Q
from django_tables2 import RequestConfig
from matplotlib.ticker import MaxNLocator
from nautobot.core.views import generic
from nautobot.core.views.mixins import ContentTypePermissionRequiredMixin
from nautobot.core.views.paginator import EnhancedPaginator, get_paginate_count

from nautobot_device_lifecycle_mgmt import choices
from nautobot_device_lifecycle_mgmt.filters import (
    DeviceSoftwareValidationResultFilterSet,
    InventoryItemSoftwareValidationResultFilterSet,
)
from nautobot_device_lifecycle_mgmt.forms import (
    DeviceSoftwareValidationResultFilterForm,
    InventoryItemSoftwareValidationResultFilterForm,
)
from nautobot_device_lifecycle_mgmt.models import (
    DeviceSoftwareValidationResult,
    InventoryItemSoftwareValidationResult,
    SoftwareImageLCM,
    SoftwareLCM,
)
from nautobot_device_lifecycle_mgmt.tables import (
    DeviceSoftwareValidationResultListTable,
    DeviceSoftwareValidationResultTable,
    InventoryItemSoftwareValidationResultListTable,
    InventoryItemSoftwareValidationResultTable,
    SoftwareImageLCMTable,
)
from nautobot_device_lifecycle_mgmt.utils import count_related_m2m

PLUGIN_CFG = settings.PLUGINS_CONFIG["nautobot_device_lifecycle_mgmt"]

logger = logging.getLogger("nautobot_device_lifecycle_mgmt")

# ---------------------------------------------------------------------------------
#  Hardware Lifecycle Management Views
# ---------------------------------------------------------------------------------
GREEN, RED, GREY = ("#D5E8D4", "#F8CECC", "#808080")


class SoftwareSoftwareImagesLCMView(generic.ObjectView):
    """Software Images tab for Software view."""

    queryset = SoftwareLCM.objects.all()
    template_name = "nautobot_device_lifecycle_mgmt/softwarelcm_software_images.html"

    def get_extra_context(self, request, instance):
        """Adds Software Images table."""
        softwareimages = (
            instance.software_images.annotate(device_type_count=count_related_m2m(SoftwareImageLCM, "device_types"))
            .annotate(object_tag_count=count_related_m2m(SoftwareImageLCM, "object_tags"))
            .restrict(request.user, "view")
        )

        softwareimages_table = SoftwareImageLCMTable(data=softwareimages, user=request.user, orderable=False)

        paginate = {
            "paginator_class": EnhancedPaginator,
            "per_page": get_paginate_count(request),
        }
        RequestConfig(request, paginate).configure(softwareimages_table)

        return {
            "softwareimages_table": softwareimages_table,
            "active_tab": "software-images",
        }


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
        figure.savefig(buf, format="png")
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
        axis.set_xticklabels(labels, rotation=0)
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
                    xy=(rect.get_x() + rect.get_width() / 2, 0.5),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    rotation=90,
                )

        for rect in rects:
            autolabel(rect)

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


class ValidatedSoftwareDeviceReportView(generic.ObjectListView):
    """View for executive report on software Validation."""

    filterset = DeviceSoftwareValidationResultFilterSet
    filterset_form = DeviceSoftwareValidationResultFilterForm
    table = DeviceSoftwareValidationResultTable
    template_name = "nautobot_device_lifecycle_mgmt/validatedsoftware_device_report.html"
    queryset = (
        DeviceSoftwareValidationResult.objects.values("device__device_type__model", "device__device_type__pk")
        .distinct()
        .annotate(
            total=Count("device__device_type__model"),
            valid=Count("device__device_type__model", filter=Q(is_validated=True)),
            invalid=Count("device__device_type__model", filter=Q(is_validated=False) & ~Q(software=None)),
            no_software=Count("device__device_type__model", filter=Q(software=None)),
            valid_percent=ExpressionWrapper(100 * F("valid") / (F("total")), output_field=FloatField()),
        )
        .order_by("-valid_percent")
    )
    action_buttons = ("export",)
    # extra content dict to be returned by self.extra_context() method
    extra_content = {}

    def setup(self, request, *args, **kwargs):
        """Using request object to perform filtering based on query params."""
        super().setup(request, *args, **kwargs)  #
        try:
            report_last_run = (
                DeviceSoftwareValidationResult.objects.filter(run_type=choices.ReportRunTypeChoices.REPORT_FULL_RUN)
                .latest("last_updated")
                .last_run
            )
        except DeviceSoftwareValidationResult.DoesNotExist:  # pylint: disable=no-member
            report_last_run = None

        device_aggr = self.get_global_aggr(request)
        _platform_qs = (
            DeviceSoftwareValidationResult.objects.values("device__platform__name")
            .distinct()
            .annotate(
                total=Count("device__platform__name"),
                valid=Count("device__platform__name", filter=Q(is_validated=True)),
                invalid=Count("device__platform__name", filter=Q(is_validated=False) & ~Q(software=None)),
                no_software=Count("device__platform__name", filter=Q(software=None)),
            )
            .order_by("-total")
        )
        platform_qs = self.filterset(request.GET, _platform_qs).qs
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
        self.extra_content = {
            "bar_chart": ReportOverviewHelper.plot_barchart_visual(platform_qs, bar_chart_attrs),
            "device_aggr": device_aggr,
            "device_visual": ReportOverviewHelper.plot_piechart_visual(device_aggr, pie_chart_attrs),
            "report_last_run": report_last_run,
        }

    def get_global_aggr(self, request):
        """Get device and inventory global reports.

        Returns:
            device_aggr: device global report dict
        """
        device_qs = DeviceSoftwareValidationResult.objects

        device_aggr = {}
        if self.filterset is not None:
            device_aggr = self.filterset(request.GET, device_qs).qs.aggregate(
                total=Count("device"),
                valid=Count("device", filter=Q(is_validated=True)),
                invalid=Count("device", filter=Q(is_validated=False) & ~Q(software=None)),
                no_software=Count("device", filter=Q(software=None)),
            )

            device_aggr["name"] = "Devices"

        return ReportOverviewHelper.calculate_aggr_percentage(device_aggr)

    def extra_context(self):
        """Extra content method on."""
        # add global aggregations to extra context.

        return self.extra_content

    def queryset_to_csv(self):
        """Export queryset of objects as comma-separated value (CSV)."""
        csv_data = []

        csv_data.append(",".join(["Type", "Total", "Valid", "Invalid", "No Software", "Compliance"]))
        csv_data.append(
            ",".join(
                ["Devices"]
                + [
                    f"{str(val)} %" if key == "valid_percent" else str(val)
                    for key, val in self.extra_content["device_aggr"].items()
                    if key != "name"
                ]
            )
        )
        csv_data.append(",".join([]))

        qs = self.queryset.values(  # pylint: disable=invalid-name
            "device__device_type__model", "total", "valid", "invalid", "no_software", "valid_percent"
        )
        csv_data.append(
            ",".join(
                [
                    "Device Model" if item == "device__device_type__model" else item.replace("_", " ").title()
                    for item in qs[0].keys()
                ]
            )
        )
        for obj in qs:
            csv_data.append(
                ",".join([f"{str(val)} %" if key == "valid_percent" else str(val) for key, val in obj.items()])
            )

        return "\n".join(csv_data)


class DeviceSoftwareValidationResultListView(generic.ObjectListView):
    """DeviceSoftawareValidationResult List view."""

    queryset = DeviceSoftwareValidationResult.objects.all()
    filterset = DeviceSoftwareValidationResultFilterSet
    filterset_form = DeviceSoftwareValidationResultFilterForm
    table = DeviceSoftwareValidationResultListTable
    action_buttons = ("export",)
    template_name = "nautobot_device_lifecycle_mgmt/devicesoftwarevalidationresult_list.html"


class ValidatedSoftwareInventoryItemReportView(generic.ObjectListView):
    """View for executive report on inventory item software validation."""

    filterset = InventoryItemSoftwareValidationResultFilterSet
    filterset_form = InventoryItemSoftwareValidationResultFilterForm
    table = InventoryItemSoftwareValidationResultTable
    template_name = "nautobot_device_lifecycle_mgmt/validatedsoftware_inventoryitem_report.html"
    queryset = (
        InventoryItemSoftwareValidationResult.objects.values(
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
            valid_percent=ExpressionWrapper(100 * F("valid") / (F("total")), output_field=FloatField()),
        )
        .order_by("-valid_percent")
    )
    action_buttons = ("export",)
    # extra content dict to be returned by self.extra_context() method
    extra_content = {}

    def setup(self, request, *args, **kwargs):
        """Using request object to perform filtering based on query params."""
        super().setup(request, *args, **kwargs)
        try:
            report_last_run = (
                InventoryItemSoftwareValidationResult.objects.filter(
                    run_type=choices.ReportRunTypeChoices.REPORT_FULL_RUN
                )
                .latest("last_updated")
                .last_run
            )
        except InventoryItemSoftwareValidationResult.DoesNotExist:  # pylint: disable=no-member
            report_last_run = None

        inventory_aggr = self.get_global_aggr(request)
        _platform_qs = (
            InventoryItemSoftwareValidationResult.objects.values("inventory_item__manufacturer__name")
            .distinct()
            .annotate(
                total=Count("inventory_item__manufacturer__name"),
                valid=Count("inventory_item__manufacturer__name", filter=Q(is_validated=True)),
                invalid=Count("inventory_item__manufacturer__name", filter=Q(is_validated=False) & ~Q(software=None)),
                no_software=Count("inventory_item__manufacturer__name", filter=Q(software=None)),
            )
            .order_by("-total")
        )
        platform_qs = self.filterset(request.GET, _platform_qs).qs

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

        self.extra_content = {
            "bar_chart": ReportOverviewHelper.plot_barchart_visual(platform_qs, bar_chart_attrs),
            "inventory_aggr": inventory_aggr,
            "inventory_visual": ReportOverviewHelper.plot_piechart_visual(inventory_aggr, pie_chart_attrs),
            "report_last_run": report_last_run,
        }

    def get_global_aggr(self, request):
        """Get device and inventory global reports.

        Returns:
            inventory_aggr: inventory item global report dict
        """
        inventory_item_qs = InventoryItemSoftwareValidationResult.objects

        inventory_aggr = {}
        if self.filterset is not None:
            inventory_aggr = self.filterset(request.GET, inventory_item_qs).qs.aggregate(
                total=Count("inventory_item"),
                valid=Count("inventory_item", filter=Q(is_validated=True)),
                invalid=Count("inventory_item", filter=Q(is_validated=False) & ~Q(software=None)),
                no_software=Count("inventory_item", filter=Q(software=None)),
            )
            inventory_aggr["name"] = "Inventory Items"

        return ReportOverviewHelper.calculate_aggr_percentage(inventory_aggr)

    def extra_context(self):
        """Extra content method on."""
        # add global aggregations to extra context.

        return self.extra_content

    def queryset_to_csv(self):
        """Export queryset of objects as comma-separated value (CSV)."""
        csv_data = []

        csv_data.append(",".join(["Type", "Total", "Valid", "Invalid", "No Software", "Compliance"]))
        csv_data.append(
            ",".join(
                ["Inventory Items"]
                + [
                    f"{str(val)} %" if key == "valid_percent" else str(val)
                    for key, val in self.extra_content["inventory_aggr"].items()
                    if key != "name"
                ]
            )
        )
        csv_data.append(",".join([]))

        qs = self.queryset.values(  # pylint: disable=invalid-name
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
                ",".join([f"{str(val)} %" if key == "valid_percent" else str(val) for key, val in obj.items()])
            )

        return "\n".join(csv_data)


class InventoryItemSoftwareValidationResultListView(generic.ObjectListView):
    """InvenotryItemSoftawareValidationResult List view."""

    queryset = InventoryItemSoftwareValidationResult.objects.all()
    filterset = InventoryItemSoftwareValidationResultFilterSet
    filterset_form = InventoryItemSoftwareValidationResultFilterForm
    table = InventoryItemSoftwareValidationResultListTable
    action_buttons = ("export",)
    template_name = "nautobot_device_lifecycle_mgmt/inventoryitemsoftwarevalidationresult_list.html"

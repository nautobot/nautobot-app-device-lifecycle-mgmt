"""Views implementation for the Lifecycle Management app."""

import base64
import io
import logging
import urllib

import matplotlib.pyplot as plt
import numpy as np
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, ExpressionWrapper, F, FloatField, Q
from django_tables2 import RequestConfig
from matplotlib.ticker import MaxNLocator
from nautobot.apps.choices import ColorChoices
from nautobot.apps.views import NautobotUIViewSet, ObjectView
from nautobot.core.models.querysets import count_related
from nautobot.core.views import generic
from nautobot.core.views.mixins import ContentTypePermissionRequiredMixin
from nautobot.core.views.paginator import EnhancedPaginator, get_paginate_count
from nautobot.dcim.models import Device, SoftwareVersion

from nautobot_device_lifecycle_mgmt import choices, filters, forms, models, tables
from nautobot_device_lifecycle_mgmt.api import serializers

PLUGIN_CFG = settings.PLUGINS_CONFIG["nautobot_device_lifecycle_mgmt"]

logger = logging.getLogger("nautobot_device_lifecycle_mgmt")

GREEN, RED, GREY = (f"#{ColorChoices.COLOR_LIGHT_GREEN}", f"#{ColorChoices.COLOR_RED}", f"#{ColorChoices.COLOR_GREY}")


class HardwareLCMUIViewSet(NautobotUIViewSet):
    """HardwareLCM UI ViewSet."""

    bulk_update_form_class = forms.HardwareLCMBulkEditForm
    filterset_class = filters.HardwareLCMFilterSet
    filterset_form_class = forms.HardwareLCMFilterForm
    form_class = forms.HardwareLCMForm
    queryset = models.HardwareLCM.objects.prefetch_related("device_type")
    serializer_class = serializers.HardwareLCMSerializer
    table_class = tables.HardwareLCMTable

    def get_extra_context(self, request, instance):  # pylint: disable=signature-differs
        """Return any additional context data for the template.

        request: The current request
        instance: The object being viewed
        """
        if not instance:
            return {}
        if instance.device_type:
            return {"devices": Device.objects.restrict(request.user, "view").filter(device_type=instance.device_type)}
        if instance.inventory_item:
            return {
                "devices": Device.objects.restrict(request.user, "view").filter(
                    inventory_items__part_id=instance.inventory_item
                )
            }
        return {"devices": []}


class ValidatedSoftwareLCMUIViewSet(NautobotUIViewSet):
    """ValidatedSoftwareLCM UI ViewSet."""

    # TODO: Add bulk edit form
    # bulk_update_form_class = forms.ValidatedSoftwareLCMBulkEditForm
    filterset_class = filters.ValidatedSoftwareLCMFilterSet
    filterset_form_class = forms.ValidatedSoftwareLCMFilterForm
    form_class = forms.ValidatedSoftwareLCMForm
    queryset = models.ValidatedSoftwareLCM.objects.all()
    serializer_class = serializers.ValidatedSoftwareLCMSerializer
    table_class = tables.ValidatedSoftwareLCMTable


# TODO: These should probably move to a StatsPanel using the Component UI Framework in 2.4+
class ValidatedSoftwareDeviceTabView(ObjectView):
    """Tab for Validated Software Devices."""

    queryset = models.ValidatedSoftwareLCM.objects.all()
    template_name = "nautobot_device_lifecycle_mgmt/validatedsoftwarelcm_devices_tab.html"


class ValidatedSoftwareDeviceTypeTabView(ObjectView):
    """Tab for Validated Software Device Types."""

    queryset = models.ValidatedSoftwareLCM.objects.all()
    template_name = "nautobot_device_lifecycle_mgmt/validatedsoftwarelcm_device_types_tab.html"


class ValidatedSoftwareDeviceRoleTabView(ObjectView):
    """Tab for Validated Software Device Roles."""

    queryset = models.ValidatedSoftwareLCM.objects.all()
    template_name = "nautobot_device_lifecycle_mgmt/validatedsoftwarelcm_device_roles_tab.html"


class ValidatedSoftwareInventoryItemTabView(ObjectView):
    """Tab for Validated Software Inventory Items."""

    queryset = models.ValidatedSoftwareLCM.objects.all()
    template_name = "nautobot_device_lifecycle_mgmt/validatedsoftwarelcm_inventory_items_tab.html"


class ValidatedSoftwareObjectTagTabView(ObjectView):
    """Tab for Validated Software Object Tags."""

    queryset = models.ValidatedSoftwareLCM.objects.all()
    template_name = "nautobot_device_lifecycle_mgmt/validatedsoftwarelcm_object_tags_tab.html"


class ContractLCMUIViewSet(NautobotUIViewSet):
    """ContractLCM UI ViewSet."""

    bulk_update_form_class = forms.ContractLCMBulkEditForm
    filterset_class = filters.ContractLCMFilterSet
    filterset_form_class = forms.ContractLCMFilterForm
    form_class = forms.ContractLCMForm
    queryset = models.ContractLCM.objects.all()
    serializer_class = serializers.ContractLCMSerializer
    table_class = tables.ContractLCMTable


class ProviderLCMUIViewSet(NautobotUIViewSet):
    """ProviderLCM UI ViewSet."""

    bulk_update_form_class = forms.ProviderLCMBulkEditForm
    filterset_class = filters.ProviderLCMFilterSet
    filterset_form_class = forms.ProviderLCMFilterForm
    form_class = forms.ProviderLCMForm
    queryset = models.ProviderLCM.objects.all()
    serializer_class = serializers.ProviderLCMSerializer
    table_class = tables.ProviderLCMTable

    def get_extra_context(self, request, instance):  # pylint: disable=signature-differs
        """Return any additional context data for the template.

        request: The current request
        instance: The object being viewed
        """
        return {"contracts": models.ContractLCM.objects.restrict(request.user, "view").filter(provider=instance)}


class CVELCMUIViewSet(NautobotUIViewSet):
    """CVELCM UI ViewSet."""

    bulk_update_form_class = forms.CVELCMBulkEditForm
    filterset_class = filters.CVELCMFilterSet
    filterset_form_class = forms.CVELCMFilterForm
    form_class = forms.CVELCMForm
    queryset = models.CVELCM.objects.all()
    serializer_class = serializers.CVELCMSerializer
    table_class = tables.CVELCMTable


class VulnerabilityLCMUIViewSet(NautobotUIViewSet):
    """VulnerabilityLCM UI ViewSet."""

    bulk_update_form_class = forms.VulnerabilityLCMBulkEditForm
    filterset_class = filters.VulnerabilityLCMFilterSet
    filterset_form_class = forms.VulnerabilityLCMFilterForm
    form_class = forms.VulnerabilityLCMForm
    queryset = models.VulnerabilityLCM.objects.all()
    serializer_class = serializers.VulnerabilityLCMSerializer
    table_class = tables.VulnerabilityLCMTable


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


class HardwareNoticeDeviceReportView(generic.ObjectListView):
    """View for executive report on device hardware notices."""

    filterset = filters.DeviceHardwareNoticeResultFilterSet
    filterset_form = forms.DeviceHardwareNoticeResultFilterForm
    table = tables.DeviceHardwareNoticeResultTable
    template_name = "nautobot_device_lifecycle_mgmt/hardwarenotice_device_report.html"
    queryset = (
        models.DeviceHardwareNoticeResult.objects.values("device__device_type__model", "device__device_type__pk")
        .distinct()
        .annotate(
            total=Count("device__device_type__model"),
            valid=Count("device__device_type__model", filter=Q(is_supported=True)),
            invalid=Count("device__device_type__model", filter=Q(is_supported=False)),
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
                models.DeviceHardwareNoticeResult.objects.filter(run_type=choices.ReportRunTypeChoices.REPORT_FULL_RUN)
                .latest("last_updated")
                .last_run
            )
        except models.DeviceHardwareNoticeResult.DoesNotExist:  # pylint: disable=no-member
            report_last_run = None

        device_aggr = self.get_global_aggr(request)
        _device_type_qs = (
            models.DeviceHardwareNoticeResult.objects.values("device__device_type__model", "device__device_type__id")
            .distinct()
            .annotate(
                total=Count("device__device_type__model"),
                valid=Count("device__device_type__model", filter=Q(is_supported=True)),
                invalid=Count("device__device_type__model", filter=Q(is_supported=False)),
                valid_percent=ExpressionWrapper(100 * F("valid") / (F("total")), output_field=FloatField()),
            )
            .order_by("-hardware_notice__end_of_support")
        )
        device_type_qs = self.filterset(request.GET, _device_type_qs).qs
        pie_chart_attrs = {
            "aggr_labels": ["valid", "invalid"],
            "chart_labels": ["Supported", "Unsupported"],
        }
        bar_chart_attrs = {
            "device_type_id": "device__device_type__id",
            "label_accessor": "device__device_type__model",
            "xlabel": "Devices",
            "ylabel": "Device Types",
            "title": "Devices per device type",
            "chart_bars": [
                {"label": "Supported", "data_attr": "valid", "color": GREEN},
                {"label": "Unsupported", "data_attr": "invalid", "color": RED},
            ],
        }
        self.extra_content = {
            "bar_chart": ReportOverviewHelper.plot_barchart_visual_hardware_notice(device_type_qs, bar_chart_attrs),
            "device_aggr": device_aggr,
            "device_visual": ReportOverviewHelper.plot_piechart_visual(device_aggr, pie_chart_attrs),
            "report_last_run": report_last_run,
        }

    def get_global_aggr(self, request):
        """Get device and inventory global reports.

        Returns:
            device_aggr: device global report dict
        """
        device_qs = models.DeviceHardwareNoticeResult.objects

        device_aggr = {}
        if self.filterset is not None:
            device_aggr = self.filterset(request.GET, device_qs).qs.aggregate(
                total=Count("device"),
                valid=Count("device", filter=Q(is_supported=True)),
                invalid=Count("device", filter=Q(is_supported=False)),
            )

            device_aggr["name"] = "Devices"

        return ReportOverviewHelper.calculate_aggr_percentage(device_aggr)

    def extra_context(self):
        """Extra content method on."""
        # add global aggregations to extra context.

        return self.extra_content


class ValidatedSoftwareDeviceReportView(generic.ObjectListView):
    """View for executive report on software Validation."""

    filterset = filters.DeviceSoftwareValidationResultFilterSet
    filterset_form = forms.DeviceSoftwareValidationResultFilterForm
    table = tables.DeviceSoftwareValidationResultTable
    template_name = "nautobot_device_lifecycle_mgmt/validatedsoftware_device_report.html"
    queryset = (
        models.DeviceSoftwareValidationResult.objects.values("device__device_type__model", "device__device_type__pk")
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
        super().setup(request, *args, **kwargs)
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
        _platform_qs = (
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
        device_qs = models.DeviceSoftwareValidationResult.objects

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


class DeviceHardwareNoticeResultListView(generic.ObjectListView):
    """DeviceHardwareNoticeResultListView List view."""

    queryset = models.DeviceHardwareNoticeResult.objects.all()
    filterset = filters.DeviceHardwareNoticeResultFilterSet
    filterset_form = forms.DeviceHardwareNoticeResultFilterForm
    table = tables.DeviceHardwareNoticeResultListTable
    action_buttons = ("export",)
    template_name = "nautobot_device_lifecycle_mgmt/deviceshardwarenoticeresult_list.html"


class DeviceSoftwareValidationResultListView(generic.ObjectListView):
    """DeviceSoftawareValidationResult List view."""

    queryset = models.DeviceSoftwareValidationResult.objects.all()
    filterset = filters.DeviceSoftwareValidationResultFilterSet
    filterset_form = forms.DeviceSoftwareValidationResultFilterForm
    table = tables.DeviceSoftwareValidationResultListTable
    action_buttons = ("export",)
    template_name = "nautobot_device_lifecycle_mgmt/devicesoftwarevalidationresult_list.html"


class ValidatedSoftwareInventoryItemReportView(generic.ObjectListView):
    """View for executive report on inventory item software validation."""

    filterset = filters.InventoryItemSoftwareValidationResultFilterSet
    filterset_form = forms.InventoryItemSoftwareValidationResultFilterForm
    table = tables.InventoryItemSoftwareValidationResultTable
    template_name = "nautobot_device_lifecycle_mgmt/validatedsoftware_inventoryitem_report.html"
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
                models.InventoryItemSoftwareValidationResult.objects.filter(
                    run_type=choices.ReportRunTypeChoices.REPORT_FULL_RUN
                )
                .latest("last_updated")
                .last_run
            )
        except models.InventoryItemSoftwareValidationResult.DoesNotExist:  # pylint: disable=no-member
            report_last_run = None

        inventory_aggr = self.get_global_aggr(request)
        _platform_qs = (
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
        inventory_item_qs = models.InventoryItemSoftwareValidationResult.objects

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

    queryset = models.InventoryItemSoftwareValidationResult.objects.all()
    filterset = filters.InventoryItemSoftwareValidationResultFilterSet
    filterset_form = forms.InventoryItemSoftwareValidationResultFilterForm
    table = tables.InventoryItemSoftwareValidationResultListTable
    action_buttons = ("export",)
    template_name = "nautobot_device_lifecycle_mgmt/inventoryitemsoftwarevalidationresult_list.html"


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

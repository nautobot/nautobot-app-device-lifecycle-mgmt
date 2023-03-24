"""Nautobot Lifecycle Management plugin application level metrics ."""
# from prometheus_client import Gauge
# from prometheus_client.core import GaugeMetricFamily


# def metric_example():
#     """Calculate number of MODEL objects.

#     Yields:
#         GaugeMetricFamily: Prometheus Metrics
#     """
#     features = MODEL.objects.all()

#     example_gauge = GaugeMetricFamily("name", "description", labels=[""])

#     if True:
#         example_gauge.add_metric(labels=[""], value=MODEL.objects.filter().count())
#     else:
#         example_gauge.add_metric(labels=[""], value=0)

#     yield example_gauge

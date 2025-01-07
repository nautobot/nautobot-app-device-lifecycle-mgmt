"""Filtering for nautobot_device_lifecycle_mgmt."""

from nautobot.apps.filters import NameSearchFilterSet, NautobotFilterSet

from nautobot_device_lifecycle_mgmt import models


class HardwareLCMFilterSet(NautobotFilterSet, NameSearchFilterSet):  # pylint: disable=too-many-ancestors
    """Filter for HardwareLCM."""

    class Meta:
        """Meta attributes for filter."""

        model = models.HardwareLCM

        # add any fields from the model that you would like to filter your searches by using those
        fields = ["id", "name", "description"]

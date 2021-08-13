"""GraphQL implementation for the Device LifeCycle Management plugin."""
from nautobot.extras.graphql.types import DjangoObjectType
from nautobot_device_lifecycle_mgmt.models import HardwareLCM
from nautobot_device_lifecycle_mgmt.filters import HardwareLCMFilterSet


class HardwareLCMType(DjangoObjectType):
    """Graphql Type Object for the Device Lifecycle model."""

    class Meta:
        """Metadata magic method for the HardwareLCMType."""

        model = HardwareLCM
        filterset_class = HardwareLCMFilterSet


graphql_types = [
    HardwareLCMType,
]

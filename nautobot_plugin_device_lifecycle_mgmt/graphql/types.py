"""GraphQL implementation for the Device LifeCycle Management plugin."""
import graphene
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field
from taggit.managers import TaggableManager

from nautobot.extras.graphql.types import TagType
from nautobot.dcim.models import Device
from nautobot_plugin_device_lifecycle_mgmt.models import HardwareLCM
from nautobot_plugin_device_lifecycle_mgmt.filters import HardwareLCMNoticeFilter


@convert_django_field.register(TaggableManager)
def convert_field_to_list_tags(field, registry=None):
    """Convert TaggableManager to List of Tags."""
    return graphene.List(TagType)


class LCMDevice(DjangoObjectType):
    """GraphQL representation of a Nautobot Device."""

    class Meta:
        """Metadata magic method for the DjangoObjectType."""

        model = Device


class HardwareLCMType(DjangoObjectType):
    """Graphql Type Object for the Device Lifecycle model."""

    devices = graphene.List(LCMDevice)

    def resolve_devices(self, info, **kwargs):
        """Custom resolver to filter devices that are part of the hardware LifeCycle object."""
        if self.device_type:
            return Device.objects.filter(device_type=self.device_type)
        if self.inventory_item:
            return Device.objects.filter(inventoryitems__part_id=self.inventory_item)
        return []

    class Meta:
        """Metadata magic method for the HardwareLCMType."""

        model = HardwareLCM
        filterset_class = HardwareLCMNoticeFilter


graphql_types = [
    HardwareLCMType,
]

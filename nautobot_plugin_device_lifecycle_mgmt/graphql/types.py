"""GraphQL implementation for golden config plugin."""
import graphene
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field
from taggit.managers import TaggableManager

from nautobot.extras.graphql.types import TagType
from nautobot_plugin_device_lifecycle_mgmt.models import HardwareLCM
from nautobot_plugin_device_lifecycle_mgmt.filters import HardwareLCMNoticeFilter


@convert_django_field.register(TaggableManager)
def convert_field_to_list_tags(field, registry=None):
    """Convert TaggableManager to List of Tags."""
    return graphene.List(TagType)


class HardwareLCMType(DjangoObjectType):
    """Graphql Type Object for the Device Lifecycle model."""

    class Meta:
        """Metadata HardwareLCMType."""

        model = HardwareLCM
        filterset_class = HardwareLCMNoticeFilter


graphql_types = [
    HardwareLCMType,
]

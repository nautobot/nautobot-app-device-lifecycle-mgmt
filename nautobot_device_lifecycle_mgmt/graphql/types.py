"""GraphQL implementation for the Device LifeCycle Management plugin."""
import graphene

from graphene_django import DjangoObjectType

from nautobot_device_lifecycle_mgmt.models import (
    ValidatedSoftwareLCM,
)
from nautobot_device_lifecycle_mgmt.filters import (
    ValidatedSoftwareLCMFilterSet,
)


class ValidatedSoftwareLCMType(DjangoObjectType):
    """Graphql Type Object for the ValidatedSoftwareLCM model."""

    valid = graphene.Boolean()

    class Meta:
        """Metadata magic method for the ValidatedSoftwareLCM."""

        model = ValidatedSoftwareLCM
        filterset_class = ValidatedSoftwareLCMFilterSet


graphql_types = [
    ValidatedSoftwareLCMType,
]

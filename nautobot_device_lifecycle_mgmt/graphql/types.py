"""GraphQL implementation for the Device LifeCycle Management app."""

import graphene
from graphene_django import DjangoObjectType

from nautobot_device_lifecycle_mgmt.filters import ValidatedSoftwareLCMFilterSet
from nautobot_device_lifecycle_mgmt.models import ValidatedSoftwareLCM


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

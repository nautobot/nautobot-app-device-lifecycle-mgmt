"""GraphQL implementation for the Device LifeCycle Management plugin."""
import graphene

from graphene_django import DjangoObjectType
from nautobot_device_lifecycle_mgmt.models import (
    HardwareLCM,
    ContractLCM,
    ProviderLCM,
    ContactLCM,
    ValidatedSoftwareLCM,
)
from nautobot_device_lifecycle_mgmt.filters import (
    HardwareLCMFilterSet,
    ContractLCMFilterSet,
    ProviderLCMFilterSet,
    ContactLCMFilterSet,
    ValidatedSoftwareLCMFilterSet,
)


class HardwareLCMType(DjangoObjectType):
    """Graphql Type Object for the Device Lifecycle model."""

    class Meta:
        """Metadata magic method for the HardwareLCMType."""

        model = HardwareLCM
        filterset_class = HardwareLCMFilterSet


class ContractLCMType(DjangoObjectType):
    """Graphql Type Object for the Device Lifecycle model."""

    class Meta:
        """Metadata magic method for the ContractLCMType."""

        model = ContractLCM
        filterset_class = ContractLCMFilterSet


class ProviderLCMType(DjangoObjectType):
    """Graphql Type Object for the Device Lifecycle model."""

    class Meta:
        """Metadata magic method for the ProviderLCMType."""

        model = ProviderLCM
        filterset_class = ProviderLCMFilterSet


class ContactLCMType(DjangoObjectType):
    """Graphql Type Object for the Device Lifecycle model."""

    class Meta:
        """Metadata magic method for the ContactLCMType."""

        model = ContactLCM
        filterset_class = ContactLCMFilterSet


class ValidatedSoftwareLCMType(DjangoObjectType):
    """Graphql Type Object for the ValidatedSoftwareLCM model."""

    valid = graphene.Boolean()

    class Meta:
        """Metadata magic method for the ValidatedSoftwareLCM."""

        model = ValidatedSoftwareLCM
        filterset_class = ValidatedSoftwareLCMFilterSet


graphql_types = [
    HardwareLCMType,
    ContractLCMType,
    ProviderLCMType,
    ContactLCMType,
    ValidatedSoftwareLCMType,
]

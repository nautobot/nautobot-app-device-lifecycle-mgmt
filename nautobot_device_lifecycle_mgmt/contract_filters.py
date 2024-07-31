"""Filters for contract Lifecycle QuerySets."""

from django.db.models import Q


class DeviceContractFilter:
    """Filter ContractLCM objects based on the Device object."""

    def __init__(self, qs, item_obj):  # pylint: disable=invalid-name
        """Initalize DeviceContractFilter."""
        self.contract_qs = qs
        self.item_obj = item_obj

    def filter_qs(self):
        """Returns filtered ContractLCM query set."""
        self.contract_qs = self.contract_qs.filter(Q(devices=self.item_obj.pk)).distinct()

        return self.contract_qs


class InventoryItemContractFilter:
    """Filter ContractLCM objects based on the InventoryItem object."""

    def __init__(self, qs, item_obj):  # pylint: disable=invalid-name
        """Initalize InventoryItemContractFilter."""
        self.contract_qs = qs
        self.item_obj = item_obj

    def filter_qs(self):
        """Returns filtered InventoryItemContractFilter query set."""
        self.contract_qs = self.contract_qs.filter(Q(inventory_items=self.item_obj.pk)).distinct()

        return self.contract_qs

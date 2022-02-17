"""Filters for Software Lifecycle QuerySets."""

from django.db.models import Case, IntegerField, Q, Value, When


class DeviceValidatedSoftwareFilter:  # pylint: disable=too-few-public-methods
    """Filter ValidatedSoftwareLCM objects based on the Device object."""

    def __init__(self, qs, item_obj):
        """Initalize DeviceValidatedSoftwareFilter."""
        self.validated_software_qs = qs
        self.item_obj = item_obj

    def filter_qs(self):
        """Returns filtered ValidatedSoftwareLCM query set."""
        self.validated_software_qs = self.validated_software_qs.filter(
            Q(devices=self.item_obj.pk)
            | Q(device_types=self.item_obj.device_type.pk, device_roles=self.item_obj.device_role.pk)
            | Q(device_types=self.item_obj.device_type.pk, device_roles=None)
            | Q(device_types=None, device_roles=self.item_obj.device_role.pk)
            | Q(object_tags__in=self.item_obj.tags.all())
        ).distinct()

        self.validated_software_qs = self._add_weights().order_by("weight", "start")

        return self.validated_software_qs

    def _add_weights(self):
        """Adds weights to allow ordering of the ValidatedSoftwareLCM assignments."""
        return self.validated_software_qs.annotate(
            weight=Case(
                When(devices=self.item_obj.pk, preferred=True, then=Value(10)),
                When(devices=self.item_obj.pk, preferred=False, then=Value(1000)),
                When(
                    device_types=self.item_obj.device_type.pk,
                    device_roles=self.item_obj.device_role.pk,
                    preferred=True,
                    then=Value(20),
                ),
                When(
                    device_types=self.item_obj.device_type.pk,
                    device_roles=self.item_obj.device_role.pk,
                    preferred=False,
                    then=Value(1010),
                ),
                When(device_types=self.item_obj.device_type.pk, device_roles=None, preferred=True, then=Value(30)),
                When(device_types=self.item_obj.device_type.pk, device_roles=None, preferred=False, then=Value(1030)),
                When(device_roles=self.item_obj.device_role.pk, preferred=True, then=Value(40)),
                When(device_roles=self.item_obj.device_role.pk, preferred=False, then=Value(1040)),
                When(preferred=True, then=Value(990)),
                default=Value(1990),
                output_field=IntegerField(),
            )
        )


class InventoryItemValidatedSoftwareFilter:  # pylint: disable=too-few-public-methods
    """Filter ValidatedSoftwareLCM objects based on the InventoryItem object."""

    def __init__(self, qs, item_obj):
        """Initalize InventoryItemValidatedSoftwareFilter."""
        self.validated_software_qs = qs
        self.item_obj = item_obj

    def filter_qs(self):
        """Returns filtered ValidatedSoftwareLCM query set."""
        validated_software_qs = self.validated_software_qs.filter(
            Q(inventory_items=self.item_obj.pk) | Q(object_tags__in=self.item_obj.tags.all())
        ).distinct()

        self.validated_software_qs = self._add_weights().order_by("weight", "start")

        return validated_software_qs

    def _add_weights(self):
        """Adds weights to allow ordering of the ValidatedSoftwareLCM assignments."""
        return self.validated_software_qs.annotate(
            weight=Case(
                When(devices=self.item_obj.pk, preferred=True, then=Value(10)),
                When(devices=self.item_obj.pk, preferred=False, then=Value(1000)),
                When(preferred=True, then=Value(20)),
                When(preferred=False, then=Value(1010)),
                default=Value(1990),
                output_field=IntegerField(),
            )
        )

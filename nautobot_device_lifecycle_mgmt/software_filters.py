"""Filters for Software Lifecycle QuerySets."""

from django.contrib.contenttypes.models import ContentType
from django.db.models import Case, IntegerField, Q, Subquery, Value, When
from nautobot.dcim.models import Device, InventoryItem
from nautobot.extras.models import RelationshipAssociation

from nautobot_device_lifecycle_mgmt.utils import multi_tenant_mode_enabled


class BaseSoftwareFilter:
    """Base class for SoftwareFilter classes."""

    soft_obj_model = None
    soft_relation_name = None

    def __init__(self, qs, item_obj):  # pylint: disable=invalid-name
        """Initalize BaseSoftwareFilter."""
        self.software_qs = qs
        self.item_obj = item_obj

    def filter_qs(self):
        """Returns filtered SoftwareLCM query set."""
        soft_rel_sq = RelationshipAssociation.objects.filter(
            relationship__key=self.soft_relation_name,
            destination_type=ContentType.objects.get_for_model(self.soft_obj_model),
            destination_id=self.item_obj.id,
        ).values("source_id")[:1]
        self.software_qs = self.software_qs.filter(id=Subquery(soft_rel_sq))

        return self.software_qs


class DeviceSoftwareFilter(BaseSoftwareFilter):
    """Filter SoftwareLCM objects based on the Device object."""

    soft_obj_model = Device
    soft_relation_name = "device_soft"


class InventoryItemSoftwareFilter(BaseSoftwareFilter):
    """Filter SoftwareLCM objects based on the Device object."""

    soft_obj_model = InventoryItem
    soft_relation_name = "inventory_item_soft"


class DeviceValidatedSoftwareFilter:
    """Filter ValidatedSoftwareLCM objects based on the Device object."""

    def __init__(self, qs, item_obj):  # pylint: disable=invalid-name
        """Initalize DeviceValidatedSoftwareFilter."""
        self.validated_software_qs = qs
        self.item_obj = item_obj

    def filter_qs(self):
        """Return the filtered, weight-ordered ValidatedSoftwareLCM queryset."""
        if multi_tenant_mode_enabled():
            self.validated_software_qs = self._filter_multi_tenant_mode()
        else:
            self.validated_software_qs = self._filter_legacy_mode()

        self.validated_software_qs = self._add_weights().order_by("weight", "start")

        return self.validated_software_qs

    def _filter_legacy_mode(self):
        """Return the queryset filtered without tenant-awareness."""
        return (
            self.validated_software_qs.filter(device_tenants__isnull=True)
            .filter(
                Q(devices=self.item_obj.pk)
                | Q(device_types=self.item_obj.device_type.pk, device_roles=self.item_obj.role.pk)
                | Q(device_types=self.item_obj.device_type.pk, device_roles=None)
                | Q(device_types=None, device_roles=self.item_obj.role.pk)
                | Q(object_tags__in=self.item_obj.tags.all())
            )
            .distinct()
        )

    def _filter_multi_tenant_mode(self):
        """Return the queryset filtered with tenant-aware matching."""
        if self.item_obj.tenant:
            return self.validated_software_qs.filter(
                Q(devices=self.item_obj.pk)
                | Q(
                    device_tenants=self.item_obj.tenant,
                    device_types=self.item_obj.device_type.pk,
                    device_roles=self.item_obj.role.pk,
                )
                | Q(
                    device_tenants=self.item_obj.tenant,
                    device_types=self.item_obj.device_type.pk,
                    device_roles=None,
                )
                | Q(
                    device_tenants=self.item_obj.tenant,
                    device_types=None,
                    device_roles=self.item_obj.role.pk,
                )
                | Q(device_tenants=self.item_obj.tenant, device_types=None, device_roles=None)
                | Q(object_tags__in=self.item_obj.tags.all())
            ).distinct()
        # Device has no tenant: match only untenanted records via the legacy criteria.
        return self.validated_software_qs.filter(
            Q(devices=self.item_obj.pk, device_tenants__isnull=True)
            | Q(
                device_types=self.item_obj.device_type.pk,
                device_roles=self.item_obj.role.pk,
                device_tenants__isnull=True,
            )
            | Q(device_types=self.item_obj.device_type.pk, device_roles=None, device_tenants__isnull=True)
            | Q(device_types=None, device_roles=self.item_obj.role.pk, device_tenants__isnull=True)
            | Q(object_tags__in=self.item_obj.tags.all(), device_tenants__isnull=True)
        ).distinct()

    def _add_weights(self):
        """Return the queryset annotated with an integer `weight` field for ordering."""
        return self.validated_software_qs.annotate(
            weight=Case(
                When(devices=self.item_obj.pk, preferred=True, then=Value(10)),
                When(devices=self.item_obj.pk, preferred=False, then=Value(1000)),
                When(
                    device_types=self.item_obj.device_type.pk,
                    device_roles=self.item_obj.role.pk,
                    preferred=True,
                    then=Value(20),
                ),
                When(
                    device_types=self.item_obj.device_type.pk,
                    device_roles=self.item_obj.role.pk,
                    preferred=False,
                    then=Value(1010),
                ),
                When(device_types=self.item_obj.device_type.pk, device_roles=None, preferred=True, then=Value(30)),
                When(device_types=self.item_obj.device_type.pk, device_roles=None, preferred=False, then=Value(1030)),
                When(device_roles=self.item_obj.role.pk, preferred=True, then=Value(40)),
                When(device_roles=self.item_obj.role.pk, preferred=False, then=Value(1040)),
                When(preferred=True, then=Value(990)),
                default=Value(1990),
                output_field=IntegerField(),
            )
        )


class InventoryItemValidatedSoftwareFilter:
    """Filter ValidatedSoftwareLCM objects based on the InventoryItem object."""

    def __init__(self, qs, item_obj):  # pylint: disable=invalid-name
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


class DeviceSoftwareImageFilter:
    """Filter SoftwareImageLCM objects based on the Device object."""

    soft_obj_model = Device
    soft_relation_name = "device_soft"

    def __init__(self, qs, item_obj):  # pylint: disable=invalid-name
        """Initalize DeviceSoftwareImageLCMFilter."""
        self.softwareimage_qs = qs
        self.item_obj = item_obj

    def filter_qs(self):
        """Returns filtered SoftwareImageLCM query set."""
        soft_rel_obj = RelationshipAssociation.objects.filter(
            relationship__key=self.soft_relation_name,
            destination_type=ContentType.objects.get_for_model(self.soft_obj_model),
            destination_id=self.item_obj.id,
        ).values("source_id")[:1]

        object_tag_q = Q(software=soft_rel_obj, object_tags__in=self.item_obj.tags.all())
        device_type_q = Q(software=soft_rel_obj, device_types=self.item_obj.device_type)
        default_image_q = Q(software=soft_rel_obj, default_image=True)

        device_soft_image_ot_qs = self.softwareimage_qs.filter(object_tag_q)
        if device_soft_image_ot_qs.exists():
            return device_soft_image_ot_qs

        device_soft_image_dt_qs = self.softwareimage_qs.filter(device_type_q)
        if device_soft_image_dt_qs.exists():
            return device_soft_image_dt_qs

        return self.softwareimage_qs.filter(default_image_q)


class InventoryItemSoftwareImageFilter:
    """Filter SoftwareImageLCM objects based on the InventoryItem object."""

    soft_obj_model = InventoryItem
    soft_relation_name = "inventory_item_soft"

    def __init__(self, qs, item_obj):  # pylint: disable=invalid-name
        """Initalize InventoryItemSoftwareImageLCMFilter."""
        self.softwareimage_qs = qs
        self.item_obj = item_obj

    def filter_qs(self):
        """Returns filtered SoftwareImageLCM query set."""
        soft_rel_obj = RelationshipAssociation.objects.filter(
            relationship__key=self.soft_relation_name,
            destination_type=ContentType.objects.get_for_model(self.soft_obj_model),
            destination_id=self.item_obj.id,
        ).values("source_id")[:1]

        object_tag_q = Q(software=soft_rel_obj, object_tags__in=self.item_obj.tags.all())
        inv_item_q = Q(software=soft_rel_obj, inventory_items=self.item_obj.pk)
        default_image_q = Q(software=soft_rel_obj, default_image=True)

        invitem_soft_image_ot_qs = self.softwareimage_qs.filter(object_tag_q)
        if invitem_soft_image_ot_qs.exists():
            return invitem_soft_image_ot_qs

        invitem_soft_image_dt_qs = self.softwareimage_qs.filter(inv_item_q)
        if invitem_soft_image_dt_qs.exists():
            return invitem_soft_image_dt_qs

        return self.softwareimage_qs.filter(default_image_q)

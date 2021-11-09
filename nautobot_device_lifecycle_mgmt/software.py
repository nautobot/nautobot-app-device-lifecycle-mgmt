"""Django classes and functions handling Software Lifecycle related functionality."""

from datetime import date

from django.db.models import Case, IntegerField, Q, Value, When
from django.contrib.contenttypes.models import ContentType
from nautobot.extras.models import RelationshipAssociation

from .models import ValidatedSoftwareLCM, SoftwareLCM
from .tables import ValidatedSoftwareLCMTable


class ItemSoftware:
    """Base class providing functions for computing SoftwareLCM and ValidatedSoftwareLCM related objects."""

    def __init__(self, item_obj, soft_obj_model=None, soft_relation_name=None, valid_only=False):
        """Initalize ItemSoftware object."""
        self.item_obj = item_obj
        self.soft_obj_model = soft_obj_model
        self.soft_relation_name = soft_relation_name
        self.valid_only = valid_only

        if soft_relation_name:
            self.software = self.get_software()
        else:
            self.software = None

        self.validated_software_qs = self.get_validated_software_qs()

    def get_software(self):
        """Get software assigned to the object."""
        try:
            obj_soft_relation = RelationshipAssociation.objects.get(
                relationship__slug=self.soft_relation_name,
                destination_type=ContentType.objects.get_for_model(self.soft_obj_model),
                destination_id=self.item_obj.id,
            )
            obj_soft = SoftwareLCM.objects.get(id=obj_soft_relation.source_id)
        except (RelationshipAssociation.DoesNotExist, SoftwareLCM.DoesNotExist):
            obj_soft = None

        return obj_soft

    def get_validated_software_qs(self):
        """Returns ValidatedSoftware query set. Implemented by subclasses."""
        raise NotImplementedError

    def get_validated_software_table(self):
        """Returns table of validated software linked to the object."""
        if not self.validated_software_qs:
            return None

        return ValidatedSoftwareLCMTable(
            list(self.validated_software_qs),
            orderable=False,
            exclude=(
                "software",
                "start",
                "actions",
            ),
        )

    def validate_software(self, preferred_only=False):
        """Validate software against the validated software objects."""
        if not (self.software or self.validated_software_qs.count()):
            return False

        validated_software_versions = self.validated_software_qs.filter(software=self.software)
        if preferred_only:
            validated_software_versions = validated_software_versions.filter(preferred_only=True)

        return validated_software_versions.count() > 0


class DeviceSoftware(ItemSoftware):
    """Computes validated software objects for Device objects."""

    def get_validated_software_qs(self):
        """Returns ValidatedSoftware query set."""
        validated_software_qs = ValidatedSoftwareLCM.objects.filter(
            Q(devices=self.item_obj.pk)
            | Q(device_types=self.item_obj.device_type.pk, device_roles=self.item_obj.device_role.pk)
            | Q(device_types=self.item_obj.device_type.pk, device_roles=None)
            | Q(device_types=None, device_roles=self.item_obj.device_role.pk)
            | Q(object_tags__in=self.item_obj.tags.all())
        ).distinct()

        validated_software_qs = self.add_qs_weight_annotation(validated_software_qs).order_by("weight", "start")

        if self.valid_only:
            today = date.today()
            validated_software_qs = validated_software_qs.filter(
                Q(start__lte=today, end=None) | Q(start__lte=today, end__gte=today)
            )

        return validated_software_qs

    def add_qs_weight_annotation(self, qs):
        """Adds weights to allow ordering of the Validated Software assignments."""
        return qs.annotate(
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


class InventoryItemSoftware(ItemSoftware):
    """Computes validated software objects for InventoryItem objects."""

    def get_validated_software_qs(self):
        """Returns ValidatedSoftware query set."""
        validated_software_qs = (
            ValidatedSoftwareLCM.objects.filter(
                Q(inventory_items=self.item_obj.pk) | Q(object_tags__in=self.item_obj.tags.all())
            )
            .annotate(
                weight=Case(
                    When(devices=self.item_obj.pk, preferred=True, then=Value(10)),
                    When(devices=self.item_obj.pk, preferred=False, then=Value(1000)),
                    When(preferred=True, then=Value(20)),
                    When(preferred=False, then=Value(1010)),
                    default=Value(1990),
                    output_field=IntegerField(),
                )
            )
            .order_by("weight", "start")
        )

        return validated_software_qs

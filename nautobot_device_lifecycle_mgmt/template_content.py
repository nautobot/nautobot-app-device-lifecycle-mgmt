"""Extended core templates for the LifeCycle Management plugin."""
from abc import ABCMeta

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from nautobot.dcim.models import Device
from nautobot.extras.models import RelationshipAssociation
from nautobot.extras.plugins import PluginTemplateExtension
from nautobot.dcim.models import InventoryItem
from .models import HardwareLCM, SoftwareLCM, ValidatedSoftwareLCM
from .tables import ValidatedSoftwareLCMTable


class DeviceTypeHWLCM(PluginTemplateExtension, metaclass=ABCMeta):
    """Class to add table for HardwareLCM related to device type."""

    model = "dcim.devicetype"

    def right_page(self):
        """Display table on right side of page."""
        devtype_obj = self.context["object"]

        return self.render(
            "nautobot_device_lifecycle_mgmt/inc/general_notice.html",
            extra_context={"hw_notices": HardwareLCM.objects.filter(device_type=devtype_obj.pk)},
        )


class DeviceHWLCM(PluginTemplateExtension, metaclass=ABCMeta):
    """Class to add table for DeviceHWLCM related to device type."""

    model = "dcim.device"

    def right_page(self):
        """Display table on right side of page."""
        dev_obj = self.context["object"]

        return self.render(
            "nautobot_device_lifecycle_mgmt/inc/device_notice.html",
            extra_context={
                "hw_notices": HardwareLCM.objects.filter(
                    Q(device_type=dev_obj.device_type)
                    | Q(
                        inventory_item__in=[
                            i.part_id for i in InventoryItem.objects.filter(device__pk=dev_obj.pk) if i.part_id
                        ]
                    )
                )
            },
        )


class InventoryItemHWLCM(PluginTemplateExtension, metaclass=ABCMeta):
    """Class to add table for InventoryItemHWLCM related to inventory items."""

    model = "dcim.inventoryitem"

    def right_page(self):
        """Display table on right side of page."""
        inv_item_obj = self.context["object"]

        return self.render(
            "nautobot_device_lifecycle_mgmt/inc/general_notice.html",
            extra_context={"hw_notices": HardwareLCM.objects.filter(inventory_item=inv_item_obj.part_id)},
        )


class ValidatedSoftwareLCMListMixIn:
    """Mixin to add `validated_soft_list` and `validated_soft_table` properties."""

    @property
    def validated_soft_list(self):
        """Property returning list of validated software linked to the object."""
        qfilters = [
            Q(
                assigned_to_content_type=ContentType.objects.get(app_label="dcim", model=qmodel),
                assigned_to_object_id=qattr,
            )
            for qmodel, qattr in self.valid_soft_filters
        ]

        valid_soft_filter = qfilters.pop()
        for qfilter in qfilters:
            valid_soft_filter = valid_soft_filter | qfilter

        validsoft_list = ValidatedSoftwareLCM.objects.filter(valid_soft_filter)
        if not validsoft_list.exists():
            return None

        return validsoft_list

    @property
    def validated_soft_table(self):
        """Property returning table of validated software linked to the object."""
        if not self.validated_soft_list:
            return None

        return ValidatedSoftwareLCMTable(
            list(self.validated_soft_list),
            orderable=False,
            exclude=(
                "name",
                "actions",
            ),
        )


class SoftwareLCMMixIn:
    """Mixin to add `software` and `valid_software` properties."""

    @property
    def software(self):
        """Property software assigned to the object."""
        try:
            obj_soft_relation = RelationshipAssociation.objects.get(
                relationship__slug=self.soft_relation_name,
                destination_type=ContentType.objects.get_for_model(self.obj_model),
                destination_id=self.dst_obj_id,
            )
            obj_soft = SoftwareLCM.objects.get(id=obj_soft_relation.source_id)
        except (RelationshipAssociation.DoesNotExist, SoftwareLCM.DoesNotExist):
            obj_soft = None

        return obj_soft

    @property
    def valid_software(self):
        """Property checking whether software is valid."""
        if not (self.validated_soft_list and self.software):
            return False

        soft_valid_obj = self.validated_soft_list.filter(software_id=self.software)
        return soft_valid_obj.exists() and soft_valid_obj[0].valid


class DeviceSoftwareLCMAndValidatedSoftwareLCM(
    PluginTemplateExtension, ValidatedSoftwareLCMListMixIn, SoftwareLCMMixIn
):  # pylint: disable=abstract-method
    """Class to add table for SoftwareLCM and ValidatedSoftwareLCM related to device."""

    model = "dcim.device"

    def __init__(self, context):
        """Init setting up the DeviceSoftwareLCMAndValidatedSoftwareLCM object."""
        super().__init__(context)
        self.soft_relation_name = "device_soft"
        self.obj_model = Device
        self.parent_obj = self.context["object"]
        self.dst_obj_id = self.parent_obj.pk
        self.valid_soft_filters = (("device", self.parent_obj.pk), ("devicetype", self.parent_obj.device_type.pk))

    def right_page(self):
        """Display table on right side of page."""
        extra_context = {
            "validsoft_table": self.validated_soft_table,
            "obj_soft": self.software,
            "obj_soft_valid": self.valid_software,
        }

        return self.render(
            "nautobot_device_lifecycle_mgmt/inc/software_and_validatedsoftware_info.html",
            extra_context=extra_context,
        )


class InventoryItemSoftwareLCMAndValidatedSoftwareLCM(
    PluginTemplateExtension, ValidatedSoftwareLCMListMixIn, SoftwareLCMMixIn
):  # pylint: disable=abstract-method
    """Class to add table for SoftwareLCM and ValidatedSoftwareLCM related to inventory item."""

    model = "dcim.inventoryitem"

    def __init__(self, context):
        """Init setting up the InventoryItemSoftwareLCMAndValidatedSoftwareLCM object."""
        super().__init__(context)
        self.soft_relation_name = "inventory_item_soft"
        self.obj_model = InventoryItem
        self.parent_obj = self.context["object"]
        self.dst_obj_id = self.parent_obj.pk
        self.valid_soft_filters = (("inventoryitem", self.parent_obj.pk),)

    def right_page(self):
        """Display table on right side of page."""
        extra_context = {
            "validsoft_table": self.validated_soft_table,
            "obj_soft": self.software,
            "obj_soft_valid": self.valid_software,
        }

        return self.render(
            "nautobot_device_lifecycle_mgmt/inc/software_and_validatedsoftware_info.html",
            extra_context=extra_context,
        )


class DeviceTypeValidatedSoftwareLCM(
    PluginTemplateExtension, ValidatedSoftwareLCMListMixIn
):  # pylint: disable=abstract-method
    """Class to add table for ValidatedSoftwareLCM related to device type."""

    model = "dcim.devicetype"

    def __init__(self, context):
        """Init setting up the DeviceTypeValidatedSoftwareLCM object."""
        super().__init__(context)
        self.parent_obj = self.context["object"]
        self.valid_soft_filters = (("devicetype", self.parent_obj.pk),)

    def right_page(self):
        """Display table on right side of page."""
        extra_context = {
            "validsoft_table": self.validated_soft_table,
        }

        return self.render(
            "nautobot_device_lifecycle_mgmt/inc/validatedsoftware_info.html",
            extra_context=extra_context,
        )


template_extensions = [
    DeviceTypeHWLCM,
    DeviceHWLCM,
    InventoryItemHWLCM,
    DeviceSoftwareLCMAndValidatedSoftwareLCM,
    InventoryItemSoftwareLCMAndValidatedSoftwareLCM,
    DeviceTypeValidatedSoftwareLCM,
]

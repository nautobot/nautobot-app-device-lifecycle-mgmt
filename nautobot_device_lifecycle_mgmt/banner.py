"""Banners for the Device Lifecycle Management app."""

from django.urls import NoReverseMatch, Resolver404, resolve, reverse
from django.utils.html import format_html
from nautobot.apps.ui import Banner, BannerClassChoices
from nautobot.extras.models import Job

from nautobot_device_lifecycle_mgmt import models


def all_models_migrated_to_core():
    """Check if all DLM models have been migrated to core models."""
    models_to_check = [
        models.SoftwareLCM,
        models.SoftwareImageLCM,
        models.ContactLCM,
    ]
    for model in models_to_check:
        if model.objects.filter(migrated_to_core_model_flag=False).exists():
            return False
    return True


def models_migrated_to_core_banner(context):
    """Emit a banner on DLM views if models are not migrated to core."""
    try:
        app_name = resolve(context.request.path).app_name
    except (AttributeError, NoReverseMatch, Resolver404):
        return None
    if app_name != "plugins:nautobot_device_lifecycle_mgmt":
        return None
    if all_models_migrated_to_core():
        return None

    migration_job = Job.objects.filter(
        module_name="nautobot_device_lifecycle_mgmt.jobs.model_migration",
        job_class_name="DLMToNautobotCoreModelMigration",
    ).first()
    content = """Some Device Lifecycle Management models have not been migrated to Nautobot core models. Please run the migration job at <a href="{}">{}</a>."""

    return Banner(
        content=format_html(content, reverse("extras:job_run", kwargs={"pk": migration_job.pk}), str(migration_job)),
        banner_class=BannerClassChoices.CLASS_WARNING,
    )

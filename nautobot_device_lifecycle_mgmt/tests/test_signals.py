"""Test the objects created by the app's signals."""

from django.apps import apps
from nautobot.apps.choices import SecretsGroupAccessTypeChoices, SecretsGroupSecretTypeChoices
from nautobot.apps.testing import TestCase
from nautobot.extras.models import Secret, SecretsGroup, SecretsGroupAssociation

from nautobot_device_lifecycle_mgmt.signals import create_nist_objects


class CreateNistObjectsTestCase(TestCase):
    """Test the NIST secrets group association created by `create_nist_objects`."""

    def setUp(self):
        self.app_config = apps.get_app_config("nautobot_device_lifecycle_mgmt")
        self.nist_secrets_group = SecretsGroup.objects.get(name="NAUTOBOT DLM NIST SECRETS GROUP")
        self.nist_association = SecretsGroupAssociation.objects.filter(
            secrets_group=self.nist_secrets_group, secret__name="NAUTOBOT DLM NIST API KEY"
        )

    def _assert_nist_association_is_valid(self):
        association = self.nist_association.get()
        association.full_clean()
        self.assertEqual(association.access_type, SecretsGroupAccessTypeChoices.TYPE_HTTP)
        self.assertEqual(association.secret_type, SecretsGroupSecretTypeChoices.TYPE_TOKEN)

    def test_nist_association_uses_valid_choices(self):
        create_nist_objects(sender=self.app_config)
        self._assert_nist_association_is_valid()

    def test_invalid_nist_association_is_corrected(self):
        self.nist_association.update(access_type="HTTP_HEADER", secret_type="apiKey")
        create_nist_objects(sender=self.app_config)
        self._assert_nist_association_is_valid()

    def test_invalid_nist_association_is_kept_when_valid_values_are_taken(self):
        self.nist_association.update(access_type="HTTP_HEADER", secret_type="apiKey")
        other_secret = Secret(name="Other API Token", provider="environment-variable", parameters={"variable": "X"})
        other_secret.validated_save()
        self.nist_secrets_group.secrets.add(
            other_secret,
            through_defaults={
                "access_type": SecretsGroupAccessTypeChoices.TYPE_HTTP,
                "secret_type": SecretsGroupSecretTypeChoices.TYPE_TOKEN,
            },
        )
        create_nist_objects(sender=self.app_config)
        self.assertEqual(self.nist_association.get().access_type, "HTTP_HEADER")

"""Test Jobs."""

import unittest
from datetime import date
from unittest import mock

from django.contrib.contenttypes.models import ContentType
from nautobot.apps.choices import JobResultStatusChoices
from nautobot.apps.testing import TransactionTestCase, create_job_result_and_run_job
from nautobot.dcim.models import Platform, SoftwareVersion
from nautobot.extras.models import Status
from requests.exceptions import ChunkedEncodingError, Timeout

from nautobot_device_lifecycle_mgmt.jobs.cve_tracking import NistCveSyncSoftware
from nautobot_device_lifecycle_mgmt.models import (
    DeviceHardwareNoticeResult,
    DeviceSoftwareValidationResult,
    ValidatedSoftwareLCM,
)
from nautobot_device_lifecycle_mgmt.tests import conftest


class DeviceHardwareNoticeFullReportTestCase(TransactionTestCase):
    """Test DeviceHardwareNoticeFullReport class."""

    databases = ("default", "job_logs")

    def setUp(self):  # pylint: disable=invalid-name
        """Initialize test case."""
        # Create Nautobot Objects
        self.devices = conftest.create_devices()
        self.hardware_notices = conftest.create_device_type_hardware_notices()

        # Update devices with device types matching those used by the hardware notcies
        self.devices[0].device_type = self.hardware_notices[0].device_type
        self.devices[0].save()
        self.devices[1].device_type = self.hardware_notices[1].device_type
        self.devices[1].save()
        self.devices[2].device_type = self.hardware_notices[2].device_type
        self.devices[2].save()

    def test_hardware_notice_reporting_data_generation(self):
        """Test successfully generating device hardware notice reporting data."""
        job_result = create_job_result_and_run_job(
            module="nautobot_device_lifecycle_mgmt.jobs.lifecycle_reporting", name="DeviceHardwareNoticeFullReport"
        )
        self.assertEqual(DeviceHardwareNoticeResult.objects.all().count(), 3)
        for index, obj in enumerate(DeviceHardwareNoticeResult.objects.all()):
            self.assertEqual(obj.device, self.devices[index])
            self.assertEqual(obj.hardware_notice, self.hardware_notices[index])
        self.assertEqual(job_result.status, JobResultStatusChoices.STATUS_SUCCESS)


class DeviceSoftwareValidationFullReportTestCase(TransactionTestCase):
    """Test DeviceSoftwareValidationFullReport class."""

    databases = ("default", "job_logs")

    def setUp(self):
        """Initialize test case."""
        active_status, _ = Status.objects.get_or_create(name="Active")
        active_status.content_types.add(ContentType.objects.get_for_model(SoftwareVersion))

        self.devices = conftest.create_devices()
        device_platform, _ = Platform.objects.get_or_create(name="cisco_ios")

        self.software_valid = SoftwareVersion.objects.create(
            platform=device_platform, version="15.2(1)T", status=active_status
        )
        self.software_no_vs = SoftwareVersion.objects.create(
            platform=device_platform, version="12.0(1)T", status=active_status
        )

        # devices[0]: software with a matching ValidatedSoftwareLCM → is_validated=True
        self.devices[0].software_version = self.software_valid
        self.devices[0].save()

        # devices[1]: software but no ValidatedSoftwareLCM for it → is_validated=False
        self.devices[1].software_version = self.software_no_vs
        self.devices[1].save()

        # devices[2]: no software_version → is_validated=False, software=None

        validated_software = ValidatedSoftwareLCM.objects.create(
            software=self.software_valid,
            start=date(2020, 1, 1),
        )
        validated_software.device_types.set([self.devices[0].device_type])

    def test_device_software_validation_report(self):
        """Test that all devices get a result with correct is_validated and software fields."""
        job_result = create_job_result_and_run_job(
            module="nautobot_device_lifecycle_mgmt.jobs.lifecycle_reporting",
            name="DeviceSoftwareValidationFullReport",
        )
        self.assertEqual(job_result.status, JobResultStatusChoices.STATUS_SUCCESS)
        self.assertEqual(DeviceSoftwareValidationResult.objects.count(), len(self.devices))

        result_valid = DeviceSoftwareValidationResult.objects.get(device=self.devices[0])
        self.assertTrue(result_valid.is_validated)
        self.assertEqual(result_valid.software, self.software_valid)

        result_wrong_sw = DeviceSoftwareValidationResult.objects.get(device=self.devices[1])
        self.assertFalse(result_wrong_sw.is_validated)
        self.assertEqual(result_wrong_sw.software, self.software_no_vs)

        result_no_sw = DeviceSoftwareValidationResult.objects.get(device=self.devices[2])
        self.assertFalse(result_no_sw.is_validated)
        self.assertIsNone(result_no_sw.software)


class NistCveSyncSoftwareQueryApiTestCase(unittest.TestCase):
    """Test NistCveSyncSoftware.query_api retry/session-rebuild behavior."""

    def _build_job(self, max_attempts=3):
        """Construct a NistCveSyncSoftware instance with stubbed integration/logger.

        Bypasses Job.__init__ since we only exercise query_api in isolation.
        """
        job = NistCveSyncSoftware.__new__(NistCveSyncSoftware)
        job.logger = mock.MagicMock()
        job.integration = mock.MagicMock()
        job.integration.extra_config = {"retries": {"max_attempts": max_attempts, "backoff": 0}}
        return job

    def test_query_api_rebuilds_session_on_chunked_encoding_error(self):
        """A ChunkedEncodingError mid-stream rebuilds the session and returns the next response."""
        failing_session = mock.MagicMock()
        failing_session.get.side_effect = ChunkedEncodingError("Stream 35 was reset by remote peer. Reason: 0x2.")

        success_response = mock.MagicMock()
        success_response.json.return_value = {"vulnerabilities": [], "totalResults": 0}
        rebuilt_session = mock.MagicMock()
        rebuilt_session.get.return_value = success_response

        job = self._build_job()
        job.nist_session = failing_session
        job.nist_session_init = mock.MagicMock(return_value=rebuilt_session)

        with mock.patch("nautobot_device_lifecycle_mgmt.jobs.cve_tracking.sleep"):
            result = job.query_api("https://example.com/")

        self.assertEqual(result, {"vulnerabilities": [], "totalResults": 0})
        failing_session.close.assert_called_once()
        job.nist_session_init.assert_called_once()
        rebuilt_session.get.assert_called_once_with("https://example.com/")

    def test_query_api_raises_after_exhausting_attempts(self):
        """When every attempt resets, the original error propagates after max_attempts."""
        err = ChunkedEncodingError("Stream 35 was reset by remote peer. Reason: 0x2.")
        failing_session = mock.MagicMock()
        failing_session.get.side_effect = err
        rebuilt_session = mock.MagicMock()
        rebuilt_session.get.side_effect = err

        job = self._build_job(max_attempts=2)
        job.nist_session = failing_session
        job.nist_session_init = mock.MagicMock(return_value=rebuilt_session)

        with mock.patch("nautobot_device_lifecycle_mgmt.jobs.cve_tracking.sleep"):
            with self.assertRaises(ChunkedEncodingError):
                job.query_api("https://example.com/")

        # session rebuilt once between the two attempts; not rebuilt after the final failure
        self.assertEqual(job.nist_session_init.call_count, 1)

    def test_query_api_rebuilds_session_on_timeout(self):
        """A Timeout also triggers session rebuild and retry."""
        failing_session = mock.MagicMock()
        failing_session.get.side_effect = Timeout("Read timed out.")

        success_response = mock.MagicMock()
        success_response.json.return_value = {"vulnerabilities": [], "totalResults": 0}
        rebuilt_session = mock.MagicMock()
        rebuilt_session.get.return_value = success_response

        job = self._build_job()
        job.nist_session = failing_session
        job.nist_session_init = mock.MagicMock(return_value=rebuilt_session)

        with mock.patch("nautobot_device_lifecycle_mgmt.jobs.cve_tracking.sleep"):
            result = job.query_api("https://example.com/")

        self.assertEqual(result, {"vulnerabilities": [], "totalResults": 0})
        failing_session.close.assert_called_once()
        job.nist_session_init.assert_called_once()

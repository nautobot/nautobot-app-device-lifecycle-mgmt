"""Test Jobs."""

import json
import unittest
from datetime import date
from unittest import mock

from django.contrib.contenttypes.models import ContentType
from nautobot.apps.choices import JobResultStatusChoices
from nautobot.apps.testing import TransactionTestCase, create_job_result_and_run_job
from nautobot.dcim.models import Platform, SoftwareVersion
from nautobot.extras.models import Status
from requests.exceptions import ChunkedEncodingError, HTTPError, MissingSchema, RequestException, Timeout

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


class NistCveSyncSoftwareGetSoftwareVersionsTestCase(TransactionTestCase):
    """Test NistCveSyncSoftware.get_software_versions filtering behavior."""

    databases = ("default", "job_logs")

    def setUp(self):
        """Create a set of Software Versions to filter against."""
        active_status, _ = Status.objects.get_or_create(name="Active")
        active_status.content_types.add(ContentType.objects.get_for_model(SoftwareVersion))
        device_platform, _ = Platform.objects.get_or_create(name="cisco_ios")

        self.software_a = SoftwareVersion.objects.create(
            platform=device_platform, version="15.2(1)T", status=active_status
        )
        self.software_b = SoftwareVersion.objects.create(
            platform=device_platform, version="12.0(1)T", status=active_status
        )
        self.software_c = SoftwareVersion.objects.create(
            platform=device_platform, version="17.3(1)", status=active_status
        )

    def test_none_returns_all_software_versions(self):
        """When no Software Versions are selected, all are returned."""
        result = NistCveSyncSoftware.get_software_versions(None)
        self.assertIn(self.software_a, result)
        self.assertIn(self.software_b, result)
        self.assertIn(self.software_c, result)
        self.assertEqual(result.count(), SoftwareVersion.objects.count())

    def test_empty_returns_all_software_versions(self):
        """An empty selection falls back to all Software Versions."""
        result = NistCveSyncSoftware.get_software_versions([])
        self.assertIn(self.software_a, result)
        self.assertIn(self.software_b, result)
        self.assertIn(self.software_c, result)
        self.assertEqual(result.count(), SoftwareVersion.objects.count())

    def test_subset_returns_only_selected_software_versions(self):
        """A selection restricts the queryset to just those Software Versions."""
        result = NistCveSyncSoftware.get_software_versions([self.software_a, self.software_c])
        self.assertEqual(set(result), {self.software_a, self.software_c})


class NistCveSyncSoftwareRunTestCase(unittest.TestCase):
    """Test NistCveSyncSoftware.run software-version selection wiring."""

    def _build_job(self):
        """Construct a NistCveSyncSoftware instance with a stubbed logger.

        Bypasses Job.__init__ since we only exercise run() in isolation.
        """
        job = NistCveSyncSoftware.__new__(NistCveSyncSoftware)
        job.logger = mock.MagicMock()
        job.nist_api_key = None
        job.nist_session = None
        return job

    def test_run_passes_selected_software_versions_to_get_software_versions(self):
        """run() forwards the selected software_versions to get_software_versions and iterates the result."""
        integration = mock.MagicMock()
        selected = [mock.MagicMock(), mock.MagicMock()]

        # get_software_versions has its own dedicated tests; stub it here to isolate the
        # run() wiring that builds software_qs and loops over it (an empty queryset exercises
        # the "no software" path without needing to mock the NIST HTTP calls in the loop body).
        software_qs = mock.MagicMock()
        software_qs.__len__.return_value = 0
        software_qs.__iter__.return_value = iter([])

        job = self._build_job()
        job.nist_session_init = mock.MagicMock(return_value=mock.MagicMock())
        job.get_software_versions = mock.MagicMock(return_value=software_qs)

        with mock.patch("nautobot_device_lifecycle_mgmt.jobs.cve_tracking.sleep"):
            job.run(nist_integration=integration, software_versions=selected)

        job.get_software_versions.assert_called_once_with(selected)
        software_qs.__len__.assert_called_once()
        job.nist_session.close.assert_called_once()


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

    def test_query_api_does_not_retry_on_http_error(self):
        """An HTTPError (4xx/5xx) is logged and raised immediately without retrying or rebuilding the session."""
        response = mock.MagicMock()
        http_err = HTTPError("404 Client Error")
        http_err.response = mock.MagicMock(status_code=404)
        response.raise_for_status.side_effect = http_err
        session = mock.MagicMock()
        session.get.return_value = response

        job = self._build_job()
        job.nist_session = session
        job.nist_session_init = mock.MagicMock()

        with mock.patch("nautobot_device_lifecycle_mgmt.jobs.cve_tracking.sleep"):
            with self.assertRaises(HTTPError):
                job.query_api("https://example.com/")

        # No retry: the request is made exactly once and the session is neither closed nor rebuilt.
        session.get.assert_called_once()
        session.close.assert_not_called()
        job.nist_session_init.assert_not_called()

    def test_query_api_does_not_retry_on_non_transient_request_error(self):
        """A malformed-request error (e.g. MissingSchema) fails fast without retrying or rebuilding the session."""
        failing_session = mock.MagicMock()
        failing_session.get.side_effect = MissingSchema("Invalid URL 'example.com': No scheme supplied.")

        job = self._build_job()
        job.nist_session = failing_session
        job.nist_session_init = mock.MagicMock()

        with mock.patch("nautobot_device_lifecycle_mgmt.jobs.cve_tracking.sleep"):
            with self.assertRaises(MissingSchema):
                job.query_api("example.com/")

        # No retry: request made exactly once, session neither closed nor rebuilt.
        failing_session.get.assert_called_once()
        failing_session.close.assert_not_called()
        job.nist_session_init.assert_not_called()

    def test_query_api_rebuilds_session_on_generic_request_exception(self):
        """Any RequestException (not just the enumerated transport errors) triggers the retry path."""
        failing_session = mock.MagicMock()
        failing_session.get.side_effect = RequestException("Some other requests failure.")

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

    def test_query_api_does_not_retry_on_json_decode_error(self):
        """A malformed JSON body is logged and raised immediately without retrying or rebuilding the session."""
        response = mock.MagicMock()
        response.json.side_effect = json.JSONDecodeError("Expecting value", "not json", 0)
        session = mock.MagicMock()
        session.get.return_value = response

        job = self._build_job()
        job.nist_session = session
        job.nist_session_init = mock.MagicMock()

        with mock.patch("nautobot_device_lifecycle_mgmt.jobs.cve_tracking.sleep"):
            with self.assertRaises(json.JSONDecodeError):
                job.query_api("https://example.com/")

        # No retry: the request is made exactly once and the session is neither closed nor rebuilt.
        session.get.assert_called_once()
        session.close.assert_not_called()
        job.nist_session_init.assert_not_called()

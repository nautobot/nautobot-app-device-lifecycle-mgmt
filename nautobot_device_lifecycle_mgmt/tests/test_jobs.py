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

from nautobot_device_lifecycle_mgmt.choices import CVESeverityChoices
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


def _cvss_metric(score, severity=None, severity_in_cvss_data=True, vector=None):
    """Build a NIST CVSS metric entry list."""
    metric = {"cvssData": {"baseScore": score}}
    if vector is not None:
        metric["cvssData"]["vectorString"] = vector
    if severity is not None:
        if severity_in_cvss_data:
            metric["cvssData"]["baseSeverity"] = severity
        else:
            metric["baseSeverity"] = severity
    return [metric]


class NistCveSyncSoftwarePrepCveTestCase(unittest.TestCase):
    """Test NistCveSyncSoftware CVSS score/severity selection."""

    def setUp(self):
        """Construct a NistCveSyncSoftware instance, bypassing Job.__init__."""
        self.job = NistCveSyncSoftware.__new__(NistCveSyncSoftware)
        self.job.logger = mock.MagicMock()

    @staticmethod
    def _cve_json(metrics=None):
        """Build a minimal NIST CVE record."""
        cve = {
            "id": "CVE-2024-0001",
            "descriptions": [{"lang": "en", "value": "Test CVE"}],
            "published": "2024-01-01T00:00:00.000",
            "lastModified": "2024-02-01T00:00:00.000",
            "references": [{"url": "https://example.com/CVE-2024-0001"}],
        }
        if metrics is not None:
            cve["metrics"] = metrics
        return cve

    def test_prefers_v40_over_lower_versions(self):
        """CVSS v4.0 is used when present alongside v3.1 and v2."""
        result = self.job.prep_cve_for_dlc(
            self._cve_json(
                {
                    "cvssMetricV40": _cvss_metric(
                        9.3, "CRITICAL", vector="CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N"
                    ),
                    "cvssMetricV31": _cvss_metric(7.5, "HIGH", vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"),
                    "cvssMetricV2": _cvss_metric(
                        5.0, "MEDIUM", severity_in_cvss_data=False, vector="AV:N/AC:L/Au:N/C:P/I:P/A:P"
                    ),
                }
            )
        )
        self.assertEqual(result["cvss_base_score"], 9.3)
        self.assertEqual(result["cvss_severity"], CVESeverityChoices.CRITICAL)
        self.assertEqual(result["cvss_vector"], "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N")
        self.assertNotIn("cvssv2_score", result)
        self.assertNotIn("cvssv3_score", result)

    def test_prefers_v31_over_v2(self):
        """CVSS v3.1 is used when v4.0 is absent."""
        result = self.job.prep_cve_for_dlc(
            self._cve_json(
                {
                    "cvssMetricV31": _cvss_metric(7.5, "HIGH"),
                    "cvssMetricV2": _cvss_metric(5.0, "MEDIUM", severity_in_cvss_data=False),
                }
            )
        )
        self.assertEqual(result["cvss_base_score"], 7.5)
        self.assertEqual(result["cvss_severity"], CVESeverityChoices.HIGH)

    def test_uses_v30_when_only_version(self):
        """CVSS v3.0 is used when it is the only version available."""
        result = self.job.prep_cve_for_dlc(self._cve_json({"cvssMetricV30": _cvss_metric(4.3, "MEDIUM")}))
        self.assertEqual(result["cvss_base_score"], 4.3)
        self.assertEqual(result["cvss_severity"], CVESeverityChoices.MEDIUM)

    def test_non_v2_severity_uses_standardize(self):
        """Severity for v3+ comes from standardize_cvss_severity, not the v2 score conversion."""
        with mock.patch.object(NistCveSyncSoftware, "convert_v2_base_score_to_severity") as mock_convert:
            result = self.job.prep_cve_for_dlc(self._cve_json({"cvssMetricV31": _cvss_metric(9.8, "CRITICAL")}))
        mock_convert.assert_not_called()
        self.assertEqual(result["cvss_severity"], CVESeverityChoices.CRITICAL)

    def test_v2_severity_derived_from_score(self):
        """Severity for v2 always comes from the base score, ignoring NIST's baseSeverity."""
        with mock.patch("nautobot_device_lifecycle_mgmt.jobs.cve_tracking.standardize_cvss_severity") as mock_std:
            result = self.job.prep_cve_for_dlc(
                self._cve_json(
                    {
                        "cvssMetricV2": _cvss_metric(
                            9.8, "CRITICAL", severity_in_cvss_data=False, vector="AV:N/AC:L/Au:N/C:P/I:P/A:P"
                        )
                    }
                )
            )
        mock_std.assert_not_called()
        self.assertEqual(result["cvss_base_score"], 9.8)
        self.assertEqual(result["cvss_severity"], CVESeverityChoices.HIGH)
        self.assertEqual(result["cvss_vector"], "AV:N/AC:L/Au:N/C:P/I:P/A:P")

    def test_v2_without_severity(self):
        """A v2 metric with no baseSeverity still gets a severity from its score."""
        result = self.job.prep_cve_for_dlc(self._cve_json({"cvssMetricV2": _cvss_metric(2.1)}))
        self.assertEqual(result["cvss_base_score"], 2.1)
        self.assertEqual(result["cvss_severity"], CVESeverityChoices.LOW)

    def test_no_metrics(self):
        """A CVE without CVSS metrics has no score and a severity of None."""
        for metrics in (None, {}):
            with self.subTest(metrics=metrics):
                result = self.job.prep_cve_for_dlc(self._cve_json(metrics))
                self.assertIsNone(result["cvss_base_score"])
                self.assertEqual(result["cvss_severity"], CVESeverityChoices.NONE)
                self.assertEqual(result["cvss_vector"], "")

    def test_missing_vector_string(self):
        """A metric without a vectorString results in an empty vector."""
        result = self.job.prep_cve_for_dlc(self._cve_json({"cvssMetricV31": _cvss_metric(7.5, "HIGH")}))
        self.assertEqual(result["cvss_vector"], "")

    def test_update_cve_leaves_legacy_scores_untouched(self):
        """update_cve sets cvss/severity and does not modify cvss_v2/cvss_v3."""
        current_cve = mock.MagicMock(cvss=1.0, cvss_v2=3.3, cvss_v3=4.4, comments="")
        updated_cve = self.job.prep_cve_for_dlc(
            self._cve_json(
                {"cvssMetricV31": _cvss_metric(9.8, "CRITICAL", vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H")}
            )
        )

        self.job.update_cve(current_cve, updated_cve)

        self.assertEqual(current_cve.cvss, 9.8)
        self.assertEqual(current_cve.severity, CVESeverityChoices.CRITICAL)
        self.assertEqual(current_cve.cvss_vector, "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H")
        self.assertEqual(current_cve.cvss_v2, 3.3)
        self.assertEqual(current_cve.cvss_v3, 4.4)
        current_cve.validated_save.assert_called_once()

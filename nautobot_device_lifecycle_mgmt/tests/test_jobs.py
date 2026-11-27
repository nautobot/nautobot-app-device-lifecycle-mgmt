"""Test Jobs."""

import unittest
from datetime import date
from unittest import mock

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from nautobot.apps.choices import JobResultStatusChoices
from nautobot.apps.testing import TestCase, TransactionTestCase, create_job_result_and_run_job
from nautobot.dcim.models import Platform, SoftwareVersion
from nautobot.extras.models import Status
from nautobot.tenancy.models import Tenant
from requests.exceptions import ChunkedEncodingError, Timeout

from nautobot_device_lifecycle_mgmt.choices import CVESeverityChoices
from nautobot_device_lifecycle_mgmt.jobs.cve_tracking import UNNAMED_CVSS_SOURCE, NistCveSyncSoftware
from nautobot_device_lifecycle_mgmt.models import (
    CVELCM,
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

    def test_unfiltered_run_is_recorded_as_full_run(self):
        """A run without platform or tenant filters records every result as a full report run."""
        create_job_result_and_run_job(
            module="nautobot_device_lifecycle_mgmt.jobs.lifecycle_reporting",
            name="DeviceSoftwareValidationFullReport",
        )

        self.assertEqual(
            set(DeviceSoftwareValidationResult.objects.values_list("run_type", flat=True)),
            {ReportRunTypeChoices.REPORT_FULL_RUN},
        )

    def test_filtered_run_validates_only_matching_devices(self):
        """Platform and tenant filters limit which devices are validated and mark the run as filtered."""
        tenant = Tenant.objects.create(name="Tenant A")
        self.devices[0].tenant = tenant
        self.devices[0].save()
        platform = self.devices[0].platform

        job_result = create_job_result_and_run_job(
            "nautobot_device_lifecycle_mgmt.jobs.lifecycle_reporting",
            "DeviceSoftwareValidationFullReport",
            platforms=[str(platform.pk)],
            tenants=[str(tenant.pk)],
        )

        self.assertEqual(job_result.status, JobResultStatusChoices.STATUS_SUCCESS)
        result = DeviceSoftwareValidationResult.objects.get()
        self.assertEqual(result.device, self.devices[0])
        self.assertEqual(result.run_type, ReportRunTypeChoices.REPORT_FILTERED_RUN)


class NistCveSyncSoftwareForceUpdateTestCase(unittest.TestCase):
    """Test when NistCveSyncSoftware.run updates existing CVEs."""

    NIST_MODIFIED = "2024-02-01T00:00:00.000"

    def _run_job(self, force_cve_updates, existing_cves, new_cves=None, software_count=1):
        """Run the job against mocked software and NIST data and return the mocked update_cve.

        Args:
            force_cve_updates (bool): Value of the Force CVE Updates option.
            existing_cves (dict): CVE name to the Last Modified Date stored on the existing CVE.
            new_cves (list): Names of CVEs that NIST returns and the job creates during the run.
            software_count (int): Number of Software Versions that each return all of the CVEs.
        """
        new_cves = new_cves or []
        job = NistCveSyncSoftware.__new__(NistCveSyncSoftware)
        job.logger = mock.MagicMock()
        job.nist_session_init = mock.MagicMock()
        job.create_dlc_cves = mock.MagicMock()
        job.update_cve = mock.MagicMock()
        job.get_cve_info = mock.MagicMock(
            return_value={
                "new": {name: {"modified_date": self.NIST_MODIFIED} for name in new_cves},
                "existing": {name: {"modified_date": self.NIST_MODIFIED} for name in existing_cves},
            }
        )
        integration = mock.MagicMock(remote_url="https://nvd.example.com", extra_config={"api_call_delay": 0})

        dlc_cves = {name: mock.MagicMock(last_modified_date=modified) for name, modified in existing_cves.items()}
        dlc_cves.update({name: mock.MagicMock(last_modified_date=date(2024, 2, 1)) for name in new_cves})
        mock_cvelcm = mock.MagicMock(DoesNotExist=Exception)
        mock_cvelcm.objects.get.side_effect = lambda name: dlc_cves[name]

        module = "nautobot_device_lifecycle_mgmt.jobs.cve_tracking"
        with (
            mock.patch(f"{module}.SoftwareVersion") as mock_software,
            mock.patch(f"{module}.CVELCM", mock_cvelcm),
            mock.patch(f"{module}.get_nist_urls", return_value=["https://nvd.example.com/?cpeName=test"]),
            mock.patch(f"{module}.sleep"),
        ):
            mock_software.objects.all.return_value = [
                mock.MagicMock(**{"platform.network_driver": "cisco_ios", "version": "15.2(1)T"})
                for _ in range(software_count)
            ]
            job.run(nist_integration=integration, force_cve_updates=force_cve_updates)

        return job.update_cve

    def test_unmodified_cve_not_updated_without_force(self):
        """An existing CVE whose NIST Modified Date is unchanged is not updated by default."""
        update_cve = self._run_job(False, {"CVE-2024-0001": date(2024, 2, 1)})
        update_cve.assert_not_called()

    def test_modified_cve_updated_without_force(self):
        """An existing CVE whose NIST Modified Date changed is updated by default."""
        update_cve = self._run_job(False, {"CVE-2024-0001": date(2023, 1, 1)})
        update_cve.assert_called_once()

    def test_force_updates_unmodified_cves(self):
        """With Force CVE Updates, every existing CVE is updated even if NIST has not modified it."""
        update_cve = self._run_job(True, {"CVE-2024-0001": date(2024, 2, 1), "CVE-2024-0002": date(2024, 2, 1)})
        self.assertEqual(update_cve.call_count, 2)

    def test_force_updates_shared_cve_once(self):
        """A CVE returned for several Software Versions is only force updated once per run."""
        update_cve = self._run_job(True, {"CVE-2024-0001": date(2024, 2, 1)}, software_count=3)
        update_cve.assert_called_once()

    def test_force_skips_cves_created_in_run(self):
        """CVEs created during the run are not force updated."""
        update_cve = self._run_job(True, {}, new_cves=["CVE-2024-0003"])
        update_cve.assert_not_called()


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


def _cvss_metric(score, severity=None, severity_in_cvss_data=True, vector=None, entry_type=None):
    """Build a NIST CVSS metric entry list."""
    metric = {"cvssData": {"baseScore": score}}
    if entry_type is not None:
        metric["type"] = entry_type
    if vector is not None:
        metric["cvssData"]["vectorString"] = vector
    if severity is not None:
        if severity_in_cvss_data:
            metric["cvssData"]["baseSeverity"] = severity
        else:
            metric["baseSeverity"] = severity
    return [metric]


def _metric_vector(score):
    """Return the test vector string that identifies a metric entry by its score."""
    return f"TEST/{score}"


def _metric_entry(score, entry_type, source=None):
    """Build a one-entry NIST CVSS metric list of the given type, identified by its score."""
    metric = _cvss_metric(score, vector=_metric_vector(score), entry_type=entry_type)
    if source is not None:
        metric[0]["source"] = source
    return metric


def _nist_cve_record(metrics=None):
    """Build a minimal NIST CVE record for CVE-2024-0001."""
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


class NistCveSyncSoftwarePrepCveBase(unittest.TestCase):
    """Shared setup for tests of NistCveSyncSoftware.prep_cve_for_dlc."""

    def setUp(self):
        """Construct a NistCveSyncSoftware instance, bypassing Job.__init__."""
        self.job = NistCveSyncSoftware.__new__(NistCveSyncSoftware)
        self.job.logger = mock.MagicMock()

    @staticmethod
    def _cve_json(metrics=None):
        """Build a minimal NIST CVE record."""
        return _nist_cve_record(metrics)


class NistCveSyncSoftwarePrepCveTestCase(NistCveSyncSoftwarePrepCveBase):
    """Test NistCveSyncSoftware CVSS score/severity selection."""

    def test_cvss_score_selection(self):
        """The CVSS Base Score comes from NIST's own score for the highest version NIST scored, else another source."""
        # "Primary" is NIST's own score and "Secondary" is another source's, such as the vendor's.
        # Each case is (NIST metrics, expected base score).
        cases = {
            "Primary v4.0 over Primary v3.1 and v2": (
                {
                    "cvssMetricV40": _metric_entry(9.3, "Primary"),
                    "cvssMetricV31": _metric_entry(7.5, "Primary"),
                    "cvssMetricV2": _metric_entry(5.0, "Primary"),
                },
                9.3,
            ),
            "Primary v3.1 over Primary v2": (
                {"cvssMetricV31": _metric_entry(7.5, "Primary"), "cvssMetricV2": _metric_entry(5.0, "Primary")},
                7.5,
            ),
            "Primary v3.0 when it is the only version": (
                {"cvssMetricV30": _metric_entry(4.3, "Primary")},
                4.3,
            ),
            "Primary over a Secondary listed before it in the same version": (
                {"cvssMetricV31": _metric_entry(6.0, "Secondary") + _metric_entry(6.7, "Primary")},
                6.7,
            ),
            "Primary v3.1 over a higher Secondary-only v4.0": (
                {
                    "cvssMetricV40": _metric_entry(9.3, "Secondary"),
                    "cvssMetricV31": _metric_entry(9.8, "Secondary") + _metric_entry(7.5, "Primary"),
                },
                7.5,
            ),
            "NIST's own v2 over a higher vendor-only v3.1": (
                {
                    "cvssMetricV31": _metric_entry(9.8, "Secondary", source="psirt@cisco.com"),
                    "cvssMetricV2": _metric_entry(5.0, "Primary", source="nvd@nist.gov"),
                },
                5.0,
            ),
            "empty higher version is skipped": (
                {"cvssMetricV40": [], "cvssMetricV31": _metric_entry(7.5, "Primary")},
                7.5,
            ),
            "non-CVSS metric keys are ignored": (
                {"ssvcMetricV1": [{"other": "data"}], "cvssMetricV31": _metric_entry(7.5, "Primary")},
                7.5,
            ),
            "no Primary: first Secondary of the highest version": (
                {
                    "cvssMetricV40": _metric_entry(9.3, "Secondary") + _metric_entry(8.7, "Secondary"),
                    "cvssMetricV31": _metric_entry(7.5, "Secondary"),
                },
                9.3,
            ),
            "entries without a type are not Primary": (
                {"cvssMetricV31": _metric_entry(7.5, None), "cvssMetricV2": _metric_entry(5.0, None)},
                7.5,
            ),
            "no CVSS metrics": ({}, None),
        }
        for name, (metrics, score) in cases.items():
            with self.subTest(name):
                result = self.job.prep_cve_for_dlc(self._cve_json(metrics))
                self.assertEqual(result["cvss_base_score"], score)
                expected_vector = _metric_vector(score) if score is not None else ""
                self.assertEqual(result["cvss_vector"], expected_vector)

    def test_cvss_source_when_nist_has_not_scored(self):
        """When no entry is NIST's own, the result names the source of the score used and nothing is logged yet."""
        # Each case is (NIST metrics, expected cvss_source).
        cases = {
            "source of the first Secondary in the highest version": (
                {
                    "cvssMetricV40": _metric_entry(9.3, "Secondary", source="psirt@cisco.com")
                    + _metric_entry(8.7, "Secondary", source="other@example.com"),
                    "cvssMetricV31": _metric_entry(7.5, "Secondary", source="v31@example.com"),
                },
                "psirt@cisco.com",
            ),
            "placeholder when the entry has no source": (
                {"cvssMetricV2": _metric_entry(5.0, "Secondary")},
                UNNAMED_CVSS_SOURCE,
            ),
            "placeholder when the entry's source is null": (
                {"cvssMetricV31": [{"type": "Secondary", "source": None, "cvssData": {"baseScore": 7.5}}]},
                UNNAMED_CVSS_SOURCE,
            ),
            "placeholder when the entry's source is empty": (
                {"cvssMetricV31": [{"type": "Secondary", "source": "", "cvssData": {"baseScore": 7.5}}]},
                UNNAMED_CVSS_SOURCE,
            ),
            "entries without a type are not NIST's own": (
                {"cvssMetricV31": _metric_entry(7.5, None), "cvssMetricV2": _metric_entry(5.0, None)},
                UNNAMED_CVSS_SOURCE,
            ),
        }
        for name, (metrics, source) in cases.items():
            with self.subTest(name):
                self.job.logger.reset_mock()
                result = self.job.prep_cve_for_dlc(self._cve_json(metrics))
                self.assertEqual(result["cvss_source"], source)
                self.job.logger.info.assert_not_called()

    def test_no_cvss_source_when_nist_scored(self):
        """The source is None when NIST's own score is used or the CVE has no CVSS metrics."""
        cases = {
            "NIST's own v2 over a higher vendor-only v3.1": {
                "cvssMetricV31": _metric_entry(9.8, "Secondary", source="psirt@cisco.com"),
                "cvssMetricV2": _metric_entry(5.0, "Primary", source="nvd@nist.gov"),
            },
            "Primary listed after a Secondary in the same version": {
                "cvssMetricV31": _metric_entry(6.0, "Secondary") + _metric_entry(6.7, "Primary"),
            },
            "no CVSS metrics": {},
            "only non-CVSS metrics": {"ssvcMetricV1": [{"other": "data"}]},
        }
        for name, metrics in cases.items():
            with self.subTest(name):
                result = self.job.prep_cve_for_dlc(self._cve_json(metrics))
                self.assertIsNone(result["cvss_source"])

    def test_secondary_score_without_base_score_keeps_source(self):
        """A non-NIST entry without a baseScore keeps its source and is flagged as missing a base score."""
        metric = [{"type": "Secondary", "source": "psirt@cisco.com", "cvssData": {"baseSeverity": "HIGH"}}]
        result = self.job.prep_cve_for_dlc(self._cve_json({"cvssMetricV31": metric}))
        self.assertIsNone(result["cvss_base_score"])
        self.assertEqual(result["cvss_source"], "psirt@cisco.com")
        self.assertTrue(result["cvss_base_score_missing"])

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

    def test_missing_base_score(self):
        """A CVSS metric without a baseScore results in no score and is flagged, without logging yet."""
        cases = (
            ("cvssMetricV31", {"baseSeverity": "HIGH"}, CVESeverityChoices.HIGH),
            ("cvssMetricV2", {}, CVESeverityChoices.NONE),
        )
        for metric_key, cvss_data, expected_severity in cases:
            with self.subTest(metric_key=metric_key):
                self.job.logger.reset_mock()
                result = self.job.prep_cve_for_dlc(self._cve_json({metric_key: [{"cvssData": cvss_data}]}))
                self.assertIsNone(result["cvss_base_score"])
                self.assertEqual(result["cvss_severity"], expected_severity)
                self.assertTrue(result["cvss_base_score_missing"])
                self.job.logger.warning.assert_not_called()

    def test_base_score_not_missing(self):
        """A CVE with a base score, or without CVSS metrics, is not flagged as missing a base score."""
        cases = {
            "has a base score": {"cvssMetricV31": _cvss_metric(7.5, "HIGH")},
            "no CVSS metrics": {},
            "only non-CVSS metrics": {"ssvcMetricV1": [{"other": "data"}]},
        }
        for name, metrics in cases.items():
            with self.subTest(name):
                result = self.job.prep_cve_for_dlc(self._cve_json(metrics))
                self.assertFalse(result["cvss_base_score_missing"])

    def test_missing_vector_string(self):
        """A metric without a vectorString results in an empty vector."""
        result = self.job.prep_cve_for_dlc(self._cve_json({"cvssMetricV31": _cvss_metric(7.5, "HIGH")}))
        self.assertEqual(result["cvss_vector"], "")


class NistCveSyncSoftwareScoresTestCase(NistCveSyncSoftwarePrepCveBase):
    """Test the CVSS scores NistCveSyncSoftware sets on a CVE, including the deprecated cvss_v2/cvss_v3 scores."""

    def test_legacy_scores_use_exploitability_scores(self):
        """cvss_v2/cvss_v3 values come from the v2 and v3.1 exploitability scores, ignoring v4.0."""
        v31_metric = _cvss_metric(7.5, "HIGH")
        v31_metric[0]["exploitabilityScore"] = 3.9
        v2_metric = _cvss_metric(5.0)
        v2_metric[0]["exploitabilityScore"] = 8.6
        result = self.job.prep_cve_for_dlc(
            self._cve_json(
                {"cvssMetricV40": _cvss_metric(9.3, "CRITICAL"), "cvssMetricV31": v31_metric, "cvssMetricV2": v2_metric}
            )
        )
        self.assertEqual(result["cvssv2_score"], 8.6)
        self.assertEqual(result["cvssv3_score"], 3.9)

    def test_legacy_scores_prefer_v31_over_v30(self):
        """The v3.1 exploitability score is used over v3.0 for cvss_v3."""
        v31_metric = _cvss_metric(7.5, "HIGH")
        v31_metric[0]["exploitabilityScore"] = 3.9
        v30_metric = _cvss_metric(7.0, "HIGH")
        v30_metric[0]["exploitabilityScore"] = 2.8
        result = self.job.prep_cve_for_dlc(self._cve_json({"cvssMetricV31": v31_metric, "cvssMetricV30": v30_metric}))
        self.assertEqual(result["cvssv3_score"], 3.9)

    def test_legacy_scores_prefer_nist_entry(self):
        """cvss_v3 uses NIST's own exploitability score over a vendor entry listed before it."""
        vendor = _cvss_metric(6.0, "MEDIUM", entry_type="Secondary")
        vendor[0]["exploitabilityScore"] = 0.8
        nist = _cvss_metric(6.7, "MEDIUM", entry_type="Primary")
        nist[0]["exploitabilityScore"] = 0.9
        result = self.job.prep_cve_for_dlc(self._cve_json({"cvssMetricV31": vendor + nist}))
        self.assertEqual(result["cvssv3_score"], 0.9)

    def test_legacy_scores_defaults(self):
        """A missing exploitability score or a missing v2/v3.x metric results in None."""
        cases = (
            {"cvssMetricV31": _cvss_metric(7.5, "HIGH"), "cvssMetricV2": _cvss_metric(5.0)},
            {"cvssMetricV2": _cvss_metric(5.0)},
            {"cvssMetricV40": _cvss_metric(9.3, "CRITICAL")},
        )
        for metrics in cases:
            with self.subTest(metrics=list(metrics)):
                result = self.job.prep_cve_for_dlc(self._cve_json(metrics))
                self.assertIsNone(result["cvssv2_score"])
                self.assertIsNone(result["cvssv3_score"])

    def test_legacy_scores_no_metrics(self):
        """A CVE without CVSS metrics has no cvss_v2/cvss_v3 values."""
        for metrics in (None, {}):
            with self.subTest(metrics=metrics):
                result = self.job.prep_cve_for_dlc(self._cve_json(metrics))
                self.assertIsNone(result["cvssv2_score"])
                self.assertIsNone(result["cvssv3_score"])

    def test_update_cve_sets_scores(self):
        """update_cve sets cvss, severity, vector and the legacy cvss_v2/cvss_v3 scores."""
        current_cve = mock.MagicMock(cvss=1.0, cvss_v2=3.3, cvss_v3=4.4, comments="")
        v31_metric = _cvss_metric(9.8, "CRITICAL", vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H")
        v31_metric[0]["exploitabilityScore"] = 3.9
        updated_cve = self.job.prep_cve_for_dlc(self._cve_json({"cvssMetricV31": v31_metric}))

        self.job.update_cve(current_cve, updated_cve)

        self.assertEqual(current_cve.cvss, 9.8)
        self.assertEqual(current_cve.severity, CVESeverityChoices.CRITICAL)
        self.assertEqual(current_cve.cvss_vector, "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H")
        self.assertIsNone(current_cve.cvss_v2)
        self.assertEqual(current_cve.cvss_v3, 3.9)
        current_cve.validated_save.assert_called_once()


class NistCveSyncSoftwareCvssScoreLogTestCase(NistCveSyncSoftwarePrepCveBase):
    """Test that NistCveSyncSoftware logs CVSS score details only when a CVE is created or updated."""

    SOURCE_MESSAGE = "CVSS score provided by %s for %s"
    MISSING_SCORE_MESSAGE = "NIST did not provide a CVSS base score for %s; the CVSS Base Score is empty."

    def _dlc_cve(self):
        dlc_cve = mock.MagicMock(comments="")
        dlc_cve.name = "CVE-2024-0001"
        return dlc_cve

    def _score_log_calls(self):
        info_calls = [call for call in self.job.logger.info.call_args_list if call.args[0] == self.SOURCE_MESSAGE]
        warning_calls = [
            call for call in self.job.logger.warning.call_args_list if call.args[0] == self.MISSING_SCORE_MESSAGE
        ]
        return info_calls + warning_calls

    def _assert_logged(self, dlc_cve, grouping):
        """Assert the source message and the missing base score warning were logged for the CVE."""
        extra = {"object": dlc_cve, "grouping": grouping}
        self.job.logger.info.assert_any_call(self.SOURCE_MESSAGE, "psirt@cisco.com", dlc_cve.name, extra=extra)
        self.job.logger.warning.assert_any_call(self.MISSING_SCORE_MESSAGE, dlc_cve.name, extra=extra)

    def _vendor_cve_info(self):
        """Return CVE information for a vendor-only score without a base score, which triggers both logs."""
        metric = [{"type": "Secondary", "source": "psirt@cisco.com", "cvssData": {"baseSeverity": "HIGH"}}]
        return self.job.prep_cve_for_dlc(self._cve_json({"cvssMetricV31": metric}))

    def test_create_logs_for_new_cve(self):
        """Creating a CVE logs the score's source and the missing base score warning."""
        dlc_cve = self._dlc_cve()
        with mock.patch.object(CVELCM.objects, "get_or_create", return_value=(dlc_cve, True)):
            self.job.create_dlc_cves({"CVE-2024-0001": self._vendor_cve_info()}, mock.MagicMock())
        self._assert_logged(dlc_cve, "CVE Creation")

    def test_create_does_not_log_for_existing_cve(self):
        """Nothing is logged when get_or_create finds an existing CVE."""
        with mock.patch.object(CVELCM.objects, "get_or_create", return_value=(self._dlc_cve(), False)):
            self.job.create_dlc_cves({"CVE-2024-0001": self._vendor_cve_info()}, mock.MagicMock())
        self.assertEqual(self._score_log_calls(), [])

    def test_update_logs(self):
        """Updating a CVE logs the score's source and the missing base score warning."""
        dlc_cve = self._dlc_cve()
        self.job.update_cve(dlc_cve, self._vendor_cve_info())
        self._assert_logged(dlc_cve, "CVE Updates")

    def test_update_does_not_log_when_save_fails(self):
        """Nothing is logged when the updated CVE fails validation."""
        dlc_cve = self._dlc_cve()
        dlc_cve.validated_save.side_effect = ValidationError("invalid")
        self.job.update_cve(dlc_cve, self._vendor_cve_info())
        self.assertEqual(self._score_log_calls(), [])

    def test_no_logs_for_nist_score_with_base_score(self):
        """Creating or updating a CVE with NIST's own base score logs neither message."""
        cve_info = self.job.prep_cve_for_dlc(self._cve_json({"cvssMetricV31": _metric_entry(7.5, "Primary")}))
        with mock.patch.object(CVELCM.objects, "get_or_create", return_value=(self._dlc_cve(), True)):
            self.job.create_dlc_cves({"CVE-2024-0001": cve_info}, mock.MagicMock())
        self.job.update_cve(self._dlc_cve(), cve_info)
        self.assertEqual(self._score_log_calls(), [])

    def test_processing_does_not_log(self):
        """Processing a CVE that is neither created nor updated logs neither message."""
        self._vendor_cve_info()
        self.assertEqual(self._score_log_calls(), [])


class NistCveSyncSoftwareCreateCveTestCase(TestCase):
    """Test the CVSS values NistCveSyncSoftware.create_dlc_cves saves to the database."""

    def setUp(self):
        """Construct a NistCveSyncSoftware instance, bypassing Job.__init__."""
        self.job = NistCveSyncSoftware.__new__(NistCveSyncSoftware)
        self.job.logger = mock.MagicMock()

    def _create_cve(self, metrics):
        """Run a NIST CVE record through prep_cve_for_dlc and create_dlc_cves, and return the saved CVE."""
        cve_info = self.job.prep_cve_for_dlc(_nist_cve_record(metrics))
        self.job.create_dlc_cves({"CVE-2024-0001": cve_info}, mock.MagicMock())
        return CVELCM.objects.get(name="CVE-2024-0001")

    def test_saves_nist_score_and_legacy_scores(self):
        """A CVE scored by NIST is saved with NIST's highest-version score, vector, severity and legacy scores."""
        v31_metric = _cvss_metric(
            9.8, "CRITICAL", vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H", entry_type="Primary"
        )
        v31_metric[0]["exploitabilityScore"] = 3.9
        v2_metric = _cvss_metric(7.5, vector="AV:N/AC:L/Au:N/C:P/I:P/A:P", entry_type="Primary")
        v2_metric[0]["exploitabilityScore"] = 10.0

        cve = self._create_cve({"cvssMetricV31": v31_metric, "cvssMetricV2": v2_metric})

        self.assertEqual(cve.cvss, 9.8)
        self.assertEqual(cve.severity, CVESeverityChoices.CRITICAL)
        self.assertEqual(cve.cvss_vector, "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H")
        self.assertEqual(cve.cvss_v2, 10.0)
        self.assertEqual(cve.cvss_v3, 3.9)
        self.assertEqual(cve.link, "https://example.com/CVE-2024-0001")

    def test_saves_vendor_score_when_nist_has_not_scored(self):
        """A CVE scored only by the vendor, like CVE-2025-20115, is saved with the vendor's score."""
        metric = _cvss_metric(
            8.6, "HIGH", vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H", entry_type="Secondary"
        )
        metric[0]["source"] = "psirt@cisco.com"

        cve = self._create_cve({"cvssMetricV31": metric})

        self.assertEqual(cve.cvss, 8.6)
        self.assertEqual(cve.severity, CVESeverityChoices.HIGH)
        self.assertEqual(cve.cvss_vector, "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H")
        self.assertIsNone(cve.cvss_v2)
        self.assertIsNone(cve.cvss_v3)

    def test_saves_empty_values_without_cvss_metrics(self):
        """A CVE without CVSS metrics is saved with no score, a severity of None and an empty vector."""
        cve = self._create_cve({})

        self.assertIsNone(cve.cvss)
        self.assertEqual(cve.severity, CVESeverityChoices.NONE)
        self.assertEqual(cve.cvss_vector, "")
        self.assertIsNone(cve.cvss_v2)
        self.assertIsNone(cve.cvss_v3)


class NistCveSyncSoftwareRunTestCase(TestCase):
    """Test NistCveSyncSoftware.run for Software Versions that netutils cannot build NIST URLs for."""

    def setUp(self):
        """Create a job with a stubbed logger and NIST session."""
        self.active_status, _ = Status.objects.get_or_create(name="Active")
        self.active_status.content_types.add(ContentType.objects.get_for_model(SoftwareVersion))
        self.job = NistCveSyncSoftware.__new__(NistCveSyncSoftware)
        self.job.logger = mock.MagicMock()
        self.job.nist_session_init = mock.MagicMock()

    def test_unsupported_platform_is_skipped(self):
        """A platform without a NIST mapping is skipped with a warning, also when it has no manufacturer."""
        platform = Platform.objects.create(name="FortiOS", network_driver="fortinet")
        SoftwareVersion.objects.create(platform=platform, version="7.0.1", status=self.active_status)

        self.job.run(nist_integration=mock.MagicMock())

        self.job.logger.warning.assert_called_once()
        self.assertIn("fortinet", self.job.logger.warning.call_args.args)
        self.job.logger.error.assert_not_called()

    def test_url_errors_are_logged_with_platform_name(self):
        """Versions netutils cannot parse are logged as errors, also when the platform has no manufacturer."""
        for name, network_driver, version in (("Cisco IOS", "cisco_ios", ""), ("Junos", "juniper_junos", "garbage")):
            platform = Platform.objects.create(name=name, network_driver=network_driver)
            SoftwareVersion.objects.create(platform=platform, version=version, status=self.active_status)

        self.job.run(nist_integration=mock.MagicMock())

        logged_platforms = {logged_call.args[1] for logged_call in self.job.logger.error.call_args_list}
        self.assertEqual(logged_platforms, {"Cisco IOS", "Junos"})

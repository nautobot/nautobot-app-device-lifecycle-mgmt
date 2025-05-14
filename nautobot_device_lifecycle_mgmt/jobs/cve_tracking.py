# pylint: disable=logging-not-lazy, consider-using-f-string
"""Jobs for the CVE Tracking portion of the Device Lifecycle app."""

import json
import re
from datetime import date, datetime
from time import sleep

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from nautobot.dcim.models import Device, InventoryItem
from nautobot.dcim.models.devices import SoftwareVersion
from nautobot.extras.jobs import BooleanVar, Job, ObjectVar, StringVar
from nautobot.extras.models import ExternalIntegration, Secret
from nautobot.extras.secrets.exceptions import SecretError
from netutils.lib_mapper import NIST_LIB_MAPPER_REVERSE
from netutils.nist import get_nist_vendor_platform_urls
from requests import Session
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError
from urllib3.util import Retry

from nautobot_device_lifecycle_mgmt.models import CVELCM, VulnerabilityLCM

name = "CVE Tracking"  # pylint: disable=invalid-name


class GenerateVulnerabilities(Job):
    """Generates VulnerabilityLCM objects based on CVEs that are related to Devices."""

    name = "Generate Vulnerabilities"
    description = "Generates any missing Vulnerability objects."
    read_only = False
    published_after = StringVar(
        regex=r"^[0-9]{4}\-[0-9]{2}\-[0-9]{2}$",
        label="CVEs Published After",
        description="Enter a date in ISO Format (YYYY-MM-DD) to only process CVEs published after that date.",
        default="1970-01-01",
        required=False,
    )
    debug = BooleanVar(description="Enable for more verbose logging.")

    class Meta:
        """Meta class for the job."""

        has_sensitive_variables = False
        field_order = [
            "published_after",
            "_task_queue",
            "debug",
        ]

    def run(self, published_after, debug=False):  # pylint: disable=too-many-locals, arguments-differ
        """Check if software assigned to each device is valid. If no software is assigned return warning message."""
        # Although the default is set on the class attribute for the UI, it doesn't default for the API
        published_after = published_after if published_after is not None else "1970-01-01"
        cves = CVELCM.objects.filter(published_date__gte=datetime.fromisoformat(published_after))
        count_before = VulnerabilityLCM.objects.count()

        for cve in cves:
            if debug:
                self.logger.info(
                    "Generating vulnerabilities for CVE %s" % cve,
                    extra={"object": cve},
                )
            for software in cve.affected_softwares.all():
                for device in Device.objects.filter(software_version=software):
                    VulnerabilityLCM.objects.get_or_create(cve=cve, software=software, device=device)

                for inventory_item in InventoryItem.objects.filter(software_version=software):
                    VulnerabilityLCM.objects.get_or_create(cve=cve, software=software, inventory_item=inventory_item)

        diff = VulnerabilityLCM.objects.count() - count_before
        self.logger.info("Processed %d CVEs and generated %d Vulnerabilities." % (cves.count(), diff))


class NistCveSyncSoftware(Job):
    """Checks all device SoftwareVersion for NIST recorded vulnerabilities."""

    name = "NIST - Software CVE Search"
    description = "Searches the NIST DBs for CVEs related to SoftwareVersion"
    read_only = False

    nist_integration = ObjectVar(
        model=ExternalIntegration,
        query_params={
            "name__contains": "NIST",
        },
        description="Select the NIST integration to use",
        required=True,
        default=lambda: ExternalIntegration.objects.get(name="NAUTOBOT DLM NIST EXTERNAL INTEGRATION"),
    )

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta class for the job."""

        commit_default = True
        soft_time_limit = 3600

    def run(self, *args, **kwargs: dict):  # pylint: disable=too-many-locals
        """Check all software in DLC against NIST database and associate registered CVEs.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        try:
            self.nist_api_key = Secret.objects.get(name="NAUTOBOT DLM NIST API KEY").get_value()  # pylint: disable=attribute-defined-outside-init
        except SecretError as err:
            self.logger.error(
                "This job REQUIRES a fully configured Secret named 'NAUTOBOT DLM NIST API KEY'.  Please refer to the documentation to obtain an api key and complete configuration. %s",
                err,
            )
            return

        if kwargs.get("nist_integration"):
            self.integration = kwargs["nist_integration"]  # pylint: disable=attribute-defined-outside-init
        else:
            self.logger.error("NIST ExternalIntegration object is required.")
            return

        cve_counter = 0

        for software in SoftwareVersion.objects.all():
            manufacturer = software.platform.manufacturer.name.lower()
            platform = software.platform.network_driver.lower()
            version = software.version.replace(" ", "")
            self.logger.info(platform)
            try:
                platform = NIST_LIB_MAPPER_REVERSE[platform]
            except KeyError:
                self.logger.warning(
                    "OS Platform %s is not yet supported; Skipping.",
                    platform,
                    extra={"object": software.platform, "grouping": "CVE Information"},
                )
                continue

            try:
                cpe_software_search_urls = get_nist_vendor_platform_urls(manufacturer, platform, version)
                if not cpe_software_search_urls:
                    self.logger.error(
                        "The URL generator was not able to create URLs for this Software Version. Please check the version value for %s %s %s.",
                        software.platform.manufacturer.name,
                        software.platform.network_driver,
                        software.version,
                        extra={"grouping": "URL Creation"},
                    )
                    continue
                # URLS are obtaind from netutils.nist method that includes the NIST URL.
                # We need to remove the NIST URL and replace it with the one from the integration in order to allow customization if needed.
                cpe_software_search_urls = [
                    re.sub(r"^.*(?=\?)", self.integration.remote_url, cpe_url) for cpe_url in cpe_software_search_urls
                ]
            # Known possible error from netutils.nist method
            except ValueError as err:
                self.logger.error(
                    "There was an error in creating URLs for this Software Version. Please check the version value for %s %s %s. ERROR: %s",
                    software.platform.manufacturer.name,
                    software.platform.network_driver,
                    software.version,
                    err,
                    extra={"grouping": "URL Creation"},
                )
                continue

            self.logger.info(
                "Gathering CVE Information for Software Version: %s",
                version,
                extra={"object": software.platform, "grouping": "CVE Information"},
            )

            software_cve_info = self.get_cve_info(cpe_software_search_urls, software)
            all_software_cve_info = {**software_cve_info["new"], **software_cve_info["existing"]}

            cve_counter += len(software_cve_info["new"])
            self.create_dlc_cves(software_cve_info["new"])

            for software_cve, cve_info in all_software_cve_info.items():
                try:
                    matching_dlc_cve = CVELCM.objects.get(name=software_cve)
                except CVELCM.DoesNotExist:
                    self.logger.warning(
                        "CVE %s does not exist in the DLM DB. Skipping.",
                        software_cve,
                        extra={"object": software, "grouping": "CVE Association"},
                    )
                    continue

                try:
                    matching_dlc_cve.affected_softwares.add(software)
                except IntegrityError as err:
                    self.logger.error(
                        "Unable to create association between CVE and Software Version.  ERROR: %s",
                        err,
                        extra={"object": matching_dlc_cve, "grouping": "CVE Association"},
                    )

                if str(cve_info["modified_date"][0:10]) != str(matching_dlc_cve.last_modified_date):
                    self.update_cve(matching_dlc_cve, cve_info)

            # API Rest Timer
            sleep(self.integration.extra_config.get("api_call_delay", 6))

        self.logger.info(
            "Performed discovery on all software. Created %s CVE.", cve_counter, extra={"grouping": "CVE Creation"}
        )

    def create_dlc_cves(self, cpe_cves: dict) -> None:
        """Create CVE entries in the DLC database.

        Args:
            cpe_cves (dict): Dictionary of CVEs to be created.
        """
        created_count = 0

        for cve, info in cpe_cves.items():
            try:
                description = (
                    f"{info['description'][0:252]}..." if len(info["description"]) > 255 else info["description"]
                )
            except TypeError:
                description = "No Description Provided from NIST DB."

            _, created = CVELCM.objects.get_or_create(
                name=cve,
                description=description,
                published_date=date.fromisoformat(info.get("published_date", "1900-01-01")[0:10]),
                last_modified_date=date.fromisoformat(info.get("modified_date", "1900-01-01")[0:10]),
                link=info["url"],
                cvss=info["cvss_base_score"],
                severity=info["cvss_severity"],
                cvss_v2=info["cvssv2_score"],
                cvss_v3=info["cvssv3_score"],
                comments="ENTRY CREATED BY NAUTOBOT NIST JOB",
            )

            if created:
                created_count += 1

        self.logger.info("Created New CVEs.", extra={"grouping": "CVE Creation"})

    def get_cve_info(self, cpe_software_search_urls: list, software: SoftwareVersion) -> dict:
        """Search NIST for software and related CVEs.

        Args:
            cpe_software_search_urls (list): List of URLs to query for CVE information.
            software (object): Software object being queried.

        Returns:
            dict: Dictionary containing new and existing CVE information.
        """
        cve_set = set()
        all_cve_info = {"new": {}, "existing": {}}

        for cpe_software_search_url in cpe_software_search_urls:
            result = self.query_api(cpe_software_search_url)
            if result["totalResults"] > 0:
                cve_set.union({cve["cve"] for cve in result["vulnerabilities"]})
        if cve_set:
            self.logger.info(
                "Received %s results.",
                len(cve_set),
                extra={"object": software, "grouping": "CVE Creation"},
            )
            all_cve_info = self.process_cves(cve_set, software)

        return all_cve_info

    def process_cves(self, cve_set: set, software: SoftwareVersion) -> dict:
        """Return processed CVE info categorized as new or existing.

        Args:
            cve_set (set): Set of CVEs returned from CPE search.
            software (object): Software object being queried.

        Returns:
            dict: Dictionary of CVEs categorized as new or existing.
        """
        processed_cve_info = {"new": {}, "existing": {}}
        dlc_cves = CVELCM.objects.values_list("name", flat=True)

        for cve in cve_set:
            cve_name = cve["id"]
            if not cve_name.startswith("CVE"):
                continue
            if cve_name not in dlc_cves:
                processed_cve_info["new"].update({cve_name: self.prep_cve_for_dlc(cve)})
            else:
                processed_cve_info["existing"].update({cve_name: self.prep_cve_for_dlc(cve)})
        self.logger.info(
            "Prepared %s CVE for creation." % len(processed_cve_info["new"]),
            extra={"object": software, "grouping": "CVE Creation"},
        )

        return processed_cve_info

    def query_api(self, url: str) -> dict:
        """Query the NIST API using an established session.

        Args:
            url (str): The API endpoint being queried.

        Returns:
            dict: Dictionary of returned results if successful.
        """
        # Build retry configuration; Uses Integration settings but setting sane defaults in case they are removed
        retries = Retry(
            total=self.integration.extra_config.get("retries", {}).get("max_attempts", 3),
            backoff_factor=self.integration.extra_config.get("retries", {}).get("backoff", 1),
            status_forcelist=[502, 503, 504],
            allowed_methods=["GET"],
        )

        # Create and configure session
        session = Session()
        session.mount("https://", HTTPAdapter(max_retries=retries))
        session.headers.update({"apiKey": self.nist_api_key})

        try:
            result = session.get(url)
            result.raise_for_status()
            return result.json()
        except HTTPError as err:
            code = err.response.status_code
            self.logger.error(
                "The NIST Service is currently unavailable. Status Code: %s. Try running the job again later.", code
            )
            raise
        except json.JSONDecodeError as err:
            self.logger.error("Invalid JSON response from NIST Service: %s", err)
            raise
        finally:
            session.close()

    @staticmethod
    def convert_v2_base_score_to_severity(score: float) -> str:
        """Uses V2 Base Score to convert to Severity Value.

        Args:
            score (float): CVSS V2 Base Score

        Returns:
            str: Severity Value ["HIGH", "MEDIUM", "LOW", "UNDEFINED"]
        """
        if 0.0 >= score <= 3.9:
            return "LOW"
        if 4.0 >= score <= 6.9:
            return "MEDIUM"
        if 7.0 >= score <= 10:
            return "HIGH"
        return "UNDEFINED"

    def prep_cve_for_dlc(self, cve_json: dict) -> dict:  # pylint: disable=too-many-locals
        """Convert CVE info into a format compatible with the DLC model.

        Args:
            cve_json (dict): JSON object containing CVE information.

        Returns:
            dict: Dictionary of CVE information formatted for DLC.
        """
        cve_name = cve_json["id"]
        cve_description = next(
            (desc["value"] for desc in cve_json["descriptions"] if desc["lang"] == "en"),
            "No English description provided."
        )

        cve_published_date = cve_json["published"]
        cve_modified_date = cve_json["lastModified"]
        cve_impact = cve_json.get("metrics")

        # Determine URL
        if len(cve_json["references"]) > 0:
            cve_url = cve_json["references"][0].get("url", f"https://www.cvedetails.com/cve/{cve_name}/")
        else:
            cve_url = f"https://www.cvedetails.com/cve/{cve_name}/"

        # Determine if V3 exists and set all params based on found version info
        if cve_impact:
            if cve_impact.get("cvssMetricV31"):
                cvss_base_score = cve_impact["cvssMetricV31"][0]["cvssData"]["baseScore"]
                cvss_severity = cve_impact["cvssMetricV31"][0]["cvssData"]["baseSeverity"]
                if cve_impact.get("cvssMetricV2"):
                    cvssv2_score = cve_impact["cvssMetricV2"][0].get("exploitabilityScore", 10)
                else:
                    cvssv2_score = 10
                cvssv3_score = cve_impact["cvssMetricV31"][0].get("exploitabilityScore", 10)

            elif cve_impact.get("cvssMetricV30"):
                cvss_base_score = cve_impact["cvssMetricV30"][0]["cvssData"]["baseScore"]
                cvss_severity = cve_impact["cvssMetricV30"][0]["cvssData"]["baseSeverity"]
                if cve_impact.get("cvssMetricV2"):
                    cvssv2_score = cve_impact["cvssMetricV2"][0].get("exploitabilityScore", 10)
                else:
                    cvssv2_score = 10
                cvssv3_score = cve_impact["cvssMetricV30"][0].get("exploitabilityScore", 10)

            else:
                cvss_base_score = cve_impact["cvssMetricV2"][0]["cvssData"]["baseScore"]
                cvss_severity = cve_impact["cvssMetricV2"][0]["baseSeverity"] or self.convert_v2_base_score_to_severity(
                    cvss_base_score
                )
                cvssv2_score = cve_impact["cvssMetricV2"][0].get("exploitabilityScore", 10)
                cvssv3_score = 0

            all_cve_info = {
                "url": cve_url,
                "description": cve_description,
                "published_date": cve_published_date,
                "modified_date": cve_modified_date,
                "cvss_base_score": cvss_base_score,
                "cvss_severity": cvss_severity,
                "cvssv2_score": cvssv2_score,
                "cvssv3_score": cvssv3_score,
            }

        else:
            all_cve_info = {
                "url": cve_url,
                "description": cve_description,
                "published_date": cve_published_date,
                "modified_date": cve_modified_date,
            }
        return all_cve_info

    def update_cve(self, current_dlc_cve: CVELCM, updated_cve: dict) -> None:
        """Update CVE information if the latest info is newer than existing info.

        Args:
            current_dlc_cve (CVELCM): Current CVE object from the DLM database.
            updated_cve (dict): Latest CVE information from the software pull.
        """
        update_message = "ENTRY HAS BEEN UPDATED BY NAUTOBOT NIST JOB"
        description = updated_cve.get("description", "No description provided from NIST DB")
        current_dlc_cve.description = (
            f"{description[0:252]}..."
            if len(description) > 255
            else description
        )

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_dlc_cve.last_modified_date = f"{updated_cve['modified_date'][0:10]}"
        current_dlc_cve.link = updated_cve["url"]
        current_dlc_cve.cvss = updated_cve["cvss_base_score"]
        current_dlc_cve.severity = updated_cve["cvss_severity"].title()
        current_dlc_cve.cvss_v2 = updated_cve["cvssv2_score"]
        current_dlc_cve.cvss_v3 = updated_cve["cvssv3_score"]
        current_dlc_cve.comments = f"{update_message} - {timestamp}\n\n{current_dlc_cve.comments}"

        try:
            current_dlc_cve.validated_save()
            self.logger.info("Modified CVE.", extra={"object": current_dlc_cve, "grouping": "CVE Updates"})
        except ValidationError as err:
            self.logger.error(
                "Unable to update CVE. ERROR: %s", err, extra={"object": current_dlc_cve, "grouping": "CVE Updates"}
            )

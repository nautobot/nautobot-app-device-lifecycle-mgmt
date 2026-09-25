# CVE Tracking

The CVE Tracking portion of the app provides two additional objects - CVE objects and Vulnerability objects.

## CVE objects

A CVE object can be used to record Common Vulnerabilities and Exposures as well as any detailed information that is useful to track about them such as publish date, severity, CVSS scores and more. CVE objects can be used individually, but they can then be associated to one or many Software objects via `Affected Softwares` field.

When creating a CVE object, the following fields are available. Fields in **bold** are mandatory.

| Field | Description |
| -- | -- |
| **Name** | The name of the CVE |
| **Published Date** | Date when the CVE was published |
| **Link** | The URL that the CVE details were obtained from |
| Status | The current status of the CVE (requires a [Status object](https://docs.nautobot.com/projects/core/en/stable/models/extras/status/) to be created and associated to the CVE model) |
| Description | The description of the CVE |
| Severity | The severity (Low, Medium, High, Critical) of the CVE |
| CVSS Base Score | The Common Vulnerability Scoring System base score of the CVE. The NIST CVE Search Job populates this from the highest CVSS version available (v4.0, then v3.1, v3.0, v2) |
| CVSS Vector | The CVSS vector string for the CVSS version used for the CVSS Base Score and Severity. The version is shown by the vector's prefix (for example `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H`); CVSS v2 vectors have no prefix (for example `AV:N/AC:L/Au:N/C:P/I:P/A:P`). On the CVE detail page, click the vector to open a pop-up that explains each metric and links to the official CVSS calculator. The NIST CVE Search Job populates this automatically |
| CVSSv2 Score | **Deprecated.** Legacy field retained for backward compatibility; no longer populated by the NIST CVE Search Job |
| CVSSv3 Score | **Deprecated.** Legacy field retained for backward compatibility; no longer populated by the NIST CVE Search Job |
| Affected Softwares | Software versions affected by this CVE |
| Fix | The software fix (if available) for the CVE |
| Comments | Any additional comments or details about the CVE |
| Tags | Arbitrary [tag objects](https://docs.nautobot.com/projects/core/en/stable/models/extras/tag/) that can be applied to this CVE |
| Last Modified Date | The date that the CVE record was last modified |

!!! warning "Deprecated fields"
    The CVSSv2 Score (`cvss_v2`) and CVSSv3 Score (`cvss_v3`) fields are deprecated and will be removed in an upcoming major version of this app. If you rely on these fields (for example in the REST API, GraphQL, filters, or export templates), plan to migrate to a custom field before upgrading to the next major version.

!!! note
    In addition to these standard fields, you can also add one or more [Custom Fields](https://docs.nautobot.com/projects/core/en/stable/models/extras/customfield/) to the model.


### Software Association

As stated previously, you can associate a CVE to one or many software versions. These relationships will present themselves as breadcrumb links on the CVE item's detail view, and as the "Related CVEs" tab on the Software item's detail view.

Example of a breadcrumb link on a CVE item's view:

![](../images/ss_lcm_cve_breadcrumb_light.png#only-light){ .on-glb }
![](../images/ss_lcm_cve_breadcrumb_dark.png#only-dark){ .on-glb }
[//]: # "`https://next.demo.nautobot.com/plugins/nautobot-device-lifecycle-mgmt/cve/0cc65c48-a17e-592b-8495-0f4681598eef/`"

Example of the "Related CVEs" tab on a Software item's view:

![](../images/ss_lcm_software_breadcrumb_light.png#only-light){ .on-glb }
![](../images/ss_lcm_software_breadcrumb_dark.png#only-dark){ .on-glb }
[//]: # "`https://next.demo.nautobot.com/plugins/nautobot-device-lifecycle-mgmt/software-versions/6d4b73fb-38da-523c-84fd-5109163231c9/related-cves/?tab=nautobot_device_lifecycle_mgmt:1`"

## Vulnerability objects

A Vulnerability object is the representation of a discovered relationship between a CVE object, a Software object and a Device (or Inventory Item) object. Vulnerability objects cannot be created manually, but rather they must be generated via a Job. They require the combination of a CVE object that is associated to a Software object **and** that Software object to be associated to a Device or Inventory Item object in order to be discovered and generated. You can think of Vulnerability objects like an attack surface that was found in your infrastructure that must be mitigated (such as upgrading the affected device to a patched software version).

To generate Vulnerability objects you must run the ``Generate Vulnerabilities`` Job that is packaged as part of this app. One Vulnerability object will be created for **each** unique combination of CVE/Software/Device and CVE/Software/Inventory Item.

!!! note
    When running the ``Generate Vulnerabilities`` Job, if any unique combinations are found that match an existing Vulnerability object, the Job will not create a duplicate object nor modify the existing object.

### Modifying or Removing Vulnerability objects

After a Vulnerability object has been generated, the CVE, Software, Device and Inventory Item fields on that object cannot be modified, however the following fields may be modified (individually or in bulk).

| Field | Description |
| -- | -- |
| Status | The current status of the Vulnerability (requires a [Status object](https://docs.nautobot.com/projects/core/en/stable/models/extras/status/) to be created and associated to the Vulnerability model) |
| Tags | Arbitrary [tag objects](https://docs.nautobot.com/projects/core/en/stable/models/extras/tag/) that can be applied to this CVE |

!!! note
    In addition to these standard fields, you can also add one or more [Custom Fields](https://docs.nautobot.com/projects/core/en/stable/models/extras/customfield/) to the model.

As was stated previously, running the ``Generate Vulnerabilities`` Job will not modify (or delete) any existing Vulnerability objects - **even if the associations that existed previously no longer exist**. You do have the ability to delete one or more Vulnerability objects via the GUI or API. In addition to manually removing a Vulnerability, if any CVE, Software, Device or Inventory Item objects are removed, any Vulnerability objects that reference the deleted items will also be removed automatically.

## Automated CVE Discovery via NIST API 2.0
The NTC Nautobot Device Lifecycle Management app now supports automated CVE discovery via the NIST NVD API 2.0.  This feature is optional and can be enabled by obtaining an API key, updating the necessary Secret, and running the ``NIST - Software CVE Search`` Job. Continue reading for more information.

!!! note
    If a manual CVE entry exists with a Name that differs from the NIST CVE Name, a new CVE record will be created and associated.  If the manual Name
    matches, any updates pulled from NIST will be made to the existing record and the association will be ensured.

!!! note
    If a record is updated due to a mismatched Modified Date against NIST, a comment will be added to the TOP of the comments section notifying of an update and the timestamp that the record was locally modified.  The record's Last Modifed Date will be updated to show when the record itself was modifed in NIST.

!!! note
    The Job sets the CVE's CVSS Base Score and Severity from the highest CVSS version NIST provides (v4.0, then v3.1, v3.0, v2), and records that version's vector string in the CVSS Vector field. For v3.0 and later, the Severity is NIST's `baseSeverity`. For v2, the Severity is always derived from the base score (Low: 0.0-3.9, Medium: 4.0-6.9, High: 7.0-10.0). The legacy CVSSv2 Score and CVSSv3 Score fields are no longer modified by the Job.

### External Integration
An External Integration must be created and configured in order to use the NIST NVD API for automatic software CVE discovery. On this note, the following is installed for you:

- A new External Integration object named ``NAUTOBOT DLM NIST EXTERNAL INTEGRATION`` that allows you to control the following behaviors of the integration:
    - ``api_call_delay``: A delay between API calls in seconds (default: 6).  NIST Recommends a minimum value of 6 to prevent overloading resources.
    - ``retries``: Controls how the job handles transient failures from the NIST API. There are two retry layers:
        - HTTP status retries at the session layer (502/503/504).
        - Transport-level failures at the job layer — `requests.exceptions.ConnectionError`, `ChunkedEncodingError` (e.g., HTTP/2 stream resets such as `Stream X was reset by remote peer`), and `Timeout`. On a transport-level failure the job closes the existing NIST session, re-initializes a fresh one via `nist_session_init`, sleeps `backoff * attempt` seconds, and retries the same URL up to `max_attempts` times before re-raising. HTTP errors and JSON decode errors are not retried at the job layer and propagate immediately.
        - ``max_attempts``: The maximum number of attempts (default: 3). Used by both layers above.
        - ``backoff``: The backoff factor for the retry attempts (default: 2). At the session layer this is the urllib3 `backoff_factor`; at the job layer this is the multiplier applied as `backoff * attempt` before each rebuild-and-retry.
- A new Secrets Group object named ``NAUTOBOT DLM NIST SECRETS GROUP`` used for access to the NIST API Key from the External Integration.
- A new Secret object named ``NAUTOBOT DLM NIST API KEY``.  This object is created for you during setup with minimum defaults.  The Secret name must be exactly as above, but you will need to configure the Secret to properly access the NIST API Key.
    - To obtain your NIST API Key go [here](https://nvd.nist.gov/developers/request-an-api-key).
    - This key will be made invalid if not used for a seven day period and a request for a new key will be necessary to use this function.

NOTE: You may change the name of the External Integration or create your own using other configuration settings, but the SecretsGroup and Secret objects must be named as above.  The External Integration is selected when starting the Job run.


### Version formats for NIST CVE search

The ``NIST - Software CVE Search`` Job uses `netutils.nist` and `netutils.os_version` to build NIST NVD query URLs from each Software Version's platform (network driver) and version string. Each NIST-mapped platform uses either the **default** parser or a **vendor-specific** parser. The **version** value on your Software Version objects should match the format expected by that parser so that CVE discovery works correctly.

#### Platforms using the default parser

These platforms use the default parser from `netutils.os_version` (Generic - Loosely based on, and compatible with SymVer formatting.):

| Network driver   | NIST vendor:platform                              |
|------------------|---------------------------------------------------|
| `arista_eos`     | arista:eos                                        |
| `aruba_os`       | arubanetworks:arubaos                             |
| `cisco_asa`      | cisco:adaptive_security_appliance_software        |
| `cisco_ios`      | cisco:ios                                         |
| `cisco_nxos`     | cisco:nx-os                                       |
| `cisco_xe`       | cisco:ios_xe                                      |
| `cisco_xr`       | cisco:ios_xr                                      |
| `paloalto_panos` | paloaltonetworks:pan-os                           |

**Default parser version format:**

- **Full (preferred):** `major.minor.patch` with optional `-prerelease` and `+buildmetadata`.
    - `major`, `minor`, `patch`: numeric, no leading zeros (e.g. `0`, `1`, `10`).
    - `prerelease`: alphanumeric, hyphens, dots (e.g. `alpha`, `alpha.beta.1`).
    - `buildmetadata`: alphanumeric, hyphens, dots (e.g. `build.1`).
- **Fallback:** `major.minor` followed by any suffix (e.g. `15.5(2)S1c`, `10.20`, `1.0.0-alpha`).

Examples: `15.5`, `10.20.30`, `1.0.0-alpha.beta.1`, `15.5(2)S1c`, `9.1.6`, `9.1.15-h1`.

#### Platforms using a custom parser

| Network driver   | NIST vendor:platform |
|------------------|----------------------|
| `juniper_junos`  | juniper:junos        |

**Juniper JunOS version format:**

- **Core:** `main.minor` (digits), then optionally a **type** (`x`, `X`, `r`, `R`, `s`, `S`) and **build** (digits).
- **Optional suffix** after `-` or `:`: service letter (`s`/`S` or `d`/`D`) + optional `service_build` (digits) + optional `.` + `service_respin` (digits).

Pattern: 
<pre>
12.1R3-S4.1
│   ││ ││ │
│   ││ ││ └─── service_respin
│   ││ |└───── service_build (4)
│   ││ └────── service_letter (S)
│   │└──────── build (3)
│   └───────── build_type (R)
└───────────── main.minor (12.1)
</pre>

Examples: `12.3R4`, `12.1R3-S4.1`, `12.1x47`, `12.2x50:d41.1`, `10.2R2.11`, `10.4s`.

If the version does not match this pattern, the JunOS parser will not populate the fields needed for the custom NIST URL builder and CVE discovery may fail or be incorrect for that software.

If your platform is not in the above listings the entry will be skipped leaving a log message.  You may submit an issue request to have a mapping added to the netutils library to support your platform. Issue requests for netutils can be submitted here: https://github.com/networktocode/netutils/issues

### Run Job
Automated discovery is used by running the ``NIST - Software CVE Search`` Job.

To run this job, use the "Jobs" menu dropdown and navigate to the **CVE Tracking** section. The jobs will appear here and all you will need to do is click the play button in order to use the default External Integration[^1].  If you have configured additional Integrations, you may select the External Integration that you want to use.  **As stated previously, the name of the External Integration does not matter, but the External Integration must contain a SecretsGroup and Secret named as above**.

![](../images/ss_lcm_cve_nist_job_light.png#only-light){ .on-glb }
![](../images/ss_lcm_cve_nist_job_dark.png#only-dark){ .on-glb }
[//]: # "`https://next.demo.nautobot.com/extras/jobs/`"

![](../images/ss_lcm_cve_nist_job_run_light.png#only-light){ .on-glb }
![](../images/ss_lcm_cve_nist_job_run_dark.png#only-dark){ .on-glb }
[//]: # "`https://next.demo.nautobot.com/extras/jobs/fae52b77-309e-48d7-97fb-33a85f3028e1/run/`"

The job output should indicate the softwares checked and the amount of CVEs received for that software, as well as the amount of CVEs created.  These will not always be the same.  New CVE will be created for software with existing CVE, also software will share CVEs.

![](../images/ss_lcm_cve_nist_job_log_light.png#only-light){ .on-glb }
![](../images/ss_lcm_cve_nist_job_log_dark.png#only-dark){ .on-glb }
[//]: # "`https://next.demo.nautobot.com/extras/job-results/6b261884-fb23-43cb-a958-b5a99aebc3b2/`"

[^1] Warning: If play button is grayed out. You will need to enable the job by clicking on edit button in the row and navigate to "Job" portion and click on "Enable"


### Additional Notes:
Due to the way vendor platform entries vary in NIST, some platforms may work without issue, others may not work so well (false positives/negatives).  Juniper JunOS is a great example and has a custom parser in netutils to handle this.

If the platform you are attempting to gather information from does not work, a custom parser will likely be needed to build a proper NIST search URL.

### External Documentation References

#### Relevent Netutils Module Documentation
*OS Version Module* - Responsible for parsing version strings into version parameters:
    https://netutils.readthedocs.io/en/latest/user/lib_use_cases_os_version/

*NIST Module* - Responsible for all NIST related functions:
    https://netutils.readthedocs.io/en/latest/user/lib_use_cases_nist/

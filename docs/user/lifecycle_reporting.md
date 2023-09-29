# Lifecycle Reporting

Lifecycle reporting can be seen by running either of the two jobs below:

- Device Software Validation Report
- Inventory Item Software Validation Report

You can run these reports two ways:

- The "Device Lifecycle" dropdown menu and selecting either **Device Software Validation - Report** or **Inventory Item Software Validation - Report** and then clicking on **Run Software Validation** execute button on right side of screen.

![](../images/lcm_software_validation_report_run.png)

- The "Jobs" dropdown and navigating to **Device/Sofware Lifecycle Reporting** section. The jobs will appear here and all you will need to do is click the play button.

![](../images/lcm_software_validation_report_run_jobs.png)

!!! warning "If play button is grayed out."
    You will need to enable the job by clicking on edit button in the row and navigate to "Job" portion and click on "Enable"

## Device Software Validation Reports

Once the jobs are ran you can nagivate to the Device Software Validation Reports by selecting **Device Software Validation - Report** or **Inventory Item Software Validation - Report** from the "Device Lifecycle" dropdown menu.

- ** Summary Graph ** - This will have your validated job results per platform

![](../images/lcm_software_validation_report_run_graph.png)

!!! warning "If graph has too many platforms it will not render very well. You can filter it down to only a few with the right side search form. This issue is currenlty being worked on."

- ** Executive Summary ** - Quick summary of all objects found with the report run.

![](../images/lcm_software_validation_report_run_executive_summary.png)

- ** Device Type/Inventory Item Summary ** - Summery of each Device Type or Inventory Item objects found with the report run.

![](../images/lcm_software_validation_report_run_detailed_summary.png)

---

From the Device Software Validation Reports you can export the report results using the **Export Data** column. The export will be a CVS file. To gather all results export data from the Executive Summary row or you can export each individual Device Type/Inventory Item in its row.

## Validation Results Page

Once the jobs are ran you can nagivate to the results page by selecting **Device Software Validation - List** or **Inventory Item Software Validation - List** from the "Device Lifecycle" dropdown menu.

![](../images/lcm_software_validation_report_run_results_list.png)

The validation list page will give you all the information needed in regards to the validation results. All columns are sortable and filters can be applied.

| Column | Description |
| -- | -- |
| **Device/Invenotry Item** | Name of the device/inventory item in the job result. |
| **Current Software** | Software that is currenlty on the device/inventory item. |
| **Valid** | The result of the software validation of the device/inventory item. |
| **Last Run** | Last time the software validation job was ran on the device/inventory item. |
| **Run Type** | Type of software validation job that was ran. |
| **Approved Software** | This is Validated Software object that is associated. This can be a list of softwares. |

!!! warning "Hardcoded filter warning."
    If you navigated from the summary page by clicking on the links in the **Valid** or **Invalid** columns there will be a hardcoded filter set.

    **Example:** http://prod.nautobot.com/plugins/nautobot-device-lifecycle-mgmt/device-validated-software-result/?&device_type=ASR-9903&valid=False&**exclude_sw_missing=True**

    This is added so that list of device/inventory items validation results that have missing software will be omited from view. 
    You can remove the filter from clicking on the "x" by the **exclude_sw_missing** filter.

## Exporting Validation Job Results

There are various ways that you can export the validation result data to a CSV file.

**"Device/Inventory Item Software Validation - Report" page **

You can export the validation results using the export button ![](../images/lcm_software_validation_export_button.png) on the row, which will give you more details of the results.

![](../images/lcm_software_validation_report_csv_small.png)

If you hit the export button on the right side it will only give you the summary numbers that are displayed on the page.

![](../images/lcm_software_validation_reports_export_button.png)

If you want all the results click on the export data button on the *Executive Summary* table.

If you are only looking for **individual results** per platform/inventory item you can click on the export data button on that row.

**"Device/Inventory Item Software Validation - List" page**

The export button ![](../images/lcm_software_validation_export_button_green.png) on the right pane of the page.

!!! warning "This will export data that is populated on the screen so if there are any filters applied to the list it will only export those filtered items"

## Validated Software Results List - API

You can gather all the results from report by using the API that is built into Nautobot.

API command

> GET /api/plugins/nautobot-device-lifecycle-mgmt/device-validated-software-result/

Output

```
HTTP 200 OK
API-Version: 1.2
Allow: GET, HEAD, OPTIONS
Content-Type: application/json
Vary: Accept

{
    "count": 1,
    "next": "http://127.0.0.1:8080/api/plugins/nautobot-device-lifecycle-mgmt/device-validated-software-result/?limit=50&offset=50",
    "previous": null,
    "results": [
        {
            "id": "66134b8d-3466-4f3c-8c65-136dad061a5f",
            "display": "Device: core1 - Not Valid",
            "device": {
                "display": "core1",
                "id": "95b61475-0d09-4f65-b2b3-1e7e199264c7",
                "url": "http://127.0.0.1:8080/api/dcim/devices/95b61475-0d09-4f65-b2b3-1e7e199264c7/",
                "name": "core1"
            },
            "software": {
                "display": "juniper - 20.1.1",
                "id": "1eb3ca93-5af4-4ab8-a501-eb9b6d01c39b",
                "url": "http://127.0.0.1:8080/api/plugins/nautobot-device-lifecycle-mgmt/software/1eb3ca93-5af4-4ab8-a501-eb9b6d01c39b/",
                "device_platform": "b2689411-f1db-4a41-b8fa-2babaed5d5e7",
                "version": "20.1.1",
                "end_of_support": null
            },
            "is_validated": false,
            "last_run": "2023-05-09T14:40:45.890392Z",
            "run_type": "full-report-run",
            "valid_software": [
                "e7350b60-8180-4d3e-bccd-3a6dff50fb7c"
            ],
            "url": "http://127.0.0.1:8080/api/plugins/nautobot-device-lifecycle-mgmt/device-validated-software-result/66134b8d-3466-4f3c-8c65-136dad061a5f/",
            "created": "2023-05-09",
            "last_updated": "2023-05-09T14:40:45.973772Z",
            "custom_fields": {},
            "tags": []
        },
    }
}
```

You are able to get the result of if the Device/Inventory Item is valid or not by the "display" key. The key will display the following.

-  "display": "Device: << device.name >> - Not Valid"
-  "display": "Device: << device.name >> - Valid"
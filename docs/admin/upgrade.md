# Upgrading the App

Here you will find any steps necessary to upgrade the App in your Nautobot environment.

!!! note
    If you want to upgrade to a version 3.x of Device Lifecycle Management from the existing version you **MUST** first install a version 2.3.x that contains the "Device Lifecycle Management to Nautobot Core Model Migration" Job. This Job **MUST** be run, which will migrate deprecated DLM objects to the Core, before installing a version 3.x of the DLM app.

## Upgrade Guide 2.x -> 3.x only

Device Lifecycle Management App v3.0 removes the following models:

- SoftwareLCM
- SoftwareImageLCM
- ContactLCM

These models are now part of the core Nautobot application, starting with version 2.2.0.

If you have existing instances of the above models you **MUST** migrate them before installing DLM version 3.0 by following the below steps:

- Ensure your Nautobot version is at least 2.2.0. DLM version 3.0 requires Nautobot version to be min 2.2.0.
- Install version 2.3.x of the DLM app which includes a job named "Device Lifecycle Management to Nautobot Core Model Migration".
- Run the "Device Lifecycle Management to Nautobot Core Model Migration" job and review the logs.
- If needed, fix any errors and warnings and rerun the job until migration is fully complete.
- Install version 3.x of the Device Lifecycle Management app.

### Running the DLM 2.x -> 3 migration Job

The Device Lifecycle Management to Nautobot Core Model Migration Job, included in versions 2.3.x of the application, migrates existing `SoftwareLCM`, `SoftwareImageLCM`, and `ContactLCM` models to the Core models. These models will be removed in the version 3.0 of the DLM app.

To run the migration job, navigate to the “Jobs -> Jobs” page. On that page, find the job named "“"Device Lifecycle Management to Nautobot Core Model Migration"”" in the section titled "DLM Models -> Nautobot Core Models Migration".

![](../images/lcm_version3_migration_job_location.png)

As part of the migration process, this job creates tags on the core model objects that reference DLM objects from which they have been migrated. The data migrations in version 3.0 of the DLM require these tags to rewrite references from DLM to Core models. These are needed to update instances of `ValidatedSoftwareLCM`, `DeviceSoftwareValidationResult`, `InventoryItemValidationResult`, `CVELCM`, and `VulnerabilityLCM` models.

Tags created by the migration job follow the below naming convention:

`DLM_migration-SoftwareLCM__{UUID}` - created for SoftwareVersion objects migrated from DLM SoftwareLCM objects.
`DLM_migration-ContactLCM__{UUID}` - created for Contact objects migrated from DLM ContactLCM objects.
`DLM_migration-SoftwareImageLCM__{UUID}` - created for SoftwareImage objects migrated from DLM SoftwareImageLCM object.

The above tags **MUST** be in place before installing v3.0 of the DLM application. If these tags are not present the data migrations included in v3.0 of the app will prevent Nautobot from starting to avoid data loss. If that happens, you will have to downgrade the app to v2.3.x and rectify issues reported by the data migrations.

When the migration job included in DLM v2.3.x is run new core objects corresponding to the DLM objects will be created. If the job errors out, the already created objects will remain in place. 

If you get any errors in the job logs, note what the problem is, fix it, and rerun the job. Objects already migrated will be revalidated and the job will attempt to migrate the object that failed migration during the previous runs.

#### Migration Job options

Migration job comes with several options, these are explained below.

![](../images/lcm_version3_migration_job_options.png)

**Dryrun** - Enable for reporting mode. No changes are made in this mode, only informational messages about what the migration job identified needs to be migrated.

**Hide ChangeLog migration messages** - Don't display log messages related to ChangeLog object migrations. Select this option if you have a lot of Change logs related to the DLM objects being migrated.

**Update Core to match DLM** - Forcibly update existing Core objects to match DLM objects. If an existing Core object matches the DLM object, then the Job will automatically update the Core object to match the DLM one. You must either enable this option or manually update the DLM side to match the core side.

**Remove dangling relationship associations** - Remove DLM relationship associations where one side refers to the object that is gone. Use this option if the job reports that the object referenced by the relationships association is deleted.

### Q&A

#### I have no existing ValidatedSoftwareLCM, DeviceSoftwareValidationResult, InventoryItemValidationResult, CVELCM, or VulnerabilityLCM objects.

If you don’t have any of the above objects you can run the migration job, and once you’ve confirmed the core objects have been created you can:

- Delete the old DLM `SoftwareLCM`, `ValidatedSoftwareLCM`, and `ContactLCM` objects.
- Delete the `DLM_migration-*` tags created by the migration

Then you can proceed to install v3.0 of the DLM app.

#### The 2.x to 3.0 migration job is taking a long time

It is normal for the job to take a few hours during the initial run. This depends on the number of DLM Software objects and the number of devices that have DLM Software assigned.


## Upgrade Guide

When a new release comes out it may be necessary to run a migration of the database to account for any changes in the data models used by this app. Execute the command `nautobot-server post-upgrade` within the runtime environment of your Nautobot installation after updating the `nautobot-device-lifecycle-mgmt` package via `pip`.

```shell
pip3 install --upgrade nautobot-device-lifecycle-mgmt
```

!!! note
    To ensure Nautobot Device Life Cycle Management app is automatically re-installed during future upgrades, check for a file named `local_requirements.txt` in the Nautobot root directory (alongside `requirements.txt`). The `nautobot-device-lifecycle-mgmt` package should be listed in it.

## Run Post Upgrade Steps

Once the configuration has been updated, run the post migration script as the Nautobot user

```shell
nautobot-server post_upgrade
```

This should run migrations for the app to be ready for use.

## Restart Nautobot Services

As a user account that has privileges to restart services, restart the Nautobot services

```shell
sudo systemctl restart nautobot nautobot-worker
```

If you are on Nautobot >= 1.1.0 and have the RQ worker continuing on, also restart the RQ worker service.

```shell
sudo systemctl restart nautobot-rq-worker
```

!!! note
    If you have multiple workers defined, you will need to restart each worker process. For example `systemctl restart nautobot nautobot-worker@1 nautobot-worker@2` etc.

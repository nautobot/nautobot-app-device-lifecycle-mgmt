# Upgrading the App

Here you will find any steps necessary to upgrade the App in your Nautobot environment.

## Upgrade Guide

When a new release comes out it may be necessary to run a migration of the database to account for any changes in the data models used by this app. Execute the command `nautobot-server post-upgrade` within the runtime environment of your Nautobot installation after updating the `nautobot-device-lifecycle-mgmt` package via `pip`.

```shell
pip3 install --upgrade nautobot-device-lifecycle-mgmt
```

!!! note
    To ensure Nautobot Device Life Cycle Management app is automatically re-installed during future upgrades, check for a file named `local_requirements.txt` in the Nautobot root directory (alongside `requirements.txt`). The `nautobot-app-device-lifecycle-mgmt` package should be listed in it.

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

# Upgrading the Device Lifecycle Plugin

This document is intended to provide an upgrade procedure for the Device Lifecycle Plugin
within Nautobot.  The most stable version of the plugin is available as a Python package 
in pypi and can be upgraded using pip. (https://pypi.org/project/nautobot-device-lifecycle-mgmt/)

```pip3 install --upgrade nautobot-device-lifecycle-mgmt```

#### Check that the plugin will be installed for future upgrades.
To ensure Nautobot Device Life Cycle Management plugin is automatically re-installed during future
upgrades, create a file named local_requirements.txt (if not already existing) in the Nautobot root directory
(alongside requirements.txt) and list the nautobot-plugin-device-lifecycle-mgmt package:

First, check that the plugin is defined in the local_requirements.txt. 

```cat local_requirements.txt```

If not, add the plugin name to the requriements. 

```echo nautobot-device-lifecycle-mgmt >> local_requirements.txt```

#### Run Post Upgrade Steps
Once the configuration has been updated, run the post migration script as the Nautobot user

```nautobot-server post_upgrade```

This should run migrations for the plugin to be ready for use.

#### Restart Nautobot Services
As a user account that has privileges to restart services, restart the Nautobot services

```sudo systemctl restart nautobot nautobot-worker```

If you are on Nautobot >= 1.1.0 and have the RQ worker continuing on, also restart the RQ worker service.

```sudo systemctl restart nautobot-rq-worker```
> NOTE: If you have multiple workers defined, you will need to restart each worker process. For example
> `systemctl restart nautobot nautobot-worker@1 nautobot-worker@2`, etc...
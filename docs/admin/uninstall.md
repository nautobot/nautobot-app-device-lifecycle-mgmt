# Uninstall the App from Nautobot

## Uninstall Guide

!!! warning "Developer Note - Remove Me!"
    Detailed instructions on how to remove the app from Nautobot.

Remove the configuration you added in `nautobot_config.py` from `PLUGINS` & `PLUGINS_CONFIG`.

## Database Cleanup

!!! warning "Developer Note - Remove Me!"
    Beyond deleting tables, is there anything else that needs cleaning up, such as CFs, relationships, etc. if they're no longer desired?

Drop all tables from the plugin: `nautobot_plugin_device_lifecycle_mgmt*`.

Any cleanup operations to ensure the database is clean after the app is removed.

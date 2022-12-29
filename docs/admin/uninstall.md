# Uninstall the App from Nautobot

## Uninstall Guide

!!! warning "Developer Note - Remove Me!"
    Detailed instructions on how to remove the app from Nautobot.

Remove any related configuration you added in `nautobot_config.py` from `PLUGINS` & `PLUGINS_CONFIG`.

## Database Cleanup

!!! warning "Note - Remove related dependencies prior to dropping database"
    Prior to removing this plugin, ensure any related custom fields, relationships, or other dependencies should be removed from the app.

Drop all tables from the plugin: `nautobot_plugin_device_lifecycle_mgmt*`.

Any cleanup operations to ensure the database is clean after the app is removed.

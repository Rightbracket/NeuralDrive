*This chapter is for all users.*

# Updating NeuralDrive

NeuralDrive uses a LiveUSB deployment model. This means that system updates are typically applied by re-flashing the USB drive with a newer ISO image.

## Update Model

Unlike traditional operating systems that use package managers for updates, NeuralDrive is designed as an immutable system. This ensures that the core operating environment is always in a known, stable state.

## Upgrade Procedure

To upgrade to a new version:
1. **Back up data**: Backup models, configurations, and WebUI data from the persistence partition.
2. **Re-flash**: Use an ISO writer to flash the new version onto the USB drive.
3. **Initialize persistence**: Re-create the persistence partition on first boot.
4. **Restore data**: Copy the backed-up data back to the appropriate locations (optional).

> **Warning**: Re-flashing the USB drive destroys the persistence partition and all data stored on it. Always ensure a complete backup of critical data before proceeding with an upgrade.

## Backup Procedure

It is recommended to copy the following directories to an external drive or network location before re-flashing:
- `/var/lib/neuraldrive/`: Contains downloaded models and Open WebUI user data.
- `/etc/neuraldrive/`: Contains system configurations, TLS certificates, and the API key.

## Version Checking

To verify the current version of the system:
- **Command line**: `cat /etc/neuraldrive/version` (e.g., `dev-snapshot`).
- **System API**: Send a `GET` request to `/system/status` and check the `version` field.

## Future Plans

A specialized `neuraldrive-upgrade` tool is planned for future releases. This tool will automate the process of downloading and applying updates directly to the persistence partition without requiring a full re-flash.

[Writing the USB Drive](../getting-started/writing-usb.md)
[Storage Management](../models/storage.md)

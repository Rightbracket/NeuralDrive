*Audience: Admin*

# External Storage

NeuralDrive is designed to work with external storage devices for model persistence and data management. This is particularly useful for systems running from a read-only medium (CD) or for users who maintain a large library of models that exceed the size of a standard USB drive.

## Auto-Mounting

The system includes pre-configured `udev` rules that automatically detect and mount external storage devices (USB, SATA, etc.) as they are connected.

*   **Mount Point**: `/mnt/external/<LABEL>`
*   **Directory Name**: The drive's volume label is used as the directory name. If no label exists, the device identifier (e.g., `sdb1`) is used.

## Configuring External Model Storage

By default, models are stored in `/var/lib/neuraldrive/models/`. You can redirect this to an external drive using one of two methods.

### Method 1: Bind Mount (Recommended)

Edit `/etc/fstab` to mount your external storage directory directly over the default models directory. This is the most reliable method for ensuring persistence.

```bash
/mnt/external/MyModels/ollama /var/lib/neuraldrive/models/ none bind 0 0
```

### Method 2: Symlinking

Alternatively, you can create a symbolic link from the default location to the external drive.

```bash
# Stop the Ollama service
sudo systemctl stop ollama

# Move existing models to the external drive
sudo mv /var/lib/neuraldrive/models/* /mnt/external/MyModels/

# Create the symlink
sudo ln -s /mnt/external/MyModels/ /var/lib/neuraldrive/models

# Restart the service
sudo systemctl start ollama
```

## Use Cases

1.  **CD Mode with External Storage**: When running NeuralDrive from a CD, you can still have a persistent model library by connecting an external USB drive.
2.  **Shared Model Library**: Multiple NeuralDrive instances can share a single large external drive containing a comprehensive library of LLMs.
3.  **Supplementing USB Storage**: If your primary USB drive runs low on space, you can seamlessly add a second drive to expand your available model storage.

For more information on model storage and management, see [Storage Management](../models/storage.md) and [CD Mode vs USB Mode](cd-vs-usb.md).

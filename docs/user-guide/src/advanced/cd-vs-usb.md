*Audience: Everyone*

# CD Mode vs USB Mode

NeuralDrive's hybrid ISO image can be used in two distinct ways: as a live environment from a USB drive or as a read-only system from a CD/DVD. The choice of medium significantly impacts the features and persistence of the system.

## USB Mode (Recommended)

When NeuralDrive is flashed to a USB drive, it creates a persistence partition that allows for the full suite of features. This is the intended deployment method for most users.

*   **Persistence**: Models, system configurations, and user data are saved to the USB drive and survive reboots.
*   **Model Management**: Downloading and updating models via the WebUI or command line is fully supported.
*   **Performance**: USB 3.0+ provides acceptable I/O speeds for system operations.

## CD Mode

If the ISO is burned to a CD or DVD, or booted in an environment where the boot medium is read-only, NeuralDrive operates in a restricted live mode.

*   **Read-Only System**: All system changes are made to a `tmpfs` (RAM-based filesystem) and are lost upon reboot.
*   **Disabled Downloads**: Since there is no persistent storage on the disc, model downloads are disabled. Users will see a warning: "Downloads disabled — connect external storage."
*   **Stateless Security**: Every boot starts with a clean, known state, making it ideal for high-security environments where no data should remain on the hardware.

## Booting to RAM

For CD mode, a specialized "Copy to RAM" (toram) boot option is available in the boot menu. This loads the entire image into system memory, which has several benefits:

*   **Speed**: Operating purely from RAM is faster than reading from an optical drive.
*   **Drive Availability**: Once loaded, the CD can be ejected, freeing the drive for other uses.
*   **Hardware Compatibility**: Requires sufficient RAM (typically 16GB+) to hold both the system and the models.

## Comparison and Use Cases

| Feature | USB Mode | CD Mode |
| :--- | :--- | :--- |
| **Persistence** | Full | None (lost on reboot) |
| **Model Downloads** | Enabled | Disabled (unless external storage added) |
| **Encryption** | Supported | Not applicable |
| **Typical Use Case** | Permanent local LLM server | Evaluation, high-security workstations |

### When to Use Each

*   **USB**: Best for regular use, developing with LLMs locally, or setting up a dedicated server for a small team.
*   **CD**: Best for testing hardware compatibility, air-gapped security needs, or environments where the operating system must never be modified.

> **Tip**: If using CD mode but still needing persistent model storage, you can connect a separate USB or SATA drive. NeuralDrive will automatically detect and mount it. For more, see [External Storage](external-storage.md).

For the initial setup process on either medium, refer to [First Boot Setup](../getting-started/first-boot.md).

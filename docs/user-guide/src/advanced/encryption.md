*Audience: Admin*

# LUKS Encryption

NeuralDrive supports LUKS2 encryption for its persistence partition. This ensures that models, system configurations, and credentials stored on the USB drive are protected from unauthorized access if the physical medium is lost or stolen.

## What is Protected?

When encryption is enabled, it applies specifically to the persistence partition (typically labeled `persistence`). This partition stores:

*   **Models**: All LLMs downloaded via Ollama.
*   **Configs**: Network settings, API keys, and system customizations.
*   **WebUI Data**: User accounts and administrative settings.

## Enabling Encryption

There are two primary ways to enable LUKS encryption.

### 1. First-Boot Wizard

During the initial setup process, the first-boot wizard will present an option to "Enable Persistence Encryption." Selecting this option will prompt you to enter a passphrase that will be required to unlock the partition on every subsequent boot.

### 2. Build Configuration

For automated deployments or pre-configured images, you can enable encryption in the `neuraldrive-build.yaml` file:

```yaml
security:
  encrypt_persistent: true
```

## Boot Experience

When encryption is enabled, the system will pause during the boot sequence to prompt for the decryption passphrase. This occurs before any NeuralDrive services (including the WebUI) are started.

> **Warning**: If you lose your passphrase, the data on the persistence partition is unrecoverable. There is no password reset or recovery mechanism for LUKS-encrypted partitions.

## Performance Considerations

Using LUKS2 encryption introduces a minor overhead for disk I/O operations. However, because LLM inference is primarily bound by GPU or CPU performance and VRAM/RAM bandwidth, the impact on overall model performance is negligible for most users.

## Important Note: Destructive Operation

Enabling encryption for the first time on a drive that already contains data is a **destructive operation**. It will reformat the persistence partition. Ensure you back up any critical data before enabling this feature on an existing installation.

For more information on the first-time setup process, see [First Boot Setup](../getting-started/first-boot.md). To explore other security features, refer to [Security](../admin/security.md).

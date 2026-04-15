*This chapter is for contributors and maintainers.*

# Storage Architecture

NeuralDrive uses a hybrid storage model that combines an immutable base system with a persistent writable layer. This design ensures that the appliance remains stable over time while allowing for model storage and user data persistence.

## Partition Layout

The standard NeuralDrive image expects a 4-partition layout on the boot media (typically a USB drive or internal SSD):

1. **Partition 1 (EFI)**: FAT32. Contains the GRUB bootloader and EFI binaries.
2. **Partition 2 (Boot)**: Ext4. Contains the Linux kernel and initrd.
3. **Partition 3 (Live System)**: ISO9660 or SquashFS. Contains the compressed, read-only root filesystem.
4. **Partition 4 (Persistence)**: Ext4 or LUKS2-encrypted. Contains the `persistence` layer used by `live-boot`.

## Immutable Root (SquashFS)

The core operating system is stored in a highly compressed SquashFS image. During the boot process, this image is mounted as the read-only root (`/`). This ensures that:
- Accidental changes to system binaries are impossible.
- The system always boots into a known-good state.
- The disk footprint of the OS remains small.

## Persistence and OverlayFS

To allow for data persistence, NeuralDrive uses `overlayfs`. This kernel feature merges the read-only SquashFS layer with a writable directory on the persistence partition.

### Key Persistent Paths

While the entire filesystem can be made persistent, NeuralDrive is configured to prioritize specific directories:

- `/var/lib/neuraldrive/models/`: Stores the large LLM weights for Ollama.
- `/var/lib/neuraldrive/webui/`: Stores the Open WebUI database and user-uploaded documents.
- `/etc/neuraldrive/`: Stores system configuration, API keys, and TLS certificates.
- `/var/log/`: Persists system logs across reboots for troubleshooting.

## Model Storage Management

Because LLM models can be dozens of gigabytes in size, NeuralDrive handles model storage separately from the main OS updates. When a user downloads a model via the WebUI or System API, it is saved directly to the persistence partition. This means models survive system updates (re-flashing the SquashFS partition).

## Encryption (LUKS2)

For deployments requiring high security, the persistence partition can be encrypted using LUKS2. This is handled during the first-boot setup wizard. If encryption is enabled:
1. The user provides a passphrase.
2. The persistence partition is formatted as a LUKS2 volume.
3. The system adds the necessary `crypttab` entries to the initramfs to prompt for the password at boot.

> **Warning**: If the persistence partition is lost or corrupted, all downloaded models and user configurations will be deleted. Always ensure the system is shut down cleanly to prevent filesystem corruption on the writable layer.


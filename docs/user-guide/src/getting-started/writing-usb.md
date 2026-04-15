*This chapter is for everyone.*

# USB Writing

NeuralDrive is distributed as a hybrid ISO image. This format allows the same file to be written to USB drives or burned to physical optical media. Because NeuralDrive runs as a live system, your choice of writing method determines whether your settings and models persist across reboots.

**WARNING: Writing the NeuralDrive ISO to a USB drive or disk destroys all existing data on that device. Ensure you have backed up any important files before proceeding.**

## Recommended Method: Automated Flash Script

The most reliable way to create a NeuralDrive USB is using the provided `neuraldrive-flash.sh` script. This script automates the `dd` write process and the creation of the required persistence partition in a single step.

1. Locate the script in the `scripts/` directory of the NeuralDrive repository.
2. Identify your USB device path (e.g., `/dev/sdX` or `/dev/nvmeXn1`).
3. Run the script with root privileges:

```bash
sudo ./scripts/neuraldrive-flash.sh neuraldrive.iso /dev/sdX
```

The script performs the following actions:
- Writes the ISO image to the device using `dd` (bs=4M, conv=fsync).
- Automatically executes `prepare-usb.sh` to configure the persistence layer.

## Manual Writing Options

If you cannot use the automated script, choose one of the following manual methods.

### Option B: Manual dd and Persistence Setup

This method is standard for Linux and macOS users who prefer the command line.

1. Write the ISO to the USB device:
   ```bash
   sudo dd if=neuraldrive.iso of=/dev/sdX bs=4M conv=fsync status=progress
   ```
2. Once the write completes, initialize the persistence partition:
   ```bash
   sudo /usr/lib/neuraldrive/prepare-usb.sh /dev/sdX
   ```
   The `prepare-usb.sh` script creates an ext4 partition labeled "persistence" and writes the necessary `persistence.conf` file to enable union mounts.

### Option C: GUI Tools (Balena Etcher or Rufus)

You can use common graphical utilities like Balena Etcher or Rufus to write the ISO.

1. Select the `neuraldrive.iso` file in your GUI tool.
2. Select your USB drive and click Flash/Start.
3. **Important:** After the GUI tool finishes, you must still run the `prepare-usb.sh` script (see Option B, step 2) on a Linux system to enable data persistence. Without this step, your changes will be lost on every reboot.

### Option D: Ventoy

NeuralDrive is compatible with Ventoy. Simply copy the `neuraldrive.iso` file to your Ventoy-enabled USB drive. Note that persistence setup via Ventoy may require additional manual configuration not covered by the standard `prepare-usb.sh` script.

## Partition Layout

After a successful flash and persistence setup, your USB drive will have the following partition structure:

| Partition | Label | Type | Filesystem | Size | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | EFI | EFI System | FAT32 | 512 MiB | UEFI boot files |
| 2 | NBOOT | Linux | ext2 | 1 GiB | GRUB and kernel images |
| 3 | NSYSTEM | Linux | SquashFS | ~8 GiB | Read-only root filesystem |
| 4 | persistence | Linux | ext4 | Remaining | Persistent storage for models and settings |

## Verification

To verify your USB drive is ready:
1. Ensure the drive is recognized by your system.
2. Check that the "persistence" partition is present and labeled correctly.
3. Confirm that the drive is bootable in your system's UEFI settings.

## Note on CD/DVD Burning

NeuralDrive can be burned to physical media using any standard ISO burning tool (such as Brasero on Linux or Disk Utility on macOS). Note that physical discs are read-only; persistence features will not be available, and all data will be stored in RAM.

For instructions on what to do after your USB is ready, see [First Boot](first-boot.md).

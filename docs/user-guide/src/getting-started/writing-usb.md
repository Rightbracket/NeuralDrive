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

If you cannot use the automated script, choose one of the following manual methods based on your operating system.

### Linux: Manual dd

1. Identify your USB device:
   ```bash
   lsblk
   ```
   Look for your USB drive by size. It will appear as `/dev/sdX` or `/dev/nvmeXn1`. **Do not use a partition path** like `/dev/sdb1` — use the whole-disk device.

2. Unmount any mounted partitions on the device:
   ```bash
   sudo umount /dev/sdX*
   ```

3. Write the ISO to the USB device:
   ```bash
   sudo dd if=neuraldrive.iso of=/dev/sdX bs=4M conv=fsync status=progress
   ```

4. Initialize the persistence partition:
   ```bash
   sudo /usr/lib/neuraldrive/prepare-usb.sh /dev/sdX
   ```
   The `prepare-usb.sh` script creates an ext4 partition labeled "persistence" and writes the necessary `persistence.conf` file to enable union mounts.

### macOS: dd with diskutil

macOS uses different device paths and a slightly different `dd` syntax.

1. Identify your USB device:
   ```bash
   diskutil list
   ```
   Look for your USB drive by size. It will appear as `/dev/diskN` (e.g., `/dev/disk4`). **Do not use a partition path** like `/dev/disk4s1` — use the whole-disk device.

2. Unmount the USB drive (this does not eject it):
   ```bash
   diskutil unmountDisk /dev/diskN
   ```

3. Write the ISO using the raw device (`rdiskN`) for significantly faster writes:
   ```bash
   sudo dd if=neuraldrive.iso of=/dev/rdiskN bs=4m status=progress
   ```
   > **Note:** macOS `dd` uses lowercase `4m` (not `4M`), and `conv=fsync` is not supported. The raw device path `/dev/rdiskN` bypasses the buffer cache and is roughly 10x faster than `/dev/diskN`.

4. Eject the drive:
   ```bash
   diskutil eject /dev/diskN
   ```

5. **Persistence partition:** The `prepare-usb.sh` script requires Linux tools (`sfdisk`, `mkfs.ext4`) and cannot run directly on macOS. To set up persistence, choose one of:
   - **Boot NeuralDrive first:** Boot the USB on the target machine. On first boot, the system will detect the missing persistence partition and offer to create it.
   - **Use the Docker builder:** Pass the USB device into the builder container and run the script there.
   - **Use any Linux machine:** Mount the USB on a Linux system and run `sudo /usr/lib/neuraldrive/prepare-usb.sh /dev/sdX`.

### Windows: Rufus

[Rufus](https://rufus.ie/) is a free, open-source tool for writing ISO images on Windows.

1. Download and run Rufus.
2. Under **Device**, select your USB drive.
3. Under **Boot selection**, click **SELECT** and choose the `neuraldrive.iso` file.
4. Set **Partition scheme** to **GPT** and **Target system** to **UEFI**.
5. Click **START** and wait for the write to complete.

> **Note:** Rufus may offer to write in "ISO Image mode" or "DD Image mode." Either mode works. If you encounter boot issues, try DD Image mode.

6. **Persistence partition:** Rufus does not create the NeuralDrive persistence partition. After flashing, set up persistence using one of the methods described in the macOS section above (boot the target machine, use a Linux system, or use the Docker builder).

### Cross-Platform GUI: Balena Etcher

[Balena Etcher](https://etcher.balena.io/) works on Linux, macOS, and Windows.

1. Download and install Balena Etcher.
2. Click **Flash from file** and select the `neuraldrive.iso` file.
3. Click **Select target** and choose your USB drive.
4. Click **Flash** and wait for the write and verification to complete.

**Important:** Balena Etcher does not create the persistence partition. Follow the persistence setup instructions for your platform described above.

### Ventoy

NeuralDrive is compatible with [Ventoy](https://ventoy.net/). Simply copy the `neuraldrive.iso` file to your Ventoy-enabled USB drive. Note that persistence setup via Ventoy may require additional manual configuration not covered by the standard `prepare-usb.sh` script.

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

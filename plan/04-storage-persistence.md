# Implementation Plan: 04-storage-persistence.md — Partition Layout, Persistence & Model Storage

This document details the storage architecture for NeuralDrive, ensuring that model downloads and configurations persist across reboots on LiveUSB media.

## Section 1: Boot Media Detection

NeuralDrive must determine its boot environment early in the boot process.

- **Detection Script**: `/usr/lib/neuraldrive/detect-media.sh`
- **Configuration Output**: `/run/neuraldrive/media.conf`

```bash
#!/bin/bash
# NeuralDrive Media Detection Script

# Determine boot device from cmdline
BOOT_DEV=$(grep -o 'boot=[^ ]*' /proc/cmdline | cut -d= -f2)

# If no boot= is specified, find the device with label 'NeuralDrive'
if [[ -z "$BOOT_DEV" ]]; then
    BOOT_DEV=$(lsblk -d -n -o NAME,LABEL | grep 'NeuralDrive' | awk '{print $1}')
fi

IS_USB=false
IS_CD=false

if [[ $(cat /sys/block/${BOOT_DEV}/removable) == "1" ]]; then
    IS_USB=true
elif [[ $(cat /sys/block/${BOOT_DEV}/device/type) == "5" ]]; then
    IS_CD=true
fi

# Write config for later services
cat <<EOF > /run/neuraldrive/media.conf
NEURALDRIVE_BOOT_DEV="/dev/${BOOT_DEV}"
NEURALDRIVE_IS_USB=${IS_USB}
NEURALDRIVE_IS_CD=${IS_CD}
EOF
```

## Section 2: USB Partition Layout

NeuralDrive uses a GPT partition table.

### Layout Details
| # | Label | Type | Filesystem | Size | Purpose |
|---|-------|------|-----------|------|---------|
| 1 | EFI | EFI System | FAT32 | 512 MiB | UEFI boot |
| 2 | NBOOT | Linux | ext2 | 1 GiB | GRUB + kernel + initramfs |
| 3 | NSYSTEM | Linux | SquashFS | 8 GiB | Read-only root filesystem |
| 4 | persistence | Linux | ext4 | Remaining | Persistent data |

**Important**: Partition 4 must have the filesystem label `persistence` (exact, lowercase). This is required by live-boot for automatic persistence detection. The kernel boot parameter `persistence` must also be present in the GRUB configuration (see 01-base-system.md §4).

### Expansion Script
The persistence partition is created as a **post-dd step** after writing the ISO to USB. live-build produces a fixed-size ISO-hybrid image; the persistence partition is created in the remaining free space.

**Two-step USB setup:**

1. Write the ISO to USB:
```bash
sudo dd if=neuraldrive.iso of=/dev/sdX bs=4M conv=fsync status=progress
```

2. Create the persistence partition (run on the host, not the live system):
```bash
# Find the end of the ISO's partitions and create partition in remaining space
sudo parted /dev/sdX -- mkpart primary ext4 -1 100%
sudo mkfs.ext4 -L persistence /dev/sdXN   # where N is the new partition number
sudo mount /dev/sdXN /mnt
sudo mkdir -p /mnt/neuraldrive/{models,config,logs,home}
sudo mkdir -p /mnt/neuraldrive/models/{manifests,blobs}
cat <<'EOF' | sudo tee /mnt/persistence.conf
/var/lib/neuraldrive  union
/etc/neuraldrive      union
/var/log/neuraldrive  union
/home                 union
EOF
sudo umount /mnt
```

Alternatively, the NeuralDrive toolkit (09-image-toolkit.md) provides a `neuraldrive-flash` helper script that automates both steps.

**Note**: Re-flashing a new ISO image to the USB will destroy ALL partitions, including the persistence partition. Users must back up their persistent data before upgrading. See the upgrade procedure below.

## Section 3: Persistence Implementation

NeuralDrive uses the `live-boot` persistence mechanism.

- **Mechanism**: `overlayfs` with the persistence partition as the upper layer.
- **Partition Label**: Must be `persistence` (exact, lowercase) for live-boot auto-detection.
- **Persistence Configuration**: `persistence.conf` placed at the **root of the persistence partition filesystem** (not in `/etc/`).
- **Boot Parameter**: The GRUB kernel command line must include `persistence` (see 01-base-system.md §4).

### Content of `persistence.conf`
This file is placed on the root of the persistence partition (e.g., after mounting the partition at `/mnt`, the file would be `/mnt/persistence.conf`):
```text
/var/lib/neuraldrive  union
/etc/neuraldrive      union
/var/log/neuraldrive  union
/home                 union
```

## Section 4: Model Storage Management

Models are stored in `/var/lib/neuraldrive/models/` which is part of the persistent `persistence` partition (mounted via live-boot overlayfs).

- **Storage Monitoring**: `neuraldrive-storage-monitor.service`
- **Thresholds**:
  - **80%**: Warning log entry.
  - **90%**: Critical alert in the dashboard.
  - **95%**: API blocks further downloads.

### Storage Reporting Command
```bash
# Get summary of model sizes and available space
du -sh /var/lib/neuraldrive/models/*
df -h /var/lib/neuraldrive
```

## Section 5: External Storage Support

Drives are auto-mounted via a udev rule triggering a systemd unit.

### Mount Strategy
External drives are mounted to `/mnt/external/<LABEL>`.
If `EXTERNAL_MODEL_PATH` is set in `/etc/neuraldrive/storage.conf`, a bind-mount is created:

```bash
# Mount external model storage
mount --bind /mnt/external/models_drive/models /var/lib/neuraldrive/models
```

## Section 6: CD/DVD Boot Mode (Non-Persistent)

If `NEURALDRIVE_IS_CD=true`:
- `/var` is mounted as `tmpfs` (50% of RAM).
- Model downloads are disabled in the TUI/dashboard.
- User is prompted to connect a USB drive for persistence.

## Section 7: Storage Security (Optional LUKS2)

Users can choose to encrypt the persistence partition during the first-boot setup.

```bash
# Format with LUKS2
cryptsetup luksFormat --type luks2 /dev/sdb4
cryptsetup open /dev/sdb4 neuraldrive_data
mkfs.ext4 /dev/mapper/neuraldrive_data
```

## Section 8: Disk I/O Optimization

- **`noatime`**: Reduces wear by not updating access times.
- **`commit=60`**: Reduces wear by batching writes every 60 seconds.
- **`zram`**: Used for swap to prevent wearing out the USB with paging.

### Mount Flags
The persistence partition is mounted automatically by live-boot's overlayfs mechanism using the directories specified in `persistence.conf`. The following mount options are applied via the live-boot configuration:
- **`noatime`**: Reduces wear by not updating access times.
- **`commit=60`**: Reduces wear by batching writes every 60 seconds.

These are configured by including a `fstab` fragment in the persistence setup or by passing mount options to live-boot. The persistence partition itself does not appear in `/etc/fstab`; live-boot manages its mounting.

### zram Swap Configuration
NeuralDrive uses zram (compressed RAM swap) instead of on-disk swap to avoid USB wear.

Create `/usr/lib/neuraldrive/setup-zram.sh`:
```bash
#!/bin/bash
# Configure zram for compressed swap
# Uses 50% of RAM for compressed swap (effective ~2x due to compression)

TOTAL_MEM_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
ZRAM_SIZE_KB=$((TOTAL_MEM_KB / 2))

modprobe zram num_devices=1
echo lz4 > /sys/block/zram0/comp_algorithm
echo "${ZRAM_SIZE_KB}K" > /sys/block/zram0/disksize
mkswap /dev/zram0
swapon -p 100 /dev/zram0

echo "zram swap configured: ${ZRAM_SIZE_KB}KB (compressed)"
```

systemd service (`neuraldrive-zram.service`):
```ini
[Unit]
Description=NeuralDrive zram Swap
DefaultDependencies=no
After=local-fs.target

[Service]
Type=oneshot
ExecStart=/usr/lib/neuraldrive/setup-zram.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

### Partition Creation Commands (for USB image writing tools)
These are the commands used by the post-dd setup step (or the `neuraldrive-flash` helper from 09-image-toolkit.md) to create the persistence partition:

```bash
#!/bin/bash
# /usr/lib/neuraldrive/prepare-usb.sh
# Run on the HOST after dd'ing the ISO to USB.
# Usage: sudo ./prepare-usb.sh /dev/sdX

set -e

DEV="$1"
if [ -z "$DEV" ]; then
    echo "Usage: prepare-usb.sh /dev/sdX"
    exit 1
fi

# Safety check — ensure this looks like a NeuralDrive USB
if ! lsblk -no LABEL "$DEV"* 2>/dev/null | grep -q "NeuralDrive"; then
    echo "Error: $DEV does not appear to contain a NeuralDrive image."
    exit 1
fi

# Create persistence partition in remaining free space
echo "Creating persistence partition..."
sudo parted "$DEV" -- mkpart primary ext4 -1 100%
PART_NUM=$(lsblk -ln -o NAME "$DEV" | tail -1)
PART_DEV="/dev/$PART_NUM"

# Format with label 'persistence' (required by live-boot)
sudo mkfs.ext4 -L persistence -O ^has_journal -m 1 "$PART_DEV"

# Re-enable journal in writeback mode for performance
sudo tune2fs -o journal_data_writeback -J size=64 "$PART_DEV"

# Mount and set up persistence.conf + directory structure
sudo mount "$PART_DEV" /mnt
cat <<'EOF' | sudo tee /mnt/persistence.conf
/var/lib/neuraldrive  union
/etc/neuraldrive      union
/var/log/neuraldrive  union
/home                 union
EOF
sudo mkdir -p /mnt/neuraldrive/{models,config,logs,home}
sudo mkdir -p /mnt/neuraldrive/models/{manifests,blobs}
sudo umount /mnt

echo "Persistence partition created and configured on $PART_DEV"
echo "USB is ready to boot."
```

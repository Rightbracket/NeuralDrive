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
| 4 | NDATA | Linux | ext4 | Remaining | Persistent data |

### Expansion Script
On the first boot, NeuralDrive expands the `NDATA` partition to use the full disk.

```bash
# Expand NDATA partition to fill USB
PART_NUM=4
DEV_PATH="/dev/sdb" # Example path
parted ${DEV_PATH} resizepart ${PART_NUM} 100%
resize2fs ${DEV_PATH}${PART_NUM}
```

## Section 3: Persistence Implementation

NeuralDrive uses the `live-boot` persistence mechanism.

- **Mechanism**: `overlayfs` with `NDATA` as the upper layer.
- **Persistence Configuration**: `/etc/persistence.conf` (on the NDATA partition).

### Content of `persistence.conf`
```text
/var/lib/neuraldrive  union
/etc/neuraldrive      union
/var/log/neuraldrive  union
/home                 union
```

## Section 4: Model Storage Management

Models are stored in `/var/lib/neuraldrive/models/` which is part of the persistent `NDATA` partition.

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

Users can choose to encrypt the `NDATA` partition during the first-boot setup.

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

### Mount Flags in `/etc/fstab` (on NDATA)
```text
LABEL=NDATA /var/lib/neuraldrive ext4 defaults,noatime,commit=60,data=writeback 0 2
```

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
These are the exact `sgdisk` commands used by the first-boot initialization to set up the USB partition layout:

```bash
#!/bin/bash
# /usr/lib/neuraldrive/init-partitions.sh
# Called during first-boot to create NDATA partition on remaining USB space

DEV="$1"  # e.g., /dev/sda

# Verify this is the boot device and has free space
if [ -z "$DEV" ]; then
    echo "Usage: init-partitions.sh /dev/sdX"
    exit 1
fi

# Get the end of the last partition
LAST_END=$(sgdisk -p "$DEV" | tail -1 | awk '{print $3}')
DISK_END=$(sgdisk -p "$DEV" | grep "last usable sector" | awk '{print $NF}')

if [ "$LAST_END" -ge "$DISK_END" ]; then
    echo "No free space available for NDATA partition."
    exit 0
fi

# Create partition 4 (NDATA) using remaining space
sgdisk -n 4:0:0 -t 4:8300 -c 4:"NDATA" "$DEV"
partprobe "$DEV"
sleep 2

# Format as ext4 with optimized settings
mkfs.ext4 -L NDATA -O ^has_journal -m 1 "${DEV}4"

# Re-enable journal in writeback mode for performance
tune2fs -o journal_data_writeback -J size=64 "${DEV}4"

# Create directory structure
mount "${DEV}4" /mnt
mkdir -p /mnt/neuraldrive/{models,config,logs,home}
mkdir -p /mnt/neuraldrive/models/{manifests,blobs}
umount /mnt

echo "NDATA partition created and formatted on ${DEV}4"
```

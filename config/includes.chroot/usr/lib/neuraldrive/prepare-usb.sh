#!/bin/bash
set -e

DEV="$1"
if [ -z "$DEV" ]; then
    echo "Usage: prepare-usb.sh /dev/sdX"
    exit 1
fi

if ! lsblk -no LABEL "$DEV"* 2>/dev/null | grep -q "NeuralDrive"; then
    echo "Error: $DEV does not appear to contain a NeuralDrive image."
    exit 1
fi

echo "Creating persistence partition..."
sudo parted "$DEV" -- mkpart primary ext4 -1 100%
PART_NUM=$(lsblk -ln -o NAME "$DEV" | tail -1)
PART_DEV="/dev/$PART_NUM"

sudo mkfs.ext4 -L persistence -O ^has_journal -m 1 "$PART_DEV"
sudo tune2fs -o journal_data_writeback -J size=64 "$PART_DEV"

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

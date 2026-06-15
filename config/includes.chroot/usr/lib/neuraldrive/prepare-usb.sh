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

# Pre-seed the rw/ + work/ upperdir structure for each `union` entry above.
# live-boot mounts each union entry as overlayfs(upperdir=<partition>/<entry>/rw,
# workdir=<partition>/<entry>/work). Files created at the partition root
# (e.g., /mnt/models) would be invisible inside the overlay — only files under
# the rw/ subtree of the matching entry will appear in the live filesystem.
sudo mkdir -p \
    /mnt/var/lib/neuraldrive/rw/models/manifests \
    /mnt/var/lib/neuraldrive/rw/models/blobs \
    /mnt/var/lib/neuraldrive/rw/ollama/.ollama \
    /mnt/var/lib/neuraldrive/rw/config \
    /mnt/var/lib/neuraldrive/rw/webui \
    /mnt/var/lib/neuraldrive/work \
    /mnt/var/log/neuraldrive/rw \
    /mnt/var/log/neuraldrive/work \
    /mnt/etc/neuraldrive/rw \
    /mnt/etc/neuraldrive/work \
    /mnt/home/rw \
    /mnt/home/work
sudo umount /mnt

echo "Persistence partition created and configured on $PART_DEV"
echo "USB is ready to boot."

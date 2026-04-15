#!/bin/bash
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
    echo "Error: Must run as root."
    exit 1
fi

ISO="$1"
DEV="$2"

if [ -z "$ISO" ] || [ -z "$DEV" ]; then
    echo "Usage: neuraldrive-flash <iso-file> <device>"
    echo "Example: neuraldrive-flash neuraldrive-2026.04.iso /dev/sdb"
    exit 1
fi

if [ ! -f "$ISO" ]; then
    echo "Error: ISO file not found: $ISO"
    exit 1
fi

if [ ! -b "$DEV" ]; then
    echo "Error: $DEV is not a block device."
    exit 1
fi

echo "WARNING: This will DESTROY ALL DATA on $DEV"
echo "Device: $(lsblk -dno MODEL,SIZE "$DEV" 2>/dev/null || echo 'unknown')"
read -r -p "Continue? [y/N] " CONFIRM
if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "Aborted."
    exit 0
fi

echo "Writing ISO to $DEV..."
dd if="$ISO" of="$DEV" bs=4M conv=fsync status=progress
sync

echo "Creating persistence partition..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PREPARE_SCRIPT="${SCRIPT_DIR}/../config/includes.chroot/usr/lib/neuraldrive/prepare-usb.sh"
if [ -f "$PREPARE_SCRIPT" ]; then
    bash "$PREPARE_SCRIPT" "$DEV"
else
    echo "Warning: prepare-usb.sh not found. Persistence partition not created."
    echo "Run prepare-usb.sh manually after flashing."
fi

echo ""
echo "NeuralDrive has been written to $DEV"
echo "You can now boot from this device."

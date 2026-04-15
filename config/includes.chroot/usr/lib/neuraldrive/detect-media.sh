#!/bin/bash
mkdir -p /run/neuraldrive

BOOT_DEV=$(grep -o 'boot=[^ ]*' /proc/cmdline | cut -d= -f2)

if [ -z "$BOOT_DEV" ]; then
    BOOT_DEV=$(lsblk -d -n -o NAME,LABEL | grep 'NeuralDrive' | awk '{print $1}')
fi

IS_USB=false
IS_CD=false

if [ -n "$BOOT_DEV" ]; then
    REMOVABLE=$(cat "/sys/block/${BOOT_DEV}/removable" 2>/dev/null || echo "0")
    DEV_TYPE=$(cat "/sys/block/${BOOT_DEV}/device/type" 2>/dev/null || echo "0")

    if [ "$REMOVABLE" = "1" ]; then
        IS_USB=true
    elif [ "$DEV_TYPE" = "5" ]; then
        IS_CD=true
    fi
fi

cat <<EOF > /run/neuraldrive/media.conf
NEURALDRIVE_BOOT_DEV="/dev/${BOOT_DEV}"
NEURALDRIVE_IS_USB=${IS_USB}
NEURALDRIVE_IS_CD=${IS_CD}
EOF

#!/bin/bash
set -euo pipefail

CONFIG="${1:-}"
OUTPUT_DIR="./output"
mkdir -p "$OUTPUT_DIR"

ISO_FILE=$(find . -maxdepth 1 -name '*.iso' -print -quit)
if [ -z "$ISO_FILE" ]; then
    echo "Error: No ISO file found."
    exit 1
fi

# Version derived from build.sh via includes.chroot; read it back for filename
if [ -f config/includes.chroot/etc/neuraldrive/version ]; then
    ND_VERSION="$(cat config/includes.chroot/etc/neuraldrive/version)"
elif [ -n "${NEURALDRIVE_VERSION:-}" ]; then
    ND_VERSION="$NEURALDRIVE_VERSION"
else
    ND_VERSION="dev-$(date +%Y.%m.%d)-$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')"
fi

FILENAME="neuraldrive-${ND_VERSION}.iso"
if [ -n "$CONFIG" ] && command -v yq &>/dev/null; then
    CUSTOM_NAME=$(yq '.neuraldrive.output.filename' "$CONFIG" 2>/dev/null)
    if [ "$CUSTOM_NAME" != "null" ] && [ -n "$CUSTOM_NAME" ]; then
        FILENAME="$CUSTOM_NAME"
    fi
fi

mv "$ISO_FILE" "${OUTPUT_DIR}/${FILENAME}"

cd "$OUTPUT_DIR"
sha256sum "$FILENAME" > SHA256SUMS

echo "ISO: ${OUTPUT_DIR}/${FILENAME}"
echo "SHA256: $(cat SHA256SUMS)"

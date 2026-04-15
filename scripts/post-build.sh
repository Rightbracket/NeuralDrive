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

FILENAME="neuraldrive-$(date +%Y.%m).iso"
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

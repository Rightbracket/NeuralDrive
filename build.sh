#!/bin/bash
# NeuralDrive Build Script
# Builds a LiveCD/LiveUSB ISO image for LLM inference.
#
# Usage:
#   ./build.sh                    # Standard build
#   ./build.sh neuraldrive-build.yaml  # Custom config build
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${1:-}"
OUTPUT_DIR="${SCRIPT_DIR}/output"

echo "============================================"
echo "  NeuralDrive Image Builder"
echo "============================================"
echo ""

# --- Pre-flight checks ---
if [ "$(id -u)" -ne 0 ]; then
    echo "Error: This script must be run as root (or via sudo)."
    echo "Usage: sudo ./build.sh"
    exit 1
fi

if ! command -v lb &>/dev/null; then
    echo "Error: live-build is not installed."
    echo "Install with: sudo apt install -y live-build"
    exit 1
fi

# --- Custom config support ---
if [ -n "$CONFIG_FILE" ]; then
    if [ ! -f "$CONFIG_FILE" ]; then
        echo "Error: Config file not found: $CONFIG_FILE"
        exit 1
    fi
    echo "Using custom config: $CONFIG_FILE"
    "${SCRIPT_DIR}/scripts/validate-config.sh" "$CONFIG_FILE"
    "${SCRIPT_DIR}/scripts/apply-branding.sh" "$CONFIG_FILE"
fi

# --- Clean previous build ---
echo "Cleaning previous build artifacts..."
lb clean --all 2>/dev/null || true

# --- Configure live-build ---
echo "Configuring live-build..."
lb config \
    --distribution bookworm \
    --architectures amd64 \
    --binary-images iso-hybrid \
    --bootloaders "grub-efi,grub-pc" \
    --debian-installer none \
    --archive-areas "main contrib non-free non-free-firmware" \
    --apt-recommends false \
    --linux-packages "linux-image-amd64" \
    --iso-volume "NeuralDrive" \
    --iso-application "NeuralDrive Inference Server" \
    --iso-publisher "NeuralDrive Project"

# --- Build the image ---
echo ""
echo "Building NeuralDrive image..."
echo "This will take 30-90 minutes depending on network speed and CPU."
echo ""
lb build

# --- Post-processing ---
echo ""
echo "Post-processing..."
mkdir -p "$OUTPUT_DIR"

ISO_FILE=$(find . -maxdepth 1 -name '*.iso' -print -quit)
if [ -z "$ISO_FILE" ]; then
    echo "Error: No ISO file found after build."
    exit 1
fi

# Move ISO to output directory
FINAL_NAME="neuraldrive-$(date +%Y.%m).iso"
mv "$ISO_FILE" "${OUTPUT_DIR}/${FINAL_NAME}"

# Generate checksums
cd "$OUTPUT_DIR"
sha256sum "$FINAL_NAME" > SHA256SUMS
echo ""
echo "============================================"
echo "  Build complete!"
echo "  Image: ${OUTPUT_DIR}/${FINAL_NAME}"
echo "  SHA256: $(cat SHA256SUMS)"
echo "============================================"
echo ""
echo "To write to USB:"
echo "  sudo dd if=${OUTPUT_DIR}/${FINAL_NAME} of=/dev/sdX bs=4M conv=fsync status=progress"
echo "  sudo ./scripts/prepare-usb.sh /dev/sdX"

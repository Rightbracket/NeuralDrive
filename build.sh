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

# --- Derive version ---
# CalVer: YYYY.MM.REVISION where REVISION = total release count (never resets)
# Priority: NEURALDRIVE_VERSION env > exact git tag > dev fallback
if [ -n "${NEURALDRIVE_VERSION:-}" ]; then
    ND_VERSION="$NEURALDRIVE_VERSION"
elif command -v git &>/dev/null && git describe --exact-match --tags HEAD 2>/dev/null | grep -qE '^v[0-9]+\.[0-9]+\.[0-9]+$'; then
    ND_VERSION="$(git describe --exact-match --tags HEAD | sed 's/^v//')"
else
    ND_VERSION="dev-$(date +%Y.%m.%d)-$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')"
fi
echo "Version: ${ND_VERSION}"

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
    --linux-packages "linux-image" \
    --compression xz \
    --iso-volume "NeuralDrive" \
    --iso-application "NeuralDrive Inference Server" \
    --iso-publisher "NeuralDrive Project"

# --- Build the image ---
echo ""
echo "Building NeuralDrive image..."
echo "This will take 30-90 minutes depending on network speed and CPU."
echo ""

mkdir -p config/includes.chroot/etc/neuraldrive
echo "$ND_VERSION" > config/includes.chroot/etc/neuraldrive/version

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

FINAL_NAME="neuraldrive-${ND_VERSION}.iso"
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

#!/bin/bash
set -euo pipefail

CONFIG="$1"
if [ -z "$CONFIG" ]; then
    echo "Usage: apply-branding.sh <config.yaml>"
    exit 1
fi

HOSTNAME=$(yq '.neuraldrive.hostname' "$CONFIG" 2>/dev/null)
NAME=$(yq '.neuraldrive.name' "$CONFIG" 2>/dev/null)
TITLE=$(yq '.neuraldrive.webui.branding.title' "$CONFIG" 2>/dev/null)
SSH_ENABLED=$(yq '.neuraldrive.security.ssh_enabled // false' "$CONFIG" 2>/dev/null)
NVIDIA=$(yq '.neuraldrive.gpu.nvidia // true' "$CONFIG" 2>/dev/null)
AMD=$(yq '.neuraldrive.gpu.amd // false' "$CONFIG" 2>/dev/null)
INTEL=$(yq '.neuraldrive.gpu.intel // false' "$CONFIG" 2>/dev/null)

if [ "$HOSTNAME" != "null" ] && [ -n "$HOSTNAME" ]; then
    echo "$HOSTNAME" > config/includes.chroot/etc/hostname
    echo "Hostname set to: $HOSTNAME"
fi

if [ "$TITLE" != "null" ] && [ -n "$TITLE" ]; then
    sed -i "s/WEBUI_NAME=.*/WEBUI_NAME=$TITLE/" config/includes.chroot/etc/neuraldrive/webui.env 2>/dev/null || true
    echo "WebUI title set to: $TITLE"
fi

if [ "$NVIDIA" = "false" ]; then
    rm -f config/package-lists/gpu-nvidia.list.chroot
    echo "NVIDIA drivers excluded."
fi

if [ "$AMD" = "false" ]; then
    rm -f config/package-lists/gpu-amd.list.chroot
    rm -f config/archives/rocm.list.chroot
    echo "AMD ROCm excluded."
fi

if [ "$INTEL" = "false" ]; then
    rm -f config/package-lists/gpu-intel.list.chroot
    echo "Intel Arc drivers excluded."
fi

EXTRA_PKGS=$(yq '.neuraldrive.system.extra_packages[]' "$CONFIG" 2>/dev/null || true)
if [ -n "$EXTRA_PKGS" ]; then
    echo "$EXTRA_PKGS" > config/package-lists/custom-extras.list.chroot
    echo "Extra packages added: $(echo "$EXTRA_PKGS" | tr '\n' ' ')"
fi

echo "Branding applied."

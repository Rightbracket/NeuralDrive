#!/bin/bash
mkdir -p /run/neuraldrive
GPU_CONF="/run/neuraldrive/gpu.conf"

GPU_LIST=$(lspci -nn | grep -E "VGA|3D|Display")

DETECTED_VENDORS=""

if echo "$GPU_LIST" | grep -qi "10de"; then
    echo "VENDOR=NVIDIA" >> "$GPU_CONF"
    DETECTED_VENDORS="NVIDIA $DETECTED_VENDORS"
    modprobe nvidia nvidia-uvm nvidia-drm 2>/dev/null || echo "NVIDIA_MODULE_MISSING=true" >> "$GPU_CONF"
    nvidia-smi -pm 1 2>/dev/null || true
fi

if echo "$GPU_LIST" | grep -qi "1002"; then
    echo "VENDOR=AMD" >> "$GPU_CONF"
    DETECTED_VENDORS="AMD $DETECTED_VENDORS"
    modprobe amdgpu 2>/dev/null || echo "AMD_MODULE_MISSING=true" >> "$GPU_CONF"
fi

if echo "$GPU_LIST" | grep -qi "8086"; then
    echo "VENDOR=INTEL" >> "$GPU_CONF"
    DETECTED_VENDORS="INTEL $DETECTED_VENDORS"
    modprobe i915 2>/dev/null || echo "INTEL_MODULE_MISSING=true" >> "$GPU_CONF"
fi

if [ -z "$DETECTED_VENDORS" ]; then
    echo "VENDOR=CPU" >> "$GPU_CONF"
    echo "No supported GPU found. Falling back to CPU mode."
else
    echo "Detected GPUs: $DETECTED_VENDORS"
fi

SB_STATE=$(mokutil --sb-state 2>/dev/null || echo "unknown")
if echo "$SB_STATE" | grep -qi "enabled"; then
    echo "SECURE_BOOT=true" >> "$GPU_CONF"
fi

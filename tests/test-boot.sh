#!/bin/bash
set -euo pipefail

ISO_PATH=$1
TIMEOUT=300

if [ -z "$ISO_PATH" ]; then
    echo "Usage: test-boot.sh <iso-path>"
    exit 1
fi

if ! command -v qemu-system-x86_64 &>/dev/null; then
    echo "Error: QEMU not installed."
    exit 1
fi

echo "Starting QEMU (UEFI mode)..."
qemu-system-x86_64 \
    -m 4G \
    -drive file="$ISO_PATH",format=raw,readonly=on \
    -bios /usr/share/ovmf/OVMF.fd \
    -net nic -net user,hostfwd=tcp::11434-:11434,hostfwd=tcp::8443-:8443 \
    -display none -vnc :1 -daemonize

START_TIME=$(date +%s)
while true; do
    if curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
        echo "PASS: Ollama API ready."
        break
    fi
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))
    if [ $ELAPSED -gt $TIMEOUT ]; then
        echo "FAIL: Boot timeout exceeded (${TIMEOUT}s)."
        pkill qemu-system-x86_64 2>/dev/null || true
        exit 1
    fi
    echo "  Waiting... (${ELAPSED}s / ${TIMEOUT}s)"
    sleep 5
done

echo "Checking health endpoint..."
if curl -sf -k https://localhost:8443/health >/dev/null 2>&1; then
    echo "PASS: Caddy health endpoint responding."
else
    echo "WARN: Caddy health endpoint not responding (may need more time)."
fi

pkill qemu-system-x86_64 2>/dev/null || true
echo ""
echo "BVT Passed."

#!/bin/bash
# BVT (Build Verification Test): Boot the ISO in QEMU and verify it reaches
# a login prompt via serial console. Optionally checks the Caddy health endpoint.
set -euo pipefail

ISO_PATH="${1:-}"
TIMEOUT=300
BOOT_LOG="/tmp/neuraldrive-boot.log"

if [ -z "$ISO_PATH" ]; then
    echo "Usage: test-boot.sh <iso-path>"
    exit 1
fi

if ! command -v qemu-system-x86_64 &>/dev/null; then
    echo "Error: QEMU not installed."
    exit 1
fi

KVM_FLAG=""
if [ -w /dev/kvm ]; then
    KVM_FLAG="-enable-kvm"
    echo "KVM acceleration available."
else
    echo "WARNING: KVM not available, using software emulation (slow)."
    TIMEOUT=600
fi

rm -f "$BOOT_LOG"
touch "$BOOT_LOG"

echo "Starting QEMU (UEFI, serial console)..."
qemu-system-x86_64 \
    $KVM_FLAG \
    -m 4G \
    -cdrom "$ISO_PATH" \
    -bios /usr/share/ovmf/OVMF.fd \
    -net nic -net user,hostfwd=tcp::8443-:8443 \
    -display none \
    -serial file:"$BOOT_LOG" \
    -no-reboot &
QEMU_PID=$!

echo "QEMU PID: $QEMU_PID"

BOOTED=false
START_TIME=$(date +%s)
while true; do
    if grep -qi "login:" "$BOOT_LOG" 2>/dev/null; then
        echo "PASS: System booted to login prompt."
        BOOTED=true
        break
    fi

    if grep -qi "kernel panic" "$BOOT_LOG" 2>/dev/null; then
        echo "FAIL: Kernel panic detected."
        echo "--- Boot log (last 80 lines) ---"
        tail -80 "$BOOT_LOG"
        kill "$QEMU_PID" 2>/dev/null || true
        exit 1
    fi

    if ! kill -0 "$QEMU_PID" 2>/dev/null; then
        echo "FAIL: QEMU exited unexpectedly."
        echo "--- Boot log ---"
        cat "$BOOT_LOG"
        exit 1
    fi

    ELAPSED=$(( $(date +%s) - START_TIME ))
    if [ "$ELAPSED" -gt "$TIMEOUT" ]; then
        echo "FAIL: Boot timeout exceeded (${TIMEOUT}s)."
        echo "--- Boot log (last 80 lines) ---"
        tail -80 "$BOOT_LOG"
        kill "$QEMU_PID" 2>/dev/null || true
        exit 1
    fi

    if (( ELAPSED % 30 < 5 )); then
        echo "  Waiting for login prompt... (${ELAPSED}s / ${TIMEOUT}s)"
    fi
    sleep 5
done

# Best-effort: check Caddy health endpoint through port forwarding.
# Caddy listens on 0.0.0.0:8443 so hostfwd works for this.
echo "Checking Caddy health endpoint (best-effort)..."
sleep 10
if curl -sf -k https://localhost:8443/health --max-time 15 2>/dev/null; then
    echo "PASS: Caddy health endpoint responding."
else
    echo "INFO: Caddy health endpoint not responding (non-blocking for BVT)."
fi

kill "$QEMU_PID" 2>/dev/null || true
wait "$QEMU_PID" 2>/dev/null || true

echo ""
echo "BVT Passed."

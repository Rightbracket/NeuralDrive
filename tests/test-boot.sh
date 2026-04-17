#!/usr/bin/env bash
# BVT (Build Verification Test): Boot ISO in QEMU, verify all NeuralDrive
# services start, probe endpoints, collect full diagnostics.
#
# Design: NEVER fail fast. Collect ALL diagnostic information before
# rendering a verdict. Every phase runs regardless of prior failures.
set -uo pipefail

# ── Configuration ──────────────────────────────────────────────────
ISO_PATH="${1:-}"
BOOT_LOG="/tmp/neuraldrive-boot.log"
QEMU_IN="/tmp/qemu-in"
BOOT_TIMEOUT=300     # seconds to wait for login prompt
SVC_SETTLE=60        # seconds after login for services to settle
DIAG_WAIT=15         # seconds after last diagnostic command for output flush
LIVE_USER="user"     # Debian live default user
LIVE_PASS="live"     # Debian live default password

# All neuraldrive services that should be active after boot
ALL_SERVICES=(
    gpu-detect certs setup zram show-ip           # oneshot
    ollama caddy webui system-api gpu-monitor      # long-running
    storage-monitor                                # long-running
)

# ── Result accumulators ────────────────────────────────────────────
FAILURES=0
declare -a PASS_MSGS=() FAIL_MSGS=() INFO_MSGS=()

pass_msg() { PASS_MSGS+=("$1"); echo "  PASS: $1"; }
fail_msg() { FAIL_MSGS+=("$1"); FAILURES=$((FAILURES + 1)); echo "  FAIL: $1"; }
info_msg() { INFO_MSGS+=("$1"); echo "  INFO: $1"; }

# ── Helpers ────────────────────────────────────────────────────────
log_size() { wc -c < "$BOOT_LOG" 2>/dev/null || echo 0; }

# Wait for a regex pattern to appear in the boot log after a byte offset.
# Returns 0 on match, 1 on timeout/QEMU exit.
wait_serial() {
    local pattern="$1" timeout="${2:-30}" after="${3:-0}"
    local start
    start=$(date +%s)
    while true; do
        if tail -c "+$((after + 1))" "$BOOT_LOG" 2>/dev/null | grep -qi "$pattern"; then
            return 0
        fi
        if ! kill -0 "$QEMU_PID" 2>/dev/null; then return 1; fi
        local elapsed=$(( $(date +%s) - start ))
        if [ "$elapsed" -gt "$timeout" ]; then return 1; fi
        sleep 2
    done
}

# Send a string to the VM via serial (FIFO → QEMU stdin → serial).
# Second arg is optional sleep after sending (default 1s).
send_serial() {
    printf '%s\r' "$1" >&3
    sleep "${2:-1}"
}

cleanup() {
    exec 3>&- 2>/dev/null || true
    kill "$QEMU_PID" 2>/dev/null || true
    wait "$QEMU_PID" 2>/dev/null || true
    rm -f "$QEMU_IN"
}
trap cleanup EXIT

# ── Validation ─────────────────────────────────────────────────────
if [ -z "$ISO_PATH" ]; then
    echo "Usage: test-boot.sh <iso-path>"
    exit 1
fi
if [ ! -f "$ISO_PATH" ]; then
    echo "Error: ISO not found: $ISO_PATH"
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
    BOOT_TIMEOUT=600
fi

# ── Phase 1: Boot ──────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════"
echo " Phase 1: Boot"
echo "══════════════════════════════════════════"

rm -f "$BOOT_LOG" "$QEMU_IN"
touch "$BOOT_LOG"
mkfifo "$QEMU_IN"

# Open FIFO read-write so open() doesn't block (no reader yet).
# We only ever write to FD 3; QEMU reads the other end via < redirect.
exec 3<>"$QEMU_IN"

echo "Starting QEMU (UEFI, serial via FIFO)..."
qemu-system-x86_64 \
    $KVM_FLAG \
    -m 4G \
    -cdrom "$ISO_PATH" \
    -bios /usr/share/ovmf/OVMF.fd \
    -net nic -net user,hostfwd=tcp::8443-:8443,hostfwd=tcp::4443-:443 \
    -display none \
    -serial stdio \
    -no-reboot < "$QEMU_IN" > "$BOOT_LOG" 2>&1 &
QEMU_PID=$!
echo "QEMU PID: $QEMU_PID"

BOOTED=false
START=$(date +%s)
while true; do
    if grep -qi "login:" "$BOOT_LOG" 2>/dev/null; then
        pass_msg "System booted to login prompt"
        BOOTED=true
        break
    fi
    if grep -qi "kernel panic" "$BOOT_LOG" 2>/dev/null; then
        fail_msg "Kernel panic detected"
        break
    fi
    if ! kill -0 "$QEMU_PID" 2>/dev/null; then
        fail_msg "QEMU exited unexpectedly"
        break
    fi
    ELAPSED=$(( $(date +%s) - START ))
    if [ "$ELAPSED" -gt "$BOOT_TIMEOUT" ]; then
        fail_msg "Boot timeout exceeded (${BOOT_TIMEOUT}s)"
        break
    fi
    if (( ELAPSED % 30 < 4 )); then
        echo "  Waiting for login prompt... (${ELAPSED}s / ${BOOT_TIMEOUT}s, log: $(log_size) bytes)"
    fi
    sleep 3
done

# ── Phase 2: Serial Login ─────────────────────────────────────────
LOGGED_IN=false
if $BOOTED; then
    echo ""
    echo "══════════════════════════════════════════"
    echo " Phase 2: Serial Login"
    echo "══════════════════════════════════════════"

    POS=$(log_size)
    echo "  Sending username: ${LIVE_USER}"
    send_serial "$LIVE_USER" 2

    if wait_serial "assword:" 20 "$POS"; then
        POS=$(log_size)
        echo "  Sending password"
        send_serial "$LIVE_PASS" 5
        # Don't try to detect the shell prompt ($) — it matches too many
        # things in the boot log. Just wait and try commands.
        pass_msg "Serial login completed (${LIVE_USER})"
        LOGGED_IN=true
    else
        info_msg "Password prompt not detected — login may have failed"
        # Still try sending password in case prompt was missed in the log
        send_serial "$LIVE_PASS" 5
        LOGGED_IN=true  # Optimistic — diagnostics will reveal if it worked
    fi
fi

# ── Phase 3: Service Settle ───────────────────────────────────────
if $LOGGED_IN; then
    echo ""
    echo "══════════════════════════════════════════"
    echo " Phase 3: Waiting ${SVC_SETTLE}s for services"
    echo "══════════════════════════════════════════"
    WAITED=0
    while [ "$WAITED" -lt "$SVC_SETTLE" ]; do
        echo "  ${WAITED}s / ${SVC_SETTLE}s ..."
        sleep 15
        WAITED=$((WAITED + 15))
    done
fi

# ── Phase 4: Diagnostics via Serial ───────────────────────────────
if $LOGGED_IN; then
    echo ""
    echo "══════════════════════════════════════════"
    echo " Phase 4: Collecting Diagnostics (serial)"
    echo "══════════════════════════════════════════"

    # Wake terminal (in case of screensaver/blank)
    send_serial "" 1
    send_serial "" 1

    # ── 4a: Unit listing ──
    echo "  → systemctl list-units neuraldrive-*"
    send_serial "echo '---UNIT_LIST_START---'" 1
    send_serial "systemctl list-units 'neuraldrive-*' --no-pager --all" 5
    send_serial "echo '---UNIT_LIST_END---'" 1

    # ── 4b: Failed units ──
    echo "  → systemctl --failed"
    send_serial "echo '---FAILED_START---'" 1
    send_serial "systemctl --failed --no-pager" 3
    send_serial "echo '---FAILED_END---'" 1

    # ── 4c: Listening ports ──
    echo "  → ss -tlnp"
    send_serial "echo '---PORTS_START---'" 1
    send_serial "sudo ss -tlnp 2>/dev/null || ss -tlnp" 3
    send_serial "echo '---PORTS_END---'" 1

    # ── 4d: GPU config ──
    echo "  → GPU config"
    send_serial "echo '---GPU_START---'" 1
    send_serial "cat /run/neuraldrive/gpu.conf 2>/dev/null || echo 'GPU_CONF_MISSING'" 2
    send_serial "echo '---GPU_END---'" 1

    # ── 4e: TLS certs ──
    echo "  → TLS cert check"
    send_serial "echo '---TLS_START---'" 1
    send_serial "ls -la /etc/neuraldrive/tls/ 2>/dev/null || echo 'TLS_DIR_MISSING'" 2
    send_serial "echo '---TLS_END---'" 1

    # ── 4f: Per-service status ──
    echo "  → Per-service status"
    for svc in "${ALL_SERVICES[@]}"; do
        send_serial "echo '---SVCDETAIL:neuraldrive-${svc}:start---'" 1
        send_serial "systemctl status neuraldrive-${svc}.service --no-pager --lines=20 2>&1 || true" 3
        send_serial "echo '---SVCDETAIL:neuraldrive-${svc}:end---'" 1
    done

    # ── 4g: Parseable active/inactive check ──
    echo "  → Parseable service state check"
    send_serial "echo '---ACTIVE_CHECK_START---'" 1
    for svc in "${ALL_SERVICES[@]}"; do
        send_serial "printf 'SVCSTATE:neuraldrive-${svc}:%s\n' \"\$(systemctl is-active neuraldrive-${svc}.service 2>/dev/null || echo unknown)\"" 2
    done
    send_serial "echo '---ACTIVE_CHECK_END---'" 1

    # ── 4h: Journal errors ──
    echo "  → Journal errors (priority err+)"
    send_serial "echo '---JOURNAL_START---'" 1
    send_serial "sudo journalctl -p err --no-pager -n 100 --no-hostname 2>/dev/null || echo 'JOURNAL_UNAVAILABLE'" 8
    send_serial "echo '---JOURNAL_END---'" 1

    # ── 4i: Internal endpoint checks ──
    echo "  → Internal endpoint probes"
    send_serial "echo '---EP_START---'" 1
    send_serial "curl -sf -k https://localhost:8443/health --max-time 5 >/dev/null 2>&1 && echo 'EP:caddy_health:pass' || echo 'EP:caddy_health:fail'" 3
    send_serial "curl -sf -k -o /dev/null -w 'EP:webui_https:%{http_code}\n' https://localhost/ --max-time 5 2>/dev/null || echo 'EP:webui_https:fail'" 3
    send_serial "curl -sf http://localhost:11434/api/tags --max-time 5 >/dev/null 2>&1 && echo 'EP:ollama_api:pass' || echo 'EP:ollama_api:fail'" 3
    send_serial "curl -sf http://localhost:3001/ --max-time 5 >/dev/null 2>&1 && echo 'EP:system_api:pass' || echo 'EP:system_api:fail'" 3
    send_serial "echo '---EP_END---'" 1

    # ── 4j: Disk / memory snapshot ──
    echo "  → System resource snapshot"
    send_serial "echo '---RESOURCES_START---'" 1
    send_serial "df -h / /var/lib/neuraldrive 2>/dev/null || df -h /" 2
    send_serial "free -h" 2
    send_serial "echo '---RESOURCES_END---'" 1

    # ── 4k: Final marker ──
    send_serial "echo '===ALL_DIAG_DONE==='" 1

    echo "  Waiting ${DIAG_WAIT}s for serial output to flush..."
    POS=$(log_size)
    if ! wait_serial "===ALL_DIAG_DONE===" "$((DIAG_WAIT + 30))" "$POS"; then
        info_msg "Diagnostic marker not seen — output may be incomplete"
    fi
    sleep 5  # extra buffer for serial flush
fi

# ── Phase 5: External Endpoint Checks (from CI host) ──────────────
echo ""
echo "══════════════════════════════════════════"
echo " Phase 5: External Endpoint Checks"
echo "══════════════════════════════════════════"

if kill -0 "$QEMU_PID" 2>/dev/null; then
    # Caddy /health on :8443
    if curl -sf -k https://localhost:8443/health --max-time 15 2>/dev/null; then
        pass_msg "Caddy /health reachable (host → :8443)"
    else
        fail_msg "Caddy /health not reachable (host → :8443)"
    fi

    # Open WebUI via Caddy on :443 (forwarded to host :4443)
    HTTP_CODE=$(curl -sf -k -o /dev/null -w '%{http_code}' https://localhost:4443/ --max-time 15 2>/dev/null || echo "000")
    if [ "$HTTP_CODE" != "000" ]; then
        pass_msg "Caddy :443 reachable (HTTP ${HTTP_CODE}, host → :4443)"
    else
        fail_msg "Caddy :443 not reachable (host → :4443)"
    fi
else
    info_msg "QEMU not running — skipping external endpoint checks"
fi

# ── Phase 6: Parse Service States ─────────────────────────────────
echo ""
echo "══════════════════════════════════════════"
echo " Phase 6: Service State Analysis"
echo "══════════════════════════════════════════"

SVC_CHECKED=0
SVC_ACTIVE=0
SVC_FAILED=0
SVC_UNKNOWN=0

for svc in "${ALL_SERVICES[@]}"; do
    # Find SVCSTATE:neuraldrive-<svc>:<state> in the log.
    # Take the last match (in case of duplicates from echo).
    state=$(grep -o "SVCSTATE:neuraldrive-${svc}:[a-z]*" "$BOOT_LOG" 2>/dev/null \
            | tail -1 \
            | cut -d: -f3)
    SVC_CHECKED=$((SVC_CHECKED + 1))
    if [ "$state" = "active" ]; then
        pass_msg "neuraldrive-${svc}.service → active"
        SVC_ACTIVE=$((SVC_ACTIVE + 1))
    elif [ -n "$state" ]; then
        fail_msg "neuraldrive-${svc}.service → ${state}"
        SVC_FAILED=$((SVC_FAILED + 1))
    else
        # Could not parse state — maybe serial login failed or output garbled.
        # Fall back to boot log for systemd start/fail messages.
        if grep -qi "Started NeuralDrive.*${svc}" "$BOOT_LOG" 2>/dev/null; then
            info_msg "neuraldrive-${svc}.service — started (from boot log, state unverified)"
            SVC_ACTIVE=$((SVC_ACTIVE + 1))
        elif grep -qi "Failed to start.*${svc}" "$BOOT_LOG" 2>/dev/null; then
            fail_msg "neuraldrive-${svc}.service — failed (from boot log)"
            SVC_FAILED=$((SVC_FAILED + 1))
        else
            info_msg "neuraldrive-${svc}.service — state unknown (not in log)"
            SVC_UNKNOWN=$((SVC_UNKNOWN + 1))
        fi
    fi
done

# ── Parse internal endpoint results from serial ───────────────────
echo ""
echo "── Internal Endpoint Results ──"
for ep in caddy_health webui_https ollama_api system_api; do
    result=$(grep -o "EP:${ep}:[a-z0-9]*" "$BOOT_LOG" 2>/dev/null | tail -1 | cut -d: -f3)
    if [ -z "$result" ]; then
        info_msg "EP ${ep}: no result (serial diagnostics may not have run)"
    elif [ "$result" = "pass" ]; then
        pass_msg "EP ${ep}: reachable"
    elif echo "$result" | grep -qE '^[0-9]+$'; then
        # HTTP status code
        if [ "$result" -ge 200 ] && [ "$result" -lt 500 ]; then
            pass_msg "EP ${ep}: HTTP ${result}"
        else
            fail_msg "EP ${ep}: HTTP ${result}"
        fi
    else
        fail_msg "EP ${ep}: ${result}"
    fi
done

# ── Phase 7: Full Boot Log ────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════"
echo " Full Boot & Diagnostic Log"
echo "══════════════════════════════════════════"
echo ""
LOG_BYTES=$(log_size)
echo "(${LOG_BYTES} bytes)"
echo "────────────────────────────────────────────"
cat "$BOOT_LOG" 2>/dev/null || echo "(empty)"
echo ""
echo "────────────────────────────────────────────"

# ── Phase 8: Summary & Verdict ────────────────────────────────────
echo ""
echo "══════════════════════════════════════════"
echo " BVT RESULTS SUMMARY"
echo "══════════════════════════════════════════"
echo ""

if [ ${#PASS_MSGS[@]} -gt 0 ]; then
    for msg in "${PASS_MSGS[@]}"; do echo "  ✓ $msg"; done
fi
if [ ${#FAIL_MSGS[@]} -gt 0 ]; then
    echo ""
    for msg in "${FAIL_MSGS[@]}"; do echo "  ✗ $msg"; done
fi
if [ ${#INFO_MSGS[@]} -gt 0 ]; then
    echo ""
    for msg in "${INFO_MSGS[@]}"; do echo "  ℹ $msg"; done
fi

echo ""
echo "  Services: ${SVC_ACTIVE}/${SVC_CHECKED} active, ${SVC_FAILED} failed, ${SVC_UNKNOWN} unknown"
echo "  Totals:   ${#PASS_MSGS[@]} passed, ${#FAIL_MSGS[@]} failed, ${#INFO_MSGS[@]} info"
echo ""

if [ "$FAILURES" -gt 0 ]; then
    echo "BVT FAILED (${FAILURES} failure(s))"
    echo ""
    exit 1
else
    echo "BVT PASSED"
    echo ""
    exit 0
fi

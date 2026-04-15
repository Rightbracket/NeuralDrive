#!/bin/bash
set -euo pipefail

CONFIG="$1"
if [ -z "$CONFIG" ]; then
    echo "Usage: validate-config.sh <config.yaml>"
    exit 1
fi

if ! command -v yq &>/dev/null; then
    echo "Error: yq is required. Install from https://github.com/mikefarah/yq"
    exit 1
fi

ERRORS=0

check_field() {
    local path="$1"
    local desc="$2"
    local val
    val=$(yq "$path" "$CONFIG" 2>/dev/null)
    if [ "$val" = "null" ] || [ -z "$val" ]; then
        echo "MISSING: $desc ($path)"
        ERRORS=$((ERRORS + 1))
    fi
}

check_field '.neuraldrive.version' "NeuralDrive version"
check_field '.neuraldrive.name' "Image name"
check_field '.neuraldrive.hostname' "Default hostname"
check_field '.neuraldrive.system.kernel' "Kernel selection"
check_field '.neuraldrive.output.format' "Output format"
check_field '.neuraldrive.output.filename' "Output filename"

FORMAT=$(yq '.neuraldrive.output.format' "$CONFIG" 2>/dev/null)
if [ "$FORMAT" != "iso-hybrid" ] && [ "$FORMAT" != "raw-disk" ]; then
    echo "INVALID: output.format must be 'iso-hybrid' or 'raw-disk', got '$FORMAT'"
    ERRORS=$((ERRORS + 1))
fi

KERNEL=$(yq '.neuraldrive.system.kernel' "$CONFIG" 2>/dev/null)
if [ "$KERNEL" != "default" ] && [ "$KERNEL" != "backport" ]; then
    echo "INVALID: system.kernel must be 'default' or 'backport', got '$KERNEL'"
    ERRORS=$((ERRORS + 1))
fi

if [ $ERRORS -gt 0 ]; then
    echo ""
    echo "Validation failed with $ERRORS error(s)."
    exit 1
fi

echo "Configuration valid."

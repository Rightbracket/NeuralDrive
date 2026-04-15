#!/bin/bash
set -euo pipefail

echo "NeuralDrive GPU Verification"
echo "============================"

source /run/neuraldrive/gpu.conf 2>/dev/null || {
    echo "SKIP: GPU config not found (not running on NeuralDrive)."
    exit 0
}

echo "Detected vendor: $VENDOR"

if [ "$VENDOR" = "NVIDIA" ]; then
    if command -v nvidia-smi &>/dev/null; then
        echo "PASS: nvidia-smi available"
        nvidia-smi -L
        echo ""
        echo "Running inference test..."
        ollama run phi3:mini "What is 2+2? Reply with just the number." --verbose 2>&1 | tail -5
        echo "PASS: NVIDIA inference test complete."
    else
        echo "FAIL: NVIDIA detected but nvidia-smi not found."
        exit 1
    fi
fi

if [ "$VENDOR" = "AMD" ]; then
    if command -v rocm-smi &>/dev/null; then
        echo "PASS: rocm-smi available"
        rocm-smi --showproductname
        echo ""
        echo "Running inference test..."
        ollama run phi3:mini "What is 2+2? Reply with just the number." --verbose 2>&1 | tail -5
        echo "PASS: AMD inference test complete."
    else
        echo "FAIL: AMD detected but rocm-smi not found."
        exit 1
    fi
fi

if [ "$VENDOR" = "CPU" ]; then
    echo "CPU-only mode. Running inference test..."
    ollama run phi3:mini "What is 2+2? Reply with just the number." --verbose 2>&1 | tail -5
    echo "PASS: CPU inference test complete."
fi

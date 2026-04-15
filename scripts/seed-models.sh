#!/bin/bash
set -e

STAGING_DIR="./model-staging"
export OLLAMA_MODELS="$STAGING_DIR"
mkdir -p "$STAGING_DIR"

ollama serve &
OLLAMA_PID=$!
sleep 3

ollama pull qwen2.5:3b
ollama pull llama3.1:8b

kill $OLLAMA_PID
wait $OLLAMA_PID 2>/dev/null || true

echo "Models staged in $STAGING_DIR"
echo "Pack into models.squashfs or copy into includes.chroot for next build."

#!/bin/bash
set -euo pipefail

CONFIG="$1"
if [ -z "$CONFIG" ]; then
    echo "Usage: download-models.sh <config.yaml>"
    exit 1
fi

STAGING_DIR="./model-staging"
export OLLAMA_MODELS="$STAGING_DIR"
mkdir -p "$STAGING_DIR"

MODEL_COUNT=$(yq '.neuraldrive.models.preload | length' "$CONFIG" 2>/dev/null)
if [ "$MODEL_COUNT" = "0" ] || [ "$MODEL_COUNT" = "null" ]; then
    echo "No models to preload."
    exit 0
fi

echo "Starting temporary Ollama instance for model download..."
ollama serve &
OLLAMA_PID=$!

for i in $(seq 0 30); do
    if curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
        break
    fi
    sleep 1
done

for i in $(seq 0 $((MODEL_COUNT - 1))); do
    MODEL=$(yq ".neuraldrive.models.preload[$i]" "$CONFIG")
    echo "Pulling model: $MODEL"
    ollama pull "$MODEL"
done

kill $OLLAMA_PID
wait $OLLAMA_PID 2>/dev/null || true

echo "Models staged in $STAGING_DIR"
echo "Total size: $(du -sh "$STAGING_DIR" | cut -f1)"

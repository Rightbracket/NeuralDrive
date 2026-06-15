#!/usr/bin/env bash
set -euo pipefail

SECRETS_DIR="$(cd "$(dirname "$0")/.." && pwd)/docker/dev-secrets"

echo "Setting up NeuralDrive dev environment..."

mkdir -p "$SECRETS_DIR/tls"

# API key
if [[ ! -f "$SECRETS_DIR/api.key" ]]; then
    printf "nd-%s" "$(openssl rand -hex 16)" > "$SECRETS_DIR/api.key"
    echo "  Generated API key: $SECRETS_DIR/api.key"
else
    echo "  API key already exists, skipping"
fi

# TLS cert
if [[ ! -f "$SECRETS_DIR/tls/server.crt" ]]; then
    openssl req -x509 -newkey rsa:2048 -nodes \
        -keyout "$SECRETS_DIR/tls/server.key" \
        -out "$SECRETS_DIR/tls/server.crt" \
        -days 365 \
        -subj "/CN=neuraldrive.local" \
        -addext "subjectAltName=DNS:localhost,DNS:neuraldrive.local,IP:127.0.0.1" \
        2>/dev/null
    echo "  Generated TLS cert: $SECRETS_DIR/tls/"
else
    echo "  TLS cert already exists, skipping"
fi

# GPU stub (CPU-only mode)
if [[ ! -f "$SECRETS_DIR/gpu.conf" ]]; then
    printf "GPU_VENDOR=none\nGPU_COUNT=0\n" > "$SECRETS_DIR/gpu.conf"
    echo "  Created GPU stub (CPU mode): $SECRETS_DIR/gpu.conf"
else
    echo "  gpu.conf already exists, skipping"
fi

# docker/.env
ENV_FILE="$(cd "$(dirname "$0")/.." && pwd)/docker/.env"
if [[ ! -f "$ENV_FILE" ]]; then
    API_KEY=$(cat "$SECRETS_DIR/api.key")
    printf "NEURALDRIVE_API_KEY=%s\n" "$API_KEY" > "$ENV_FILE"
    echo "  Created docker/.env"
else
    echo "  docker/.env already exists, skipping"
fi

API_KEY=$(cat "$SECRETS_DIR/api.key")

echo ""
echo "Dev environment ready. Start the stack with:"
echo ""
echo "  docker compose -f docker-compose.dev.yml up"
echo ""
echo "Endpoints:"
echo "  Web UI:      https://localhost/"
echo "  Health:      https://localhost:8443/health"
echo "  System API:  https://localhost:8443/system/status"
echo "  Ollama:      http://localhost:11434/api/tags"
echo ""
echo "API key: $API_KEY"
echo "(also in docker/dev-secrets/api.key)"
echo ""
echo "To enable GPU passthrough (NVIDIA + Container Toolkit required):"
echo "  docker compose -f docker-compose.dev.yml --profile gpu up"

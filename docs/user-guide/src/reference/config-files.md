*Audience: Admin*

# Configuration Files

This document provides a complete reference for all critical configuration and state files within the NeuralDrive appliance.

## Master File Inventory

| File | Purpose | Format | Owner |
| :--- | :--- | :--- | :--- |
| `/etc/neuraldrive/ollama.conf` | Ollama environment variables | KEY=VALUE | root:neuraldrive-admin |
| `/etc/neuraldrive/webui.env` | Open WebUI configuration | KEY=VALUE | root:neuraldrive-admin |
| `/etc/neuraldrive/caddy.env` | Caddy API key environment | KEY=VALUE | root:neuraldrive-admin |
| `/etc/neuraldrive/api.env` | System API environment | KEY=VALUE | root:neuraldrive-admin |
| `/etc/neuraldrive/api.key` | API authentication key | plaintext | root:root (600) |
| `/etc/neuraldrive/Caddyfile` | Caddy reverse proxy configuration | Caddyfile | root:neuraldrive-caddy |
| `/etc/neuraldrive/nftables.conf` | Global firewall rules | nftables | root:root |
| `/etc/neuraldrive/neuraldrive-models.yaml` | Model catalog definitions | YAML | root:neuraldrive-admin |
| `/etc/neuraldrive/version` | Build version string | plaintext | root:root |
| `/etc/neuraldrive/tls/server.crt` | System TLS certificate | PEM | root:neuraldrive-caddy |
| `/etc/neuraldrive/tls/server.key` | System TLS private key | PEM | root:neuraldrive-caddy (600) |
| `/etc/neuraldrive/tls/neuraldrive-ca.crt` | Root CA for clients | PEM | root:root (644) |
| `/etc/neuraldrive/firewall-custom.conf` | User-defined firewall rules | nftables | root:root |
| `/run/neuraldrive/gpu.conf` | GPU detection results (at boot) | KEY=VALUE | root:root (runtime) |

## Key Configuration Reference

### `ollama.conf`

Defines the behavior of the underlying LLM inference engine.

```ini
OLLAMA_HOST=127.0.0.1:11434
OLLAMA_MODELS=/var/lib/neuraldrive/models/
OLLAMA_KEEP_ALIVE=5m
OLLAMA_MAX_LOADED_MODELS=1
OLLAMA_NUM_PARALLEL=1
```

### `webui.env`

Configures the Open WebUI chat interface and authentication.

```ini
OLLAMA_BASE_URL=http://localhost:11434
DATA_DIR=/var/lib/neuraldrive/webui
ENABLE_SIGNUP=false
DEFAULT_USER_ROLE=user
WEBUI_AUTH=true
WEBUI_NAME=NeuralDrive
ENABLE_EASTER_EGGS=false
```

### `api.key`

This file contains the master authentication token (`nd-xxxx`) used to secure both the inference API and the system management API. It is generated during the first-boot initialization and should be treated with high sensitivity.

### `Caddyfile`

NeuralDrive's reverse proxy configuration. It manages TLS termination and routing to internal services.

> **Note**: For instructions on using your own TLS certificates, see [TLS Certificates](../admin/tls-certs.md). To modify boot-time behavior, consult [Boot Parameters](boot-parameters.md).

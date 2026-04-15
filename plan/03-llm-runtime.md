# Implementation Plan: 03-llm-runtime.md — LLM Serving & Model Management

This document outlines the implementation for the core LLM serving software and model management within the NeuralDrive project.

## Section 1: Ollama Installation & Configuration

### Installation Method
NeuralDrive downloads the standalone Ollama binary during the `live-build` chroot phase (see `01-base-system.md`, hook `03-install-extras.chroot`). There is no official `.deb` package in Debian repositories; the binary is fetched directly from Ollama's release server.

- **Source**: [https://ollama.com/download/ollama-linux-amd64](https://ollama.com/download/ollama-linux-amd64)
- **Binary Location**: `/usr/local/bin/ollama`
- **Data Directory**: `/var/lib/neuraldrive/models/`

### Systemd Service: `neuraldrive-ollama.service`
The service is configured to start after GPU detection is complete and paths are established.

```ini
[Unit]
Description=NeuralDrive Ollama Service
After=network.target neuraldrive-gpu-detect.service
Requires=neuraldrive-gpu-detect.service

[Service]
EnvironmentFile=/etc/neuraldrive/ollama.conf
ExecStartPre=/usr/bin/mkdir -p /var/lib/neuraldrive/models
ExecStart=/usr/local/bin/ollama serve
User=neuraldrive-ollama
Group=neuraldrive-ollama
Restart=always
RestartSec=5
KillMode=process

# Resource Limits
LimitNOFILE=65535
MemoryHigh=90%
MemoryMax=95%

[Install]
WantedBy=multi-user.target
```

### Configuration: `/etc/neuraldrive/ollama.conf`
This file contains environment overrides read by the systemd unit.

```bash
# NeuralDrive Ollama Configuration
OLLAMA_HOST=127.0.0.1:11434
OLLAMA_MODELS=/var/lib/neuraldrive/models/
OLLAMA_KEEP_ALIVE=5m
OLLAMA_MAX_LOADED_MODELS=1
OLLAMA_NUM_PARALLEL=1

# GPU Paths (Populated by neuraldrive-gpu-detect.service)
# LD_LIBRARY_PATH=/usr/local/cuda/lib64
```

### Logging
- **Primary**: `journald`
- **Secondary**: `/var/log/neuraldrive/ollama.log` via `rsyslog` or simple redirection.

## Section 2: llama.cpp Server (Secondary Runtime)

For advanced users requiring direct GGUF loading or specific quantization controls not exposed by Ollama.

- **Installation**: Compiled during image build with CUDA/ROCm/oneAPI support.
- **Binary**: `/usr/local/bin/llama-server`
- **Service**: `neuraldrive-llama-server.service` (Disabled by default).

### Comparison Table

| Feature | Ollama | llama.cpp Server |
|---------|--------|------------------|
| Model Format | Modelfile (GGUF based) | Direct GGUF |
| API | Ollama API & OpenAI | OpenAI-like |
| Memory Management | Automatic / Dynamic | Manual / Static |
| Multi-model | Yes (On-demand) | No (Single model) |
| Performance | High (Optimized) | Highest (Raw access) |
| Ease of Use | Seamless | Technical |

## Section 3: Model Management

### Pre-loaded Models (Two-Phase Build Approach)
Models are NOT pulled during the `live-build` chroot phase, because running Ollama as a server inside a chroot is fragile and unnecessary. Instead, model pre-loading uses a two-phase approach:

**Phase 1** — Build the base ISO without models (via `lb build`).

**Phase 2** — Seed models in a separate step on a matching Linux environment:
```bash
#!/bin/bash
# scripts/seed-models.sh — Run OUTSIDE of live-build, on a Linux host
set -e

STAGING_DIR="./model-staging"
export OLLAMA_MODELS="$STAGING_DIR"
mkdir -p "$STAGING_DIR"

# Start Ollama temporarily (no GPU needed for pull)
ollama serve &
OLLAMA_PID=$!
sleep 3

# Pull models from catalog
ollama pull qwen2.5:3b
ollama pull llama3.1:8b
# Add more models as needed from neuraldrive-models.yaml

# Stop Ollama
kill $OLLAMA_PID
wait $OLLAMA_PID 2>/dev/null || true

echo "Models staged in $STAGING_DIR"
echo "Pack into models.squashfs or copy into includes.chroot for next build."
```

The staged `models/blobs/` and `models/manifests/` directories are then either:
- Packed into `models.squashfs` (for the SquashFS overlay approach, see 09-image-toolkit.md §5), or
- Copied into `config/includes.chroot/usr/share/neuraldrive/models/` for baking into the image directly.

At runtime, if the persistence partition has no models, the pre-loaded models from `/usr/share/neuraldrive/models/` are symlinked into `/var/lib/neuraldrive/models/`.

### Model Catalog: `neuraldrive-models.yaml`
A curated list of recommended models.

```yaml
models:
  small:
    - name: "qwen2.5:3b"
      size: "1.9GB"
      ram_req: "8GB"
    - name: "phi3:mini"
      size: "2.3GB"
      ram_req: "8GB"
  medium:
    - name: "llama3.1:8b"
      size: "4.7GB"
      ram_req: "16GB"
      vram_req: "8GB"
  large:
    - name: "llama3.1:70b"
      size: "40GB"
      ram_req: "64GB"
      vram_req: "24GB+"
```

### Lifecycle Commands
- **Download**: `ollama pull <model>`
- **Check Status**: `ollama ps`
- **Local Files**: Models are stored in `/var/lib/neuraldrive/models/blobs/` with metadata in `/var/lib/neuraldrive/models/manifests/`.

## Section 4: Multi-Model Concurrency

Ollama manages VRAM allocation automatically.
- **Dynamic Loading**: Models load into memory on the first request and stay for `OLLAMA_KEEP_ALIVE`.
- **Concurrency**: `OLLAMA_NUM_PARALLEL` allows multiple requests to be processed by a single loaded model.
- **Eviction**: If a new model is requested and VRAM is full, the Least Recently Used (LRU) model is evicted.

## Section 5: API Layer

### Native Ollama API (`:11434`)
- `POST /api/generate`: Raw completion.
- `POST /api/chat`: Structured chat.
- `GET /api/tags`: List local models.

### OpenAI Compatibility
Ollama provides OpenAI-compatible endpoints at `/v1/*` automatically. NeuralDrive routes these through Caddy for TLS and basic authentication.

## Section 6: Performance Tuning

- **Thread Count**: `OLLAMA_NUM_THREADS` is set to match physical CPU cores detected at boot.
- **Flash Attention**: Enabled by default for NVIDIA and supported AMD GPUs.
- **Memory Mapping (mmap)**: Enabled to allow faster model startup by reading directly from disk into memory.
- **Context Window**: Configurable via `Modelfile` or API request parameters.

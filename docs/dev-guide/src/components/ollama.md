*This chapter is for contributors and maintainers.*

# Ollama Integration

Ollama serves as the core inference engine for NeuralDrive. It is managed as a systemd service and configured to optimize resource usage on the appliance.

## Installation

The Ollama binary is installed to `/usr/local/bin/ollama` during the build process via the `03-install-extras` hook. We use the official static binary to ensure compatibility across different Debian versions.

## Service Configuration

The `neuraldrive-ollama.service` manages the lifecycle of the inference engine.

### Service Unit Highlights
- **User**: Runs as `neuraldrive-ollama` (UID 901).
- **Dependencies**: `Requires=neuraldrive-gpu-detect.service`.
- **Security**: Uses `DeviceAllow` to restrict access to only relevant GPU device nodes.
- **Resource Limits**: 
  - `MemoryHigh=90%`: Triggers aggressive swapping/GC when system memory is nearly full.
  - `MemoryMax=95%`: The hard limit before the OOM killer intervenes.

## Configuration (ollama.conf)

System-wide settings are stored in `/etc/neuraldrive/ollama.conf`:
- `OLLAMA_HOST=127.0.0.1:11434`: Ensures the API is only accessible locally (proxied by Caddy).
- `OLLAMA_MODELS=/var/lib/neuraldrive/models/`: Directs model weights to the persistence layer.
- `OLLAMA_KEEP_ALIVE=5m`: Models are unloaded from VRAM after 5 minutes of inactivity.
- `OLLAMA_MAX_LOADED_MODELS=1`: Limits concurrent model loading to prevent VRAM exhaustion on smaller cards.
- `OLLAMA_NUM_PARALLEL=1`: Processes one request at a time to maintain deterministic performance.

## GPU Support

Ollama automatically detects the compute provider based on the drivers loaded by `gpu-detect.sh`.
- **NVIDIA**: Uses the CUDA runner.
- **AMD**: Uses the ROCm/HIP runner.
- **Intel**: Uses the OneAPI runner.
- **CPU**: Falls back to the AVX/AVX2 optimized CPU runner.

## Model Management

Models can be managed via the Open WebUI or the `ollama` CLI. When a model is "pulled," it is stored as a series of blobs in the persistent `/var/lib/neuraldrive/models/` directory.

> **Tip**: To interact with Ollama manually for troubleshooting, use the `neuraldrive-admin` user:
> `sudo -u neuraldrive-ollama ollama list`


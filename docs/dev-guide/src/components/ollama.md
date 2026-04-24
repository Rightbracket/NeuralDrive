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
- **Security**: The service uses `PrivateDevices=no` to allow GPU access. Note that all `DeviceAllow` directives were removed because cgroup v2's eBPF device filter blocked CUDA access even with explicit allow rules.
- **Resource Limits**: 
  - `MemoryHigh=90%`: Triggers aggressive swapping/GC when system memory is nearly full.
  - `MemoryMax=95%`: The hard limit before the OOM killer intervenes.
- **GPU Initialization**: The unit includes `ExecStartPre` commands to ensure CUDA is ready:
  - `ExecStartPre=-/sbin/modprobe nvidia-current-uvm`: Loads the CUDA Unified Video Memory module (named `nvidia-current-uvm` in the Debian package).
  - `ExecStartPre=-/usr/bin/nvidia-modprobe -u`: Creates the `/dev/nvidia-uvm` and `/dev/nvidia-uvm-tools` device nodes.

### Persistent Config Overrides
The service unit includes two `EnvironmentFile` directives to manage configuration:
1. `EnvironmentFile=/etc/neuraldrive/ollama.conf`: Contains baked-in system defaults.
2. `EnvironmentFile=-/var/lib/neuraldrive/config/ollama.conf`: Allows persistent user-defined overrides. The `-` prefix ensures the service starts even if this file is missing.

## Configuration (ollama.conf)

System-wide settings are defined in the environment files:
- `OLLAMA_HOST=127.0.0.1:11434`: Ensures the API is only accessible locally (proxied by Caddy).
- `OLLAMA_MODELS=/var/lib/neuraldrive/models/`: Directs model weights to the persistence layer.
- `OLLAMA_KEEP_ALIVE=5m`: Models are unloaded from VRAM after 5 minutes of inactivity.
- `OLLAMA_MAX_LOADED_MODELS=0`: Set to `0` for auto mode. Ollama manages multiple models based on available VRAM using LRU (Least Recently Used) eviction.
- `OLLAMA_NUM_PARALLEL=1`: Processes one request at a time to maintain deterministic performance.

## API Usage Details

### Loading Models
To load a model, send a `POST` request to `/api/generate` with `keep_alive` set to `-1`. Note that `keep_alive` must be an integer; passing it as a string ("-1") will result in a rejection.

### Unloading Models
To unload a model, send a `POST` request to `/api/generate` with `keep_alive` set to `0`. To verify the eviction, poll `/api/ps` until the model no longer appears. A race condition exists where the 200 OK response may return before the eviction process is fully complete.

### Monitoring
`GET /api/ps` returns a list of running models, including the `size_vram` utilized by each.

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


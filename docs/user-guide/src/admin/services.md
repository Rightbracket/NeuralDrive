*This chapter is for system administrators.*

# Service Management

NeuralDrive is composed of several specialized services that handle different aspects of the system, from GPU detection to web application hosting.

## NeuralDrive Service List

The following services are managed by `systemd`:

- **`neuraldrive-setup`**: Handles initial system setup and first-boot configurations.
- **`neuraldrive-gpu-detect`**: Automatically detects available GPUs and prepares the system before Ollama starts.
- **`neuraldrive-certs`**: Manages the generation and renewal of TLS certificates.
- **`neuraldrive-zram`**: Configures zram-based swap space for efficient memory management.
- **`neuraldrive-show-ip`**: Displays the active IP address on the physical console at boot.
- **`neuraldrive-ollama`**: The core LLM inference server (internal port 11434).
- **`neuraldrive-webui`**: The Open WebUI dashboard for user interaction (internal port 3000).
- **`neuraldrive-caddy`**: The reverse proxy that exposes services via ports 443 and 8443.
- **`neuraldrive-gpu-monitor`**: Collects and serves GPU telemetry data (internal port 1312).
- **`neuraldrive-system-api`**: Provides programmatic access to system management (internal port 3001).
- **`neuraldrive-storage-monitor`**: Monitors disk usage and provides alerts based on defined thresholds.

## Monitoring and Control

Service status can be checked using several interfaces:
- **TUI Services Screen**: Real-time status and control.
- **Web System Panel**: Visual status overview.
- **Command Line**: Standard `systemctl` commands.

```bash
# Check status
systemctl status neuraldrive-ollama

# Restart a service
sudo systemctl restart neuraldrive-ollama

# View logs
journalctl -u neuraldrive-ollama -f
```

## Service Dependencies

NeuralDrive services are designed with a specific boot order to ensure reliability:
- `gpu-detect` must complete before `ollama` starts.
- `ollama` must be active before `webui` begins operation.
- `certs` must successfully generate certificates before `caddy` can bind to its ports.

## Storage Monitoring

The `neuraldrive-storage-monitor` service provides automated alerts when disk usage exceeds specific thresholds:
- **80%**: Warning threshold.
- **90%**: Critical threshold.
- **95%**: Immediate action required.

[Service Reference](../reference/services.md)
[TUI Services](../using/tui-services.md)

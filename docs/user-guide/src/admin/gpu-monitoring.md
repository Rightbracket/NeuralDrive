*This chapter is for all users and system administrators.*

# GPU Monitoring

NeuralDrive provides multiple ways to monitor GPU health, utilization, and resource consumption in real-time.

## TUI Dashboard

The Terminal User Interface (TUI) provides a high-level overview of GPU status, including VRAM usage, temperature, and utilization percentages. This dashboard is accessible directly from the physical console or via SSH.

## Web System Panel

A more detailed GPU monitoring interface is available through the web System Panel.

- **URL**: `https://<IP>:8443/monitor/`
- **Dashboard**: "GPU Hot"

This interface provides a real-time dashboard powered by an internal service running on port 1312, which is securely proxied by Caddy.

## Command-Line Tools

For advanced diagnostics, standard vendor-specific command-line tools are available:
- **NVIDIA**: `nvidia-smi`
- **AMD**: `rocm-smi`
- **General Hardware Check**: `lspci | grep -i vga`

## Monitoring Service

The `neuraldrive-gpu-monitor.service` is responsible for collecting and serving GPU telemetry. This service runs as the `neuraldrive-monitor` user and exposes data on internal port 1312.

## System API

Programmatic access to GPU telemetry is available via the System Management API.

- **Endpoint**: `GET /system/gpu`
- **Response Data**:
  - Vendor and device names.
  - VRAM total and currently used.
  - Current temperature.

[Terminal Interface](../using/tui.md)
[System Management API](system-api.md)

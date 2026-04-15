*Audience: Admin*

# Service Reference

This document provides a detailed overview of the systemd services that power the NeuralDrive appliance.

## Master Service Inventory

| Service | Type | User | Port | Dependencies | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `neuraldrive-setup` | oneshot | root | — | network.target | First-boot initialization and state generation. |
| `neuraldrive-gpu-detect` | oneshot | root | — | — | GPU auto-detection and driver selection via PCI enumeration. |
| `neuraldrive-certs` | oneshot | root | — | network-online, local-fs | Generates self-signed TLS certificates (skips if they already exist). |
| `neuraldrive-zram` | oneshot | root | — | local-fs | Sets up compressed RAM-based swap space. |
| `neuraldrive-show-ip` | oneshot | root | — | network-online | Displays the current IP address on the physical console. |
| `neuraldrive-ollama` | long-running | neuraldrive-ollama | 11434 | gpu-detect | The underlying LLM inference and model management engine. |
| `neuraldrive-webui` | long-running | neuraldrive-webui | 3000 | ollama | The Open WebUI dashboard and chat interface. |
| `neuraldrive-caddy` | long-running | neuraldrive-caddy | 443, 8443 | certs | The TLS reverse proxy and API gateway. |
| `neuraldrive-gpu-monitor` | long-running | neuraldrive-monitor | 1312 | gpu-detect | Monitors GPU temperature, VRAM usage, and health. |
| `neuraldrive-system-api` | long-running | neuraldrive-api | 3001 | network | The backend service for the System Management API. |
| `neuraldrive-storage-monitor` | long-running | root | — | local-fs | Monitors available storage space and persistence health. |

## Systemd Hardening Summary

All NeuralDrive services are configured with systemd-native security hardening to minimize the system attack surface:

-   **PrivateDevices**: Most services are denied access to `/dev/` nodes, except for the GPU-specific services.
-   **ProtectSystem**: The root filesystem is mounted read-only for service processes.
-   **ProtectHome**: Services have no access to the `/home/` directory.
-   **NoNewPrivileges**: Prevents processes from gaining elevated permissions via `setuid` or `setgid`.
-   **RestrictAddressFamilies**: Limits network communication to only necessary protocols (e.g., `AF_INET`, `AF_INET6`, `AF_UNIX`).

> **Tip**: You can monitor the status and logs of any service using the `systemctl status <service>` and `journalctl -u <service>` commands. For a list of common service-related issues, see the [Common Issues troubleshooting guide](../troubleshooting/common-issues.md).

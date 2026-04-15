*Audience: Admin*

# Port Reference

This document outlines the network ports utilized by NeuralDrive for internal communication and external access.

## Port Assignment Matrix

| Port | Protocol | Service | Exposure | Description |
| :--- | :--- | :--- | :--- | :--- |
| **443** | TCP | `neuraldrive-caddy` | External | Primary Web UI dashboard access (HTTPS). |
| **8443** | TCP | `neuraldrive-caddy` | External | API gateway and System Management Panel (HTTPS). |
| **5353** | UDP | `avahi-daemon` | External | mDNS discovery for `neuraldrive.local` resolution. |
| **22** | TCP | `sshd` | External | Optional SSH access (rate-limited, must be enabled via boot parameter). |
| **11434** | TCP | `neuraldrive-ollama` | Internal only | The underlying Ollama inference API. |
| **3000** | TCP | `neuraldrive-webui` | Internal only | The Open WebUI dashboard backend. |
| **3001** | TCP | `neuraldrive-system-api` | Internal only | The System Management API backend. |
| **1312** | TCP | `neuraldrive-gpu-monitor` | Internal only | The GPU Hot health and telemetry monitor. |

## Exposure Definitions

-   **External**: These ports are open on the system firewall (`nftables`) and are accessible from other machines on the local network.
-   **Internal only**: These ports are bound exclusively to the `localhost` (127.0.0.1) interface. They are not reachable from the network. Caddy acts as a secure reverse proxy to these services, providing TLS termination and authentication.

> **Warning**: Never modify the internal port bindings, as they are hard-coded into the NeuralDrive security model.

> **Note**: For more information on configuring the firewall, see [Firewall Configuration](../admin/firewall.md). For details on the API endpoints exposed via these ports, see [API Endpoint Reference](api-endpoints.md).

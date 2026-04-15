*This chapter is for system administrators and developers.*

# System Management API

The NeuralDrive System Management API provides programmatic access to system operations, monitoring, and configuration.

## Access and Endpoints

The API is accessible over HTTPS:
- **URL**: `https://<IP>:8443/system/`

Internally, the `neuraldrive-system-api` service runs on port 3001 and is proxied by Caddy to port 8443.

## Authentication

All requests to the System Management API require a Bearer token for authentication. This is the same token used for the inference API and can be found in `/etc/neuraldrive/api.key`.

## Common Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/system/status` | CPU, RAM, disk, uptime, and system version. |
| `GET` | `/system/services` | List all `neuraldrive-*` services and their status. |
| `POST` | `/system/services/{name}/restart` | Restart a specific service. |
| `POST` | `/system/services/{name}/{action}` | Start or stop a specific service. |
| `GET` | `/system/logs` | Service log tailing (query params: `service`, `lines`). |
| `GET` | `/system/storage` | Detailed disk usage (models and persistence). |
| `GET` | `/system/network` | Interfaces, hostname, and mDNS status. |
| `POST` | `/system/network/hostname` | Set a new system hostname. |
| `GET` | `/system/gpu` | GPU vendor, device names, VRAM usage, and temperature. |
| `POST` | `/system/ssh/{action}` | Enable or disable SSH access. |
| `GET` | `/system/security` | Firewall, TLS, and SSH status. |
| `POST` | `/system/api-keys/rotate` | Rotate the system API key. |
| `GET` | `/system/ca-cert` | Download the root CA certificate (no authentication required). |

## Implementation Details

The API is implemented using FastAPI and is served by Uvicorn. The application environment is located at `/usr/lib/neuraldrive/api/`.

For security reasons, only services prefixed with `neuraldrive-` can be managed through the API.

## See Also

- [System Management API Reference](../reference/system-api-endpoints.md) — complete endpoint listing with request and response schemas.
- [API Overview](../api/overview.md) — architecture and authentication for the inference API.
- [API Key Management](../api/api-keys.md) — key rotation, storage, and best practices.

*Audience: Admin / Developers*

# System Management API Reference

NeuralDrive provides a dedicated management API for monitoring health, controlling services, and configuring the underlying system.

## Authentication

All management requests must include the system API key (found in `/etc/neuraldrive/api.key`) in the `Authorization` header:

```http
Authorization: Bearer nd-xxxx
```

**Base URL**: `https://<IP_ADDRESS>:8443/system/`

## Health and Status

### GET /system/status
Returns high-level system metrics and version information.

**Response Schema**:
```json
{
  "hostname": "string",
  "cpu_percent": 12.5,
  "memory": {
    "total_gb": 32,
    "used_percent": 45.1
  },
  "disk": {
    "models": {
      "total": "512G",
      "used": "120G",
      "free": "392G"
    },
    "total": "1T"
  },
  "uptime_seconds": 86400,
  "version": "v1.2.0"
}
```

### GET /system/gpu
Reports detected GPU hardware and real-time utilization.

**Response Schema**:
```json
{
  "vendor": "NVIDIA",
  "devices": [
    {
      "name": "RTX 4090",
      "vram_total_mb": 24576,
      "vram_used_mb": 4096,
      "temp_c": 55
    }
  ]
}
```

## Service Management

### GET /system/services
Lists all core services and their current runtime status.

### POST /system/services/{name}/{action}
Controls a specific system service.
-   **Actions**: `start`, `stop`, `restart`
-   **Allowed Services**: `neuraldrive-ollama`, `neuraldrive-webui`, `neuraldrive-caddy`, `neuraldrive-gpu-monitor`, `neuraldrive-system-api`, `neuraldrive-certs`.

### GET /system/logs
Retrieves recent journal logs for a specific service.
-   **Query Parameters**: `service=ollama`, `lines=50`

## System Configuration

### GET /system/network
Returns current network configuration including interface IPs, hostname, and mDNS status.

### POST /system/network/hostname
Updates the system hostname.
-   **Query Parameters**: `hostname=new-name`

### POST /system/api-keys/rotate
Generates a new master API key and invalidates the previous one.
-   **Warning**: This will immediately break existing client integrations until they are updated with the new key.

### GET /system/ca-cert
Downloads the root CA certificate used for TLS signing.
-   **Note**: This endpoint does not require authentication.

> **Note**: For information on LLM inference, see the [API Endpoint Reference](api-endpoints.md). For details on the system architecture, see [Service Reference](services.md).

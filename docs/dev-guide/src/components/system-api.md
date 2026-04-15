*This chapter is for contributors and maintainers.*

# System Management API

The NeuralDrive System API is a custom FastAPI application that provides programmatic control over the appliance's hardware and software configuration.

## Application Structure

The source code is located at `/usr/lib/neuraldrive/api/neuraldrive_api/`. The application is consolidated in a single entry point:
- `main.py`: Route definitions, token verification, and all endpoint logic.

## Authentication

All endpoints (except `/system/ca-cert`) require a Bearer token. The API verifies this token against the master key stored in `/etc/neuraldrive/api.key`.

## Primary Endpoints

### System Status
- `GET /system/status`: Returns CPU/RAM usage and system uptime.
- `GET /system/gpu`: Returns detailed GPU metrics (temp, VRAM, utilization).

### Service Management
- `GET /system/services`: Lists the status of all NeuralDrive services.
- `POST /system/services/{name}/{action}`: Allows starting, stopping, or restarting services.
- `GET /system/logs`: Retrieves the last N lines of the system journal for a specific service.

### Configuration
- `POST /system/network/hostname`: Updates the system hostname and mDNS name.
- `GET /system/security`: Returns the current firewall status and SSH settings.
- `POST /system/api-keys/rotate`: Generates a new master API key.

## systemd Integration

The API interacts with systemd via the `systemctl` CLI or the `dbus` Python bindings. It is limited to a whitelist of NeuralDrive-specific services to prevent unauthorized modification of core OS components.

## Development and Testing

The API can be run locally for development:
```bash
# With venv active
uvicorn main:app --host 0.0.0.0 --port 3001
```

Testing is handled via `pytest` in the `tests/test_api.py` file. These tests mock the system calls to ensure the API logic is correct without needing a full NeuralDrive environment.

> **Warning**: The System API runs as a privileged user (`neuraldrive-api`) with specific sudo permissions to manage services. Never expose port 3001 directly to the internet; always route traffic through the Caddy proxy.


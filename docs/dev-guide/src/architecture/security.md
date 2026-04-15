*This chapter is for contributors and maintainers.*

# Security Model

The NeuralDrive security model is built on the principle of defense-in-depth. As an appliance that often handles sensitive or private data, the system must protect against both external network attacks and local privilege escalation.

## Threat Model

The primary threats NeuralDrive is designed to mitigate include:
- **Unauthorized Inference**: Using the LLM without a valid API key.
- **System Tampering**: Unauthorized changes to the system configuration or service units.
- **Data Exfiltration**: Accessing stored model weights or user chat history.
- **Denial of Service**: Exhausting system resources (GPU VRAM or system memory) through malicious requests.

## Defense Layers

### 1. Service Isolation
Each major component runs as a dedicated, non-root user. This limits the "blast radius" if a single service is compromised.

| Service | User | UID |
|---------|------|-----|
| Ollama  | `neuraldrive-ollama` | 901 |
| WebUI   | `neuraldrive-webui`  | 902 |
| Caddy   | `neuraldrive-caddy`  | 903 |
| Monitor | `neuraldrive-monitor`| 904 |
| System API | `neuraldrive-api` | 905 |

### 2. systemd Hardening
Every service unit employs advanced systemd hardening directives:
- `ProtectSystem=strict`: The root filesystem is read-only for the service.
- `ProtectHome=yes`: Access to `/home` is denied.
- `PrivateTmp=yes`: A private `/tmp` directory is created.
- `NoNewPrivileges=yes`: Prevents the service and its children from gaining new privileges via `setuid` binaries.
- `DeviceAllow`: Only the necessary GPU devices (`/dev/nvidia*`, `/dev/dri/*`) are permitted for the Ollama service.

### 3. Authentication and Authorization
NeuralDrive uses a dual-key system for authentication:
- **Admin Password**: Used for local TUI access and the initial WebUI account creation.
- **API Key**: A 32-character token (prefixed with `nd-`) used for all programmatic access to the inference and system APIs.

The System API key is stored in `/etc/neuraldrive/api.key` with `0600` permissions, owned by the `neuraldrive-api` user.

### 4. Transport Layer Security (TLS)
All network communication is encrypted via TLS 1.3. The system generates a unique CA and server certificate during the first-boot process. Caddy enforces HTTPS for all routes.

## SSH Security

SSH is disabled by default. When enabled via the System API:
- Only key-based authentication is permitted.
- Only the `neuraldrive-admin` user is allowed to log in.
- `fail2ban` monitors logs and bans IPs after three failed attempts.

## Immutable OS

The read-only SquashFS root filesystem prevents persistent malware from being installed on the system. Any changes made to the system directories (outside of the persistence layer) are discarded on reboot.

> **Warning**: Security is a shared responsibility. While NeuralDrive provides a hardened base, users must ensure their API keys are kept secret and that physical access to the appliance is restricted.


*This chapter is for system administrators.*

# Security

The security design of NeuralDrive is built on principles of defense in depth and minimal attack surface. Each component is isolated and operates with only the necessary privileges.

## Security Design Principles

NeuralDrive implements several key security architectural features:
- **Defense in Depth**: Multiple layers of security control from the kernel to the application.
- **Minimal Attack Surface**: Only essential services are exposed.
- **Read-Only Root**: The core system is a SquashFS image.
- **Default-Deny Networking**: All incoming traffic is blocked except for required services.
- **No Default Passwords**: Credentials are unique to each installation or rely on key-based authentication.

## Default Security Posture

By default, the system-level firewall blocks all incoming traffic except for:
- HTTPS (port 443)
- System API (port 8443)
- mDNS (port 5353)

SSH is disabled by default and requires manual activation.

## Service Isolation

Every major service in NeuralDrive runs as a dedicated, low-privilege user account. Systemd hardening is applied to each unit to restrict access to the rest of the system.

| Service | User | UID |
| --- | --- | --- |
| neuraldrive-ollama | neuraldrive-ollama | 901 |
| neuraldrive-webui | neuraldrive-webui | 902 |
| neuraldrive-caddy | neuraldrive-caddy | 903 |
| neuraldrive-monitor | neuraldrive-monitor | 904 |
| neuraldrive-api | neuraldrive-api | 905 |

The systemd units for these services employ several hardening flags:
- `ProtectSystem=full`: Makes `/usr`, `/boot`, and `/etc` read-only for the service.
- `NoNewPrivileges=true`: Prevents the service from gaining more privileges via `setuid`.
- `PrivateTmp=true`: Gives the service its own `/tmp` directory.

## Data Protection and Permissions

NeuralDrive enforces a strict file permissions model to protect sensitive data:
- **Models**: Owned by `neuraldrive-ollama:neuraldrive-ollama` with `640` permissions.
- **Configurations**: Owned by `root:neuraldrive-admin` with `640` permissions.
- **Credentials**: Owned by `root:root` with `600` permissions.

## Audit Logging

System audit logs are maintained for monitoring security events. Logs are stored in JSON format for easy programmatic analysis.

Log file: `/var/log/neuraldrive/audit.log`

Log rotation is handled daily with a maximum of 7 rotations and a 100MB limit per file.

[Firewall](firewall.md)
[TLS Certificates](tls-certs.md)
[SSH Access](ssh.md)
[LUKS Encryption](../advanced/encryption.md)

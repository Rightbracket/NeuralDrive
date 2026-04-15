# 05-security.md — Security Architecture & Hardening

This document defines the implementation plan for securing the NeuralDrive headless inference server.

## Section 1: Security Design Principles
- **Defense in depth**: Multi-layered protection using nftables (network), systemd (process), and application-level authentication.
- **Minimal attack surface**: Only essential services (Caddy, Ollama, WebUI) run by default. SSH is disabled by default.
- **Read-only root**: The SquashFS base system prevents persistent changes to the OS core.
- **Default-deny networking**: The firewall blocks all incoming traffic except for dashboard (443/8443) and discovery (5353).
- **No default passwords**: Admin credentials and API keys are unique to each installation and generated during the first-boot sequence.

## Section 2: Firewall Configuration (nftables)
The firewall is managed by `nftables`. The configuration resides at `/etc/neuraldrive/nftables.conf`.

### nftables.conf
```nftables
#!/usr/sbin/nft -f

flush ruleset

table inet filter {
    chain input {
        type filter hook input priority 0; policy drop;

        # Allow established and related connections
        ct state established,related accept

        # Allow loopback
        iifname "lo" accept

        # ICMP rate limiting
        ip protocol icmp icmp type echo-request limit rate 5/second accept
        ip6 nexthdr icmpv6 icmpv6 type echo-request limit rate 5/second accept

        # TCP 443/8443 — Caddy (Web Dashboard & API)
        tcp dport { 443, 8443 } accept

        # TCP 22 — SSH (With Rate Limiting)
        tcp dport 22 ct state new limit rate 3/minute burst 5 packets accept

        # UDP 5353 — mDNS/Avahi (Local Network Discovery, rate-limited)
        udp dport 5353 limit rate 10/second accept
    }

    chain forward {
        type filter hook forward priority 0; policy drop;
    }

    chain output {
        type filter hook output priority 0; policy accept;
    }
}
```

### Integration
- **Service**: `nftables.service` (Standard Debian service)
- **User overrides**: `/etc/neuraldrive/firewall-custom.conf` is included at the end of the main ruleset if it exists.

## Section 3: Service Isolation
Services are decoupled into dedicated system users and hardened using systemd directives.

### Service Users
- `neuraldrive-ollama` (uid 901)
- `neuraldrive-webui` (uid 902)
- `neuraldrive-caddy` (uid 903)
- `neuraldrive-monitor` (uid 904)
- `neuraldrive-api` (uid 905) — System Management API

### systemd Hardening Template
Every `neuraldrive-*` service unit must include these directives:
```ini
[Service]
User=neuraldrive-<service>
Group=neuraldrive-<service>
ProtectSystem=strict
ProtectHome=yes
NoNewPrivileges=yes
PrivateTmp=yes
PrivateDevices=yes
ProtectKernelTunables=yes
ProtectControlGroups=yes
RestrictNamespaces=yes
MemoryDenyWriteExecute=yes
CapabilityBoundingSet=
SystemCallFilter=@system-service
SystemCallErrorNumber=EPERM
ReadOnlyPaths=/
ReadWritePaths=/etc/neuraldrive/ /var/log/neuraldrive/
```
*Note: `neuraldrive-ollama` is granted `PrivateDevices=no` and `DeviceAllow=/dev/nvidia* rw` / `DeviceAllow=/dev/dri/* rw` to access GPU hardware.*

## Section 4: TLS & Certificate Management
NeuralDrive defaults to HTTPS for all external communications.

### generate-certs.sh
```bash
#!/bin/bash
# /usr/lib/neuraldrive/generate-certs.sh
CERT_DIR="/etc/neuraldrive/tls"
mkdir -p "$CERT_DIR"

# Detect primary IP address for SAN inclusion
IP_ADDR=$(ip -4 route get 1 2>/dev/null | awk '{print $7; exit}')
SAN="DNS:neuraldrive.local,DNS:neuraldrive"
if [ -n "$IP_ADDR" ]; then
    SAN="${SAN},IP:${IP_ADDR}"
fi

openssl req -x509 -newkey rsa:4096 -sha256 -days 365 -nodes \
  -keyout "$CERT_DIR/server.key" -out "$CERT_DIR/server.crt" \
  -subj "/C=US/ST=State/L=City/O=NeuralDrive/CN=neuraldrive.local" \
  -addext "subjectAltName=${SAN}"
chmod 600 "$CERT_DIR/server.key"

# Also export CA cert for clients to trust
cp "$CERT_DIR/server.crt" "$CERT_DIR/neuraldrive-ca.crt"
chmod 644 "$CERT_DIR/neuraldrive-ca.crt"
echo "Certificate generated. SAN: ${SAN}"
echo "Client CA cert: ${CERT_DIR}/neuraldrive-ca.crt"
```

### systemd Service: `neuraldrive-certs.service`
This oneshot service runs before Caddy starts, generating certificates only if they don't already exist. Certificates are persisted across reboots (stored under `/etc/neuraldrive/tls/` which is on the persistence partition).

```ini
[Unit]
Description=NeuralDrive TLS Certificate Generation
After=local-fs.target network-online.target
Wants=network-online.target
Before=neuraldrive-caddy.service

[Service]
Type=oneshot
ExecCondition=/bin/sh -c '! test -f /etc/neuraldrive/tls/server.crt'
ExecStart=/usr/lib/neuraldrive/generate-certs.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

**Notes**:
- `ExecCondition` skips certificate generation if certs already exist (idempotent).
- `After=network-online.target` ensures the IP address is available for SAN inclusion.
- Caddy declares `Requires=neuraldrive-certs.service` and `After=neuraldrive-certs.service` to ensure certs exist before it starts.
- To regenerate certificates (e.g., after IP change), delete the cert files and restart: `sudo rm /etc/neuraldrive/tls/server.* && sudo systemctl restart neuraldrive-certs neuraldrive-caddy`.

### Caddyfile TLS
```caddyfile
# /etc/neuraldrive/Caddyfile
{
    admin off
}

neuraldrive.local:443 {
    tls /etc/neuraldrive/tls/server.crt /etc/neuraldrive/tls/server.key
    reverse_proxy localhost:3000
}
```

## Section 5: Authentication & Authorization
Credentials are set during the first-boot phase and stored in `/etc/neuraldrive/credentials.conf` (chmod 600).

- **First-boot behavior**:
  1. A random 16-character alphanumeric admin password is generated.
  2. A 32-character API key is generated for direct Ollama/WebUI API access.
  3. These values are stored and displayed on the TTY console.
- **Open WebUI**: Registration is disabled (`ENABLE_SIGNUP=False`). The initial admin account is provisioned via the environment variables `ADMIN_EMAIL` and `INITIAL_ADMIN_PASSWORD`.
- **API Access**: Managed via the `neuraldrive-apikey` TUI utility.

## Section 6: SSH Hardening
SSH is inactive by default. It can be enabled via `neuraldrive.ssh=1` in `/proc/cmdline` or via the TUI.

### SSH Config (`/etc/ssh/sshd_config.d/neuraldrive.conf`)
```sshconfig
Port 22
PasswordAuthentication no
PubkeyAuthentication yes
PermitRootLogin no
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
AllowUsers neuraldrive-admin
```

### fail2ban Config (`/etc/fail2ban/jail.d/neuraldrive.conf`)
```ini
[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log
maxretry = 5
bantime = 600
findtime = 600
```

## Section 7: Data Protection
- **Encryption**: If enabled at boot, the USB persistence partition is formatted as a LUKS2 volume. The passphrase is requested on the TUI at every boot.
- **Permissions**:
  - Models: `neuraldrive-ollama:neuraldrive-ollama` (640)
  - Configs: `root:neuraldrive-admin` (640)
  - Credentials: `root:root` (600)

## Section 8: Audit Logging
Audit logs are stored in `/var/log/neuraldrive/audit.log` and structured as JSON.

### logrotate.conf
```
/var/log/neuraldrive/*.log {
    daily
    rotate 7
    size 100M
    compress
    delaycompress
    missingok
    notifempty
}
```

## Section 9: Updates
NeuralDrive is a LiveCD system. Security updates are delivered via new image releases. The file `/etc/neuraldrive/version` contains the build timestamp and a package manifest hash for verification.

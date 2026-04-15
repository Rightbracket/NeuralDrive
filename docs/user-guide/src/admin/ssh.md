*This chapter is for system administrators.*

# SSH Access

SSH access is disabled by default in NeuralDrive. This minimizes the initial attack surface and ensures that users must explicitly opt-in to remote command-line management.

## Enabling SSH

SSH can be enabled through three primary methods:
- **TUI (Terminal User Interface)**: Use the Services or Security menu to toggle SSH.
- **Boot Parameter**: Add `neuraldrive.ssh=1` to the kernel command line (e.g., in `/proc/cmdline`) during the boot process.
- **System API**: Send a `POST` request to `/system/ssh/enable` using an authenticated API client.

## SSH Configuration and Security

The system uses a hardened SSH configuration located at `/etc/ssh/sshd_config.d/neuraldrive.conf`.

- **Authentication**: Key-only authentication is enforced. Password authentication is disabled (`PasswordAuthentication no`).
- **User Restrictions**: Only the `neuraldrive-admin` user is permitted to log in (`AllowUsers neuraldrive-admin`).
- **Root Login**: Root login is strictly prohibited (`PermitRootLogin no`).
- **Session Settings**: `MaxAuthTries 3`, `ClientAliveInterval 300`, and `ClientAliveCountMax 2` are set to ensure session integrity and prevent brute-force attempts.

## Adding SSH Keys

Public SSH keys should be placed in the authorized keys file:

```bash
/etc/neuraldrive/ssh/authorized_keys
```

Alternatively, keys can be injected into this location during the image building process.

## Brute-Force Protection

In addition to the rate-limiting provided by the firewall, `fail2ban` monitors SSH login attempts. The configuration is located at `/etc/fail2ban/jail.d/neuraldrive.conf`.

- **Max Retries**: 5 failed attempts.
- **Ban Time**: 600 seconds.
- **Find Time**: 600 seconds.

## Firewall Rate-Limiting

The system firewall (`nftables`) further protects the SSH port by rate-limiting new connections to 3 per minute with a burst allowance of 5 packets.

## See Also

- [Security](security.md) — NeuralDrive security architecture and hardening overview.
- [Firewall](firewall.md) — nftables configuration and port management.

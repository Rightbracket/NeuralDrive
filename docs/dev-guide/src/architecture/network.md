*This chapter is for contributors and maintainers.*

# Network Architecture

NeuralDrive is designed to operate as a secure network appliance. It uses a combination of Caddy for edge routing, Avahi for service discovery, and nftables for firewalling.

## Edge Proxy (Caddy)

Caddy serves as the single point of entry for all network traffic. It listens on port 443 and manages the following internal routing:

| External Path | Internal Destination | Purpose |
|---------------|----------------------|---------|
| `/`           | `localhost:3000`     | Open WebUI |
| `/v1/*`       | `localhost:11434`    | Ollama OpenAI-compatible API |
| `/api/*`      | `localhost:11434`    | Ollama Native API |
| `/system/*`   | `localhost:3001`     | System API (FastAPI) |
| `/monitor/*`  | `localhost:1312`     | GPU Hot Dashboard |
| `/health`     | `200 OK`             | Liveness Probe |

### Multiplexed API Port (8443)
In addition to the standard HTTPS port, NeuralDrive can be configured to listen on port 8443 specifically for programmatic API access. This helps separate browser traffic from automated scripts or external integrations.

## Service Discovery (mDNS)

To simplify headless access, NeuralDrive runs `avahi-daemon`. By default, the appliance advertises itself as `neuraldrive.local`. This allows users to access the WebUI at `https://neuraldrive.local` without needing to know the IP address.

The mDNS name can be changed via the System API or the first-boot wizard.

## Firewall (nftables)

The system uses `nftables` with a "default drop" policy. The firewall configuration is managed via `/etc/nftables.conf` and a custom drop-in at `/etc/nftables.service.d/neuraldrive.conf`.

### Permitted Traffic
- **Inbound TCP 443/8443**: WebUI and API access.
- **Inbound TCP 22**: SSH (rate-limited to 3 attempts per minute).
- **Inbound UDP 5353**: mDNS for service discovery.
- **Inbound ICMP**: Echo requests (rate-limited to 5 per second).
- **Outbound**: All traffic permitted (required for downloading models and system updates).

## Internal Port Assignments

Services are bound to `localhost` whenever possible to ensure they are only accessible via the Caddy proxy or the local TUI.

- **3000**: Open WebUI
- **3001**: System API (FastAPI)
- **11434**: Ollama
- **1312**: GPU Monitor

> **Note**: The System API and Ollama services enforce their own authentication (API keys), but Caddy provides the first layer of defense by requiring valid TLS and potentially enforcing IP-based allowlists.


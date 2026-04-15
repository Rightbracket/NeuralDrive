*Audience: Everyone*

# Network & mDNS Troubleshooting

This guide addresses connectivity issues between your client machine and the NeuralDrive appliance.

## mDNS and Hostname Resolution

### `neuraldrive.local` doesn't resolve

The `neuraldrive.local` address uses Multicast DNS (mDNS) for discovery.

1.  **Client Software**: Ensure your client has mDNS support. Windows (via Bonjour), macOS (native), and Linux (Avahi) are supported.
2.  **Network Hardware**: Some routers or managed switches block multicast traffic (UDP 5353).
3.  **Corporate Networks**: mDNS is often disabled or filtered on enterprise-grade networks.
4.  **Workaround**: Use the direct IP address shown on the NeuralDrive console (TUI).

## TLS and Certificates

### HTTPS certificate warning

NeuralDrive uses self-signed certificates for end-to-end encryption. Browsers will display a "Your connection is not private" warning.

1.  **Expected Behavior**: This warning is expected when using the default self-signed CA.
2.  **CA Installation**: To resolve this, download the CA certificate and add it to your browser or OS trust store.
    -   **Path**: `/etc/neuraldrive/tls/neuraldrive-ca.crt`
    -   **URL**: `https://<IP>:8443/system/ca-cert`
3.  **Custom Certificates**: You can replace the default certificates in `/etc/neuraldrive/tls/` with your own.

## Wi-Fi Configuration

1.  **Supported hardware**: Most Intel and Realtek Wi-Fi chipsets are supported via NetworkManager.
2.  **TUI Configuration**: Use the "Network" menu in the TUI to scan and connect to access points.
3.  **Command Line**: Advanced users can use `nmcli dev wifi connect <SSID> password <PASSWORD>` for manual association.

## Firewall and Ports

### Can't connect from another machine

1.  **Port Access**: Ensure the following ports are open on the host firewall (nftables):
    -   **443**: Web UI Dashboard.
    -   **8443**: API Gateway and System Panel.
2.  **Ping Test**: Verify basic ICMP connectivity with `ping <IP_ADDRESS>`. If pings are successful but port 443 fails, the web server (Caddy) may be offline.

> **Note**: For more information on configuring networking and firewall rules, see [Network Configuration](../admin/network.md) and [TLS Certificate Trust](../api/tls-trust.md).

*This chapter is for system administrators.*

# Network Configuration

NeuralDrive uses NetworkManager for managing both wired and wireless interfaces. By default, the system attempts to obtain an IP address via DHCP.

## Static IP Configuration

If a static IP address is required, it can be configured using the TUI (Terminal User Interface) or via the command line with `nmcli`.

To configure a static IP using `nmcli`, identify the connection name:

```bash
nmcli connection show
```

Apply the static configuration:

```bash
sudo nmcli connection modify "Wired connection 1" \
  ipv4.addresses 192.168.1.100/24 \
  ipv4.gateway 192.168.1.1 \
  ipv4.dns "1.1.1.1,8.8.8.8" \
  ipv4.method manual
sudo nmcli connection up "Wired connection 1"
```

## Hostname Configuration

The default hostname is `neuraldrive`. To change the hostname, use `hostnamectl` or the TUI:

```bash
sudo hostnamectl set-hostname my-neural-node
```

## mDNS and Avahi

NeuralDrive automatically advertises its presence on the local network using mDNS (Multicast DNS) via Avahi. By default, the system is reachable at `neuraldrive.local`.

Avahi service files are located at:
- `/etc/avahi/services/neuraldrive-web.service` (port 443)
- `/etc/avahi/services/neuraldrive-api.service` (port 8443)

The system uses `systemd-resolved` with mDNS support enabled to handle local name resolution.

> **Warning**: mDNS does not work on all networks. Corporate environments, certain routers, and VPNs often block multicast traffic. If `neuraldrive.local` is unreachable, check the IP address on the physical console.

## Console IP Display

At boot, the `neuraldrive-show-ip.service` runs to detect the active IP address and display it directly on the console. This ensures that the node can be located even if mDNS fails or DHCP assigns an unexpected address.

[First Boot Setup](../getting-started/first-boot.md)
[Network Troubleshooting](../troubleshooting/network.md)

*This chapter is for system administrators.*

# Firewall

NeuralDrive uses `nftables` as the primary firewall. The configuration is designed to block all unsolicited incoming traffic while allowing essential system services.

## Default Policy

The firewall is configured with a strict default-deny policy for incoming and forwarded traffic.

- **Input Chain**: `policy drop`
- **Forward Chain**: `policy drop`
- **Output Chain**: `policy accept`

## Allowed Traffic

The default ruleset permits the following incoming connections:
- **Established and Related**: Existing outbound sessions.
- **Loopback**: Traffic within the system.
- **ICMP**: Rate-limited echo requests (5 per second).
- **Web Services**: TCP ports 443 (HTTPS) and 8443 (System API).
- **SSH**: TCP port 22, rate-limited to 3 new connections per minute with a burst of 5.
- **mDNS**: UDP port 5353, rate-limited to 10 per second for local service discovery.

## Configuration Files

The primary firewall rules are defined in `/etc/neuraldrive/nftables.conf`.

```nftables
#!/usr/sbin/nft -f
flush ruleset
table inet filter {
    chain input {
        type filter hook input priority 0; policy drop;
        ct state established,related accept
        iifname "lo" accept
        ip protocol icmp icmp type echo-request limit rate 5/second accept
        ip6 nexthdr icmpv6 icmpv6 type echo-request limit rate 5/second accept
        tcp dport { 443, 8443 } accept
        tcp dport 22 ct state new limit rate 3/minute burst 5 packets accept
        udp dport 5353 limit rate 10/second accept
    }
    chain forward { type filter hook forward priority 0; policy drop; }
    chain output { type filter hook output priority 0; policy accept; }
}
```

Administrators can add custom rules by creating `/etc/neuraldrive/firewall-custom.conf`. If this file exists, it is included at the end of the ruleset.

## Managing the Firewall

To view the active ruleset:

```bash
sudo nft list ruleset
```

To reload the configuration after making changes:

```bash
sudo systemctl restart nftables
```

[Security](security.md)
[SSH Access](ssh.md)

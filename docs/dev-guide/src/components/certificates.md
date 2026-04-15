*This chapter is for contributors and maintainers.*

# Certificate Generation

NeuralDrive includes an automated system for managing TLS certificates, ensuring that all network communication is encrypted from the moment the appliance first boots.

## The generate-certs.sh Script

The `generate-certs.sh` script is located at `/usr/lib/neuraldrive/generate-certs.sh`. It is executed by the `neuraldrive-certs.service`.

### Certificate Parameters
The script uses `openssl` to generate a self-signed Root CA and a Server Certificate with the following parameters:
- **Algorithm**: RSA 4096-bit.
- **Digest**: SHA-256.
- **Validity**: 365 days.
- **Subject Alternative Names (SAN)**:
  - `DNS:neuraldrive.local`
  - `DNS:<hostname>.local`
  - `IP:<eth0_ip>`
  - `IP:127.0.0.1`

## Certificate Storage

All certificate material is stored in the persistent directory `/etc/neuraldrive/tls/`:
- `neuraldrive-ca.crt`: The public Root CA certificate. Users should install this on their client machines to trust the appliance.
- `server.crt`: The certificate presented by Caddy to clients.
- `server.key`: The private key for the server certificate (Permission `0600`).
- `ca.key`: The private key for the Root CA (Permission `0600`).

## Persistence and Regeneration

The certificates are generated once during the first-boot process. Because they are stored on the persistence partition, they survive system updates.

### Regeneration Triggers
The `neuraldrive-certs.service` uses an `ExecCondition` that checks for the existence of `/etc/neuraldrive/tls/server.crt`. If the file is present, the service exits without action. A new certificate is generated only if:
1. The server certificate file has been manually deleted.
2. The system is performing its first boot and no certificates exist yet.

## Exporting the CA

To allow client browsers to connect without security warnings, the `neuraldrive-ca.crt` can be downloaded via the System API at `GET /system/ca-cert`. 

> **Warning**: Never share or export the `.key` files. If the private keys are compromised, the security of the appliance's network communication is invalidated.


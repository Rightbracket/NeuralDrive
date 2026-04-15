*This chapter is for system administrators.*

# TLS Certificates

NeuralDrive uses TLS to encrypt all communication between clients and the node. Certificates are automatically managed to ensure secure defaults without requiring manual intervention.

## Automatic Generation

The `neuraldrive-certs.service` is responsible for certificate management. This is a oneshot service that runs at first boot and before the Caddy web server starts.

The certificate generation is idempotent. The service uses an `ExecCondition` to check for existing certificates and only generates new ones if they are missing.

## Certificate Details

The generated certificates are self-signed RSA 4096-bit with SHA-256 signatures. They have a 365-day validity period and include the following Subject Alternative Names (SANs):
- `DNS:neuraldrive.local`
- `DNS:neuraldrive`
- `IP:<detected-IP>`

## Certificate Files

Certificates and keys are stored in `/etc/neuraldrive/tls/`.

| File | Permissions | Description |
| --- | --- | --- |
| `server.crt` | 644 | The server certificate. |
| `server.key` | 600 | The private key for the server certificate. |
| `neuraldrive-ca.crt` | 644 | The root CA certificate used to sign the server certificate. |

## Client Trust

To avoid browser warnings and ensure secure programmatic access, the CA certificate can be downloaded and installed in the client's trust store.

The CA certificate is available at:
- `https://<IP>:8443/system/ca-cert` (no authentication required)
- `/etc/neuraldrive/tls/neuraldrive-ca.crt` (on the filesystem)

## Manual Management

### Regenerating Certificates

If certificates need to be regenerated (e.g., due to a hostname change), delete the existing files and restart the certificate service:

```bash
sudo rm /etc/neuraldrive/tls/server.*
sudo systemctl restart neuraldrive-certs neuraldrive-caddy
```

### Using Custom Certificates

To use certificates issued by a third-party CA:
1. Replace `server.crt` and `server.key` in `/etc/neuraldrive/tls/` with your custom files.
2. Ensure the file names match and permissions are correctly set (644 for the certificate, 600 for the key).
3. Restart Caddy: `sudo systemctl restart neuraldrive-caddy`.

[TLS Certificate Trust](../api/tls-trust.md)
[Security](security.md)

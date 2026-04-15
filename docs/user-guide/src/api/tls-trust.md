*This chapter is for developers and administrators.*

# TLS Trust

NeuralDrive uses TLS to secure all communications between your client and the server. Because NeuralDrive is a local-first system, it employs a self-signed certificate rather than one from a public Certificate Authority (CA). To establish a secure connection, you must instruct your tools and operating system to trust the NeuralDrive CA.

## Why Self-Signed?

Standard CAs like Let's Encrypt require a public domain name and a publicly reachable server to verify ownership. NeuralDrive is designed to operate on local networks, often without a public DNS record. A self-signed CA allows NeuralDrive to generate valid certificates for `neuraldrive.local`, local IP addresses, and custom hostnames without external dependencies.

## Downloading the CA Certificate

You can retrieve the CA certificate (`neuraldrive-ca.crt`) using one of three methods:

1.  **SCP (Recommended):** Use secure copy to pull the file directly from the NeuralDrive server.
    `scp <username>@neuraldrive.local:/etc/neuraldrive/tls/neuraldrive-ca.crt ./`
2.  **System API:** Download the certificate via the management endpoint.
    `curl -k -H "Authorization: Bearer <API_KEY>" https://neuraldrive.local:8443/system/ca-cert -o neuraldrive-ca.crt`
3.  **Local Filesystem:** If you have direct terminal access to the NeuralDrive machine, the file is located at `/etc/neuraldrive/tls/neuraldrive-ca.crt`.

## Installing the Certificate

### Operating System Level

Installing the CA at the OS level allows browsers and many native applications to trust NeuralDrive automatically.

*   **macOS:**
    1.  Open **Keychain Access**.
    2.  Drag `neuraldrive-ca.crt` into the **System** keychain.
    3.  Double-click the certificate, expand **Trust**, and set **When using this certificate** to **Always Trust**.
*   **Linux (Ubuntu/Debian):**
    1.  `sudo cp neuraldrive-ca.crt /usr/local/share/ca-certificates/neuraldrive.crt`
    2.  `sudo update-ca-certificates`
*   **Windows:**
    1.  Double-click `neuraldrive-ca.crt`.
    2.  Click **Install Certificate...**
    3.  Select **Local Machine** and click **Next**.
    4.  Select **Place all certificates in the following store** and browse for **Trusted Root Certification Authorities**.

### Tool-Specific Configuration

Many development environments maintain their own certificate stores or require explicit paths.

*   **Python (requests/httpx/OpenAI SDK):**
    Set the environment variable: `export REQUESTS_CA_BUNDLE=/path/to/neuraldrive-ca.crt`
    Or `export SSL_CERT_FILE=/path/to/neuraldrive-ca.crt`
*   **Node.js:**
    Set the environment variable: `export NODE_EXTRA_CA_CERTS=/path/to/neuraldrive-ca.crt`
*   **cURL:**
    Use the `--cacert` flag: `curl --cacert neuraldrive-ca.crt ...`

## Certificate Management

### Regeneration

If your server's IP address changes or the certificate expires, you can force a regeneration by deleting the existing server certificates and restarting the certificate services:

```bash
sudo rm /etc/neuraldrive/tls/server.crt /etc/neuraldrive/tls/server.key
sudo systemctl restart neuraldrive-certs neuraldrive-caddy
```

This will generate a new server certificate signed by the existing CA.

### Custom Certificates

If you prefer to use your own certificate (e.g., from a corporate CA), replace the files in `/etc/neuraldrive/tls/server.crt` and `/etc/neuraldrive/tls/server.key` and restart the `neuraldrive-caddy` service. Note that the `neuraldrive-certs` service should be disabled to prevent it from overwriting your custom files on reboot.

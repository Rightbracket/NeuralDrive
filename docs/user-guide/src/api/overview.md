*This chapter assumes familiarity with REST APIs.*

# API Overview

NeuralDrive exposes a comprehensive set of APIs to facilitate integration with external tools, coding agents, and custom scripts. By default, all API traffic is served over TLS on a unified public port.

## Base URLs and Ports

The primary entry point for all external communication is port **8443**. This port is managed by a Caddy reverse proxy that handles TLS termination and directs traffic to the appropriate internal services.

| API Type | Path Prefix | Internal Port | Description |
|----------|-------------|---------------|-------------|
| OpenAI Compatible | `/v1/` | 11434 | Compatible with standard OpenAI SDKs and integrations. |
| Ollama Native | `/api/` | 11434 | Direct access to native Ollama features and model management. |
| System Management | `/system/` | 3001 | NeuralDrive-specific administrative and management operations. |

The base URL for most integrations is:
`https://neuraldrive.local:8443`

## Authentication

NeuralDrive uses Bearer token authentication for all API requests. You must include your API key in the `Authorization` header.

**Header Format:**
`Authorization: Bearer <API_KEY>`

**Key Format:**
API keys follow the pattern `nd-xxxxxxxxxxxxxxxx`. You can find your key in `/etc/neuraldrive/api.key` or rotate it using the System Management API. Refer to the [API Keys](./api-keys.md) chapter for details on management and rotation.

## TLS and Security

All external connections require TLS. NeuralDrive generates a self-signed certificate on first boot with Subject Alternative Names (SAN) for `neuraldrive.local`, the local hostname, and the detected IP address.

To establish a secure connection, clients should trust the NeuralDrive Certificate Authority (CA). You can download the CA certificate via SCP from `/etc/neuraldrive/tls/neuraldrive-ca.crt` or through the `/system/ca-cert` endpoint. Detailed installation steps are available in the [TLS Trust](./tls-trust.md) chapter.

## Rate Limits and Timeouts

To ensure system stability, NeuralDrive enforces the following limits:

*   **Rate Limit:** 100 requests per minute per source IP address.
*   **Generation Timeout:** 600 seconds (10 minutes) for inference tasks.
*   **Management Timeout:** 30 seconds for administrative operations via the System API.

## Internal Access

While port 8443 is the recommended public interface, services are also available on internal ports for local debugging or specialized networking configurations:

*   **Ollama:** 11434
*   **WebUI:** 3000
*   **System API:** 3001

Note that these internal ports typically do not have the same TLS or authentication protections as the public 8443 interface.

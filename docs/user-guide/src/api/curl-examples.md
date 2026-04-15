*This chapter assumes basic command-line familiarity.*

# cURL Examples

Using `curl` is the quickest way to verify your connection to the NeuralDrive API or perform one-off administrative tasks. All examples assume you have downloaded the NeuralDrive CA certificate (`neuraldrive-ca.crt`) to your current directory.

## Trusting the Certificate

NeuralDrive uses a self-signed certificate. For security, we recommend using the `--cacert` flag to point to the CA certificate.

*   **Recommended (Secure):** `curl --cacert neuraldrive-ca.crt ...`
*   **Alternative (Insecure):** `curl -k ...` (Only use for quick health checks)

## OpenAI-Compatible API

These endpoints follow the standard OpenAI request and response formats.

### Chat Completion

```bash
curl --cacert neuraldrive-ca.crt \
  -X POST https://neuraldrive.local:8443/v1/chat/completions \
  -H "Authorization: Bearer nd-xxxxxxxxxxxxxxxxxxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1:8b",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### List Available Models

```bash
curl --cacert neuraldrive-ca.crt \
  -H "Authorization: Bearer nd-xxxxxxxxxxxxxxxxxxxx" \
  https://neuraldrive.local:8443/v1/models
```

## Ollama Native API

Directly interact with the underlying Ollama service for tasks like pulling models.

### Pull a Model

```bash
curl --cacert neuraldrive-ca.crt \
  -X POST https://neuraldrive.local:8443/api/pull \
  -H "Authorization: Bearer nd-xxxxxxxxxxxxxxxxxxxx" \
  -d '{"name": "mistral"}'
```

### Get Model Details

```bash
curl --cacert neuraldrive-ca.crt \
  -X POST https://neuraldrive.local:8443/api/show \
  -H "Authorization: Bearer nd-xxxxxxxxxxxxxxxxxxxx" \
  -d '{"name": "llama3.1:8b"}'
```

## Health and Management

### Health Check

The health endpoint is public and does not require an API key or certificate verification (though `-k` is used here for brevity).

```bash
curl -k https://neuraldrive.local:8443/health
```

### System CA Certificate

Download the CA certificate directly from the System API if you do not have SSH access. This endpoint is public and does not require authentication. Use `-k` to skip certificate verification — you cannot verify a certificate you have not yet downloaded.

```bash
curl -k https://neuraldrive.local:8443/system/ca-cert -o neuraldrive-ca.crt
```

Once you have the certificate, verify it by checking its fingerprint against the value displayed in the TUI or on the console during boot.

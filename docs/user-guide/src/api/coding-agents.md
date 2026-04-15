*This chapter assumes familiarity with REST APIs.*

# Coding Agents

NeuralDrive is designed to provide high-performance local inference for coding agents and IDE integrations. By following a standard OpenAI-compatible pattern, you can connect your favorite development tools to NeuralDrive with minimal configuration.

## Generic Configuration Pattern

Most coding agents use a common set of parameters for OpenAI-compatible providers:

*   **Provider:** OpenAI Compatible (or Custom)
*   **Base URL:** `https://neuraldrive.local:8443/v1`
*   **API Key:** `nd-xxxxxxxxxxxxxxxxxxxx`
*   **Model Name:** e.g., `llama3.1:8b`, `codestral`, or `starcoder2`

### Important Note on TLS Trust

Because NeuralDrive uses a self-signed certificate, most agents will fail to connect unless you explicitly trust the NeuralDrive CA. Before configuring your agent, ensure you have followed the steps in the [TLS Trust](./tls-trust.md) chapter to install the certificate on your local machine.

## Cursor

To use NeuralDrive with Cursor:

1.  Open Cursor Settings > Models.
2.  In the **OpenAI API** section, toggle the switch to **Enabled**.
3.  Click **Override OpenAI Base URL** and enter: `https://neuraldrive.local:8443/v1`
4.  Enter your NeuralDrive API key in the **API Key** field.
5.  Under **Models**, add your desired model names (e.g., `llama3.1:8b`).
6.  Ensure other OpenAI models are disabled if you wish to force local inference.

## Continue

For the Continue VS Code or JetBrains extension, edit your `config.json`:

```json
{
  "models": [
    {
      "title": "NeuralDrive",
      "provider": "openai",
      "baseUrl": "https://neuraldrive.local:8443/v1",
      "apiKey": "nd-xxxxxxxxxxxxxxxxxxxx",
      "model": "llama3.1:8b"
    }
  ]
}
```

If you experience TLS verification errors, you may need to set the `NODE_EXTRA_CA_CERTS` environment variable to point to your `neuraldrive-ca.crt` file before launching your IDE.

## Aider

Aider supports OpenAI-compatible endpoints through environment variables. Use the following command to start Aider with NeuralDrive:

```bash
export OPENAI_API_BASE=https://neuraldrive.local:8443/v1
export OPENAI_API_KEY=nd-xxxxxxxxxxxxxxxxxxxx
export REQUESTS_CA_BUNDLE=/path/to/neuraldrive-ca.crt

aider --model openai/llama3.1:8b
```

By setting `REQUESTS_CA_BUNDLE`, you ensure that Aider's underlying Python libraries trust the self-signed certificate.

## Open Interpreter

Open Interpreter can be configured to use NeuralDrive by specifying the base URL and model:

```bash
export SSL_CERT_FILE=/path/to/neuraldrive-ca.crt

interpreter --model openai/llama3.1:8b \
            --api_base https://neuraldrive.local:8443/v1 \
            --api_key nd-xxxxxxxxxxxxxxxxxxxx
```

Using `--api_base` directs traffic to NeuralDrive, while `SSL_CERT_FILE` handles the TLS verification requirements for the Python environment.

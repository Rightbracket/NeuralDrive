*Audience: Developers*

# API Endpoint Reference

NeuralDrive provides two primary interfaces for model inference: an OpenAI-compatible API for standard tool integration and the native Ollama API for low-level control.

## Authentication

All API requests must include the `nd-xxxx` API key in the `Authorization` header:

```http
Authorization: Bearer nd-xxxx
```

## OpenAI-Compatible API

**Base URL**: `https://<IP_ADDRESS>:8443/v1/`

| Method | Path | Description |
| :--- | :--- | :--- |
| `POST` | `/v1/chat/completions` | Chat completions (supports streaming). |
| `POST` | `/v1/completions` | Text completions for non-chat models. |
| `GET` | `/v1/models` | Lists all available local models. |
| `POST` | `/v1/embeddings` | Generates vector embeddings for a given input. |

### Chat Completion Example

```bash
curl https://neuraldrive.local:8443/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer nd-xxxx" \
  -d '{
    "model": "llama3:8b",
    "messages": [
      {"role": "user", "content": "How do I secure an API?"}
    ]
  }'
```

## Native Ollama API

**Base URL**: `https://<IP_ADDRESS>:8443/api/`

| Method | Path | Description |
| :--- | :--- | :--- |
| `POST` | `/api/generate` | Low-level text generation. |
| `POST` | `/api/chat` | Native chat completion format. |
| `GET` | `/api/tags` | List locally installed model tags. |
| `POST` | `/api/pull` | Download a new model from the registry. |
| `POST` | `/api/show` | Retrieve detailed model metadata. |
| `DELETE` | `/api/delete` | Remove a local model. |
| `POST` | `/api/copy` | Create a copy or alias of a model. |

### Native Chat Example

```bash
curl https://neuraldrive.local:8443/api/chat \
  -H "Authorization: Bearer nd-xxxx" \
  -d '{
    "model": "llama3:8b",
    "messages": [
      {"role": "user", "content": "Explain quantization."}
    ],
    "stream": false
  }'
```

> **Note**: For information on how to manage the NeuralDrive system itself (logs, services, networking), see the [System Management API reference](system-api-endpoints.md).

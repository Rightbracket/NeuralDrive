*This chapter assumes familiarity with REST APIs.*

# Ollama Native API

While the OpenAI-compatible API is recommended for most integrations, NeuralDrive also exposes the Ollama Native API for tasks that require finer control over model management and specialized inference parameters.

## Why Use the Native API?

The Native API is necessary for operations not covered by the OpenAI specification, such as:
*   Downloading (pulling) new models from the library.
*   Getting granular progress updates during model downloads.
*   Accessing detailed model metadata (modelfile, license, parameters).
*   Performing raw text generation without chat-specific formatting.

## Base URL and Auth

The Native API is available at the `/api/` path on port 8443. Like all other external APIs, it requires a Bearer token in the `Authorization` header.

Base URL: `https://neuraldrive.local:8443/api`

## Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/generate` | POST | Raw text completion. |
| `/chat` | POST | Structured chat completion. |
| `/tags` | GET | List all models currently available on the server. |
| `/pull` | POST | Download a model from the Ollama library. |
| `/show` | POST | View details, parameters, and the Modelfile for a specific model. |
| `/delete` | DELETE | Remove a model from local storage. |

## Remote Ollama CLI

You can use the standard `ollama` command-line tool to interact with your NeuralDrive instance remotely. This allows you to run models on the server using your local terminal.

To point your local CLI to NeuralDrive, set the `OLLAMA_HOST` environment variable:

```bash
export OLLAMA_HOST=https://neuraldrive.local:8443
ollama run llama3.1:8b
```

Note that the `ollama` CLI does not natively support Bearer token authentication in all versions. For secure remote CLI usage, we recommend using `curl` or a custom wrapper that includes the `Authorization: Bearer <API_KEY>` header.

## Pulling a Model via API

When pulling a model, NeuralDrive returns a stream of JSON objects indicating the progress:

```bash
curl --cacert neuraldrive-ca.crt \
  -X POST https://neuraldrive.local:8443/api/pull \
  -H "Authorization: Bearer nd-xxxxxxxxxxxxxxxxxxxx" \
  -d '{"name": "mistral"}'
```

The response will look similar to this:
```json
{"status":"pulling manifest"}
{"status":"pulling layer","digest":"sha256:e8a35d5...","total":5120000000,"completed":1024000}
...
{"status":"success"}
```

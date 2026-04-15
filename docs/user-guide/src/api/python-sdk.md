*This chapter assumes familiarity with Python.*

# Python SDK

NeuralDrive provides a seamless integration path for Python developers by maintaining compatibility with the official OpenAI Python library. This allows you to use familiar patterns while running inference entirely on local hardware.

## Installation

To get started, install the `openai` and `httpx` libraries:

```bash
pip install openai httpx
```

## Initializing the Client

Since NeuralDrive uses a self-signed certificate, you must configure the `OpenAI` client to trust the NeuralDrive CA. The most reliable way is to use an `httpx.Client` with the `verify` parameter set to the path of your `neuraldrive-ca.crt` file.

```python
from openai import OpenAI
import httpx

# Path to the CA certificate downloaded from NeuralDrive
CA_CERT_PATH = "/path/to/neuraldrive-ca.crt"

client = OpenAI(
    base_url="https://neuraldrive.local:8443/v1",
    api_key="nd-xxxxxxxxxxxxxxxxxxxx",
    http_client=httpx.Client(verify=CA_CERT_PATH)
)
```

## Chat Completions

NeuralDrive supports both streaming and non-streaming chat completions.

### Streaming Example

Streaming provides real-time feedback as the model generates text, which is ideal for interactive applications.

```python
response = client.chat.completions.create(
    model="llama3.1:8b",
    messages=[{"role": "user", "content": "Explain quantum entanglement."}],
    stream=True
)

for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

### Non-Streaming Example

For automated scripts where the full output is needed at once:

```python
response = client.chat.completions.create(
    model="llama3.1:8b",
    messages=[{"role": "user", "content": "Write a Python function to sort a list."}],
    stream=False
)

print(response.choices[0].message.content)
```

## Embeddings

You can generate text embeddings for RAG (Retrieval-Augmented Generation) applications using compatible models.

```python
response = client.embeddings.create(
    model="mxbai-embed-large",
    input="NeuralDrive provides high-performance local AI."
)

embedding = response.data[0].embedding
print(f"Generated embedding with {len(embedding)} dimensions.")
```

## Cert Trust Options

If you prefer not to specify the CA path in every script, you have three primary alternatives:

1.  **Environment Variables:** Set `REQUESTS_CA_BUNDLE` or `SSL_CERT_FILE` in your shell environment.
2.  **System-wide Install:** Add the CA certificate to your operating system's trusted store.
3.  **Disable Verification (Testing Only):** Set `verify=False` in the `httpx.Client`. This is insecure and not recommended for production.

## Error Handling

Implement basic error handling to manage timeouts or connection issues:

```python
import openai

try:
    response = client.chat.completions.create(
        model="llama3.1:8b",
        messages=[{"role": "user", "content": "Hi!"}]
    )
except openai.APIConnectionError as e:
    print(f"Could not connect to NeuralDrive: {e}")
except openai.AuthenticationError as e:
    print(f"Invalid API key: {e}")
except openai.APITimeoutError as e:
    print(f"Request timed out (NeuralDrive limit: 600s): {e}")
```

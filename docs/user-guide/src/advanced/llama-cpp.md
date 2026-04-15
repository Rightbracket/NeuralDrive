*Audience: Developers (advanced)*

# llama.cpp Server

While Ollama is the default model server for NeuralDrive, the system also includes the `llama-server` binary for users who require lower-level control or specialized inference features.

## When to Use llama.cpp

The `llama-server` is ideal for developers who need more granular configuration than the Ollama API provides.

| Feature | Ollama | llama.cpp |
| :--- | :--- | :--- |
| **Ease of Use** | High (Managed downloads) | Medium (Manual model placement) |
| **Model Format** | Managed Blobs | Direct GGUF loading |
| **Control** | Standardized API | Fine-grained sampling & batching |
| **Resource Usage** | Integrated Management | Lower overhead per instance |

## Enabling the Server

The `llama-server` is included in the base image but is not enabled by default. You can start it manually or configure a custom systemd service.

```bash
# Example command to start the llama.cpp server
llama-server --model /path/to/my-model.gguf --port 8080 --host 0.0.0.0
```

## Configuration Options

The server supports a wide variety of command-line flags to tune performance:

*   `--ctx-size`: (Integer) Define the maximum context window size.
*   `--n-gpu-layers`: (Integer) Specifically state how many layers to offload to the GPU.
*   `--threads`: (Integer) The number of CPU threads to utilize.
*   `--batch-size`: (Integer) Set the batch size for prompt processing.

## Important Note: Model Formats

It's important to understand the difference in model storage between the two servers. Ollama stores models in a proprietary blob format within `/var/lib/neuraldrive/models/`. These blobs are not directly compatible with the `llama-server`. To use a model with llama.cpp, you must provide a raw `.gguf` file.

For more information on model formats, see [Understanding LLM Models](../models/understanding-models.md). To further optimize your inference setup, refer to [Performance Tuning](performance.md).

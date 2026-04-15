*Audience: Everyone*

# Model Loading Issues

This guide covers issues related to downloading, loading, and running Large Language Models (LLMs).

## Download Failures

### "Downloads disabled"

If the system prevents downloading new models, it has likely detected it is running in "Live CD" (read-only) mode.

1.  **USB Mode Requirement**: You must run the system from a USB drive with a valid `persistence` partition to save downloaded models.
2.  **External Storage**: If persistence is not available, you can mount an external disk to `/var/lib/neuraldrive/models/` to store downloads.

### Slow Download Speed

Model downloads depend on your internet connection and the responsiveness of the source registry.

1.  **Storage Check**: Downloads will abort if the target storage is full. Check free space with `df -h /var/lib/neuraldrive/models/`.
2.  **Resuming**: If a download is interrupted, NeuralDrive will automatically attempt to resume from the last successful byte.

## Execution Issues

### "Model failed to load"

This error occurs when the model weights cannot be loaded into available memory.

1.  **Insufficient VRAM**: The model is too large for your GPU. Try a smaller model or a version with higher quantization (e.g., Q4_K_M).
2.  **RAM Fallback**: If VRAM is exhausted, Ollama may attempt to load portions of the model into system RAM. This process is very slow and can lead to a load timeout.

### Slow Inference

If the model is generating text very slowly (less than 1 token per second):

1.  **CPU Fallback**: The system is likely running on the CPU. Check if your GPU was detected:
    ```bash
    cat /run/neuraldrive/gpu.conf
    ```
2.  **Mixed Models**: Ensure you are not running multiple models simultaneously, which may compete for limited hardware resources.

## Management and Corruption

### "Model not found"

1.  **Exact Naming**: Models must be called by their full tag (e.g., `llama3:8b`).
2.  **Verify Inventory**: Use the TUI or the following API command to list all locally available models:
    ```bash
    curl -H "Authorization: Bearer nd-xxxx" https://<IP>:8443/api/tags
    ```

### Model Corruption

If a model loads but produces garbled output or crashes the service:

1.  **Delete and Re-pull**: Remove the corrupted model and download it again via the TUI or API:
    ```bash
    curl -H "Authorization: Bearer nd-xxxx" \
      -X DELETE https://<IP>:8443/api/delete -d '{"name":"model_name"}'
    ```

> **Note**: For specific model recommendations based on your hardware, see [Model Recommendations](../models/recommendations.md). For GPU-specific issues, consult [GPU Problems](gpu.md).

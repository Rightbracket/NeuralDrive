*Audience: Admin / Developers*

# Performance Tuning

NeuralDrive is pre-optimized for a wide range of hardware, but fine-tuning specific configurations can significantly improve inference speed, concurrent user handling, and memory efficiency.

## Ollama Configuration

The primary backend service, Ollama, is controlled via `/etc/neuraldrive/ollama.conf`. Modifying these parameters allows you to tailor the system's behavior to your specific hardware and workload.

```
OLLAMA_HOST=127.0.0.1:11434
OLLAMA_MODELS=/var/lib/neuraldrive/models/
OLLAMA_KEEP_ALIVE=5m
OLLAMA_MAX_LOADED_MODELS=0
OLLAMA_NUM_PARALLEL=1
```

### Key Parameters

*   **OLLAMA_NUM_PARALLEL**: (Integer) The number of concurrent requests the server will handle. Increase this for multi-user environments, though this will increase VRAM usage.
*   **OLLAMA_KEEP_ALIVE**: (Duration) How long a model remains loaded in memory after the last request. Setting this to a higher value (e.g., `30m`) avoids the latency of reloading models.
*   **OLLAMA_MAX_LOADED_MODELS**: (Integer) The maximum number of models to keep in VRAM simultaneously. The default is `0` (auto), which allows Ollama to manage concurrent loading based on available VRAM. When memory is full, Least Recently Used (LRU) models are evicted automatically. Manual overrides can be set in `/var/lib/neuraldrive/config/ollama.conf`.
*   **OLLAMA_NUM_THREADS**: (Integer) Specifies the number of CPU threads to use for inference. By default, this auto-detects based on your hardware.
*   **OLLAMA_FLASH_ATTENTION**: (Boolean) Enabling Flash Attention can significantly improve speed on supported GPUs (e.g., NVIDIA Ampere and newer).

## Memory Management

### VRAM and RAM Spilling

Ollama uses memory mapping (`mmap`) by default. This allows the system to load models larger than the available VRAM by spilling some layers into system RAM. While this enables the execution of larger models, it will result in slower inference speeds for the layers processed by the CPU.

### zRAM Swap

NeuralDrive includes the `neuraldrive-zram.service`, which creates a compressed swap device in RAM. This is particularly beneficial when running on systems where the combined requirement of VRAM and RAM is very tight, as it provides a faster alternative to traditional disk-based swap.

## Storage and I/O

To minimize I/O wait times and reduce wear on USB flash media, NeuralDrive employs several filesystem optimizations:

*   **noatime**: The system is mounted with the `noatime` option to prevent unnecessary write operations when files are accessed.
*   **commit=60**: Data is committed to disk every 60 seconds (instead of the default 5), reducing the frequency of physical write cycles.

## Context Window Management

The size of the context window directly impacts memory consumption. A larger context window allows the model to "remember" more of the conversation but requires significantly more VRAM. Adjust the context size within your application or model configuration to balance memory usage and conversational depth.

## Multi-GPU Optimization

If multiple compatible GPUs are present, Ollama will automatically detect them and distribute model layers across all available devices. This is an effective way to run very large models that would otherwise exceed the VRAM of a single card.

For further details on configuration, see [Configuration Files Reference](../reference/config-files.md). To choose the right models for your hardware, see [Model Recommendations](../models/recommendations.md).

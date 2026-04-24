*This chapter is for everyone.*

# Model Recommendations

Selecting the right model depends on your hardware capabilities, specifically your Video RAM (VRAM) and CPU performance. Running a model that exceeds your hardware limits will result in extremely slow response times or failure to load.

## VRAM Requirements

The most critical factor for performance is the amount of VRAM available on your GPU. The following table provides recommendations for models based on standard VRAM tiers.

| VRAM | Recommended Models |
| :--- | :--- |
| **6 GB** | `qwen2.5:3b`, `phi3:mini` |
| **8 GB** | `llama3.1:8b` |
| **12 GB** | `codestral:latest` |
| **24 GB+** | `llama3.1:70b` (Q4_K_M) |

## CPU-Only Execution

If your system lacks a compatible GPU, NeuralDrive can run models on the CPU. While this is significantly slower, it is still functional for many tasks.

- **Minimum:** AVX2 support is required.
- **Preferred:** AVX-512 support provides a noticeable speed boost for CPU inference.
- **Recommendation:** Stick to smaller models (3B or 8B) for a better experience when running on CPU only.

## Concurrent Models

NeuralDrive allows multiple models to be loaded into memory simultaneously, provided there is enough VRAM. This is managed by Ollama using several environment variables:

- `OLLAMA_MAX_LOADED_MODELS`: Defines the maximum number of models kept in memory. The default is `0` (auto), which allows Ollama to manage loading based on available VRAM.
- `OLLAMA_NUM_PARALLEL`: Determines how many concurrent requests can be handled.
- `OLLAMA_KEEP_ALIVE`: Sets how long a model stays in memory after the last request before being evicted.

NeuralDrive uses a Least Recently Used (LRU) eviction policy. If you attempt to load a new model and VRAM is full, Ollama handles eviction automatically to make room for the new request.

## Model Catalog

For a curated list of models tested and recommended for NeuralDrive, you can inspect the system's model catalog located at:
`/etc/neuraldrive/neuraldrive-models.yaml`

This file contains recommendations optimized for the NeuralDrive environment. You can also view these recommendations in the [Open WebUI Models page](../using/models-web.md) or the [TUI Models screen](../using/models-tui.md).


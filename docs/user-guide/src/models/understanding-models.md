*This chapter is for everyone.*

# Understanding Models

Large Language Models (LLMs) are the core engines that power NeuralDrive. These models are probabilistic systems trained on vast datasets to predict and generate human-like text, code, and reasoning. NeuralDrive uses Ollama to manage these models, providing a streamlined experience for running them locally without external dependencies.

## Model Formats and GGUF

NeuralDrive exclusively uses the GGUF (GPT-Generated Unified Format) format for model storage and execution. GGUF is designed for efficient loading and performance on both CPUs and GPUs. It packs the model weights, configuration, and vocabulary into a single file, making it highly portable.

## Parameter Counts

The "size" of a model is often described by its parameter count, typically denoted in billions (B). Parameters are the internal variables the model learned during training.

- **3B (Small):** Extremely fast and lightweight. Ideal for basic text processing, classification, or running on hardware with limited VRAM (6GB or less). Examples: `phi3:mini`, `qwen2.5:3b`.
- **8B (Medium):** The current sweet spot for local deployment. Offers a strong balance of reasoning capability and speed. Fits comfortably on 8GB-12GB VRAM cards. Examples: `llama3.1:8b`.
- **13B (Large):** Provides deeper reasoning and better instruction following. Requires 12GB+ VRAM for optimal performance.
- **70B (Very Large):** Top-tier performance comparable to many commercial cloud models. Requires significant hardware resources (24GB+ VRAM for quantized versions). Examples: `llama3.1:70b`.

## Quantization

Quantization is a compression technique that reduces the precision of model weights (e.g., from 16-bit floats to 4-bit integers). This significantly lowers the VRAM and storage requirements with minimal impact on output quality.

NeuralDrive supports several quantization levels:

- **Q4_K_M:** The standard recommendation. It offers the smallest file size and fastest inference while maintaining high accuracy.
- **Q5_K_M:** A balanced option for users who want slightly higher quality than Q4 without the massive overhead of Q8.
- **Q8_0:** The highest quality available, preserving almost all original model precision. It requires much more VRAM and storage.

## Naming Convention

Models in NeuralDrive follow a specific naming string: `<name>:<tag>`.

- **Name:** The base model family (e.g., `llama3.1`, `codestral`).
- **Tag:** Specifies the version or size (e.g., `8b`, `latest`, `mini`).

When you pull a model like `llama3.1:8b`, NeuralDrive downloads the specific version optimized for local execution.

## Size vs Resources

A model's resource consumption is determined by its parameter count and quantization level. A larger parameter count requires more VRAM to "fit" the model for processing, while higher quantization levels increase the memory footprint of a model with the same parameter count. 

Before downloading, check [Model Recommendations](../models/recommendations.md) to ensure your hardware can support your desired model.


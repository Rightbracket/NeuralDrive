*This chapter is for contributors and maintainers.*

# Performance Benchmarking

Benchmarking allows us to track the performance of the NeuralDrive appliance over time and compare different hardware configurations.

## Methodology

We focus on two primary metrics: **Inference Speed** and **Resource Efficiency**.

### 1. Inference Speed (Tokens per Second)
This is measured using the Ollama API. We use a standardized set of prompts and models (e.g., Llama 3 8B) to ensure consistency.
- **Time to First Token (TTFT)**: The delay between sending a request and receiving the first character.
- **Tokens per Second (TPS)**: The average generation speed once the model has started responding.

### 2. Resource Efficiency
- **VRAM Utilization**: How much of the available GPU memory is consumed by the model weights and the KV cache.
- **System Memory Overhead**: The RAM usage of the base OS, Caddy, WebUI, and the System API.
- **Power Consumption**: Measured via `nvidia-smi` or external power meters during peak inference.

## Benchmarking Tools

### Internal Benchmark Script
NeuralDrive includes a utility at `/usr/lib/neuraldrive/benchmark.sh`. It performs the following:
1. Downloads a specific test model.
2. Runs a series of 5 prompts.
3. Calculates the average TPS and TTFT.
4. Logs the results along with system metadata (CPU/GPU info).

### External Tools
- **Ollama-Benchmark**: A community tool for stress-testing Ollama instances.
- **Prometheus/Grafana**: For long-term monitoring of performance metrics (available via the `neuraldrive-gpu-monitor` service).

## Comparing Configurations

Benchmarks are used to evaluate:
- **Quantization Levels**: Comparing 4-bit (q4_0) vs 8-bit (q8_0) performance.
- **Driver Versions**: Detecting regressions in new NVIDIA or ROCm driver releases.
- **Filesystem Impact**: Comparing model loading times from SquashFS vs. persistence layers.

> **Note**: Benchmark results are highly dependent on hardware. Always include the specific CPU and GPU models when sharing performance data.


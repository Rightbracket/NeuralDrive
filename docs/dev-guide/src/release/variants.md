*This chapter is for contributors and maintainers.*

# Image Variants

NeuralDrive is distributed in several variants, each tailored for different hardware targets and use cases. This helps keep the ISO size manageable and ensures that the system is optimized for its intended GPU provider.

## Full Variant (Recommended)

The **Full** variant includes the complete driver stack for all supported GPU vendors:
- NVIDIA (Proprietary)
- AMD (ROCm)
- Intel (OneAPI)

### Characteristics
- **Size**: ~6-8GB.
- **Hardware Support**: Any compatible system with a modern GPU.
- **Best For**: General use, mixed hardware environments, or users who may swap GPUs between machines.

## NVIDIA-Only Variant

The **NVIDIA-Only** variant is optimized for systems with NVIDIA hardware. It excludes the AMD and Intel compute libraries to reduce disk footprint.

### Characteristics
- **Size**: ~4-5GB.
- **Hardware Support**: NVIDIA GeForce/RTX/A-Series GPUs only.
- **Best For**: Dedicated AI workstations and servers using NVIDIA hardware.

## Minimal (CPU-Only) Variant

The **Minimal** variant excludes all proprietary GPU drivers and compute stacks. It is intended for testing, development, or low-power hardware.

### Characteristics
- **Size**: ~1.5-2GB.
- **Hardware Support**: CPU-only (AVX/AVX2 optimized).
- **Best For**: Virtual machines, CI/CD testing, or systems where the GPU is not supported by Ollama.

## Build Comparison

| Feature | Full | NVIDIA-Only | Minimal |
|---------|------|-------------|---------|
| Ollama  | Yes  | Yes         | Yes     |
| WebUI   | Yes  | Yes         | Yes     |
| NVIDIA Drivers | Yes | Yes | No |
| ROCm Libraries | Yes | No  | No |
| Intel OneAPI   | Yes | No  | No |
| SquashFS Size  | Large | Medium | Small |

## Custom Variants

Developers can create their own variants by modifying the `config/package-lists/` directory and adding a new `BUILD_VARIANT` flag to the `build.sh` script.

> **Tip**: For custom enterprise deployments, we recommend starting with the NVIDIA-Only or Full variant and removing any unnecessary networking or utility packages to further reduce the attack surface.


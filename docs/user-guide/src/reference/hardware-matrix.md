*Audience: Everyone*

# Hardware Compatibility Matrix

This document provides a comprehensive list of supported GPU hardware and their corresponding compute stacks within the NeuralDrive environment.

## Supported Graphics Hardware

| Vendor | Family | Example Cards | Compute Stack | Driver | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **NVIDIA** | Turing | RTX 2060-2080, T4 | CUDA 12.x | 535+ | Supported |
| **NVIDIA** | Ampere | RTX 3060-3090, A100, A2000 | CUDA 12.x | 535+ | Supported |
| **NVIDIA** | Ada Lovelace | RTX 4060-4090, L40 | CUDA 12.x | 535+ | Supported |
| **NVIDIA** | Hopper | H100 | CUDA 12.x | 535+ | Supported |
| **AMD** | RDNA 3 | RX 7600-7900 XTX | ROCm 6.x | amdgpu | Supported |
| **AMD** | CDNA 2/3 | MI250, MI300 | ROCm 6.x | amdgpu | Supported |
| **Intel** | Arc Alchemist | A770, A750 | oneAPI/SYCL | i915 | Experimental |
| **CPU-only** | Any x86_64 | Any | N/A | N/A | Supported (slow) |

## VRAM Recommendations

The table below outlines the minimum VRAM requirements for common model sizes at various quantization levels.

| Model Size | Quantization (Q4_K_M) | Quantization (Q8_0) | Full Weights (FP16) |
| :--- | :--- | :--- | :--- |
| **7B - 8B** | 6 GB | 10 GB | 16 GB |
| **13B - 14B** | 10 GB | 16 GB | 32 GB |
| **30B - 34B** | 24 GB | 40 GB | 64 GB |
| **70B** | 48 GB | 80 GB | 140 GB |

> **Note**: These values are estimates and do not include the memory required for context window overhead (KV cache). High context lengths will increase VRAM consumption.

## Important Hardware Considerations

-   **Secure Boot**: NVIDIA drivers require MOK (Machine Owner Key) enrollment or Secure Boot to be disabled. NeuralDrive uses DKMS-based driver installation.
-   **Bus Interface**: PCIe 4.0 or 5.0 is recommended to minimize latency during model loading and context ingestion.
-   **Power Supply**: Ensure your power supply (PSU) is rated for the peak power consumption of your GPU(s) during inference.
-   **Cooling**: GPUs can generate significant heat during long-running inference tasks. Ensure your system has adequate thermal management.

> **Note**: For detailed hardware setup instructions, see [Hardware Requirements](../getting-started/hardware-requirements.md). If your GPU is not detected, consult the [GPU Troubleshooting guide](../troubleshooting/gpu.md).

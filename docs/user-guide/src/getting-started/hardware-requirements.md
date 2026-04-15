*Audience: Users planning hardware deployments for NeuralDrive inference servers.*

# Hardware Requirements

NeuralDrive is designed to run on a wide range of x86_64 hardware, but performance varies significantly depending on your CPU, system RAM, and GPU.

## Minimum Requirements

The following specifications are suitable for running smaller models (up to 7B parameters) with Q4 quantization.

| Component | Minimum Specification |
|-----------|-----------------------|
| CPU | x86_64 with AVX2 support |
| System RAM | 8 GB |
| GPU | Optional; 6 GB VRAM recommended for acceleration |
| Storage | 16 GB USB 3.0 flash drive |

## Recommended Specifications

For high-performance inference using larger models (13B to 70B parameters) or concurrent model loading, the following hardware is recommended.

| Component | Recommended Specification |
|-----------|--------------------------|
| CPU | x86_64 with AVX-512 support |
| System RAM | 32 GB – 64 GB |
| GPU | 24 GB+ VRAM (NVIDIA RTX 3090/4090 or AMD RX 7900 XTX) |
| Storage | 128 GB+ USB 3.0 or external SSD for model persistence |

## GPU Compatibility Matrix

NeuralDrive automatically detects and configures drivers for major GPU vendors.

| Vendor | Generation | Example Hardware | Driver Type | Compute Stack | Status |
|--------|------------|------------------|-------------|---------------|--------|
| NVIDIA | Ada Lovelace | RTX 4090 | Proprietary 560+ | CUDA 12.x | Supported |
| NVIDIA | Ampere | RTX 3060 | Proprietary 560+ | CUDA 12.x | Supported |
| NVIDIA | Pascal | GTX 1080 | Proprietary 560+ | CUDA 12.x | Supported |
| AMD | RDNA 3 | RX 7900 XTX | amdgpu + ROCm | ROCm 6.x | Supported |
| AMD | RDNA 2 | RX 6800 XT | amdgpu + ROCm | ROCm 6.x | Supported |
| Intel | Arc | A770 | compute-runtime | oneAPI | Experimental |
| None | CPU | Any x86_64 | N/A | AVX2/AVX-512 | Supported |

## Model Size Cheat Sheet

Use this guide to determine if your hardware can support specific model sizes.

- **3B Models**: 8 GB System RAM.
- **8B Models**: 16 GB System RAM, 8 GB VRAM.
- **70B Models**: 64 GB System RAM, 24 GB+ VRAM.

## Important Hardware Notes

### UEFI and Secure Boot
NeuralDrive supports both hybrid BIOS and UEFI boot modes. However, the proprietary NVIDIA drivers may require you to disable Secure Boot or enroll a Machine Owner Key (MOK) during the first boot. If the GPU is not detected on an NVIDIA system, verify your Secure Boot status in the BIOS/UEFI settings.

### USB Media Selection
For the best experience, use a USB 3.0 or faster flash drive. If you plan to maintain a large library of high-parameter models, booting from an external SATA or NVMe SSD via a USB enclosure is strongly recommended for faster load times.

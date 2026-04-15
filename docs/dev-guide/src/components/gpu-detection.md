*This chapter is for contributors and maintainers.*

# GPU Auto-Detection

The `gpu-detect.sh` script is a critical component of the NeuralDrive boot sequence. It is responsible for identifying the installed hardware and ensuring the correct compute stack is initialized.

## Logic Overview

The script runs during the `neuraldrive-gpu-detect.service` phase. It performs the following steps:

1. **PCI Enumeration**: Uses `lspci` to scan for VGA and 3D controllers.
2. **Vendor Identification**: Matches the PCI IDs against known vendor strings (NVIDIA, AMD, Intel).
3. **Module Loading**: Calls `modprobe` to load the appropriate kernel modules (e.g., `nvidia`, `amdgpu`, or `i915`).
4. **Configuration Generation**: Writes the detected state to `/run/neuraldrive/gpu.conf`.

## Vendor Detection Details

### NVIDIA
If an NVIDIA card is detected (PCI vendor ID `10de`), the script:
- Loads the `nvidia`, `nvidia-uvm`, and `nvidia-drm` modules via `modprobe`.
- Enables persistence mode with `nvidia-smi -pm 1`.
- Sets `VENDOR=NVIDIA` in the config file.
- If module loading fails, records `NVIDIA_MODULE_MISSING=true`.

### AMD
If an AMD card is detected (PCI vendor ID `1002`), the script:
- Loads the `amdgpu` module.
- Sets `VENDOR=AMD`.
- If module loading fails, records `AMD_MODULE_MISSING=true`.

### Intel
If an Intel GPU is detected (PCI vendor ID `8086`), the script:
- Loads the `i915` module.
- Sets `VENDOR=INTEL`.
- If module loading fails, records `INTEL_MODULE_MISSING=true`.

## The gpu.conf File

The output of the detection process is stored in a runtime environment file:
```bash
# /run/neuraldrive/gpu.conf
VENDOR=NVIDIA
```
Additional keys may be present for error conditions (e.g., `NVIDIA_MODULE_MISSING=true`) or Secure Boot detection (`SECURE_BOOT=true`). This file is available to subsequent services for determining the active compute provider.

## Troubleshooting and Fallbacks

If no GPU is detected, or if module loading fails:
- The script sets `VENDOR=CPU`.
- A message is logged to standard output.
- Ollama will start in CPU-only mode, which is significantly slower but allows the appliance to remain functional.

## Modifying Detection Logic

To add support for new hardware or refine the detection process, modify `/usr/lib/neuraldrive/gpu-detect.sh` in the repository.

> **Note**: Changes to the detection script require a re-build of the ISO or a manual update to the file on the persistence layer for testing.


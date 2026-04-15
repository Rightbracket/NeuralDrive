*Audience: Everyone*

# GPU Troubleshooting

NeuralDrive is optimized for hardware-accelerated inference. If the system fails to detect or utilize your GPU, it will fallback to CPU inference, which is significantly slower.

## Detection Issues

### No GPU detected

If NeuralDrive does not recognize your hardware, verify the following system configurations:

1.  **Hardware Compatibility**: Ensure your GPU is listed in the [Hardware Compatibility Matrix](../reference/hardware-matrix.md).
2.  **BIOS Settings**:
    -   **IOMMU/VT-d**: Ensure these are enabled for proper PCI communication.
    -   **Above 4G Decoding**: Must be enabled for modern GPUs (RTX 30-series and newer).
    -   **Resizable BAR**: Recommended for improved performance, though not required for detection.
3.  **Secure Boot**: NVIDIA drivers require MOK (Machine Owner Key) enrollment to function with Secure Boot. If you cannot enroll the key, disable Secure Boot in the BIOS.
4.  **Mixed Vendors**: Mixed-vendor configurations (e.g., one NVIDIA and one AMD card) are not supported. The first vendor detected by the boot sequence will be initialized.

### Nouveau Conflict

NeuralDrive automatically blacklists the open-source `nouveau` driver to prevent conflicts with the proprietary NVIDIA stack. To verify:

```bash
lsmod | grep nouveau
```

If the command returns any output, the blacklist failed. Check `/etc/modprobe.d/neuraldrive-blacklist.conf`.

## Diagnostic Tools

NeuralDrive provides several utilities to inspect GPU state:

-   **NVIDIA**: Run `nvidia-smi` to view VRAM usage, temperature, and driver version.
-   **AMD**: Run `rocm-smi` to inspect ROCm status and device health.
-   **System Config**: The file `/run/neuraldrive/gpu.conf` is generated at boot by `neuraldrive-gpu-detect.service`. It contains the detected vendor:
    ```bash
    cat /run/neuraldrive/gpu.conf
    ```
-   **PCI Enumeration**: Use `lspci | grep -i vga` to see if the kernel sees the hardware at the bus level.

## Recovery and Safe Mode

### Safe Mode Boot

If a GPU driver causes a system hang or kernel panic during boot, use the **Safe Mode** option in the GRUB menu.

-   **Effect**: Skips all GPU detection and driver loading.
-   **Result**: The system will boot with generic VGA drivers and use CPU-only inference.
-   **Usage**: Ideal for troubleshooting BIOS settings or extracting logs when the GPU is failing.

> **Warning**: Running in Safe Mode will result in extremely high CPU usage and latency during model inference.

### Mixed Vendor Support

Current NeuralDrive releases only support single-vendor clusters. If you have multiple GPUs, they must all be from the same manufacturer (e.g., all NVIDIA or all AMD). Ollama will automatically distribute model layers across all compatible GPUs of the same vendor to maximize VRAM utilization.

> **Note**: For detailed kernel parameters related to GPU management, see [Boot Parameters](../reference/boot-parameters.md).

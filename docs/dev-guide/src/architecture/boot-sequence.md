*This chapter is for contributors and maintainers.*

# Boot Sequence

The NeuralDrive boot sequence is designed to move from a cold start to a fully functional LLM appliance as quickly as possible. It uses systemd to manage parallelization and service ordering.

## Timeline of Events

1. **Firmware (UEFI/BIOS)**: The system initializes hardware and locates the EFI system partition on the boot media.
2. **GRUB Bootloader**: Loads the kernel and the initial RAM disk (initrd).
3. **Kernel & initramfs**: The kernel boots and the `live-boot` scripts mount the compressed SquashFS filesystem. If persistence is detected, the overlayfs layer is established.
4. **systemd Init**: The systemd process (PID 1) starts and begins processing unit files.

## Service Ordering

The following list details the startup order of NeuralDrive-specific services:

### 1. Initialization Phase
- **`neuraldrive-setup.service`**: A oneshot service that runs `/usr/lib/neuraldrive/first-boot.sh`. It checks for the existence of a sentinel file (`/etc/neuraldrive/.setup-complete`). If missing, it blocks the TTY and runs the setup wizard.
- **`neuraldrive-zram.service`**: Configures swap space in RAM to handle memory-intensive model loading.

### 2. Hardware and Security Phase
- **`neuraldrive-gpu-detect.service`**: Runs `/usr/lib/neuraldrive/gpu-detect.sh` to identify the GPU vendor and load the appropriate kernel modules (NVIDIA, AMD, or Intel).
- **`neuraldrive-certs.service`**: Checks if TLS certificates exist in `/etc/neuraldrive/tls/`. If not, it generates a new self-signed CA and server certificate.

### 3. Application Phase
- **`neuraldrive-ollama.service`**: Starts the inference engine. This service `Requires=neuraldrive-gpu-detect` to ensure drivers are loaded first.
- **`neuraldrive-webui.service`**: Launches the Open WebUI container/process. It `Wants=neuraldrive-ollama` but can start independently.
- **`neuraldrive-system-api.service`**: Starts the FastAPI backend.

### 4. Gateway Phase
- **`neuraldrive-caddy.service`**: Starts the Caddy proxy. It `Requires=neuraldrive-certs` to ensure it has valid TLS material for binding to port 443.

### 5. Console Phase
- **`neuraldrive-show-ip.service`**: A simple oneshot that prints the current IP address and mDNS hostname to the console.
- **TUI (getty@tty1)**: The Textual TUI is launched on the main console, providing a dashboard for local administration.

## Dependency Visualization

```text
[Hardware Detect] -> [GPU Detect] -> [Ollama] -> [WebUI]
                                              \
[ZRAM Setup]                                   \
                                                +-> [Caddy]
[Certs Gen] -----------------------------------/
```

> **Note**: Failures in the `gpu-detect` service will prevent `ollama` from starting, effectively putting the appliance into a "degraded" mode where only the System API and TUI are fully functional for troubleshooting.


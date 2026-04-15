*This chapter is for contributors and maintainers.*

# Package Lists

Package lists define which software is retrieved from APT repositories and installed into the NeuralDrive image.

## Core List (`neuraldrive.list.chroot`)

This list contains the essential packages for the appliance:
- **Base System**: `systemd`, `udev`, `kmod`, `ca-certificates`.
- **Networking**: `caddy`, `avahi-daemon`, `nftables`, `curl`, `wget`.
- **Python Stack**: `python3`, `python3-venv`, `python3-pip`.
- **Utilities**: `vim`, `htop`, `pciutils`, `usbutils`, `p7zip-full`.

## GPU-Specific Lists

To support different hardware configurations, we use specialized package lists:

### NVIDIA (`nvidia.list.chroot`)
- `nvidia-driver`: The core proprietary driver.
- `nvidia-smi`: System management interface for monitoring.
- `nvidia-cuda-toolkit`: Required for compute tasks.
- `libnvidia-encode1`: For video encoding/decoding if needed by secondary apps.

### AMD (ROCm)
Packages for ROCm support are typically pulled from the official Radeon repositories defined in the `archives/` directory. These include `rocm-hip-sdk` and `amdgpu-dkms`.

### Intel (OneAPI)
Similar to AMD, Intel packages like `intel-oneapi-runtime-libs` and `intel-opencl-icd` are sourced from the Intel OneAPI repository.

## How live-build Handles Lists

During the `chroot` stage, `live-build` reads every file with the `.list.chroot` extension and passes the package names to `apt-get install`.

### Dependencies
`live-build` handles dependency resolution automatically. However, to keep the image size small, we explicitly use `--no-install-recommends` in the global build configuration.

## Customizing Package Lists

If you need to add a package to your custom build:
1. Create a new file in `config/package-lists/` (e.g., `custom.list.chroot`).
2. Add the package names, one per line.
3. Run a new build.

> **Tip**: For temporary testing, you can add packages to `neuraldrive.list.chroot`, but it is better to keep custom additions in a separate file for better maintainability.


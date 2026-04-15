# NeuralDrive Implementation Plan 02: GPU Driver Support & Auto-Detection

This document details the GPU acceleration strategies for NVIDIA, AMD, and Intel hardware on the NeuralDrive platform.

## Section 1: NVIDIA Driver Strategy

### Package Selection
Packages to be sourced from `bookworm-backports`:
```bash
sudo apt install -y -t bookworm-backports \
    nvidia-driver \
    nvidia-kernel-dkms \
    nvidia-cuda-toolkit \
    libcudnn9-cuda-12 \
    nvidia-smi \
    nvidia-persistenced
```

### Driver Integration
- **Pre-compiled Modules**: To avoid GCC/headers at runtime, use `nvidia-kernel-amd64/bookworm-backports`.
- **Nouveau Blacklisting**: Create `/etc/modprobe.d/blacklist-nouveau.conf`:
  ```text
  blacklist nouveau
  options nouveau modeset=0
  ```
- **Kernel Cmdline**: Add `rd.driver.blacklist=nouveau` to the GRUB configuration.

### Disk Footprint
- **Total Driver + CUDA Runtime**: ~3.2 GB.
- **Optimization**: Strip documentation and static libraries from `/usr/share/doc` and `/usr/lib/x86_64-linux-gnu/*.a`.

---

## Section 2: AMD ROCm Strategy

### Package Selection
Official ROCm 6.x repository for Debian 12:
```bash
# Add ROCm Repo
wget https://repo.radeon.com/rocm/rocm.gpg.key -O - | \
    gpg --dearmor | sudo tee /etc/apt/keyrings/rocm.gpg > /dev/null
echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/rocm.gpg] https://repo.radeon.com/rocm/apt/6.0.2 bookworm main" | \
    sudo tee /etc/apt/sources.list.d/rocm.list

sudo apt update
sudo apt install -y rocm-hip-runtime rocm-opencl-runtime rocm-smi
```

### Kernel Support
- **In-tree AMDGPU**: Ensure `linux-image-amd64/bookworm-backports` (6.12+) is used for RDNA3+ support.
- **Firmware**: Ensure `firmware-amd-graphics` is installed.

### Disk Footprint
- **Total ROCm (Stripped)**: ~5.8 GB. (Clean out `dev` packages and `samples` to save ~2 GB).

---

## Section 3: Intel Arc Strategy

### Package Selection
Standard Debian 12 `main` + Intel's GPU repo:
```bash
sudo apt install -y \
    intel-compute-runtime \
    intel-opencl-icd \
    level-zero \
    intel-media-va-driver-non-free \
    intel-gpu-tools
```

### Support Level
- **Status**: Experimental (Ollama 0.3.13+ via oneAPI/SYCL).
- **GPU Matrix**: Arc A380, A580, A750, A770.

---

## Section 4: GPU Auto-Detection at Boot

### Detection Script: `/usr/lib/neuraldrive/gpu-detect.sh`
```bash
#!/bin/bash
mkdir -p /run/neuraldrive
GPU_CONF="/run/neuraldrive/gpu.conf"

# Identify hardware via PCI ID
GPU_LIST=$(lspci -nn | grep -E "VGA|3D|Display")

DETECTED_VENDORS=""

if echo "$GPU_LIST" | grep -qi "10de"; then
    echo "VENDOR=NVIDIA" >> "$GPU_CONF"
    DETECTED_VENDORS="NVIDIA $DETECTED_VENDORS"
    modprobe nvidia nvidia-uvm nvidia-drm
    nvidia-smi -pm 1 # Enable persistence mode
fi

if echo "$GPU_LIST" | grep -qi "1002"; then
    echo "VENDOR=AMD" >> "$GPU_CONF"
    DETECTED_VENDORS="AMD $DETECTED_VENDORS"
    modprobe amdgpu
fi

if echo "$GPU_LIST" | grep -qi "8086"; then
    echo "VENDOR=INTEL" >> "$GPU_CONF"
    DETECTED_VENDORS="INTEL $DETECTED_VENDORS"
    modprobe i915
fi

if [ -z "$DETECTED_VENDORS" ]; then
    echo "VENDOR=CPU" >> "$GPU_CONF"
    echo "No supported GPU found. Falling back to CPU mode."
else
    echo "Detected GPUs: $DETECTED_VENDORS"
fi
```

### systemd Service: `neuraldrive-gpu-detect.service`
```ini
[Unit]
Description=NeuralDrive GPU Auto-Detection
Before=neuraldrive-ollama.service
DefaultDependencies=no

[Service]
Type=oneshot
ExecStart=/usr/lib/neuraldrive/gpu-detect.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

---

## Section 5: Multi-GPU Support

### Environment Variables
- **NVIDIA**: `CUDA_VISIBLE_DEVICES` defaults to all devices.
- **AMD**: `HIP_VISIBLE_DEVICES` for ROCm targeting.
- **Ollama**: Automatically detects and leverages multiple GPUs of the same vendor.

### Mixed Vendor Limitation
NeuralDrive will prioritize NVIDIA if present, then AMD, then Intel. Mixed vendor execution is **not supported** in this release.

---

## Section 6: Known Issues & Mitigations

### Secure Boot & MOK
NVIDIA drivers will fail to load if Secure Boot is enabled without MOK signing.
- **Mitigation**: Detect Secure Boot status via `mokutil --sb-state`. If enabled, display a TUI alert prompting the user to either disable Secure Boot or enroll the NeuralDrive public key.

### Nouveau Conflict
Ensure `config/includes.chroot/etc/modprobe.d/blacklist-nouveau.conf` is present.
Verify with: `lsmod | grep nouveau` (should return no results).

---

## Section 7: Verification & Diagnostics

### Diagnostic Commands
```bash
# NVIDIA
nvidia-smi

# AMD
rocm-smi
clinfo | grep "Platform Name"

# Intel
intel_gpu_top -s 1 # monitoring
```

### NeuralDrive Health Check: `/usr/bin/neuraldrive-check`
```bash
#!/bin/bash
source /run/neuraldrive/gpu.conf
echo "NeuralDrive Status:"
echo "-------------------"
echo "Detected Mode: $VENDOR"
echo "Kernel: $(uname -r)"
if [ "$VENDOR" == "NVIDIA" ]; then
    nvidia-smi -L
fi
```

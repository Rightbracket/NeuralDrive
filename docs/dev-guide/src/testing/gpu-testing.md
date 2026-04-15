*This chapter is for contributors and maintainers.*

# GPU Testing

GPU testing is the most critical part of the NeuralDrive validation process. Because the appliance's value depends on its ability to utilize hardware acceleration, every release must be verified on real hardware.

## On-Target Validation

The `test-gpu.sh` script is included in the ISO image at `/usr/lib/neuraldrive/test-gpu.sh`.

### 1. Detection Verification
The first step is verifying that `gpu-detect.sh` has identified the hardware correctly.
```bash
cat /run/neuraldrive/gpu.conf
```
Check that `NEURALDRIVE_GPU_VENDOR` matches your hardware and that the appropriate kernel modules are loaded (`lsmod | grep -E "nvidia|amdgpu|i915"`).

### 2. Compute Stack Functional Test
Run a simple inference task to ensure the compute provider (CUDA/ROCm/OneAPI) is functional.
```bash
# Verify Ollama can see the GPU
ollama list
# Run a small model
ollama run tinyllama "Hello, what is your name?"
```

### 3. VRAM and Performance
Use vendor-specific tools to monitor VRAM usage during inference:
- **NVIDIA**: `nvidia-smi`
- **AMD**: `rocm-smi`
- **Intel**: `intel_gpu_top`

Verify that the model weights are fully loaded into VRAM and that the inference speed (tokens per second) is within the expected range for the hardware.

## Hot Dashboard Testing

NeuralDrive includes a dedicated GPU monitoring service (`neuraldrive-gpu-monitor.service`). Access the dashboard at `https://<ip>/monitor/` to verify:
- Real-time temperature reporting.
- Power consumption metrics.
- Multi-GPU visibility (if applicable).

## Testing Matrix

Maintainers maintain a spreadsheet of verified hardware configurations. Before a major release, tests are performed on:
- NVIDIA GeForce (Consumer)
- NVIDIA RTX/A-Series (Professional)
- AMD Radeon RX (Consumer)
- Intel Arc (Consumer)

> **Note**: If you have access to hardware not currently in our test matrix, please run `test-gpu.sh` and share the results on GitHub.


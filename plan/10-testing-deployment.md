# Plan 10: Testing, QA & Deployment

## 1. Testing Strategy Overview
NeuralDrive must boot and provide a functional LLM API on a variety of hardware. Our testing strategy covers five layers:

- **Unit Tests**: Python/Textual TUI components and the management API.
- **Integration Tests**: Communication between Ollama, Caddy, and the TUI.
- **System Tests**: Boot process, GPU driver loading, and model serving.
- **Hardware Compatibility Matrix**: Physical testing on diverse GPU architectures.
- **User Acceptance (UAT)**: Manual validation of the first-boot experience and model downloading.

## 2. Build Verification Tests (BVT)
Every successful build triggers automated verification in a virtualized environment.

### `tests/test-boot.sh`
```bash
#!/bin/bash
# QEMU Boot Test Script
# Runs NeuralDrive in a VM and checks for service readiness.

ISO_PATH=$1
TIMEOUT=300

echo "Starting QEMU (UEFI mode)..."
qemu-system-x86_64 \
    -m 4G \
    -drive file=$ISO_PATH,format=raw,readonly=on \
    -bios /usr/share/ovmf/OVMF.fd \
    -net nic -net user,hostfwd=tcp::11434-:11434 \
    -display none -vnc :1 -daemonize

# Wait for Ollama API
START_TIME=$(date +%s)
while true; do
    if curl -s http://localhost:11434/api/tags > /dev/null; then
        echo "Ollama API ready."
        break
    fi
    CURRENT_TIME=$(date +%s)
    if [ $((CURRENT_TIME - START_TIME)) -gt $TIMEOUT ]; then
        echo "Error: Boot timeout exceeded."
        exit 1
    fi
    sleep 5
done

# Cleanup
pkill qemu-system-x86_64
echo "BVT Passed."
```

## 3. GPU Testing Matrix
We maintain a physical testing lab to ensure driver stability and performance across hardware generations.

| GPU Architecture | Driver (Debian) | Target Framework | Required Status |
| :--- | :--- | :--- | :--- |
| **NVIDIA Ada Lovelace** (4090) | `nvidia-driver` 560+ | CUDA 12.x | Required |
| **NVIDIA Ampere** (3060) | `nvidia-driver` 560+ | CUDA 12.x | Required |
| **NVIDIA Pascal** (1080) | `nvidia-driver` 560+ | CUDA 12.x | Required |
| **AMD RDNA 3** (7900 XTX) | `amdgpu` + ROCm 6.x | ROCm | Required |
| **AMD RDNA 2** (6800 XT) | `amdgpu` + ROCm 6.x | ROCm | Desired |
| **Intel Arc** (A770) | `compute-runtime` | oneAPI | Desired |
| **CPU Only** (x86_64) | N/A | AVX2/AVX-512 | Required |

### `tests/test-gpu.sh`
```bash
#!/bin/bash
# Runs on target hardware after boot.

# Detect NVIDIA
if command -v nvidia-smi &> /dev/null; then
    echo "NVIDIA detected: $(nvidia-smi --query-gpu=name --format=csv,noheader)"
    ollama run phi3:mini "What is 2+2?" --verbose
fi

# Detect AMD
if command -v rocm-smi &> /dev/null; then
    echo "AMD detected: $(rocm-smi --showproductname | grep -v 'GPU')"
    ollama run phi3:mini "What is 2+2?" --verbose
fi
```

## 4. API Testing Suite
Using `pytest` and `httpx` to verify OpenAI-compatible endpoints.

```python
import httpx
import pytest

API_URL = "http://localhost:11434/v1"

def test_health():
    response = httpx.get(f"{API_URL}/models")
    assert response.status_code == 200

def test_chat_completion():
    payload = {
        "model": "phi3:mini",
        "messages": [{"role": "user", "content": "Hello!"}],
        "stream": False
    }
    response = httpx.post(f"{API_URL}/chat/completions", json=payload, timeout=60.0)
    assert response.status_code == 200
    assert "choices" in response.json()
```

## 5. USB Lifecycle & Persistence
We test the robustness of the `NDATA` partition and persistence layers.

1.  **Fresh Install**: dd image → boot → verify first-boot wizard.
2.  **Persistence Check**: Pull `llama3.1:8b` → reboot → verify model is still present.
3.  **Expansion**: Verify `NDATA` partition utilizes the full remaining USB capacity.
4.  **Security**: Verify that selecting LUKS encryption during the wizard prompts for a password on subsequent boots.

## 6. Performance Benchmarking
Metrics are published to `docs/benchmarks.md` to help users choose hardware.

- **Metric**: Tokens Per Second (TPS).
- **Metric**: Time to First Token (TTFT).
- **Metric**: VRAM Overhead (MB).
- **Test Model**: `llama3.1:8b` (Q4_K_M).

## 7. Release Process & Checklist
Versions use CalVer format: `YYYY.MM.PATCH` (e.g., `2026.04.0`).

- [ ] `lb clean && lb build` completed in a fresh environment.
- [ ] BVT Passed (QEMU BIOS and UEFI).
- [ ] Physical boot test successful on at least 2 machines.
- [ ] Security scan (`debsecan`) confirms no critical vulnerabilities in base packages.
- [ ] `SHA256SUMS` generated and signed with the NeuralDrive GPG key.
- [ ] `CHANGELOG.md` updated with new features and model updates.

## 8. CI/CD Pipeline
GitHub Actions automates the build and artifact generation.

### `.github/workflows/build.yml`
```yaml
name: NeuralDrive Build & Test
on: [push, workflow_dispatch]

jobs:
  build-iso:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build ISO via Docker
        run: docker compose run builder
      - name: Run Boot Test (QEMU)
        run: ./tests/test-boot.sh output/neuraldrive.iso
      - name: Upload Artifact
        uses: actions/upload-artifact@v4
        with:
          name: neuraldrive-iso
          path: output/neuraldrive.iso
```

## 9. Monitoring & Telemetry (Opt-in)
NeuralDrive includes an optional, anonymous telemetry service.

- **Hardware**: GPU model name and system RAM capacity.
- **Performance**: Average TPS for loaded models.
- **Privacy**: No prompts or responses are ever sent. Telemetry is disabled by default and must be explicitly enabled in the TUI or WebUI settings.

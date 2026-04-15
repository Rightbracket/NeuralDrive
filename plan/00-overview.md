# NeuralDrive: Project Overview & Architecture

## 1. Project Summary

NeuralDrive is a purpose-built LiveCD/LiveUSB Linux distribution for running Large Language Models (LLMs) as a headless inference server. It boots from removable media, auto-detects GPU hardware, and presents a ready-to-use LLM serving environment with both local and remote management interfaces.

### Design Goals

| Priority | Goal | Measure of Success |
|----------|------|--------------------|
| P0 | Boot-to-inference in under 2 minutes | First API response within 120s of power-on |
| P0 | GPU auto-detection and acceleration | NVIDIA, AMD, and Intel Arc GPUs work without manual driver install |
| P0 | OpenAI-compatible API | Coding agents (Copilot, Cursor, etc.) can connect out of the box |
| P1 | Multiple concurrent models | Load/unload models without restarting services |
| P1 | USB persistence | Models, configs, and user data survive reboots |
| P1 | Minimal attack surface | Only essential services, firewall-first networking |
| P2 | Web dashboard | Remote model management and monitoring |
| P2 | Local TUI | Terminal-based management for direct access |
| P3 | Custom image toolkit | Users build their own NeuralDrive images with pre-loaded models |

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        BOOT MEDIA (USB/CD)                         │
├──────────┬──────────────┬──────────────────┬───────────────────────┤
│ EFI      │ Boot         │ System           │ Persistent Data       │
│ Partition│ (GRUB)       │ (SquashFS)       │ (ext4, USB only)      │
│ FAT32    │ ext2         │ Read-only rootfs │ /models, /config,     │
│ 512 MB   │ 1 GB         │ ~4-8 GB          │ /var — expandable     │
└──────────┴──────────────┴──────────────────┴───────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         RUNTIME STACK                              │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    Caddy (Reverse Proxy)                     │  │
│  │            :443/8443 → services, auto-TLS                    │  │
│  └──────────┬──────────────┬───────────────┬────────────────────┘  │
│             │              │               │                        │
│  ┌──────────▼───┐ ┌───────▼──────┐ ┌──────▼──────────┐           │
│  │   Ollama     │ │  Open WebUI  │ │  GPU Hot        │           │
│  │  (LLM API)   │ │  (Dashboard) │ │  (Monitoring)   │           │
│  │  :11434      │ │  :3000       │ │  :1312          │           │
│  └──────────────┘ └──────────────┘ └─────────────────┘           │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              NeuralDrive TUI (Local Terminal)                │  │
│  │     Model management, monitoring, service control            │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              GPU Driver Layer (auto-detected)                │  │
│  │   NVIDIA (nvidia-driver + CUDA) │ AMD (amdgpu + ROCm)       │  │
│  │   Intel Arc (compute-runtime)   │ CPU fallback (AVX/AVX2)   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              Debian 12 (bookworm) — Minimal Server           │  │
│  │              Linux 6.1 LTS + HWE backport kernel available   │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Technology Stack Decisions

### 3.1 Base Distribution: Debian 12 (bookworm)

**Decision**: Debian 12 stable with selective backports.

**Rationale**:
- **live-build** is the most mature and well-documented live image build system in existence. It is Debian's own official toolchain for producing live images, with comprehensive documentation at [live-team.pages.debian.net](https://live-team.pages.debian.net/live-manual/html/live-manual/index.en.html).
- NVIDIA provides official `.deb` packages for Debian, including `nvidia-driver`, `cuda-toolkit`, and `libcudnn`. These are well-tested and stable.
- Debian's non-free-firmware handling (improved in bookworm) simplifies GPU driver inclusion in live images.
- Stable kernel (6.1 LTS) reduces risk of driver incompatibilities. Backport kernels (6.12+) available when newer GPU support is needed.
- Largest package ecosystem ensures all dependencies are available without custom packaging.

**Alternatives considered**:
- *Arch Linux*: Latest kernels and NVIDIA packages, flexible archiso. Rejected due to rolling-release instability risk for a "just works" appliance, and requirement to build on an Arch host.
- *Alpine Linux*: Smallest footprint (~130 MB). Rejected due to limited GPU driver packaging and sparse ML ecosystem.
- *Ubuntu*: Good hardware support. Rejected due to snap complexity and Ubuntu-specific divergences from Debian that add friction without benefit for this use case.

### 3.2 LLM Runtime: Ollama (primary) + llama.cpp server (secondary)

**Decision**: Ship Ollama as the default runtime, with llama.cpp server available for advanced users.

**Rationale**:
- **Ollama** provides the best balance of ease-of-use and capability:
  - Built-in model management (pull, list, delete, create)
  - OpenAI-compatible API (`/v1/chat/completions`, `/v1/completions`, `/v1/embeddings`)
  - Automatic GPU detection (NVIDIA CUDA, AMD ROCm, Intel oneAPI)
  - Multi-model concurrency with automatic GPU memory management
  - GGUF format support (the most efficient format for inference)
  - Single binary, minimal dependencies
  - Active development, large community
- **llama.cpp server** (`llama-server`) provides:
  - Lower-level control over inference parameters
  - Slightly smaller memory footprint
  - Direct GGUF model loading without a management layer
  - Useful for users who want maximum control or minimal overhead

**Model format**: GGUF (primary). This is the standard quantized format for local inference, supported by both Ollama and llama.cpp. Quantization levels (Q4_K_M, Q5_K_M, Q8_0) provide flexibility between quality and resource usage.

### 3.3 GPU Support: Multi-vendor auto-detection

**Decision**: Pre-install drivers for NVIDIA, AMD, and Intel. Auto-detect at boot.

| Vendor | Driver Package | Compute Stack | Footprint |
|--------|---------------|---------------|-----------|
| NVIDIA | `nvidia-driver` (open kernel modules, 560+) | CUDA 12.x | ~3 GB |
| AMD | `amdgpu-dkms` | ROCm 6.x (HIP runtime) | ~6 GB |
| Intel | `intel-compute-runtime` | oneAPI Level Zero | ~500 MB |
| None | CPU fallback | AVX2/AVX-512 via llama.cpp | 0 |

Boot-time detection via PCI device enumeration loads appropriate kernel modules. Systems without a supported GPU fall back to CPU inference automatically.

### 3.4 User Interfaces

| Interface | Technology | Purpose |
|-----------|-----------|---------|
| Web Dashboard | Open WebUI | Remote model management, chat, monitoring |
| GPU Monitoring | GPU Hot | Real-time GPU metrics via web |
| Local TUI | Python + Textual | Terminal-based management and monitoring |
| API | Ollama API (OpenAI-compatible) | Programmatic access for coding agents |

### 3.5 Networking & Security

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Reverse Proxy | Caddy | Auto-TLS, routing, basic auth |
| Firewall | nftables | Default-deny, allowlist services |
| Encryption | LUKS2 | Optional encrypted persistent partition |
| SSH | OpenSSH (optional) | Key-only authentication, disabled by default |

### 3.6 Boot & Storage

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Bootloader | GRUB 2 | Hybrid BIOS + UEFI, CD + USB |
| Root filesystem | SquashFS + overlayfs | Read-only base with writable overlay |
| Persistence | ext4 partition on USB | Models, configs, user data |
| Image format | Hybrid ISO (isohybrid) | Compatible with CD burn and USB dd/Etcher |

---

## 4. Plan Document Structure

This plan is organized as a sequence of implementation documents. Each covers a distinct subsystem and can be implemented in order, though some parallelism is possible (noted below).

| File | Topic | Dependencies | Phase |
|------|-------|-------------|-------|
| `01-base-system.md` | Base OS, kernel, bootloader, build environment | None | 1 |
| `02-gpu-support.md` | GPU drivers, CUDA/ROCm, auto-detection | 01 | 1 |
| `03-llm-runtime.md` | Ollama, llama.cpp, model management | 01, 02 | 2 |
| `04-storage-persistence.md` | Partition layout, persistence, model storage | 01 | 1 |
| `05-security.md` | Hardening, firewall, TLS, authentication | 01 | 2 |
| `06-local-interface.md` | TUI application | 03 | 3 |
| `07-web-interface.md` | Open WebUI, GPU Hot, Caddy | 03, 05 | 3 |
| `08-api-services.md` | API layer, networking, remote access | 03, 05 | 3 |
| `09-image-toolkit.md` | Custom image builder for users | 01-08 | 4 |
| `10-testing-deployment.md` | Testing, QA, deployment, documentation | 01-09 | 4 |

### Implementation Phases

**Phase 1 — Foundation** (01, 02, 04): Build environment, base system that boots with GPU support and persistent storage. Target: bootable image with shell access and working GPU.

**Phase 2 — Core Services** (03, 05): LLM runtime installation and security hardening. Target: bootable image that serves LLM inference over API with basic security.

**Phase 3 — Interfaces** (06, 07, 08): User-facing management tools. Target: full user experience with TUI, web dashboard, and documented API access.

**Phase 4 — Distribution** (09, 10): Toolkit for users to build custom images, comprehensive testing, and release documentation. Target: shippable product with build-your-own capability.

---

## 5. Resource Requirements

### Minimum Hardware (7B model, Q4 quantization)
- CPU: x86_64 with AVX2 (most CPUs since ~2013)
- RAM: 8 GB (4 GB system + 4 GB model)
- GPU (optional): 6 GB VRAM (NVIDIA GTX 1060+ / AMD RX 580+)
- Storage: 16 GB USB drive (8 GB system + 8 GB for one model)

### Recommended Hardware (13B-70B models)
- CPU: x86_64 with AVX-512
- RAM: 32-64 GB
- GPU: 24 GB+ VRAM (NVIDIA RTX 3090/4090, AMD RX 7900 XTX)
- Storage: 128 GB+ USB drive or external SSD

### Build Environment
- Host: Debian 12+ or Ubuntu 22.04+ (for live-build)
- Disk: 50 GB free space for build working directory
- RAM: 4 GB minimum
- Internet: Required for package downloads during build
- Alternative: Docker-based build (any OS with Docker)

---

## 6. Key Design Decisions & Trade-offs

### Why LiveCD/USB instead of a regular install?
- Zero commitment: boot, use, remove. No changes to host system.
- Portable: carry your LLM server in your pocket.
- Reproducible: every boot starts from a known-good state (except persistent data).
- Secure: read-only root filesystem limits attack surface.

### Why not Docker/VM-based instead?
- Direct hardware access: GPU passthrough in VMs adds latency and complexity.
- Lower overhead: no hypervisor/container runtime layer between LLM and GPU.
- Simpler: one boot, everything works. No OS + Docker + container orchestration.

### Why Debian over Arch?
- Stability over freshness. A live system that "just works" is more valuable than having the latest kernel for most users. Backports bridge the gap when needed.
- live-build is purpose-built for this exact use case. archiso is good but less battle-tested for custom appliance images.

### Why Ollama over raw llama.cpp?
- Model management. Downloading, cataloging, and switching models via `ollama pull` / `ollama list` is dramatically simpler than manually downloading GGUF files.
- API completeness. Ollama's OpenAI-compatible API includes streaming, function calling, and embeddings — the full surface coding agents expect.
- Both are available. Advanced users can bypass Ollama and use llama-server directly.

### Why Open WebUI over building from scratch?
- 131K GitHub stars, active development, full feature set (model management, chat, RAG, multi-user, API keys). Building a comparable dashboard would take months and provide less functionality.
- It integrates with Ollama natively and supports any OpenAI-compatible backend.

---

## 7. Naming & Branding

- **Project name**: NeuralDrive
- **Config directory**: `/etc/neuraldrive/`
- **Data directory**: `/var/lib/neuraldrive/`
- **Model storage**: `/var/lib/neuraldrive/models/` (symlinked to persistent partition on USB)
- **Log directory**: `/var/log/neuraldrive/`
- **Service prefix**: `neuraldrive-*` (systemd units)
- **Default hostname**: `neuraldrive`
- **Default mDNS**: `neuraldrive.local`

# NeuralDrive Documentation Plan

> Detailed specification for user-facing and developer/maintainer documentation.
> Tool: mdbook v0.5.2. Two separate books sharing a common build.

---

## 1. Documentation Architecture

### 1.1 Two Separate Books

NeuralDrive documentation is split into two independent mdbook projects:

| Book | Directory | Audience | Deployment |
|------|-----------|----------|------------|
| **User Guide** | `docs/user-guide/` | End users (hobbyists, devs, admins) | Published to project site / GitHub Pages |
| **Developer Guide** | `docs/dev-guide/` | Open source contributors | Published alongside, linked from CONTRIBUTING.md |

**Rationale**: Separate books avoid cognitive overload. Users never see build system internals; contributors never wade through quick-start tutorials to find architecture docs. Cross-linking between books is done via relative URLs.

**Note**: The existing `plan/` directory remains internal project planning and is NOT incorporated into either documentation book. Docs are written fresh with user/developer audiences in mind, drawing on plan/ as source material but not copying it.

### 1.2 Audience Profiles

All three user types are served equally, with clear signposting:

| Persona | Profile | Needs | Signposting |
|---------|---------|-------|-------------|
| **Home Lab Hobbyist** | Comfortable flashing a USB, basic terminal use, not a Linux expert | Quick-start, visual guides, "just works" instructions | Default path. No jargon without explanation. |
| **Developer / AI Engineer** | Integrating with coding agents, building apps against the API | API reference, SDK examples, client configuration, cert trust | Sections marked with `[Developer]` badges |
| **IT Admin / Sysadmin** | Deploying on physical hardware in office/lab, managing security | Network config, security hardening, monitoring, fleet deployment | Sections marked with `[Admin]` badges |

**Skill-level convention**: Each chapter opens with a one-line audience note:
> *"This chapter is for everyone"* / *"This chapter assumes familiarity with REST APIs"* / *"This chapter assumes Linux system administration experience"*

---

## 2. User Guide — Detailed Chapter Specification

### SUMMARY.md Structure

```
# Summary

[Introduction](./introduction.md)

# Getting Started

- [What is NeuralDrive?](./getting-started/what-is-neuraldrive.md)
- [Hardware Requirements](./getting-started/hardware-requirements.md)
- [Quick Start](./getting-started/quick-start.md)
- [Writing the USB Drive](./getting-started/writing-usb.md)
- [First Boot Setup](./getting-started/first-boot.md)

# Using NeuralDrive

- [Web Dashboard](./using/web-dashboard.md)
  - [Chat Interface](./using/chat.md)
  - [Model Management](./using/models-web.md)
  - [RAG Documents](./using/rag.md)
- [Terminal Interface (TUI)](./using/tui.md)
  - [Dashboard](./using/tui-dashboard.md)
  - [Model Management](./using/models-tui.md)
  - [Service Control](./using/tui-services.md)
  - [Log Viewer](./using/tui-logs.md)
- [Local Chat](./using/local-chat.md)

# Working with Models

- [Understanding LLM Models](./models/understanding-models.md)
- [Downloading Models](./models/downloading.md)
- [Model Recommendations by Hardware](./models/recommendations.md)
- [Storage Management](./models/storage.md)
- [Pre-loading Models into Images](./models/preloading.md)

# API & Integration

- [API Overview](./api/overview.md)
- [Connecting Coding Agents](./api/coding-agents.md)
- [Python SDK Examples](./api/python-sdk.md)
- [curl Examples](./api/curl-examples.md)
- [TLS Certificate Trust](./api/tls-trust.md)
- [API Key Management](./api/api-keys.md)
- [Ollama Native API](./api/ollama-native.md)

# System Administration

- [Network Configuration](./admin/network.md)
- [Security](./admin/security.md)
  - [Firewall](./admin/firewall.md)
  - [TLS Certificates](./admin/tls-certs.md)
  - [SSH Access](./admin/ssh.md)
- [GPU Monitoring](./admin/gpu-monitoring.md)
- [Service Management](./admin/services.md)
- [Updating NeuralDrive](./admin/updating.md)
- [System Management API](./admin/system-api.md)

# Advanced

- [Building Custom Images](./advanced/custom-images.md)
- [Build Configuration Reference](./advanced/build-config-reference.md)
- [Custom Hooks & Overlays](./advanced/hooks-overlays.md)
- [CD Mode vs USB Mode](./advanced/cd-vs-usb.md)
- [External Storage](./advanced/external-storage.md)
- [LUKS Encryption](./advanced/encryption.md)
- [Performance Tuning](./advanced/performance.md)
- [llama.cpp Server (Advanced)](./advanced/llama-cpp.md)

# Troubleshooting

- [Common Issues](./troubleshooting/common-issues.md)
- [GPU Problems](./troubleshooting/gpu.md)
- [Boot Failures](./troubleshooting/boot.md)
- [Network & mDNS](./troubleshooting/network.md)
- [Model Loading Issues](./troubleshooting/models.md)
- [FAQ](./troubleshooting/faq.md)

# Reference

- [Hardware Compatibility Matrix](./reference/hardware-matrix.md)
- [Configuration Files](./reference/config-files.md)
- [Boot Parameters](./reference/boot-parameters.md)
- [Service Reference](./reference/services.md)
- [API Endpoint Reference](./reference/api-endpoints.md)
- [System Management API Reference](./reference/system-api-endpoints.md)
- [Port Reference](./reference/ports.md)
- [Glossary](./reference/glossary.md)
```

### Per-Chapter Outlines

---

#### Introduction (`introduction.md`)
- **Audience**: Everyone
- **Length**: ~300 words
- **Content**:
  - One-paragraph elevator pitch: what NeuralDrive is and why it exists
  - How to use this documentation (audience badges, navigation tips)
  - Links to quick-start for impatient users
  - Version this documentation covers
- **Cross-refs**: Quick Start, What is NeuralDrive

---

#### What is NeuralDrive? (`getting-started/what-is-neuraldrive.md`)
- **Audience**: Everyone
- **Length**: ~800 words
- **Content**:
  - Problem statement: running LLMs locally shouldn't require Linux expertise
  - What NeuralDrive provides: boot-from-USB LLM server with auto GPU detection
  - Key features list (bullet points):
    - Boot-to-inference in under 2 minutes
    - NVIDIA / AMD / Intel GPU auto-detection
    - OpenAI-compatible API (works with Cursor, Continue, etc.)
    - Web dashboard for chat and model management
    - Terminal interface for local management
    - USB persistence for models and config
    - Custom image builder toolkit
  - Architecture diagram (simplified version of plan/00 diagram)
  - Design goals table (from plan/00 §1, simplified for users)
  - Use cases: home lab, development workstation, small office, air-gapped environments
  - What NeuralDrive is NOT (not a cloud service, not a Docker image, not a full desktop OS)
- **Cross-refs**: Hardware Requirements, Quick Start

---

#### Hardware Requirements (`getting-started/hardware-requirements.md`)
- **Audience**: Everyone
- **Length**: ~600 words + tables
- **Content**:
  - Minimum requirements table (7B model, Q4 quantization):
    - CPU: x86_64 with AVX2
    - RAM: 8 GB
    - GPU: Optional, 6 GB VRAM minimum
    - USB: 16 GB
  - Recommended requirements table (13B-70B models):
    - CPU: x86_64 with AVX-512
    - RAM: 32-64 GB
    - GPU: 24 GB+ VRAM
    - USB: 128 GB+ or external SSD
  - GPU compatibility matrix (from plan/10 §3):
    - NVIDIA: Pascal (1080) through Ada Lovelace (4090) — fully supported
    - AMD: RDNA 2 and RDNA 3 — supported via ROCm
    - Intel Arc: A380-A770 — experimental
    - No GPU: CPU fallback with AVX2/AVX-512
  - Model size vs hardware cheat sheet:
    - 3B model → 8GB RAM, any GPU
    - 8B model → 16GB RAM, 8GB VRAM recommended
    - 70B model → 64GB RAM, 24GB+ VRAM required
  - Secure Boot note (NVIDIA may require MOK or Secure Boot disable)
  - USB drive recommendations (USB 3.0+, SSD preferred for large model libraries)
- **Cross-refs**: Model Recommendations by Hardware, GPU Problems

---

#### Quick Start (`getting-started/quick-start.md`)
- **Audience**: Everyone
- **Length**: ~500 words (terse, numbered steps)
- **Content**:
  - Prerequisite: downloaded NeuralDrive ISO, USB drive, target machine
  - Step 1: Flash USB (`dd` command, Balena Etcher, Rufus, or `neuraldrive-flash`)
  - Step 2: Create persistence partition (`prepare-usb.sh` or `neuraldrive-flash` which does both)
  - Step 3: Boot from USB (BIOS boot menu key, UEFI boot order)
  - Step 4: Complete first-boot wizard on the console
  - Step 5: Open browser to displayed IP address
  - Step 6: Log in with displayed credentials
  - Step 7: Pull your first model and start chatting
  - Callout box: "Want to connect a coding agent? See Connecting Coding Agents"
  - Callout box: "Booting from CD? See CD Mode vs USB Mode"
- **Cross-refs**: Writing the USB Drive, First Boot Setup, Connecting Coding Agents
- **Notes**: This should be printable as a "quick-start card" (single page). Keep it scannable.

---

#### Writing the USB Drive (`getting-started/writing-usb.md`)
- **Audience**: Everyone
- **Length**: ~800 words
- **Content**:
  - Option A: `neuraldrive-flash` (automated — handles dd + persistence partition)
  - Option B: Manual with `dd` + `prepare-usb.sh`
  - Option C: Balena Etcher / Rufus (GUI tools) + manual `prepare-usb.sh`
  - Option D: Ventoy (ISO boot from multi-boot USB)
  - Partition layout diagram explaining what each partition does
  - Verification: how to confirm the USB was written correctly
  - Warning box: "Writing an ISO destroys all existing data on the USB drive"
  - CD burning instructions (brief, for the CD mode audience)
- **Cross-refs**: Quick Start, CD Mode vs USB Mode, Updating NeuralDrive

---

#### First Boot Setup (`getting-started/first-boot.md`)
- **Audience**: Everyone
- **Length**: ~1000 words + screenshots/mockups
- **Content**:
  - What happens at boot (GRUB menu, driver detection, service startup)
  - GRUB menu options explained (Normal, Safe Mode, CD Mode, Debug)
  - Console output: IP address display, "NeuralDrive is ready!" message
  - First-boot wizard walkthrough (step by step):
    1. Welcome — hardware summary
    2. Security — admin password and API key generation
    3. Wi-Fi (if applicable) — SSID selection
    4. Network — DHCP or static IP
    5. Storage — persistence drive, optional LUKS encryption
    6. Models — recommended starter models based on detected hardware
    7. Finish — credentials display, dashboard URL
  - Important: "Write down your admin password and API key!"
  - Note: "First-boot requires a local keyboard and monitor. After setup, you can manage everything remotely."
  - What to do next (web dashboard, TUI, or API)
- **Cross-refs**: Security, Web Dashboard, Terminal Interface

---

#### Web Dashboard (`using/web-dashboard.md`)
- **Audience**: Everyone
- **Length**: ~600 words
- **Content**:
  - What Open WebUI provides (chat, model management, RAG, multi-user)
  - Accessing the dashboard: `https://<IP>/` or `https://neuraldrive.local/`
  - Login with first-boot credentials
  - Dashboard layout overview
  - NeuralDrive System Panel introduction (port 8443)
  - Two-application architecture explained simply
- **Cross-refs**: Chat Interface, Model Management, System Management API

#### Chat Interface (`using/chat.md`)
- **Audience**: Everyone
- **Length**: ~500 words
- **Content**:
  - Starting a new conversation
  - Selecting a model from the dropdown
  - Streaming responses
  - Conversation history
  - Keyboard shortcuts
- **Cross-refs**: Model Management, Downloading Models

#### Model Management (Web) (`using/models-web.md`)
- **Audience**: Everyone
- **Length**: ~500 words
- **Content**:
  - Viewing installed models
  - Pulling new models (search, download, progress)
  - Deleting models
  - Model details (size, quantization, format)
- **Cross-refs**: Understanding LLM Models, Storage Management

#### RAG Documents (`using/rag.md`)
- **Audience**: Developers
- **Length**: ~400 words
- **Content**:
  - What RAG is (brief explanation)
  - Uploading documents
  - Using documents in conversations
  - Limitations on a LiveUSB system
- **Cross-refs**: Chat Interface

---

#### Terminal Interface (TUI) (`using/tui.md`)
- **Audience**: Everyone
- **Length**: ~500 words + TUI mockup
- **Content**:
  - What the TUI is and when to use it (local management, no browser needed)
  - How to access (auto-launches on tty1, or `neuraldrive-tui` from shell)
  - Main dashboard layout explanation (mockup from plan/06 §2)
  - Navigation: M/S/N/L/C/Q keybindings
  - Exiting to shell (Q)
- **Cross-refs**: TUI Dashboard, First Boot Setup

#### TUI sub-pages (dashboard, models, services, logs) — each ~300 words
- Per-screen navigation, key bindings, what information is displayed
- Mockups from plan/06 §2

---

#### Understanding LLM Models (`models/understanding-models.md`)
- **Audience**: Everyone (educational)
- **Length**: ~800 words
- **Content**:
  - What is an LLM? (one paragraph, non-technical)
  - Model sizes: parameter count (3B, 8B, 13B, 70B) and what it means
  - Quantization explained simply: Q4, Q5, Q8 — tradeoff between quality and resource usage
  - GGUF format: what it is, why NeuralDrive uses it
  - Model naming convention: `llama3.1:8b`, `codestral:latest`, `phi3:mini`
  - How model size relates to VRAM and RAM
- **Cross-refs**: Hardware Requirements, Model Recommendations by Hardware

#### Downloading Models (`models/downloading.md`)
- **Audience**: Everyone
- **Length**: ~500 words
- **Content**:
  - Via Web Dashboard (Open WebUI Models page)
  - Via TUI (P key on Models screen)
  - Via command line (`ollama pull <model>`)
  - Via API (`POST /api/pull`)
  - Download progress and cancellation
  - Where models are stored on disk
- **Cross-refs**: Storage Management, Ollama Native API

#### Model Recommendations by Hardware (`models/recommendations.md`)
- **Audience**: Everyone
- **Length**: ~600 words + table
- **Content**:
  - Recommendation table: GPU VRAM → suggested models
    - 6 GB: qwen2.5:3b, phi3:mini
    - 8 GB: llama3.1:8b
    - 12 GB: codestral:latest
    - 24 GB+: llama3.1:70b (Q4_K_M)
  - CPU-only recommendations
  - Tips for running multiple models concurrently
  - Model catalog (`neuraldrive-models.yaml`) description
- **Cross-refs**: Hardware Requirements, Understanding LLM Models

#### Storage Management (`models/storage.md`)
- **Audience**: Everyone / Admin
- **Length**: ~500 words
- **Content**:
  - Checking available space (TUI, web, command line)
  - Storage thresholds (80% warning, 90% critical, 95% blocks downloads)
  - Deleting unused models to free space
  - External storage support
  - USB drive size recommendations
- **Cross-refs**: External Storage, Model Recommendations

#### Pre-loading Models into Images (`models/preloading.md`)
- **Audience**: Admin
- **Length**: ~400 words
- **Content**:
  - Why pre-load (offline environments, faster deployment)
  - Using `neuraldrive-build.yaml` `models.preload` setting
  - Two-phase build approach (brief, link to custom images chapter for detail)
- **Cross-refs**: Building Custom Images, Build Configuration Reference

---

#### API Overview (`api/overview.md`)
- **Audience**: Developers
- **Length**: ~600 words
- **Content**:
  - Two APIs: OpenAI-compatible (port 8443 /v1/) and Ollama native (port 8443 /api/)
  - Authentication: Bearer token required for all API calls
  - Base URL: `https://neuraldrive.local:8443/v1`
  - Self-signed TLS: why and how to handle it
  - System Management API (port 8443 /system/) — separate from inference API
  - Rate limiting: 100 req/min per source IP
  - Timeouts: 600s for generation, 30s for management
- **Cross-refs**: TLS Certificate Trust, API Key Management, API Endpoint Reference

#### Connecting Coding Agents (`api/coding-agents.md`)
- **Audience**: Developers
- **Length**: ~800 words
- **Content**:
  - Generic setup pattern: Provider=OpenAI Compatible, Base URL, API Key
  - **Cursor**: step-by-step configuration
  - **Continue**: step-by-step configuration
  - **GitHub Copilot** (with compatible proxy): notes
  - **Aider**: command-line flags
  - **Open Interpreter**: configuration
  - **LM Studio** (as client): configuration
  - TLS trust: brief note + link to TLS Certificate Trust chapter
  - Troubleshooting: "Connection refused" → check firewall, IP, port
- **Cross-refs**: API Overview, TLS Certificate Trust, Troubleshooting FAQ

#### Python SDK Examples (`api/python-sdk.md`)
- **Audience**: Developers
- **Length**: ~600 words + code blocks
- **Content**:
  - OpenAI Python SDK: streaming and non-streaming examples
  - Certificate trust setup (3 options from plan/08 §2)
  - Embedding API example
  - Function calling example
  - Error handling patterns
- **Cross-refs**: API Overview, TLS Certificate Trust

#### curl Examples (`api/curl-examples.md`)
- **Audience**: Developers
- **Length**: ~400 words + code blocks
- **Content**:
  - Chat completion
  - Model listing
  - Model pulling
  - Health check
  - Using `--cacert` vs `-k` (and why to prefer `--cacert`)
- **Cross-refs**: API Overview, TLS Certificate Trust

#### TLS Certificate Trust (`api/tls-trust.md`)
- **Audience**: Developers / Admin
- **Length**: ~700 words
- **Content**:
  - Why NeuralDrive uses self-signed certs
  - Downloading the CA cert (via SCP, via API endpoint `/system/ca-cert`, via browser)
  - Installing the cert:
    - macOS (Keychain)
    - Linux (ca-certificates)
    - Windows (Certificate Manager)
    - Python (REQUESTS_CA_BUNDLE, SSL_CERT_FILE, httpx verify param)
    - Node.js (NODE_EXTRA_CA_CERTS)
    - curl (--cacert)
  - Regenerating certificates after IP change
  - Using user-provided certificates
- **Cross-refs**: Security, Python SDK Examples, curl Examples

#### API Key Management (`api/api-keys.md`)
- **Audience**: Developers / Admin
- **Length**: ~400 words
- **Content**:
  - Where to find your API key (first-boot display, TUI, credentials file)
  - Rotating API keys (TUI, System API endpoint)
  - Pre-setting API keys in custom images
  - API key format: `nd-xxxxxxxxxxxxxxxx`
- **Cross-refs**: Security, Building Custom Images

#### Ollama Native API (`api/ollama-native.md`)
- **Audience**: Developers
- **Length**: ~400 words
- **Content**:
  - When to use native API vs OpenAI-compatible
  - Endpoint list (/api/generate, /api/chat, /api/tags, /api/pull, /api/show)
  - Using ollama CLI remotely (`OLLAMA_HOST` environment variable)
  - Authentication requirement
- **Cross-refs**: API Overview, API Endpoint Reference

---

#### Network Configuration (`admin/network.md`)
- **Audience**: Admin
- **Length**: ~500 words
- **Content**:
  - Default: DHCP via NetworkManager
  - Static IP configuration (TUI, nmcli)
  - Hostname configuration
  - mDNS / Avahi: neuraldrive.local
  - mDNS troubleshooting (doesn't work on all networks)
  - Always check IP address on console
- **Cross-refs**: First Boot Setup, Network Troubleshooting

#### Security (`admin/security.md`)
- **Audience**: Admin
- **Length**: ~600 words (overview, links to sub-pages)
- **Content**:
  - Security design principles (defense in depth, minimal attack surface, read-only root)
  - Default security posture summary
  - Links to: Firewall, TLS Certificates, SSH Access
  - Data protection: file permissions model
  - Audit logging
- **Cross-refs**: Firewall, TLS Certificates, SSH Access, LUKS Encryption

#### Firewall (`admin/firewall.md`)
- **Audience**: Admin
- **Length**: ~400 words
- **Content**:
  - Default policy: drop all incoming except 443, 8443, 5353
  - SSH port (22) only open when SSH enabled, rate-limited
  - Custom rules: `/etc/neuraldrive/firewall-custom.conf`
  - Viewing active rules
- **Cross-refs**: Security, SSH Access

#### TLS Certificates (`admin/tls-certs.md`)
- **Audience**: Admin
- **Length**: ~400 words
- **Content**:
  - Auto-generated at first boot
  - SAN includes hostname + IP address
  - Regenerating (delete + restart service)
  - Using your own certificates (replace files, restart Caddy)
  - Certificate file locations
- **Cross-refs**: TLS Certificate Trust, Security

#### SSH Access (`admin/ssh.md`)
- **Audience**: Admin
- **Length**: ~400 words
- **Content**:
  - Disabled by default
  - Enabling via TUI, boot parameter, or API
  - Key-only authentication (no passwords)
  - Adding SSH keys
  - fail2ban protection
  - SSH hardening details
- **Cross-refs**: Security, Firewall

#### GPU Monitoring (`admin/gpu-monitoring.md`)
- **Audience**: Everyone / Admin
- **Length**: ~400 words
- **Content**:
  - TUI dashboard (real-time VRAM, temperature, utilization)
  - Web System Panel GPU page
  - Command-line: nvidia-smi, rocm-smi
  - GPU Hot web dashboard
- **Cross-refs**: Terminal Interface, System Management API

#### Service Management (`admin/services.md`)
- **Audience**: Admin
- **Length**: ~500 words
- **Content**:
  - List of NeuralDrive services and what they do
  - Checking service status (TUI, web, systemctl)
  - Restarting services
  - Service dependency order
  - Storage monitoring service (automated threshold alerts at 80%/90%/95%)
  - systemd journal log access
- **Cross-refs**: Service Reference, TUI Services

#### Updating NeuralDrive (`admin/updating.md`)
- **Audience**: Everyone
- **Length**: ~600 words
- **Content**:
  - Update model: new ISO → reflash USB
  - Step-by-step upgrade procedure:
    1. Back up persistent data
    2. Re-flash USB with new ISO
    3. Recreate persistence partition
    4. Restore data (optional)
  - Warning: re-flashing destroys persistence partition
  - Version checking (/etc/neuraldrive/version)
  - Future: `neuraldrive-upgrade` tool
- **Cross-refs**: Writing the USB Drive, Storage Management

#### System Management API (`admin/system-api.md`)
- **Audience**: Admin / Developers
- **Length**: ~500 words
- **Content**:
  - What the System Panel API provides
  - Access: `https://<IP>:8443/system/`
  - Authentication (same API key as inference API)
  - Quick overview of endpoints (table)
  - Link to full reference
- **Cross-refs**: System Management API Reference

---

#### Building Custom Images (`advanced/custom-images.md`)
- **Audience**: Admin
- **Length**: ~1000 words
- **Content**:
  - What the neuraldrive-builder toolkit is
  - Prerequisites: Docker (recommended) or Debian 12 with live-build
  - Step-by-step build process:
    1. Clone repo
    2. Copy `neuraldrive-build.yaml.example` → `neuraldrive-build.yaml`
    3. Edit configuration
    4. Run `build.sh` (or `docker compose run builder`)
    5. Flash output ISO
  - Configuration highlights (GPU selection, model pre-loading, branding)
  - Build time estimates
  - Output formats (iso-hybrid, raw-disk)
  - **Important note**: Model pre-loading currently requires a manual step — `scripts/download-models.sh` stages models into `./model-staging/`, but packaging them into `models.squashfs` or copying into `config/includes.chroot/` is not yet automated. Document this as a known manual step.
- **Cross-refs**: Build Configuration Reference, Custom Hooks & Overlays

#### Build Configuration Reference (`advanced/build-config-reference.md`)
- **Audience**: Admin
- **Length**: ~800 words + annotated YAML
- **Content**:
  - Full `neuraldrive-build.yaml` with every key documented
  - Sections: system, gpu, models, network, security, webui, output
  - Default values and valid options for each field
  - Examples for common configurations:
    - NVIDIA-only minimal image
    - Full image with pre-loaded models
    - Custom branded image
- **Cross-refs**: Building Custom Images

#### Custom Hooks & Overlays (`advanced/hooks-overlays.md`)
- **Audience**: Admin (advanced)
- **Length**: ~600 words
- **Content**:
  - Hook system: scripts in `hooks/chroot/` run during image build
  - Overlay system: files in `overlay/` mirror root filesystem
  - Package injection: `.deb` files in `packages/`
  - Examples: installing custom pip packages, adding config files
- **Cross-refs**: Building Custom Images

#### CD Mode vs USB Mode (`advanced/cd-vs-usb.md`)
- **Audience**: Everyone
- **Length**: ~500 words
- **Content**:
  - USB mode: full features, persistence, model downloads
  - CD mode: read-only, tmpfs, no model downloads, connect external storage
  - CD-to-RAM boot option (loads entire image to RAM)
  - When to use each mode
  - Messaging: what users see in CD mode and why
- **Cross-refs**: External Storage, First Boot Setup

#### External Storage (`advanced/external-storage.md`)
- **Audience**: Admin
- **Length**: ~400 words
- **Content**:
  - Auto-mount via udev rules
  - Configuring external model storage
  - Mount point: `/mnt/external/<LABEL>`
  - Bind-mount configuration
- **Cross-refs**: Storage Management, CD Mode vs USB Mode

#### LUKS Encryption (`advanced/encryption.md`)
- **Audience**: Admin
- **Length**: ~500 words
- **Content**:
  - What LUKS2 encryption protects
  - Enabling during first-boot wizard
  - Boot experience with encryption (passphrase prompt)
  - Implications for performance
  - Warning: formatting is destructive
- **Cross-refs**: First Boot Setup, Security

#### Performance Tuning (`advanced/performance.md`)
- **Audience**: Admin / Developers
- **Length**: ~600 words
- **Content**:
  - Ollama configuration tuning (OLLAMA_NUM_PARALLEL, OLLAMA_KEEP_ALIVE, OLLAMA_MAX_LOADED_MODELS)
  - Thread count optimization (OLLAMA_NUM_THREADS)
  - Flash attention
  - Memory mapping (mmap)
  - Context window sizing
  - zram swap
  - Disk I/O optimizations (noatime, commit=60)
  - Multi-GPU setup
- **Cross-refs**: Configuration Files Reference, Model Recommendations

#### llama.cpp Server (`advanced/llama-cpp.md`)
- **Audience**: Developers (advanced)
- **Length**: ~400 words
- **Content**:
  - When to use llama.cpp server vs Ollama
  - Enabling the service
  - Direct GGUF model loading
  - Configuration options
  - Comparison table (from plan/03 §2)
- **Cross-refs**: Understanding LLM Models, Performance Tuning

---

#### Common Issues (`troubleshooting/common-issues.md`)
- **Audience**: Everyone
- **Length**: ~800 words
- **Content**:
  - "I can't reach the web dashboard" → check IP, firewall, port
  - "My models disappeared after reboot" → persistence partition issue
  - "The API returns 401 Unauthorized" → check API key, Bearer header
  - "Model download is extremely slow" → check network, storage space
  - "The system is running out of memory" → model too large for hardware
  - "The TUI shows 'Ollama Offline'" → check service status
  - Using `neuraldrive-check` health check tool (`/usr/bin/neuraldrive-check`) for quick diagnostics
- **Cross-refs**: Relevant deeper troubleshooting pages

#### GPU Problems (`troubleshooting/gpu.md`)
- **Audience**: Everyone
- **Length**: ~600 words
- **Content**:
  - "No GPU detected" → check compatibility, Secure Boot, BIOS settings
  - Secure Boot and NVIDIA (MOK enrollment)
  - Nouveau conflict
  - Safe Mode boot option
  - Diagnostic commands (nvidia-smi, rocm-smi, lspci)
  - Mixed vendor GPUs (not supported in this release)
- **Cross-refs**: Hardware Compatibility Matrix, Boot Parameters

#### Boot Failures (`troubleshooting/boot.md`)
- **Audience**: Everyone
- **Length**: ~400 words
- **Content**:
  - BIOS vs UEFI boot
  - Boot order configuration
  - GRUB Debug mode
  - Common errors and fixes
- **Cross-refs**: Boot Parameters, Writing the USB Drive

#### Network & mDNS (`troubleshooting/network.md`)
- **Audience**: Everyone
- **Length**: ~400 words
- **Content**:
  - "neuraldrive.local doesn't resolve" → use IP address instead
  - mDNS limitations (corporate networks, missing Bonjour)
  - "HTTPS certificate warning" → install CA cert
  - Wi-Fi connectivity issues
- **Cross-refs**: Network Configuration, TLS Certificate Trust

#### Model Loading Issues (`troubleshooting/models.md`)
- **Audience**: Everyone
- **Length**: ~400 words
- **Content**:
  - "Model failed to load" → insufficient VRAM/RAM
  - "Downloads disabled" → CD mode, need USB or external storage
  - Slow inference → CPU fallback, check GPU detection
  - Model corruption → re-pull
- **Cross-refs**: Model Recommendations, GPU Problems

#### FAQ (`troubleshooting/faq.md`)
- **Audience**: Everyone
- **Length**: ~800 words
- **Content**:
  - Q: Can I install NeuralDrive to a hard drive? A: Not designed for this; it's a Live system.
  - Q: Can I run it in a VM? A: Yes with GPU passthrough, but that's advanced.
  - Q: Can I use it without a GPU? A: Yes, CPU inference works but is slower.
  - Q: How do I add more users? A: Via Open WebUI admin panel.
  - Q: Can I use it offline? A: Yes, with pre-loaded models.
  - Q: How is this different from running Ollama directly? A: Turnkey appliance, no OS setup, portable.
  - Q: What models are recommended? A: See Model Recommendations.
  - Q: Can I use my own TLS certificate? A: Yes, see TLS Certificates.
  - Q: Is there telemetry? A: Optional, disabled by default, anonymous hardware stats only.
- **Cross-refs**: Various

---

#### Reference Pages (each ~400-600 words, mostly tables)

- **Hardware Compatibility Matrix**: Full GPU table with driver version, compute stack, status
- **Configuration Files**: Every file in `/etc/neuraldrive/` with purpose, format, ownership
- **Boot Parameters**: GRUB kernel parameters and their effects
- **Service Reference**: Every `neuraldrive-*` service with description, port, user, dependencies
- **API Endpoint Reference**: OpenAI-compatible endpoints with request/response schemas
- **System Management API Reference**: All `/system/*` endpoints with request/response schemas
- **Port Reference**: All ports, what service uses them, internal vs external
- **Glossary**: GGUF, quantization, VRAM, SquashFS, overlayfs, live-boot, persistence, mDNS, etc.

---

## 3. Developer Guide — Detailed Chapter Specification

### SUMMARY.md Structure

```
# Summary

[Introduction](./introduction.md)

# Getting Started

- [Development Environment Setup](./getting-started/dev-environment.md)
- [Building from Source](./getting-started/building.md)
- [Running Tests](./getting-started/testing.md)

# Contributing

- [How to Contribute](./contributing/how-to-contribute.md)
- [Code Style & Standards](./contributing/code-style.md)
- [Pull Request Process](./contributing/pr-process.md)
- [Issue Guidelines](./contributing/issues.md)

# Architecture

- [System Overview](./architecture/overview.md)
- [Boot Sequence](./architecture/boot-sequence.md)
- [Service Dependency Graph](./architecture/service-dependencies.md)
- [Storage Architecture](./architecture/storage.md)
- [Network Architecture](./architecture/network.md)
- [Security Model](./architecture/security.md)

# Build System

- [live-build Overview](./build/live-build.md)
- [Directory Structure](./build/directory-structure.md)
- [Build Hooks](./build/hooks.md)
- [Package Lists](./build/package-lists.md)
- [Archive Sources](./build/archive-sources.md)
- [Docker Build Environment](./build/docker.md)
- [CI/CD Pipeline](./build/cicd.md)

# Components

- [GPU Auto-Detection](./components/gpu-detection.md)
- [Ollama Integration](./components/ollama.md)
- [Open WebUI Integration](./components/open-webui.md)
- [Caddy Reverse Proxy](./components/caddy.md)
- [System Management API](./components/system-api.md)
- [Terminal User Interface (TUI)](./components/tui.md)
- [First-Boot Wizard](./components/first-boot-wizard.md)
- [Certificate Generation](./components/certificates.md)

# Testing

- [Test Strategy](./testing/strategy.md)
- [QEMU Boot Tests](./testing/qemu.md)
- [GPU Testing](./testing/gpu-testing.md)
- [API Tests](./testing/api-tests.md)
- [Hardware Compatibility Testing](./testing/hardware.md)
- [Performance Benchmarking](./testing/benchmarks.md)

# Release

- [Versioning](./release/versioning.md)
- [Release Checklist](./release/checklist.md)
- [ISO Signing](./release/signing.md)
- [Image Variants](./release/variants.md)
```

### Per-Chapter Outlines

---

#### Introduction (`introduction.md`)
- **Length**: ~300 words
- **Content**:
  - Welcome to the NeuralDrive developer documentation
  - Who this is for (contributors, maintainers, anyone building custom images)
  - Link to User Guide for end-user documentation
  - Technology overview: Debian 12 + live-build + Ollama + Open WebUI + Caddy + Python TUI

---

#### Development Environment Setup (`getting-started/dev-environment.md`)
- **Length**: ~800 words
- **Content**:
  - Option A: Debian 12 host (native, recommended for fast iteration)
  - Option B: Docker (any OS)
  - Option C: VM running Debian 12
  - Installing dependencies (live-build, debootstrap, etc.)
  - Cloning the repository
  - Directory layout explanation
  - QEMU setup for boot testing
  - Python venv setup for TUI/API development
  - Editor setup recommendations

#### Building from Source (`getting-started/building.md`)
- **Length**: ~600 words
- **Content**:
  - Full build: `./build.sh` or `docker compose run builder`
  - Clean build: `lb clean --all`
  - Incremental builds
  - Build output location
  - Common build errors and fixes
  - Build time expectations (30-90 minutes with GPU stacks)

#### Running Tests (`getting-started/testing.md`)
- **Length**: ~400 words
- **Content**:
  - `tests/test-boot.sh` — QEMU boot verification
  - `tests/test-gpu.sh` — on-target GPU verification
  - `tests/test_api.py` — API integration tests with pytest
  - Running individual vs full test suite
  - CI/CD test automation

---

#### Contributing chapters (4 pages, ~400 words each)
- How to Contribute: finding issues, discussion, contribution types
- Code Style: shell script conventions, Python (ruff), YAML formatting, commit messages
- PR Process: branch naming, review process, CI requirements
- Issue Guidelines: bug reports, feature requests, templates

---

#### Architecture chapters (6 pages, ~600-800 words each)
- **System Overview**: Runtime stack diagram, component roles, data flow
- **Boot Sequence**: GRUB → live-boot → systemd → GPU detect → services → TUI. Detailed timeline.
- **Service Dependencies**: systemd dependency graph (ASCII art or description)
- **Storage Architecture**: Partition layout, persistence mechanism, overlayfs, SquashFS
- **Network Architecture**: Caddy routing, port assignments, mDNS, firewall rules
- **Security Model**: Threat model, defense layers, authentication flow, service isolation

---

#### Build System chapters (7 pages, ~500-700 words each)
- **live-build Overview**: What live-build is, how it works, official docs link
- **Directory Structure**: Annotated tree of `auto/`, `config/`, `scripts/`
- **Build Hooks**: Each hook explained (01-setup-system, 02-setup-autologin, 03-install-extras, 04-install-python-apps, 05-generate-configs)
- **Package Lists**: neuraldrive.list.chroot, NVIDIA, ROCm, Intel packages
- **Archive Sources**: backports, ROCm, Intel repos
- **Docker Build**: Dockerfile, docker-compose.yml, privileged mode requirement
- **CI/CD Pipeline**: GitHub Actions workflow, build matrix, artifact publishing

---

#### Component chapters (8 pages, ~500-800 words each)
- Each component: purpose, configuration, code location, how to modify, integration points
- **GPU Auto-Detection**: gpu-detect.sh, PCI enumeration, modprobe, config output
- **Ollama Integration**: installation method, service config, environment variables, model storage
- **Open WebUI**: pip install, venv isolation, environment variables, feature toggles
- **Caddy**: Caddyfile routing, TLS config, environment-based auth, service unit
- **System Management API**: FastAPI app, endpoint list, auth, systemd integration
- **TUI**: Textual framework, screen architecture, code structure, refresh intervals
- **First-Boot Wizard**: wizard flow, sentinel files, credential generation, SUDOERS cleanup
- **Certificate Generation**: generate-certs.sh, SAN inclusion, persistence, regeneration

---

#### Testing chapters (6 pages, ~400-600 words each)
- Detailed guide for each test type, how to run, how to add new tests, CI integration

#### Release chapters (4 pages, ~400 words each)
- CalVer format, release process, GPG signing, image variants (full, nvidia, minimal)

---

## 4. mdbook Configuration

### User Guide `book.toml`

```toml
[book]
title = "NeuralDrive User Guide"
authors = ["NeuralDrive Contributors"]
description = "User documentation for the NeuralDrive LLM inference server"
language = "en"
src = "src"

[build]
build-dir = "../../build/docs/user-guide"

[output.html]
default-theme = "coal"
preferred-dark-theme = "coal"
git-repository-url = "https://github.com/<org>/NeuralDrive"
edit-url-template = "https://github.com/<org>/NeuralDrive/edit/main/docs/user-guide/src/{path}"
additional-css = ["custom.css"]

[output.html.search]
enable = true
```

### Developer Guide `book.toml`

```toml
[book]
title = "NeuralDrive Developer Guide"
authors = ["NeuralDrive Contributors"]
description = "Developer and contributor documentation for NeuralDrive"
language = "en"
src = "src"

[build]
build-dir = "../../build/docs/dev-guide"

[output.html]
default-theme = "coal"
preferred-dark-theme = "coal"
git-repository-url = "https://github.com/<org>/NeuralDrive"
edit-url-template = "https://github.com/<org>/NeuralDrive/edit/main/docs/dev-guide/src/{path}"

[output.html.search]
enable = true
```

### Custom CSS (`custom.css`)
Minimal custom styling for terminal aesthetic consistency with the NeuralDrive brand:
- Code blocks: dark background (#0A0A0A) with amber (#F59E0B) syntax highlights
- Admonition boxes for notes, warnings, tips
- Audience badges (`[Developer]`, `[Admin]`) styled as inline labels

---

## 5. Writing Order & Dependencies

Writing should follow this priority order. Dependencies are listed — a chapter should not be written before its dependencies.

### Phase 1: Core Path (write first — enables basic use)
| Priority | Chapter | Dependencies | Est. Words |
|----------|---------|-------------|------------|
| 1 | Introduction | None | 300 |
| 2 | What is NeuralDrive? | None | 800 |
| 3 | Hardware Requirements | None | 600 |
| 4 | Quick Start | Hardware Requirements | 500 |
| 5 | Writing the USB Drive | None | 800 |
| 6 | First Boot Setup | Writing the USB Drive | 1000 |
| 7 | Web Dashboard | First Boot Setup | 600 |
| 8 | Chat Interface | Web Dashboard | 500 |
| | **Phase 1 subtotal** | | **~5,100** |

### Phase 2: Integration (write second — enables developer workflows)
| Priority | Chapter | Dependencies | Est. Words |
|----------|---------|-------------|------------|
| 9 | API Overview | None | 600 |
| 10 | TLS Certificate Trust | API Overview | 700 |
| 11 | Connecting Coding Agents | API Overview, TLS Trust | 800 |
| 12 | Python SDK Examples | API Overview, TLS Trust | 600 |
| 13 | curl Examples | API Overview, TLS Trust | 400 |
| 14 | API Key Management | API Overview | 400 |
| 15 | Ollama Native API | API Overview | 400 |
| | **Phase 2 subtotal** | | **~3,900** |

### Phase 3: Deep Usage (write third — complete user experience)
| Priority | Chapter | Dependencies | Est. Words |
|----------|---------|-------------|------------|
| 16 | Understanding LLM Models | None | 800 |
| 17 | Downloading Models | Understanding Models | 500 |
| 18 | Model Recommendations | Understanding Models, Hardware Reqs | 600 |
| 19 | Storage Management | None | 500 |
| 20 | Terminal Interface (TUI) + sub-pages | None | 1700 |
| 21 | Model Management (Web) | Web Dashboard | 500 |
| 22 | RAG Documents | Web Dashboard | 400 |
| 23 | Local Chat | None | 300 |
| | **Phase 3 subtotal** | | **~5,300** |

### Phase 4: Administration (write fourth — admin workflows)
| Priority | Chapter | Dependencies | Est. Words |
|----------|---------|-------------|------------|
| 24 | Network Configuration | None | 500 |
| 25 | Security (overview + 3 sub-pages) | None | 1800 |
| 26 | GPU Monitoring | None | 400 |
| 27 | Service Management | None | 500 |
| 28 | Updating NeuralDrive | Writing the USB Drive | 600 |
| 29 | System Management API | API Overview | 500 |
| | **Phase 4 subtotal** | | **~4,300** |

### Phase 5: Advanced & Reference (write fifth)
| Priority | Chapter | Dependencies | Est. Words |
|----------|---------|-------------|------------|
| 30 | Building Custom Images | None | 1000 |
| 31 | Build Configuration Reference | Custom Images | 800 |
| 32 | Custom Hooks & Overlays | Custom Images | 600 |
| 33 | CD Mode vs USB Mode | None | 500 |
| 34 | External Storage | None | 400 |
| 35 | LUKS Encryption | First Boot Setup | 500 |
| 36 | Performance Tuning | None | 600 |
| 37 | llama.cpp Server | None | 400 |
| | **Phase 5 subtotal** | | **~4,800** |

### Phase 6: Troubleshooting & Reference (write last)
| Priority | Chapter | Dependencies | Est. Words |
|----------|---------|-------------|------------|
| 38 | Common Issues | All usage chapters | 800 |
| 39 | GPU Problems | GPU Monitoring | 600 |
| 40 | Boot Failures | First Boot Setup | 400 |
| 41 | Network & mDNS | Network Config | 400 |
| 42 | Model Loading Issues | Understanding Models | 400 |
| 43 | FAQ | All chapters | 800 |
| 44-51 | Reference pages (8 pages) | All chapters | 4000 |
| 52 | Glossary | All chapters | 500 |
| | **Phase 6 subtotal** | | **~7,900** |

### Phase 7: Developer Guide (can be written in parallel with Phase 3+)
| Priority | Chapter Group | Est. Words |
|----------|--------------|------------|
| A | Getting Started (3 chapters) | 1800 |
| B | Contributing (4 chapters) | 1600 |
| C | Architecture (6 chapters) | 4200 |
| D | Build System (7 chapters) | 4200 |
| E | Components (8 chapters) | 5200 |
| F | Testing (6 chapters) | 3000 |
| G | Release (4 chapters) | 1600 |
| | **Dev Guide subtotal** | **~21,600** |

### Totals

| Book | Chapters | Est. Words |
|------|----------|------------|
| User Guide | ~52 pages | ~31,300 |
| Developer Guide | ~38 pages | ~21,600 |
| **Total** | **~90 pages** | **~52,900** |

---

## 6. Cross-Reference Strategy

- **Within books**: Standard mdbook relative links `[text](../path/to/page.md)`
- **Between books**: Relative URL links `[Developer Guide](../../dev-guide/src/architecture/overview.md)` or absolute URLs once deployed
- **To external resources**:
  - Ollama documentation: https://github.com/ollama/ollama
  - Open WebUI docs: https://docs.openwebui.com/
  - live-build manual: https://live-team.pages.debian.net/live-manual/
  - Debian wiki: https://wiki.debian.org/
- **Admonition conventions** (using mdbook-admonish or HTML):
  - `> **Note**:` — general information
  - `> **Warning**:` — destructive or security-sensitive actions
  - `> **Tip**:` — optional improvements
  - `> **Developer**:` — content primarily for developer audience
  - `> **Admin**:` — content primarily for admin audience

---

## 7. File Structure on Disk

```
NeuralDrive/
├── docs/
│   ├── user-guide/
│   │   ├── book.toml
│   │   ├── custom.css
│   │   └── src/
│   │       ├── SUMMARY.md
│   │       ├── introduction.md
│   │       ├── getting-started/
│   │       │   ├── what-is-neuraldrive.md
│   │       │   ├── hardware-requirements.md
│   │       │   ├── quick-start.md
│   │       │   ├── writing-usb.md
│   │       │   └── first-boot.md
│   │       ├── using/
│   │       │   ├── web-dashboard.md
│   │       │   ├── chat.md
│   │       │   ├── models-web.md
│   │       │   ├── rag.md
│   │       │   ├── tui.md
│   │       │   ├── tui-dashboard.md
│   │       │   ├── models-tui.md
│   │       │   ├── tui-services.md
│   │       │   ├── tui-logs.md
│   │       │   └── local-chat.md
│   │       ├── models/
│   │       │   ├── understanding-models.md
│   │       │   ├── downloading.md
│   │       │   ├── recommendations.md
│   │       │   ├── storage.md
│   │       │   └── preloading.md
│   │       ├── api/
│   │       │   ├── overview.md
│   │       │   ├── coding-agents.md
│   │       │   ├── python-sdk.md
│   │       │   ├── curl-examples.md
│   │       │   ├── tls-trust.md
│   │       │   ├── api-keys.md
│   │       │   └── ollama-native.md
│   │       ├── admin/
│   │       │   ├── network.md
│   │       │   ├── security.md
│   │       │   ├── firewall.md
│   │       │   ├── tls-certs.md
│   │       │   ├── ssh.md
│   │       │   ├── gpu-monitoring.md
│   │       │   ├── services.md
│   │       │   ├── updating.md
│   │       │   └── system-api.md
│   │       ├── advanced/
│   │       │   ├── custom-images.md
│   │       │   ├── build-config-reference.md
│   │       │   ├── hooks-overlays.md
│   │       │   ├── cd-vs-usb.md
│   │       │   ├── external-storage.md
│   │       │   ├── encryption.md
│   │       │   ├── performance.md
│   │       │   └── llama-cpp.md
│   │       ├── troubleshooting/
│   │       │   ├── common-issues.md
│   │       │   ├── gpu.md
│   │       │   ├── boot.md
│   │       │   ├── network.md
│   │       │   ├── models.md
│   │       │   └── faq.md
│   │       └── reference/
│   │           ├── hardware-matrix.md
│   │           ├── config-files.md
│   │           ├── boot-parameters.md
│   │           ├── services.md
│   │           ├── api-endpoints.md
│   │           ├── system-api-endpoints.md
│   │           ├── ports.md
│   │           └── glossary.md
│   └── dev-guide/
│       ├── book.toml
│       └── src/
│           ├── SUMMARY.md
│           ├── introduction.md
│           ├── getting-started/
│           │   ├── dev-environment.md
│           │   ├── building.md
│           │   └── testing.md
│           ├── contributing/
│           │   ├── how-to-contribute.md
│           │   ├── code-style.md
│           │   ├── pr-process.md
│           │   └── issues.md
│           ├── architecture/
│           │   ├── overview.md
│           │   ├── boot-sequence.md
│           │   ├── service-dependencies.md
│           │   ├── storage.md
│           │   ├── network.md
│           │   └── security.md
│           ├── build/
│           │   ├── live-build.md
│           │   ├── directory-structure.md
│           │   ├── hooks.md
│           │   ├── package-lists.md
│           │   ├── archive-sources.md
│           │   ├── docker.md
│           │   └── cicd.md
│           ├── components/
│           │   ├── gpu-detection.md
│           │   ├── ollama.md
│           │   ├── open-webui.md
│           │   ├── caddy.md
│           │   ├── system-api.md
│           │   ├── tui.md
│           │   ├── first-boot-wizard.md
│           │   └── certificates.md
│           ├── testing/
│           │   ├── strategy.md
│           │   ├── qemu.md
│           │   ├── gpu-testing.md
│           │   ├── api-tests.md
│           │   ├── hardware.md
│           │   └── benchmarks.md
│           └── release/
│               ├── versioning.md
│               ├── checklist.md
│               ├── signing.md
│               └── variants.md
```

---

## 8. Build & Serve Commands

```bash
# Build both books
cd docs/user-guide && mdbook build && cd ../dev-guide && mdbook build

# Serve locally for review (user guide)
cd docs/user-guide && mdbook serve --open

# Serve locally for review (dev guide)
cd docs/dev-guide && mdbook serve --open --port 3001
```

Output goes to `build/docs/user-guide/` and `build/docs/dev-guide/`.

A top-level `docs/build-docs.sh` script should build both books and optionally deploy to GitHub Pages.

---

## 9. Open Questions for Implementation

1. **GitHub org/repo URL**: Needed for `book.toml` `git-repository-url` and edit links.
2. **Hosting**: GitHub Pages (simplest), or custom domain?
3. **Screenshots/diagrams**: Should the docs include actual screenshots (deferred until TUI/web are implemented), or are ASCII mockups from the plan files sufficient initially?
4. **mdbook plugins**: Consider `mdbook-admonish` for styled callout boxes (Note, Warning, Tip). Also `mdbook-linkcheck` for CI validation of internal links.
5. **Versioned docs**: Should docs be versioned per release (e.g., v2026.04), or single "latest" version?

---

## Appendix A: GitHub Pages Deployment for Two mdbook Books

### Feasibility

Fully supported. GitHub Pages serves a single directory tree as static files. Two mdbook books are just two sets of HTML output in subdirectories. Real production example: [FuelLabs/sway](https://github.com/FuelLabs/sway) deploys 3 separate mdbook books from one repo (Sway Book, Sway Reference, Standard Library) using this exact pattern.

### URL Structure

```
https://<user>.github.io/NeuralDrive/              → Landing page (links to both books)
https://<user>.github.io/NeuralDrive/user-guide/    → User Guide
https://<user>.github.io/NeuralDrive/dev-guide/     → Developer Guide
```

### Critical: `site-url` Configuration

Each book's `book.toml` **must** set `site-url` to include the repo name AND book subdirectory. Without this, the 404 page and some internal links break when served from a subdirectory.

```toml
# docs/user-guide/book.toml
[output.html]
site-url = "/NeuralDrive/user-guide/"

# docs/dev-guide/book.toml
[output.html]
site-url = "/NeuralDrive/dev-guide/"
```

### GitHub Actions Workflow

Uses `peaceiris/actions-gh-pages` with `destination_dir` to deploy each book to its own subdirectory on the `gh-pages` branch:

```yaml
name: Deploy Documentation
on:
  push:
    branches: [main]
    paths: ['docs/**']

permissions:
  contents: write

jobs:
  deploy-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup mdBook
        uses: peaceiris/actions-mdbook@v2
        with:
          mdbook-version: '0.4.45'

      - name: Build User Guide
        run: mdbook build docs/user-guide

      - name: Build Developer Guide
        run: mdbook build docs/dev-guide

      # Deploy landing page to root
      - name: Deploy landing page
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs/landing
          destination_dir: .
          keep_files: true

      # Deploy User Guide to /user-guide/
      - name: Deploy User Guide
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs/user-guide/book
          destination_dir: user-guide
          keep_files: true

      # Deploy Developer Guide to /dev-guide/
      - name: Deploy Developer Guide
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs/dev-guide/book
          destination_dir: dev-guide
          keep_files: true
```

**Notes:**
- `keep_files: true` is important — without it, each deploy step would wipe files from previous steps on the `gh-pages` branch.
- `destination_dir: .` for the landing page deploys to the root without clobbering book subdirectories.
- `paths: ['docs/**']` limits workflow triggers to documentation changes only.

### Landing Page

A simple `docs/landing/index.html` at the root provides navigation to both books:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>NeuralDrive Documentation</title>
  <style>
    body { font-family: system-ui, sans-serif; background: #0a0a0a; color: #fff;
           display: flex; flex-direction: column; align-items: center; justify-content: center;
           min-height: 100vh; margin: 0; }
    h1 { color: #f59e0b; }
    a { color: #10b981; text-decoration: none; font-size: 1.3rem; margin: 0.5rem 0; }
    a:hover { text-decoration: underline; }
    .links { display: flex; flex-direction: column; align-items: center; gap: 1rem; margin-top: 2rem; }
  </style>
</head>
<body>
  <h1>NeuralDrive Documentation</h1>
  <p>Boot-to-inference LLM server on a USB stick.</p>
  <div class="links">
    <a href="user-guide/">User Guide &rarr;</a>
    <a href="dev-guide/">Developer Guide &rarr;</a>
  </div>
</body>
</html>
```

### Cross-Linking Between Books

Since both books are under the same domain, cross-linking uses relative URLs:

```markdown
<!-- From within user-guide, link to dev-guide -->
For build system details, see the [Developer Guide](../../dev-guide/build/hooks.html).

<!-- From within dev-guide, link to user-guide -->
For end-user instructions, see the [User Guide](../../user-guide/getting-started/quick-start.html).
```

Note: cross-book links use `.html` extensions (mdbook's output format), not `.md`.

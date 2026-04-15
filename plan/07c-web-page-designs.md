# 07c: Web Page Designs

This document provides ASCII wireframes and functional specifications for every page in the NeuralDrive web interface. It serves as a companion to 07a (Design System) and 07b (Site Architecture). The wireframes reflect the design system's dark/amber/green terminal aesthetic, ensuring consistency between the TUI and the web dashboard.

## OPEN WEBUI PAGES (Configuration Notes)

These pages are part of the standard Open WebUI installation. NeuralDrive configures Open WebUI via environment variables (`WEBUI_NAME`, `STATIC_DIR`, feature toggles) but cannot inject custom CSS or replace branding in the community version (see 07a §7). Open WebUI's built-in dark mode provides a reasonable visual match to the System Panel.

### Section 1: Login Page
The entry point for the NeuralDrive chat interface.

**ASCII Wireframe**
```text
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                      [ NEURALDRIVE ]                        │
│                     The Neural Engine                       │
│                                                             │
│                 ┌─────────────────────────┐                 │
│                 │ Username                │                 │
│                 ├─────────────────────────┤                 │
│                 │ Password                │                 │
│                 └─────────────────────────┘                 │
│                                                             │
│                      [  LOG IN  ]                           │
│                                                             │
│                                                             │
│  Host: neuraldrive.local             IP: 192.168.1.50       │
└─────────────────────────────────────────────────────────────┘
```
- **Customization**: App title displays "NeuralDrive" (via `WEBUI_NAME` env var), custom favicon (via `STATIC_DIR`), built-in dark mode enabled. Open WebUI logo and branding remain visible per community license.
- **Data Source**: Open WebUI Auth API.
- **Key Actions**: Login with credentials set during first-boot wizard.
- **Update Behavior**: Static until form submission.

### Section 2: Chat Interface
The primary interface for interacting with LLMs.

**ASCII Wireframe**
```text
┌─────────┬───────────────────────────────────────────────────┐
│ SIDEBAR │  Llama 3.1 8B                                 [X] │
│         ├───────────────────────────────────────────────────┤
│ New Chat│                                                   │
│         │  User: How do I check GPU usage?                  │
│ History │  ND:   You can check the System Panel or run      │
│ - Topic1│        `nvidia-smi` in the terminal.              │
│ - Topic2│                                                   │
│         │                                                   │
│         ├───────────────────────────────────────────────────┤
│ Settings│  [ Type your message...                     ] [>] │
└─────────┴───────────────────────────────────────────────────┘
```
- **Customization**: Built-in dark mode active. Open WebUI's native styling applies. Unused features (voice, image gen, community) disabled via config to simplify the interface.
- **Data Source**: Open WebUI Chat API / Ollama API.
- **Key Actions**: Message input, model selection, chat history management.
- **Update Behavior**: Real-time message streaming via WebSockets.

### Section 3: Model Library
Browser for downloading and managing models.

- **Customization**: Standard Open WebUI model library with dark mode. No custom styling possible without Enterprise license or fork.
- **Data Source**: Ollama API (`/api/tags`).
- **Key Actions**: Pull new models, delete existing models, view model details.
- **Update Behavior**: Polling every 10 seconds for download progress.

---

## NEURALDRIVE SYSTEM PANEL PAGES

These pages are custom-built for NeuralDrive using the System API and the design system.

### Section 4: System Dashboard
The landing page of the System Panel, providing a high-level overview.

**ASCII Wireframe**
```text
┌─────────┬───────────────────────────────────────────────────┐
│ SIDEBAR │  neuraldrive.local │ 192.168.1.50 │ Up: 4h 12m    │
│         ├───────────────────────────────────────────────────┤
│ ◆ Dash  │ ┌─ GPU ──────────────┐ ┌─ System ────────────────┐ │
│   GPU   │ │ RTX 4090           │ │ CPU:  ██░░░░░░ 22%      │ │
│   Svc   │ │ VRAM: ████████░ 78%│ │ RAM:  ██████░░ 72%      │ │
│   Disk  │ │ Temp: 68°C  Fan: 45│ │ Disk: █████░░░ 62%      │ │
│   Net   │ │ Util: ████████ 91% │ └─────────────────────────┘ │
│   Logs  │ └────────────────────┘                             │
│   Keys  │ ┌─ Services ─────────────────────────────────────┐ │
│         │ │ ● neuraldrive-ollama    Running                │ │
│ ─────── │ │ ● neuraldrive-webui     Running                │ │
│ Chat →  │ │ ● neuraldrive-caddy     Running                │ │
│         │ └────────────────────────────────────────────────┘ │
│         │                                                    │
│         │ [ OPEN CHAT ]  [ PULL MODEL ]  [ VIEW LOGS ]       │
└─────────┴────────────────────────────────────────────────────┘
```
- **Data Source**: `GET /system/status`, GPU Hot API.
- **Key Actions**: Quick access to chat, model pull, and log viewing.
- **Refresh**: Metrics update every 5 seconds; services update every 30 seconds.

### Section 5: GPU Monitoring
Detailed real-time monitoring for installed GPUs.

**ASCII Wireframe**
```text
┌─────────┬───────────────────────────────────────────────────┐
│ SIDEBAR │  GPU MONITORING                                   │
│         ├───────────────────────────────────────────────────┤
│   Dash  │ ┌─ RTX 4090 (ID: 0) ────────────────────────────┐ │
│ ◆ GPU   │ │ Driver: 550.54.14     Power: 240W / 450W      │ │
│   Svc   │ │                                               │ │
│   Disk  │ │ Utilization %:  ▂▃▅▆▇█▇▅▃ (91%)               │ │
│   Net   │ │ VRAM Usage:     ████████░ (18.4 / 24.0 GB)    │ │
│   Logs  │ │ Temperature:    68°C                          │ │
│   Keys  │ └───────────────────────────────────────────────┘ │
│         │ ┌─ Active Models ───────────────────────────────┐ │
│         │ │ Llama-3.1-8B-Q4_K_M       4.7 GB  [VRAM]      │ │
│         │ │ Mistral-7B-v0.3           4.1 GB  [VRAM]      │ │
│         │ └───────────────────────────────────────────────┘ │
└─────────┴───────────────────────────────────────────────────┘
```
- **Data Source**: GPU Hot API (`:1312`), `GET /system/status`.
- **Key Actions**: View detailed telemetry, check VRAM allocation.
- **Refresh**: Every 2 seconds for smooth charts and utilization updates.

### Section 6: Service Management
Control panel for systemd services.

**ASCII Wireframe**
```text
┌─────────┬───────────────────────────────────────────────────┐
│ SIDEBAR │  SERVICE MANAGEMENT                               │
│         ├───────────────────────────────────────────────────┤
│   Dash  │ SERVICE NAME         STATUS      UPTIME    ACTION │
│   GPU   │ ──────────────────────────────────────────────────┤
│ ◆ Svc   │ ollama               ● RUNNING   4h 12m    [RESRT]│
│   Disk  │ webui                ● RUNNING   4h 10m    [RESRT]│
│   Net   │ caddy                ● RUNNING   4h 12m    [RESRT]│
│   Logs  │ gpu-monitor          ● RUNNING   4h 12m    [RESRT]│
│   Keys  │ system-api           ● RUNNING   4h 12m    [RESRT]│
│         │ ──────────────────────────────────────────────────┤
│         │ [ RESTART ALL ]                                   │
└─────────┴───────────────────────────────────────────────────┘
```
- **Data Source**: `GET /system/services`, `POST /system/services/{name}/restart`.
- **Key Actions**: Restart, stop, or start services. Confirmation modal on stop/restart.
- **Refresh**: Every 10 seconds.

### Section 7: Storage Management
Disk usage and persistence settings.

**ASCII Wireframe**
```text
┌─────────┬───────────────────────────────────────────────────┐
│ SIDEBAR │  STORAGE & MODELS                                 │
│         ├───────────────────────────────────────────────────┤
│   Dash  │ ┌─ Partition Layout ────────────────────────────┐ │
│   GPU   │ │ / (Root)     ████████░░ 82% (112GB/128GB)     │ │
│   Svc   │ │ /data (Pers) ████░░░░░░ 40% (400GB/1TB)       │ │
│ ◆ Disk  │ └───────────────────────────────────────────────┘ │
│   Net   │ ┌─ Model Storage ───────────────────────────────┐ │
│   Logs  │ │ llama3.1:8b       4.7 GB     [ DELETE ]       │ │
│   Keys  │ │ codestral:latest  8.2 GB     [ DELETE ]       │ │
│         │ └───────────────────────────────────────────────┘ │
│         │ Persistence: ENABLED (SDA3)                       │
└─────────┴───────────────────────────────────────────────────┘
```
- **Data Source**: `GET /system/storage`, Ollama API (`/api/tags`).
- **Key Actions**: Delete models, mount/unmount external drives.
- **Refresh**: Every 30 seconds.

### Section 8: Network & Security
Configuration for connectivity and system protection.

**ASCII Wireframe**
```text
┌─────────┬───────────────────────────────────────────────────┐
│ SIDEBAR │  NETWORK & SECURITY                               │
│         ├───────────────────────────────────────────────────┤
│   Dash  │ ┌─ Interface: eth0 ─────────────────────────────┐ │
│   GPU   │ │ IP: 192.168.1.50      Gateway: 192.168.1.1    │ │
│   Svc   │ │ DNS: 8.8.8.8          mDNS: neuraldrive.local │ │
│   Disk  │ └───────────────────────────────────────────────┘ │
│ ◆ Net   │ ┌─ Security ────────────────────────────────────┐ │
│   Logs  │ │ SSH Access: [ ENABLED ]  (Port 22)            │ │
│   Keys  │ │ Firewall:   [ ACTIVE  ]  (Ports 80, 443, 8443)│ │
│         │ │ SSL Cert:   Expires in 82 days                │ │
│         │ └───────────────────────────────────────────────┘ │
└─────────┴───────────────────────────────────────────────────┘
```
- **Data Source**: `GET /system/network`, `GET /system/security`.
- **Key Actions**: Toggle SSH, regenerate TLS certificates.
- **Refresh**: Static on load, manual refresh required for changes.

### Section 9: Log Viewer
System-wide log browser with filtering.

**ASCII Wireframe**
```text
┌─────────┬───────────────────────────────────────────────────┐
│ SIDEBAR │  SYSTEM LOGS                                      │
│         ├───────────────────────────────────────────────────┤
│   Dash  │ Service: [ ollama ] Level: [ Info ] [ Search... ] │
│   GPU   │ ──────────────────────────────────────────────────┤
│   Svc   │ 12:00:01 [INFO] Initializing Ollama runner...     │
│   Disk  │ 12:00:05 [INFO] Loaded model llama3.1:8b          │
│   Net   │ 12:01:12 [WARN] High VRAM usage detected (92%)    │
│ ◆ Logs  │ 12:02:45 [INFO] Request completed in 450ms        │
│   Keys  │                                                   │
│         │ ──────────────────────────────────────────────────┤
│         │ [ ] Auto-tail    [ DOWNLOAD LOGS ]    [ CLEAR ]   │
└─────────┴───────────────────────────────────────────────────┘
```
- **Data Source**: `GET /system/logs?service=X&level=Y&search=Z`.
- **Key Actions**: Filter by service/level, search text, toggle auto-tail.
- **Refresh**: Real-time streaming if auto-tail is enabled; otherwise static.

### Section 10: API Key Management
Manage access tokens for external integrations.

**ASCII Wireframe**
```text
┌─────────┬───────────────────────────────────────────────────┐
│ SIDEBAR │  API KEY MANAGEMENT                               │
│         ├───────────────────────────────────────────────────┤
│   Dash  │ Your System API Key:                              │
│   GPU   │ ┌───────────────────────────────────────────────┐ │
│   Svc   │ │ nd_live_********************************3f2  │ │
│   Disk  │ └───────────────────────────────────────────────┘ │
│   Net   │ [ REVEAL ]  [ COPY ]  [ REGENERATE ]              │
│   Logs  │                                                   │
│ ◆ Keys  │ Usage:                                            │
│         │ curl -H "Authorization: Bearer <key>" \           │
│         │      https://neuraldrive.local/system/status      │
└─────────┴───────────────────────────────────────────────────┘
```
- **Data Source**: `GET /system/api-keys`, `POST /system/api-keys/rotate`.
- **Key Actions**: Reveal key, copy to clipboard, regenerate key with confirmation.
- **Refresh**: Static.

### Section 11: About / System Info
Version information and hardware summary.

**ASCII Wireframe**
```text
┌─────────┬───────────────────────────────────────────────────┐
│ SIDEBAR │  ABOUT NEURALDRIVE                                │
│         ├───────────────────────────────────────────────────┤
│         │ NeuralDrive Version: v1.0.0-stable                │
│         │ Build Date: 2026-04-15                            │
│         │                                                   │
│         │ Component Versions:                               │
│         │ - Ollama: 0.1.45                                  │
│         │ - Open WebUI: 0.3.10                              │
│         │                                                   │
│         │ Hardware Summary:                                 │
│         │ - CPU: AMD Ryzen 9 7950X (32 Threads)             │
│         │ - RAM: 64 GB DDR5                                 │
│         │ - GPU: NVIDIA RTX 4090 (24 GB)                    │
│         │                                                   │
│         │ [ DOCUMENTATION ]  [ GITHUB ]  [ REPORT ISSUE ]   │
└─────────┴───────────────────────────────────────────────────┘
```
- **Data Source**: `GET /system/status`.
- **Key Actions**: View version history, access external links.
- **Refresh**: Static.

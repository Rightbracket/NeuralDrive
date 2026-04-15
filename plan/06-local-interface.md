# 06-local-interface.md — Terminal User Interface (TUI)

This document defines the architecture and implementation of the NeuralDrive TUI, the primary console-based interface for management and monitoring.

## Section 1: TUI Architecture
- **Framework**: Python 3.11 + [Textual](https://textual.textualize.io/).
- **Application**: `neuraldrive-tui`
- **Location**: `/usr/local/bin/neuraldrive-tui` (system-wide script pointing to `/usr/lib/neuraldrive/tui/main.py`)
- **Isolation**: Runs in a dedicated Python virtualenv at `/usr/lib/neuraldrive/tui/venv/`.
- **System Service**: `neuraldrive-tui.service`
```ini
[Unit]
Description=NeuralDrive Console TUI
After=network-online.target neuraldrive-ollama.service

[Service]
ExecStart=/usr/local/bin/neuraldrive-tui
StandardInput=tty
StandardOutput=tty
TTYPath=/dev/tty1
Restart=always
User=neuraldrive-admin

[Install]
WantedBy=multi-user.target
```

## Section 2: Screen Layout & Mockups

### Main Dashboard
```text
┌──────────────── NeuralDrive v1.0.0 ──────────────────────────┐
│ Host: neuraldrive.local    │ Uptime: 2h 15m │ IP: 192.168.1.50 │
├──────────────────────────────────────────────────────────────┤
│ GPU: NVIDIA RTX 4090  │ VRAM: 12.4/24.0 GB │ Temp: 65°C │ 85% │
│ CPU: 12%              │ RAM: 18.2/64.0 GB  │ Disk: 45.2 GB    │
├──────────────────────────────────────────────────────────────┤
│ LOADED MODELS                                                │
│ ● llama3.1:8b        [GPU] 4.7 GB   85 req/min  ▂▃▅▆▇█▇▅▃    │
│ ● codestral:latest   [GPU] 8.2 GB   12 req/min  ▁▁▂▁▁▁▂▁▁    │
│ ○ phi3:mini           ---  (not loaded)                     │
├──────────────────────────────────────────────────────────────┤
│ [M]odels  [S]ervices  [N]etwork  [L]ogs  [C]hat  [Q]uit      │
└──────────────────────────────────────────────────────────────┘
```

### Models Screen (M)
```text
┌──────────────── Model Management ────────────────────────────┐
│ NAME                SIZE    STATUS      ACTION               │
│ llama3.1:8b        4.7GB   LOADED      [U]nload  [D]elete   │
│ codestral:latest   8.2GB   LOADED      [U]nload  [D]elete   │
│ mistral:7b         4.1GB   CACHED      [L]oad    [D]elete   │
├──────────────────────────────────────────────────────────────┤
│ [P]ull Model  [I]mport GGUF  [B]ack                          │
└──────────────────────────────────────────────────────────────┘
```

### Logs Screen (L)
```text
┌──────────────── System Logs ─────────────────────────────────┐
│ Service: [All Services] │ Level: [Info+] │ Search: [        ]│
├──────────────────────────────────────────────────────────────┤
│ 10:15:30 [OLLAMA] Loaded llama3.1:8b successfully            │
│ 10:15:35 [WEBUI] Admin user logged in from 192.168.1.5       │
│ 10:16:12 [OLLAMA] Error: Connection closed by remote peer    │
├──────────────────────────────────────────────────────────────┤
│ [S]elect Service  [F]ilter  [C]lear  [B]ack                  │
└──────────────────────────────────────────────────────────────┘
```

## Section 3: Navigation & Interaction
- `M`: Navigate to Models Screen.
- `S`: Navigate to Services Screen (Start/Stop/Restart services).
- `N`: Network Settings (IP, Hostname, mDNS status).
- `L`: View Journald logs for all `neuraldrive-*` units.
- `C`: Open local chat tester.
- `Q`: Quit TUI to the shell.

## Section 4: Data Sources & Integration
- **GPU Metrics**: Parsed from `nvidia-smi --query-gpu=... --format=csv,noheader,nounits` (or AMD/Intel equivalents via `/sys/class/drm`).
- **Models**: Queried from `Ollama API` at `localhost:11434/api/tags` and `/api/ps`.
- **System Stats**: Using the `psutil` library.
- **Service Status**: Via `systemd-python` or `subprocess.check_output(['systemctl', 'is-active', service])`.

## Section 5: Python Code Structure
The TUI is organized as a package in `/usr/lib/neuraldrive/tui/`.

```text
tui/
├── main.py              # Entry point & App class
├── screens/
│   ├── dashboard.py     # Main layout & stats widgets
│   ├── models.py        # Model list & pull logic
│   ├── services.py      # Service control management
│   └── logs.py          # Log streaming (tailing journald)
├── widgets/
│   ├── stats_box.py     # Reusable GPU/CPU indicator
│   └── model_item.py    # List item for models
└── utils/
    ├── api_client.py    # Async wrapper for Ollama/WebUI
    └── hardware.py      # Hardware metrics collectors
```

### Core App Class (`main.py`)
```python
from textual.app import App
from .screens.dashboard import DashboardScreen

class NeuralDriveTUI(App):
    CSS_PATH = "styles.tcss"
    BINDINGS = [
        ("m", "push_screen('models')", "Models"),
        ("s", "push_screen('services')", "Services"),
        ("n", "push_screen('network')", "Network"),
        ("l", "push_screen('logs')", "Logs"),
        ("c", "push_screen('chat')", "Chat"),
        ("q", "quit", "Quit"),
    ]

    def on_mount(self):
        self.push_screen(DashboardScreen())

if __name__ == "__main__":
    app = NeuralDriveTUI()
    app.run()
```

## Section 6: First-Boot Wizard
If `/etc/neuraldrive/first-boot-complete` does not exist, the TUI launches in "Wizard Mode".

### Wizard Steps:
1. **Welcome**: Hardware summary and health check.
2. **Security**: Prompt for admin password and generate API keys.
3. **Network**: Configure DHCP or Static IP.
4. **Storage**: Select persistence drive and optional LUKS encryption.
5. **Models**: Recommended starter model selector.
6. **Finish**: Writes configurations and touches the `first-boot-complete` file.

## Section 7: Implementation Requirements
- **Venv setup**: `python3 -m venv /usr/lib/neuraldrive/tui/venv/ && ./venv/bin/pip install textual psutil httpx rich`.
- **Refresh**: Dashboard updates every 2s for GPU/CPU, 10s for model list.
- **Resilience**: If `ollama.service` is down, show a red "Ollama Offline" badge instead of crashing.
- **Keyboard-only**: Every action must have a dedicated key or be reachable via Tab/Enter.

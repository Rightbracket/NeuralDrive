*This chapter is for everyone.*

# Terminal Interface (TUI)

The NeuralDrive Terminal User Interface (TUI) provides a keyboard-driven dashboard for system monitoring and management. Built using Python 3.11 and the Textual framework, it offers a responsive and high-performance way to interact with your system directly from the console.

## When to Use the TUI

While the web interface is excellent for daily chat and document management, the TUI is better suited for:

- **Initial Configuration:** Checking network status and IP addresses.
- **System Monitoring:** Real-time tracking of CPU, GPU, and VRAM usage.
- **Troubleshooting:** Reviewing system logs and restarting services if they become unresponsive.
- **Offline Use:** Managing models and chatting without needing a second device to access the web UI.

## Accessing the TUI

By default, the TUI auto-launches on **tty1** for the `neuraldrive-admin` user. If you are at the physical console of the NeuralDrive machine, it should be the first thing you see after boot.

To run it manually from any shell session, use the command:
```bash
neuraldrive-tui
```

This command is a symlink from `/usr/local/bin/neuraldrive-tui` to the actual source at `/usr/lib/neuraldrive/tui/main.py`.

## Main Dashboard Layout

The main dashboard provides a high-level overview of system health and active models.

```text
┌──────────────── NeuralDrive v1.0.0 ──────────────────────────┐
│ Host: neuraldrive.local    │ Uptime: 2h 15m │ IP: 192.168.1.50 │
├──────────────────────────────────────────────────────────────┤
│ GPU: NVIDIA RTX 4090  │ VRAM: 12.4/24.0 GB │ Temp: 65°C │ 85% │
│ CPU: 12%              │ RAM: 18.2/64.0 GB  │ Disk: 45.2 GB    │
├──────────────────────────────────────────────────────────────┤
│ LOADED MODELS                                                │
│ ● llama3.1:8b        [GPU] 4.7 GB   85 req/min              │
│ ● codestral:latest   [GPU] 8.2 GB   12 req/min              │
│ ○ phi3:mini           ---  (not loaded)                      │
├──────────────────────────────────────────────────────────────┤
│ [M]odels  [S]ervices  [N]etwork  [L]ogs  [C]hat  [Q]uit     │
└──────────────────────────────────────────────────────────────┘
```

## Navigation Keybindings

Navigation is performed using single-letter hotkeys shown at the bottom of the screen:

- **M:** Models screen for managing downloads and loading state.
- **S:** Services screen for restarting or stopping system components.
- **N:** Network screen for hostname and IP configuration.
- **L:** Logs screen for real-time system and service logs.
- **C:** Chat screen for a lightweight, terminal-based LLM chat.
- **Q:** Quit the TUI and return to the shell.

## Resilience

The TUI is designed to be resilient. If the underlying Ollama service is unavailable, an "Ollama Offline" badge will appear on the dashboard, and certain model management features will be disabled until the service is restored via the **Services** screen.


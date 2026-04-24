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

This launcher script (installed at `/usr/local/bin/neuraldrive-tui`) activates the Python virtual environment and runs the application from `/usr/lib/neuraldrive/tui/main.py`.

## Main Dashboard Layout

The main dashboard provides a high-level overview of system health and active models.

```text
┌──────────────── NeuralDrive v1.0.0 ───────────────── 10:45:22 ─┐
│ Host: neuraldrive.local    │ Uptime: 2h 15m │ IP: 192.168.1.50 │
├────────────────────────────────────────────────────────────────┤
│ GPU: NVIDIA RTX 4090  │ VRAM: 12.4/24.0 GB │ Temp: 65°C │ 85%  │
│ CPU: 12%              │ RAM: 18.2/64.0 GB  │ Disk: 45.2 GB     │
├────────────────────────────────────────────────────────────────┤
│ LOADED MODELS                                                  │
│ ● llama3.1:8b        [GPU] 4.7 GB                              │
│ ● codestral:latest   [GPU] 8.2 GB                              │
│ ○ phi3:mini           ---  (not loaded)                        │
├────────────────────────────────────────────────────────────────┤
│ F1 Dashboard  F2 Models  F3 Services  F4 Logs  F5 Chat  Q Quit │
└────────────────────────────────────────────────────────────────┘
```

## Navigation Keybindings

Navigation is performed using function keys:

- **F1:** Dashboard overview.
- **F2:** Models screen for managing downloads and loading state.
- **F3:** Services screen for restarting or stopping system components.
- **F4:** Logs screen for real-time system and service logs.
- **F5:** Chat screen for a lightweight, terminal-based LLM chat.
- **Q:** Quit the TUI and return to the shell.

Within each screen, the following navigation model is used:
- **Tab / Shift+Tab:** Cycle focus between different screen zones.
- **Arrow Keys:** Navigate within a focused zone (e.g., scrolling a list).
- **Enter:** Activate the currently focused element or button.

## Troubleshooting and Debugging

If the TUI encounters a critical error, it will write a crash dump to `/var/lib/neuraldrive/logs/tui-crash-*.log`.

Screenshots captured within the TUI are saved to `/var/lib/neuraldrive/screenshots/`.

### Re-running the First-Boot Wizard

If you need to force the first-boot wizard to run again, launch the TUI with the `--wizard` flag:
```bash
neuraldrive-tui --wizard
```
This removes the sentinel file and initiates the guided setup process.

## Resilience

The TUI is designed to be resilient. If the underlying Ollama service is unavailable, an "Ollama Offline" badge will appear on the dashboard, and certain model management features will be disabled until the service is restored via the **Services** screen.


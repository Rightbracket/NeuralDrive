*This chapter is for contributors and maintainers.*

# Terminal User Interface (TUI)

The NeuralDrive TUI provides a local management console for administrators. It is designed to be usable directly from a physical keyboard and monitor without requiring a network connection.

## Technology Stack

The TUI is built using the **Textual** framework, a modern Python library for building sophisticated terminal applications. It uses async I/O to maintain a responsive interface even while performing long-running system tasks.

## Interface Structure

The TUI is divided into several screens:

### Dashboard
The default screen showing:
- System hostname and version.
- Current IP addresses (IPv4 and IPv6).
- mDNS address (`neuraldrive.local`).
- CPU, Memory, and Disk usage gauges.
- GPU status overview.
Manual refresh is available via the **R** key, alongside a live clock.

### Models
Lists all LLM models currently stored in the persistence layer. Shows model name and metadata columns (params, quantization, disk size, VRAM usage, and status). Users can Load, Unload, or Delete models. This screen refreshes automatically on user action.

### Services
Provides a list of all NeuralDrive systemd units with their current status (active, inactive, failed). Users can select a service to view its recent logs or trigger a restart. This screen auto-polls every 5 seconds.

### Logs
System-wide log viewer for NeuralDrive services and kernel messages.

### Chat
A lightweight chat interface allowing users to test models locally. It includes a model selector dropdown and supports streaming responses via `@work(exclusive=True)`. Model selection persists across screen switches.

## Hotkeys

- **F1**: Dashboard
- **F2**: Models
- **F3**: Services
- **F4**: Logs
- **F5**: Chat
- **Q**: Quit

## Navigation Model

The TUI uses a zone-based focus system.
- **Tab / Shift+Tab**: Cycle focus between different zones within a screen.
- **Arrow Keys**: Navigate within the currently focused zone.
- **Enter**: Activate the selected item or button.

## Custom Widgets

Several custom composite widgets are used to build the interface:
- `SafeHeader`: A subclass of Textual's `Header` that catches `NoMatches` exceptions during `_on_mount`, working around Textual bug #4258.
- `ServiceItem`: Displays service name, status label, and control buttons (Start, Stop, Restart).
- `ModelItem`: Displays model name, metadata, and action buttons (Load, Unload, Delete).

## Crash Dump Logging

The TUI overrides `App._handle_exception` to write crash dumps to `/var/lib/neuraldrive/logs/tui-crash-*.log` with a full traceback. The entire `main()` function is also wrapped in a try/except block to catch crashes occurring outside the Textual event loop. Screenshots are saved to `/var/lib/neuraldrive/screenshots/`.

## CLI Flags

- `--wizard`: Removes the sentinel file (`/etc/neuraldrive/first-boot-complete`) and forces the first-boot wizard to re-run on the next launch.

## Command Palette

The Textual command palette is explicitly disabled (`ENABLE_COMMAND_PALETTE = False`).

## Auto-Login and Startup

The TUI is launched automatically on TTY1 via a `getty@tty1` service override created by the `02-setup-autologin.chroot` build hook. This override configures autologin for the `neuraldrive-admin` user, and a `.bashrc` snippet detects TTY1 and runs `/usr/local/bin/neuraldrive-tui` — a launcher script that activates the Python virtual environment and starts the application.

## Code Location

The source code for the TUI is located at `/usr/lib/neuraldrive/tui/`.
- `main.py`: The main `NeuralDriveTUI` application class and screen orchestration.
- `styles.tcss`: Textual CSS stylesheet for the interface.
- `widgets/`: Custom UI components (gauges, log viewers).
- `screens/`: Individual screen definitions (dashboard, models, services, network, logs, chat, wizard).

## Refresh Intervals

- **Dashboard**: Manual refresh (R key) with live clock.
- **Services**: Auto-polls every 5 seconds.
- **Models**: Refreshes on user action.
- **System Metrics**: Refreshed every 2 seconds.

## Modifying the TUI

To add a new screen or widget:
1. Define the component in the `widgets/` or `screens/` directory.
2. Register the new screen in `main.py`.
3. Test locally by running `python main.py` (ensure you have the `textual` library installed in your venv).

> **Tip**: Use the `textual console` tool during development to see live debug output and CSS reload notifications.


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

### Services
Provides a list of all NeuralDrive systemd units with their current status (active, inactive, failed). Users can select a service to view its recent logs or trigger a restart.

### Models
Lists all LLM models currently stored in the persistence layer. Shows model size and allows users to delete unused models to free up disk space.

### Networking
Allows basic network configuration, such as switching between DHCP and static IP, or configuring a Wi-Fi connection.

## Auto-Login and Startup

The TUI is launched automatically on TTY1 via a `getty@tty1` service override created by the `02-setup-autologin.chroot` build hook. This override configures autologin for the `neuraldrive-admin` user, and a `.bashrc` snippet detects TTY1 and runs `/usr/local/bin/neuraldrive-tui` — a launcher script that activates the Python virtual environment and starts the application.

## Code Location

The source code for the TUI is located at `/usr/lib/neuraldrive/tui/`.
- `main.py`: The main `NeuralDriveTUI` application class and screen orchestration.
- `styles.tcss`: Textual CSS stylesheet for the interface.
- `widgets/`: Custom UI components (gauges, log viewers).
- `screens/`: Individual screen definitions (dashboard, models, services, network, logs, chat, wizard).

## Refresh Intervals

- **System Metrics**: Refreshed every 2 seconds.
- **Service Status**: Refreshed every 5 seconds.
- **Network Info**: Refreshed only on request or after a configuration change.

## Modifying the TUI

To add a new screen or widget:
1. Define the component in the `widgets/` or `screens/` directory.
2. Register the new screen in `main.py`.
3. Test locally by running `python main.py` (ensure you have the `textual` library installed in your venv).

> **Tip**: Use the `textual console` tool during development to see live debug output and CSS reload notifications.


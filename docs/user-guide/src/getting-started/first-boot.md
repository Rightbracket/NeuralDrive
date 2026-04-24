*This chapter is for everyone.*

# First Boot

Setting up NeuralDrive for the first time requires a local keyboard and monitor. Once the initial configuration is complete, you can manage the system entirely over your network.

## Booting NeuralDrive

Insert your NeuralDrive USB and power on your hardware. Access your system's boot menu (usually via F12, F11, or Esc) and select the USB drive. You will see the GRUB boot menu with several options:

- **NeuralDrive (Normal):** The standard boot mode. Enables data persistence and hardware acceleration via `nvidia-drm.modeset=1`.
- **NeuralDrive (Safe Mode):** Use this if you encounter display or boot errors. This mode disables modesetting (`nomodeset`), advanced interrupt controllers (`noapic`), and persistence.
- **NeuralDrive (CD Mode - RAM Only):** Loads the entire system into memory (`toram`). Useful for testing or when using physical optical media where persistence is not possible.
- **NeuralDrive (Debug):** Provides detailed boot information by setting `systemd.log_level=debug`. Use this when troubleshooting startup failures.

## Boot Sequence Overview

NeuralDrive follows a structured startup process:
1. **GRUB:** Loads the initial bootloader and kernel parameters.
2. **live-boot:** Initializes the Debian live environment and mounts the persistent partition.
3. **systemd:** Starts core system services.
4. **GPU Detect:** Automatically identifies NVIDIA, AMD, or Intel hardware and loads appropriate drivers.
5. **Services:** Launches the internal API, system monitor, and web interface.
6. **TUI:** Displays the final status screen.

Once the boot process is complete, the console will display your system's IP address:
`NeuralDrive is ready! Dashboard: https://192.168.x.x/`

## First-Boot Wizard

If the system has not been initialized, a Text User Interface (TUI) wizard will start automatically. The wizard runs as part of the TUI application, checking for a sentinel file on startup. You must complete these six steps to prepare your server:

1. **Welcome:** Introductory screen with hardware summary and system health check.
2. **Storage/Persistence:** Detects your USB boot device and creates an ext4 persistence partition on unused space. This step also creates required directories under `/var/lib/neuraldrive/` (ollama, models, config, webui, logs).
3. **Security:** Sets the administrator password and configures system credentials.
4. **Network:** Configure your network connection, including Wi-Fi (if applicable) and IP assignment (DHCP or static).
5. **Models:** Select initial LLM models to download based on your hardware capabilities.
6. **Done:** Final completion summary and display of system credentials.

### Re-running the Wizard

If you need to reset your configuration, run `neuraldrive-tui --wizard` from the console. This command removes the sentinel file and forces the wizard to run again on the next TUI launch.

### Write Down Your Credentials

At the end of the wizard, your final credentials and the dashboard URL will be displayed. Record these immediately, as they are required for logging into the web dashboard.

## System Initialization Files

NeuralDrive uses a sentinel file to track its state:
- `/etc/neuraldrive/first-boot-complete`: Confirms the user setup wizard has been finished.

Once this file is present, the system will boot directly to the ready state.

Next step: [Web Dashboard](../using/web-dashboard.md)

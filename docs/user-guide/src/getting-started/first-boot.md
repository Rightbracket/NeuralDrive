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

If the system has not been initialized, a Text User Interface (TUI) wizard will start automatically. You must complete these seven steps to prepare your server:

1. **Welcome:** Displays a hardware summary and runs a brief system health check to ensure your GPU is detected correctly.
2. **Security:** Generates a random administrator password and API key. You can choose to keep these or set a custom password.
3. **Wi-Fi:** If no Ethernet connection is detected, the wizard provides an SSID selector to configure your wireless network.
4. **Network:** Choose between DHCP (default) or a static IP address.
5. **Storage:** Select the drive for your persistent data. You can also enable LUKS encryption here. **Warning: This step is destructive to data on the selected drive.**
6. **Models:** Recommends specific LLM starter models based on your hardware's VRAM and capabilities.
7. **Finish:** The system writes your configurations, provisions the web administrator account, and removes insecure default permissions (like NOPASSWD sudo).

### Write Down Your Credentials

At the end of the wizard, your final credentials and the dashboard URL will be displayed. Record these immediately, as they are required for logging into the web dashboard.

## System Initialization Files

NeuralDrive uses two sentinel files to track its state:
- `/etc/neuraldrive/initialized`: Indicates that the core system initialization has occurred.
- `/etc/neuraldrive/first-boot-complete`: Confirms the user setup wizard has been finished.

Once these files are present, the system will boot directly to the ready state in the future.

Next step: [Web Dashboard](../using/web-dashboard.md)

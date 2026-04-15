*This chapter is for contributors and maintainers.*

# First-Boot Wizard

The First-Boot Wizard is a specialized mode of the TUI that guides the user through the initial configuration of the appliance.

## Execution Trigger

The wizard is triggered by the `neuraldrive-setup.service`. This service checks for the existence of `/etc/neuraldrive/.setup-complete`. If this file is missing, the service:
1. Blocks the standard TTY login.
2. Launches the TUI in "Setup Mode".
3. Prevents any other NeuralDrive application services (Ollama, WebUI, Caddy) from starting until setup is finished.

## Wizard Flow

The wizard consists of seven mandatory steps:

1. **Welcome**: Introduction and hardware verification.
2. **Network**: Configuration of Ethernet or Wi-Fi.
3. **Persistence**: Detection and optional encryption (LUKS2) of the persistent partition.
4. **Credentials**: Setting the `neuraldrive-admin` password and generating the initial API key.
5. **Branding**: Setting the system hostname and mDNS name.
6. **Model Selection**: Choosing a "Small", "Medium", or "Large" model to pre-download.
7. **Finalization**: Writing configuration files, generating TLS certs, and creating the sentinel file.

## Credential Generation

- **Admin Password**: The user is prompted to enter a password for the `neuraldrive-admin` account.
- **API Key**: The system automatically generates a 32-character random string, prefixed with `nd-`. This key is displayed to the user once and then stored in `/etc/neuraldrive/api.key`.

## Sentinel File

Once the user completes the wizard, the script runs `touch /etc/neuraldrive/.setup-complete`. This ensures that subsequent reboots proceed directly to the standard dashboard.

## Customizing the Wizard

The wizard logic is integrated into the TUI application. To add a new step:
1. Create a new `Screen` class in `usr/lib/neuraldrive/tui/screens/wizard.py` or in a new screen file within `screens/`.
2. Add the screen to the wizard orchestration loop in `main.py`.

> **Note**: For development, you can re-trigger the wizard on a running system by deleting the sentinel file and restarting the `neuraldrive-setup` service. **Warning**: This may overwrite existing credentials and configuration.


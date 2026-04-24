*This chapter is for contributors and maintainers.*

# First-Boot Wizard

The First-Boot Wizard is a specialized mode of the TUI that guides the user through the initial configuration of the appliance.

## Execution Trigger

The wizard is not a separate service. It is an integrated component of the TUI application (`main.py`). Upon startup, the TUI checks for the existence of the sentinel file `/etc/neuraldrive/first-boot-complete`. If this file is missing, the TUI presents the wizard interface before allowing access to the main dashboard.

## Wizard Flow

The wizard consists of the following steps:

1. **Welcome**: Introduction and hardware verification.
2. **Storage/Persistence**: Detects the boot device, creates the persistence partition, and initializes the directory structure:
   - `/var/lib/neuraldrive/ollama`
   - `/var/lib/neuraldrive/models`
   - `/var/lib/neuraldrive/config`
   - `/var/lib/neuraldrive/webui`
   - `/var/lib/neuraldrive/logs`
3. **Security**: Prompts for the `neuraldrive-admin` password and generates initial credentials.
4. **Network**: Configuration of Ethernet or Wi-Fi.
5. **Models**: Selection of initial models for download.
6. **Done**: Finalizes configuration and generates the sentinel file.

## Credential Generation

- **Admin Password**: The user is prompted to set the password for the `neuraldrive-admin` account.
- **API Key**: The system automatically generates a 32-character random string, prefixed with `nd-`. This key is displayed once and then stored in the persistence layer.

## Sentinel File

Completion of the wizard creates the sentinel file at `/etc/neuraldrive/first-boot-complete`. This ensures that subsequent reboots bypass the wizard and proceed directly to the standard dashboard.

## CLI Re-run

To re-run the wizard on a configured system, use the following command:
`neuraldrive-tui --wizard`
This command removes the sentinel file, forcing the wizard to launch on the next application start.

## Customizing the Wizard

The wizard logic is integrated into the TUI application. To add a new step:
1. Create a new `Screen` class in the `screens/` directory.
2. Add the screen to the wizard orchestration loop in `main.py`.

> **Note**: For development, you can re-trigger the wizard by using the `--wizard` flag. **Warning**: This may overwrite existing credentials and configuration.


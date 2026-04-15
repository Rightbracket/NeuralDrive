*This chapter is for contributors and maintainers.*

# Build Hooks

Hooks are scripts that `live-build` executes inside the chroot environment during the build process. They are used to perform configuration tasks that cannot be handled by simple file inclusion or package installation.

## Hook Execution Order

Hooks are executed in alphabetical order. In NeuralDrive, we use a numeric prefix (e.g., `01-`, `02-`) to ensure a predictable sequence. All hooks are located in `config/hooks/normal/`.

## Current Hooks Breakdown

### `01-setup-system.hook.chroot`
Performs base system configuration, including:
- Setting the default locale and timezone.
- Configuring the hostname.
- Creating the `neuraldrive-admin` user.
- Setting up the `sudoers` file.

### `02-setup-autologin.hook.chroot`
Configures the system to automatically log into the TTY1 console and launch the NeuralDrive TUI. This involves modifying `getty` service overrides.

### `03-install-extras.hook.chroot`
Installs components that are not available via standard APT repositories, such as the Ollama binary. It also handles the installation of GPU-specific firmware.

### `04-install-python-apps.hook.chroot`
Sets up the Python virtual environments for the System API, WebUI, and TUI. It runs `pip install` for all requirements and ensures the environments are correctly owned by their respective service users.

### `05-generate-configs.hook.chroot`
Generates default configuration files and ensures correct permissions for sensitive files (like API keys and TLS directories). It also enables all NeuralDrive systemd services.

## Writing New Hooks

When adding a new hook:
1. **Naming**: Use the `.hook.chroot` suffix.
2. **Interpreter**: Always start with `#!/bin/sh` or `#!/bin/bash`.
3. **Safety**: Include `set -e` to ensure the build fails if the hook encounters an error.
4. **Permissions**: Ensure the script is executable (`chmod +x`).

> **Note**: Hooks run as the root user inside the chroot. Be careful when modifying system files and always verify that the changes will be persistent in the final SquashFS image.


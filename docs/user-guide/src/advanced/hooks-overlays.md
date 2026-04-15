*Audience: Admin (advanced)*

# Custom Hooks & Overlays

The NeuralDrive build system uses the underlying Debian `live-build` framework to allow for deep customization. You can inject scripts, configuration files, and third-party packages into the final image without modifying the core build scripts.

## Hook System

Hooks are executable scripts that run within the Debian environment (chroot) during the image creation process. They allow you to perform complex setup tasks like installing specific Python packages, configuring system services, or modifying system files.

### Implementation

Hooks must be placed in the `hooks/chroot/` directory of the builder. During the build, they are executed in alphabetical order. Using a numeric prefix (e.g., `01-`, `02-`) ensures a deterministic execution sequence.

### Example Hook Script

To install custom Python packages via `pip`:

```bash
#!/bin/bash
# File: hooks/chroot/05-custom-pip-packages.hook.chroot

echo "Installing custom pip packages..."
pip install --no-cache-dir langchain-community chromadb
```

## Overlay System

The overlay system provides a way to add or overwrite files in the final root filesystem. The contents of the `overlay/` directory are mirrored directly onto the target system's root.

### Implementation

If you want to add a file to `/etc/neuraldrive/custom.conf`, you should place it at `overlay/etc/neuraldrive/custom.conf` in the builder directory.

### Common Uses

*   **Config Files**: Provide default configurations for services like SSH, Nginx, or Ollama.
*   **Scripts**: Inject administrative scripts into `/usr/local/bin/`.
*   **Static Assets**: Replace or add branding assets like splash screens or icons.

## Package Injection

You can automatically install third-party Debian (`.deb`) packages by placing them in the `packages/` directory.

### Implementation

Any `.deb` file found in the `packages/` folder will be included in the local repository created during the build and installed by `apt` alongside the standard system packages. This is particularly useful for proprietary drivers or custom-built software not available in the Debian repositories.

## Execution Order

During the `lb build` process, these customizations are applied as follows:

1.  **Overlay Injection**: Files from `overlay/` are copied into the chroot environment.
2.  **Package Installation**: Standard packages and injected `.deb` files are installed via `apt`.
3.  **Hooks**: Scripts in `hooks/chroot/` are executed in alphabetical order.

> **Warning**: Hooks run with root privileges inside the chroot. Ensure your scripts are idempotent and do not fail, as a hook failure will cause the entire image build to fail.

For an overview of the full build process, refer to [Building Custom Images](custom-images.md).

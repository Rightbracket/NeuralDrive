# Plan 09: NeuralDrive Image Toolkit (neuraldrive-builder)

## 1. Toolkit Overview
NeuralDrive is designed to be customizable. The `neuraldrive-builder` toolkit allows users and organizations to create tailored versions of the distribution with specific models, configurations, and branding.

- **Purpose**: Enable custom image generation for specific deployment needs.
- **Target Audience**: Power users, labs, and organizations.
- **Distribution**: Git repository containing build scripts and a Dockerized build environment.
- **Host Requirements**: Linux with Docker (recommended) or Debian 12 (Bookworm) with `live-build`.

## 2. Configuration File Format
The build process is driven by `neuraldrive-build.yaml`.

```yaml
neuraldrive:
  version: "1.0"
  name: "My Custom NeuralDrive"     # Custom image name
  hostname: "my-llm-server"          # Default hostname

  system:
    kernel: "default"                # "default" (6.1) or "backport" (6.12+)
    locale: "en_US.UTF-8"
    timezone: "UTC"
    extra_packages:                  # Additional .deb packages
      - "htop"
      - "vim"

  gpu:
    nvidia: true                     # Include NVIDIA drivers
    amd: false                       # Include AMD ROCm
    intel: false                     # Include Intel Arc support

  models:
    preload:                         # Models baked into the image
      - "llama3.1:8b"
      - "codestral:latest"
    catalog: "default"               # model catalog to include (default/minimal/none)

  network:
    ssh_enabled: false
    default_ip: "dhcp"               # "dhcp" or static IP

  security:
    encrypt_persistent: false
    api_key: ""                      # Pre-set API key, or empty for auto-generate

  webui:
    enabled: true
    admin_email: "admin@example.com"
    branding:
      title: "Custom NeuralDrive"
      logo: "assets/custom-logo.png"   # Path to custom logo file

  output:
    format: "iso-hybrid"             # "iso-hybrid" or "raw-disk"
    filename: "neuraldrive-custom.iso"
    compression: "xz"
```

## 3. Build Scripts

### `build.sh` (Main Entry Point)
```bash
#!/bin/bash
set -e

# Load configuration
CONFIG_FILE="neuraldrive-build.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: $CONFIG_FILE not found."
    exit 1
fi

# 1. Validate Configuration
./scripts/validate-config.sh "$CONFIG_FILE"

# 2. Prepare live-build directory
lb clean
lb config --apt-recommends false --architectures amd64 --bootstrap debootstrap

# 3. Apply Customizations
./scripts/apply-branding.sh "$CONFIG_FILE"
./scripts/download-models.sh "$CONFIG_FILE"

# 4. Run Build
lb build

# 5. Post-process
./scripts/post-build.sh "$CONFIG_FILE"

echo "Build complete: $(yq '.neuraldrive.output.filename' $CONFIG_FILE)"
```

### Helper Scripts
- `scripts/validate-config.sh`: Uses `yq` to check required fields and types.
- `scripts/download-models.sh`: Uses a temporary Ollama instance to pull models into `config/includes.chroot/var/lib/neuraldrive/models/`.
- `scripts/apply-branding.sh`: Replaces splash screens, WebUI logos, and sets `/etc/hostname`.
- `scripts/post-build.sh`: Runs `isohybrid` on the generated ISO and creates `SHA256SUMS`.

## 4. Docker Build Environment

### `Dockerfile`
```dockerfile
FROM debian:bookworm

RUN apt-get update && apt-get install -y \
    live-build \
    debootstrap \
    squashfs-tools \
    xorriso \
    grub-pc-bin \
    grub-efi-amd64-bin \
    mtools \
    python3-yaml \
    wget \
    curl \
    && curl -L https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -o /usr/bin/yq \
    && chmod +x /usr/bin/yq \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
```

### `docker-compose.yml`
```yaml
services:
  builder:
    build: .
    volumes:
      - ./:/build
      - ./output:/output
    privileged: true
    command: /build/build.sh
```

## 5. Model Pre-loading Strategy
Large models are handled via a SquashFS overlay to keep the primary system image manageable.

1.  **Download**: During build, models are pulled into a staging area.
2.  **Compression**: Models are packed into `models.squashfs`.
3.  **Boot Mounting**: At runtime, `neuraldrive-init` detects `models.squashfs` and mounts it to `/var/lib/neuraldrive/models/`.
4.  **First Boot**: On USB media, the initialization script offers to copy pre-loaded models to the `NDATA` persistent partition (`/var/lib/neuraldrive/models/`) to improve performance and allow for updates.

## 6. USB Image Writing
The output ISO is an `isohybrid` image.

- **Command Line**: `sudo dd if=neuraldrive.iso of=/dev/sdX bs=4M status=progress && sync`
- **GUI Tools**: Fully compatible with Balena Etcher, Rufus (DD mode), and Raspberry Pi Imager.
- **Ventoy**: Native support for ISO booting.
- **Partitioning**: On first boot, the system detects the free space on the USB drive, creates an `NDATA` partition, and configures `overlayfs` for persistence.

## 7. Advanced Customization

- **`hooks/chroot/`**: Scripts executed inside the Debian environment before the image is finalized. Use these to install custom pip packages or configure system services.
- **`packages/`**: Drop any `.deb` files here; they will be installed automatically during the build.
- **`overlay/`**: A directory structure that mirrors the root filesystem. Files placed here will overwrite the defaults in the final image.

## 8. Toolkit Documentation
- **`README.md`**: Quick-start guide.
- **`docs/configuration.md`**: Deep dive into every YAML key.
- **`docs/advanced.md`**: Guide for writing custom hooks and using the overlay system.
- **`docs/model-guide.md`**: VRAM requirements and hardware recommendations for popular models.

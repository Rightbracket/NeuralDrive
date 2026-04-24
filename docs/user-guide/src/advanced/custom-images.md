*Audience: Admin*

# Building Custom Images

The `neuraldrive-builder` toolkit provides the necessary infrastructure to generate tailored NeuralDrive ISO images. By modifying the build configuration, you can pre-load specific LLM models, inject custom branding, or bake in specific GPU drivers and system packages.

## Prerequisites

Building a custom image requires a Linux environment with sufficient disk space (at least 50GB recommended) and a fast internet connection for downloading packages and models.

*   **Docker (Recommended)**: The easiest way to build is using the provided Docker environment.
*   **Debian 12 (Native)**: If building natively, you must use Debian 12 (Bookworm) with the `live-build` package installed.

## Build Process

Follow these steps to generate a custom NeuralDrive ISO.

### 1. Prepare the Environment

Clone the NeuralDrive repository and navigate to the builder directory.

```bash
git clone https://github.com/Rightbracket/NeuralDrive.git
cd NeuralDrive/builder
```

### 2. Configure the Build

The build is controlled by `neuraldrive-build.yaml`. Create your configuration file from the provided example.

```bash
cp neuraldrive-build.yaml.example neuraldrive-build.yaml
```

Edit `neuraldrive-build.yaml` to suit your requirements. Key sections include:

*   **system**: Define the kernel version, locale, and additional Debian packages.
*   **gpu**: Enable or disable support for NVIDIA, AMD, and Intel GPUs.
*   **models**: Specify which models to pre-load.
*   **webui**: Customize the management interface branding.
*   **output**: Set the filename and compression level.

### 3. Pre-load Models

> **Note**: Model pre-loading currently requires a manual staging step.

To include models in your image, you must first stage them. The `scripts/download-models.sh` script uses a temporary Ollama instance to pull the models listed in your configuration into the `./model-staging/` directory.

```bash
./scripts/download-models.sh
```

These models are later packaged into the final image.

### 4. Execute the Build

You can run the build either natively or via Docker.

**Using Docker (Recommended):**

```bash
docker compose run builder
```

The Docker environment uses a `debian:bookworm` base and runs in privileged mode to allow `live-build` to mount filesystems.

**Using Native Build:**

```bash
sudo ./build.sh
```

The `build.sh` script performs the following actions:
1. Validates the configuration using `scripts/validate-config.sh`.
2. Prepares the `live-build` environment.
3. Applies branding via `scripts/apply-branding.sh`.
4. Runs the `lb build` process.
5. Post-processes the output via `scripts/post-build.sh` (e.g., running `isohybrid`).

### 5. Retrieve the ISO

Once the build completes, the resulting ISO file will be located in the `output/` directory.

## Configuration Example

```yaml
neuraldrive:
  version: "1.0"
  name: "My Custom NeuralDrive"
  hostname: "my-llm-server"
  system:
    kernel: "default"            # "default" (6.1) or "backport" (6.12+)
    locale: "en_US.UTF-8"
    timezone: "UTC"
    extra_packages: ["htop", "vim"]
  gpu:
    nvidia: true
    amd: false
    intel: false
  models:
    preload: ["llama3.1:8b", "codestral:latest"]
    catalog: "default"           # default/minimal/none
  network:
    ssh_enabled: false
    default_ip: "dhcp"
  security:
    encrypt_persistent: false
    api_key: ""                  # Empty = auto-generate at first boot
  webui:
    enabled: true
    admin_email: "admin@example.com"
    branding:
      title: "Custom NeuralDrive"
      logo: "assets/custom-logo.png"
  output:
    format: "iso-hybrid"
    filename: "neuraldrive-custom.iso"
    compression: "xz"
```

## Build Estimates

Build times vary significantly based on your configuration:
*   **Minimal Image**: 30-45 minutes.
*   **Full GPU Stack (NVIDIA + AMD)**: 60-70 minutes.
*   **Heavy Model Pre-loading**: 90+ minutes (largely dependent on download speeds).

## Output Formats

NeuralDrive supports two primary output formats:
*   **iso-hybrid (Default)**: A bootable image compatible with both USB flash drives and optical media (CD/DVD).
*   **raw-disk**: A standard disk image for virtual machines or direct disk writing.

For detailed information on every configuration key, see the [Build Configuration Reference](build-config-reference.md). To further customize the system during the build process, refer to [Custom Hooks & Overlays](hooks-overlays.md).

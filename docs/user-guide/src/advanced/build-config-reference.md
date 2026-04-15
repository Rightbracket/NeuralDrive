*Audience: Admin*

# Build Configuration Reference

This reference provides a complete annotation of all keys available in the `neuraldrive-build.yaml` file. This file controls the generation of the NeuralDrive ISO image and defines the default system state.

## Specification

### `neuraldrive`
*   `version`: (String) The internal version of the NeuralDrive build. Default: `"1.0"`
*   `name`: (String) The human-readable name of the image. This appears in the boot menu and the WebUI title. Default: `"NeuralDrive"`
*   `hostname`: (String) The default system hostname. Default: `"neuraldrive"`

### `system`
*   `kernel`: (Enum) Specifies the Linux kernel version.
    *   `default`: Standard Debian 12 kernel (6.1 LTS).
    *   `backport`: Newer kernel from Debian backports (6.12+), recommended for recent hardware.
*   `locale`: (String) System locale. Example: `"en_US.UTF-8"`
*   `timezone`: (String) System timezone. Example: `"UTC"` or `"America/New_York"`
*   `extra_packages`: (List) Additional Debian packages to install. Example: `["htop", "vim", "tmux"]`

### `gpu`
*   `nvidia`: (Boolean) Enable NVIDIA driver and toolkit installation. Default: `true`
*   `amd`: (Boolean) Enable ROCm drivers and AMD GPU support. Default: `false`
*   `intel`: (Boolean) Enable Intel GPU and XPU support. Default: `false`

### `models`
*   `preload`: (List) A list of models to pre-load during the build process. Example: `["llama3.1:8b", "codestral:latest"]`
*   `catalog`: (Enum) The set of models to include in the default available list.
    *   `default`: Includes standard common models.
    *   `minimal`: Includes only the absolute essentials for basic testing.
    *   `none`: No models pre-populated.

### `network`
*   `ssh_enabled`: (Boolean) Enable SSH server by default. Default: `false`
*   `default_ip`: (String) Default IP configuration. Use `"dhcp"` or a static IP in CIDR format. Default: `"dhcp"`

### `security`
*   `encrypt_persistent`: (Boolean) Enable LUKS2 encryption for the persistence partition by default. Default: `false`
*   `api_key`: (String) Default API key for external access. If empty, a key will be auto-generated at first boot. Default: `""`

### `webui`
*   `enabled`: (Boolean) Enable the NeuralDrive management WebUI. Default: `true`
*   `admin_email`: (String) The default administrative email for the WebUI. Default: `"admin@example.com"`
*   `branding.title`: (String) The title displayed in the WebUI. Default: `"NeuralDrive"`
*   `branding.logo`: (Path) Path to the custom logo file relative to the builder root. Default: `"assets/logo.png"`

### `output`
*   `format`: (Enum) The final output image format.
    *   `iso-hybrid`: Bootable on both USB and CD.
    *   `raw-disk`: Raw disk image.
*   `filename`: (String) The name of the resulting image file. Default: `"neuraldrive.iso"`
*   `compression`: (Enum) Compression algorithm for the ISO image.
    *   `xz`: Higher compression, slower build time.
    *   `gzip`: Faster build time, larger image size.

## Configuration Examples

### NVIDIA-Only Minimal Image

This configuration creates a lightweight image focused on NVIDIA GPUs with no extra overhead.

```yaml
neuraldrive:
  name: "NVIDIA Minimal NeuralDrive"
gpu:
  nvidia: true
  amd: false
  intel: false
models:
  catalog: "minimal"
  preload: []
```

### Full Image with Pre-loaded Models

A comprehensive image containing all GPU drivers and several models ready for immediate use.

```yaml
neuraldrive:
  name: "Full NeuralDrive with Models"
gpu:
  nvidia: true
  amd: true
  intel: true
models:
  catalog: "default"
  preload: ["llama3.1:8b", "codestral:latest", "mistral:7b"]
output:
  compression: "xz"
```

### Custom Branded Image

Designed for deployment with specific hostname and branding requirements.

```yaml
neuraldrive:
  name: "Company NeuralDrive"
  hostname: "company-llm-server"
webui:
  branding:
    title: "Company AI Lab"
    logo: "assets/company-logo.png"
network:
  ssh_enabled: true
```

For more details on the build process, see [Building Custom Images](custom-images.md).

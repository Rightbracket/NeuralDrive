*This chapter is for contributors and maintainers.*

# Directory Structure

This chapter describes the purpose of the primary directories and files in the NeuralDrive repository.

## Root Directory

- `build.sh`: The main entry point for starting a build.
- `Dockerfile`: Defines the containerized build environment.
- `docker-compose.yml`: Orchestrates the builder container and volume mounts.
- `neuraldrive-build.yaml.example`: Template for CI/CD or local build configurations.

## config/

The `config/` directory is the heart of the `live-build` setup.

- `archives/`: Contains `.list` and `.key` files for external repositories (e.g., ROCm, Intel, Debian Backports).
- `hooks/`:
  - `live/`: Scripts that run inside the chroot during the build process. They must be named with a numeric prefix (e.g., `01-setup-system.chroot`).
- `includes.chroot/`: This directory mirrors the root filesystem of the final appliance.
  - `etc/neuraldrive/`: Configuration files for Ollama, WebUI, and the System API.
  - `etc/systemd/system/`: Systemd unit files for all NeuralDrive services.
  - `usr/lib/neuraldrive/`: Location for custom scripts, Python applications, and their virtual environments.
- `package-lists/`:
  - `neuraldrive.list.chroot`: List of standard Debian packages to install.
  - `nvidia.list.chroot`: Packages required for NVIDIA GPU support.
- `preseed/`: (Empty) NeuralDrive uses a live system approach rather than a traditional Debian installer, so preseed files are not used.

## scripts/

Contains utility scripts for developers and maintainers:
- `neuraldrive-flash.sh`: Writes a generated ISO to a physical USB drive.
- `download-models.sh`: Downloads model weights from the Ollama registry for pre-loading.
- `seed-models.sh`: Stages downloaded models into the build filesystem.
- `apply-branding.sh`: Applies NeuralDrive branding to the Open WebUI interface.
- `validate-config.sh`: Validates the build configuration before starting.
- `post-build.sh`: Post-build cleanup and image finalization.

## docs/

Source files for the documentation.
- `user-guide/`: End-user documentation.
- `dev-guide/`: This developer guide.

## tests/

Integration and unit tests.
- `test_api.py`: Pytest suite for the System API.
- `test-boot.sh`: Launches the ISO in QEMU for boot verification.
- `test-gpu.sh`: Shell script for on-target GPU validation.

## plan/

Internal design documents and implementation plans used during the development of NeuralDrive.


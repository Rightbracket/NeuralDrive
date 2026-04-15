*This chapter is for contributors and maintainers.*

# Development Environment Setup

Setting up a reliable development environment is the first step toward contributing to NeuralDrive. Because the project relies on `live-build` to generate a bootable Debian image, the host environment must support several low-level system tools.

## Supported Environments

There are three primary ways to set up your development environment:

### Option A: Debian 12 Native (Recommended)
Developing on a native Debian 12 (Bookworm) system is the most reliable method. It avoids potential issues with loop device mounting and filesystem permissions that can occur in containerized environments.

### Option B: Docker (Any OS)
If you are on macOS, Windows, or a non-Debian Linux distribution, you can use the provided Docker environment. This container encapsulates all necessary build dependencies. Note that building requires privileged mode to manage loop devices for SquashFS and ISO generation.

### Option C: Virtual Machine
Running Debian 12 inside a VM (via VirtualBox, Proxmox, or VMware) provides the benefits of a native environment while keeping the build system isolated from your primary OS.

## Prerequisites

Regardless of your environment, you must install the core build dependencies.

### Core Build Tools
Install the following packages on a Debian-based host:
```bash
sudo apt update
sudo apt install -y \
    live-build \
    debootstrap \
    squashfs-tools \
    xorriso \
    grub-pc-bin \
    grub-efi-amd64-bin \
    mtools \
    yq \
    git \
    curl
```

### Python Environment
The System API and TUI are developed in Python. It is recommended to use a virtual environment for local development:
```bash
python3 -m venv venv
source venv/bin/activate
pip install textual psutil httpx rich  # TUI dependencies
pip install fastapi uvicorn            # API dependencies
```

## Repository Structure

After cloning the repository, familiarize yourself with the layout:
- `config/`: The core of the `live-build` configuration.
- `config/hooks/`: Scripts executed inside the chroot during the build process.
- `config/includes.chroot/`: Files that are copied directly onto the final system filesystem.
- `scripts/`: Helper scripts for building, flashing, and testing.
- `docs/`: Markdown source for this documentation and the user guide.

## Tooling and Editors

Any text editor can be used, but VS Code or Neovim are recommended for their robust support for Shell and Python.

> **Tip**: Install the ShellCheck extension to catch common errors in hook scripts and helper utilities.

## QEMU for Testing

To test the generated ISO images without flashing a physical drive, install QEMU:
```bash
sudo apt install qemu-system-x86 qemu-utils
```
This allows you to run the `tests/test-boot.sh` utility to verify that the image boots correctly in a virtualized environment.


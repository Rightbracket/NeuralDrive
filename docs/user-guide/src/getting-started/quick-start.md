*Audience: Users ready to install and deploy NeuralDrive for the first time.*

# Quick Start Guide

This guide describes how to flash NeuralDrive to a USB drive and start your first inference server.

## Prerequisites

- NeuralDrive ISO file.
- A USB flash drive (16 GB or larger).
- A target computer with x86_64 architecture and compatible GPU.

## Step 1: Flash the USB Drive

The method depends on which operating system you are using to write the USB drive.

**Linux** — Use the automated flash script for the simplest experience:
```bash
sudo ./scripts/neuraldrive-flash.sh neuraldrive.iso /dev/sdX
```
This writes the image and creates the persistence partition in one step.

**macOS** — Use `dd` with macOS device paths:
```bash
diskutil list                                          # find your USB (e.g., /dev/disk4)
diskutil unmountDisk /dev/diskN
sudo dd if=neuraldrive.iso of=/dev/rdiskN bs=4m status=progress
diskutil eject /dev/diskN
```

**Windows** — Use [Rufus](https://rufus.ie/) or [Balena Etcher](https://etcher.balena.io/) to write the ISO to your USB drive.

**Any platform** — [Balena Etcher](https://etcher.balena.io/) provides a graphical interface that works on Linux, macOS, and Windows.

> [!NOTE]
> On macOS and Windows, the persistence partition cannot be created during flashing. NeuralDrive will detect this on first boot and offer to set it up automatically. For full details on each method and persistence setup, see [Writing the USB Drive](writing-usb.md).

## Step 2: Boot from USB

1. Insert the USB drive into the target machine.
2. Power on the machine and access the BIOS/UEFI boot menu (typically by pressing F12, F11, or ESC).
3. Select the NeuralDrive USB device and press Enter.

## Step 3: Complete First-Boot Wizard

NeuralDrive will automatically launch a seven-step wizard to configure your server.

1. Set the administrative password.
2. Generate your API key.
3. Configure Wi-Fi or Ethernet settings.
4. Set up the local storage and persistence partition.

## Step 4: Record the IP Address

Once the wizard is complete, the local console (TUI) will display the system's IP address and mDNS hostname (default: `neuraldrive.local`). Note this address for remote access.

## Step 5: Access the Web Dashboard

1. Open a web browser on a different computer on the same network.
2. Navigate to `https://<IP-ADDRESS>/` (or `https://neuraldrive.local/`).
3. You will receive a self-signed certificate warning; accept it to proceed.

## Step 6: Log In

Log in using the administrative credentials you created during the first-boot wizard.

## Step 7: Pull a Model

1. Navigate to the model management section of the dashboard.
2. Enter the name of a model (e.g., `llama3.1`) and click Pull.
3. Once the download is complete, you can begin chatting or using the API.

> [!TIP]
> **Connecting a coding agent?**
> See the [Connecting Coding Agents](../api/coding-agents.md) guide for API details.

> [!NOTE]
> **Booting from CD?**
> If you are using read-only media, see [CD Mode vs USB Mode](../advanced/cd-vs-usb.md) for details on RAM-only operation.

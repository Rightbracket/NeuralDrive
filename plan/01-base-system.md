# NeuralDrive Implementation Plan 01: Base System, Kernel & Build Environment

This document outlines the setup and configuration of the NeuralDrive base system, a headless Linux distribution optimized for LLM inference.

## Section 1: Build Environment Setup

### Host Requirements
- **OS**: Debian 12 (Bookworm) or Ubuntu 22.04+ (LTS).
- **Disk Space**: Minimum 20 GB free space for build artifacts and compressed images.
- **RAM**: 8 GB minimum (16 GB recommended for faster SquashFS compression).

### Installing Build Dependencies
Run the following on the host system:
```bash
sudo apt update
sudo apt install -y live-build debootstrap squashfs-tools xorriso \
    grub-pc-bin grub-efi-amd64-bin mtools
```

### Docker-based Build Alternative
For non-Debian hosts, use this `Dockerfile`:
```dockerfile
FROM debian:bookworm
RUN apt-get update && apt-get install -y \
    live-build debootstrap squashfs-tools xorriso \
    grub-pc-bin grub-efi-amd64-bin mtools \
    sudo
WORKDIR /build
```

### Directory Structure
```text
NeuralDrive/
├── auto/                # live-build automation scripts
├── config/
│   ├── hooks/           # custom scripts for chroot
│   ├── includes.chroot/ # files to overlay on rootfs
│   ├── package-lists/   # lists of .deb packages
│   └── preseed/         # debconf answers
└── build.sh             # entry point script
```

---

## Section 2: live-build Configuration

### Initialization
Initialize the configuration with the following flags:
```bash
lb config \
    --distribution bookworm \
    --architectures amd64 \
    --binary-images iso-hybrid \
    --bootloaders "grub-efi,grub-pc" \
    --debian-installer none \
    --archive-areas "main contrib non-free non-free-firmware" \
    --apt-recommends false \
    --linux-packages "linux-image-amd64" \
    --iso-volume "NeuralDrive" \
    --iso-application "NeuralDrive Inference Server" \
    --iso-publisher "NeuralDrive Project"
```

### Package Selection
Create `config/package-lists/neuraldrive.list.chroot`:
```text
# Base System
systemd
systemd-sysv
dbus
network-manager
iproute2
iputils-ping
curl
wget
ca-certificates
gnupg
sudo
less
vim-tiny
htop
pciutils
usbutils
lsof
tmux

# Filesystem Utilities
btrfs-progs
e2fsprogs
dosfstools
parted
gdisk
cryptsetup

# Firmware
linux-firmware
firmware-misc-nonfree

# Networking & Remote Access
nftables
openssh-server
avahi-daemon
fail2ban

# Python (required for TUI and management API)
python3
python3-venv
python3-pip

# Build tools (for pip packages with C extensions)
build-essential
python3-dev

# Caddy reverse proxy (downloaded via hook)
# See config/hooks/live/03-install-extras.chroot
```

### Custom Hooks
Create `config/hooks/live/01-setup-system.chroot`:
```bash
#!/bin/sh
set -e

# Disable SSH by default (security — enabled via TUI or boot param)
systemctl disable ssh

# Create neuraldrive service users
useradd -r -s /usr/sbin/nologin -u 901 neuraldrive-ollama
useradd -r -s /usr/sbin/nologin -u 902 neuraldrive-webui
useradd -r -s /usr/sbin/nologin -u 903 neuraldrive-caddy
useradd -r -s /usr/sbin/nologin -u 904 neuraldrive-monitor

# Create admin user for TUI access
useradd -m -s /bin/bash -G sudo,video,render neuraldrive-admin

# Allow neuraldrive-admin sudo without password (first-boot wizard sets real password)
echo "neuraldrive-admin ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/neuraldrive-admin
chmod 440 /etc/sudoers.d/neuraldrive-admin

# Create NeuralDrive directories
mkdir -p /etc/neuraldrive /var/lib/neuraldrive/models /var/log/neuraldrive /usr/lib/neuraldrive

# Enable NeuralDrive services
systemctl enable neuraldrive-setup.service
systemctl enable neuraldrive-gpu-detect.service
systemctl enable nftables.service
systemctl enable avahi-daemon.service
```

Create `config/hooks/live/02-setup-autologin.chroot` — auto-launch TUI on tty1 and display IP at boot:
```bash
#!/bin/sh
set -e

# Configure automatic login to neuraldrive-admin on tty1
mkdir -p /etc/systemd/system/getty@tty1.service.d/
cat > /etc/systemd/system/getty@tty1.service.d/autologin.conf << 'EOF'
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin neuraldrive-admin --noclear %I $TERM
EOF

# Auto-start TUI on login for neuraldrive-admin
cat >> /home/neuraldrive-admin/.profile << 'PROFILE'
# Launch NeuralDrive TUI on interactive login to tty1
if [ "$(tty)" = "/dev/tty1" ] && [ -z "$DISPLAY" ]; then
    exec /usr/local/bin/neuraldrive-tui
fi
PROFILE

# Create IP display script (shown on tty2+ and during boot)
cat > /usr/lib/neuraldrive/show-ip.sh << 'IPSCRIPT'
#!/bin/bash
IP_ADDR=$(ip -4 route get 1 2>/dev/null | awk '{print $7; exit}')
echo ""
echo "============================================"
echo "  NeuralDrive is ready!"
echo "  Dashboard: https://${IP_ADDR:-[no network]}/"
echo "  API:       https://${IP_ADDR:-[no network]}:8443/v1"
echo "  mDNS:      https://neuraldrive.local/"
echo "============================================"
echo ""
IPSCRIPT
chmod +x /usr/lib/neuraldrive/show-ip.sh
```

Create `config/hooks/live/03-install-extras.chroot` — install Caddy and Ollama:
```bash
#!/bin/sh
set -e

# Install Caddy
curl -fsSL https://caddyserver.com/api/download?os=linux\&arch=amd64 -o /usr/local/bin/caddy
chmod +x /usr/local/bin/caddy

# Install Ollama (download release binary since no official .deb in Debian repos)
curl -fsSL https://ollama.com/download/ollama-linux-amd64 -o /usr/local/bin/ollama
chmod +x /usr/local/bin/ollama
```

---

## Section 3: Kernel Configuration

### Kernel Selection
- **Default**: `linux-image-amd64` (6.1 LTS).
- **Backports**: To enable newer GPU support, add `bookworm-backports` to `config/archives/backports.list.chroot`:
  ```text
  deb http://deb.debian.org/debian bookworm-backports main contrib non-free non-free-firmware
  ```
  Then specify `--linux-packages "linux-image-amd64/bookworm-backports"`.

### Kernel Parameters
Default boot options in `config/bootloaders/grub-pc/grub.cfg`:
- `quiet splash`: Clean boot output.
- `nomodeset`: Fallback for driver issues.
- `nvidia-drm.modeset=1`: Required for CUDA/Wayland-related features.

---

## Section 4: Bootloader Configuration

### GRUB Menu Entries
Configured in `config/includes.binary/boot/grub/grub.cfg`:
```text
menuentry "NeuralDrive (Normal)" {
    linux /live/vmlinuz boot=live components quiet splash nvidia-drm.modeset=1 findiso
    initrd /live/initrd.img
}

menuentry "NeuralDrive (Safe Mode)" {
    linux /live/vmlinuz boot=live components nomodeset noapic irqpoll
    initrd /live/initrd.img
}

menuentry "NeuralDrive (CD Mode - RAM Only)" {
    linux /live/vmlinuz boot=live components toram noprompt
    initrd /live/initrd.img
}

menuentry "NeuralDrive (Debug)" {
    linux /live/vmlinuz boot=live components verbose systemd.log_level=debug break=bottom
    initrd /live/initrd.img
}
```

### Customization
- **Timeout**: `set timeout=5`.
- **Splash**: Place `splash.png` in `config/includes.binary/boot/grub/`.

---

## Section 5: System Services Configuration

### First-Boot Detection
Script: `/usr/lib/neuraldrive/first-boot.sh`
```bash
#!/bin/bash
if [ ! -f /etc/neuraldrive/initialized ]; then
    # Generate SSH host keys
    ssh-keygen -A
    # Set default hostname
    hostnamectl set-hostname neuraldrive
    touch /etc/neuraldrive/initialized
fi
```

### systemd Units
`config/includes.chroot/etc/systemd/system/neuraldrive-setup.service`:
```ini
[Unit]
Description=NeuralDrive Initial Setup
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/lib/neuraldrive/first-boot.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

---

## Section 6: Build Process

### Build Execution
```bash
sudo lb clean --all
sudo lb config \
    --distribution bookworm \
    --architectures amd64 \
    --binary-images iso-hybrid \
    --bootloaders "grub-efi,grub-pc" \
    --debian-installer none \
    --archive-areas "main contrib non-free non-free-firmware" \
    --apt-recommends false
sudo lb build
```

### Output
- `live-image-amd64.hybrid.iso`: Flash to USB with `dd` or burn to CD.

### Estimates & Troubleshooting
- **Build Time**: ~15-30 minutes depending on network speed and CPU.
- **Failures**: Common issues include lack of disk space during SquashFS creation or missing firmware packages. Ensure `non-free-firmware` is in `archive-areas`.

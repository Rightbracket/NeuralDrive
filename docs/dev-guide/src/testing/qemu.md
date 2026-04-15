*This chapter is for contributors and maintainers.*

# QEMU Boot Tests

QEMU is the primary tool for verifying that the generated ISO images boot correctly and that the initial system services are initialized.

## The test-boot.sh Script

Located at `scripts/test-boot.sh`, this script automates the process of launching an ISO in a virtual machine.

### Usage
```bash
./scripts/test-boot.sh build/neuraldrive-dev.iso
```

### VM Configuration
The script configures QEMU with the following parameters:
- **CPU**: `host` (if available) or `qemu64`.
- **Memory**: 8GB.
- **Boot Mode**: UEFI (via OVMF firmware).
- **Networking**: User-mode networking with port forwarding:
  - `4443` -> `443` (WebUI)
  - `3001` -> `3001` (System API)
- **Persistence**: A virtual 20GB disk is created to simulate the persistence partition.

## What is Validated?

A successful QEMU boot test confirms:
1. **GRUB Integrity**: The bootloader loads and displays the menu.
2. **Kernel/Initrd**: The system successfully transitions from the initramfs to the SquashFS root.
3. **systemd Startup**: Core services reach the `multi-user.target`.
4. **TUI Initialization**: The console on TTY1 displays either the dashboard or the setup wizard.
5. **Network Connectivity**: The virtual machine receives an IP address and the forwarded ports respond to requests.

## Adding New Boot Tests

To test specific scenarios (like multiple disks or specific network configurations), you can pass additional flags to `test-boot.sh`.

```bash
# Example: Testing with a simulated secondary disk
./scripts/test-boot.sh --extra-drive /path/to/disk.img build/neuraldrive-dev.iso
```

> **Tip**: Use the `-nographic` flag if you are testing on a headless server. You can then connect to the TUI via a virtual serial console or SSH if enabled.


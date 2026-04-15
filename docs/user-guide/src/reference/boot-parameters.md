*Audience: Admin*

# Boot Parameters

NeuralDrive supports several kernel command-line parameters to modify system behavior during the boot process.

## Supported Parameters

| Parameter | Default | Description |
| :--- | :--- | :--- |
| `neuraldrive.ssh=1` | unset | Enables the SSH server on boot. Required for remote management. |
| `neuraldrive.safe=1` | unset | Safe Mode: Skips GPU detection and driver loading. Forces CPU inference. |
| `neuraldrive.debug=1` | unset | Enables verbose logging during the entire boot sequence. |
| `neuraldrive.ip=<IP>` | DHCP | Sets a static IP address for the primary network interface. |
| `persistence` | set | Enables the persistence partition if detected on the USB media. |
| `toram` | unset | Loads the entire system image into system RAM. Required for CD mode. |
| `nomodeset` | unset | Disables Kernel Mode Setting (KMS), providing a generic VGA console. |

## How to Modify Parameters

### One-time Modification

To temporarily add a parameter during boot:

1.  Reboot the system and wait for the GRUB menu to appear.
2.  Press `e` to edit the current boot entry.
3.  Locate the line starting with `linux`.
4.  Add your parameter(s) to the end of that line.
5.  Press `Ctrl+X` or `F10` to boot with the modified parameters.

### Permanent Modification

To permanently change boot parameters in a custom NeuralDrive image, you must modify the GRUB configuration template before generating the final ISO:

1.  Edit `/boot/grub/grub.cfg` in your source directory.
2.  Update the `linux` lines with your desired defaults.

> **Warning**: Modifying the `persistence` parameter may result in data loss if not configured correctly for your target media.

> **Note**: For issues related to system startup, consult the [Boot Failures troubleshooting guide](../troubleshooting/boot.md).

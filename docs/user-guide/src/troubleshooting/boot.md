*Audience: Everyone*

# Boot Failures

This section addresses issues that prevent NeuralDrive from reaching the console or dashboard.

## BIOS and UEFI Compatibility

NeuralDrive is distributed as an `isohybrid` image, which supports both legacy BIOS and modern UEFI boot modes.

1.  **Preferred Mode**: UEFI is highly recommended for compatibility with modern GPU drivers and Secure Boot.
2.  **Boot Order**: Ensure the USB flash drive is set as the primary boot device in your system firmware.
3.  **USB Port**: If the drive is not detected, try a different USB port (e.g., USB 2.0 instead of 3.x).

## GRUB Menu Options

When the system starts, the GRUB menu provides three primary boot entries:

-   **Normal**: Standard boot with full GPU detection and driver initialization.
-   **Safe Mode**: Skips GPU driver loading and PCI enumeration. Use this if the system hangs during boot.
-   **Debug Mode**: Appends `debug` and `verbose` to the kernel command line, providing detailed systemd output for troubleshooting.

## Common Boot Errors

### Black Screen

If the system hangs with a black screen or blinking cursor shortly after selecting a boot entry:

1.  **Driver Issue**: This is typically caused by a GPU driver conflict. Reboot and select **Safe Mode**.
2.  **Kernel Modesetting**: If Safe Mode fails, try editing the boot parameter (press 'e' in GRUB) and add `nomodeset`.

### "No bootable device"

If the hardware fails to recognize the USB drive entirely:

1.  **Flash Verification**: The image may have been written incorrectly. Re-flash the USB drive and enable "Verify write" in your flashing utility.
2.  **GPT vs MBR**: Ensure your BIOS is set to match the partition style of the flash drive.

### Kernel Panic

If the boot process halts with a "Kernel Panic" or "VFS: Unable to mount root fs":

1.  **Corrupt Image**: This usually indicates a bad write to the USB drive. Re-flash using a high-quality USB 3.x drive.
2.  **Memory Corruption**: In rare cases, this may indicate faulty RAM. Run a MemTest86+ cycle to verify hardware health.

> **Note**: For a complete list of supported kernel arguments, see [Boot Parameters](../reference/boot-parameters.md). For instructions on creating the bootable media, see [Writing the USB Drive](../getting-started/writing-usb.md).

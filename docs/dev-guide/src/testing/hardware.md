*This chapter is for contributors and maintainers.*

# Hardware Compatibility Testing

Hardware Compatibility Testing (HCT) is the process of verifying that NeuralDrive runs reliably on various physical machine configurations.

## The HCT Process

HCT is performed manually by contributors and community members. It focuses on the areas where virtualization (QEMU) cannot provide accurate results.

### 1. Boot Compatibility
- **UEFI vs BIOS**: Testing boot success on both modern UEFI and legacy BIOS systems.
- **Secure Boot**: Verifying if the image boots with Secure Boot enabled (requires signed kernels).
- **USB Controller Compatibility**: Ensuring the live system can boot from USB 2.0, 3.0, and 3.1 ports.

### 2. Network Stability
- **Ethernet Chipsets**: Testing common drivers (Intel, Realtek, Mellanox).
- **Wi-Fi Support**: Verifying that firmware for common Wi-Fi cards (Intel Wireless, Broadcom) is included and functional.

### 3. Storage Performance
- **Persistence Latency**: Measuring the performance impact of the OverlayFS layer on different types of media (USB stick vs. NVMe SSD).
- **LUKS Performance**: Ensuring that encrypted persistence does not significantly degrade model loading times.

## Reporting Results

We use a "Hardware Compatibility List" (HCL) to track verified systems. When reporting a test result, include:
- **Manufacturer and Model** (e.g., Dell PowerEdge R740, Razer Blade 15).
- **CPU and RAM**.
- **GPU Model and VRAM**.
- **NeuralDrive Version**.
- **Status** (Verified, Issues Found, Not Working).

## Community Testing Program

NeuralDrive encourages users to participate in the testing program by providing pre-release "Beta" ISOs. Feedback from these tests is used to refine the `gpu-detect.sh` script and include missing firmware in the base image.

> **Tip**: If a system fails to boot, capturing the output of `journalctl -b` (if reachable via SSH) or taking a photo of the console screen is essential for debugging.


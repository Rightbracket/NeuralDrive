*Audience: Everyone*

# Common Issues

This guide provides solutions for frequent technical challenges encountered while using NeuralDrive. If your issue is not listed here, consult the specialized troubleshooting pages for [GPU](gpu.md), [Boot](boot.md), [Network](network.md), or [Models](models.md).

## Dashboard and Access

### I can't reach the web dashboard

If the web interface does not load at `https://neuraldrive.local`, verify the following:

1.  **Check the Local IP**: The NeuralDrive console (TUI) displays the current IP address. Attempt to connect directly via `https://<IP_ADDRESS>`.
2.  **Verify Port 443**: Ensure your client machine can reach the NeuralDrive device on port 443. Some firewalls or router settings may block this traffic.
3.  **Network Connection**: Confirm the NeuralDrive device has an active Ethernet or Wi-Fi connection.
4.  **mDNS Resolution**: The `.local` hostname requires mDNS (Avahi/Bonjour) support on the client. If your client is on a corporate network, mDNS may be filtered.

### The API returns 401 Unauthorized

All API requests must include a valid Bearer token.

1.  **Key Format**: Verify your API key follows the `nd-xxxx` format.
2.  **Header Syntax**: Ensure the header is sent correctly:
    ```http
    Authorization: Bearer nd-xxxx
    ```
3.  **Key Location**: The system API key is stored in `/etc/neuraldrive/api.key` and can be viewed or rotated via the TUI.

## System Persistence

### My models disappeared after reboot

NeuralDrive is a live system. Data only survives reboots if a persistence partition is active.

1.  **USB Mode Requirement**: Persistence is only available when running from a USB drive with a labeled `persistence` partition. It does not function in "Live CD" (ISO only) mode.
2.  **Verify Mount**: Run the following command to check if the persistence layer is active:
    ```bash
    mount | grep persistence
    ```
3.  **Partition Health**: If the partition is present but not mounting, check the filesystem integrity using `fsck`.

## Resource Management

### The system is running out of memory

Large language models require significant RAM or VRAM. If the system becomes unresponsive or returns memory errors:

1.  **Downsize the Model**: Use a smaller model (e.g., 7B instead of 70B).
2.  **Increase Quantization**: Use a more compressed version of the model (e.g., Q4_K_M instead of Q8_0 or FP16).
3.  **Check Swap**: NeuralDrive uses zram for compressed swap. Verify it is active with `zramctl`.

### Model download is extremely slow or fails

1.  **Storage Space**: Model downloads will abort if the disk is full. Check availability with `df -h /var/lib/neuraldrive`.
2.  **Network Stability**: Ensure the device has a stable connection to the internet. Downloads are resumed automatically if interrupted, but high latency can cause timeouts.
3.  **Proxy Settings**: If you are behind a corporate proxy, ensure the environment variables are correctly set in `/etc/neuraldrive/ollama.conf`.

## Service Status

### The TUI shows 'Ollama Offline'

If the inference engine is not responding:

1.  **Check Service Status**:
    ```bash
    systemctl status neuraldrive-ollama
    ```
2.  **Restart the Service**:
    ```bash
    systemctl restart neuraldrive-ollama
    ```
3.  **Check Logs**: If the service fails to start, inspect the logs for GPU driver or initialization errors:
    ```bash
    journalctl -u neuraldrive-ollama -e
    ```

## Diagnostics

### NeuralDrive-Check

NeuralDrive includes a dedicated diagnostic tool for rapid health assessment. Run this from the console or via SSH:

```bash
/usr/bin/neuraldrive-check
```

This tool verifies:
-   GPU driver initialization and VRAM availability.
-   Persistence partition mount status.
-   Core service health (Ollama, WebUI, Caddy).
-   Network connectivity and API key validity.

> **Tip**: Always run `neuraldrive-check` before seeking manual support, as it identifies 90% of common configuration errors.

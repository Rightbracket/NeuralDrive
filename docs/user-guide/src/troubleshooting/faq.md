*Audience: Everyone*

# Frequently Asked Questions

This guide provides answers to common questions about NeuralDrive's capabilities, architecture, and administration.

## Installation and Compatibility

### Can I install NeuralDrive to a hard drive?

NeuralDrive is a live system designed to run from removable media. It is not intended for standard disk installation. Persistence of configuration and models is achieved through a dedicated partition on the USB drive. This ensures the host system remains untouched and the appliance remains portable.

### Can I run NeuralDrive in a Virtual Machine (VM)?

Yes. You can run NeuralDrive in a VM using the ISO image. For optimal performance, you must use GPU passthrough to give the VM direct access to the host hardware. If GPU passthrough is not available, NeuralDrive will fallback to CPU-only mode, which is significantly slower but functional.

### Can I use NeuralDrive without a GPU?

Yes. If no compatible GPU is detected, NeuralDrive will automatically fallback to CPU inference. While functional, the performance will be substantially lower than GPU-accelerated modes. This is ideal for lightweight testing or running small models on high-performance CPUs.

## Usage and Administration

### How do I add more users?

NeuralDrive uses Open WebUI for its primary dashboard. You can manage users through the Admin Panel at `https://<IP_ADDRESS>/admin`. Note that user registration is disabled by default to maintain local security; the admin must manually create or approve new user accounts.

### Can I use NeuralDrive offline?

NeuralDrive is fully offline-capable. Once models are downloaded, no internet connection is required for inference, API access, or dashboard usage. For entirely air-gapped operations, you can pre-load models onto the persistence partition of your USB drive before moving to the target environment.

### How is this different from running Ollama directly?

NeuralDrive is a turnkey appliance that eliminates the complexity of system setup. It includes:
-   An optimized operating system with a minimal attack surface.
-   Automated GPU driver detection and configuration.
-   A built-in web dashboard, API gateway, and system monitoring.
-   Self-signed TLS encryption for all traffic.
-   Pre-configured firewall and security hardening.
-   Portability on a single USB drive.

### Can I use my own TLS certificate?

Yes. You can replace the default self-signed certificates in `/etc/neuraldrive/tls/` with your own PEM-formatted certificates. After replacing the files, restart the Caddy service to apply the changes:
```bash
systemctl restart neuraldrive-caddy
```

### Is there any telemetry or data collection?

No. NeuralDrive is designed for privacy and local-first operations. No data, usage metrics, or telemetry are ever sent to external servers.

## Hardware and Performance

### What models are recommended?

Model performance depends entirely on your available VRAM and RAM. See [Model Recommendations](../models/recommendations.md) for a list of tested models and their hardware requirements.

### Can I use multiple GPUs?

Yes. Ollama automatically detects and utilizes all available GPUs from the same vendor. It will distribute model layers across GPUs to maximize VRAM utilization, enabling the execution of models that are too large for a single card.

> **Note**: For more information on hardware compatibility, see the [Hardware Matrix](../reference/hardware-matrix.md). For advanced system settings, see [Boot Parameters](../reference/boot-parameters.md).

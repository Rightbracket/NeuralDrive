*This chapter is for contributors and maintainers.*

# Service Dependency Graph

NeuralDrive uses systemd to manage a complex tree of service dependencies. Understanding this graph is essential for troubleshooting startup issues and adding new components.

## Dependency Types

We primarily use three types of systemd dependencies:
- **`Requires=`**: Strong dependency. If the required unit fails, this unit will not start.
- **`Wants=`**: Weak dependency. This unit will attempt to start the wanted unit, but will proceed even if it fails.
- **`After=` / `Before=`**: Controls ordering. Does not imply a requirement, only the sequence in which units are started.

## Core Dependency Tree

The following diagram illustrates the relationship between the primary NeuralDrive services.

```text
multi-user.target
├── neuraldrive-caddy.service
│   ├── After: network.target
│   ├── Requires: neuraldrive-certs.service
│   └── Wants: neuraldrive-webui.service, neuraldrive-system-api.service
├── neuraldrive-webui.service
│   ├── After: neuraldrive-ollama.service
│   └── Wants: neuraldrive-ollama.service
├── neuraldrive-ollama.service
│   ├── After: neuraldrive-gpu-detect.service
│   └── Requires: neuraldrive-gpu-detect.service
├── neuraldrive-system-api.service
│   └── After: network.target
├── neuraldrive-gpu-detect.service
│   └── Before: neuraldrive-ollama.service
└── neuraldrive-certs.service
    └── Before: neuraldrive-caddy.service
```

## Service Breakdown

### `neuraldrive-ollama`
This is the most critical service in the application stack. It requires `neuraldrive-gpu-detect` to ensure that kernel modules for NVIDIA, AMD, or Intel GPUs are loaded before the Ollama binary attempts to initialize its compute provider.

### `neuraldrive-caddy`
As the edge proxy, Caddy is the final piece of the puzzle. It requires `neuraldrive-certs` because it cannot bind to port 443 without valid certificate files in `/etc/neuraldrive/tls/`. It also `Wants` the backend services (WebUI and System API) so that systemd attempts to bring the whole stack up when the proxy is started.

### `neuraldrive-gpu-monitor`
This service runs independently of Ollama. It `Wants=neuraldrive-gpu-detect` but can run in a fallback mode using CPU-only monitoring if no GPU is found.

## Failure Cascades

- **GPU Detection Failure**: If `gpu-detect` fails, `ollama` will not start. Consequently, the WebUI will show connection errors, though the System API will remain available for logs.
- **Certificate Failure**: If `certs.service` fails to generate or find certificates, `caddy` will fail to start. This makes the appliance unreachable over the network via HTTPS.

> **Tip**: Use `systemctl list-dependencies neuraldrive-caddy.service` on a running system to see a live representation of the current dependency tree.


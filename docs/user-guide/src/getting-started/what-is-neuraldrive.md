*Audience: Users and decision-makers looking for a conceptual overview of the NeuralDrive platform.*

# What is NeuralDrive

Running large language models locally often requires significant Linux expertise, including managing complex GPU driver installations, orchestrating runtimes like Ollama or llama.cpp, and configuring network security. NeuralDrive removes these barriers by providing a pre-configured, bootable environment that transforms any compatible hardware into a dedicated LLM server.

## Overview

NeuralDrive is a Debian 12-based LiveCD/LiveUSB distribution that boots entirely into RAM. It provides a headless inference environment that is ready to use in less than two minutes. By automating hardware detection and driver loading, it ensures that your NVIDIA, AMD, or Intel GPU is immediately available for model acceleration.

### Key Features

- **Rapid Deployment**: Boot-to-inference in under two minutes.
- **Hardware Autoprobe**: Automatic detection and configuration for NVIDIA (CUDA), AMD (ROCm), and Intel Arc (oneAPI) hardware.
- **Standardized API**: Fully OpenAI-compatible API available at port 8443, allowing immediate connection with popular coding agents and tools.
- **Web-Based Management**: Access a feature-rich dashboard via Open WebUI for model downloading and interactive chatting.
- **Local Management**: A Python-based Textual TUI is available on the local console for system status and network configuration.
- **Persistence Support**: Configurations and downloaded models survive reboots when using a USB drive with a designated "persistence" partition.
- **Customizable**: Includes a toolkit for users to build their own customized system images.

## Architecture

NeuralDrive uses a layered approach to ensure stability and performance across different hardware configurations.

```text
+-------------------------------------------------------+
|                    User Interfaces                    |
|   (Open WebUI Dashboard :443 / TUI Console / API)     |
+-------------------------------------------------------+
|                    Security Layer                     |
|    (Caddy Reverse Proxy / nftables / Bearer Auth)     |
+-------------------------------------------------------+
|                    Runtime Stack                      |
|           (Ollama / llama.cpp advanced)               |
+-------------------------------------------------------+
|                    GPU Compute Layer                  |
|        (NVIDIA CUDA / AMD ROCm / Intel oneAPI)        |
+-------------------------------------------------------+
|                   Operating System                    |
|          (Debian 12 / SquashFS / OverlayFS)           |
+-------------------------------------------------------+
|                    Boot Media                         |
|             (LiveUSB / LiveCD / ISO)                  |
+-------------------------------------------------------+
```

## Design Goals

The development of NeuralDrive is guided by specific performance and usability targets.

| Priority | Goal | Measure |
|----------|------|---------|
| P0 | Boot-to-inference <2min | First API response within 120s of power-on |
| P0 | GPU auto-detection | NVIDIA, AMD, and Intel GPUs work without manual driver installs |
| P0 | OpenAI-compatible API | Popular coding agents connect out of the box |
| P1 | Multiple concurrent models | Load and unload different models without system restarts |
| P1 | USB persistence | Downloaded models and system configs survive reboots |
| P2 | Web dashboard | Full remote management via browser |
| P3 | Custom image toolkit | Provide tools for users to build and sign their own images |

## Use Cases

NeuralDrive is designed for environments where privacy, simplicity, and performance are paramount.

- **Home Labs**: Run private LLMs on consumer hardware without cluttering your primary OS.
- **Developer Workstations**: Quickly spin up an inference server to test local AI-integrated applications.
- **Small Offices**: Provide a shared, local AI resource for a small team over a local network.
- **Air-Gapped Environments**: Deploy AI capabilities to systems with restricted or no internet access by pre-loading models onto the USB media.

## What NeuralDrive is Not

To maintain its focus as a specialized inference tool, NeuralDrive excludes several common features found in other platforms:

- **Not a Cloud Service**: NeuralDrive is local software that runs on your hardware; no data is sent to external servers unless you explicitly configure it.
- **Not Docker-Based**: The entire stack runs directly on the OS for maximum performance and reduced overhead.
- **Not a Desktop OS**: NeuralDrive is a headless server distribution. While it provides a web interface, it does not include a traditional desktop environment like GNOME or KDE.

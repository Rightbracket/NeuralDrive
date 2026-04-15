*Audience: Everyone*

# Glossary

This alphabetical list defines technical terms and concepts utilized throughout the NeuralDrive documentation.

-   **API Key**: A unique authentication token (`nd-xxxx`) used to secure access to the inference and system management APIs.
-   **Avahi**: A system that facilitates service discovery on a local network via mDNS. It allows the `neuraldrive.local` hostname to resolve without a central DNS server.
-   **Caddy**: A high-performance, memory-safe web server that serves as NeuralDrive's reverse proxy, managing TLS encryption and request routing.
-   **CUDA**: NVIDIA's parallel computing platform and programming model that enables hardware acceleration on NVIDIA GPUs.
-   **GGUF**: The primary file format used by NeuralDrive for storing and distributing quantized LLM weights. It is optimized for fast loading and efficient memory usage.
-   **Inference**: The process of using a trained machine learning model to generate an output (e.g., text, images, or embeddings) based on input data.
-   **Live System**: An operating system designed to boot and run entirely from removable media (like a USB drive) without requiring installation to a permanent hard disk.
-   **LUKS**: Linux Unified Key Setup. The standard for Linux disk encryption, used by NeuralDrive to secure data on the persistence partition.
-   **mDNS**: Multicast DNS. A protocol that resolves hostnames in small networks that do not have a dedicated local DNS server.
-   **Ollama**: The underlying inference engine in NeuralDrive that manages downloading, loading, and serving large language models.
-   **Open WebUI**: A feature-rich, self-hosted web interface that provides a user-friendly chat environment for interacting with local LLMs.
-   **Overlayfs**: A union filesystem that allows NeuralDrive to layer a writable storage area (the persistence partition) over a read-only base system.
-   **Persistence**: A dedicated writable partition on the NeuralDrive USB media that stores downloaded models, user accounts, and system configuration between reboots.
-   **Quantization**: The process of reducing the precision of a model's weights (e.g., from 16-bit to 4-bit) to reduce its memory footprint and increase inference speed.
-   **RAG**: Retrieval-Augmented Generation. A technique that combines LLM generation with external data retrieval to improve the accuracy and relevance of responses.
-   **ROCm**: AMD's open-source software stack for GPU computing, enabling hardware acceleration on compatible AMD graphics cards.
-   **SquashFS**: A highly compressed, read-only filesystem used for the base NeuralDrive operating system image.
-   **TUI**: Terminal User Interface. The text-based management console that appears on the physical NeuralDrive device for initial setup and monitoring.
-   **VRAM**: Video RAM. The high-speed memory dedicated to the GPU, which determines the maximum size of the model that can be hardware-accelerated.
-   **zram**: A kernel feature that creates a compressed swap area in system RAM, increasing effective memory capacity for memory-intensive LLM tasks.

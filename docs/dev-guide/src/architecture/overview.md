*This chapter is for contributors and maintainers.*

# System Overview

NeuralDrive is a specialized Linux distribution designed to function as a headless LLM appliance. It prioritizes reliability, security, and ease of use by abstracting the complexities of GPU drivers and model orchestration.

## Runtime Stack

The system follows a layered architecture that moves from low-level hardware management to high-level user interfaces.

```text
+-------------------------------------------------------+
|                    Web Browser (UI)                   |
+-------------------------------------------------------+
                           | (HTTPS)
+-------------------------------------------------------+
|                     Caddy Proxy                       |
|   (TLS, Routing, Authentication, Rate Limiting)       |
+-----------+---------------+-----------+---------------+
            |               |           |
+-----------v-----------+   |   +-------v-------+   +---|---+
|      Open WebUI       |   |   |   System API  |   |  TUI  |
| (Frontend Application)|   |   |   (FastAPI)   |   | (TTY) |
+-----------+-----------+   |   +-------+-------+   +---|---+
            |               |           |               |
+-----------v---------------v-----------v---------------v-------+
|                           Ollama                             |
|              (Inference Engine & Model Manager)              |
+-------------------------------+-------------------------------+
                                |
+-------------------------------v-------------------------------+
|                      GPU Hardware / Drivers                  |
|               (NVIDIA CUDA, AMD ROCm, Intel OneAPI)          |
+---------------------------------------------------------------+
|                        Debian 12 Base                        |
+---------------------------------------------------------------+
```

## Component Roles

### Caddy Proxy
Acts as the secure gateway for the entire appliance. It handles TLS termination using self-signed or ACME-provided certificates. Caddy routes traffic to the appropriate backend service based on the URL path and enforces Bearer token authentication for API requests.

### Ollama
The core inference engine. It manages model lifecycles (downloading, loading, unloading) and provides an OpenAI-compatible API. It is isolated within its own systemd service with restricted device access.

### Open WebUI
A self-contained web interface that communicates with Ollama. It provides a user-friendly environment for chatting with models, managing documents (RAG), and configuring user profiles.

### System API
A custom FastAPI application that provides programmatic control over the appliance. It handles tasks like restarting services, retrieving logs, and updating network configurations.

### Textual TUI
A terminal-based user interface that appears on the physical console. It allows administrators to view system status, networking info, and perform the initial setup wizard without needing a network connection.

## Data Flow

1. **User Request**: An HTTPS request arrives at Caddy on port 443.
2. **Routing**: Caddy determines if the request is for the WebUI (`/`), the inference API (`/v1/`), or the System API (`/system/`).
3. **Authentication**: If the request is for an API endpoint, Caddy verifies the Bearer token.
4. **Backend Processing**: The request is proxied to the relevant local service (e.g., localhost:11434 for Ollama).
5. **Response**: The backend service returns data to Caddy, which then passes it back to the user over the encrypted connection.


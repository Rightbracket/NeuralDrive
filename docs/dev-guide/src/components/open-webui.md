*This chapter is for contributors and maintainers.*

# Open WebUI Integration

Open WebUI provides the primary user interface for NeuralDrive. It is a feature-rich chat environment that communicates with the Ollama backend.

## Installation and Environment

Open WebUI is installed into a Python virtual environment at `/usr/lib/neuraldrive/webui/venv/`. This isolation prevents dependency conflicts with the system Python or the System API.

The service is managed by `neuraldrive-webui.service` and runs as the `neuraldrive-webui` user (UID 902).

## Configuration (webui.env)

Key configuration parameters are stored in `/etc/neuraldrive/webui.env`:
- `OLLAMA_BASE_URL=http://localhost:11434`: The internal address of the Ollama service.
- `DATA_DIR=/var/lib/neuraldrive/webui`: Persistent location for the SQLite database and user uploads.
- `ENABLE_SIGNUP=false`: Disables public account creation for security.
- `WEBUI_AUTH=true`: Enforces login for all users.
- `WEBUI_NAME=NeuralDrive`: Customizes the branding of the interface.

## Service Lifecycle

The WebUI service `Wants=neuraldrive-ollama`. This means systemd will attempt to start Ollama whenever the WebUI is started. However, the WebUI is capable of running even if Ollama is temporarily unavailable, showing a "Connection Error" in the settings.

## Data Persistence

The `/var/lib/neuraldrive/webui` directory contains:
- `webui.db`: The SQLite database containing user accounts, chat history, and settings.
- `uploads/`: Documents uploaded for RAG (Retrieval-Augmented Generation).
- `cache/`: Temporary files and model templates.

## Customization

To modify the default behavior of Open WebUI on NeuralDrive:
1. Update the environment variables in `config/includes.chroot/etc/neuraldrive/webui.env`.
2. For UI changes, the CSS or frontend assets can be modified in the source before building.

> **Note**: Major updates to Open WebUI often require database migrations. These are handled automatically by the application on startup, but it is recommended to back up the `webui.db` file before performing a system upgrade.


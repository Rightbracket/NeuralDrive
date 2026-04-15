# Plan 07: Web Dashboard & Remote Management

NeuralDrive provides a primary web interface for chat and model management, alongside a monitoring dashboard for GPU performance. All traffic is consolidated through Caddy.

## Section 1: Open WebUI Deployment

Open WebUI serves as the primary user interface. It connects to the local Ollama instance and handles user authentication and chat history.

### 1.1 Installation Method
Install Open WebUI into an isolated virtual environment to avoid dependency conflicts.

- **Venv Path**: `/usr/lib/neuraldrive/webui/venv/`
- **Installation**:
  ```bash
  python3 -m venv /usr/lib/neuraldrive/webui/venv
  /usr/lib/neuraldrive/webui/venv/bin/pip install --upgrade pip
  /usr/lib/neuraldrive/webui/venv/bin/pip install open-webui
  ```

### 1.2 Configuration
Configuration is handled via environment variables set in the systemd service.

- `OLLAMA_BASE_URL`: `http://localhost:11434`
- `WEBUI_SECRET_KEY`: Generated during first-boot (stored in `/etc/neuraldrive/webui.secret`)
- `DATA_DIR`: `/var/lib/neuraldrive/webui/` (persistent storage)
- `ENABLE_SIGNUP`: `false` (admin creates users or uses first-boot credentials)
- `DEFAULT_USER_ROLE`: `user`
- `WEBUI_AUTH`: `true`

### 1.3 systemd Service: `neuraldrive-webui.service`
```ini
[Unit]
Description=NeuralDrive Open WebUI Dashboard
After=network.target neuraldrive-ollama.service
Wants=neuraldrive-ollama.service

[Service]
User=neuraldrive-webui
Group=neuraldrive-webui
WorkingDirectory=/var/lib/neuraldrive/webui
EnvironmentFile=/etc/neuraldrive/webui.env
ExecStart=/usr/lib/neuraldrive/webui/venv/bin/open-webui serve
Restart=always
RestartSec=5

# Hardening
ProtectSystem=full
ProtectHome=true
NoNewPrivileges=true
PrivateTmp=true
DeviceAllow=/dev/null rw
ReadOnlyPaths=/usr/lib/neuraldrive/webui
ReadWritePaths=/var/lib/neuraldrive/webui

[Install]
WantedBy=multi-user.target
```

## Section 2: Open WebUI Features Configuration

- **Model Management**: Enabled. Allows pulling, deleting, and creating models.
- **Chat Interface**: Enabled with streaming for real-time inference.
- **RAG**: Enabled. Users can upload documents to `/var/lib/neuraldrive/webui/uploads/`.
- **Tools**: Enabled for function calling.
- **Web Search**: Disabled by default.
- **Image/Voice/Community**: Disabled to maintain focus on headless LLM inference.
- **Admin Panel**: Accessible by the first user (created during setup).

## Section 3: GPU Hot Monitoring Dashboard

NeuralDrive uses GPU Hot (or a lightweight FastAPI wrapper) for real-time telemetry.

### 3.1 Installation
```bash
python3 -m venv /usr/lib/neuraldrive/gpu-monitor/venv
/usr/lib/neuraldrive/gpu-monitor/venv/bin/pip install gpu-hot  # or custom wrapper
```

### 3.2 systemd Service: `neuraldrive-gpu-monitor.service`
```ini
[Unit]
Description=NeuralDrive GPU Monitoring Service
After=neuraldrive-gpu-detect.service

[Service]
User=neuraldrive-monitor
Group=neuraldrive-monitor
SupplementaryGroups=video render
ExecStart=/usr/lib/neuraldrive/gpu-monitor/venv/bin/gpu-hot --port 1312 --host 127.0.0.1
Restart=always

[Install]
WantedBy=multi-user.target
```

## Section 4: Caddy Reverse Proxy Configuration

Caddy handles TLS termination and routes traffic to the appropriate backend service.

### 4.1 Caddyfile: `/etc/neuraldrive/Caddyfile`
```caddy
{
    admin off
    auto_https disable_redirects
}

# Standard Web Dashboard
:443 {
    tls /etc/neuraldrive/tls/server.crt /etc/neuraldrive/tls/server.key

    # Open WebUI
    handle /* {
        reverse_proxy localhost:3000
    }
}

# API and Monitoring
:8443 {
    tls /etc/neuraldrive/tls/server.crt /etc/neuraldrive/tls/server.key

    # OpenAI-compatible API
    handle /v1/* {
        reverse_proxy localhost:11434
    }

    # GPU Monitoring
    handle /monitor/* {
        uri strip_prefix /monitor
        reverse_proxy localhost:1312
    }

    # Ollama Native API
    handle /api/* {
        reverse_proxy localhost:11434
    }

    # System Management API
    handle /system/* {
        uri strip_prefix /system
        reverse_proxy localhost:3001
    }

    # Health check
    handle /health {
        respond "OK" 200
    }
}
```

## Section 5: Dashboard Integration

Access points are unified under the `neuraldrive.local` mDNS hostname.
- **Main UI**: `https://neuraldrive.local/`
- **GPU Metrics**: `https://neuraldrive.local:8443/monitor`
- **API Endpoints**: `https://neuraldrive.local:8443/v1`

Custom CSS is injected into Open WebUI to match the NeuralDrive terminal aesthetic (dark mode, amber/green highlights).

## Section 6: Custom System Management Panel

A lightweight FastAPI app provides a bridge between the web interface and system-level operations.

### 6.1 Features
- Service control (Restart Ollama/WebUI)
- Storage overview (Disk usage of model library)
- System logs (View last 50 lines of journalctl)
- Network status

### 6.2 Implementation (Skeleton)
```python
from fastapi import FastAPI
import subprocess

app = FastAPI()

@app.get("/status")
def get_status():
    return {"status": "running", "version": "0.1.0"}

@app.post("/services/{name}/restart")
def restart_service(name: str):
    # Only allow neuraldrive-* services
    if not name.startswith("neuraldrive-"):
        return {"error": "Unauthorized"}
    subprocess.run(["systemctl", "restart", name])
    return {"message": f"Restarting {name}"}
```
This service runs on port 3001 as `neuraldrive-system-api.service`.

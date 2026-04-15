# Plan 08: API Layer, Remote Access & Networking

NeuralDrive provides both industry-standard (OpenAI-compatible) and native APIs for remote model inference and system management. All external access is protected via TLS and authentication.

## Section 1: API Architecture

- **Public Facing**: Port `8443` (TLS terminated by Caddy)
- **Authentication**: `Bearer <API_KEY>` (Shared between Open WebUI, Ollama proxy, and System API)
- **Internal Only**: Ports `11434` (Ollama), `3000` (WebUI), `3001` (System API)
- **Encryption**: Automatic self-signed certificates for `neuraldrive.local`, or user-provided certs.

## Section 2: OpenAI-Compatible API

- **Proxy Route**: `https://neuraldrive.local:8443/v1/`
- **Authentication**: Key generated during first-boot (stored in `/etc/neuraldrive/api.key`)

### 2.1 Usage Example (Python OpenAI SDK)
```python
from openai import OpenAI
import httpx

# Option 1: Trust the NeuralDrive CA certificate (recommended)
# First, copy the CA cert from NeuralDrive:
#   scp neuraldrive-admin@neuraldrive.local:/etc/neuraldrive/tls/neuraldrive-ca.crt .
# Or download via: https://neuraldrive.local:8443/system/ca-cert
client = OpenAI(
    base_url="https://neuraldrive.local:8443/v1",
    api_key="nd-xxxxxxxxxxxxxxxxxxxx",
    http_client=httpx.Client(verify="/path/to/neuraldrive-ca.crt")
)

# Option 2: Use environment variable (applies globally)
# export REQUESTS_CA_BUNDLE=/path/to/neuraldrive-ca.crt
# export SSL_CERT_FILE=/path/to/neuraldrive-ca.crt

# Option 3: Disable verification (NOT recommended for production)
# client = OpenAI(
#     base_url="https://neuraldrive.local:8443/v1",
#     api_key="nd-xxxxxxxxxxxxxxxxxxxx",
#     http_client=httpx.Client(verify=False)
# )

response = client.chat.completions.create(
    model="llama3.1:8b",
    messages=[{"role": "user", "content": "Hello!"}],
    stream=True
)

for chunk in response:
    print(chunk.choices[0].delta.content or "", end="")
```

### 2.2 Quick Testing (curl)
```bash
# With CA certificate trust (recommended):
curl --cacert /path/to/neuraldrive-ca.crt \
  -X POST https://neuraldrive.local:8443/v1/chat/completions \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1:8b",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'

# Without cert verification (quick test only):
curl -k -X POST https://neuraldrive.local:8443/v1/chat/completions \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1:8b",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## Section 3: Ollama Native API

The native Ollama API is exposed via `/api/` on port `8443` for administrative tasks.

### 3.1 Model Management Examples
- **Pull Model**: `curl -k -X POST https://neuraldrive.local:8443/api/pull -d '{"name": "mistral"}'`
- **List Models**: `curl -k -X GET https://neuraldrive.local:8443/api/tags`
- **Show Model**: `curl -k -X POST https://neuraldrive.local:8443/api/show -d '{"name": "llama3.1:8b"}'`

## Section 4: NeuralDrive Management API

A custom FastAPI service (`neuraldrive-system-api`) manages system-level tasks. This is the canonical API definition — 07-web-interface.md §6 references this section.

### 4.1 systemd Service: `neuraldrive-system-api.service`
```ini
[Unit]
Description=NeuralDrive System Management API
After=network.target

[Service]
User=neuraldrive-api
Group=neuraldrive-api
EnvironmentFile=/etc/neuraldrive/api.env
ExecStart=/usr/lib/neuraldrive/api/venv/bin/uvicorn neuraldrive_api.main:app --host 127.0.0.1 --port 3001
Restart=always
RestartSec=5
WorkingDirectory=/usr/lib/neuraldrive/api

# Hardening
ProtectSystem=full
ProtectHome=true
NoNewPrivileges=true
PrivateTmp=true
ReadWritePaths=/etc/neuraldrive /var/log/neuraldrive /var/lib/neuraldrive

[Install]
WantedBy=multi-user.target
```

### 4.2 Authentication
```python
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import subprocess
import psutil
import shutil
import json

app = FastAPI(title="NeuralDrive System API", version="1.0.0")
auth_scheme = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(auth_scheme)):
    with open("/etc/neuraldrive/api.key", "r") as f:
        valid_key = f.read().strip()
    if credentials.credentials != valid_key:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return credentials.credentials
```

### 4.3 Endpoint Reference

All endpoints require `Authorization: Bearer <API_KEY>` via the `verify_token` dependency.

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/system/status` | System overview (CPU, RAM, disk, uptime) |
| GET | `/system/logs` | Service log tailing |
| GET | `/system/services` | List all neuraldrive-* services and their status |
| POST | `/system/services/{name}/restart` | Restart a neuraldrive-* service |
| POST | `/system/services/{name}/{action}` | Start/stop a neuraldrive-* service |
| GET | `/system/storage` | Disk usage breakdown (models, configs, logs) |
| GET | `/system/network` | Network interfaces, IP, mDNS status |
| POST | `/system/network/hostname` | Set hostname |
| GET | `/system/gpu` | GPU info, VRAM usage, temperature |
| POST | `/system/ssh/{action}` | Enable/disable SSH |
| GET | `/system/security` | Firewall status, TLS cert info, SSH status |
| POST | `/system/api-keys/rotate` | Rotate the API key |
| GET | `/system/ca-cert` | Download the CA certificate for client trust |

### 4.4 Implementation Skeleton
```python
# --- System Status ---
@app.get("/system/status", dependencies=[Depends(verify_token)])
def get_system_status():
    return {
        "hostname": subprocess.check_output(["hostname"]).decode().strip(),
        "cpu_percent": psutil.cpu_percent(),
        "memory": {
            "total_gb": round(psutil.virtual_memory().total / (1024**3), 1),
            "used_percent": psutil.virtual_memory().percent,
        },
        "disk": {
            "models": shutil.disk_usage("/var/lib/neuraldrive/models")._asdict(),
            "total": shutil.disk_usage("/var/lib/neuraldrive")._asdict(),
        },
        "uptime_seconds": int(psutil.boot_time()),
        "version": open("/etc/neuraldrive/version").read().strip() if os.path.exists("/etc/neuraldrive/version") else "dev",
    }

# --- Service Management ---
ALLOWED_SERVICES = [
    "neuraldrive-ollama", "neuraldrive-webui", "neuraldrive-caddy",
    "neuraldrive-gpu-monitor", "neuraldrive-system-api", "neuraldrive-certs",
]

@app.get("/system/services", dependencies=[Depends(verify_token)])
def list_services():
    results = []
    for svc in ALLOWED_SERVICES:
        status = subprocess.run(
            ["systemctl", "is-active", svc], capture_output=True, text=True
        )
        results.append({"name": svc, "status": status.stdout.strip()})
    return {"services": results}

@app.post("/system/services/{name}/restart", dependencies=[Depends(verify_token)])
def restart_service(name: str):
    if name not in ALLOWED_SERVICES:
        raise HTTPException(status_code=403, detail=f"Service '{name}' not in allowlist")
    subprocess.run(["systemctl", "restart", name], check=True)
    return {"message": f"Restarted {name}"}

@app.post("/system/services/{name}/{action}", dependencies=[Depends(verify_token)])
def service_action(name: str, action: str):
    if name not in ALLOWED_SERVICES:
        raise HTTPException(status_code=403, detail=f"Service '{name}' not in allowlist")
    if action not in ("start", "stop"):
        raise HTTPException(status_code=400, detail="Action must be 'start' or 'stop'")
    subprocess.run(["systemctl", action, name], check=True)
    return {"message": f"{action.capitalize()}ed {name}"}

# --- Logs ---
@app.get("/system/logs", dependencies=[Depends(verify_token)])
def get_logs(service: str = "ollama", lines: int = 50):
    if not service.startswith("neuraldrive-"):
        service = f"neuraldrive-{service}"
    if service not in ALLOWED_SERVICES:
        raise HTTPException(status_code=403, detail="Service not in allowlist")
    res = subprocess.run(
        ["journalctl", "-u", service, "-n", str(min(lines, 500)), "--no-pager"],
        capture_output=True, text=True,
    )
    return {"service": service, "lines": res.stdout.splitlines()}

# --- Storage ---
@app.get("/system/storage", dependencies=[Depends(verify_token)])
def get_storage():
    models_usage = shutil.disk_usage("/var/lib/neuraldrive/models")
    return {
        "models": {
            "total_gb": round(models_usage.total / (1024**3), 1),
            "used_gb": round(models_usage.used / (1024**3), 1),
            "free_gb": round(models_usage.free / (1024**3), 1),
            "percent": round(models_usage.used / models_usage.total * 100, 1),
        },
        "persistence": shutil.disk_usage("/var/lib/neuraldrive")._asdict(),
    }

# --- Network ---
@app.get("/system/network", dependencies=[Depends(verify_token)])
def get_network():
    interfaces = psutil.net_if_addrs()
    result = {}
    for iface, addrs in interfaces.items():
        for addr in addrs:
            if addr.family.name == "AF_INET":
                result[iface] = {"ip": addr.address, "netmask": addr.netmask}
    return {
        "interfaces": result,
        "hostname": subprocess.check_output(["hostname"]).decode().strip(),
        "mdns": "neuraldrive.local",
    }

@app.post("/system/network/hostname", dependencies=[Depends(verify_token)])
def set_hostname(hostname: str):
    subprocess.run(["hostnamectl", "set-hostname", hostname], check=True)
    return {"message": f"Hostname set to {hostname}"}

# --- GPU ---
@app.get("/system/gpu", dependencies=[Depends(verify_token)])
def get_gpu():
    gpu_conf = "/run/neuraldrive/gpu.conf"
    info = {"vendor": "unknown", "devices": []}
    if os.path.exists(gpu_conf):
        with open(gpu_conf) as f:
            for line in f:
                if line.startswith("VENDOR="):
                    info["vendor"] = line.strip().split("=")[1]
    # NVIDIA details via nvidia-smi
    if info["vendor"] == "NVIDIA":
        try:
            res = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total,memory.used,temperature.gpu",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, check=True,
            )
            for line in res.stdout.strip().splitlines():
                parts = [p.strip() for p in line.split(",")]
                info["devices"].append({
                    "name": parts[0], "vram_total_mb": int(parts[1]),
                    "vram_used_mb": int(parts[2]), "temp_c": int(parts[3]),
                })
        except Exception:
            pass
    return info

# --- SSH ---
@app.post("/system/ssh/{action}", dependencies=[Depends(verify_token)])
def manage_ssh(action: str):
    if action not in ("enable", "disable"):
        raise HTTPException(status_code=400, detail="Action must be 'enable' or 'disable'")
    cmd = "start" if action == "enable" else "stop"
    subprocess.run(["systemctl", cmd, "ssh"], check=True)
    return {"message": f"SSH {action}d"}

# --- Security ---
@app.get("/system/security", dependencies=[Depends(verify_token)])
def get_security():
    ssh_active = subprocess.run(
        ["systemctl", "is-active", "ssh"], capture_output=True, text=True
    ).stdout.strip() == "active"
    cert_exists = os.path.exists("/etc/neuraldrive/tls/server.crt")
    return {
        "ssh_enabled": ssh_active,
        "tls_configured": cert_exists,
        "firewall": "nftables",
    }

# --- API Key Rotation ---
@app.post("/system/api-keys/rotate", dependencies=[Depends(verify_token)])
def rotate_api_key():
    import secrets
    new_key = f"nd-{secrets.token_hex(16)}"
    with open("/etc/neuraldrive/api.key", "w") as f:
        f.write(new_key)
    # Update Caddy env and reload
    with open("/etc/neuraldrive/caddy.env", "w") as f:
        f.write(f"NEURALDRIVE_API_KEY={new_key}\n")
    subprocess.run(["systemctl", "reload", "neuraldrive-caddy"])
    return {"message": "API key rotated", "new_key": new_key}

# --- CA Certificate Download ---
@app.get("/system/ca-cert")
def download_ca_cert():
    from fastapi.responses import FileResponse
    cert_path = "/etc/neuraldrive/tls/neuraldrive-ca.crt"
    if not os.path.exists(cert_path):
        raise HTTPException(status_code=404, detail="CA certificate not found")
    return FileResponse(cert_path, media_type="application/x-pem-file", filename="neuraldrive-ca.crt")
```

## Section 5: Network Configuration & Service Discovery

### 5.1 mDNS (Avahi) Announcement
Avahi advertises NeuralDrive on the local network so it is reachable at `neuraldrive.local`.

- **File**: `/etc/avahi/services/neuraldrive-web.service`
  ```xml
  <service-group>
    <name replace-wildcards="yes">NeuralDrive Web UI</name>
    <service>
      <type>_http._tcp</type>
      <port>443</port>
    </service>
  </service-group>
  ```
- **File**: `/etc/avahi/services/neuraldrive-api.service`
  ```xml
  <service-group>
    <name replace-wildcards="yes">NeuralDrive LLM API</name>
    <service>
      <type>_llm._tcp</type>
      <port>8443</port>
    </service>
  </service-group>
  ```

### 5.2 Network Stack
- **Manager**: `NetworkManager` for both wired and wireless interfaces.
- **Firewall**: `nftables` (Blocking everything except 443, 8443, and SSH if enabled).
- **Resolver**: `systemd-resolved` with mDNS support.

## Section 6: Client Configuration Guide

### 6.1 Coding Agents (Cursor/Continue/IDE)
- **Provider**: OpenAI Compatible
- **Base URL**: `https://neuraldrive.local:8443/v1`
- **API Key**: `nd-xxxxxxxxxxxxxxxxxxxx` (From TUI or `/etc/neuraldrive/api.key`)

### 6.2 CLI (Ollama Binary)
If the user has the `ollama` CLI installed locally:
```bash
OLLAMA_HOST=https://neuraldrive.local:8443 ollama run llama3.1:8b
```
*(Note: Requires the self-signed cert to be trusted or `-k` equivalent depending on client).*

## Section 7: Performance & Reliability

- **Request Timeouts**:
  - Generation: 600s (allows for deep reasoning model outputs)
  - Management: 30s
- **Caddy Backend Connection Pooling**: Configured for high-throughput model inference.
- **Health Checks**: Caddy periodically checks `localhost:11434` and `localhost:3000`. If they are down, a 503 response with a "System Initializing" message is returned.
- **Rate Limiting**: 100 requests per minute per source IP for the API endpoints to prevent accidental DOS from misconfigured loops.

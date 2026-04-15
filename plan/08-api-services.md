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

A custom FastAPI service (`neuraldrive-api`) manages system-level tasks.

### 4.1 FastAPI Implementation Skeleton
```python
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import subprocess
import psutil
import shutil

app = FastAPI(title="NeuralDrive System API")
auth_scheme = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(auth_scheme)):
    with open("/etc/neuraldrive/api.key", "r") as f:
        valid_key = f.read().strip()
    if credentials.credentials != valid_key:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return credentials.credentials

@app.get("/system/status", dependencies=[Depends(verify_token)])
def get_system_status():
    return {
        "hostname": "neuraldrive",
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": shutil.disk_usage("/var/lib/neuraldrive/models")
    }

@app.get("/system/logs", dependencies=[Depends(verify_token)])
def get_logs(service: str = "ollama"):
    # Limit to neuraldrive-* services
    if not service.startswith("neuraldrive-"):
         service = f"neuraldrive-{service}"
    res = subprocess.run(["journalctl", "-u", service, "-n", "50", "--no-pager"], capture_output=True, text=True)
    return {"logs": res.stdout}

@app.post("/system/ssh/{action}", dependencies=[Depends(verify_token)])
def manage_ssh(action: str):
    if action not in ["enable", "disable"]:
        raise HTTPException(status_code=400, detail="Invalid action")
    cmd = "start" if action == "enable" else "stop"
    subprocess.run(["systemctl", cmd, "ssh"])
    return {"message": f"SSH {action}d"}
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

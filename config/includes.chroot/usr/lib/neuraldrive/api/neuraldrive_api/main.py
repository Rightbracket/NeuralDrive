import os
import secrets
import subprocess
import shutil
import time
from pathlib import Path

import psutil
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

VERSION_FILE = "/etc/neuraldrive/version"


def _read_version() -> str:
    if os.path.exists(VERSION_FILE):
        return Path(VERSION_FILE).read_text().strip()
    return "dev"


app = FastAPI(title="NeuralDrive System API", version=_read_version())
auth_scheme = HTTPBearer()

API_KEY_PATH = "/etc/neuraldrive/api.key"
CERT_DIR = "/etc/neuraldrive/tls"
GPU_CONF = "/run/neuraldrive/gpu.conf"
MODELS_DIR = "/var/lib/neuraldrive/models"
DATA_DIR = "/var/lib/neuraldrive"

ALLOWED_SERVICES = [
    "neuraldrive-ollama",
    "neuraldrive-webui",
    "neuraldrive-caddy",
    "neuraldrive-gpu-monitor",
    "neuraldrive-system-api",
    "neuraldrive-certs",
]


def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(auth_scheme),
) -> str:
    if not os.path.exists(API_KEY_PATH):
        raise HTTPException(status_code=503, detail="API key not configured")
    valid_key = Path(API_KEY_PATH).read_text().strip()
    if credentials.credentials != valid_key:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return credentials.credentials


def _read_gpu_conf() -> dict[str, str]:
    conf: dict[str, str] = {}
    if os.path.exists(GPU_CONF):
        for line in Path(GPU_CONF).read_text().splitlines():
            if "=" in line:
                k, v = line.strip().split("=", 1)
                conf[k] = v
    return conf


def _systemctl(action: str, service: str) -> str:
    result = subprocess.run(
        ["systemctl", action, service],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


@app.get("/system/status", dependencies=[Depends(verify_token)])
def get_system_status():
    mem = psutil.virtual_memory()
    version = "dev"
    if os.path.exists(VERSION_FILE):
        version = Path(VERSION_FILE).read_text().strip()

    models_usage = shutil.disk_usage(MODELS_DIR) if os.path.exists(MODELS_DIR) else None
    total_usage = shutil.disk_usage(DATA_DIR) if os.path.exists(DATA_DIR) else None

    return {
        "hostname": subprocess.check_output(["hostname"]).decode().strip(),
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "cpu_count": psutil.cpu_count(logical=True),
        "memory": {
            "total_gb": round(mem.total / (1024**3), 1),
            "used_gb": round(mem.used / (1024**3), 1),
            "used_percent": mem.percent,
        },
        "disk": {
            "models": models_usage._asdict() if models_usage else None,
            "total": total_usage._asdict() if total_usage else None,
        },
        "uptime_seconds": int(time.time() - psutil.boot_time()),
        "version": version,
    }


@app.get("/system/services", dependencies=[Depends(verify_token)])
def list_services():
    results = []
    for svc in ALLOWED_SERVICES:
        status = _systemctl("is-active", svc)
        uptime = ""
        if status == "active":
            prop = subprocess.run(
                ["systemctl", "show", svc, "--property=ActiveEnterTimestamp"],
                capture_output=True,
                text=True,
            )
            uptime = prop.stdout.strip().split("=", 1)[-1] if "=" in prop.stdout else ""
        results.append({"name": svc, "status": status, "since": uptime})
    return {"services": results}


@app.post("/system/services/{name}/restart", dependencies=[Depends(verify_token)])
def restart_service(name: str):
    if name not in ALLOWED_SERVICES:
        raise HTTPException(
            status_code=403, detail=f"Service '{name}' not in allowlist"
        )
    subprocess.run(["systemctl", "restart", name], check=True)
    return {"message": f"Restarted {name}"}


@app.post("/system/services/{name}/{action}", dependencies=[Depends(verify_token)])
def service_action(name: str, action: str):
    if name not in ALLOWED_SERVICES:
        raise HTTPException(
            status_code=403, detail=f"Service '{name}' not in allowlist"
        )
    if action not in ("start", "stop"):
        raise HTTPException(status_code=400, detail="Action must be 'start' or 'stop'")
    subprocess.run(["systemctl", action, name], check=True)
    return {"message": f"{action.capitalize()}ed {name}"}


@app.get("/system/logs", dependencies=[Depends(verify_token)])
def get_logs(service: str = "ollama", lines: int = 50, level: str = ""):
    if not service.startswith("neuraldrive-"):
        service = f"neuraldrive-{service}"
    if service not in ALLOWED_SERVICES:
        raise HTTPException(status_code=403, detail="Service not in allowlist")
    capped_lines = min(lines, 500)
    cmd = ["journalctl", "-u", service, "-n", str(capped_lines), "--no-pager"]
    if level:
        cmd.extend(["-p", level])
    res = subprocess.run(cmd, capture_output=True, text=True)
    return {"service": service, "lines": res.stdout.splitlines()}


@app.get("/system/storage", dependencies=[Depends(verify_token)])
def get_storage():
    result: dict = {"persistence": None, "models": None}
    if os.path.exists(MODELS_DIR):
        mu = shutil.disk_usage(MODELS_DIR)
        result["models"] = {
            "total_gb": round(mu.total / (1024**3), 1),
            "used_gb": round(mu.used / (1024**3), 1),
            "free_gb": round(mu.free / (1024**3), 1),
            "percent": round(mu.used / mu.total * 100, 1) if mu.total > 0 else 0,
        }
    if os.path.exists(DATA_DIR):
        result["persistence"] = shutil.disk_usage(DATA_DIR)._asdict()
    return result


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
    if not hostname or len(hostname) > 63:
        raise HTTPException(status_code=400, detail="Hostname must be 1-63 characters")
    subprocess.run(["hostnamectl", "set-hostname", hostname], check=True)
    return {"message": f"Hostname set to {hostname}"}


@app.get("/system/gpu", dependencies=[Depends(verify_token)])
def get_gpu():
    conf = _read_gpu_conf()
    info: dict = {"vendor": conf.get("VENDOR", "unknown"), "devices": []}

    if info["vendor"] == "NVIDIA":
        try:
            res = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=name,memory.total,memory.used,temperature.gpu,utilization.gpu",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            for line in res.stdout.strip().splitlines():
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 5:
                    info["devices"].append(
                        {
                            "name": parts[0],
                            "vram_total_mb": int(parts[1]),
                            "vram_used_mb": int(parts[2]),
                            "temp_c": int(parts[3]),
                            "utilization_percent": int(parts[4]),
                        }
                    )
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    return info


@app.post("/system/ssh/{action}", dependencies=[Depends(verify_token)])
def manage_ssh(action: str):
    if action not in ("enable", "disable"):
        raise HTTPException(
            status_code=400, detail="Action must be 'enable' or 'disable'"
        )
    cmd = "start" if action == "enable" else "stop"
    subprocess.run(["systemctl", cmd, "ssh"], check=True)
    if action == "enable":
        subprocess.run(["systemctl", "enable", "ssh"], check=False)
    else:
        subprocess.run(["systemctl", "disable", "ssh"], check=False)
    return {"message": f"SSH {action}d"}


@app.get("/system/security", dependencies=[Depends(verify_token)])
def get_security():
    ssh_active = _systemctl("is-active", "ssh") == "active"
    cert_exists = os.path.exists(f"{CERT_DIR}/server.crt")
    cert_expiry = ""
    if cert_exists:
        try:
            res = subprocess.run(
                [
                    "openssl",
                    "x509",
                    "-enddate",
                    "-noout",
                    "-in",
                    f"{CERT_DIR}/server.crt",
                ],
                capture_output=True,
                text=True,
            )
            cert_expiry = (
                res.stdout.strip().split("=", 1)[-1] if "=" in res.stdout else ""
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    return {
        "ssh_enabled": ssh_active,
        "tls_configured": cert_exists,
        "tls_expiry": cert_expiry,
        "firewall": "nftables",
    }


@app.post("/system/api-keys/rotate", dependencies=[Depends(verify_token)])
def rotate_api_key():
    new_key = f"nd-{secrets.token_hex(16)}"
    Path(API_KEY_PATH).write_text(new_key)
    caddy_env_path = Path("/etc/neuraldrive/caddy.env")
    caddy_env_path.write_text(f"NEURALDRIVE_API_KEY={new_key}\n")
    subprocess.run(["systemctl", "reload", "neuraldrive-caddy"], check=False)
    return {"message": "API key rotated", "new_key": new_key}


@app.get("/system/ca-cert")
def download_ca_cert():
    cert_path = f"{CERT_DIR}/neuraldrive-ca.crt"
    if not os.path.exists(cert_path):
        raise HTTPException(status_code=404, detail="CA certificate not found")
    return FileResponse(
        cert_path,
        media_type="application/x-pem-file",
        filename="neuraldrive-ca.crt",
    )

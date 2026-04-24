from __future__ import annotations

import subprocess
import psutil
import os


def get_cpu_percent() -> float:
    return psutil.cpu_percent(interval=0)


def get_memory_info() -> dict:
    mem = psutil.virtual_memory()
    return {
        "total_gb": round(mem.total / (1024**3), 1),
        "used_gb": round(mem.used / (1024**3), 1),
        "percent": mem.percent,
    }


def get_disk_info() -> dict:
    paths_to_check = ["/var/lib/neuraldrive", "/"]
    for path in paths_to_check:
        if os.path.exists(path):
            usage = psutil.disk_usage(path)
            return {
                "path": path,
                "total_gb": round(usage.total / (1024**3), 1),
                "used_gb": round(usage.used / (1024**3), 1),
                "free_gb": round(usage.free / (1024**3), 1),
                "percent": usage.percent,
            }
    return {"path": "/", "total_gb": 0, "used_gb": 0, "free_gb": 0, "percent": 0}


def get_gpu_info() -> dict:
    conf_path = "/run/neuraldrive/gpu.conf"
    info: dict = {"vendor": "CPU", "devices": []}
    if os.path.exists(conf_path):
        for line in open(conf_path):
            if line.startswith("VENDOR="):
                info["vendor"] = line.strip().split("=", 1)[1]

    if info["vendor"] == "NVIDIA":
        try:
            res = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=name,memory.total,memory.used,temperature.gpu,utilization.gpu,fan.speed",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if res.returncode == 0:
                for line in res.stdout.strip().splitlines():
                    parts = [p.strip() for p in line.split(",")]
                    if len(parts) >= 5:
                        info["devices"].append(
                            {
                                "name": parts[0],
                                "vram_total_mb": int(parts[1]),
                                "vram_used_mb": int(parts[2]),
                                "temp_c": int(parts[3]),
                                "util_percent": int(parts[4]),
                                "fan_percent": int(parts[5])
                                if len(parts) > 5 and parts[5].isdigit()
                                else 0,
                            }
                        )
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
            pass

    elif info["vendor"] == "AMD":
        try:
            res = subprocess.run(
                [
                    "rocm-smi",
                    "--showproductname",
                    "--showtemp",
                    "--showmeminfo",
                    "vram",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if res.returncode == 0:
                info["raw_output"] = res.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    return info


def get_uptime() -> str:
    boot = psutil.boot_time()
    import time

    elapsed = int(time.time() - boot)
    hours, remainder = divmod(elapsed, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours}h {minutes}m"


def get_ip_address() -> str:
    try:
        addrs = psutil.net_if_addrs()
        for iface, addr_list in addrs.items():
            if iface == "lo":
                continue
            for addr in addr_list:
                if addr.family.name == "AF_INET" and not addr.address.startswith(
                    "127."
                ):
                    return addr.address
    except Exception:
        pass
    return "no network"


def get_hostname() -> str:
    try:
        return subprocess.check_output(["hostname"], timeout=3).decode().strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return "neuraldrive"


def get_service_status(service: str) -> str:
    try:
        res = subprocess.run(
            ["systemctl", "is-active", service],
            capture_output=True,
            text=True,
            timeout=3,
        )
        return res.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return "unknown"


NEURALDRIVE_SERVICES = [
    "neuraldrive-ollama",
    "neuraldrive-webui",
    "neuraldrive-caddy",
    "neuraldrive-gpu-monitor",
    "neuraldrive-system-api",
]


def get_boot_device() -> str | None:
    try:
        with open("/proc/cmdline") as f:
            cmdline = f.read()
        for part in cmdline.split():
            if part.startswith("boot=live") or part.startswith("root="):
                pass
            if part.startswith("live-media="):
                media_dev = part.split("=", 1)[1]
                pkname_res = subprocess.run(
                    ["lsblk", "-no", "PKNAME", media_dev],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if pkname_res.returncode == 0 and pkname_res.stdout.strip():
                    return f"/dev/{pkname_res.stdout.strip()}"
                # PKNAME failed — fall through to findmnt instead of
                # returning an unvalidated partition/symlink path.
        res = subprocess.run(
            ["findmnt", "-n", "-o", "SOURCE", "/run/live/medium"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if res.returncode == 0 and res.stdout.strip():
            part_dev = res.stdout.strip()
            pkname_res = subprocess.run(
                ["lsblk", "-no", "PKNAME", part_dev],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if pkname_res.returncode == 0 and pkname_res.stdout.strip():
                return f"/dev/{pkname_res.stdout.strip()}"
    except (OSError, subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def get_disk_partitions(device: str) -> list[dict]:
    try:
        res = subprocess.run(
            ["lsblk", "-J", "-b", "-o", "NAME,SIZE,FSTYPE,LABEL,MOUNTPOINT", device],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if res.returncode != 0:
            return []
        import json

        data = json.loads(res.stdout)
        partitions = []
        for bd in data.get("blockdevices", []):
            for child in bd.get("children", []):
                partitions.append(
                    {
                        "name": child.get("name", ""),
                        "size_bytes": int(child.get("size", 0)),
                        "fstype": child.get("fstype", ""),
                        "label": child.get("label", ""),
                        "mountpoint": child.get("mountpoint", ""),
                    }
                )
            if not bd.get("children"):
                partitions.append(
                    {
                        "name": bd.get("name", ""),
                        "size_bytes": int(bd.get("size", 0)),
                        "fstype": bd.get("fstype", ""),
                        "label": bd.get("label", ""),
                        "mountpoint": bd.get("mountpoint", ""),
                    }
                )
        return partitions
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        return []


def get_device_size(device: str) -> int:
    try:
        res = subprocess.run(
            ["lsblk", "-b", "-d", "-n", "-o", "SIZE", device],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if res.returncode == 0:
            return int(res.stdout.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        pass
    return 0


def get_unpartitioned_space(device: str) -> int:
    total = get_device_size(device)
    if not total:
        return 0
    parts = get_disk_partitions(device)
    used = sum(p["size_bytes"] for p in parts)
    free = total - used
    return max(0, free)

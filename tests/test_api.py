import httpx
import pytest

API_URL = "http://localhost:11434/v1"
SYSTEM_API_URL = "http://localhost:3001"


def test_ollama_health():
    response = httpx.get("http://localhost:11434/api/tags", timeout=10.0)
    assert response.status_code == 200


def test_ollama_models_list():
    response = httpx.get(f"{API_URL}/models", timeout=10.0)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_chat_completion():
    payload = {
        "model": "phi3:mini",
        "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
        "stream": False,
    }
    response = httpx.post(f"{API_URL}/chat/completions", json=payload, timeout=120.0)
    assert response.status_code == 200
    data = response.json()
    assert "choices" in data
    assert len(data["choices"]) > 0


def test_system_status_requires_auth():
    response = httpx.get(f"{SYSTEM_API_URL}/system/status", timeout=10.0)
    assert response.status_code in (401, 403)


def test_system_status_with_auth():
    key = open("/etc/neuraldrive/api.key").read().strip()
    response = httpx.get(
        f"{SYSTEM_API_URL}/system/status",
        headers={"Authorization": f"Bearer {key}"},
        timeout=10.0,
    )
    assert response.status_code == 200
    data = response.json()
    assert "hostname" in data
    assert "cpu_percent" in data
    assert "memory" in data


def test_system_services_list():
    key = open("/etc/neuraldrive/api.key").read().strip()
    response = httpx.get(
        f"{SYSTEM_API_URL}/system/services",
        headers={"Authorization": f"Bearer {key}"},
        timeout=10.0,
    )
    assert response.status_code == 200
    data = response.json()
    assert "services" in data
    service_names = [s["name"] for s in data["services"]]
    assert "neuraldrive-ollama" in service_names

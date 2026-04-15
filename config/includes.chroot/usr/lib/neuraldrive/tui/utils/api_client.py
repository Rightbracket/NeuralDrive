from __future__ import annotations

import httpx


OLLAMA_URL = "http://localhost:11434"
TIMEOUT = httpx.Timeout(10.0, read=120.0)


async def ollama_available() -> bool:
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(3.0)) as client:
            resp = await client.get(f"{OLLAMA_URL}/api/tags")
            return resp.status_code == 200
    except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPError):
        return False


async def list_models() -> list[dict]:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(f"{OLLAMA_URL}/api/tags")
            resp.raise_for_status()
            return resp.json().get("models", [])
    except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPError):
        return []


async def list_running_models() -> list[dict]:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(f"{OLLAMA_URL}/api/ps")
            resp.raise_for_status()
            return resp.json().get("models", [])
    except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPError):
        return []


async def pull_model(name: str):
    async with httpx.AsyncClient(timeout=httpx.Timeout(10.0, read=600.0)) as client:
        async with client.stream(
            "POST", f"{OLLAMA_URL}/api/pull", json={"name": name}
        ) as resp:
            async for line in resp.aiter_lines():
                yield line


async def delete_model(name: str) -> bool:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.delete(f"{OLLAMA_URL}/api/delete", json={"name": name})
            return resp.status_code == 200
    except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPError):
        return False


async def chat_stream(model: str, messages: list[dict]):
    payload = {"model": model, "messages": messages, "stream": True}
    async with httpx.AsyncClient(timeout=httpx.Timeout(10.0, read=600.0)) as client:
        async with client.stream(
            "POST", f"{OLLAMA_URL}/api/chat", json=payload
        ) as resp:
            async for line in resp.aiter_lines():
                yield line

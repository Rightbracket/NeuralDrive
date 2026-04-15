from __future__ import annotations

import json

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Static

from utils import api_client
from widgets.model_item import ModelItem


class ModelsScreen(Screen):
    BINDINGS = [("r", "refresh", "Refresh")]

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll():
            yield Static("Installed Models", classes="heading")
            yield Vertical(id="model-list")
            yield Static("", id="model-status")
            yield Static("Pull Model", classes="heading")
            yield Input(placeholder="e.g. llama3:8b", id="pull-input")
            yield Button("Pull", variant="primary", id="pull-btn", classes="primary")
        yield Footer()

    def on_mount(self) -> None:
        self.action_refresh()

    def action_refresh(self) -> None:
        self.app.call_later(self._load_models)

    async def _load_models(self) -> None:
        all_models = await api_client.list_models()
        running = await api_client.list_running_models()
        running_names = {m.get("name", "") for m in running}

        container = self.query_one("#model-list", Vertical)
        container.remove_children()

        if not all_models:
            container.mount(Static("  No models installed", classes="muted"))
            return

        for m in all_models:
            name = m.get("name", "unknown")
            size_bytes = m.get("size", 0)
            size_str = f"{size_bytes / (1024**3):.1f} GB" if size_bytes else "—"
            loaded = name in running_names
            container.mount(ModelItem(name, size_str, loaded))

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "pull-btn":
            await self._pull_model()

    async def _pull_model(self) -> None:
        name_input = self.query_one("#pull-input", Input)
        model_name = name_input.value.strip()
        if not model_name:
            return

        status = self.query_one("#model-status", Static)
        status.update(f"Pulling {model_name}...")

        try:
            async for line in api_client.pull_model(model_name):
                try:
                    data = json.loads(line)
                    msg = data.get("status", "")
                    total = data.get("total", 0)
                    completed = data.get("completed", 0)
                    if total:
                        pct = int(completed / total * 100)
                        status.update(f"{msg}  {pct}%")
                    else:
                        status.update(msg)
                except json.JSONDecodeError:
                    pass
            status.update(f"✓ {model_name} pulled successfully")
            name_input.value = ""
            await self._load_models()
        except Exception as exc:
            status.update(f"✗ Pull failed: {exc}")

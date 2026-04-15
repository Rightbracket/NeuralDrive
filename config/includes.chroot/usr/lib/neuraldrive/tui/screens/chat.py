from __future__ import annotations

import json

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, RichLog, Select, Static

from utils import api_client


class ChatScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def __init__(self) -> None:
        super().__init__()
        self._messages: list[dict] = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield Static("  Model: ", classes="label")
            yield Select([], id="chat-model-select")
        yield RichLog(highlight=True, markup=False, id="chat-log")
        with Horizontal(id="chat-input-row"):
            yield Input(placeholder="Type a message…", id="chat-input")
            yield Button("Send", id="chat-send", classes="primary")
        yield Footer()

    def on_mount(self) -> None:
        self.app.call_later(self._load_model_options)

    async def _load_model_options(self) -> None:
        models = await api_client.list_models()
        select = self.query_one("#chat-model-select", Select)
        options = [(m.get("name", "?"), m.get("name", "?")) for m in models]
        select.set_options(options)
        if options:
            select.value = options[0][1]

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "chat-send":
            await self._send_message()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "chat-input":
            await self._send_message()

    async def _send_message(self) -> None:
        input_widget = self.query_one("#chat-input", Input)
        text = input_widget.value.strip()
        if not text:
            return

        select = self.query_one("#chat-model-select", Select)
        model = str(select.value) if select.value is not Select.BLANK else ""
        if not model:
            return

        log = self.query_one("#chat-log", RichLog)
        log.write(f"\n[You] {text}")
        input_widget.value = ""

        self._messages.append({"role": "user", "content": text})
        log.write(f"\n[{model}] ", end="")

        assistant_text = ""
        try:
            async for line in api_client.chat_stream(model, self._messages):
                try:
                    data = json.loads(line)
                    chunk = data.get("message", {}).get("content", "")
                    if chunk:
                        assistant_text += chunk
                        log.write(chunk, end="")
                except json.JSONDecodeError:
                    pass
            log.write("")
            if assistant_text:
                self._messages.append({"role": "assistant", "content": assistant_text})
        except Exception as exc:
            log.write(f"\n[error] {exc}")

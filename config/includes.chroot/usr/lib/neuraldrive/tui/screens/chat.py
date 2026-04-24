from __future__ import annotations

import json

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Button, Footer, Input, RichLog, Select, Static

from widgets.safe_header import SafeHeader

from utils import api_client


class ChatScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def __init__(self) -> None:
        super().__init__()
        self._messages: list[dict] = []

    def compose(self) -> ComposeResult:
        yield SafeHeader()
        with Horizontal(id="chat-model-row"):
            yield Static(" Model ", id="chat-model-label")
            yield Select([], id="chat-model-select", prompt="Choose a model…")
        yield Static("", id="chat-notice")
        yield RichLog(highlight=True, markup=False, wrap=True, id="chat-log")
        with Horizontal(id="chat-input-row"):
            yield Input(placeholder="Type a message…", id="chat-input")
            yield Button("Send", id="chat-send", classes="primary")
        yield Footer()

    def on_mount(self) -> None:
        self.app.call_later(self._load_model_options)
        self._refresh_timer = self.set_interval(10, self._poll_model_options)

    def on_screen_resume(self) -> None:
        self.app.call_later(self._load_model_options)

    async def _poll_model_options(self) -> None:
        await self._load_model_options()

    async def _load_model_options(self) -> None:
        notice = self.query_one("#chat-notice", Static)
        select = self.query_one("#chat-model-select", Select)
        send_btn = self.query_one("#chat-send", Button)
        chat_input = self.query_one("#chat-input", Input)

        available = await api_client.ollama_available()
        if not available:
            notice.update("  Ollama is not running. Start it from the Services screen.")
            notice.add_class("error")
            send_btn.disabled = True
            chat_input.disabled = True
            return

        models = await api_client.list_models()
        running = await api_client.list_running_models()
        running_names = {m.get("name", "") for m in running}
        options = []
        for m in models:
            name = m.get("name", "?")
            label = f"* {name}" if name in running_names else name
            options.append((label, name))
        previous = select.value
        select.set_options(options)

        if not options:
            notice.update(
                "  No models installed. Pull a model from the Models screen (F2)."
            )
            notice.add_class("warn")
            send_btn.disabled = True
            chat_input.disabled = True
            return

        notice.update("")
        notice.remove_class("error", "warn")
        send_btn.disabled = False
        chat_input.disabled = False
        option_values = [v for _, v in options]
        if previous is not Select.BLANK and previous in option_values:
            select.value = previous
        elif select.value is Select.BLANK:
            select.value = options[0][1]

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "chat-send":
            self._do_send()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "chat-input":
            self._do_send()

    def _do_send(self) -> None:
        input_widget = self.query_one("#chat-input", Input)
        text = input_widget.value.strip()
        if not text:
            return

        select = self.query_one("#chat-model-select", Select)
        model = str(select.value) if select.value is not Select.BLANK else ""
        if not model:
            log = self.query_one("#chat-log", RichLog)
            log.write("[error] No model selected. Choose a model from the dropdown.")
            return

        log = self.query_one("#chat-log", RichLog)
        log.write(f"\n[You] {text}")
        input_widget.value = ""

        self._messages.append({"role": "user", "content": text})
        self._stream_response(model)

    @work(exclusive=True)
    async def _stream_response(self, model: str) -> None:
        log = self.query_one("#chat-log", RichLog)
        send_btn = self.query_one("#chat-send", Button)
        chat_input = self.query_one("#chat-input", Input)

        send_btn.disabled = True
        chat_input.disabled = True
        log.write(f"[{model}] ...")

        assistant_text = ""
        try:
            async for line in api_client.chat_stream(model, self._messages):
                try:
                    data = json.loads(line)
                    chunk = data.get("message", {}).get("content", "")
                    if chunk:
                        assistant_text += chunk
                except json.JSONDecodeError:
                    pass

            if assistant_text:
                log.clear()
                for msg in self._messages:
                    role = "You" if msg["role"] == "user" else model
                    log.write(f"[{role}] {msg['content']}")
                log.write(f"[{model}] {assistant_text}")
                self._messages.append({"role": "assistant", "content": assistant_text})
            else:
                log.write(f"[{model}] (no response)")
        except Exception as exc:
            log.write(f"\n[error] {exc}")
            if self._messages and self._messages[-1]["role"] == "user":
                self._messages.pop()
        finally:
            send_btn.disabled = False
            chat_input.disabled = False
            chat_input.focus()

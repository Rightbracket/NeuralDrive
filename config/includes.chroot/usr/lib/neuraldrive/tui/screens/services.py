from __future__ import annotations

import subprocess

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Static

from widgets.safe_header import SafeHeader

from textual.binding import Binding

from utils import hardware


class ServicesScreen(Screen):
    BINDINGS = [
        ("r", "refresh", "Refresh"),
        Binding("up", "move_up", "Up", show=False),
        Binding("down", "move_down", "Down", show=False),
    ]

    def compose(self) -> ComposeResult:
        yield SafeHeader()
        with VerticalScroll():
            yield Static("NeuralDrive Services", classes="heading")
            yield Vertical(id="service-list")
        yield Static("", id="svc-status")
        with Horizontal(id="svc-actions"):
            yield Button("Start", id="svc-start", variant="primary")
            yield Button("Stop", id="svc-stop", variant="error")
            yield Button("Restart", id="svc-restart")
        yield Footer()

    def on_mount(self) -> None:
        self._selected_index = 0
        self._services: list[tuple[str, str]] = []
        self.app.call_later(self._load_services)

    def on_screen_resume(self) -> None:
        self.app.call_later(self._load_services)

    async def _load_services(self) -> None:
        container = self.query_one("#service-list", Vertical)
        await container.remove_children()
        self._services = []
        for svc in hardware.NEURALDRIVE_SERVICES:
            status = hardware.get_service_status(svc)
            self._services.append((svc, status))

        for i, (svc, status) in enumerate(self._services):
            short = svc.replace("neuraldrive-", "")
            if status == "active":
                indicator = "●"
                cls = "svc-row svc-active"
            else:
                indicator = "○"
                cls = "svc-row svc-inactive"
            if i == self._selected_index:
                cls += " svc-selected"
            row = Static(
                f"  {indicator}  {short:<20} {status}", classes=cls, id=f"svc-{i}"
            )
            await container.mount(row)

        self._update_action_buttons()

    def _update_action_buttons(self) -> None:
        if not self._services:
            return
        _, status = self._services[self._selected_index]
        self.query_one("#svc-start", Button).disabled = status == "active"
        self.query_one("#svc-stop", Button).disabled = status != "active"

    def action_move_up(self) -> None:
        if self._selected_index > 0:
            self._selected_index -= 1
            self.app.call_later(self._load_services)

    def action_move_down(self) -> None:
        if self._selected_index < len(self._services) - 1:
            self._selected_index += 1
            self.app.call_later(self._load_services)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id or ""
        if btn_id == "svc-start":
            self._run_action("start")
        elif btn_id == "svc-stop":
            self._run_action("stop")
        elif btn_id == "svc-restart":
            self._run_action("restart")

    @work(exclusive=True)
    async def _run_action(self, action: str) -> None:
        if not self._services:
            return
        svc, _ = self._services[self._selected_index]
        short = svc.replace("neuraldrive-", "")
        status_widget = self.query_one("#svc-status", Static)
        status_widget.update(f"  {action.title()}ing {short}...")

        try:
            res = subprocess.run(
                ["sudo", "systemctl", action, svc],
                capture_output=True,
                text=True,
                timeout=15,
            )
            if res.returncode == 0:
                status_widget.update(f"  ✓ {short} {action}ed")
            else:
                status_widget.update(f"  ✗ {short}: {res.stderr.strip()}")
        except subprocess.TimeoutExpired:
            status_widget.update(f"  ✗ {short}: timeout")

        self.app.call_later(self._load_services)

    def action_refresh(self) -> None:
        self.app.call_later(self._load_services)

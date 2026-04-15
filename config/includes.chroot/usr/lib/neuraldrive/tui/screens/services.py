from __future__ import annotations

import subprocess

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static

from utils import hardware


class ServiceRow(Horizontal):
    def __init__(self, service: str, status: str) -> None:
        super().__init__(classes="service-row")
        self.service_name = service
        self.service_status = status

    def compose(self) -> ComposeResult:
        short = self.service_name.replace("neuraldrive-", "")
        cls = "ok" if self.service_status == "active" else "error"
        yield Static(
            f"{'●' if self.service_status == 'active' else '○'} {short}", classes=cls
        )
        yield Static("", classes="value")
        yield Button("Start", id=f"start-{self.service_name}")
        yield Button("Stop", id=f"stop-{self.service_name}")
        yield Button("Restart", id=f"restart-{self.service_name}")


class ServicesScreen(Screen):
    BINDINGS = [("r", "refresh", "Refresh")]

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll():
            yield Static("NeuralDrive Services", classes="heading")
            yield Vertical(id="service-list")
            yield Static("", id="svc-status")
        yield Footer()

    def on_mount(self) -> None:
        self._load_services()

    def _load_services(self) -> None:
        container = self.query_one("#service-list", Vertical)
        container.remove_children()
        for svc in hardware.NEURALDRIVE_SERVICES:
            status = hardware.get_service_status(svc)
            container.mount(ServiceRow(svc, status))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id or ""
        for action in ("start", "stop", "restart"):
            prefix = f"{action}-"
            if btn_id.startswith(prefix):
                svc = btn_id[len(prefix) :]
                self._run_systemctl(action, svc)
                return

    def _run_systemctl(self, action: str, service: str) -> None:
        status_widget = self.query_one("#svc-status", Static)
        try:
            res = subprocess.run(
                ["systemctl", action, service],
                capture_output=True,
                text=True,
                timeout=15,
            )
            if res.returncode == 0:
                status_widget.update(f"✓ {action} {service}")
            else:
                status_widget.update(f"✗ {action} {service}: {res.stderr.strip()}")
        except subprocess.TimeoutExpired:
            status_widget.update(f"✗ {action} {service}: timeout")
        self._load_services()

    def action_refresh(self) -> None:
        self._load_services()

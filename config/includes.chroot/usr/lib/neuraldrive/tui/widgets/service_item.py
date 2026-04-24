from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, Static


class ServiceItem(Horizontal):
    can_focus = False

    def __init__(self, service: str, display_name: str, status: str) -> None:
        super().__init__(name=service, classes="svc-item")
        self._service = service
        self._display_name = display_name
        self._status = status

    def compose(self) -> ComposeResult:
        active = self._status == "active"
        indicator = "\u25cf" if active else "\u25cb"
        status_cls = "svc-status-active" if active else "svc-status-inactive"
        yield Static(self._display_name, classes="svc-name")
        yield Static(f"{indicator} {self._status}", classes=f"svc-state {status_cls}")
        start_btn = Button("Start", name=self._service, classes="svc-start")
        stop_btn = Button("Stop", name=self._service, classes="svc-stop")
        restart_btn = Button("Restart", name=self._service, classes="svc-restart")
        start_btn.can_focus = False
        stop_btn.can_focus = False
        restart_btn.can_focus = False
        if active:
            start_btn.disabled = True
        else:
            stop_btn.disabled = True
            restart_btn.disabled = True
        yield start_btn
        yield stop_btn
        yield restart_btn

    def get_action_buttons(self) -> list[Button]:
        return list(self.query("Button"))

    def update_status(self, status: str) -> None:
        self._status = status
        active = status == "active"
        indicator = "\u25cf" if active else "\u25cb"
        status_cls = "svc-status-active" if active else "svc-status-inactive"
        state_widget = self.query_one(".svc-state", Static)
        state_widget.update(f"{indicator} {status}")
        state_widget.remove_class("svc-status-active", "svc-status-inactive")
        state_widget.add_class(status_cls)
        for btn in self.query("Button"):
            if btn.has_class("svc-start"):
                btn.disabled = active
            elif btn.has_class("svc-stop"):
                btn.disabled = not active
            elif btn.has_class("svc-restart"):
                btn.disabled = not active

from __future__ import annotations

import subprocess

from textual import work
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Static
from textual.binding import Binding

from widgets.safe_header import SafeHeader
from widgets.service_item import ServiceItem
from utils import hardware


POLL_INTERVAL = 5


class ServicesScreen(Screen):
    BINDINGS = [
        ("r", "refresh", "Refresh"),
        Binding("up", "nav_up", show=False, priority=True),
        Binding("down", "nav_down", show=False, priority=True),
        Binding("left", "nav_left", show=False, priority=True),
        Binding("right", "nav_right", show=False, priority=True),
        Binding("enter", "activate", show=False, priority=True),
    ]

    def compose(self) -> ComposeResult:
        yield SafeHeader()
        yield Static("NeuralDrive Services", classes="heading")
        yield VerticalScroll(id="svc-list")
        yield Static("", id="svc-status")
        yield Footer()

    def on_mount(self) -> None:
        self._svc_items: list[ServiceItem] = []
        self._highlight_index = 0
        self._btn_index = 0
        self._poll_timer = self.set_interval(POLL_INTERVAL, self._poll_services)
        self.app.call_later(self._load_services)

    def on_screen_resume(self) -> None:
        self.app.call_later(self._load_services)

    def on_screen_suspend(self) -> None:
        pass

    async def _load_services(self) -> None:
        container = self.query_one("#svc-list", VerticalScroll)
        await container.remove_children()
        self._svc_items = []
        for svc in hardware.NEURALDRIVE_SERVICES:
            status = hardware.get_service_status(svc)
            short = svc.replace("neuraldrive-", "")
            item = ServiceItem(svc, short, status)
            container.mount(item)
            self._svc_items.append(item)
        if self._svc_items:
            self._highlight_index = min(
                self._highlight_index, len(self._svc_items) - 1
            )
            self._btn_index = 0
            self._apply_highlight()

    async def _poll_services(self) -> None:
        for item in self._svc_items:
            status = hardware.get_service_status(item.name)
            item.update_status(status)
        if self._svc_items:
            self._apply_btn_highlight()

    def _get_active_buttons(self) -> list[Button]:
        if not self._svc_items:
            return []
        item = self._svc_items[self._highlight_index]
        return [b for b in item.get_action_buttons() if not b.disabled]

    def _apply_highlight(self) -> None:
        self._clear_btn_highlight()
        for i, item in enumerate(self._svc_items):
            if i == self._highlight_index:
                item.add_class("svc-highlighted")
                item.scroll_visible()
                self._apply_btn_highlight()
            else:
                item.remove_class("svc-highlighted")

    def _clear_highlight(self) -> None:
        self._clear_btn_highlight()
        for item in self._svc_items:
            item.remove_class("svc-highlighted")

    def _apply_btn_highlight(self) -> None:
        buttons = self._get_active_buttons()
        if not buttons:
            return
        self._btn_index = max(0, min(self._btn_index, len(buttons) - 1))
        for item in self._svc_items:
            for btn in item.get_action_buttons():
                btn.remove_class("svc-btn-active")
        for i, btn in enumerate(buttons):
            if i == self._btn_index:
                btn.add_class("svc-btn-active")
            else:
                btn.remove_class("svc-btn-active")

    def _clear_btn_highlight(self) -> None:
        for item in self._svc_items:
            for btn in item.get_action_buttons():
                btn.remove_class("svc-btn-active")

    def action_nav_up(self) -> None:
        if self._svc_items and self._highlight_index > 0:
            self._highlight_index -= 1
            self._btn_index = 0
            self._apply_highlight()

    def action_nav_down(self) -> None:
        if self._svc_items and self._highlight_index < len(self._svc_items) - 1:
            self._highlight_index += 1
            self._btn_index = 0
            self._apply_highlight()

    def action_nav_left(self) -> None:
        if self._btn_index > 0:
            self._btn_index -= 1
            self._apply_btn_highlight()

    def action_nav_right(self) -> None:
        buttons = self._get_active_buttons()
        if self._btn_index < len(buttons) - 1:
            self._btn_index += 1
            self._apply_btn_highlight()

    def action_activate(self) -> None:
        buttons = self._get_active_buttons()
        if buttons and 0 <= self._btn_index < len(buttons):
            buttons[self._btn_index].press()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn = event.button
        if btn.has_class("svc-start"):
            self._run_action(btn.name or "", "start")
        elif btn.has_class("svc-stop"):
            self._run_action(btn.name or "", "stop")
        elif btn.has_class("svc-restart"):
            self._run_action(btn.name or "", "restart")

    @work(exclusive=True)
    async def _run_action(self, service: str, action: str) -> None:
        short = service.replace("neuraldrive-", "")
        status_widget = self.query_one("#svc-status", Static)
        status_widget.update(f"  {action.title()}ing {short}...")
        try:
            res = subprocess.run(
                ["sudo", "systemctl", action, service],
                capture_output=True,
                text=True,
                timeout=15,
            )
            if res.returncode == 0:
                status_widget.update(f"  \u2713 {short} {action}ed")
            else:
                status_widget.update(f"  \u2717 {short}: {res.stderr.strip()}")
        except subprocess.TimeoutExpired:
            status_widget.update(f"  \u2717 {short}: timeout")
        await self._poll_services()

    def action_refresh(self) -> None:
        self.app.call_later(self._load_services)

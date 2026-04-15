from __future__ import annotations

import subprocess

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Footer, Header, RichLog, Select, Static

from utils import hardware

_SERVICE_OPTIONS = [
    (svc.replace("neuraldrive-", ""), svc) for svc in hardware.NEURALDRIVE_SERVICES
]
_SERVICE_OPTIONS.insert(0, ("all (neuraldrive*)", "neuraldrive-*"))


class LogsScreen(Screen):
    BINDINGS = [("r", "refresh", "Refresh")]

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield Static("  Service: ", classes="label")
            yield Select(
                _SERVICE_OPTIONS, value="neuraldrive-*", id="log-service-select"
            )
        yield RichLog(highlight=True, markup=False, id="log-output")
        yield Footer()

    def on_mount(self) -> None:
        self._load_logs()

    def on_select_changed(self, event: Select.Changed) -> None:
        self._load_logs()

    def _load_logs(self) -> None:
        log_widget = self.query_one("#log-output", RichLog)
        log_widget.clear()

        select = self.query_one("#log-service-select", Select)
        unit = (
            str(select.value) if select.value is not Select.BLANK else "neuraldrive-*"
        )

        try:
            cmd = ["journalctl", "-u", unit, "-n", "200", "--no-pager", "--no-hostname"]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            output = res.stdout.strip() if res.stdout else "(no log output)"
            for line in output.splitlines():
                log_widget.write(line)
        except subprocess.TimeoutExpired:
            log_widget.write("[timeout reading logs]")
        except FileNotFoundError:
            log_widget.write("[journalctl not available]")

    def action_refresh(self) -> None:
        self._load_logs()

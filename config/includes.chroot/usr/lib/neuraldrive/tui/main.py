from textual.app import App, ComposeResult
from textual.binding import Binding

from screens.dashboard import DashboardScreen
from screens.models import ModelsScreen
from screens.services import ServicesScreen
from screens.network import NetworkScreen
from screens.logs import LogsScreen
from screens.chat import ChatScreen
from screens.wizard import FirstBootWizard

import argparse
import os
import sys
import traceback
from datetime import datetime

PERSIST_DIR = "/var/lib/neuraldrive"
OVERLAY_LOG_DIR = "/var/log/neuraldrive"


def _persistent_available() -> bool:
    return os.path.ismount(PERSIST_DIR)


def _log_dir() -> str:
    if _persistent_available():
        p = os.path.join(PERSIST_DIR, "logs")
        try:
            os.makedirs(p, exist_ok=True)
            return p
        except PermissionError:
            pass
    os.makedirs(OVERLAY_LOG_DIR, exist_ok=True)
    return OVERLAY_LOG_DIR


def _screenshot_dir() -> str:
    if _persistent_available():
        p = os.path.join(PERSIST_DIR, "screenshots")
        try:
            os.makedirs(p, exist_ok=True)
            return p
        except PermissionError:
            pass
    os.makedirs(OVERLAY_LOG_DIR, exist_ok=True)
    return OVERLAY_LOG_DIR


def _write_crash_dump(error: BaseException) -> str | None:
    try:
        crash_dir = _log_dir()
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        dump_path = os.path.join(crash_dir, f"tui-crash-{ts}.log")
        with open(dump_path, "w") as f:
            f.write(f"NeuralDrive TUI crash at {ts}\n")
            f.write(f"Python: {sys.version}\n")
            f.write(f"Args: {sys.argv}\n\n")
            traceback.print_exception(type(error), error, error.__traceback__, file=f)
        return dump_path
    except Exception:
        return None


class NeuralDriveTUI(App):
    CSS_PATH = "styles.tcss"
    TITLE = "NeuralDrive"
    ENABLE_COMMAND_PALETTE = False

    BINDINGS = [
        Binding("f2", "switch_screen('dashboard')", "F2 Dash", priority=True),
        Binding("f3", "switch_screen('models')", "F3 Models", priority=True),
        Binding("f4", "switch_screen('services')", "F4 Svc", priority=True),
        Binding("f5", "switch_screen('chat')", "F5 Chat", priority=True),
        Binding("f6", "switch_screen('logs')", "F6 Logs", priority=True),
        Binding("q", "quit", "Quit"),
        Binding("up", "focus_previous", "Previous", show=False),
        Binding("down", "focus_next", "Next", show=False),
    ]

    SCREENS = {
        "dashboard": DashboardScreen,
        "models": ModelsScreen,
        "services": ServicesScreen,
        "network": NetworkScreen,
        "logs": LogsScreen,
        "chat": ChatScreen,
    }

    def __init__(self, force_wizard: bool = False) -> None:
        super().__init__()
        self._force_wizard = force_wizard

    def on_mount(self) -> None:
        self.push_screen(DashboardScreen())
        sentinel_exists = os.path.exists("/etc/neuraldrive/first-boot-complete")
        if self._force_wizard or not sentinel_exists:
            self.push_screen(FirstBootWizard())

    def _handle_exception(self, error: Exception) -> None:
        dump_path = _write_crash_dump(error)
        if dump_path:
            self.log(f"Crash dump saved to {dump_path}")
        super()._handle_exception(error)

    def action_focus_next(self) -> None:
        self.screen.focus_next()

    def action_focus_previous(self) -> None:
        self.screen.focus_previous()

    def action_switch_screen(self, screen_name: str) -> None:
        if screen_name in self.SCREENS:
            self.switch_screen(screen_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NeuralDrive TUI")
    parser.add_argument(
        "--wizard", action="store_true", help="Force the first-boot wizard to run"
    )
    args = parser.parse_args()

    screenshot_dir = _screenshot_dir()
    os.environ["TEXTUAL_SCREENSHOT_LOCATION"] = screenshot_dir
    try:
        app = NeuralDriveTUI(force_wizard=args.wizard)
        app.run(mouse=False)
    except Exception as exc:
        dump_path = _write_crash_dump(exc)
        traceback.print_exc()
        if dump_path:
            print(f"\nCrash dump saved to {dump_path}")
        sys.exit(1)

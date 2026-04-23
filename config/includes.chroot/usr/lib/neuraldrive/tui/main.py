from textual.app import App, ComposeResult
from textual.binding import Binding

from screens.dashboard import DashboardScreen
from screens.models import ModelsScreen
from screens.services import ServicesScreen
from screens.network import NetworkScreen
from screens.logs import LogsScreen
from screens.chat import ChatScreen
from screens.wizard import FirstBootWizard

import os


class NeuralDriveTUI(App):
    CSS_PATH = "styles.tcss"
    TITLE = "NeuralDrive"

    BINDINGS = [
        Binding("m", "switch_screen('models')", "Models"),
        Binding("s", "switch_screen('services')", "Services"),
        Binding("n", "switch_screen('network')", "Network"),
        Binding("l", "switch_screen('logs')", "Logs"),
        Binding("c", "switch_screen('chat')", "Chat"),
        Binding("d", "switch_screen('dashboard')", "Dashboard"),
        Binding("q", "quit", "Quit"),
    ]

    SCREENS = {
        "dashboard": DashboardScreen,
        "models": ModelsScreen,
        "services": ServicesScreen,
        "network": NetworkScreen,
        "logs": LogsScreen,
        "chat": ChatScreen,
    }

    def on_mount(self) -> None:
        self.push_screen(DashboardScreen())
        if not os.path.exists("/etc/neuraldrive/first-boot-complete"):
            self.push_screen(FirstBootWizard())

    def action_switch_screen(self, screen_name: str) -> None:
        if screen_name in self.SCREENS:
            self.switch_screen(screen_name)


if __name__ == "__main__":
    app = NeuralDriveTUI()
    app.run(mouse=False)

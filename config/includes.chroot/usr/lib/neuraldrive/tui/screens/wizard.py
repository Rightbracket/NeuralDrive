from __future__ import annotations

import os
import secrets
import subprocess

from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import Button, Input, Static

SENTINEL = "/etc/neuraldrive/first-boot-complete"
CREDENTIALS_PATH = "/etc/neuraldrive/credentials.conf"
API_KEY_PATH = "/etc/neuraldrive/api.key"
SUDOERS_PATH = "/etc/sudoers.d/neuraldrive-admin"


class FirstBootWizard(Screen):
    BINDINGS = [("escape", "cancel_wizard", "Skip")]

    def __init__(self) -> None:
        super().__init__()
        self._step = 0
        self._admin_password = ""
        self._wifi_ssid = ""
        self._wifi_psk = ""
        self._generated_api_key = ""

    def compose(self) -> ComposeResult:
        with Center(id="wizard-container"):
            with Vertical(id="wizard-box"):
                yield Static("", id="wiz-title")
                yield Static("", id="wiz-body")
                yield Input(placeholder="", id="wiz-input")
                yield Input(placeholder="", id="wiz-input2", password=True)
                yield Static("", id="wiz-error")
                yield Button("Next →", id="wiz-next", classes="primary")
                yield Button("Skip", id="wiz-skip")

    def on_mount(self) -> None:
        self._show_step()

    def _show_step(self) -> None:
        title = self.query_one("#wiz-title", Static)
        body = self.query_one("#wiz-body", Static)
        inp = self.query_one("#wiz-input", Input)
        inp2 = self.query_one("#wiz-input2", Input)
        error = self.query_one("#wiz-error", Static)
        next_btn = self.query_one("#wiz-next", Button)
        skip_btn = self.query_one("#wiz-skip", Button)

        inp.display = False
        inp2.display = False
        skip_btn.display = False
        error.update("")
        inp.value = ""
        inp2.value = ""

        if self._step == 0:
            title.update("Welcome to NeuralDrive")
            body.update(
                "This wizard will configure your system.\n\n"
                "Steps: Security → WiFi → Network → Storage → Models → Done"
            )
            next_btn.label = "Begin →"

        elif self._step == 1:
            title.update("Step 1: Security")
            body.update("Set an admin password for the 'neuraldrive' user.")
            inp.display = True
            inp.placeholder = "New password"
            inp.password = True
            inp2.display = True
            inp2.placeholder = "Confirm password"
            next_btn.label = "Set Password →"

        elif self._step == 2:
            title.update("Step 2: WiFi (Optional)")
            body.update("Enter WiFi credentials, or skip for wired-only.")
            inp.display = True
            inp.placeholder = "SSID"
            inp.password = False
            inp2.display = True
            inp2.placeholder = "Passphrase"
            skip_btn.display = True
            next_btn.label = "Connect →"

        elif self._step == 3:
            title.update("Step 3: Network")
            from utils import hardware

            ip = hardware.get_ip_address()
            hostname = hardware.get_hostname()
            body.update(
                f"Current configuration:\n"
                f"  Hostname: {hostname}\n"
                f"  IP: {ip}\n\n"
                "DHCP is active. Static IP can be configured later."
            )
            next_btn.label = "Next →"

        elif self._step == 4:
            title.update("Step 4: Storage")
            from utils import hardware

            disk = hardware.get_disk_info()
            body.update(
                f"Storage: {disk['free_gb']} GB free of {disk['total_gb']} GB\n"
                f"Path: {disk['path']}\n\n"
                "Models will be stored at /var/lib/neuraldrive/models."
            )
            next_btn.label = "Next →"

        elif self._step == 5:
            title.update("Step 5: Models")
            body.update(
                "Models can be pulled after setup from:\n"
                "  • This TUI (press M for Models)\n"
                "  • Open WebUI dashboard\n"
                "  • Command line: ollama pull <model>"
            )
            next_btn.label = "Next →"

        elif self._step == 6:
            self._generated_api_key = secrets.token_urlsafe(32)
            title.update("Setup Complete")
            body.update(
                "NeuralDrive is ready.\n\n"
                f"API Key: {self._generated_api_key}\n\n"
                "Save this key — it is required for API access.\n"
                "Press Finish to start using NeuralDrive."
            )
            next_btn.label = "Finish ✓"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "wiz-skip":
            self._step += 1
            self._show_step()
            return

        if event.button.id == "wiz-next":
            if self._step == 1:
                if not self._validate_password():
                    return
            elif self._step == 2:
                self._configure_wifi()
            elif self._step == 6:
                self._finalize()
                return

            self._step += 1
            if self._step > 6:
                self._finalize()
            else:
                self._show_step()

    def _validate_password(self) -> bool:
        error = self.query_one("#wiz-error", Static)
        pw = self.query_one("#wiz-input", Input).value
        pw2 = self.query_one("#wiz-input2", Input).value

        if len(pw) < 8:
            error.update("Password must be at least 8 characters")
            return False
        if pw != pw2:
            error.update("Passwords do not match")
            return False

        self._admin_password = pw
        return True

    def _configure_wifi(self) -> None:
        ssid = self.query_one("#wiz-input", Input).value.strip()
        psk = self.query_one("#wiz-input2", Input).value.strip()
        if not ssid:
            return
        self._wifi_ssid = ssid
        self._wifi_psk = psk
        try:
            subprocess.run(
                ["nmcli", "device", "wifi", "connect", ssid, "password", psk],
                capture_output=True,
                timeout=30,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    def _finalize(self) -> None:
        try:
            if self._admin_password:
                proc = subprocess.Popen(
                    ["chpasswd"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                proc.communicate(
                    input=f"neuraldrive:{self._admin_password}\n".encode(),
                    timeout=10,
                )

                if os.path.exists(SUDOERS_PATH):
                    with open(SUDOERS_PATH, "r") as f:
                        content = f.read()
                    content = content.replace("NOPASSWD:", "")
                    with open(SUDOERS_PATH, "w") as f:
                        f.write(content)

            if self._generated_api_key:
                os.makedirs(os.path.dirname(API_KEY_PATH), exist_ok=True)
                with open(API_KEY_PATH, "w") as f:
                    f.write(self._generated_api_key + "\n")
                os.chmod(API_KEY_PATH, 0o600)

                os.makedirs(os.path.dirname(CREDENTIALS_PATH), exist_ok=True)
                with open(CREDENTIALS_PATH, "w") as f:
                    f.write(f"api_key={self._generated_api_key}\n")
                os.chmod(CREDENTIALS_PATH, 0o600)

            os.makedirs(os.path.dirname(SENTINEL), exist_ok=True)
            with open(SENTINEL, "w") as f:
                f.write("")

        except Exception:
            pass

        self.app.pop_screen()

    def action_cancel_wizard(self) -> None:
        self.app.pop_screen()

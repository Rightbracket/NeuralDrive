from __future__ import annotations

import os
import secrets
import subprocess

from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import Button, Input, Static

from utils import config

SENTINEL = "/etc/neuraldrive/first-boot-complete"
CREDENTIALS_PATH = "/etc/neuraldrive/credentials.conf"
API_KEY_PATH = "/etc/neuraldrive/api.key"
SUDOERS_PATH = "/etc/sudoers.d/neuraldrive-admin"
PERSISTENCE_MOUNT = "/var/lib/neuraldrive"
PERSISTENCE_CONF_CONTENT = "/var/lib/neuraldrive union\n/etc/neuraldrive union\n/var/log/neuraldrive union\n/home union\n"


class FirstBootWizard(Screen):
    """Step order: Welcome → Storage → Security → Network → Models → Done"""

    BINDINGS = [("escape", "cancel_wizard", "Skip")]

    def __init__(self) -> None:
        super().__init__()
        self._step = 0
        self._admin_password = ""
        self._wifi_ssid = ""
        self._wifi_psk = ""
        self._generated_api_key = ""
        self._boot_device: str | None = None
        self._unpartitioned_bytes = 0
        self._has_persistence = False
        self._awaiting_confirm = False

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

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if self._awaiting_confirm:
            self._handle_storage_confirm()
        else:
            self.focus_next()

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
        self._awaiting_confirm = False

        if self._step == 0:
            title.update("Welcome to NeuralDrive")
            body.update(
                "This wizard will configure your system.\n\n"
                "Steps: Storage → Security → Network → Models → Done"
            )
            next_btn.label = "Begin →"

        elif self._step == 1:
            self._show_storage_step(title, body, inp, next_btn, skip_btn)

        elif self._step == 2:
            title.update("Step 2: Security")
            body.update("Set an admin password for the 'neuraldrive-admin' user.")
            inp.display = True
            inp.placeholder = "New password"
            inp.password = True
            inp2.display = True
            inp2.placeholder = "Confirm password"
            next_btn.label = "Set Password →"

        elif self._step == 3:
            title.update("Step 3: Network (Optional)")
            body.update("Enter WiFi credentials, or skip for wired-only.")
            inp.display = True
            inp.placeholder = "SSID"
            inp.password = False
            inp2.display = True
            inp2.placeholder = "Passphrase"
            skip_btn.display = True
            next_btn.label = "Connect →"

        elif self._step == 4:
            title.update("Step 4: Models")
            body.update(
                "Models can be pulled after setup from:\n"
                "  • This TUI (press M for Models)\n"
                "  • Open WebUI dashboard\n"
                "  • Command line: ollama pull <model>"
            )
            next_btn.label = "Next →"

        elif self._step == 5:
            self._generated_api_key = secrets.token_urlsafe(32)
            title.update("Setup Complete")
            body.update(
                "NeuralDrive is ready.\n\n"
                f"API Key: {self._generated_api_key}\n\n"
                "Save this key — it is required for API access.\n"
                "Press Finish to start using NeuralDrive."
            )
            next_btn.label = "Finish ✓"

        if inp.display:
            inp.focus()
        else:
            next_btn.focus()

    def _show_storage_step(
        self,
        title: Static,
        body: Static,
        inp: Input,
        next_btn: Button,
        skip_btn: Button,
    ) -> None:
        title.update("Step 1: Storage & Persistence")

        from utils import hardware

        self._boot_device = hardware.get_boot_device()
        if not self._boot_device:
            body.update(
                "Could not detect boot device.\n\n"
                "Persistence partition cannot be created automatically.\n"
                "Data will be stored on the ephemeral overlay (lost on reboot).\n\n"
                "You can create a persistence partition manually later\n"
                "using: sudo /usr/lib/neuraldrive/prepare-usb.sh /dev/sdX"
            )
            next_btn.label = "Next →"
            return

        partitions = hardware.get_disk_partitions(self._boot_device)
        self._has_persistence = any(p.get("label") == "persistence" for p in partitions)
        total_bytes = hardware.get_device_size(self._boot_device)
        total_gb = total_bytes / (1024**3) if total_bytes else 0

        if self._has_persistence:
            pers = next(p for p in partitions if p.get("label") == "persistence")
            pers_gb = pers["size_bytes"] / (1024**3)
            body.update(
                f"Boot device: {self._boot_device} ({total_gb:.0f} GB)\n\n"
                f"✓ Persistence partition found: {pers_gb:.1f} GB\n"
                f"  Models, config, and logs will survive reboots.\n\n"
                "No action needed."
            )
            next_btn.label = "Next →"
            return

        self._unpartitioned_bytes = hardware.get_unpartitioned_space(self._boot_device)
        free_gb = self._unpartitioned_bytes / (1024**3)

        if self._unpartitioned_bytes < 1024 * 1024 * 1024:
            body.update(
                f"Boot device: {self._boot_device} ({total_gb:.0f} GB)\n\n"
                "No persistence partition found.\n"
                f"Only {free_gb:.1f} GB unpartitioned space available\n"
                "(minimum 1 GB required).\n\n"
                "Data will be stored on the ephemeral overlay (lost on reboot)."
            )
            next_btn.label = "Next →"
            return

        body.update(
            f"Boot device: {self._boot_device} ({total_gb:.0f} GB)\n\n"
            "No persistence partition found.\n"
            f"Available space: {free_gb:.1f} GB\n\n"
            "A persistence partition stores your models, config,\n"
            "and logs so they survive reboots.\n\n"
            "Type 'yes' to create it, or skip to use\n"
            "ephemeral overlay storage."
        )
        inp.display = True
        inp.placeholder = "Type 'yes' to create persistence partition"
        inp.password = False
        self._awaiting_confirm = True
        skip_btn.display = True
        next_btn.label = "Create Partition →"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "wiz-skip":
            self._awaiting_confirm = False
            self._step += 1
            self._show_step()
            return

        if event.button.id == "wiz-next":
            if self._step == 1 and self._awaiting_confirm:
                self._handle_storage_confirm()
                return
            if self._step == 2:
                if not self._validate_password():
                    return
            elif self._step == 3:
                self._configure_wifi()
            elif self._step == 5:
                self._finalize()
                return

            self._step += 1
            if self._step > 5:
                self._finalize()
            else:
                self._show_step()

    def _handle_storage_confirm(self) -> None:
        inp = self.query_one("#wiz-input", Input)
        error = self.query_one("#wiz-error", Static)

        if inp.value.strip().lower() != "yes":
            error.update("Type 'yes' to confirm, or press Skip.")
            return

        self._awaiting_confirm = False
        body = self.query_one("#wiz-body", Static)
        body.update("Creating persistence partition...\nThis may take a moment.")
        self.query_one("#wiz-next", Button).disabled = True
        self.query_one("#wiz-skip", Button).display = False
        inp.display = False

        err = self._create_persistence_partition()
        self.query_one("#wiz-next", Button).disabled = False

        if err:
            error.update(f"Partition creation failed: {err}")
            body.update(
                "Partition creation failed.\n"
                "Data will use the ephemeral overlay.\n"
                "You can retry manually later."
            )
            self.query_one("#wiz-next", Button).label = "Next →"
        else:
            body.update(
                "✓ Persistence partition created and mounted.\n\n"
                "Models, config, and logs will now survive reboots."
            )
            self.query_one("#wiz-next", Button).label = "Next →"

    def _create_persistence_partition(self) -> str | None:
        if not self._boot_device:
            return "No boot device detected"

        try:
            res = subprocess.run(
                [
                    "sudo",
                    "parted",
                    "-m",
                    self._boot_device,
                    "unit",
                    "B",
                    "print",
                    "free",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if res.returncode != 0:
                return f"parted print failed: {res.stderr.strip()}"

            free_start = None
            free_end = None
            for line in res.stdout.strip().splitlines():
                if ":free;" in line:
                    parts = line.split(":")
                    if len(parts) >= 3:
                        start_b = int(parts[1].rstrip("B"))
                        end_b = int(parts[2].rstrip("B"))
                        size_b = end_b - start_b
                        if size_b > 1024 * 1024 * 1024:
                            free_start = parts[1]
                            free_end = parts[2]

            if not free_start or not free_end:
                return "No free space block large enough found"

            proc = subprocess.run(
                [
                    "sudo",
                    "parted",
                    self._boot_device,
                    "--script",
                    "--",
                    "mkpart",
                    "primary",
                    "ext4",
                    free_start,
                    free_end,
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if proc.returncode != 0:
                return proc.stderr.strip()

            subprocess.run(
                ["sudo", "partprobe", self._boot_device],
                capture_output=True,
                timeout=10,
            )

            import time

            time.sleep(2)

            res = subprocess.run(
                ["lsblk", "-ln", "-o", "NAME", self._boot_device],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if res.returncode != 0:
                return "Could not determine new partition device"
            parts = res.stdout.strip().splitlines()
            if not parts:
                return "No partitions found after creation"
            new_part = f"/dev/{parts[-1].strip()}"

            proc = subprocess.run(
                [
                    "sudo",
                    "mkfs.ext4",
                    "-L",
                    "persistence",
                    "-m",
                    "1",
                    new_part,
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if proc.returncode != 0:
                return f"mkfs.ext4 failed: {proc.stderr.strip()}"

            subprocess.run(
                ["sudo", "mkdir", "-p", "/mnt/persistence"],
                capture_output=True,
                timeout=5,
            )
            proc = subprocess.run(
                ["sudo", "mount", new_part, "/mnt/persistence"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if proc.returncode != 0:
                return f"Mount failed: {proc.stderr.strip()}"

            proc = subprocess.run(
                ["sudo", "tee", "/mnt/persistence/persistence.conf"],
                input=PERSISTENCE_CONF_CONTENT.encode(),
                capture_output=True,
                timeout=5,
            )
            if proc.returncode != 0:
                return "Failed to write persistence.conf"

            for d in [
                "/mnt/persistence/var/lib/neuraldrive/ollama/.ollama",
                "/mnt/persistence/var/lib/neuraldrive/models",
                "/mnt/persistence/var/lib/neuraldrive/config",
                "/mnt/persistence/var/log/neuraldrive",
                "/mnt/persistence/etc/neuraldrive",
                "/mnt/persistence/home",
            ]:
                subprocess.run(
                    ["sudo", "mkdir", "-p", d],
                    capture_output=True,
                    timeout=5,
                )

            subprocess.run(
                [
                    "sudo",
                    "chown",
                    "-R",
                    "neuraldrive-ollama:neuraldrive-ollama",
                    "/mnt/persistence/var/lib/neuraldrive/ollama",
                ],
                capture_output=True,
                timeout=5,
            )

            subprocess.run(
                ["sudo", "umount", "/mnt/persistence"],
                capture_output=True,
                timeout=10,
            )

            subprocess.run(
                ["sudo", "mkdir", "-p", PERSISTENCE_MOUNT],
                capture_output=True,
                timeout=5,
            )
            proc = subprocess.run(
                ["sudo", "mount", new_part, PERSISTENCE_MOUNT],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if proc.returncode != 0:
                return f"Mount at {PERSISTENCE_MOUNT} failed: {proc.stderr.strip()}"

            subprocess.run(
                ["sudo", "systemctl", "restart", "neuraldrive-ollama"],
                capture_output=True,
                timeout=30,
            )

            self._has_persistence = True
            return None

        except subprocess.TimeoutExpired:
            return "Operation timed out"
        except FileNotFoundError as e:
            return f"Required tool not found: {e}"

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

    def _sudo_write(self, path: str, content: str, mode: str = "0644") -> str | None:
        try:
            subprocess.run(
                ["sudo", "mkdir", "-p", os.path.dirname(path)],
                capture_output=True,
                timeout=5,
            )
            proc = subprocess.run(
                ["sudo", "tee", path],
                input=content.encode(),
                capture_output=True,
                timeout=5,
            )
            if proc.returncode != 0:
                return f"Failed to write {path}: {proc.stderr.decode().strip()}"
            subprocess.run(
                ["sudo", "chmod", mode, path],
                capture_output=True,
                timeout=5,
            )
            return None
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return f"Failed to write {path}: {e}"

    def _finalize(self) -> None:
        errors: list[str] = []

        if self._admin_password:
            try:
                proc = subprocess.run(
                    ["sudo", "chpasswd"],
                    input=f"neuraldrive-admin:{self._admin_password}\n".encode(),
                    capture_output=True,
                    timeout=10,
                )
                if proc.returncode != 0:
                    errors.append(
                        f"Password change failed: {proc.stderr.decode().strip()}"
                    )
            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                errors.append(f"Password change failed: {e}")

        if self._generated_api_key:
            err = self._sudo_write(API_KEY_PATH, self._generated_api_key + "\n", "0600")
            if err:
                errors.append(err)

            err = self._sudo_write(
                CREDENTIALS_PATH,
                f"api_key={self._generated_api_key}\n",
                "0600",
            )
            if err:
                errors.append(err)

        cfg_data = config.load()
        cfg_data["wizard_complete"] = True
        if self._admin_password:
            cfg_data["security"] = {"password_set": True}
        if self._wifi_ssid:
            cfg_data["network"] = {"wifi_ssid": self._wifi_ssid}
        if self._generated_api_key:
            cfg_data["api"] = {"key_generated": True}
        if self._has_persistence:
            cfg_data["storage"] = {"persistence": True}
        cfg_err = config.save(cfg_data)
        if cfg_err:
            errors.append(cfg_err)

        err = self._sudo_write(SENTINEL, "")
        if err:
            errors.append(err)

        # Remove NOPASSWD LAST — after all other sudo operations are done,
        # since removing it makes subsequent sudo calls require a TTY password prompt
        if self._admin_password:
            try:
                result = subprocess.run(
                    ["sudo", "cat", SUDOERS_PATH],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0 and "NOPASSWD:" in result.stdout:
                    new_content = result.stdout.replace("NOPASSWD:", "")
                    err = self._sudo_write(SUDOERS_PATH, new_content, "0440")
                    if err:
                        errors.append(err)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

        if errors:
            error_widget = self.query_one("#wiz-error", Static)
            error_widget.update("\n".join(errors))
            return

        self.app.pop_screen()

    def action_cancel_wizard(self) -> None:
        self.app.pop_screen()

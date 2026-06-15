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
PERSISTENT_CREDENTIALS_PATH = "/var/lib/neuraldrive/config/credentials.conf"
PERSISTENT_API_KEY_PATH = "/var/lib/neuraldrive/config/api.key"
SUDOERS_PATH = "/etc/sudoers.d/neuraldrive-admin"
# persistence.conf lists directories that live-boot mounts as overlayfs on
# subsequent boots, with `<partition>/<entry-path>/rw` as the upperdir and
# `…/work` as the workdir. Anything we pre-seed MUST go inside the matching
# `rw/` subtree — files at the partition root are invisible to the overlay.
PERSISTENCE_UNION_ENTRIES = (
    "/var/lib/neuraldrive",
    "/etc/neuraldrive",
    "/var/log/neuraldrive",
    "/home",
)
PERSISTENCE_CONF_CONTENT = "".join(f"{p} union\n" for p in PERSISTENCE_UNION_ENTRIES)


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
        # True after _create_persistence_partition seeds a fresh partition this
        # session — in that case we must reboot before the user does anything
        # else, because writes are still landing in the ephemeral overlay (the
        # union mounts only activate on the next boot).
        self._fresh_persistence = False
        # Mountpoint of the freshly-created persistence partition. Kept mounted
        # across _create_persistence_partition → _finalize so that finalize can
        # mirror wizard-written state into the per-entry rw/ upperdirs. Cleared
        # (and partition unmounted) only at the very end of _finalize.
        self._persistence_staging_mount: str | None = None
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
                "This key is stored at /etc/neuraldrive/api.key\n"
                "and on persistent storage when available.\n"
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
                "✓ Persistence partition created.\n\n"
                "Models, config, and logs will survive reboots.\n"
                "A reboot is required at the end of the wizard to\n"
                "activate the partition's overlay filesystem."
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

            # Snapshot partition list BEFORE mkpart so the diff is reliable
            pre_res = subprocess.run(
                ["lsblk", "-ln", "-o", "NAME", self._boot_device],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if pre_res.returncode != 0:
                return "Cannot list partitions — aborting to avoid unsafe disk changes"
            before_parts = {
                line.strip()
                for line in pre_res.stdout.strip().splitlines()
                if line.strip()
            }

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

            partprobe_proc = subprocess.run(
                ["sudo", "partprobe", self._boot_device],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if partprobe_proc.returncode != 0:
                return f"partprobe failed: {partprobe_proc.stderr.strip()}"

            import time

            new_part = None
            for _attempt in range(6):
                time.sleep(1)
                post_res = subprocess.run(
                    ["lsblk", "-ln", "-o", "NAME", self._boot_device],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if post_res.returncode != 0:
                    continue

                after_parts = {
                    line.strip()
                    for line in post_res.stdout.strip().splitlines()
                    if line.strip()
                }

                new_parts = after_parts - before_parts
                base_name = os.path.basename(self._boot_device)
                new_parts.discard(base_name)

                if len(new_parts) == 1:
                    new_part = f"/dev/{new_parts.pop()}"
                    break

            if not new_part:
                return "New partition did not appear after partprobe (timed out)"

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

            proc = subprocess.run(
                ["sudo", "mkdir", "-p", "/mnt/persistence"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if proc.returncode != 0:
                return f"mkdir /mnt/persistence failed: {proc.stderr.strip()}"
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

            # Pre-seed the directory structure INSIDE each union entry's rw/
            # upperdir (and a matching work/ for overlayfs), so the files are
            # visible once live-boot activates the overlays on next boot. We
            # intentionally do NOT mkdir at the partition root (e.g.,
            # /mnt/persistence/models) — that path is outside the overlay and
            # any writes there would be orphaned/invisible after reboot.
            for d in [
                "/mnt/persistence/var/lib/neuraldrive/rw/ollama/.ollama",
                "/mnt/persistence/var/lib/neuraldrive/rw/models",
                "/mnt/persistence/var/lib/neuraldrive/rw/config",
                "/mnt/persistence/var/lib/neuraldrive/rw/webui",
                "/mnt/persistence/var/lib/neuraldrive/work",
                "/mnt/persistence/var/log/neuraldrive/rw",
                "/mnt/persistence/var/log/neuraldrive/work",
                "/mnt/persistence/etc/neuraldrive/rw",
                "/mnt/persistence/etc/neuraldrive/work",
                "/mnt/persistence/home/rw",
                "/mnt/persistence/home/work",
            ]:
                proc = subprocess.run(
                    ["sudo", "mkdir", "-p", d],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if proc.returncode != 0:
                    return f"mkdir {d} failed: {proc.stderr.strip()}"

            proc = subprocess.run(
                [
                    "sudo",
                    "chown",
                    "-R",
                    "neuraldrive-ollama:neuraldrive-ollama",
                    "/mnt/persistence/var/lib/neuraldrive/rw/ollama",
                    "/mnt/persistence/var/lib/neuraldrive/rw/models",
                    "/mnt/persistence/var/lib/neuraldrive/rw/config",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if proc.returncode != 0:
                return f"chown failed: {proc.stderr.strip()}"

            proc = subprocess.run(
                [
                    "sudo",
                    "chown",
                    "-R",
                    "neuraldrive-webui:neuraldrive-webui",
                    "/mnt/persistence/var/lib/neuraldrive/rw/webui",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if proc.returncode != 0:
                return f"chown webui failed: {proc.stderr.strip()}"

            # Leave the partition mounted at /mnt/persistence so _finalize() can
            # mirror wizard-written state (sentinel, api key, config, etc.) into
            # the per-entry rw/ upperdirs. _finalize will unmount when done.
            #
            # We intentionally do NOT direct-mount the partition at
            # /var/lib/neuraldrive here. The `union` entries in persistence.conf
            # only activate on the next boot (via live-boot's initrd). Mounting
            # the partition directly would land ollama writes at the partition
            # root, which would be invisible once the overlay activates on
            # reboot — exactly the bug this rewrite fixes. The wizard's
            # _finalize() will force a reboot before exit.
            self._persistence_staging_mount = "/mnt/persistence"
            self._has_persistence = True
            self._fresh_persistence = True
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
            mkdir_proc = subprocess.run(
                ["sudo", "mkdir", "-p", os.path.dirname(path)],
                capture_output=True,
                timeout=5,
            )
            if mkdir_proc.returncode != 0:
                return f"Failed to create dir for {path}: {mkdir_proc.stderr.decode().strip()}"
            proc = subprocess.run(
                ["sudo", "tee", path],
                input=content.encode(),
                capture_output=True,
                timeout=5,
            )
            if proc.returncode != 0:
                return f"Failed to write {path}: {proc.stderr.decode().strip()}"
            chmod_proc = subprocess.run(
                ["sudo", "chmod", mode, path],
                capture_output=True,
                timeout=5,
            )
            if chmod_proc.returncode != 0:
                return f"Failed to chmod {path}: {chmod_proc.stderr.decode().strip()}"
            return None
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return f"Failed to write {path}: {e}"

    def _persistence_root(self) -> str | None:
        """Return the mountpoint where the persistence partition is reachable.

        Two cases are valid:

        * **First-boot wizard run** (the persistence partition was just created
          this session): live-boot did not mount it at boot; the wizard left
          it mounted at /mnt/persistence (self._persistence_staging_mount).
        * **Subsequent wizard runs / re-runs**: live-boot mounts the partition
          at /run/live/persistence/<dev>/ during the initrd phase. We scan
          /proc/mounts for that prefix.

        Returns None when neither path is available — the wizard then cannot
        mirror state and surfaces an error before the user reboots.
        """
        if self._persistence_staging_mount and os.path.ismount(
            self._persistence_staging_mount
        ):
            return self._persistence_staging_mount
        try:
            with open("/proc/mounts") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) < 2:
                        continue
                    mp = parts[1]
                    if mp.startswith("/run/live/persistence/"):
                        return mp
        except OSError:
            pass
        return None

    def _mirror_to_persistence_upper(self, path: str) -> str | None:
        """Copy a file from the live filesystem into the matching union upperdir.

        Required after _fresh_persistence: on this boot, writes to (e.g.)
        /etc/neuraldrive/first-boot-complete land in the ephemeral tmpfs
        overlay. On the next boot, live-boot activates the union overlay using
        <partition>/etc/neuraldrive/rw/ as the upper — which is empty. Without
        mirroring, every wizard-written file (sentinel, api key, credentials,
        config.yaml, password hash side-effects) would be lost on reboot.

        Returns None on success, error message on failure.
        """
        root = self._persistence_root()
        if not root:
            return "Persistence partition mountpoint not found in /proc/mounts"

        for entry in PERSISTENCE_UNION_ENTRIES:
            if path == entry or path.startswith(entry + "/"):
                rel = path[len(entry) :].lstrip("/")
                dest = os.path.join(root, entry.lstrip("/"), "rw", rel)
                proc = subprocess.run(
                    ["sudo", "mkdir", "-p", os.path.dirname(dest)],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if proc.returncode != 0:
                    return f"mkdir {os.path.dirname(dest)} failed: {proc.stderr.strip()}"
                proc = subprocess.run(
                    ["sudo", "cp", "-a", path, dest],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if proc.returncode != 0:
                    return f"cp {path} -> {dest} failed: {proc.stderr.strip()}"
                return None
        # Path isn't under any union entry — nothing to mirror.
        return None

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
            key_content = self._generated_api_key + "\n"
            cred_content = f"api_key={self._generated_api_key}\n"

            err = self._sudo_write(API_KEY_PATH, key_content, "0600")
            if err:
                errors.append(err)
            err = self._sudo_write(CREDENTIALS_PATH, cred_content, "0600")
            if err:
                errors.append(err)

            persist_dir = os.path.dirname(PERSISTENT_API_KEY_PATH)
            if os.path.isdir(persist_dir):
                err = self._sudo_write(PERSISTENT_API_KEY_PATH, key_content, "0600")
                if err:
                    errors.append(err)
                err = self._sudo_write(
                    PERSISTENT_CREDENTIALS_PATH, cred_content, "0600"
                )
                if err:
                    errors.append(err)

        cfg_data = config.load()
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

        if errors:
            error_widget = self.query_one("#wiz-error", Static)
            error_widget.update("\n".join(errors))
            return

        # All config writes succeeded — now write sentinel and strip NOPASSWD
        err = self._sudo_write(SENTINEL, "")
        if err:
            error_widget = self.query_one("#wiz-error", Static)
            error_widget.update(f"Failed to write sentinel: {err}")
            return

        # If persistence was just created this session, mirror all
        # wizard-written state into the persistence partition's union upperdirs
        # NOW, before the user reboots. On this boot those files live in the
        # ephemeral tmpfs overlay; on next boot live-boot activates the union
        # overlays using <partition>/<entry>/rw/ as the upper — empty unless we
        # populate it here. See _mirror_to_persistence_upper docstring.
        if self._fresh_persistence:
            mirror_paths = [
                SENTINEL,
                API_KEY_PATH,
                CREDENTIALS_PATH,
                "/etc/neuraldrive/config.yaml",
                PERSISTENT_API_KEY_PATH,
                PERSISTENT_CREDENTIALS_PATH,
                "/var/lib/neuraldrive/config/config.yaml",
            ]
            for p in mirror_paths:
                if not os.path.exists(p):
                    continue
                mirr_err = self._mirror_to_persistence_upper(p)
                if mirr_err:
                    error_widget = self.query_one("#wiz-error", Static)
                    error_widget.update(
                        f"Persistence mirror failed: {mirr_err}\n"
                        "Do NOT reboot — your settings would be lost."
                    )
                    return

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
                        # Sudoers strip failed but sentinel+config are written —
                        # wizard is complete, just warn
                        pass
                    elif self._fresh_persistence:
                        # Mirror the updated sudoers too.
                        self._mirror_to_persistence_upper(SUDOERS_PATH)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

        # All mirroring done — release the staging mount of the persistence
        # partition. live-boot will mount it the proper way (with overlays) on
        # the next boot. Failure here is non-fatal: the kernel releases it on
        # reboot anyway.
        if self._persistence_staging_mount:
            try:
                subprocess.run(
                    ["sudo", "umount", self._persistence_staging_mount],
                    capture_output=True,
                    timeout=10,
                )
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
            self._persistence_staging_mount = None

        self.app.pop_screen()

        # If persistence was created this session, the union overlays aren't
        # active yet — they only activate on the next boot. Force a reboot now
        # so the user lands in a coherent state where the partition actually
        # holds their data. Skipping this step is what caused the original
        # data-loss bug (writes during this boot landed in the tmpfs overlay).
        if self._fresh_persistence:
            self.app.push_screen(_RebootPromptScreen())

    def action_cancel_wizard(self) -> None:
        # Forbid skipping when persistence was just created — the user MUST
        # reboot before doing anything else, or the partition's overlays won't
        # activate and data will be lost.
        if self._fresh_persistence:
            return
        self.app.pop_screen()


class _RebootPromptScreen(Screen):
    """Forced reboot prompt shown after creating a fresh persistence partition.

    Cannot be dismissed: skipping here would leave the user in a half-state
    where writes go to the ephemeral overlay and the persistence partition's
    overlays are dormant. Until live-boot activates the overlays on next boot,
    nothing the user does will persist.
    """

    BINDINGS = []

    def compose(self) -> ComposeResult:
        with Center(id="wizard-container"):
            with Vertical(id="wizard-box"):
                yield Static("Reboot Required", id="wiz-title")
                yield Static(
                    "Persistence partition created.\n\n"
                    "A reboot is required to activate it. Until then, any data\n"
                    "written to /var/lib/neuraldrive lives in temporary memory\n"
                    "and will be lost.\n\n"
                    "Press Enter to reboot now.",
                    id="wiz-body",
                )
                yield Static("", id="wiz-error")
                yield Button("Reboot Now", id="reboot-now", classes="primary")

    def on_mount(self) -> None:
        self.query_one("#reboot-now", Button).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "reboot-now":
            try:
                subprocess.Popen(["sudo", "systemctl", "reboot"])
            except (FileNotFoundError, OSError) as e:
                self.query_one("#wiz-error", Static).update(f"Reboot failed: {e}")

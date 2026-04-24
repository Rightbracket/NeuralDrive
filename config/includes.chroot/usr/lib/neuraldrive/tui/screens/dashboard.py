from __future__ import annotations

from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Static

from widgets.safe_header import SafeHeader

from utils import api_client, hardware
from widgets.stats_box import StatsBox


class DashboardScreen(Screen):
    BINDINGS = [("r", "refresh", "Refresh")]

    def compose(self) -> ComposeResult:
        yield SafeHeader()
        with VerticalScroll():
            with Horizontal(id="dash-topbar"):
                yield Static("", id="dash-hostname")
                yield Static("", id="dash-clock")
            with Horizontal(id="stats-panel"):
                yield StatsBox("CPU", [("Usage", "…")], id="box-cpu")
                yield StatsBox("Memory", [("Used", "…"), ("Total", "…")], id="box-mem")
                yield StatsBox("Disk", [("Used", "…"), ("Free", "…")], id="box-disk")
                yield StatsBox(
                    "GPU",
                    [("Device", "…"), ("VRAM", "…"), ("Temp", "…"), ("Util", "…")],
                    id="box-gpu",
                )
            yield Static("Active Models", classes="heading")
            yield Vertical(id="loaded-models")
            yield Static("Services", classes="heading")
            yield Vertical(id="service-badges")
        yield Footer()

    def on_mount(self) -> None:
        self._refresh_system()
        self.set_interval(2.0, self._refresh_system)
        self._refresh_models()
        self.set_interval(10.0, self._refresh_models)

    def _refresh_system(self) -> None:
        hostname = hardware.get_hostname()
        ip = hardware.get_ip_address()
        uptime = hardware.get_uptime()
        self.query_one("#dash-hostname", Static).update(
            f"  {hostname}  •  {ip}  •  up {uptime}"
        )
        now = datetime.now().strftime("%H:%M:%S")
        self.query_one("#dash-clock", Static).update(now)

        cpu = hardware.get_cpu_percent()
        self.query_one("#box-cpu", StatsBox).update_row("Usage", f"{cpu:.0f}%")

        mem = hardware.get_memory_info()
        box_mem = self.query_one("#box-mem", StatsBox)
        box_mem.update_row("Used", f"{mem['used_gb']} GB")
        box_mem.update_row("Total", f"{mem['total_gb']} GB")

        disk = hardware.get_disk_info()
        box_disk = self.query_one("#box-disk", StatsBox)
        box_disk.update_row("Used", f"{disk['used_gb']} GB ({disk['percent']}%)")
        box_disk.update_row("Free", f"{disk['free_gb']} GB")

        gpu = hardware.get_gpu_info()
        box_gpu = self.query_one("#box-gpu", StatsBox)
        if gpu["devices"]:
            dev = gpu["devices"][0]
            box_gpu.update_row("Device", dev["name"])
            vram_total = dev["vram_total_mb"]
            vram_used = dev["vram_used_mb"]
            box_gpu.update_row("VRAM", f"{vram_used} / {vram_total} MB")
            box_gpu.update_row("Temp", f"{dev['temp_c']}\u00b0C")
            box_gpu.update_row("Util", f"{dev['util_percent']}%")
        else:
            box_gpu.update_row("Device", gpu["vendor"])

        container = self.query_one("#service-badges", Vertical)
        container.remove_children()
        for svc in hardware.NEURALDRIVE_SERVICES:
            status = hardware.get_service_status(svc)
            cls = "badge-online" if status == "active" else "badge-offline"
            short = svc.replace("neuraldrive-", "")
            container.mount(
                Static(f"  {'●' if status == 'active' else '○'} {short}", classes=cls)
            )

    def _refresh_models(self) -> None:
        self.app.call_later(self._refresh_models_async)

    async def _refresh_models_async(self) -> None:
        running = await api_client.list_running_models()
        container = self.query_one("#loaded-models", Vertical)
        container.remove_children()
        if not running:
            container.mount(Static("  No models loaded", classes="muted"))
        else:
            for m in running:
                name = m.get("name", "unknown")
                size_vram = m.get("size_vram", 0)
                size_bytes = m.get("size", 0)
                if size_vram and size_vram > 0:
                    vram_gb = f"{size_vram / (1024**3):.1f} GB"
                    tag = f"[GPU] {vram_gb}"
                else:
                    ram_gb = f"{size_bytes / (1024**3):.1f} GB" if size_bytes else ""
                    tag = f"[CPU] {ram_gb}"
                container.mount(Static(f"  ● {name}  {tag}", classes="ok"))

    def action_refresh(self) -> None:
        self._refresh_system()
        self._refresh_models()

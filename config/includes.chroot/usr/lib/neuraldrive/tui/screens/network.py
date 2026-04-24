from __future__ import annotations

import psutil

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Static

from widgets.safe_header import SafeHeader

from utils import hardware


class NetworkScreen(Screen):
    BINDINGS = [("r", "refresh", "Refresh")]

    def compose(self) -> ComposeResult:
        yield SafeHeader()
        with VerticalScroll():
            yield Static("Network Configuration", classes="heading")
            yield Static("", id="net-hostname")
            yield Static("", id="net-ip")
            yield Static("Interfaces", classes="heading")
            yield Vertical(id="net-ifaces")
            yield Static("Access URLs", classes="heading")
            yield Static("", id="net-urls")
        yield Footer()

    def on_mount(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        hostname = hardware.get_hostname()
        ip = hardware.get_ip_address()
        self.query_one("#net-hostname", Static).update(f"  Hostname: {hostname}")
        self.query_one("#net-ip", Static).update(f"  Primary IP: {ip}")

        container = self.query_one("#net-ifaces", Vertical)
        container.remove_children()
        try:
            addrs = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            for iface in sorted(addrs.keys()):
                if iface == "lo":
                    continue
                is_up = stats.get(iface, None)
                up_str = "UP" if is_up and is_up.isup else "DOWN"
                ipv4 = ""
                for addr in addrs[iface]:
                    if addr.family.name == "AF_INET":
                        ipv4 = addr.address
                        break
                cls = "ok" if up_str == "UP" else "error"
                container.mount(
                    Static(
                        f"  {iface}: {ipv4 or 'no address'}  [{up_str}]", classes=cls
                    )
                )
        except Exception:
            container.mount(Static("  Unable to enumerate interfaces", classes="error"))

        urls = (
            f"  Web UI: https://{ip}/\n  API:    https://{ip}/api/"
            if ip != "no network"
            else "  No network available"
        )
        self.query_one("#net-urls", Static).update(urls)

    def action_refresh(self) -> None:
        self._refresh()

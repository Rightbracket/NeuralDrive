from __future__ import annotations

import asyncio
import json

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Input, ProgressBar, Static

from widgets.safe_header import SafeHeader

from textual.binding import Binding

from utils import api_client, config
from widgets.model_item import ModelItem

CURATED_MODELS = [
    (
        "CPU / ≤4 GB VRAM",
        [
            ("qwen2.5:3b", "1.9 GB", "Fast general-purpose"),
            ("phi3:mini", "2.3 GB", "Microsoft reasoning model"),
            ("gemma2:2b", "1.6 GB", "Google lightweight"),
        ],
    ),
    (
        "6 GB VRAM",
        [
            ("llama3.2:3b", "2.0 GB", "Meta compact model"),
            ("mistral:7b", "4.1 GB", "Mistral AI flagship"),
            ("qwen2.5:7b", "4.7 GB", "Strong multilingual"),
        ],
    ),
    (
        "8 GB VRAM",
        [
            ("llama3.1:8b", "4.7 GB", "Meta general-purpose"),
            ("gemma2:9b", "5.4 GB", "Google mid-range"),
            ("deepseek-coder-v2:lite", "5.0 GB", "Code-focused"),
        ],
    ),
    (
        "12 GB VRAM",
        [
            ("codestral:latest", "12 GB", "Mistral code generation"),
            ("llama3.1:8b-instruct-q8_0", "8.5 GB", "High-quality quantization"),
            ("qwen2.5:14b", "9.0 GB", "Strong reasoning"),
        ],
    ),
    (
        "24 GB+ VRAM",
        [
            ("llama3.1:70b", "40 GB", "Meta flagship (Q4)"),
            ("qwen2.5:32b", "20 GB", "Top-tier multilingual"),
            ("deepseek-coder-v2:16b", "8.9 GB", "Full code model"),
        ],
    ),
]


class ModelCatalog(Screen):
    BINDINGS = [
        ("escape", "cancel", "Back"),
        Binding("up", "nav_up", show=False, priority=True),
        Binding("down", "nav_down", show=False, priority=True),
        Binding("pageup", "page_up", show=False, priority=True),
        Binding("pagedown", "page_down", show=False, priority=True),
        Binding("enter", "activate", show=False, priority=True),
        Binding("space", "activate", show=False, priority=True),
        Binding("tab", "next_zone", show=False, priority=True),
        Binding("shift+tab", "prev_zone", show=False, priority=True),
    ]

    def __init__(self, installed_names: set[str]) -> None:
        super().__init__()
        self._installed = installed_names
        self._selected: set[str] = set()
        self._catalog_buttons: list[Button] = []
        self._highlight_index = 0
        self._zone = "list"

    def compose(self) -> ComposeResult:
        yield SafeHeader()
        yield Static(
            "  ↑↓ Navigate   Enter Select   Tab Actions   Esc Back", classes="muted"
        )
        with VerticalScroll(id="catalog-scroll"):
            for tier_label, models in CURATED_MODELS:
                yield Static(f"  {tier_label}", classes="tier-heading")
                for model_name, size, desc in models:
                    installed = any(
                        model_name == n or model_name == n.split(":")[0]
                        for n in self._installed
                    )
                    if installed:
                        label = f"  ✓  {model_name}  ({size}) — {desc}  [installed]"
                        btn = Button(
                            label,
                            id=f"cat-{model_name.replace(':', '--').replace('.', '-')}",
                            classes="catalog-item catalog-installed",
                            disabled=True,
                        )
                    else:
                        label = f"  ○  {model_name}  ({size}) — {desc}"
                        btn = Button(
                            label,
                            id=f"cat-{model_name.replace(':', '--').replace('.', '-')}",
                            classes="catalog-item",
                        )
                    btn.tooltip = model_name
                    btn.can_focus = False
                    yield btn
        with Horizontal(id="catalog-buttons"):
            yield Button("Download Selected", id="download-selected", variant="primary")
            yield Button("Cancel", id="catalog-cancel")
        yield Footer()

    def on_mount(self) -> None:
        self._catalog_buttons = list(self.query("Button.catalog-item"))
        self._zone = "list"
        self._highlight_index = 0
        self.set_focus(None)
        if self._catalog_buttons:
            self._apply_highlight()

    def _apply_highlight(self) -> None:
        for i, btn in enumerate(self._catalog_buttons):
            if i == self._highlight_index:
                btn.add_class("catalog-highlighted")
                btn.scroll_visible()
            else:
                btn.remove_class("catalog-highlighted")

    def _clear_highlight(self) -> None:
        for btn in self._catalog_buttons:
            btn.remove_class("catalog-highlighted")

    def _toggle_highlighted(self) -> None:
        if not self._catalog_buttons:
            return
        btn = self._catalog_buttons[self._highlight_index]
        if btn.disabled:
            return
        model_name = btn.tooltip or ""
        if not model_name:
            return
        if model_name in self._selected:
            self._selected.discard(model_name)
            btn.label = str(btn.label).replace("  ✓  ", "  ○  ")
            btn.remove_class("catalog-checked")
        else:
            self._selected.add(model_name)
            btn.label = str(btn.label).replace("  ○  ", "  ✓  ")
            btn.add_class("catalog-checked")

    def action_nav_up(self) -> None:
        if self._zone == "buttons":
            self._zone = "list"
            self.set_focus(None)
            self._apply_highlight()
            return
        if self._catalog_buttons and self._highlight_index > 0:
            self._highlight_index -= 1
            self._apply_highlight()

    def action_nav_down(self) -> None:
        if self._zone == "list" and self._catalog_buttons:
            if self._highlight_index < len(self._catalog_buttons) - 1:
                self._highlight_index += 1
                self._apply_highlight()

    def action_page_up(self) -> None:
        if self._zone == "buttons":
            self._zone = "list"
            self.set_focus(None)
            self._apply_highlight()
            return
        if not self._catalog_buttons:
            return
        scroll = self.query_one("#catalog-scroll", VerticalScroll)
        page_size = max(1, scroll.size.height // 3)
        self._highlight_index = max(0, self._highlight_index - page_size)
        self._apply_highlight()

    def action_page_down(self) -> None:
        if not self._catalog_buttons:
            return
        if self._zone == "buttons":
            return
        scroll = self.query_one("#catalog-scroll", VerticalScroll)
        page_size = max(1, scroll.size.height // 3)
        last = len(self._catalog_buttons) - 1
        self._highlight_index = min(last, self._highlight_index + page_size)
        self._apply_highlight()

    def action_activate(self) -> None:
        if self._zone == "list":
            self._toggle_highlighted()
        else:
            focused = self.focused
            if focused and focused.id == "download-selected":
                self.dismiss(list(self._selected))
            elif focused and focused.id == "catalog-cancel":
                self.dismiss([])

    def action_next_zone(self) -> None:
        if self._zone == "list":
            self._zone = "buttons"
            self._clear_highlight()
            self.query_one("#download-selected", Button).focus()
        else:
            focused = self.focused
            if focused and focused.id == "download-selected":
                self.query_one("#catalog-cancel", Button).focus()
            else:
                self.query_one("#download-selected", Button).focus()

    def action_prev_zone(self) -> None:
        if self._zone == "buttons":
            self._zone = "list"
            self.set_focus(None)
            self._apply_highlight()

    def action_cancel(self) -> None:
        self.dismiss([])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id or ""
        if btn_id == "download-selected":
            self.dismiss(list(self._selected))
        elif btn_id == "catalog-cancel":
            self.dismiss([])


class ModelsScreen(Screen):
    BINDINGS = [
        ("r", "refresh", "Refresh"),
        Binding("up", "nav_up", show=False, priority=True),
        Binding("down", "nav_down", show=False, priority=True),
        Binding("left", "nav_left", show=False, priority=True),
        Binding("right", "nav_right", show=False, priority=True),
        Binding("pageup", "page_up", show=False, priority=True),
        Binding("pagedown", "page_down", show=False, priority=True),
        Binding("enter", "activate", show=False, priority=True),
        Binding("tab", "next_zone", show=False, priority=True),
        Binding("shift+tab", "prev_zone", show=False, priority=True),
    ]

    ZONES = ["models", "browse", "pull-input", "pull-btn"]

    def compose(self) -> ComposeResult:
        yield SafeHeader()
        yield Static("Installed Models", classes="heading")
        with Horizontal(id="model-legend"):
            yield Static("Model", classes="legend-name")
            yield Static("Params", classes="legend-col legend-params")
            yield Static("Quant", classes="legend-col legend-quant")
            yield Static("Disk", classes="legend-col legend-disk")
            yield Static("VRAM", classes="legend-col legend-vram")
            yield Static("Status", classes="legend-col legend-status")
        yield VerticalScroll(id="model-list")
        yield Button(
            "Browse Available Models",
            id="open-catalog",
            variant="primary",
            classes="primary",
        )
        yield Static("Pull by Name", classes="heading")
        with Horizontal(id="pull-input-row"):
            yield Input(placeholder="e.g. llama3:8b", id="pull-input")
            yield Button("Pull", id="pull-btn")
        yield Static("", id="model-status")
        with Horizontal(id="pull-row"):
            yield ProgressBar(total=100, show_eta=True, id="pull-progress")
            yield Button("Cancel", id="cancel-pull", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#pull-progress", ProgressBar).display = False
        self.query_one("#cancel-pull", Button).display = False
        self._pull_queue: list[str] = []
        self._pulling = False
        self._model_items: list[ModelItem] = []
        self._highlight_index = 0
        self._btn_index = 0
        self._zone = "models"
        self.action_refresh()

    # ── Zone management ──────────────────────────────────────

    def _enter_zone(self, zone: str) -> None:
        self._zone = zone
        if zone == "models":
            self.set_focus(None)
            self._apply_highlight()
        elif zone == "browse":
            self._clear_highlight()
            self.query_one("#open-catalog", Button).focus()
        elif zone == "pull-input":
            self._clear_highlight()
            self.query_one("#pull-input", Input).focus()
        elif zone == "pull-btn":
            self._clear_highlight()
            self.query_one("#pull-btn", Button).focus()

    def action_next_zone(self) -> None:
        idx = self.ZONES.index(self._zone) if self._zone in self.ZONES else 0
        idx = (idx + 1) % len(self.ZONES)
        self._enter_zone(self.ZONES[idx])

    def action_prev_zone(self) -> None:
        idx = self.ZONES.index(self._zone) if self._zone in self.ZONES else 0
        idx = (idx - 1) % len(self.ZONES)
        self._enter_zone(self.ZONES[idx])

    # ── Model list highlight ─────────────────────────────────

    def _apply_highlight(self) -> None:
        self._clear_btn_highlight()
        for i, item in enumerate(self._model_items):
            if i == self._highlight_index:
                item.add_class("model-highlighted")
                item.scroll_visible()
                self._apply_btn_highlight()
            else:
                item.remove_class("model-highlighted")

    def _clear_highlight(self) -> None:
        self._clear_btn_highlight()
        for item in self._model_items:
            item.remove_class("model-highlighted")

    # ── Per-model button highlight ───────────────────────────

    def _get_active_buttons(self) -> list[Button]:
        if not self._model_items:
            return []
        item = self._model_items[self._highlight_index]
        return [b for b in item.get_action_buttons() if not b.disabled]

    def _apply_btn_highlight(self) -> None:
        buttons = self._get_active_buttons()
        if not buttons:
            return
        self._btn_index = max(0, min(self._btn_index, len(buttons) - 1))
        for i, btn in enumerate(buttons):
            if i == self._btn_index:
                btn.add_class("model-btn-active")
            else:
                btn.remove_class("model-btn-active")

    def _clear_btn_highlight(self) -> None:
        for item in self._model_items:
            for btn in item.get_action_buttons():
                btn.remove_class("model-btn-active")

    # ── Navigation actions ───────────────────────────────────

    def action_nav_up(self) -> None:
        if self._zone != "models":
            return
        if self._model_items and self._highlight_index > 0:
            self._highlight_index -= 1
            self._apply_highlight()

    def action_nav_down(self) -> None:
        if self._zone != "models":
            return
        if self._model_items and self._highlight_index < len(self._model_items) - 1:
            self._highlight_index += 1
            self._apply_highlight()

    def action_nav_left(self) -> None:
        if self._zone != "models":
            return
        if self._btn_index > 0:
            self._btn_index -= 1
            self._apply_btn_highlight()

    def action_nav_right(self) -> None:
        if self._zone != "models":
            return
        buttons = self._get_active_buttons()
        if self._btn_index < len(buttons) - 1:
            self._btn_index += 1
            self._apply_btn_highlight()

    def action_page_up(self) -> None:
        if self._zone != "models" or not self._model_items:
            return
        scroll = self.query_one("#model-list", VerticalScroll)
        page_size = max(1, scroll.size.height // 6)
        self._highlight_index = max(0, self._highlight_index - page_size)
        self._apply_highlight()

    def action_page_down(self) -> None:
        if self._zone != "models" or not self._model_items:
            return
        scroll = self.query_one("#model-list", VerticalScroll)
        page_size = max(1, scroll.size.height // 6)
        last = len(self._model_items) - 1
        self._highlight_index = min(last, self._highlight_index + page_size)
        self._apply_highlight()

    def action_activate(self) -> None:
        if self._zone == "models":
            buttons = self._get_active_buttons()
            if buttons and 0 <= self._btn_index < len(buttons):
                btn = buttons[self._btn_index]
                if not btn.disabled:
                    btn.press()
        elif self._zone == "browse":
            self.query_one("#open-catalog", Button).press()
        elif self._zone == "pull-input":
            inp = self.query_one("#pull-input", Input)
            name = inp.value.strip()
            if name and not self._pulling:
                self._pulling = True
                self._start_pull(name)
        elif self._zone == "pull-btn":
            self.query_one("#pull-btn", Button).press()

    def action_refresh(self) -> None:
        self.app.call_later(self._load_models)

    async def _load_models(self) -> None:
        all_models = await api_client.list_models()
        running = await api_client.list_running_models()
        running_map = {m.get("name", ""): m for m in running}

        vram_cache = config.get("vram_cache", {})
        if not isinstance(vram_cache, dict):
            vram_cache = {}
        cache_changed = False
        for name, info in running_map.items():
            vram_bytes = info.get("size_vram", 0)
            if vram_bytes and vram_cache.get(name) != vram_bytes:
                vram_cache[name] = vram_bytes
                cache_changed = True
        if cache_changed:
            config.set_key("vram_cache", vram_cache)

        container = self.query_one("#model-list", VerticalScroll)
        container.remove_children()
        self._model_items = []

        if not all_models:
            container.mount(Static("  No models installed", classes="muted"))
        else:
            for m in all_models:
                name = m.get("name", "unknown")
                size_bytes = m.get("size", 0)
                size_str = f"{size_bytes / (1024**3):.1f} GB" if size_bytes else "—"
                details = m.get("details", {})
                params = details.get("parameter_size", "")
                quant = details.get("quantization_level", "")
                loaded = name in running_map

                if name in running_map:
                    vb = running_map[name].get("size_vram", 0)
                    vram_str = f"{vb / (1024**3):.1f} GB" if vb else "—"
                elif name in vram_cache:
                    vb = vram_cache[name]
                    vram_str = f"~{vb / (1024**3):.1f} GB" if vb else "—"
                else:
                    vram_str = "—"

                item = ModelItem(name, size_str, params, quant, vram_str, loaded)
                container.mount(item)
                self._model_items.append(item)

        if self._model_items:
            self._highlight_index = min(
                self._highlight_index, len(self._model_items) - 1
            )
            self._btn_index = 0
            if self._zone == "models":
                self._apply_highlight()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        btn = event.button
        btn_id = btn.id or ""
        if btn_id == "pull-btn":
            name = self.query_one("#pull-input", Input).value.strip()
            if name and not self._pulling:
                self._pulling = True
                self._start_pull(name)
        elif btn_id == "open-catalog":
            installed = {m.get("name", "") for m in await api_client.list_models()}
            self.app.push_screen(ModelCatalog(installed), self._on_catalog_result)
        elif btn_id == "cancel-pull":
            self._cancel_pull()
        elif btn.has_class("model-load"):
            self._load_to_vram(btn.name or "")
        elif btn.has_class("model-unload"):
            self._unload_from_vram(btn.name or "")
        elif btn.has_class("model-delete"):
            self._delete_model(btn.name or "")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "pull-input" and not self._pulling:
            name = event.input.value.strip()
            if name:
                self._pulling = True
                self._start_pull(name)

    def _cancel_pull(self) -> None:
        self._pull_queue.clear()
        self.workers.cancel_group(self, "default")
        self._pulling = False
        status = self.query_one("#model-status", Static)
        status.update("  Download cancelled")
        self.query_one("#pull-progress", ProgressBar).display = False
        self.query_one("#cancel-pull", Button).display = False
        self.query_one("#pull-btn", Button).disabled = False
        self.query_one("#open-catalog", Button).disabled = False

    def _on_catalog_result(self, selected: list[str]) -> None:
        if not selected:
            return
        self._pull_queue = list(selected)
        self._pull_next()

    def _pull_next(self) -> None:
        if not self._pull_queue:
            self.app.call_later(self._load_models)
            return
        model_name = self._pull_queue.pop(0)
        self._pulling = True
        self._start_pull(model_name)

    @work(exclusive=True)
    async def _start_pull(self, model_name: str) -> None:
        status = self.query_one("#model-status", Static)
        progress = self.query_one("#pull-progress", ProgressBar)
        cancel_btn = self.query_one("#cancel-pull", Button)
        pull_btn = self.query_one("#pull-btn", Button)
        catalog_btn = self.query_one("#open-catalog", Button)

        pull_btn.disabled = True
        catalog_btn.disabled = True
        progress.display = True
        cancel_btn.display = True
        self._pulling = True
        progress.update(total=100, progress=0)

        remaining = len(self._pull_queue)
        queue_msg = f"  (+{remaining} queued)" if remaining else ""
        status.update(f"Pulling {model_name}...{queue_msg}")

        try:
            async for line in api_client.pull_model(model_name):
                try:
                    data = json.loads(line)
                    msg = data.get("status", "")
                    total = data.get("total", 0)
                    completed = data.get("completed", 0)
                    if total:
                        pct = int(completed / total * 100)
                        progress.update(total=100, progress=pct)
                        size_mb = total / (1024 * 1024)
                        done_mb = completed / (1024 * 1024)
                        status.update(
                            f"{msg}  {done_mb:.0f}/{size_mb:.0f} MB  ({pct}%){queue_msg}"
                        )
                    else:
                        status.update(f"{msg}{queue_msg}")
                except json.JSONDecodeError:
                    pass
            status.update(f"✓ {model_name} pulled successfully")
            self.query_one("#pull-input", Input).value = ""
        except asyncio.CancelledError:
            status.update(f"  Download of {model_name} cancelled")
            return
        except Exception as exc:
            status.update(f"✗ Pull failed: {exc}")
        finally:
            self._pulling = False
            pull_btn.disabled = False
            catalog_btn.disabled = False
            progress.display = False
            cancel_btn.display = False

        if self._pull_queue:
            self._pull_next()
        else:
            await self._load_models()

    @work()
    async def _load_to_vram(self, model_name: str) -> None:
        status = self.query_one("#model-status", Static)
        status.update(f"Loading {model_name} into VRAM...")
        load_btn = None
        try:
            load_btn = self.query_one(
                f"Button.model-load[name='{model_name}']", Button
            )
            load_btn.label = "Loading…"
            load_btn.disabled = True
        except Exception:
            pass
        success = await api_client.load_model(model_name)
        if success:
            status.update(f"  \u2713 {model_name} loaded into VRAM")
        else:
            status.update(f"  \u2717 Failed to load {model_name}")
        await self._load_models()

    @work()
    async def _load_to_vram(self, model_name: str) -> None:
        status = self.query_one("#model-status", Static)
        status.update(f"Loading {model_name} into VRAM...")
        load_btn = self._find_model_button(model_name, "model-load")
        if load_btn:
            load_btn.label = "Loading\u2026"
            load_btn.disabled = True
        success = await api_client.load_model(model_name)
        if success:
            status.update(f"  \u2713 {model_name} loaded into VRAM")
        else:
            status.update(f"  \u2717 Failed to load {model_name}")
        await self._load_models()

    def _find_model_button(self, model_name: str, btn_class: str) -> Button | None:
        for item in self._model_items:
            if item.name == model_name:
                for btn in item.query("Button"):
                    if btn.has_class(btn_class):
                        return btn
        return None

    @work()
    async def _delete_model(self, model_name: str) -> None:
        status = self.query_one("#model-status", Static)
        running = await api_client.list_running_models()
        running_names = {m.get("name", "") for m in running}
        if model_name in running_names:
            status.update(f"Unloading {model_name} from VRAM before delete...")
            await api_client.unload_model(model_name)
        status.update(f"Deleting {model_name}...")
        success = await api_client.delete_model(model_name)
        if success:
            status.update(f"  \u2713 {model_name} deleted")
        else:
            status.update(f"  \u2717 Failed to delete {model_name}")
        await self._load_models()

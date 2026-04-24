from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, Static


class ModelItem(Horizontal):
    can_focus = False

    def __init__(
        self,
        name: str,
        size: str,
        params: str = "",
        quant: str = "",
        vram_str: str = "",
        loaded: bool = False,
    ) -> None:
        super().__init__(name=name, classes="model-item")
        self._model_name = name
        self._model_size = size
        self._params = params
        self._quant = quant
        self._vram_str = vram_str
        self._loaded = loaded

    def compose(self) -> ComposeResult:
        yield Static(self._model_name, classes="model-name")
        yield Static(self._params, classes="model-params")
        yield Static(self._quant, classes="model-quant")
        yield Static(self._model_size, classes="model-disk")
        yield Static(self._vram_str, classes="model-vram")
        if self._loaded:
            yield Static("● GPU", classes="model-status-loaded")
        else:
            yield Static("○ ready", classes="model-status-cached")
        load_btn = Button("Load", name=self._model_name, classes="model-load")
        unload_btn = Button("Unload", name=self._model_name, classes="model-unload")
        delete_btn = Button("Delete", name=self._model_name, classes="model-delete")
        load_btn.can_focus = False
        unload_btn.can_focus = False
        delete_btn.can_focus = False
        if self._loaded:
            load_btn.disabled = True
        else:
            unload_btn.disabled = True
        yield load_btn
        yield unload_btn
        yield delete_btn

    def get_action_buttons(self) -> list[Button]:
        """Return the action buttons in left-to-right order."""
        return list(self.query("Button"))

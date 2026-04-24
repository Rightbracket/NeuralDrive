from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, Static


class ModelItem(Horizontal):
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
            yield Static("● VRAM", classes="model-status-loaded")
        else:
            yield Static("○ ready", classes="model-status-cached")
        load_btn = Button("Load", name=self._model_name, classes="model-load")
        unload_btn = Button("Unload", name=self._model_name, classes="model-unload")
        if self._loaded:
            load_btn.disabled = True
        else:
            unload_btn.disabled = True
        yield load_btn
        yield unload_btn

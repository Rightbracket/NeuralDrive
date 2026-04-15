from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static


class ModelItem(Horizontal):
    def __init__(self, name: str, size: str, loaded: bool = False) -> None:
        super().__init__(classes="model-item")
        self._name = name
        self._size = size
        self._loaded = loaded

    def compose(self) -> ComposeResult:
        yield Static(self._name, classes="model-name")
        yield Static(self._size, classes="model-size")
        status_cls = "model-status-loaded" if self._loaded else "model-status-cached"
        status_txt = "● loaded" if self._loaded else "○ cached"
        yield Static(status_txt, classes=status_cls)

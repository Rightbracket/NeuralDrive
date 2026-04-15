from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static


class StatsBox(Vertical):
    DEFAULT_CSS = ""

    def __init__(
        self,
        title: str,
        rows: list[tuple[str, str]] | None = None,
        *,
        id: str | None = None,
    ) -> None:
        super().__init__(id=id, classes="stats-box")
        self._title = title
        self._rows: list[tuple[str, str]] = rows or []

    def compose(self) -> ComposeResult:
        yield Static(self._title, classes="box-title")
        for label, value in self._rows:
            yield Static(f"{label}: ", classes="label")
            yield Static(value, classes="value", id=self._make_id(label))

    def update_row(self, label: str, value: str) -> None:
        row_id = self._make_id(label)
        try:
            widget = self.query_one(f"#{row_id}", Static)
            widget.update(value)
        except Exception:
            pass

    @staticmethod
    def _make_id(label: str) -> str:
        return "stat-" + label.lower().replace(" ", "-").replace("/", "-")

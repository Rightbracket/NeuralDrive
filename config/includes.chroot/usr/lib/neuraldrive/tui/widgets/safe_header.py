from __future__ import annotations

from textual.css.query import NoMatches
from textual.widgets import Header
from textual.widgets._header import HeaderTitle


class SafeHeader(Header):

    def _on_mount(self, event) -> None:
        original_set_title = None

        async def safe_set_title() -> None:
            try:
                self.query_one(HeaderTitle).update(self.format_title())
            except (NoMatches, Exception):
                pass

        self.watch(self.app, "title", safe_set_title)
        self.watch(self.app, "sub_title", safe_set_title)
        self.watch(self.screen, "title", safe_set_title)
        self.watch(self.screen, "sub_title", safe_set_title)

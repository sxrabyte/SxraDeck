"""Shared touch widgets: the top bar (with on-screen Back) and menu buttons."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, Static

BACK_ID = "deck-back"


class TopBar(Horizontal):
    """Persistent header: a big tappable Back button + the screen title.

    Replaces the Escape-key-only navigation so every screen can be left
    with a finger. Set ``root=True`` to turn Back into Exit on the home menu.
    """

    def __init__(self, title: str, root: bool = False) -> None:
        super().__init__(id="topbar")
        self._title = title
        self._root = root

    def compose(self) -> ComposeResult:
        label = "✕ EXIT" if self._root else "◀ BACK"
        yield Button(label, id=BACK_ID, classes="backbtn")
        yield Static(self._title, id="topbar-title")


class MenuButton(Button):
    """A full-width, finger-sized menu row.

    ``key`` is the original menu label; the button carries it as ``name`` so
    the screen can map a press back to the menu entry regardless of casing.
    ``wired`` controls the dimmed "not implemented yet" styling.
    """

    def __init__(self, key: str, wired: bool = True, kind: str = "leaf") -> None:
        marker = {"menu": "❯ ", "leaf": "∙ ", "run": "▶ "}.get(kind, "")
        classes = "menu-btn" if wired else "menu-btn menu-btn-disabled"
        super().__init__(f"{marker}{key}", name=key, classes=classes)
        self.wired = wired

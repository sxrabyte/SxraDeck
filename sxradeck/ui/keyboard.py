"""On-screen touch keyboard / keypads.

The deck has no physical keyboard, so any value a command needs
(a MAC, a BSSID, a channel, an SSID, a wordlist path) is tapped in
through one of these full-screen modal pads. Each pad returns the
typed string on OK, or ``None`` on cancel.
"""

from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static

# ─── Special key tokens (used as Button.name) ────────────────────────────────
BKSP = "__bksp__"
CLR = "__clr__"
OK = "__ok__"
CANCEL = "__cancel__"
SHIFT = "__shift__"
MODE = "__mode__"
SPACE = "__space__"

# ─── Layouts ─────────────────────────────────────────────────────────────────
_HEX_ROWS = [
    ["0", "1", "2", "3", "4"],
    ["5", "6", "7", "8", "9"],
    ["A", "B", "C", "D", "E"],
    ["F", ":", BKSP, CLR],
]

_NUM_ROWS = [
    ["1", "2", "3"],
    ["4", "5", "6"],
    ["7", "8", "9"],
    [CLR, "0", BKSP],
]

_TEXT_LOWER = [
    ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
    ["a", "s", "d", "f", "g", "h", "j", "k", "l"],
    [SHIFT, "z", "x", "c", "v", "b", "n", "m", BKSP],
    [MODE, "-", "_", ".", "/", SPACE, ":"],
]

_TEXT_SYMS = [
    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
    ["!", "@", "#", "$", "%", "&", "*", "?", "+", "="],
    ["(", ")", "[", "]", "{", "}", ",", ";", BKSP],
    [MODE, "~", "|", "\\", "'", SPACE, "."],
]

_LABELS = {
    BKSP: "⌫",      # ⌫
    CLR: "CLR",
    OK: "OK",
    CANCEL: "CANCEL",
    SHIFT: "⇧",     # ⇧
    MODE: "123",
    SPACE: "SPACE",
}


def kind_for_param(name: str) -> str:
    """Pick the right pad for a parameter name."""
    n = name.upper()
    if any(tok in n for tok in ("BSSID", "MAC", "BDADDR", "ADDR")):
        return "hex"
    if any(tok in n for tok in ("CH", "CHANNEL", "COUNT", "NUM", "PORT", "TIMES")):
        return "num"
    return "text"


class KeyboardScreen(ModalScreen[str | None]):
    """Full-screen tap keyboard. Dismisses with the typed string or None."""

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def __init__(self, title: str, value: str = "", kind: str = "text") -> None:
        super().__init__()
        self._title = title
        self._buffer = value
        self._kind = kind
        self._shift = False
        self._syms = False

    # --- layout ---------------------------------------------------------------
    def _rows(self) -> list[list[str]]:
        if self._kind == "hex":
            return _HEX_ROWS
        if self._kind == "num":
            return _NUM_ROWS
        return _TEXT_SYMS if self._syms else _TEXT_LOWER

    def _key_label(self, token: str) -> str:
        if token in _LABELS:
            return _LABELS[token]
        if self._kind == "text" and not self._syms and self._shift and token.isalpha():
            return token.upper()
        return token

    def compose(self) -> ComposeResult:
        with Vertical(id="kbd"):
            yield Static(self._title, id="kbd-title")
            yield Static(self._display_text(), id="kbd-buffer")
            with Vertical(id="kbd-keys"):
                for ri, row in enumerate(self._rows()):
                    with Horizontal(classes="kbd-row"):
                        for token in row:
                            yield self._make_key(token, ri)
                with Horizontal(classes="kbd-row kbd-actions"):
                    yield Button(_LABELS[CANCEL], name=CANCEL, classes="kbd-key kbd-cancel")
                    yield Button(_LABELS[OK], name=OK, classes="kbd-key kbd-ok")

    def _make_key(self, token: str, row_index: int) -> Button:
        classes = "kbd-key"
        if token in (BKSP, CLR, SHIFT, MODE, SPACE):
            classes += " kbd-special"
        if token == SHIFT and self._shift:
            classes += " kbd-active"
        return Button(self._key_label(token), name=token, classes=classes)

    # --- display --------------------------------------------------------------
    def _display_text(self) -> str:
        return (self._buffer or " ") + "█"  # buffer + block cursor

    def _refresh_buffer(self) -> None:
        self.query_one("#kbd-buffer", Static).update(self._display_text())

    def _rebuild_keys(self) -> None:
        """Re-render the key grid after a shift / mode toggle."""
        keys = self.query_one("#kbd-keys", Vertical)
        keys.remove_children()
        for ri, row in enumerate(self._rows()):
            krow = Horizontal(classes="kbd-row")
            keys.mount(krow)
            krow.mount(*[self._make_key(t, ri) for t in row])
        actions = Horizontal(classes="kbd-row kbd-actions")
        keys.mount(actions)
        actions.mount(
            Button(_LABELS[CANCEL], name=CANCEL, classes="kbd-key kbd-cancel"),
            Button(_LABELS[OK], name=OK, classes="kbd-key kbd-ok"),
        )

    # --- input ----------------------------------------------------------------
    @on(Button.Pressed)
    def _on_key(self, event: Button.Pressed) -> None:
        event.stop()
        token = event.button.name or ""
        if token == OK:
            self.dismiss(self._buffer)
            return
        if token == CANCEL:
            self.dismiss(None)
            return
        if token == BKSP:
            self._buffer = self._buffer[:-1]
            self._refresh_buffer()
            return
        if token == CLR:
            self._buffer = ""
            self._refresh_buffer()
            return
        if token == SPACE:
            self._buffer += " "
            self._refresh_buffer()
            return
        if token == SHIFT:
            self._shift = not self._shift
            self._rebuild_keys()
            return
        if token == MODE:
            self._syms = not self._syms
            self._shift = False
            self._rebuild_keys()
            return
        # literal character
        ch = token
        if self._kind == "text" and not self._syms and self._shift and ch.isalpha():
            ch = ch.upper()
            self._shift = False  # one-shot shift
            self._buffer += ch
            self._rebuild_keys()
            self._refresh_buffer()
            return
        self._buffer += ch
        self._refresh_buffer()

    def action_cancel(self) -> None:
        self.dismiss(None)

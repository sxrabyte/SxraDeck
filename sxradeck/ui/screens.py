"""Touch-first screens for SxraDeck.

Navigation is entirely tappable: every screen carries a TopBar with an
on-screen Back button, menu entries are big buttons, command parameters are
filled with the on-screen keyboard, and disruptive commands ask for
confirmation before running.
"""

from __future__ import annotations

import asyncio

from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, RichLog, Static

from sxradeck.core.command import Command
from sxradeck.ui.keyboard import KeyboardScreen, kind_for_param
from sxradeck.ui.widgets import BACK_ID, MenuButton, TopBar


class DeckScreen(Screen):
    """Base screen: Escape or the on-screen Back button both go back."""

    BINDINGS = [Binding("escape", "go_back", "Back")]

    def __init__(self, title: str, root: bool = False) -> None:
        super().__init__()
        self._bar_title = title
        self._root = root

    @on(Button.Pressed, f"#{BACK_ID}")
    def _handle_back(self, event: Button.Pressed) -> None:
        event.stop()
        self.action_go_back()

    def action_go_back(self) -> None:
        if self._root:
            self.app.exit()
        else:
            self.app.pop_screen()


class MenuScreen(DeckScreen):
    """A menu / submenu rendered as big tappable rows."""

    def __init__(self, title: str, entries: dict, root: bool = False) -> None:
        super().__init__(title, root=root)
        self.entries = entries

    def compose(self) -> ComposeResult:
        yield TopBar(self._bar_title, root=self._root)
        with VerticalScroll(id="menu-scroll"):
            for key, value in self.entries.items():
                if isinstance(value, dict):
                    kind, wired = "menu", True
                elif isinstance(value, Command):
                    kind, wired = "run", bool(value.cmd)
                elif callable(value):
                    kind, wired = "run", True
                else:
                    kind, wired = "leaf", False
                yield MenuButton(key, wired=wired, kind=kind)

    @on(Button.Pressed, ".menu-btn")
    def _on_menu(self, event: Button.Pressed) -> None:
        event.stop()
        key = event.button.name
        if key not in self.entries:
            return
        value = self.entries[key]
        if isinstance(value, dict):
            self.app.push_screen(MenuScreen(key, value))
        elif isinstance(value, Command):
            if not value.cmd:
                self.notify(f"{key}: not wired up yet", severity="warning")
            elif value.prompt:
                self.app.push_screen(ParamScreen(value))
            else:
                self._launch(value, {})
        elif callable(value):
            value()
        else:
            self.notify(f"{key}: not wired up yet", severity="warning")

    @work
    async def _launch(self, command: Command, params: dict) -> None:
        if command.confirm:
            ok = await self.app.push_screen_wait(ConfirmScreen(command, params))
            if not ok:
                return
        self.app.push_screen(OutputScreen(command, params))


class ParamScreen(DeckScreen):
    """Collects a command's parameters via the on-screen keyboard, then runs."""

    def __init__(self, command: Command) -> None:
        super().__init__(command.label)
        self._command = command
        self._values: dict[str, str] = {name: "" for name in command.prompt}

    def compose(self) -> ComposeResult:
        yield TopBar(self._bar_title)
        with VerticalScroll(id="param-scroll"):
            yield Static(self._command.label, classes="param-head")
            for i, name in enumerate(self._command.prompt):
                with Horizontal(classes="param-row"):
                    yield Static(name, classes="param-name")
                    yield Button(
                        "   ", id=f"pf-{i}", name=name, classes="param-edit"
                    )
            yield Button("▶ RUN", id="param-run", classes="run-btn")
        yield Static("", id="param-preview")

    def on_mount(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        for i, name in enumerate(self._command.prompt):
            btn = self.query_one(f"#pf-{i}", Button)
            val = self._values[name]
            btn.label = val if val else "tap to enter…"
        run = self.query_one("#param-run", Button)
        run.disabled = not all(self._values[n] for n in self._command.prompt)
        try:
            preview = self._command.cmd.format(**self._values)
        except (KeyError, IndexError):
            preview = self._command.cmd or ""
        self.query_one("#param-preview", Static).update(f"$ {preview}")

    @on(Button.Pressed, ".param-edit")
    def _edit_param(self, event: Button.Pressed) -> None:
        event.stop()
        self._open_keyboard(event.button.name)

    @work
    async def _open_keyboard(self, name: str) -> None:
        kind = kind_for_param(name)
        result = await self.app.push_screen_wait(
            KeyboardScreen(f"Enter {name}", self._values[name], kind)
        )
        if result is not None:
            self._values[name] = result
            self._refresh()

    @on(Button.Pressed, "#param-run")
    def _run(self, event: Button.Pressed) -> None:
        event.stop()
        self._launch()

    @work
    async def _launch(self) -> None:
        if self._command.confirm:
            ok = await self.app.push_screen_wait(
                ConfirmScreen(self._command, self._values)
            )
            if not ok:
                return
        self.app.push_screen(OutputScreen(self._command, dict(self._values)))


class ConfirmScreen(ModalScreen[bool]):
    """Yes/No gate shown before a disruptive command runs."""

    BINDINGS = [Binding("escape", "no", "Cancel")]

    def __init__(self, command: Command, params: dict) -> None:
        super().__init__()
        self._command = command
        self._params = params

    def compose(self) -> ComposeResult:
        try:
            resolved = self._command.cmd.format(**self._params)
        except (KeyError, IndexError):
            resolved = self._command.cmd or ""
        with Vertical(id="confirm-box"):
            yield Static("⚠ CONFIRM", id="confirm-title")
            yield Static(self._command.label, classes="confirm-label")
            yield Static(f"$ {resolved}", classes="confirm-cmd")
            with Horizontal(id="confirm-actions"):
                yield Button("✕ CANCEL", id="confirm-no", classes="kbd-key kbd-cancel")
                yield Button("▶ RUN", id="confirm-yes", classes="kbd-key kbd-ok")

    @on(Button.Pressed, "#confirm-yes")
    def _yes(self, event: Button.Pressed) -> None:
        event.stop()
        self.dismiss(True)

    @on(Button.Pressed, "#confirm-no")
    def _no(self, event: Button.Pressed) -> None:
        event.stop()
        self.dismiss(False)

    def action_no(self) -> None:
        self.dismiss(False)


class OutputScreen(DeckScreen):
    """Streams a command's output; STOP kills it, Back leaves (and stops it)."""

    def __init__(self, command: Command, params: dict | None = None) -> None:
        super().__init__(command.label)
        self._command = command
        self._params = params or {}
        self._proc: asyncio.subprocess.Process | None = None

    def compose(self) -> ComposeResult:
        yield TopBar(self._bar_title)
        yield RichLog(id="output", highlight=True, wrap=True, auto_scroll=True)
        with Horizontal(id="output-actions"):
            yield Button("■ STOP", id="output-stop", classes="run-btn stop-btn")

    def on_mount(self) -> None:
        self.run_worker(self._stream_output(), exclusive=True)

    async def _stream_output(self) -> None:
        log = self.query_one("#output", RichLog)
        try:
            cmd = self._command.cmd.format(**self._params)
        except (KeyError, IndexError):
            cmd = self._command.cmd or ""
        log.write(f"$ {cmd}\n")
        try:
            self._proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
        except Exception as exc:  # noqa: BLE001 - surface any launch error to the deck
            log.write(f"[failed to start: {exc}]")
            return
        assert self._proc.stdout is not None
        async for line in self._proc.stdout:
            log.write(line.decode(errors="replace").rstrip())
        await self._proc.wait()
        log.write(f"\n[exit {self._proc.returncode}]")
        self._stop_disabled()

    def _stop_disabled(self) -> None:
        try:
            self.query_one("#output-stop", Button).disabled = True
        except Exception:  # noqa: BLE001 - screen may already be gone
            pass

    @on(Button.Pressed, "#output-stop")
    def _stop(self, event: Button.Pressed) -> None:
        event.stop()
        self._terminate()
        self._stop_disabled()

    def _terminate(self) -> None:
        if self._proc and self._proc.returncode is None:
            try:
                self._proc.terminate()
            except ProcessLookupError:
                pass

    def action_go_back(self) -> None:
        self._terminate()
        super().action_go_back()

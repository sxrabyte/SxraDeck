"""Headless touch-UI tests driven by Textual's Pilot.

Run with: python -m pytest   (or just: python tests/test_ui.py)
No physical terminal or display is needed; Pilot simulates taps.
"""

import asyncio

from textual.widgets import Button, RichLog

from sxradeck.core.command import Command
from sxradeck.ui.app import SxraDeck
from sxradeck.ui.keyboard import KeyboardScreen, kind_for_param
from sxradeck.ui.screens import ConfirmScreen, MenuScreen, OutputScreen, ParamScreen
from sxradeck.ui.widgets import MenuButton

PANEL = (60, 20)  # ~ Waveshare 3.5B at a readable font


def _btn(screen, name):
    for b in screen.query(Button):
        if b.name == name:
            return b
    raise AssertionError(f"no button name={name!r} on {type(screen).__name__}")


def _log_text(screen):
    """Plain text of the RichLog (Strip.text joins segments; str() does not)."""
    return "\n".join(s.text for s in screen.query_one("#output", RichLog).lines)


def test_kind_for_param():
    assert kind_for_param("BSSID") == "hex"
    assert kind_for_param("target MAC") == "hex"
    assert kind_for_param("CH") == "num"
    assert kind_for_param("channel") == "num"
    assert kind_for_param("SSID") == "text"
    assert kind_for_param("wordlist") == "text"


async def _nav_flow():
    app = SxraDeck()
    async with app.run_test(size=PANEL) as pilot:
        # home menu renders the five modules
        home = app.screen
        assert isinstance(home, MenuScreen) and home._root
        assert [b.name for b in home.query(MenuButton)] == [
            "SHADOWSCAN", "STATIC", "BLUEJACK", "PHANTOM", "SYSCORE"
        ]

        # tap into a submenu, then leave via the on-screen Back button
        await pilot.click(MenuButton)
        await pilot.pause()
        assert isinstance(app.screen, MenuScreen) and not app.screen._root
        await pilot.click("#deck-back")
        await pilot.pause()
        assert app.screen is home

        # Escape key still works as a secondary back
        await pilot.click(MenuButton)
        await pilot.pause()
        await pilot.press("escape")
        await pilot.pause()
        assert app.screen is home


async def _output_flow():
    app = SxraDeck()
    async with app.run_test(size=PANEL) as pilot:
        app.push_screen(OutputScreen(Command("echo", cmd="echo hello-deck")))
        for _ in range(40):
            await pilot.pause(0.05)
            if "exit 0" in _log_text(app.screen):
                break
        text = _log_text(app.screen)
        assert "hello-deck" in text
        assert "exit 0" in text


async def _param_keyboard_flow():
    app = SxraDeck()
    async with app.run_test(size=PANEL) as pilot:
        cmd = Command(
            "probe", cmd="echo host {HOST} ch {CH}",
            prompt=["HOST", "CH"], confirm=True,
        )
        app.push_screen(ParamScreen(cmd))
        await pilot.pause()
        ps = app.screen
        assert ps.query_one("#param-run", Button).disabled  # nothing entered yet

        # HOST -> full keyboard; type a, b, switch layer, 1
        await pilot.click(_btn(ps, "HOST"))
        await pilot.pause()
        assert isinstance(app.screen, KeyboardScreen)
        assert app.screen._kind == "text"
        await pilot.click(_btn(app.screen, "a"))
        await pilot.click(_btn(app.screen, "b"))
        await pilot.click(_btn(app.screen, "__mode__"))
        await pilot.pause()
        await pilot.click(_btn(app.screen, "1"))
        await pilot.click(_btn(app.screen, "__ok__"))
        await pilot.pause()
        assert ps._values["HOST"] == "ab1"

        # CH -> number pad
        await pilot.click(_btn(ps, "CH"))
        await pilot.pause()
        assert app.screen._kind == "num"
        await pilot.click(_btn(app.screen, "6"))
        await pilot.click(_btn(app.screen, "__ok__"))
        await pilot.pause()
        assert ps._values["CH"] == "6"
        assert not ps.query_one("#param-run", Button).disabled

        # RUN -> confirm gate (confirm=True) -> RUN -> output
        await pilot.click("#param-run")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.click("#confirm-yes")
        for _ in range(30):
            await pilot.pause(0.05)
            if isinstance(app.screen, OutputScreen):
                break
        assert isinstance(app.screen, OutputScreen)
        for _ in range(30):
            await pilot.pause(0.05)
            if "host ab1 ch 6" in _log_text(app.screen):
                break
        assert "host ab1 ch 6" in _log_text(app.screen)


async def _hex_pad_flow():
    app = SxraDeck()
    async with app.run_test(size=PANEL) as pilot:
        cmd = Command("spoof", cmd="echo {BSSID}", prompt=["BSSID"])
        app.push_screen(ParamScreen(cmd))
        await pilot.pause()
        ps = app.screen
        await pilot.click(_btn(ps, "BSSID"))
        await pilot.pause()
        kb = app.screen
        assert kb._kind == "hex"
        for ch in ("A", "1", ":", "F"):
            await pilot.click(_btn(kb, ch))
        await pilot.click(_btn(kb, "__ok__"))
        await pilot.pause()
        assert ps._values["BSSID"] == "A1:F"


def test_navigation():
    asyncio.run(_nav_flow())


def test_output_streaming():
    asyncio.run(_output_flow())


def test_param_and_keyboard():
    asyncio.run(_param_keyboard_flow())


def test_hex_pad():
    asyncio.run(_hex_pad_flow())


if __name__ == "__main__":
    for fn in (test_kind_for_param, test_navigation, test_output_streaming,
               test_param_and_keyboard, test_hex_pad):
        fn()
        print(f"PASS {fn.__name__}")
    print("ALL TESTS PASSED")

"""SxraDeck - touch-first TUI launcher.

The whole interface is tappable: no key is required to navigate, go back, or
type a value. See sxradeck/ui/screens.py for the screen flow and
sxradeck/ui/keyboard.py for the on-screen keyboard.
"""

from pathlib import Path

from textual.app import App

from sxradeck.core.command import Command
from sxradeck.modules import SHADOWSCAN
from sxradeck.ui.screens import MenuScreen

# ─── Menu ─────────────────────────────────────────────────────────────────────
# dict      -> submenu
# Command   -> run (prompts for params first if Command.prompt is set)
# None      -> placeholder, shown dimmed as "not wired up yet"

MENU = {
    "SHADOWSCAN": {
        "FREQ_SWEEP": SHADOWSCAN.FREQ_SWEEP,
        "BLE_PULSE": SHADOWSCAN.BLE_PULSE,
        "BT_SWEEP": SHADOWSCAN.BT_SWEEP,
        "SIGNAL_MAP": SHADOWSCAN.SIGNAL_MAP,
    },

    "STATIC": {
        "DARKMODE": {
            "enable": None,
            "disable": None,
        },
        "INTERCEPT": {
            "all channels": None,
            "select channel": None,
            "target BSSID": None,
        },
        "INJECT": {
            "deauth": None,
            "fakeauth": None,
        },
        "HANDSHAKE_RIP": {
            "capture": None,
            "force deauth": None,
            "crack": None,
        },
        "ROGUE_AP": None,
        "NOISE_FLOOD": None,
    },

    "BLUEJACK": {
        "BT_INIT": None,
        "BT_SWEEP": None,
        "BLE_PULSE": None,
        "TARGET_INFO": None,
        "DEEP_PULSE": None,
        "ID_SPOOF": None,
    },

    "PHANTOM": {
        "FACE_SWAP": None,
        "BT_MASK": None,
        "DARKNET": {
            "enable": None,
            "disable": None,
            "check": None,
        },
        "TUNNEL": {
            "openvpn": None,
            "wireguard": None,
        },
        "EXPOSURE_CHECK": None,
        "DEADSWITCH": None,
    },

    "SYSCORE": {
        "SYS_VITALS": None,
        "NET_STATUS": None,
        "INTERFACE_CTL": {
            "wlan up": None,
            "wlan down": None,
            "rfkill list": None,
            "rfkill unblock": None,
        },
        "DISPLAY_CTL": None,
        "POWER_CTL": {
            "reboot": None,
            "shutdown": None,
        },
    },
}


class SxraDeck(App):
    CSS_PATH = str(Path(__file__).parent / "styles.tcss")
    TITLE = "SxraDeck"

    def on_mount(self) -> None:
        # The home menu is just a MenuScreen with root=True (Back becomes Exit).
        self.push_screen(MenuScreen("☠ SXRADECK ☠", MENU, root=True))


def main():
    SxraDeck().run()


if __name__ == "__main__":
    main()

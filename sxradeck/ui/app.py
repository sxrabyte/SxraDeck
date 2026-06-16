from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Header, ListView, ListItem, Label, Static, RichLog, Footer
from textual.containers import Center
from pathlib import Path
from sxradeck.core.command import Command
from sxradeck.modules import SHADOWSCAN
import asyncio


# ─── Menu Screen Dictionary ─────────────────────────────────────────────────────

MENU = {
    "SHADOWSCAN": {
        "FREQ_SWEEP": SHADOWSCAN.FREQ_SWEEP,
        "BLE_PULSE": SHADOWSCAN.BLE_PULSE,
        "BT_SWEEP": None,             # hcitool scan
        "SIGNAL_MAP": None,           # iw dev / hciconfig -a
    },

    "STATIC": {
        "DARKMODE": {
            "enable": None,           # airmon-ng start wlan0
            "disable": None,          # airmon-ng stop wlan0
        },
        "INTERCEPT": {
            "all channels": None,     # airodump-ng wlan0
            "select channel": None,   # airodump-ng -c <CH> wlan0 (prompt for CH)
            "target BSSID": None,     # airodump-ng --bssid <BSSID> -w out wlan0
        },
        "INJECT": {
            "deauth": None,           # aireplay-ng --deauth 10 -a <BSSID> wlan0
            "fakeauth": None,         # aireplay-ng --fakeauth 0 -a <BSSID> wlan0
        },
        "HANDSHAKE_RIP": {
            "capture": None,          # airodump-ng -c <CH> --bssid <BSSID> -w out wlan0
            "force deauth": None,     # aireplay-ng --deauth 5 -a <BSSID> wlan0
            "crack": None,            # aircrack-ng -w wordlist out.cap
        },
        "ROGUE_AP": None,             # hostapd hostapd.conf + dnsmasq
        "NOISE_FLOOD": None,          # mdk4 wlan0 b -n "SSID"
    },

    "BLUEJACK": {
        "BT_INIT": None,              # hciconfig hci0 up + piscan
        "BT_SWEEP": None,             # hcitool scan
        "BLE_PULSE": None,            # hcitool lescan
        "TARGET_INFO": None,          # hcitool info <MAC> + sdptool browse <MAC>
        "DEEP_PULSE": None,           # gatttool -b <MAC> --primary
        "ID_SPOOF": None,             # hciconfig down + bdaddr -i hci0 <MAC>
    },

    "PHANTOM": {
        "FACE_SWAP": None,            # ip link set wlan0 down + macchanger -r + up
        "BT_MASK": None,              # hciconfig hci0 down + bdaddr -i hci0 <MAC>
        "DARKNET": {
            "enable": None,           # systemctl start tor
            "disable": None,          # systemctl stop tor
            "check": None,            # curl https://check.torproject.org/api/ip
        },
        "TUNNEL": {
            "openvpn": None,          # openvpn --config file.ovpn
            "wireguard": None,        # wg-quick up wg0
        },
        "EXPOSURE_CHECK": None,       # curl ifconfig.me
        "DEADSWITCH": None,           # iptables -P OUTPUT DROP
    },

    "SYSCORE": {
        "SYS_VITALS": None,           # uname -a / vcgencmd measure_temp / free -h / df -h
        "NET_STATUS": None,           # ip a / iw dev / hciconfig -a
        "INTERFACE_CTL": {
            "wlan up": None,          # ip link set wlan0 up
            "wlan down": None,        # ip link set wlan0 down
            "rfkill list": None,      # rfkill list
            "rfkill unblock": None,   # rfkill unblock all
        },
        "DISPLAY_CTL": None,          # /sys/class/backlight/ brightness
        "POWER_CTL": {
            "reboot": None,           # sudo reboot
            "shutdown": None,         # sudo shutdown now
        },
    },
}

# ─── Output Screen ────────────────────────────────────────────────────────────────

class OutputScreen(Screen):
    BINDINGS = [Binding("escape", "go_back", "Back")]

    def __init__(self, command: Command, params: dict = {}):
        super().__init__()
        self._command = command
        self._params = params

    def compose(self) -> ComposeResult:
        yield Header()
        yield RichLog(id="output", highlight=True)
        yield Footer()

    def on_mount(self) -> None:
        self.run_worker(self._stream_output())

    async def _stream_output(self) -> None:
        log = self.query_one(RichLog)
        cmd = self._command.cmd.format(**self._params)
        log.write(f"$ {cmd}\n")
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        async for line in proc.stdout:
            log.write(line.decode(errors="replace").rstrip())
        await proc.wait()
        log.write(f"\n[exit {proc.returncode}]")

    def action_go_back(self) -> None:
        self.app.pop_screen()


# ─── Base Submenu Screen ─────────────────────────────────────────────────────

class SubMenuScreen(Screen):
    BINDINGS = [Binding("escape", "go_back", "Back")]

    def action_go_back(self) -> None:
        self.app.pop_screen()

class MenuScreen(SubMenuScreen):
    def __init__(self, title: str, entries: dict):
        super().__init__()
        self.title = title
        self.entries = entries

    def compose(self) -> ComposeResult:
        yield Header()
        with Center():
            with ListView():
                for key in self.entries.keys():
                    safe_id = key.replace(" ", "_").lower()
                    yield ListItem(Label(key), id=safe_id)

    def on_list_view_selected(self, event):
        item_id = event.item.id

        for original_key, value in self.entries.items():
            if original_key.replace(" ", "_").lower() == item_id:
                if isinstance(value, dict):
                    self.app.push_screen(MenuScreen(original_key, value))
                elif callable(value):
                    value()
                elif isinstance(value, Command):
                    self.app.push_screen(OutputScreen(value))
                elif value is None:
                    pass
                break

# ─── Main Menu ────────────────────────────────────────────────────────────────

class SxraDeck(App):
    CSS_PATH = str(Path(__file__).parent / "styles.tcss")

    def compose(self):
        base_dir = Path(__file__).parent.parent.parent
        banner = base_dir / "sxradeck" / "ui" / "banner.txt"

        with open(banner, "r", encoding="utf-8") as f:
            banner = f.read()

        yield Static(banner)
        yield Header()
        with Center():
            with ListView():
                for key in MENU.keys():
                    safe_id = key.replace(" ", "_").lower()
                    yield ListItem(Label(key), id=safe_id)

    def on_list_view_selected(self, event):
        item_id = event.item.id

        for original_key, value in MENU.items():
            if original_key.replace(" ", "_").lower() == item_id:
                if isinstance(value, dict):
                    self.app.push_screen(MenuScreen(original_key, value))
                elif callable(value):
                    value()
                elif isinstance(value, Command):
                    self.app.push_screen(OutputScreen(value))
                elif value is None:
                    pass
                break

def main():
    app = SxraDeck()
    app.run()

if __name__ == "__main__":
    main()
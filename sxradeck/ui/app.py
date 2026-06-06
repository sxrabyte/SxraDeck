from textual.app import App
from textual.widgets import Header, ListView, ListItem, Label, Static
from textual.containers import Center
from pathlib import Path

class SxraDeck(App):
    CSS_PATH = str(Path(__file__).parent / "styles.tcss")

    def compose(self):
        base_dir = Path(__file__).parent.parent.parent
        banner = base_dir / "sxradeck" / "ui" / "banner.txt"

        with open(banner, "r", encoding="utf-8") as f:
            banner = f.read()

        yield Static(banner)
        yield Header()
        yield Center(
            ListView(
                ListItem(Label("🐾 recon")),
                ListItem(Label("📡 airwave")),
                ListItem(Label("🔵 pawprint")),
                ListItem(Label("💀 ghostmode")),
                ListItem(Label("🌸 settings"))
            )
        )


if __name__ == "__main__":
    app = SxraDeck()
    app.run()
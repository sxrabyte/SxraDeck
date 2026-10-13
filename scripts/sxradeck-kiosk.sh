#!/usr/bin/env bash
# Boot-to-deck kiosk wrapper: brings up a single fullscreen, mouse-capable
# terminal on the Waveshare panel and runs the TUI inside it, so a fingertip
# on the resistive touchscreen lands as a tap in the UI.
#
# Two supported stacks (auto-detected). See docs/TOUCH-SETUP.md for the why.
#   1. Wayland kiosk:  cage + foot      (preferred; panel exposed as DRM/KMS)
#   2. X11:            startx + xterm   (fallback; panel exposed as fbdev /dev/fb1)
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INNER="$REPO/scripts/start-sxradeck.sh"

have() { command -v "$1" >/dev/null 2>&1; }

if have cage && have foot; then
    # foot reports SGR mouse; cage runs one app fullscreen on the DRM device.
    exec cage -s -- foot --font="monospace:size=10" -e "$INNER"
fi

if have startx && have xterm; then
    # Minimal X session: one fullscreen xterm (SGR mouse) running the deck.
    cat > /tmp/.sxradeck-xinitrc <<EOF
#!/bin/sh
xset s off -dpms
exec xterm -fullscreen -fa monospace -fs 11 -e "$INNER"
EOF
    exec startx /tmp/.sxradeck-xinitrc
fi

echo "sxradeck-kiosk: need either (cage + foot) or (startx + xterm) installed." >&2
echo "  Wayland:  sudo apt install cage foot" >&2
echo "  X11:      sudo apt install xserver-xorg xinit xterm" >&2
exit 1

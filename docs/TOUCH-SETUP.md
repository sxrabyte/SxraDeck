# SxraDeck — Touchscreen Setup (Waveshare 3.5B)

The UI is fully tappable (on-screen Back on every screen, big buttons, an
on-screen keyboard for every value). But a Textual app only *receives* taps if
it runs inside a terminal that reports **xterm-style mouse events**. This guide
gets touch from the panel into the app.

## The one thing that trips everyone up

A bare framebuffer console (`fbcon` on `/dev/fb1`) — the default "boot to a
glowing terminal" setup — **does not forward mouse/touch** to terminal apps.
`gpm` uses its own protocol that Textual doesn't speak. So:

> **Run the TUI inside a real terminal emulator on a minimal graphical stack.**
> Then the resistive touchscreen acts as a pointer and taps become clicks.

The `scripts/sxradeck-kiosk.sh` wrapper does exactly this and auto-picks a stack.

## Step 1 — which display stack do you have?

The Waveshare 3.5B (ILI9486 + XPT2046 resistive touch, SPI) shows up one of two ways:

```sh
ls /dev/dri/card*     # exists  -> DRM/KMS driver  -> use Wayland (cage + foot)
ls /dev/fb1           # exists  -> fbdev only      -> use X11 (startx + xterm)
cat /proc/bus/input/devices | grep -iA2 -E 'xpt2046|ads7846|touch'  # the touch device
```

- **DRM/KMS present** (`/dev/dri/cardN`, modern `panel-mipi-dbi`/tinydrm overlay):
  ```sh
  sudo apt install cage foot
  ```
- **fbdev only** (`/dev/fb1`, classic `fbtft`/`fb_ili9486`):
  ```sh
  sudo apt install xserver-xorg xinit xterm
  ```
  For X on an SPI panel you also need the framebuffer copied to it — either the
  Waveshare `LCD-show` config, or `fbcp`/`fbcp-ili9341` mirroring `fb0`→`fb1`.

## Step 2 — calibrate the resistive touch

Resistive panels are imprecise out of the box; calibrate once so taps land where
you touch.

- **Wayland / libinput**: add a udev rule with a calibration matrix, e.g.
  `/etc/udev/rules.d/99-sxradeck-touch.rules`:
  ```
  ATTRS{name}=="ADS7846 Touchscreen", ENV{LIBINPUT_CALIBRATION_MATRIX}="1 0 0 0 1 0"
  ```
  Tweak the matrix if X/Y are swapped or inverted (common on these panels, e.g.
  `0 1 0 -1 0 1` to rotate 90°).
- **X11**: `sudo apt install xinput-calibrator`, run it, paste the resulting
  `Section "InputClass"` into `/etc/X11/xorg.conf.d/99-calibration.conf`.

## Step 3 — run it

Manually, to test:
```sh
scripts/sxradeck-kiosk.sh
```
You should land on the SXRADECK menu. Tap a module — it should highlight and
open. Tap **◀ BACK** — it should return. If taps do nothing, the terminal isn't
reporting mouse (you're probably still on bare `fbcon`, not under cage/X).

## Step 4 — autostart on boot

```sh
mkdir -p ~/.config/systemd/user
cp scripts/sxradeck.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now sxradeck.service
sudo loginctl enable-linger "$USER"   # start at boot without logging in
```

Logs: `journalctl --user -u sxradeck.service -f`.

## Quick sanity check without the Pi

On any desktop, in a normal terminal:
```sh
python -m venv .venv && . .venv/bin/activate
pip install -e .
sxradeck        # or: scripts/start-sxradeck.sh
```
Your desktop terminal already reports mouse, so you can click the whole UI with
a mouse — same code path as touch on the deck.

## Notes on the panel size

480×320 is ~60×20 character cells. The UI is tuned for that: buttons are ≥3 cells
tall, the keyboard keys stretch to fill the width. If text looks cramped, drop
the terminal font size in `scripts/sxradeck-kiosk.sh` (`foot --font=...size=10`
or `xterm -fs 11`) to trade smaller glyphs for more rows.

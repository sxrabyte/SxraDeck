🐾 SxraDeck

A cute little hacker deck that fits in your pocket.

SxraDeck is a portable, terminal-based hacking toolkit built on a Raspberry Pi Zero 2 W. It boots straight into a custom TUI launcher — no desktop, no bloat, just a glowing terminal and a menu full of tools ready to go.
Designed to be carried. Designed to be used. Designed to be yours.

✨ Vision
Most pentesting setups live on a laptop. SxraDeck is different — it's a physical thing you hold, a tiny cyberdeck you can pull out anywhere. The aesthetic is intentional: cold green-on-black terminal energy with cute names for dangerous tools, because there's no reason hacking gear can't have a personality.
The goal isn't to replace a full pentesting rig. It's to be the thing you reach for when you want something small, fast, and fun — a first recon pass, a quick scan, a reason to learn something new.

🛠️ Hardware
ComponentDetailsBoardRaspberry Pi Zero 2 W (quad-core ARM, 512MB RAM)DisplayWaveshare 3.5" IPS touchscreenInputGPIO d-pad / joystickOSKali Linux ARM (headless)PowerUSB powerbank

💀 Features (planned)

🐾 prowl — network recon & host discovery
📡 airwave — WiFi scanning & monitor mode
🔵 pawprint — Bluetooth device scanner
💀 ghostmode — stay dark, minimal footprint tools
🌸 settings — configure the deck


🌐 Stack
Built entirely in Python using Textual for the TUI, gpiozero for hardware input, and subprocess for tool execution. Autolaunches on boot via a systemd service.

🔮 Status

Early stages. Hardware just arrived. The deck is being built.


made with ♡ by sxrabyte

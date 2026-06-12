✘_ ✘ SxraDeck
A pocket-sized hacker deck for the streets.
SxraDeck is a portable, terminal-based hacking toolkit built on a Raspberry Pi Zero 2 W. It boots straight into a custom TUI launcher - no desktop, no bloat, just a glowing terminal and a menu full of tools ready to go. Designed to be carried. Made to be fun 𓆩☠︎︎𓆪

⚠ㅤ Vision
Most pentesting setups live on a laptop. SxraDeck is different — it's a physical thing you hold, a tiny cyberdeck you can pull out anywhere. The aesthetic is intentional: cold neon-on-black terminal energy with dangerous tools hiding behind dangerous names, because hacking gear should have a personality that matches what it does ;)
The goal isn't to replace a full pentesting rig. It's to be the thing you reach for when you want something small, fast, and unapologetic - a first recon pass, a quick scan, a reason to learn something new.

⬡ Modules
SHADOWSCAN — network scanning, Bluetooth discovery, BLE scanning, signal mapping.
STATIC — monitor mode, packet capture, deauth and fakeauth injection, WPA handshake capture and cracking, rogue AP deployment, beacon flooding.
BLUEJACK — Bluetooth adapter initialization, device discovery, BLE scanning, target service enumeration, GATT inspection, MAC spoofing.
PHANTOM — MAC randomization, Bluetooth identity masking, Tor routing, VPN tunneling (OpenVPN / WireGuard), public IP exposure check, kill switch.
SYSCORE — system vitals, network and interface status, interface control, display brightness, power management.

❯❯❯❯ Hardware
ComponentDetailsBoardRaspberry Pi Zero 2 W (quad-core ARM, 512MB RAM)DisplayWaveshare 3.5" IPS touchscreenInputGPIO d-pad / joystickOSKali Linux ARM (headless)PowerUSB powerbank

➤ Stack
Built entirely in Python using Textual for the TUI, gpiozero for hardware input, and subprocess for tool execution. Autolaunches on boot via a systemd service.

𝐍𝐨𝐰 𝐥𝐨𝐚𝐝𝐢𝐧𝐠. . .
Early stages. Hardware just arrived. The deck is being built.



made with ♡ by sxrabyte☠︎︎

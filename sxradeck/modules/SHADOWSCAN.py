from sxradeck.core.command import Command

FREQ_SWEEP = Command("Frequency Sweep", cmd="iw dev wlan0 scan; iwlist wlan0 scanning")
BLE_PULSE = Command("Bluetooth Low Energy Pulse", cmd="hcitool lescan")
BT_SWEEP = Command("Bluetooth Sweep", cmd="hcitool scan")
SIGNAL_MAP = Command("Signal Map", cmd="iw dev; hciconfig -a")

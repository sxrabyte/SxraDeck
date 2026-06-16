from sxradeck.core.command import Command

SYS_VITALS = Command("System Vitals", cmd="uname -a; vcgencmd measure_temp; free -h; df -h")
NET_STATUS = Command("Network Status", cmd="ip a; iw dev; hciconfig -a")
IFACE_WLAN_UP = Command("WLAN Up", cmd="ip link set wlan0 up")
IFACE_WLAN_DOWN = Command("WLAN Down", cmd="ip link set wlan0 down")
IFACE_RFKILL_LIST = Command("RFKill List", cmd="rfkill list")
IFACE_RFKILL_UNBLOCK = Command("RFKill Unblock", cmd="rfkill unblock all")
DISPLAY_CTL = Command("Display Control", cmd="cat /sys/class/backlight/*/brightness")
POWER_REBOOT = Command("Reboot", cmd="sudo reboot")
POWER_SHUTDOWN = Command("Shutdown", cmd="sudo shutdown now")
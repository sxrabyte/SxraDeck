from sxradeck.core.command import Command

FACE_SWAP = Command("Face Swap", cmd="ip link set wlan0 down; macchanger -r wlan0; ip link set wlan0 up")
BT_MASK = Command("BT Mask", cmd="hciconfig hci0 down; bdaddr -i hci0 <MAC>")
DARKNET_ENABLE = Command("Enable Darknet", cmd="systemctl start tor")
DARKNET_DISABLE = Command("Disable Darknet", cmd="systemctl stop tor")
DARKNET_CHECK = Command("Check Darknet", cmd="curl https://check.torproject.org/api/ip")
TUNNEL_OPENVPN = Command("OpenVPN Tunnel", cmd="openvpn --config file.ovpn")
TUNNEL_WIREGUARD = Command("WireGuard Tunnel", cmd="wg-quick up wg0")
EXPOSURE_CHECK = Command("Exposure Check", cmd="curl ifconfig.me")
DEADSWITCH = Command("Dead Switch", cmd="iptables -P OUTPUT DROP")
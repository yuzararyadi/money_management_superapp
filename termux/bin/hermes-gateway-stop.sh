#!/data/data/com.termux/files/usr/bin/bash
# Stop the keep-running loop first (so it does not restart Hermes), then the gateway itself.
pkill -f "[h]ermes-gateway-loop"
proot-distro login debian -- /usr/local/bin/hermes gateway stop >/dev/null 2>&1
command -v termux-wake-unlock >/dev/null && termux-wake-unlock
echo "gateway stopped"

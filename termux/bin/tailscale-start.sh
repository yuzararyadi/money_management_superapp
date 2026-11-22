#!/data/data/com.termux/files/usr/bin/bash
# Tailscale inside the Debian proot (userspace networking, no root). Gives the app a private HTTPS address.
# Log: ~/.hermes-phone/tailscaled.log
mkdir -p "$HOME/.hermes-phone"
if pgrep -f "[t]ailscale-loop" >/dev/null; then echo "tailscale already running"; exit 0; fi
command -v termux-wake-lock >/dev/null && termux-wake-lock
( exec -a tailscale-loop bash -c "while true; do proot-distro login debian --shared-tmp -- bash -c \"mkdir -p /var/run/tailscale /root/.tailscale; exec /usr/local/bin/tailscaled --tun=userspace-networking --statedir=/root/.tailscale --socket=/var/run/tailscale/tailscaled.sock\" >> \$HOME/.hermes-phone/tailscaled.log 2>&1; sleep 10; done" ) </dev/null >/dev/null 2>&1 &
echo "tailscale started"

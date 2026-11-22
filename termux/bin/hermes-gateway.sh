#!/data/data/com.termux/files/usr/bin/bash
# Start the Hermes gateway (e.g. Telegram) and keep it running. Log: ~/.hermes-phone/gateway.log
# Hermes is installed inside a Debian proot (proot-distro), see docs/SETUP-TERMUX.md.
mkdir -p "$HOME/.hermes-phone"; LOG=$HOME/.hermes-phone/gateway.log
if pgrep -f "[h]ermes-gateway-loop" >/dev/null; then echo "gateway already running"; exit 0; fi
command -v termux-wake-lock >/dev/null && termux-wake-lock
( exec -a hermes-gateway-loop bash -c "
  while true; do
    echo \"\$(date \"+%F %T\") starting gateway\" >> $LOG
    proot-distro login debian --shared-tmp -- /usr/local/bin/hermes gateway run >> $LOG 2>&1
    echo \"\$(date \"+%F %T\") gateway exited (\$?), restarting in 15 s\" >> $LOG
    sleep 15
  done" ) </dev/null >/dev/null 2>&1 &
echo "gateway started (log: $LOG)"

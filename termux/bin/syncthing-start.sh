#!/data/data/com.termux/files/usr/bin/bash
# OPTIONAL: Syncthing keeps the app folder in two-way sync with a PC. Web UI: http://127.0.0.1:8384 on the phone.
mkdir -p "$HOME/.hermes-phone"
if pgrep -f "[s]yncthing-loop" >/dev/null; then echo "syncthing already running"; exit 0; fi
command -v termux-wake-lock >/dev/null && termux-wake-lock
( exec -a syncthing-loop bash -c "while true; do syncthing serve --no-browser --no-restart --home=\$HOME/.config/syncthing >> \$HOME/.hermes-phone/syncthing.log 2>&1; sleep 10; done" ) </dev/null >/dev/null 2>&1 &
echo "syncthing started"

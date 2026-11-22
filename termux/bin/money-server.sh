#!/data/data/com.termux/files/usr/bin/bash
# Money dashboard web app on port 8765, restarted automatically if it stops.
# Code + data: ~/money_management_superapp (override with MONEY_APP). Log: ~/.money-dashboard/server.log
APP="${MONEY_APP:-$HOME/money_management_superapp}"
if pgrep -f "[m]oney-server-loop" >/dev/null; then echo "money server already running"; exit 0; fi
command -v termux-wake-lock >/dev/null && termux-wake-lock
( exec -a money-server-loop bash -c "while true; do python \"$APP/serve_dashboard.py\"; sleep 10; done" ) </dev/null >/dev/null 2>&1 &
echo "money server started"

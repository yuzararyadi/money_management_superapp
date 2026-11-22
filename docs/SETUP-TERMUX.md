# Run it on an old Android phone (Termux)

This turns an unused Android phone into a small home server: the web app, the
Hermes AI agent and Tailscale, started automatically when the phone boots.
No root needed. It was tested on a Samsung Galaxy A54, and any reasonably
recent phone (Android 8+, 4 GB RAM or more) should work.

> Leave the phone plugged in. In Android settings, set Termux's battery usage
> to **Unrestricted**, or Android will stop it.

## 1. Termux and the app

Install **Termux** and **Termux:Boot** from [F-Droid](https://f-droid.org)
(the Play Store versions are outdated). Then, in Termux:

```bash
pkg update && pkg install -y python git openssh
git clone https://github.com/yuzararyadi/money_management_superapp.git ~/money_management_superapp
cd ~/money_management_superapp
MONEY_DASH_CONSOLE=1 python serve_dashboard.py     # test run, Ctrl+C to stop
```

On the phone, open http://127.0.0.1:8765. From another device on the same
Wi-Fi, use `http://<phone's Wi-Fi IP>:8765`. The PIN is in
`~/.money-dashboard/pin.txt`.

Optional: `sshd` lets you work on the phone from your PC
(`ssh -p 8022 <user>@<phone IP>`). Use an SSH key and set a password with `passwd`.

## 2. Start-up scripts

```bash
mkdir -p ~/bin ~/.termux/boot
cp termux/bin/*.sh ~/bin/ && chmod +x ~/bin/*.sh
cp termux/boot/start-services ~/.termux/boot/ && chmod +x ~/.termux/boot/start-services
cp termux/bin/hermes $PREFIX/bin/hermes && chmod +x $PREFIX/bin/hermes
~/bin/money-server.sh          # runs the server in the background, restarts it if it stops
```

Open the Termux:Boot app once, so Android allows it to run at boot.
After a reboot, `start-services` starts sshd, Hermes, Tailscale, the money
server and Syncthing (if installed).

## 3. Hermes AI agent (for "Ask Hermes" and chat recording)

At the time of writing, Hermes needed Python < 3.14, but Termux ships a newer
Python. So Hermes runs inside a small Debian system (proot, no root needed):

```bash
pkg install -y proot-distro && proot-distro install debian
proot-distro login debian
```

Inside Debian (check the [Hermes README](https://github.com/NousResearch/hermes-agent)
for the current install method):

```bash
apt update && apt install -y curl git ca-certificates
curl -LsSf https://astral.sh/uv/install.sh | sh && . ~/.local/bin/env
git clone https://github.com/NousResearch/hermes-agent.git /opt/hermes-agent
cd /opt/hermes-agent && uv venv --python 3.11 && uv pip install -e ".[all,messaging]"
ln -sf /opt/hermes-agent/.venv/bin/hermes /usr/local/bin/hermes
hermes setup        # choose your model provider; add a Telegram bot token from @BotFather
exit
```

Then:

- Copy the skill: `cp -r hermes/skills/personal-finance $PREFIX/var/lib/proot-distro/containers/debian/rootfs/root/.hermes/skills/`.
  Set the root folder path inside `SKILL.md`.
- Start the chat gateway: `~/bin/hermes-gateway.sh` (log: `~/.hermes-phone/gateway.log`).
- The web app's "Ask Hermes" button calls `proot-distro login debian ... hermes -z` by itself. Nothing else is needed.

Keep bot tokens and API keys in Hermes' own `.env`. Never paste them into a chat or commit them.

## 4. Tailscale: open it anywhere, privately, over HTTPS

1. Create a free [Tailscale](https://tailscale.com) account. Install the app on
   your own phones and laptop.
2. In the admin console, under DNS: turn on **MagicDNS** and **HTTPS certificates**.
3. On the server phone, inside Debian, install the static Tailscale binaries.
   Pick the arm64 build from https://pkgs.tailscale.com/stable/#static, then
   copy `tailscale` and `tailscaled` to `/usr/local/bin/`.
4. Back in Termux:

```bash
~/bin/tailscale-start.sh                                  # tailscaled in userspace mode
proot-distro login debian --shared-tmp -- tailscale up    # open the login link it prints
proot-distro login debian --shared-tmp -- tailscale serve --bg 8765
```

The app is now at `https://<phone-name>.<your-tailnet>.ts.net`, reachable only
from your own devices. Open it in Chrome on your phone and choose **Add to
Home screen** / **Install app**.

## 5. Optional: two-way sync with a PC (Syncthing)

If you also want the folder on your PC (for example inside OneDrive as a backup,
or to work on it with Claude Code), install Syncthing on both sides:

```bash
pkg install -y syncthing
cp termux/bin/syncthing-start.sh ~/bin/ && ~/bin/syncthing-start.sh
```

Share the `app/` folder between the phone and the PC. Make the phone the
main copy. Add `index.html` and `__pycache__` to `.stignore` on both sides.
If both sides change a ledger at the same time, the phone's server merges the
`*.sync-conflict-*.csv` copies automatically. On the PC, don't run a second
server against the same folder.

## Troubleshooting

| Problem | Check |
|---|---|
| App unreachable after a while | Termux battery usage = Unrestricted; `pgrep -af money-server-loop` |
| "Wrong PIN" | `cat ~/.money-dashboard/pin.txt` |
| Ask Hermes fails | `hermes -z "hi"` works in Termux? See `~/.money-dashboard/server.log` |
| Dashboard not updating | the server rebuilds within ~20 s of a file change; check the server log |

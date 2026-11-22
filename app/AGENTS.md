# Agent entry point

This folder holds the owner's money management and investment records.

- Recording receipts / payments / purchases (e.g. sent via chat to Hermes):
  follow **money/RECEIPTS.md** exactly.
- Budget context: money/profile.md, money/budget.md, money/wishlist.md.
- Debts, installments and money lent: money/debts.md (how to record them:
  money/RECEIPTS.md section 4c).
- Overall rules, payday workflow and the monthly investment workflow: **CLAUDE.md**.
- Do not modify portfolio.md, log.csv, reports/ or dashboard.html outside the
  monthly investment run described in CLAUDE.md.
- Main dashboard: index.html (GENERATED — never edit it by hand). The web
  server rebuilds it automatically when data files change; you can also run
  `python money/build_dashboard.py`. Layout changes go in
  money/dashboard_template.html.
- The dashboard is served by ../serve_dashboard.py (port 8765). Its "Add" tab
  sends free-text notes to Hermes (one-shot `hermes -z`, no file tools) for
  classification; the owner checks the rows and publishes them with a PIN; the
  server appends them to money/ledger/ (source `web-hermes` / `web-form`).
- If this folder is synced between devices (e.g. Syncthing), never create
  files named *.sync-conflict-* yourself.

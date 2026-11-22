#!/usr/bin/env python3
"""Build the main money dashboard (app/index.html).

Reads (read-only):
  money/ledger/*.csv, money/budget.md, money/wishlist.md, money/debts.md,
  money/RECEIPTS.md, money/settings.json, portfolio.md, log.csv
Writes:
  index.html  — single self-contained page (Chart.js via CDN); the investment
                tab embeds the existing dashboard.html, which is NOT modified.

Run after any ledger / wishlist / budget / portfolio change:
  python3 money/build_dashboard.py
"""
import csv, json, re, glob, os
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MONEY = os.path.join(ROOT, "money")
TEMPLATE = os.path.join(MONEY, "dashboard_template.html")
OUT = os.path.join(ROOT, "index.html")

# Your names and preferences live in money/settings.json (see that file).
def load_settings():
    try:
        return json.load(open(os.path.join(MONEY, "settings.json"), encoding="utf-8"))
    except (OSError, ValueError):
        return {}


SETTINGS = load_settings()
NAME_ME = SETTINGS.get("people", {}).get("me") or "Me"
NAME_PARTNER = SETTINGS.get("people", {}).get("partner") or "Partner"
# Who spent it: the ledger's `who` column (me / partner). Rows without it fall
# back to this rule: merchants starting with these prefixes are the partner's.
PARTNER_MERCHANT_PREFIXES = tuple(SETTINGS.get("partner_merchant_prefixes", []))


def who_of(row):
    w = (row.get("who") or "").strip().lower()
    if w in ("partner", "wife", "husband", "istri", "suami", NAME_PARTNER.lower()):
        return NAME_PARTNER
    if w in ("me", "saya", NAME_ME.lower()):
        return NAME_ME
    if PARTNER_MERCHANT_PREFIXES and (row.get("merchant") or "").startswith(PARTNER_MERCHANT_PREFIXES):
        return NAME_PARTNER
    return NAME_ME

# Categories that are bills / fixed lines in budget.md (not "living costs").
BILL_CATEGORIES = {"electricity", "utilities", "subscriptions", "housing",
                   "family-support", "tuition"}
SPEND_TYPES = {"expense"}  # income/transfer/investment/sinking-fund are not spending


def num(s):
    """'IDR 4,895,000' / '~4,520,010' / 'Rp1.993.560' -> int (last number in text)."""
    if s is None:
        return None
    found = re.findall(r"\d[\d.,]*\d|\d", s)
    if not found:
        return None
    n = found[-1]
    if "," in n and "." in n:
        n = n.replace(",", "")
    elif "," in n:
        n = n.replace(",", "") if re.fullmatch(r"\d{1,3}(,\d{3})+", n) else n.replace(",", ".")
    elif "." in n and re.fullmatch(r"\d{1,3}(\.\d{3})+", n):
        n = n.replace(".", "")
    try:
        return int(round(float(n)))
    except ValueError:
        return None


def md_tables(path):
    """Yield (heading, rows[list[dict]]) for each markdown table in a file."""
    if not os.path.exists(path):
        return []
    lines = open(path, encoding="utf-8").read().splitlines()
    out, heading, i = [], "", 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("#"):
            heading = ln.lstrip("#").strip()
        if ln.strip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            hdr = [c.strip() for c in ln.strip().strip("|").split("|")]
            rows, i = [], i + 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                rows.append(dict(zip(hdr, cells)))
                i += 1
            out.append((heading, rows))
            continue
        i += 1
    return out


def cycle_start(d):
    """Payday cycle runs from the 25th to the 24th of the next month."""
    if d.day >= 25:
        return date(d.year, d.month, 25)
    y, m = (d.year, d.month - 1) if d.month > 1 else (d.year - 1, 12)
    return date(y, m, 25)


def load_ledger():
    tx = []
    for f in sorted(glob.glob(os.path.join(MONEY, "ledger", "*.csv"))):
        if ".sync-conflict-" in f:  # Syncthing conflict copy: merged by the phone's server, not counted
            continue
        for r in csv.DictReader(open(f, encoding="utf-8")):
            try:
                d = datetime.strptime(r["date"].strip(), "%Y-%m-%d").date()
                amt = int(r["amount_idr"])
            except (ValueError, KeyError):
                continue
            merchant = r.get("merchant", "")
            tx.append({
                "date": d.isoformat(),
                "month": d.strftime("%Y-%m"),
                "cycle": cycle_start(d).isoformat(),
                "type": r.get("type", ""),
                "category": r.get("category", ""),
                "merchant": merchant,
                "description": r.get("description", ""),
                "amount": amt,
                "pay": r.get("payment_method", ""),
                "note": r.get("note", ""),
                "who": who_of(r),
                "bill": r.get("category", "") in BILL_CATEGORIES,
            })
    tx.sort(key=lambda t: t["date"])  # stable: same-day rows keep the order they were recorded
    for i, t in enumerate(tx):
        t["seq"] = i  # lets the dashboard show the most recently recorded same-day row first
    return tx


def load_budget():
    lines, payday = [], None
    for heading, rows in md_tables(os.path.join(MONEY, "budget.md")):
        if heading.lower().startswith("payday") and rows and "Line" in rows[0]:
            payday = heading.replace("Payday", "").strip()
            for r in rows:
                amt_txt = r.get("Amount (IDR)", "")
                rng = re.findall(r"\d[\d,]*", amt_txt)
                vals = [num(x) for x in rng]
                lines.append({
                    "no": r.get("#", ""),
                    "line": re.sub(r"\*", "", r.get("Line", "")),
                    "text": re.sub(r"\*", "", amt_txt),
                    "low": min(vals) if vals else None,
                    "high": max(vals) if vals else None,
                    "where": r.get("Where it goes", ""),
                })
    tuition = []
    for heading, rows in md_tables(os.path.join(MONEY, "budget.md")):
        if heading.lower().startswith("tuition"):
            for r in rows:
                tuition.append({"payday": r.get("Payday", ""), "set": r.get("Set aside", ""),
                                "balance": r.get("Fund balance", "")})
    emergency = {"target": None, "plan": []}
    for heading, rows in md_tables(os.path.join(MONEY, "budget.md")):
        if heading.lower().startswith("emergency fund plan"):
            emergency["target"] = num(heading)
            for r in rows:
                emergency["plan"].append({"payday": r.get("Payday", ""),
                                          "set": num(r.get("Set aside", "")) or 0,
                                          "balance": num(r.get("Planned balance", "")) or 0})
    return {"payday": payday, "lines": lines, "tuition": tuition, "emergency": emergency}


def load_wishlist():
    items = []
    for _, rows in md_tables(os.path.join(MONEY, "wishlist.md")):
        if rows and "Item" in rows[0]:
            for r in rows:
                if not r.get("Item"):
                    continue
                items.append({
                    "added": r.get("Added", ""), "item": r.get("Item", ""),
                    "price": num(r.get("Price (IDR)", "")), "need": r.get("Need/Want", ""),
                    "priority": r.get("Priority", ""), "decision": r.get("Decision", ""),
                    "target": r.get("Target month", ""), "status": r.get("Status", ""),
                })
    return items


def asset_class(t):
    t = t.lower()
    if "pasar uang" in t:
        return "Money market"
    if "saham" in t:
        return "Equity"
    if "obligasi" in t or "sukuk" in t:
        return "Bonds & sukuk"
    if "cash" in t:
        return "Cash"
    return "Other"


def load_portfolio():
    path = os.path.join(ROOT, "portfolio.md")
    txt = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
    m = re.search(r"last updated:\s*([^\n]+)", txt)
    tot = re.search(r"Total portfolio value:\s*([^\n]+)", txt)
    holdings = []
    for heading, rows in md_tables(path):
        if heading.lower().startswith("holdings"):
            for r in rows:
                holdings.append({
                    "name": r.get("Instrument", ""), "type": r.get("Type", ""),
                    "cls": asset_class(r.get("Type", "")),
                    "value": num(r.get("Current value", "")) or 0,
                    "pl": r.get("P/L %", ""),
                })
    log = []
    lp = os.path.join(ROOT, "log.csv")
    if os.path.exists(lp):
        for r in csv.DictReader(open(lp, encoding="utf-8")):
            log.append({"date": r["date"], "month": r["month_number"],
                        "actions": r["actions_summary"],
                        "value": num(r["portfolio_value_idr"]),
                        "bench": float(r["benchmark_nav"] or 0),
                        "ihsg": float(r["ihsg_close"] or 0)})
    return {"updated": m.group(1).strip() if m else "", "total_reported": num(tot.group(1)) if tot else None,
            "holdings": holdings, "log": log}


def load_debts():
    """money/debts.md -> {'owe': [...], 'lent': [...], 'payments': [...]}.
    Paid/remaining are computed here from the Payments table."""
    owe, lent, pays = [], [], []
    for heading, rows in md_tables(os.path.join(MONEY, "debts.md")):
        h = heading.lower()
        for r in rows:
            if not r.get("ID") and not r.get("Date"):
                continue
            if h.startswith("i owe"):
                owe.append({
                    "id": r.get("ID", ""), "started": r.get("Started", ""),
                    "lender": r.get("Lender / platform", ""), "what": r.get("What for", ""),
                    "total": num(r.get("Total (IDR)", "")) or 0,
                    "n": num(r.get("Installments", "")) or 1,
                    "per": num(r.get("Per installment (IDR)", "")),
                    "due": r.get("Due day", ""), "status": r.get("Status", ""),
                    "notes": r.get("Notes", ""),
                })
            elif h.startswith("owed to me"):
                lent.append({
                    "id": r.get("ID", ""), "date": r.get("Date lent", ""),
                    "who": r.get("Borrower", ""), "why": r.get("Reason", ""),
                    "total": num(r.get("Amount (IDR)", "")) or 0,
                    "expected": r.get("Expected back", ""), "status": r.get("Status", ""),
                    "notes": r.get("Notes", ""),
                })
            elif h.startswith("payments"):
                pays.append({
                    "date": r.get("Date", ""), "id": r.get("ID", "").strip(),
                    "amount": num(r.get("Amount (IDR)", "")) or 0,
                    "method": r.get("Method", ""), "note": r.get("Note", ""),
                })
    for item in owe + lent:
        mine = [p for p in pays if p["id"] == item["id"]]
        item["paid"] = sum(p["amount"] for p in mine)
        item["count"] = len(mine)
        item["remaining"] = max(0, item["total"] - item["paid"])
        item["last"] = max((p["date"] for p in mine), default="")
    pays.sort(key=lambda p: p["date"], reverse=True)
    return {"owe": owe, "lent": lent, "payments": pays}


def load_categories():
    """[{name, examples}] from the category table in money/RECEIPTS.md, so the
    Add form offers exactly the categories Hermes uses."""
    out = []
    for _, rows in md_tables(os.path.join(MONEY, "RECEIPTS.md")):
        if rows and "category" in rows[0]:
            for r in rows:
                if r.get("category"):
                    out.append({"name": r["category"], "examples": re.sub(r"`", "", r.get("examples", ""))})
    return out


def find_sync_conflicts():
    """Syncthing conflict copies anywhere in the folder (both sides edited a file
    at once). Ledger CSVs are merged automatically by the phone's server; any
    other file needs a human look, so the dashboard shows a warning."""
    out = []
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in (".stversions", ".stfolder", "__pycache__")]
        for fn in files:
            if ".sync-conflict-" in fn:
                out.append(os.path.relpath(os.path.join(root, fn), ROOT).replace("\\", "/"))
    return sorted(out)


def main():
    data = {
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "tx": load_ledger(),
        "budget": load_budget(),
        "wishlist": load_wishlist(),
        "portfolio": load_portfolio(),
        "people": {"me": NAME_ME, "partner": NAME_PARTNER},
        "privateNames": SETTINGS.get("private_names", []),
        "debts": load_debts(),
        "categories": load_categories(),
        "conflicts": find_sync_conflicts(),
        "billCategories": sorted(BILL_CATEGORIES),
    }
    html = open(TEMPLATE, encoding="utf-8").read()
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = html.replace("/*__DATA__*/null", payload)
    open(OUT, "w", encoding="utf-8").write(html)
    print(f"wrote {OUT}: {len(data['tx'])} ledger rows, {len(data['wishlist'])} wishlist items, "
          f"{len(data['portfolio']['holdings'])} holdings, "
          f"{len(data['debts']['owe'])} debts, {len(data['debts']['lent'])} loans out")


if __name__ == "__main__":
    main()

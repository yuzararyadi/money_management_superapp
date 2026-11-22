#!/usr/bin/env python3
"""Write a FAKE sample ledger (money/ledger/*.csv) around today's date, so a
fresh install shows a filled-in dashboard. All names and amounts are made up.

    python money/make_sample_data.py          # writes sample rows
    python money/make_sample_data.py --clear  # deletes ALL ledger CSVs (start your own)

Do not run it once you have real data: it overwrites the ledger files it writes.
"""
import csv, glob, os, random, sys
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(ROOT, "ledger")
HEADER = ["date", "type", "category", "merchant", "description", "amount_idr",
          "payment_method", "source", "note", "who"]
os.makedirs(LEDGER, exist_ok=True)

if "--clear" in sys.argv:
    for f in glob.glob(os.path.join(LEDGER, "*.csv")):
        os.remove(f)
    print("ledger cleared")
    sys.exit(0)

random.seed(7)
today = date.today()
start = today - timedelta(days=58)

DAILY = [  # (category, merchant, description, low, high, who, method)
    ("groceries", "Indomaret", "household groceries", 40_000, 180_000, "partner", "QRIS"),
    ("groceries", "Supermarket", "weekly groceries", 250_000, 650_000, "partner", "debit"),
    ("dining", "Warung Padang", "nasi padang", 20_000, 45_000, "me", "QRIS"),
    ("dining", "Coffee shop", "coffee", 25_000, 55_000, "me", "GoPay"),
    ("transport", "Pertamina", "fuel", 50_000, 200_000, "me", "debit"),
    ("transport", "Ride-hailing", "ride", 15_000, 60_000, "partner", "OVO"),
    ("kids", "Toy store", "toys", 50_000, 250_000, "partner", "QRIS"),
    ("personal", "Online shop", "clothes", 100_000, 400_000, "partner", "ShopeePay"),
    ("household", "Hardware store", "small home items", 30_000, 200_000, "me", "cash"),
    ("health", "Pharmacy", "medicine", 30_000, 150_000, "me", "debit"),
]
MONTHLY = [  # (day, type, category, merchant, description, amount, who, method)
    (25, "income", "income", "Employer", "salary", 25_000_000, "me", "transfer"),
    (26, "expense", "education", "School", "school fee", 1_500_000, "me", "transfer"),
    (26, "expense", "family-support", "Parents", "monthly support", 1_000_000, "me", "transfer"),
    (27, "expense", "electricity", "PLN", "electricity token", 500_000, "me", "QRIS"),
    (28, "expense", "utilities", "Internet provider", "home internet", 350_000, "me", "auto-debit"),
    (3, "expense", "subscriptions", "Anthropic", "Claude subscription", 330_000, "me", "credit card"),
    (5, "expense", "housing", "Housing estate", "IPL (estate fee)", 300_000, "me", "transfer"),
    (26, "sinking-fund", "emergency-fund", "Money market fund", "emergency fund top-up", 3_000_000, "me", "transfer"),
    (27, "investment", "investment", "Bibit", "monthly investment", 2_000_000, "me", "transfer"),
]

rows = []
d = start
while d <= today:
    for _ in range(random.choice([0, 1, 1, 2, 2, 3])):
        cat, merch, desc, lo, hi, who, pay = random.choice(DAILY)
        amt = round(random.randint(lo, hi), -3)
        rows.append([d.isoformat(), "expense", cat, merch, desc, amt, pay, "sample", "", who])
    for day, typ, cat, merch, desc, amt, who, pay in MONTHLY:
        if d.day == day:
            rows.append([d.isoformat(), typ, cat, merch, desc, amt, pay, "sample", "", who])
    d += timedelta(days=1)
# one installment payment and one repayment from a friend (see money/debts.md)
mid = (start + timedelta(days=30)).isoformat()
rows.append([mid, "expense", "installment", "Paylater", "new phone installment 2/6", 750_000, "paylater", "sample", "D1 installment 2/6", "me"])
rows.append([mid, "lend-repaid", "debt", "Budi", "partial repayment", 300_000, "transfer", "sample", "L1 partial repayment", "me"])

by_month = {}
for r in sorted(rows, key=lambda r: r[0]):
    by_month.setdefault(r[0][:7], []).append(r)
for month, rs in by_month.items():
    with open(os.path.join(LEDGER, f"{month}.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(HEADER)
        w.writerows(rs)
print(f"wrote {len(rows)} sample rows into {len(by_month)} ledger files")

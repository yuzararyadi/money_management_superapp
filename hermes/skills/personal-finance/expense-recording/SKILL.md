---
name: expense-recording
description: Record receipts/expenses into the money ledger.
version: 1.1.0
license: MIT
platforms: [linux, android, windows]
metadata:
  hermes:
    tags: [finance, expense, receipt, ledger, budget, money]
    category: personal-finance
---

# Expense Recording Skill

Records receipts, transfer screenshots, and short text messages about
spending/income into the owner's money ledger, and replies with a short
budget status — over chat (Telegram, WhatsApp, …).

Install: copy this folder to `~/.hermes/skills/personal-finance/expense-recording/`
and set the root folder below to where your `app/` folder lives.

## When to Use

The user sends a **receipt photo**, a **transfer/bank screenshot**, or a
**text message** like "token listrik 500rb", "bayar sekolah 1,5jt", or
"gajian masuk". Also when the user asks "can I buy X?".

## Root folder (source of truth)

`/data/data/com.termux/files/home/money_management_superapp/app/`
(change this to your own path)

The authority for HOW to record is **`money/RECEIPTS.md`** — read it every
time (it may change). Read **`money/profile.md`**, **`money/budget.md`** and
**`money/settings.json`** (names) for context before recording. This skill
mirrors RECEIPTS.md; if they disagree, RECEIPTS.md wins.

## Files (relative to root)

- `money/ledger/YYYY-MM.csv` — the transaction ledger (one file per month,
  named by the TRANSACTION date).
- `money/profile.md` — income, fixed/periodic costs. Read-only here.
- `money/budget.md` — the payday plan. Read-only here (never change amounts).
- `money/wishlist.md` — purchase decisions. UPDATE here when a wishlist item
  is bought.
- `money/debts.md` — installments and loans (RECEIPTS.md section 4c).
- `CLAUDE.md` — overall rules + purchase-decision rule. Read-only.
- `portfolio.md`, `log.csv`, `reports/`, `dashboard.html` — investment
  records. **NEVER edit these** from this skill.

## Procedure

1. **Extract** date, merchant, description, amount (whole rupiah, no
   separators: Rp527.500 → `527500`), payment method (card numbers: last 4
   digits only). If the total or date can't be read with confidence, DO NOT
   guess — ask, and record nothing until the owner answers.
2. **Classify** `type`, `category` and `who` exactly as RECEIPTS.md section 2 says.
3. **Record**: append one row to `money/ledger/YYYY-MM.csv` with the 10-column
   header from RECEIPTS.md. Duplicate check first (same date + merchant +
   amount → ask). Never edit/delete existing rows unless asked. Preferred
   method: `read_file` the CSV, then `write_file` it back with the new row
   appended (avoids shell-quoting bugs with commas).
4. **Update related files** only as RECEIPTS.md section 4 says (wishlist,
   debts.md Payments, sinking funds).
5. **Reply** in at most ~5 lines, in the owner's language:

```
✅ Dicatat: 20 Nov, PLN token, Rp500.000 (electricity)
Listrik bulan ini: Rp500.000 / Rp800.000 (63%)
Total pengeluaran bulan ini: Rp5.180.000 / Rp6.280.000 rencana
```

The web server notices the changed ledger and rebuilds the dashboard by itself.

## "Can I buy X?" questions

Apply the purchase-decision rule in CLAUDE.md, add the item to
`money/wishlist.md` with the decision, and reply with the decision + a
one-line reason.

## Privacy

Ledger files contain personal financial data. **Never** send their contents
to any service other than the owner's own chat.

## Pitfalls

- Read the files fresh each time; don't trust a cached copy from an earlier read.
- Amounts must be integer IDR with no separators; a comma in `description`
  must be quoted, or the CSV row breaks.
- budget.md may show a plan for a future payday — only compare against it if
  it already applies to the current month.
- Receipt photos: if your Hermes setup has no vision tool, ask the owner for
  the total and date instead of guessing.

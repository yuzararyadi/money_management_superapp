# Receipt & Transaction Recording Guide (for any agent, e.g. Hermes)

The owner sends receipts, transfer screenshots, or short text messages
(e.g. "token listrik 500rb") through chat (Hermes on Telegram or WhatsApp). Your job: record each one
accurately in the ledger, keep the wishlist up to date, and reply with a short
budget status. Read money/profile.md and money/budget.md first for context.

## 1. Extract
From each receipt/message, extract:
- **date** — transaction date on the receipt (YYYY-MM-DD). If none, use the
  date the message was sent and say so in `note`.
- **merchant** — store / payee name (e.g. "Indomaret", "PLN", "SD …").
- **description** — short, plain description of what was bought.
- **amount_idr** — the FINAL total actually paid (after discounts, incl. tax/
  admin fees), as a whole number with no dots/commas (e.g. 527500).
- **payment_method** — cash / debit / credit card / QRIS / transfer /
  e-wallet name. Card numbers: last 4 digits only, never the full number.

If the total or the date can't be read with confidence, DO NOT guess —
reply asking the owner to confirm, and record nothing until they answer.

## 2. Classify
`type` (one of): expense, income, transfer, investment, sinking-fund,
borrow, debt-payment, lend, lend-repaid
- expense — normal spending (incl. each installment paid on an installment
  purchase — see section 4c)
- income — salary, dividends, refunds, bonuses
- transfer — moving own money between own accounts (not spending)
- investment — Bibit buys/sells for the investment portfolio
- sinking-fund — money set aside to / paid from a sinking fund (e.g. tuition)
- borrow — cash I received as a loan from someone (not income)
- debt-payment — repaying a CASH loan I borrowed (not spending)
- lend — money I lent to someone (not spending)
- lend-repaid — someone paying back money I lent them (not income)

`category` (one of — reuse these, don't invent new ones without asking):
| category | examples |
|---|---|
| education | school fees, courses, books, uniforms |
| tuition | university tuition (paid from the tuition sinking fund) |
| emergency-fund | money moved into / taken out of the emergency fund (Dana Darurat) — type `sinking-fund` |
| family-support | monthly transfers to parents / parents-in-law |
| housing | IPL, repairs, PBB |
| electricity | PLN token |
| utilities | water (PDAM), internet, phone credit/data, gas |
| subscriptions | Claude (Anthropic, USD — record the IDR amount actually charged), Google One, streaming, apps |
| groceries | supermarket, market, minimarket household shopping |
| dining | restaurants, food delivery, coffee |
| transport | fuel, toll, parking, ride-hailing, vehicle service, vehicle tax |
| health | doctor, medicine, insurance not deducted from salary |
| household | household help, cleaning supplies, small home items |
| kids | toys, kids' activities other than school |
| personal | clothes, hobbies, personal care |
| giving | zakat, sedekah, gifts, donations |
| wishlist | an item listed in money/wishlist.md |
| installment | an installment paid on something bought with paylater / card cicilan (money/debts.md `D` item) |
| debt | borrow / debt-payment / lend / lend-repaid rows (money/debts.md) |
| investment | Bibit transactions |
| income | salary, dividend, refund |
| other | anything that fits nowhere above (note why) |

If a receipt mixes categories (e.g. groceries + household items in one
supermarket bill), record ONE row under the dominant category unless the
owner asks for a split.

`who` (whose spending): `me` = the owner or `partner` = the owner's partner.
The names are in money/settings.json ("people"); the dashboard shows the
names, the ledger stores `me` / `partner`.
- Default `me`.
- `partner` when the message starts with "Pengeluaran <partner name>",
  "<partner name>:", "Pengeluaran istri/suami", "Partner:" or similar (then
  every item in that message is `partner`), or when an item itself names the
  partner (e.g. "Sinta beli baju 150rb").
- `me` when it says "Pengeluaran <owner name>", "saya" or similar.
- If the owner forwards a receipt and it's unclear, use `me` (they can ask
  for a correction).

## 3. Record
Append one row to `money/ledger/YYYY-MM.csv` (month = transaction date).
Create the file with this exact header if it doesn't exist:

```
date,type,category,merchant,description,amount_idr,payment_method,source,note,who
```

- Rows have 10 fields; `who` is the last one (`me` / `partner`). Older rows
  have no value there — leave them as they are.

- `source`: whatsapp-receipt / whatsapp-text / bank-screenshot / manual /
  web-form / web-hermes. `web-form` and `web-hermes` rows come from the
  dashboard's "＋ Add" tab (typed by the owner; `web-hermes` = a free-text
  note that you classified via the dashboard, then the owner checked and
  published). They are already recorded, so don't add them again from a
  receipt of the same purchase (the duplicate check below catches most cases).
- When the dashboard asks you to classify a note (a one-shot request that
  says "Reply with ONE JSON object only"), follow it exactly: classify with
  the types/categories above, don't use tools, don't write any files — the
  dashboard saves the rows after the owner confirms them.
- Wrap any field containing a comma in double quotes.
- **Duplicate check:** before appending, look for a row with the same date,
  merchant and amount. If found, ask the owner before adding it again.
- Never edit or delete existing rows unless the owner asks; corrections are
  made by the owner's explicit instruction.

## 4. Update related files
- **Wishlist:** if the purchase matches an item in money/wishlist.md, set its
  Status to `Bought YYYY-MM-DD` and put the actual price in the Decision column
  note. Use category `wishlist`.
- **Tuition payment:** record with type `sinking-fund`, category `tuition`;
  then update the "Next due" date in money/profile.md only if the owner gives
  the new date.
- **Investment (Bibit) receipts:** record in the ledger (type `investment`).
  Do NOT edit portfolio.md, log.csv, reports/ or dashboard.html — those are
  updated only during the monthly investment run.
- Do NOT change budget amounts in budget.md or rules in CLAUDE.md; those
  change only during the payday run.

## 4d. Emergency fund (Dana Darurat)
- Money put INTO the emergency fund: type `sinking-fund`, category
  `emergency-fund`, positive amount (e.g. 7500000).
- Money taken OUT of it: same type/category with a NEGATIVE amount
  (e.g. -1500000), and the description says what it was for. The actual
  emergency spending (doctor, repair, …) is recorded separately as a normal
  `expense` row.
- Reply line: `Dana darurat: Rp… / Rp<target> (…%)` — balance = sum of all
  emergency-fund rows; target from the "Emergency fund plan" heading in money/budget.md.

## 4c. Debts, installments and money lent (money/debts.md)
Every money movement below gets BOTH a ledger row (section 3) AND, where
stated, a row in money/debts.md. Put the debts.md ID at the start of the
ledger `note` (e.g. `D1 installment 2/3`, `L1 partial repayment`).

| Situation | Ledger row (type / category) | money/debts.md |
|---|---|---|
| Buy something on installments (paylater, card cicilan) | none for the purchase itself | new `D` row under **I owe** (total incl. fees, number of installments, amount, due day) |
| Pay an installment | `expense` / `installment` | new row in **Payments** |
| Borrow cash from someone | `borrow` / `debt` | new `D` row (Installments = 1 unless agreed otherwise) |
| Repay borrowed cash | `debt-payment` / `debt` | new row in **Payments** |
| Lend money to someone | `lend` / `debt` | new `L` row under **Owed to me** |
| Someone repays me (full or partial) | `lend-repaid` / `debt` | new row in **Payments** |

- If a down payment (DP) is paid at purchase, it is the first Payments row
  for that `D` item and a ledger `expense` / `installment` row.
- Do not type paid/remaining totals anywhere — the dashboard calculates them
  from the Payments table.
- When the sum of payments reaches the total, set Status to
  `Paid off YYYY-MM-DD` / `Repaid YYYY-MM-DD`.
- If it isn't clear WHICH debt or loan a payment belongs to, or the direction
  (did I lend or borrow?), ask the owner before recording.
- Reply line for debts: `D1 new phone: 2/6 dibayar, sisa Rp…` or
  `L1 <name>: sisa Rp… belum kembali`.

## 4b. Refresh the dashboard
After recording, run `python3 money/build_dashboard.py` so index.html shows
the new transaction.

## 5. Reply to the owner (short, chat-friendly)
After recording, reply in at most ~5 lines:
1. What was recorded: date, merchant, amount, category (and the partner's name if who = partner).
2. Month-to-date spent in that category vs. the planned amount in
   money/budget.md (if a plan exists).
3. Warn if the category reached ≥80% of plan ("⚠️") or exceeded it ("🔴").
4. Total spent this month vs. total planned spending.

Example:
> ✅ Dicatat: 20 Nov, PLN token, Rp500.000 (electricity)
> Listrik bulan ini: Rp500.000 / Rp800.000 (63%)
> Total pengeluaran bulan ini: Rp5.180.000 / Rp6.280.000 rencana

## 6. "Can I buy X?" questions
If the owner asks whether to buy something, apply the Purchase decision rule
in CLAUDE.md ("Money management" section): emergency fund first → fits this
month's leftover without touching tuition fund / emergency fund / investment
→ else set a monthly set-aside and target month; items ≥ IDR 3,000,000 wait
7 days. Add the item to money/wishlist.md with the decision, and reply with
the decision and a one-line reason.

## 7. Privacy
Ledger files contain personal financial data. Never send their contents to
any service other than the owner's own chat with you.

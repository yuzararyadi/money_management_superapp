# Debts & Loans — SAMPLE

Two directions, one file:
- **I owe**: installment purchases (paylater, credit-card cicilan) and cash I
  borrowed. IDs `D1`, `D2`, …
- **Owed to me**: money I lent to someone. IDs `L1`, `L2`, …

Paid / remaining amounts are NOT typed into the tables below. They are
calculated from the **Payments** table, so every payment or repayment is one
new row there. The dashboard (Debts & loans tab) does the sums.

Rules:
- Never delete a row. When a debt or loan is finished, set Status to
  `Paid off YYYY-MM-DD` (I owe) or `Repaid YYYY-MM-DD` (owed to me).
- Money I lent that I decide not to collect: Status `Forgiven YYYY-MM-DD`.
- Amounts are whole rupiah, no dots/commas (e.g. 2433000).

## I owe

| ID | Started | Lender / platform | What for | Total (IDR) | Installments | Per installment (IDR) | Due day | Status | Notes |
|---|---|---|---|---|---|---|---|---|---|
| D1 | 2026-10-15 | Paylater | New phone | 4500000 | 6 | 750000 | 15 | Active | 0% installment |

Columns:
- Total = everything I will pay in the end, including interest/admin fees.
- Installments = number of payments. Use 1 for a one-off cash loan.
- Per installment = amount of each installment (empty for a cash loan with no fixed payment).
- Due day = day of month a payment is due (e.g. 15), or a date for a one-off.
- Status: `Active` / `Paid off YYYY-MM-DD`.

## Owed to me

| ID | Date lent | Borrower | Reason | Amount (IDR) | Expected back | Status | Notes |
|---|---|---|---|---|---|---|---|
| L1 | 2026-10-01 | Budi | Car repair | 1000000 | 2026-12 | Open | |

Columns:
- Expected back = date or month agreed (or `—` if none agreed).
- Status: `Open` / `Repaid YYYY-MM-DD` / `Forgiven YYYY-MM-DD`.

## Payments

One row per payment I made toward a `D` item, or per repayment I received
for an `L` item.

| Date | ID | Amount (IDR) | Method | Note |
|---|---|---|---|---|
| 2026-10-15 | D1 | 750000 | paylater | installment 1/6 |

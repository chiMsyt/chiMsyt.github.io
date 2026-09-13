# Work Samples — Timothy Ting

Four pieces. Each one exists to answer a question a client would reasonably ask
someone with no formal VA history.

| Sample | Question it answers |
|---|---|
| `client-reporting-dashboard.xlsx` | Can you actually build a spreadsheet, or do you just say "advanced Sheets"? |
| `sop-library/01-client-onboarding.md` | Will I have to explain everything twice? |
| `sop-library/02-weekly-reporting.md` | Will I know what you did without asking? |
| `sop-library/03-inbox-triage.md` | Can I trust you with my inbox? |

---

## Client Reporting Dashboard

A three-tab expense reporting system — `Data` / `Calc` / `Dashboard`, plus a
`How this works` tab explaining the design decisions.

**What it demonstrates:** SUMIFS with EOMONTH for month boundaries, data
validation, conditional formatting for budget overruns, budget-vs-actual variance,
KPI tiles, and two charts.

**The design decision worth asking about:** `Calc` references `Data` by whole
column (`Data!$E:$E`), never by a bounded range like `E2:E150`. That is why
re-importing data cannot break the report. The common failure in a client
spreadsheet is someone pasting fresh rows past the end of a hardcoded range, and
then reporting a wrong number for a month without anyone noticing.

**To view it as a Google Sheet:** upload the `.xlsx` to Google Drive and open with
Google Sheets. All formulas, validation and conditional formatting convert
directly — that is deliberate, and part of why those functions were chosen.

**To check the numbers yourself:**

```
uv run --with openpyxl python verify-dashboard.py
```

That script recomputes every rollup in plain Python from the `Data` tab and prints
what the workbook must show. It exists because `openpyxl` writes formulas but never
evaluates them, so a wrong `SUMIFS` would sit in the file looking perfectly correct.
It also asserts that `Calc` contains no bounded references back to `Data` — if
someone edits the workbook and hardcodes a range, the check fails.

## SOP Library

Three standard operating procedures. Each has a purpose, a named owner, a
frequency, prerequisites, numbered steps, an edge-case table, an escalation path,
and a definition of done.

The edge-case tables are the part worth reading. Anyone can write happy-path steps;
the value of an SOP is that it says what to do when the client will not grant
access, when the data source is down on report day, or when an email arrives asking
to change a supplier's bank details.

---

## Honest notes

- The transaction data in the dashboard is **synthetic** — generated for this
  sample, not a real client's books. The structure, formulas and design decisions
  are exactly what I would ship.
- The SOPs are written to **realistic composite scenarios**, not to real
  engagements. They are not redacted client documents.
- These are work samples, not case studies. I have not yet run these processes for
  a paying client — that is precisely what I am looking for.

I would rather show you something real and label it accurately than dress a sample
up as client work.

---

**Timothy Ting** · timothy.gabriel.ting@gmail.com · +63 960 254 7464
Portfolio: https://chimsyt.github.io

---

## Bank Reconciliation & AP/AR Workbook

**Two files, one builder.**

| File | What it is |
|---|---|
| `bank-reconciliation-ap-ar.xlsx` | The worked example. Sample data, four problems planted in it on purpose. |
| `bank-reconciliation-TEMPLATE.xlsx` | **The one you actually use.** Same formulas, no data, pre-filled to row 604. |

```bash
uv run --with openpyxl python build-reconciliation-workbook.py   # builds both
uv run --with openpyxl python verify-reconciliation.py           # checks the example
```

### Using the template

1. Type your **opening balance** and the statement's **closing balance** into
   `Bank!G2` and `Bank!G3`. These two cells are what make it a reconciliation
   rather than a matching exercise.
2. Paste bank lines into **Bank** columns A–D.
3. Enter invoices and bills into **Ledger** columns A–F. One row per document,
   never one row per payment.
4. Read **Exceptions**. All zeros and a zero variance means the period is clean.
5. **AR Aging** says who to chase. **AP Payment Run** is the week's payments —
   filter column A for `Yes`.

Every other column is a formula. Don't overwrite them.

### The design decisions, and why

- **Whole-column references.** A bounded range like `E2:E150` breaks silently
  when somebody pastes a longer month — it keeps calculating and reports a wrong
  number. The checker fails the build if one reappears.
- **Match on amount and direction, never on description.** Bank descriptions are
  free text the bank invents. Direction matters too: money in can only settle an
  invoice, money out only a bill — without that, a 500 refund would happily match
  a 500 supplier bill.
- **Exceptions from both sides.** Bank lines with no ledger entry *and* ledger
  entries with no bank line. Most reconciliation sheets check one direction,
  which hides half the errors — a bill entered twice and paid once is invisible
  from the bank side.
- **Ambiguity is flagged, never guessed.** Two payments of the same amount can't
  be told apart by amount alone, so the sheet says `REVIEW` and stops.
- **No hardcoded dates.** Aging and the payment run use `TODAY()`.
- **Formulas restricted to SUMIFS, COUNTIFS, SUMPRODUCT, IFERROR and TEXT**, so
  it behaves identically in Google Sheets and in Excel, including older Excel
  without XLOOKUP or dynamic arrays.

### The point of the worked example

The cash **agrees to the penny** — variance zero — and four transactions still
have no explanation: a freight supplier paid twice, a merchant fee nobody
mapped, and a deposit with no invoice behind it. A reconciliation that only
checks the total calls that a clean month.

### How it's checked

`verify-reconciliation.py` never reads the workbook's own answers. It reads the
typed columns only, recomputes every figure independently in Python, then opens
the file in LibreOffice so the formulas actually calculate and compares the
numbers. 23 checks.

It has already caught two real bugs: a bounded range left in the dashboard, and
a status rule that reported a duplicate payment as merely unmatched because it
tested "unmatched" before "duplicate".

**The data is synthetic and the business is invented.** This demonstrates method,
not client work, and isn't presented as anything else.

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

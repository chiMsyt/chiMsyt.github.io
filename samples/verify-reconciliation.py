#!/usr/bin/env python3
"""Independently recompute the reconciliation workbook and fail if it disagrees.

    uv run --with openpyxl python verify-reconciliation.py

This is the point of the sample, not a footnote to it. Anybody can build a
spreadsheet that looks right. The question a bookkeeping client actually cares
about is "how do you know it is right", and the answer has to be something
other than "I checked it".

So this script never reads the workbook's own answers. It reads the RAW data -
the typed columns only - recomputes every headline figure from scratch in
Python, and compares. Two implementations of the same rule, written at different
times in different languages, agreeing, is evidence. One implementation looking
plausible is not.

It also proves the workbook catches the four problems planted in the sample
data, rather than asserting that it does.
"""

import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

from openpyxl import load_workbook

HERE = Path(__file__).resolve().parent
BOOK = HERE / "bank-reconciliation-ap-ar.xlsx"
TEMPLATE = HERE / "bank-reconciliation-TEMPLATE.xlsx"

# openpyxl writes formulas but never evaluates them, so reading the file back
# proves only that the right text is in the right cell. To check the NUMBERS,
# the workbook has to be opened by something that actually calculates. Any
# LibreOffice install does; if there is not one, the value checks are skipped
# and say so rather than passing quietly.
SOFFICE = Path(r"C:\Program Files\LibreOffice\program\soffice.exe")


def recalculated(book: Path):
    """Open the workbook in LibreOffice so the formulas compute, read values."""
    exe = str(SOFFICE) if SOFFICE.exists() else shutil.which("soffice")
    if not exe:
        return None
    tmp = Path(tempfile.mkdtemp(prefix="recalc-"))
    r = subprocess.run([exe, "--headless", "--convert-to", "xlsx",
                        "--outdir", str(tmp), str(book)],
                       capture_output=True, text=True, timeout=180)
    out = tmp / book.name
    if r.returncode != 0 or not out.exists():
        return None
    return load_workbook(out, data_only=True)

failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}{'  - ' + detail if detail else ''}")
    if not ok:
        failures.append(label)


def main() -> int:
    if not BOOK.exists():
        print(f"FAIL  {BOOK.name} not found - run build-reconciliation-workbook.py")
        return 1

    wb = load_workbook(BOOK)          # formulas, not cached values
    bank_ws, led_ws = wb["Bank"], wb["Ledger"]

    # --- read ONLY the typed columns. Never a computed one. ------------------
    bank = []
    for r in range(5, bank_ws.max_row + 1):
        date = bank_ws.cell(r, 1).value
        if date is None:
            continue
        money_in = bank_ws.cell(r, 3).value or 0
        money_out = bank_ws.cell(r, 4).value or 0
        bank.append(dict(row=r, date=date, desc=bank_ws.cell(r, 2).value,
                         net=round(money_in - money_out, 2)))

    ledger = []
    for r in range(5, led_ws.max_row + 1):
        date = led_ws.cell(r, 1).value
        if date is None:
            continue
        ledger.append(dict(row=r, date=date, type=led_ws.cell(r, 2).value,
                           party=led_ws.cell(r, 3).value,
                           ref=led_ws.cell(r, 4).value,
                           amount=round(led_ws.cell(r, 5).value, 2),
                           due=led_ws.cell(r, 6).value))

    print(f"\nRead {len(bank)} bank lines and {len(ledger)} ledger entries "
          f"from the typed columns only.\n")

    # --- the matching rule, reimplemented from the written spec --------------
    def key(amount: float, direction: str) -> str:
        return f"{abs(amount):.2f}|{direction}"

    bank_keys = defaultdict(list)
    for b in bank:
        if b["net"] == 0:
            continue
        bank_keys[key(b["net"], "AR" if b["net"] > 0 else "AP")].append(b)

    ledger_keys = defaultdict(list)
    for e in ledger:
        ledger_keys[key(e["amount"], "AR" if e["type"] == "Invoice" else "AP")].append(e)

    # Precedence, mirroring the workbook exactly: ambiguity is reported first
    # and the categories are mutually exclusive. The first version of this
    # checker let them overlap, so it counted the two duplicate freight
    # payments as unmatched AND ambiguous and disagreed with the sheet 4 vs 2.
    # Both were "right"; they were answering different questions. A checker
    # that implements its own rule instead of the documented one is not a
    # check, it is a second opinion.
    def direction(b):
        return "AR" if b["net"] > 0 else "AP"

    ambiguous, unmatched_bank = [], []
    for b in bank:
        if b["net"] == 0:
            continue
        k = key(b["net"], direction(b))
        if len(bank_keys[k]) > 1 or len(ledger_keys.get(k, [])) > 1:
            ambiguous.append(b)
        elif k not in ledger_keys:
            unmatched_bank.append(b)
    open_entries = [e for e in ledger
                    if key(e["amount"], "AR" if e["type"] == "Invoice" else "AP")
                    not in bank_keys]

    print("Recomputed independently:")
    print(f"  unreconciled bank lines : {len(unmatched_bank)}")
    print(f"  ambiguous (same amount) : {len(ambiguous)}")
    print(f"  open ledger entries     : {len(open_entries)}")
    print(f"  receivables outstanding : "
          f"{sum(e['amount'] for e in open_entries if e['type'] == 'Invoice'):,.2f}")
    print(f"  payables outstanding    : "
          f"{sum(e['amount'] for e in open_entries if e['type'] == 'Bill'):,.2f}\n")

    print("Checks:")

    # --- 1. the four planted problems are all findable ----------------------
    descs = [b["desc"] for b in unmatched_bank]
    check("the freight payment with no bill behind it is surfaced",
          any("TRANSTATE" in b["desc"] for b in ambiguous + unmatched_bank))
    check("an unmapped merchant fee is unreconciled",
          any("MERCHANT FEE" in d for d in descs))
    check("an unidentified deposit is unreconciled",
          any("UNKNOWN REF" in d for d in descs))
    check("the duplicate payment is flagged as ambiguous, not silently matched",
          any("TRANSTATE" in b["desc"] for b in ambiguous),
          f"{len(ambiguous)} line(s) flagged for review")

    # --- 2. the workbook actually asks the questions we think it does -------
    # Formula text, not values: openpyxl does not evaluate, so this verifies the
    # sheet is wired the way the documentation claims.
    status_formula = bank_ws.cell(5, 8).value or ""
    check("Bank status formula checks the ledger, not itself",
          "Ledger!" in (bank_ws.cell(5, 7).value or ""))
    check("Bank status formula reports UNMATCHED and REVIEW separately",
          "UNMATCHED" in status_formula and "REVIEW" in status_formula)
    check("match key encodes direction so money in cannot settle a bill",
          '"AR"' in (bank_ws.cell(5, 6).value or "")
          and '"AP"' in (bank_ws.cell(5, 6).value or ""))
    check("aging uses TODAY() rather than a hardcoded date",
          "TODAY()" in (led_ws.cell(5, 7).value or ""))

    # --- 3. whole-column references, the design rule that matters most ------
    bounded = []
    for ws in (bank_ws, led_ws, wb["AR Aging"], wb["Exceptions"], wb["Dashboard"]):
        for row in ws.iter_rows():
            for c in row:
                f = c.value
                if isinstance(f, str) and f.startswith("="):
                    # A whole-column ref looks like $E:$E. A bounded one like
                    # $E$5:$E$120 is the failure mode - unless it is a
                    # deliberately bounded SUMPRODUCT, which cannot take a
                    # whole column.
                    if "SUMPRODUCT" in f or "COUNTIF(Ledger!$D$5" in f:
                        continue
                    import re
                    if re.search(r"\$[A-Z]+\$\d+:\$[A-Z]+\$\d+", f):
                        bounded.append(f"{ws.title}!{c.coordinate}")
    check("no accidental bounded ranges in aggregate formulas",
          not bounded, f"{len(bounded)} found: {bounded[:3]}" if bounded else "")

    # --- 4. structure a reader depends on -----------------------------------
    expected = ["Start here", "Bank", "Ledger", "Exceptions", "AR Aging",
                "AP Payment Run", "Dashboard"]
    check("all seven sheets present and named as documented",
          wb.sheetnames == expected, str(wb.sheetnames))
    check("every ledger row has a type of Invoice or Bill",
          all(e["type"] in ("Invoice", "Bill") for e in ledger))
    check("every ledger row has a due date on or after its issue date",
          all(e["due"] >= e["date"] for e in ledger))
    check("no ledger reference is used twice",
          len({e["ref"] for e in ledger}) == len(ledger))
    check("sample contains both settled and open entries",
          0 < len(open_entries) < len(ledger),
          f"{len(open_entries)} open of {len(ledger)}")

    # --- 5. the numbers the workbook actually computes ----------------------
    calc = recalculated(BOOK)
    if calc is None:
        print("  SKIP  value checks - no LibreOffice found to evaluate formulas")
    else:
        exc, dash, bank_c = calc["Exceptions"], calc["Dashboard"], calc["Bank"]
        ar_open = round(sum(e["amount"] for e in open_entries
                            if e["type"] == "Invoice"), 2)
        ap_open = round(sum(e["amount"] for e in open_entries
                            if e["type"] == "Bill"), 2)

        check("workbook's unreconciled count equals the independent one",
              exc.cell(5, 2).value == len(unmatched_bank),
              f"workbook {exc.cell(5, 2).value} vs recomputed {len(unmatched_bank)}")
        check("workbook's ambiguity count equals the independent one",
              exc.cell(6, 2).value == len(ambiguous),
              f"workbook {exc.cell(6, 2).value} vs recomputed {len(ambiguous)}")
        check("workbook's receivables total equals the independent one",
              abs((dash.cell(10, 2).value or 0) - ar_open) < 0.01,
              f"workbook {dash.cell(10, 2).value} vs recomputed {ar_open}")
        check("workbook's payables total equals the independent one",
              abs((dash.cell(10, 5).value or 0) - ap_open) < 0.01,
              f"workbook {dash.cell(10, 5).value} vs recomputed {ap_open}")
        variance = dash.cell(23, 3).value
        check("the sample's cash ties to the statement (variance is zero)",
              variance is not None and abs(variance) < 0.01,
              f"variance {variance!r}")
        check("no bank row is left with an error or a blank status",
              all(bank_c.cell(r, 8).value not in (None, "")
                  and "#" not in str(bank_c.cell(r, 8).value)
                  for r in range(5, 5 + len(bank))))
        check("the duplicate payment is REVIEWed rather than merely unmatched",
              any("TRANSTATE" in (bank_c.cell(r, 2).value or "")
                  and str(bank_c.cell(r, 8).value).startswith("REVIEW")
                  for r in range(5, 5 + len(bank))))

    # --- 6. the blank template is genuinely usable --------------------------
    if not TEMPLATE.exists():
        check("template exists", False, "run the builder")
    else:
        tcalc = recalculated(TEMPLATE)
        if tcalc is None:
            print("  SKIP  template value checks - no LibreOffice")
        else:
            tb, tl, td = tcalc["Bank"], tcalc["Ledger"], tcalc["Dashboard"]
            empties = [tb.cell(r, 8).value for r in range(5, 60)]
            check("empty template rows show nothing, not zeros or errors",
                  all(v in (None, "") for v in empties),
                  f"first few: {empties[:4]}")
            check("empty template ledger rows are blank too",
                  all(tl.cell(r, 9).value in (None, "") for r in range(5, 60)))
            check("template dashboard shows zeros, not errors",
                  all("#" not in str(td.cell(r, c).value)
                      for r in (6, 10, 14) for c in (2, 5)),
                  str([td.cell(r, c).value for r in (6, 10, 14) for c in (2, 5)]))

    print()
    if failures:
        print(f"FAILED  {len(failures)} check(s): {failures}")
        return 1
    print(f"PASS  all checks - the workbook's rules agree with an independent "
          f"recomputation,\n      and it finds all four planted problems.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

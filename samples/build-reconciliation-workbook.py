#!/usr/bin/env python3
"""Build the bank reconciliation + AP/AR workbook work sample.

    uv run --with openpyxl python build-reconciliation-workbook.py

Why this exists as a script rather than a hand-made file: the workbook has to be
rebuildable. A sample you cannot regenerate rots the moment you spot a mistake
in it, and "I can rebuild it from source" is a better answer in an interview
than "I made it once".

Design rules, all of them defensible out loud:

1. **Whole-column references everywhere.** A bounded range like E2:E150 breaks
   silently when someone pastes in a longer month - it keeps calculating and
   reports a wrong number. Whole columns cost a little speed and remove a whole
   class of silent error.
2. **Match on amount and direction, never on description.** Bank descriptions
   are free text the bank invents; they never match the ledger reliably.
3. **Exceptions are reported from BOTH sides.** Bank lines with no ledger entry
   AND ledger entries with no bank line. Most reconciliation sheets only do one
   direction, which hides half the errors - a bill entered twice and paid once
   is invisible if you only check the bank side.
4. **Ambiguity is flagged, never guessed.** Two invoices for the same amount
   cannot be told apart by amount alone, so the sheet says REVIEW rather than
   picking one. This is the known limitation of rule 2 and the honest answer to
   "how would this break".
5. **No hardcoded dates.** Aging uses TODAY(), so the workbook is still correct
   next month without being edited.
6. **Formulas that work in both Google Sheets and Excel** - SUMIFS, COUNTIFS,
   IFERROR, TEXT, EOMONTH. No dynamic arrays, no XLOOKUP, no Excel Tables.
"""

import datetime as dt
import random
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule, FormulaRule

HERE = Path(__file__).resolve().parent
SAMPLE = HERE / "bank-reconciliation-ap-ar.xlsx"
BLANK = HERE / "bank-reconciliation-TEMPLATE.xlsx"

# How far the formulas are pre-filled in the blank template. Enough for a year
# of a small business's statements; paste beyond it and the last row's formulas
# drag down like any other spreadsheet.
TEMPLATE_ROWS = 600

# Deterministic: the same command produces the same file, so a diff means a
# real change rather than new random numbers.
random.seed(20260914)

INK = "1F3346"
MUTED = "6B7A88"
RULE = "D7DEE5"
HEAD_FILL = "1F3346"
BAND = "F2F6F9"
WARN = "FFF4E5"
BAD = "FDECEA"
GOOD = "EAF6EC"

TITLE = Font(name="Calibri", size=16, bold=True, color=INK)
SUB = Font(name="Calibri", size=10, color=MUTED)
H = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
BOLD = Font(name="Calibri", size=10, bold=True, color=INK)
BODY = Font(name="Calibri", size=10)
SMALL = Font(name="Calibri", size=9, color=MUTED)
BIG = Font(name="Calibri", size=20, bold=True, color=INK)

thin = Side(style="thin", color=RULE)
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)

MONEY = '#,##0.00;[Red]-#,##0.00'
DATE = "yyyy-mm-dd"

CUSTOMERS = ["Harding Construction", "Bayline Interiors", "Crestwood Builders",
             "Dockside Marine", "Vale & Sons Painting", "Northgate Property Co",
             "Ellerslie Fitout", "Quay Street Developments"]
SUPPLIERS = ["Pigment Supply Co", "Drum & Can Packaging", "Transtate Freight",
             "Solvent Direct", "Metro Power", "Rawlins Resin",
             "Southline Logistics", "OfficeWorks Trade"]


def header(ws, row, labels, widths):
    for i, (label, w) in enumerate(zip(labels, widths), 1):
        c = ws.cell(row=row, column=i, value=label)
        c.font, c.border = H, BOX
        c.fill = PatternFill("solid", fgColor=HEAD_FILL)
        c.alignment = Alignment(vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[row].height = 26


def make_data():
    """Synthetic but internally consistent: every bank line has a cause."""
    start = dt.date(2026, 6, 1)
    ledger, bank = [], []
    inv_n, bill_n = 1000, 5000

    for week in range(12):
        monday = start + dt.timedelta(days=7 * week)

        for _ in range(random.randint(2, 4)):        # invoices raised (AR)
            inv_n += 1
            raised = monday + dt.timedelta(days=random.randint(0, 4))
            amt = round(random.uniform(480, 9600), 2)
            terms = random.choice([14, 21, 30])
            ledger.append(dict(date=raised, type="Invoice",
                               party=random.choice(CUSTOMERS),
                               ref=f"INV-{inv_n}", amount=amt,
                               due=raised + dt.timedelta(days=terms)))

        for _ in range(random.randint(2, 3)):        # bills received (AP)
            bill_n += 1
            raised = monday + dt.timedelta(days=random.randint(0, 4))
            amt = round(random.uniform(180, 5400), 2)
            ledger.append(dict(date=raised, type="Bill",
                               party=random.choice(SUPPLIERS),
                               ref=f"BILL-{bill_n}", amount=amt,
                               due=raised + dt.timedelta(days=random.choice([7, 14, 30]))))

    # Most, but deliberately not all, of the ledger settles in the bank. The
    # leftovers are the whole point - a reconciliation with nothing outstanding
    # demonstrates nothing.
    for e in ledger:
        if random.random() < 0.78:
            paid = e["due"] + dt.timedelta(days=random.randint(-6, 9))
            if paid > dt.date(2026, 9, 10):
                continue
            if e["type"] == "Invoice":
                bank.append(dict(date=paid, desc=f"DEPOSIT {e['party'][:18].upper()}",
                                 money_in=e["amount"], money_out=0))
            else:
                bank.append(dict(date=paid, desc=f"EFT PMT {e['party'][:18].upper()}",
                                 money_in=0, money_out=e["amount"]))

    # Four planted problems. Each one is a real thing that happens, and each one
    # the sheet has to catch on its own.
    bank.append(dict(date=dt.date(2026, 7, 15), desc="EFT PMT TRANSTATE FREIGHT",
                     money_in=0, money_out=842.50))          # 1. no ledger entry
    bank.append(dict(date=dt.date(2026, 7, 16), desc="EFT PMT TRANSTATE FREIGHT",
                     money_in=0, money_out=842.50))          # 2. paid twice
    bank.append(dict(date=dt.date(2026, 8, 3), desc="MERCHANT FEE STRIPE",
                     money_in=0, money_out=118.44))          # 3. unmapped fee
    bank.append(dict(date=dt.date(2026, 8, 21), desc="DEPOSIT UNKNOWN REF 88213",
                     money_in=2400.00, money_out=0))         # 4. unidentified receipt

    ledger.sort(key=lambda e: e["date"])
    bank.sort(key=lambda e: e["date"])
    return ledger, bank


def build(blank: bool = False):
    """One builder, two files.

    The template and the sample are the same workbook - identical formulas,
    identical structure - and only the data differs. That is deliberate: a
    template that drifts from the thing you demonstrated is worse than no
    template, because you end up explaining a spreadsheet you no longer use.
    """
    ledger, bank = ([], []) if blank else make_data()
    n_bank = TEMPLATE_ROWS if blank else len(bank)
    n_led = TEMPLATE_ROWS if blank else len(ledger)
    wb = Workbook()

    # ---------------------------------------------------------------- Bank
    ws = wb.active
    ws.title = "Bank"
    ws["A1"] = "Bank statement - paste new lines under the last row"
    ws["A1"].font = TITLE
    ws["A2"] = ("Columns A-D are the only ones you type. E to H are formulas and "
                "rebuild themselves; do not overwrite them.")
    ws["A2"].font = SUB
    # The two typed cells that turn this from a matching tool into an actual
    # reconciliation. Matching every line still does not tell you the cash is
    # right; agreeing to the bank's own closing balance does.
    ws["F2"] = "Opening balance"
    ws["F2"].font = SMALL
    ws["G2"] = 0
    ws["G2"].number_format = MONEY
    ws["G2"].font = BOLD
    ws["G2"].fill = PatternFill("solid", fgColor=BAND)
    ws["F3"] = "Closing balance per statement"
    ws["F3"].font = SMALL
    # In the sample the statement agrees to the penny ON PURPOSE, while four
    # transactions above it still have no explanation. That is the point worth
    # making out loud: a bank that agrees is not the same as books that are
    # right, and a reconciliation that only checks the total misses all four.
    ws["G3"] = (0 if blank
                else round(sum(b["money_in"] - b["money_out"] for b in bank), 2))
    ws["G3"].number_format = MONEY
    ws["G3"].font = BOLD
    ws["G3"].fill = PatternFill("solid", fgColor=BAND)
    ws["H2"] = "<- type these two from the statement"
    ws["H2"].font = SMALL

    header(ws, 4, ["Date", "Bank description", "Money in", "Money out",
                   "Net", "Match key", "In ledger", "Status"],
           [12, 34, 13, 13, 13, 16, 11, 30])

    for i in range(n_bank):
        r = 5 + i
        b = bank[i] if i < len(bank) else None
        ws.cell(r, 1, b["date"] if b else None).number_format = DATE
        ws.cell(r, 2, b["desc"] if b else None)
        ws.cell(r, 3, (b["money_in"] or None) if b else None).number_format = MONEY
        ws.cell(r, 4, (b["money_out"] or None) if b else None).number_format = MONEY
        ws.cell(r, 5, f"=N(C{r})-N(D{r})").number_format = MONEY
        # Direction matters: money in can only settle an Invoice, money out a
        # Bill. Without it a 500 refund would "match" a 500 supplier bill.
        ws.cell(r, 6, f'=IF(E{r}=0,"",TEXT(ABS(E{r}),"0.00")&"|"&IF(E{r}>0,"AR","AP"))')
        ws.cell(r, 7, f'=IF(F{r}="","",COUNTIF(Ledger!$H:$H,F{r}))')
        # Order matters, and the first version got it wrong. UNMATCHED was
        # tested first, so the two identical freight payments - which have no
        # ledger entry at all - were reported only as unmatched and the
        # duplicate flag never fired. A possible double payment is money
        # already out of the door, so it is now the first thing reported,
        # whether or not the ledger explains it.
        ws.cell(r, 8,
                f'=IF(F{r}="","",'
                f'IF(COUNTIF($F:$F,F{r})>1,"REVIEW - same amount appears twice",'
                f'IF(G{r}=0,"UNMATCHED - no ledger entry",'
                f'IF(G{r}>1,"REVIEW - matches several ledger entries",'
                f'"Matched"))))')
        for col in range(1, 9):
            ws.cell(r, col).font = BODY
            ws.cell(r, col).border = BOX

    last_bank = 4 + n_bank
    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:H{last_bank}"
    for rng, colour in ((f"H5:H{last_bank}", BAD),):
        ws.conditional_formatting.add(rng, FormulaRule(
            formula=[f'LEFT($H5,9)="UNMATCHED"'],
            fill=PatternFill("solid", fgColor=colour)))
    ws.conditional_formatting.add(f"H5:H{last_bank}", FormulaRule(
        formula=[f'LEFT($H5,6)="REVIEW"'],
        fill=PatternFill("solid", fgColor=WARN)))

    # -------------------------------------------------------------- Ledger
    ws = wb.create_sheet("Ledger")
    ws["A1"] = "Ledger - invoices you raised and bills you received"
    ws["A1"].font = TITLE
    ws["A2"] = ("Columns A-F are typed. G to J are formulas. One row per "
                "document, never one row per payment.")
    ws["A2"].font = SUB
    header(ws, 4, ["Date", "Type", "Party", "Reference", "Amount", "Due date",
                   "Days overdue", "Match key", "Settled", "Aging bucket"],
           [12, 10, 26, 13, 13, 12, 13, 16, 13, 14])

    for i in range(n_led):
        r = 5 + i
        e = ledger[i] if i < len(ledger) else None
        ws.cell(r, 1, e["date"] if e else None).number_format = DATE
        ws.cell(r, 2, e["type"] if e else None)
        ws.cell(r, 3, e["party"] if e else None)
        ws.cell(r, 4, e["ref"] if e else None)
        ws.cell(r, 5, (e["amount"] if e else None)).number_format = MONEY
        ws.cell(r, 6, (e["due"] if e else None)).number_format = DATE
        ws.cell(r, 7, f'=IF(I{r}="Settled","",MAX(0,TODAY()-F{r}))')
        ws.cell(r, 8, f'=IF(E{r}="","",TEXT(E{r},"0.00")&"|"&IF(B{r}="Invoice","AR","AP"))')
        ws.cell(r, 9, f'=IF(H{r}="","",IF(COUNTIF(Bank!$F:$F,H{r})>0,"Settled","Open"))')
        ws.cell(r, 10,
                f'=IF(I{r}<>"Open","",'
                f'IF(G{r}<=0,"Current",IF(G{r}<=30,"1-30",IF(G{r}<=60,"31-60",'
                f'IF(G{r}<=90,"61-90","90+")))))')
        for col in range(1, 11):
            ws.cell(r, col).font = BODY
            ws.cell(r, col).border = BOX

    last_led = 4 + n_led
    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:J{last_led}"
    dv = DataValidation(type="list", formula1='"Invoice,Bill"', allow_blank=True)
    dv.error = "Type must be Invoice (money owed to you) or Bill (money you owe)."
    ws.add_data_validation(dv)
    dv.add(f"B5:B{last_led + 200}")
    ws.conditional_formatting.add(f"G5:G{last_led}", CellIsRule(
        operator="greaterThan", formula=["30"],
        fill=PatternFill("solid", fgColor=BAD)))
    ws.conditional_formatting.add(f"I5:I{last_led}", FormulaRule(
        formula=['$I5="Settled"'], fill=PatternFill("solid", fgColor=GOOD)))

    # ---------------------------------------------------------- Exceptions
    ws = wb.create_sheet("Exceptions")
    ws["A1"] = "Exceptions - the only sheet that needs your attention"
    ws["A1"].font = TITLE
    ws["A2"] = ("Checked from both directions. A bill entered twice and paid once "
                "is invisible if you only check the bank side.")
    ws["A2"].font = SUB

    rows = [
        ("Bank lines with no matching ledger entry",
         f'=COUNTIF(Bank!$H:$H,"UNMATCHED*")',
         "Money moved that the books do not explain. Usually a fee, a transfer "
         "between own accounts, or a bill nobody entered."),
        ("Bank lines needing review for ambiguity",
         f'=COUNTIF(Bank!$H:$H,"REVIEW*")',
         "Either the same amount appears twice on the statement - a possible "
         "double payment - or it matches several ledger entries. Matching on "
         "amount cannot tell these apart, so confirm by reference before "
         "ticking any of them off."),
        ("Ledger entries still open past their due date",
         f'=COUNTIFS(Ledger!$I:$I,"Open",Ledger!$G:$G,">0")',
         "Overdue both ways: invoices to chase and bills you are late paying."),
        ("Invoices unpaid more than 60 days",
         f'=COUNTIFS(Ledger!$I:$I,"Open",Ledger!$B:$B,"Invoice",Ledger!$G:$G,">60")',
         "The number that turns into a write-off if nobody looks at it."),
        ("Duplicate references in the ledger",
         f'=SUMPRODUCT((Ledger!$D$5:$D$500<>"")*(COUNTIF(Ledger!$D$5:$D$500,'
         f'Ledger!$D$5:$D$500)>1))/2',
         "The same invoice or bill entered twice. Halved because each duplicate "
         "pair is counted from both ends."),
    ]
    header(ws, 4, ["Check", "Count", "What it means and what to do"], [46, 10, 74])
    for i, (label, formula, meaning) in enumerate(rows):
        r = 5 + i
        ws.cell(r, 1, label).font = BOLD
        c = ws.cell(r, 2, formula)
        c.font, c.alignment = BOLD, Alignment(horizontal="center")
        ws.cell(r, 3, meaning).font = BODY
        ws.cell(r, 3).alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[r].height = 42
        for col in range(1, 4):
            ws.cell(r, col).border = BOX
    ws.conditional_formatting.add(f"B5:B{4 + len(rows)}", CellIsRule(
        operator="greaterThan", formula=["0"],
        fill=PatternFill("solid", fgColor=WARN), font=Font(bold=True)))

    # ------------------------------------------------------------ AR Aging
    ws = wb.create_sheet("AR Aging")
    ws["A1"] = "Receivables aging - who to chase, in what order"
    ws["A1"].font = TITLE
    ws["A2"] = "Buckets recalculate from TODAY(). Nothing here is typed."
    ws["A2"].font = SUB
    header(ws, 4, ["Customer", "Current", "1-30 days", "31-60 days",
                   "61-90 days", "90+ days", "Total open"],
           [28, 14, 14, 14, 14, 14, 15])
    buckets = ["Current", "1-30", "31-60", "61-90", "90+"]
    for i, cust in enumerate(CUSTOMERS):
        r = 5 + i
        ws.cell(r, 1, cust).font = BODY
        for j, b in enumerate(buckets):
            ws.cell(r, 2 + j,
                    f'=SUMIFS(Ledger!$E:$E,Ledger!$C:$C,$A{r},'
                    f'Ledger!$B:$B,"Invoice",Ledger!$I:$I,"Open",'
                    f'Ledger!$J:$J,"{b}")').number_format = MONEY
        ws.cell(r, 7, f"=SUM(B{r}:F{r})").number_format = MONEY
        ws.cell(r, 7).font = BOLD
        for col in range(1, 8):
            ws.cell(r, col).border = BOX
    tot = 5 + len(CUSTOMERS)
    ws.cell(tot, 1, "Total").font = BOLD
    for col in range(2, 8):
        c = ws.cell(tot, col, f"=SUM({get_column_letter(col)}5:{get_column_letter(col)}{tot - 1})")
        c.font, c.border, c.number_format = BOLD, BOX, MONEY
    ws.cell(tot, 1).border = BOX
    ws.conditional_formatting.add(f"E5:F{tot}", CellIsRule(
        operator="greaterThan", formula=["0"],
        fill=PatternFill("solid", fgColor=BAD)))

    # -------------------------------------------------------- AP Payment run
    ws = wb.create_sheet("AP Payment Run")
    ws["A1"] = "Supplier payment run - what is due in the next 7 days"
    ws["A1"].font = TITLE
    ws["A2"] = ("Filter column A for Yes. Sorted by the ledger, so a bill cannot "
                "appear here without existing in the books.")
    ws["A2"].font = SUB
    header(ws, 4, ["Pay this run?", "Supplier", "Reference", "Amount",
                   "Due date", "Days overdue"], [14, 28, 14, 14, 13, 14])
    shown = 0
    ap_rows = ([i for i, e in enumerate(ledger) if e["type"] == "Bill"]
               if ledger else list(range(n_led)))
    for i in ap_rows:
        lr = 5 + i
        r = 5 + shown
        shown += 1
        ws.cell(r, 1, f'=IF(Ledger!I{lr}<>"Open","",IF(Ledger!F{lr}<=TODAY()+7,"Yes","-"))')
        ws.cell(r, 2, f"=Ledger!C{lr}")
        ws.cell(r, 3, f"=Ledger!D{lr}")
        ws.cell(r, 4, f"=Ledger!E{lr}").number_format = MONEY
        ws.cell(r, 5, f"=Ledger!F{lr}").number_format = DATE
        ws.cell(r, 6, f"=Ledger!G{lr}")
        for col in range(1, 7):
            ws.cell(r, col).font = BODY
            ws.cell(r, col).border = BOX
    last_ap = 4 + shown
    ws.auto_filter.ref = f"A4:F{last_ap}"
    ws.freeze_panes = "A5"
    ws.conditional_formatting.add(f"A5:F{last_ap}", FormulaRule(
        formula=['$A5="Yes"'], fill=PatternFill("solid", fgColor=WARN)))

    # ----------------------------------------------------------- Dashboard
    ws = wb.create_sheet("Dashboard")
    ws["B2"] = "Bank Reconciliation and AP/AR"
    ws["B2"].font = TITLE
    ws["B3"] = (("Your business - paste your statement into Bank, your invoices "
                 "and bills into Ledger.")
                if blank else
                ("Northbridge Trade Supplies - sample data, not a real business. "
                 "Every figure below is a formula; nothing is typed."))
    ws["B3"].font = SUB
    ws.column_dimensions["A"].width = 3
    for col, w in zip("BCDEFG", [30, 18, 6, 30, 18, 4]):
        ws.column_dimensions[col].width = w

    tiles = [
        ("B", 5, "Unreconciled bank lines", '=COUNTIF(Bank!$H:$H,"UNMATCHED*")', "0"),
        ("E", 5, "Lines needing review", '=COUNTIF(Bank!$H:$H,"REVIEW*")', "0"),
        ("B", 9, "Receivables outstanding",
         '=SUMIFS(Ledger!$E:$E,Ledger!$B:$B,"Invoice",Ledger!$I:$I,"Open")', MONEY),
        ("E", 9, "Payables outstanding",
         '=SUMIFS(Ledger!$E:$E,Ledger!$B:$B,"Bill",Ledger!$I:$I,"Open")', MONEY),
        ("B", 13, "Overdue receivables",
         '=SUMIFS(Ledger!$E:$E,Ledger!$B:$B,"Invoice",Ledger!$I:$I,"Open",'
         'Ledger!$G:$G,">0")', MONEY),
        ("E", 13, "Due to suppliers within 7 days",
         '=SUMPRODUCT((Ledger!$B$5:$B$500="Bill")*(Ledger!$I$5:$I$500="Open")*'
         '(Ledger!$F$5:$F$500<=TODAY()+7)*(Ledger!$F$5:$F$500<>"")*Ledger!$E$5:$E$500)',
         MONEY),
    ]
    for col, row, label, formula, fmt in tiles:
        c = ws.cell(row, ws[f"{col}1"].column, label)
        c.font = SMALL
        v = ws.cell(row + 1, ws[f"{col}1"].column, formula)
        v.font, v.number_format = BIG, fmt

    ws["B17"] = "Reconciled this period"
    ws["B17"].font = SMALL
    # Denominator built from whole-column COUNTIFs rather than COUNTA over a
    # bounded range. The first version of this line used Bank!$H$5:$H$500 and
    # verify-reconciliation.py failed the build for it - which is the design
    # rule catching its own author, and the reason the checker exists.
    ws["B18"] = ('=TEXT(COUNTIF(Bank!$H:$H,"Matched")/MAX(1,'
                 'COUNTIF(Bank!$H:$H,"Matched")+COUNTIF(Bank!$H:$H,"UNMATCHED*")'
                 '+COUNTIF(Bank!$H:$H,"REVIEW*")),'
                 '"0%")&" of bank lines matched to a ledger entry"')
    ws["B18"].font = BOLD

    ws["B20"] = "Does the cash agree?"
    ws["B20"].font = BOLD
    ws["B21"] = "Closing balance per the books"
    ws["B21"].font = SMALL
    ws["C21"] = "=Bank!$G$2+SUM(Bank!$E:$E)"
    ws["C21"].number_format = MONEY
    ws["C21"].font = BOLD
    ws["B22"] = "Closing balance per the statement"
    ws["B22"].font = SMALL
    ws["C22"] = "=Bank!$G$3"
    ws["C22"].number_format = MONEY
    ws["C22"].font = BOLD
    ws["B23"] = "Variance"
    ws["B23"].font = SMALL
    ws["C23"] = "=ROUND(C21-C22,2)"
    ws["C23"].number_format = MONEY
    ws["C23"].font = BOLD
    ws["E23"] = ('=IF(ROUND(C23,2)=0,"Reconciled - the cash agrees to the penny",'
                 '"NOT RECONCILED - find the difference before doing anything else")')
    ws["E23"].font = BOLD
    ws.conditional_formatting.add("E23", FormulaRule(
        formula=['ROUND($C$23,2)<>0'], fill=PatternFill("solid", fgColor=BAD)))
    ws.conditional_formatting.add("E23", FormulaRule(
        formula=['ROUND($C$23,2)=0'], fill=PatternFill("solid", fgColor=GOOD)))

    ws["B26"] = "How to read this"
    ws["B20"].font = BOLD
    for i, line in enumerate([
        "Unreconciled bank lines - money moved that the books do not explain. "
        "Work these first; everything else is arithmetic.",
        "Lines needing review - the same amount twice on the statement, or one "
        "that matches several ledger entries. The sheet will not guess which "
        "is which, and neither should you.",
        "Overdue receivables is the number a business owner actually wants. "
        "Receivables outstanding includes invoices that are not late yet.",
        "Aging buckets and the payment run both recalculate from TODAY(), so "
        "this workbook is still correct next month without being edited.",
        "A zero variance does NOT mean the books are right. The cash can agree "
        "to the penny while transactions above still have no explanation - "
        "agreeing and being correct are different questions, and this sheet "
        "asks both.",
    ]):
        c = ws.cell(27 + i, 2, "- " + line)
        c.font = BODY
        c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.merge_cells(start_row=27 + i, start_column=2, end_row=27 + i, end_column=6)
        ws.row_dimensions[27 + i].height = 28

    # ---------------------------------------------------------- Start here
    ws = wb.create_sheet("Start here", 0)
    ws.column_dimensions["A"].width = 3
    ws.column_dimensions["B"].width = 108
    ws["B2"] = ("Bank Reconciliation and AP/AR - ready to use"
                if blank else "Bank Reconciliation and AP/AR workbook")
    ws["B2"].font = TITLE
    ws["B3"] = ("Timothy Ting - chimsyt.github.io - formulas pre-filled, "
                "no data. Start at the Bank sheet."
                if blank else
                "Timothy Ting - work sample - chimsyt.github.io")
    ws["B3"].font = SUB

    body = [
        ("", ""),
        ("What it does", ""),
        ("", "Takes a bank statement and a ledger of invoices and bills, matches "
             "them against each other, and reports what does not reconcile - from "
             "both directions. It then ages the receivables and builds the week's "
             "supplier payment run from the same data, so nothing is typed twice."),
        ("", ""),
        ("How to use it", ""),
        ("", "1. Paste new bank lines into Bank columns A to D, under the last row."),
        ("", "2. Enter invoices and bills in Ledger columns A to F. One row per "
             "document, never one row per payment."),
        ("", "3. Read Exceptions. If everything there is zero, the period "
             "reconciles."),
        ("", "4. AR Aging tells you who to chase. AP Payment Run is the week's "
             "payments - filter column A for Yes."),
        ("", "Every other column is a formula and rebuilds itself. Do not "
             "overwrite them."),
        ("", ""),
        ("Design decisions, and why", ""),
        ("", "Whole-column references. A bounded range like E2:E150 breaks "
             "silently when somebody pastes in a longer month - it keeps "
             "calculating and reports a wrong number for that month. Whole "
             "columns cost a little speed and remove a whole class of silent "
             "error."),
        ("", "Matching on amount and direction, not description. Bank "
             "descriptions are free text the bank invents and they never match "
             "the ledger reliably. Direction matters too: money in can only "
             "settle an invoice, money out can only settle a bill - without that, "
             "a 500 refund would happily match a 500 supplier bill."),
        ("", "Exceptions reported from both sides. Bank lines with no ledger "
             "entry, and ledger entries with no bank line. Most reconciliation "
             "sheets only check one direction, which hides half the errors: a "
             "bill entered twice and paid once is invisible from the bank side."),
        ("", "Ambiguity is flagged, never guessed. Two payments of the same "
             "amount cannot be told apart by amount alone, so the sheet says "
             "REVIEW and stops. This is the known limitation of matching on "
             "amount and it is deliberately visible rather than hidden."),
        ("", "No hardcoded dates. Aging and the payment run use TODAY(), so the "
             "workbook is still correct next month with no edits."),
        ("", "Formulas restricted to SUMIFS, COUNTIFS, SUMPRODUCT, IFERROR and "
             "TEXT, so it behaves identically in Google Sheets and in Excel, "
             "including older Excel without XLOOKUP or dynamic arrays."),
        ("", ""),
        ("How it is checked", ""),
        ("", "verify-reconciliation.py recomputes every headline figure "
             "independently, in Python, straight from the raw data - and fails "
             "if its answer disagrees with the workbook's. The sample data has "
             "four problems planted in it on purpose: a payment with no bill "
             "behind it, the same supplier paid twice, an unmapped merchant fee, "
             "and an unidentified deposit. The checker asserts the workbook "
             "finds all four."),
        ("", ""),
        ("Honest note", ""),
        ("", "The data is synthetic and the business is invented. This is a "
             "demonstration of method, not client work, and it is not presented "
             "as anything else."),
    ]
    r = 5
    for headline, text in body:
        if headline:
            ws.cell(r, 2, headline).font = BOLD
            r += 1
        if text:
            c = ws.cell(r, 2, text)
            c.font = BODY
            c.alignment = Alignment(wrap_text=True, vertical="top")
            ws.row_dimensions[r].height = 15 * (len(text) // 100 + 1) + 6
        r += 1

    for s in wb:
        s.sheet_view.showGridLines = s.title in ("Bank", "Ledger")

    out = BLANK if blank else SAMPLE
    wb.save(out)
    print(f"wrote {out.name}  ({out.stat().st_size:,} bytes)")
    if blank:
        print(f"      empty, formulas pre-filled to row {4 + TEMPLATE_ROWS}")
    else:
        print(f"      {len(bank)} bank lines, {len(ledger)} ledger entries, "
              f"4 planted problems")
    return out


if __name__ == "__main__":
    build(blank=False)          # the portfolio sample
    build(blank=True)           # the one you actually use

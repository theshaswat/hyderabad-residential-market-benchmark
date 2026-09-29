"""Build output/Hyderabad_Residential_Benchmark.xlsx. Inputs are pulled from the sourced
facts table with SUMIFS, so every calculated cell traces back to a filing page."""
import csv
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
import model

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "Hyderabad_Residential_Benchmark.xlsx"
NAVY, BLUE, GREY, LIGHT = "0D253D", "0F62FE", "525252", "F4F4F4"
H = Font(name="Calibri", bold=True, color="FFFFFF", size=10)
HF = PatternFill("solid", fgColor=NAVY)
INP = Font(name="Calibri", color=BLUE, size=10)
CALC = Font(name="Calibri", color="161616", size=10)
NOTE = Font(name="Calibri", italic=True, color=GREY, size=9)
TITLE = Font(name="Calibri", bold=True, size=14, color=NAVY)
ASSUME = PatternFill("solid", fgColor="FFF4CC")
thin = Side(style="thin", color="E0E0E0")

def head(ws, row, labels, widths=None):
    for i, t in enumerate(labels, 1):
        c = ws.cell(row, i, t); c.font, c.fill = H, HF
        c.alignment = Alignment(wrap_text=True, vertical="center")
    if widths:
        for i, w in enumerate(widths, 1): ws.column_dimensions[L(i)].width = w

def q(dev, per, metric):
    return f'SUMIFS(Inputs!$D:$D,Inputs!$A:$A,"{dev}",Inputs!$B:$B,"{per}",Inputs!$C:$C,"{metric}")'

def title(ws, text, sub):
    ws["A1"], ws["A1"].font = text, TITLE
    ws["A2"], ws["A2"].font = sub, NOTE

def fmt(ws, rng, nf):
    cells = ws[rng]
    for row in (cells if isinstance(cells, tuple) else ((cells,),)):
        for c in row: c.number_format = nf

rows = list(csv.DictReader((ROOT / "data" / "hyderabad_developer_metrics.csv").open()))
wb = Workbook()

# ---- Inputs
ws = wb.active; ws.title = "Inputs"
title(ws, "Inputs — every figure as printed in the developer's own filing", "Blue = typed from source. Page = PDF page number in the source file.")
head(ws, 4, ["Developer", "Period", "Metric", "Value", "Unit", "Source file", "PDF page", "Note"], [11, 12, 44, 12, 9, 40, 9, 60])
for i, r in enumerate(rows, 5):
    vals = [r["developer"], r["period"], r["metric"], float(r["value"]), r["unit"], r["source_file"], int(r["pdf_page"]), r["note"]]
    for j, v in enumerate(vals, 1):
        c = ws.cell(i, j, v); c.font = INP if j == 4 else CALC
ws.freeze_panes = "A5"; ws.auto_filter.ref = f"A4:H{4 + len(rows)}"
fmt(ws, f"D5:D{4 + len(rows)}", "#,##0.00")

# ---- Share of sales
ws = wb.create_sheet("Share")
title(ws, "Hyderabad share of residential sales, by developer", "Sales in INR crore. Prestige reports INR mn; converted at 10 mn = 1 cr.")
head(ws, 4, ["Developer", "Period", "Hyderabad sales (INR cr)", "Total sales (INR cr)", "Hyderabad share", "Share printed by company", "Difference (pts)", "Basis"], [12, 12, 20, 18, 16, 20, 16, 52])
share = [
    ("Prestige", "Q1 FY27", f"={q('Prestige','Q1 FY27','presales_Hyderabad')}/10", f"={q('Prestige','Q1 FY27','presales_Total')}/10", 0.49, "Reported by city (INR mn)"),
    ("Prestige", "Q4 FY26", f"={q('Prestige','Q4 FY26','presales_Hyderabad')}/10", f"={q('Prestige','Q4 FY26','presales_Total')}/10", None, "Reported by city (INR mn)"),
    ("Prestige", "FY26", f"={q('Prestige','FY26','presales_Hyderabad')}/10", f"={q('Prestige','FY26','presales_Total')}/10", None, "Reported by city (INR mn)"),
    ("Godrej", "Q1 FY27", f"={q('Godrej','Q1 FY27','booking_Hyderabad')}", f"={q('Godrej','Q1 FY27','booking_Total')}", 0.05, "Reported by city (INR cr)"),
    ("Godrej", "Q4 FY26", f"={q('Godrej','Q4 FY26','booking_Hyderabad')}", None, None, "Q4 total not extracted; share not shown"),
    ("Godrej", "FY26", f"={q('Godrej','FY26','booking_Hyderabad')}", f"=SUM({q('Godrej','FY26','booking_MMR')},{q('Godrej','FY26','booking_Bengaluru')},{q('Godrej','FY26','booking_NCR')},{q('Godrej','FY26','booking_Pune')},{q('Godrej','FY26','booking_Hyderabad')},{q('Godrej','FY26','booking_Others')})", None, "Total = sum of six cities printed in the press release"),
    ("Brigade", "Q1 FY27", f"=D11*{q('Brigade','Q1 FY27','hyderabad_share_printed')}/100", f"={q('Brigade','Q1 FY27','presales_Total')}", 0.14, "Company prints share only (chart); INR cr is derived"),
    ("Prestige", "Q3 FY26", f"=D12*{q('Prestige','Q3 FY26','hyderabad_share_printed')}/100", f"={q('Prestige','Q3 FY26','presales_Total')}/10", 0.16, "Company prints share only; INR cr is derived"),
    ("Prestige", "Q2 FY26", f"=D13*{q('Prestige','Q2 FY26','hyderabad_share_printed')}/100", f"={q('Prestige','Q2 FY26','presales_Total')}/10", 0.11, "Company prints share only; INR cr is derived"),
]
for i, (dev, per, hy, tot, printed, basis) in enumerate(share, 5):
    ws.cell(i, 1, dev); ws.cell(i, 2, per); ws.cell(i, 3, hy); ws.cell(i, 4, tot)
    if tot is not None: ws.cell(i, 5, f"=C{i}/D{i}")
    if printed is not None:
        ws.cell(i, 6, printed).font = INP; ws.cell(i, 7, f"=(E{i}-F{i})*100")
    ws.cell(i, 8, basis).font = NOTE
fmt(ws, "C5:D13", "#,##0"); fmt(ws, "E5:F13", "0.0%"); fmt(ws, "G5:G13", "0.0")
ws["A15"], ws["A15"].font = "Prestige's share moved from 5% (Q4 FY26) to 49% (Q1 FY27) on one launch, Prestige Golden Grove, Tellapur, which alone sold INR 2,991 cr in the quarter.", NOTE
ws["A16"] = f"=\"Golden Grove sales as % of Prestige Hyderabad Q1 FY27: \"&TEXT({q('Prestige','Q1 FY27','sales_Prestige Golden Grove')}/{q('Prestige','Q1 FY27','presales_Hyderabad')},\"0.0%\")"
ws["A16"].font = NOTE

# ---- Realisation
ws = wb.create_sheet("Realisation")
title(ws, "Price benchmark — INR per sq ft", "INR/sft = value (INR cr) x 10 / area (mn sft). Areas as printed (2 dp); rounding shown in the last column.")
head(ws, 4, ["Developer", "Project / scope", "Micro-market (as stated)", "Basis", "Value (INR cr)", "Area (mn sft)", "INR per sq ft", "Area rounding effect"], [12, 36, 22, 40, 14, 13, 14, 20])
def rrow(i, dev, name, mm, basis, val, area):
    ws.cell(i, 1, dev); ws.cell(i, 2, name); ws.cell(i, 3, mm); ws.cell(i, 4, basis)
    ws.cell(i, 5, val); ws.cell(i, 6, area); ws.cell(i, 7, f"=E{i}*10/F{i}"); ws.cell(i, 8, f"=0.005/F{i}")
rrow(5, "Godrej", "Regal Pavilion", "Hyderabad (not stated)", "Booked to 30 Jun 2026", f"={q('Godrej','30 Jun 2026','booking_value_ptd_Godrej Regal Pavilion')}", f"={q('Godrej','30 Jun 2026','sold_Godrej Regal Pavilion')}")
rrow(6, "Godrej", "Madison Avenue", "Kokapet", "Booked to 30 Jun 2026", f"={q('Godrej','30 Jun 2026','booking_value_ptd_Godrej Madison Avenue')}", f"={q('Godrej','30 Jun 2026','sold_Godrej Madison Avenue')}")
rrow(7, "Godrej", "Brooklyn Avenue", "Kukatpally", "Launch quarter, Q1 FY27", f"={q('Godrej','Q1 FY27','booking_Godrej Brooklyn Avenue')}", f"={q('Godrej','Q1 FY27','booking_area_Godrej Brooklyn Avenue')}")
rrow(8, "Godrej", "Regal Pavilion, latest quarter", "Hyderabad (not stated)", "Q1 FY27 bookings", f"={q('Godrej','Q1 FY27','booking_Godrej Regal Pavilion')}", f"={q('Godrej','Q1 FY27','booking_area_Godrej Regal Pavilion')}")
rrow(9, "Godrej", "Regal Pavilion, FY26", "Hyderabad (not stated)", "FY26 bookings", f"={q('Godrej','FY26','booking_Godrej Regal Pavilion')}", f"={q('Godrej','FY26','booking_area_Godrej Regal Pavilion')}")
rrow(10, "Godrej", "All Hyderabad launches, FY26", "Hyderabad", "Launch value / launch area", f"={q('Godrej','FY26','hyderabad_launch_value')}", f"={q('Godrej','FY26','hyderabad_launch_area')}")
ws.cell(11, 1, "Prestige"); ws.cell(11, 2, "Unsold Hyderabad stock"); ws.cell(11, 3, "Hyderabad (all)"); ws.cell(11, 4, "Value of stock / area of stock, 30 Jun 2026")
ws.cell(11, 5, f"={q('Prestige','Q1 FY27','stock_value_Hyderabad')}/10"); ws.cell(11, 6, f"={q('Prestige','Q1 FY27','stock_area_Hyderabad')}"); ws.cell(11, 7, "=E11*10/F11"); ws.cell(11, 8, "=0.05/F11")
ws["D11"].alignment = Alignment(wrap_text=True)
ws.cell(13, 1, "Company-wide comparators").font = Font(name="Calibri", bold=True, color=NAVY)
ws.cell(14, 1, "Godrej"); ws.cell(14, 2, "All cities, Q1 FY27"); ws.cell(14, 4, "Bookings / area sold")
ws.cell(14, 5, f"={q('Godrej','Q1 FY27','booking_Total')}"); ws.cell(14, 6, f"={q('Godrej','Q1 FY27','booking_area_Total')}"); ws.cell(14, 7, "=E14*10/F14"); ws.cell(14, 8, "=0.05/F14")
ws.cell(15, 1, "Brigade"); ws.cell(15, 2, "All cities, Q1 FY27"); ws.cell(15, 4, "Average realisation printed"); ws.cell(15, 7, f"={q('Brigade','Q1 FY27','avg_realisation_total')}")
ws.cell(16, 1, "Prestige"); ws.cell(16, 2, "All cities, apartments, Q1 FY27"); ws.cell(16, 4, "Average realisation printed"); ws.cell(16, 7, f"={q('Prestige','Q1 FY27','avg_realisation_apartments')}")
ws.cell(18, 1, "Godrej Regal Pavilion vs Godrej company average"); ws.cell(18, 7, "=G5/G14-1")
ws.cell(19, 1, "Godrej Madison Avenue (Kokapet) vs Regal Pavilion"); ws.cell(19, 7, "=G6/G5-1")
fmt(ws, "E5:F16", "#,##0.00"); fmt(ws, "G5:G16", "#,##0"); fmt(ws, "H5:H16", "0.0%"); fmt(ws, "G18:G19", "0.0%")
ws["A21"], ws["A21"].font = "Godrej Q1 FY27 Hyderabad city area (0.4 mn sft) is printed to 1 dp, so it is not used for a per-sq-ft figure. Prestige stock value/area is an asking-price view of unsold inventory, not a sales realisation.", NOTE

# ---- Pipeline
ws = wb.create_sheet("Pipeline")
title(ws, "Launch pipeline and land adds in Hyderabad", "Micro-market = the place name printed in the filing. GDV / expected value are company estimates, not realised sales.")
head(ws, 4, ["Developer", "Project / land", "Micro-market", "Status", "Area (mn sft)", "Land (acres)", "Value (INR cr)", "Value per sq ft (INR)", "Value per acre (INR cr)", "Area basis"], [12, 36, 22, 38, 12, 11, 14, 16, 16, 44])
def prow(i, dev, name, mm, st, area, acres, val, basis):
    for j, v in enumerate([dev, name, mm, st], 1): ws.cell(i, j, v)
    if area: ws.cell(i, 5, area)
    if acres: ws.cell(i, 6, acres)
    if val: ws.cell(i, 7, val)
    if area and val: ws.cell(i, 8, f"=G{i}*10/E{i}")
    if acres and val: ws.cell(i, 9, f"=G{i}/F{i}")
    ws.cell(i, 10, basis).font = NOTE
P = "Prestige"
prow(5, P, "Prestige Golden Grove", "Tellapur", "Launched Q1 FY27", f"={q(P,'Q1 FY27','launch_tda_Prestige Golden Grove')}", f"={q(P,'Q1 FY26','land_acres_Tellapur (Prestige Golden Grove)')}", f"={q(P,'Q1 FY27','launch_gdv_Prestige Golden Grove')}/10", "Total developable area (not saleable)")
prow(6, P, "Prestige Rock Cliff", "Hyderabad", "Planned, luxury", f"={q(P,'Q1 FY27','launch_tda_Prestige Rock Cliff')}", None, f"={q(P,'Q1 FY27','launch_gdv_Prestige Rock Cliff')}/10", "Total developable area (not saleable)")
prow(7, P, "The Prestige Place", "Hyderabad", "Planned, mid-segment", f"={q(P,'Q1 FY27','launch_tda_The Prestige Place')}", None, f"={q(P,'Q1 FY27','launch_gdv_The Prestige Place')}/10", "Total developable area (not saleable)")
for i, (nm, mm, qq) in enumerate([("Pulimamidi", "Pulimamidi", "Q1 FY26"), ("Raidurg", "Raidurg", "Q2 FY26"), ("Lakdaram", "Lakdaram", "Q3 FY26"),
                                  ("Rajendra Nagar", "Rajendra Nagar", "Q3 FY26"), ("Kompally", "Kompally", "Q4 FY26")], 8):
    prow(i, P, f"Land added, {nm}", mm, f"Land bank, added {qq}", None, f"={q(P,qq,'land_acres_'+nm)}", f"={q(P,qq,'land_gdv_'+nm)}/10", "Tentative GDV of area for sale")
prow(13, "Godrej", "Neopolis", "Kokapet", "Added FY26; not yet launched", f"={q('Godrej','FY26','bd_area_Neopolis (Kokapet)')}", None, f"={q('Godrej','FY26','bd_value_Neopolis (Kokapet)')}", "Estimated saleable area")
prow(14, "Godrej", "Kukatpally", "Kukatpally", "Added FY26; Brooklyn Avenue launched", f"={q('Godrej','FY26','bd_area_Kukatpally')}", None, f"={q('Godrej','FY26','bd_value_Kukatpally')}", "Estimated saleable area")
prow(15, "Brigade", "Upcoming residential (Enclave, Manor)", "Hyderabad", "Planned", f"={q('Brigade','Q1 FY27','upcoming_launch_area_Hyderabad')}", f"={q('Brigade','30 Jun 2026','land_acres_Hyderabad')}", None, "Planned launch area; land is all Hyderabad holdings")
fmt(ws, "E5:F15", "#,##0.00"); fmt(ws, "G5:G15", "#,##0"); fmt(ws, "H5:H15", "#,##0"); fmt(ws, "I5:I15", "#,##0.0")
ws["A17"], ws["A17"].font = "Prestige lines are GDV on developable area, so per-sq-ft is a floor against saleable price. Godrej lines are expected booking value on saleable area. Do not compare the two columns directly.", NOTE

# ---- CashFlow
ws = wb.create_sheet("CashFlow")
title(ws, "Project cash-flow and cost-to-complete: Godrej Regal Pavilion, Hyderabad", "Disclosed position at 30 Jun 2026. Yellow cells are assumptions; each is sourced or marked illustrative. INR crore unless stated.")
ws.column_dimensions["A"].width = 46
for c in range(2, 20): ws.column_dimensions[L(c)].width = 11
lab = {4: "Total saleable area (mn sft)", 5: "Sold to date (mn sft)", 6: "Booking value to date (INR cr)", 7: "Collected to date (INR cr)",
       8: "Realisation on sold area (INR per sft)", 9: "Unsold area (mn sft)", 10: "Booked but not yet collected (INR cr)"}
src = {4: f"={q('Godrej','30 Jun 2026','total_saleable_Godrej Regal Pavilion')}", 5: f"={q('Godrej','30 Jun 2026','sold_Godrej Regal Pavilion')}",
       6: f"={q('Godrej','30 Jun 2026','booking_value_ptd_Godrej Regal Pavilion')}", 7: f"={q('Godrej','30 Jun 2026','collection_ptd_Godrej Regal Pavilion')}",
       8: "=B6*10/B5", 9: "=B4-B5", 10: "=B6-B7"}
for r in lab: ws.cell(r, 1, lab[r]); ws.cell(r, 2, src[r]).font = INP if r < 8 else CALC
ws.cell(3, 1, "Disclosed").font = Font(name="Calibri", bold=True, color=NAVY)
ws.cell(12, 1, "Assumptions").font = Font(name="Calibri", bold=True, color=NAVY)
for j, t in enumerate(["Scenario selector (1 Base, 2 Slow, 3 Fast)"], 0): ws.cell(13, 1, t)
ws["B13"] = 1; ws["B13"].fill = ASSUME; ws["B13"].font = INP
head(ws, 14, ["Driver", "Live", "Base", "Slow", "Fast"], None); ws.cell(14, 6, "Where it comes from").font = Font(name="Calibri", bold=True, color=NAVY); ws.cell(14, 6).alignment = Alignment(indent=1)
b = lambda m: q("Brigade", "30 Jun 2026", "portfolio_" + m)
drv = [
    ("Sales velocity (mn sft per quarter)", f"={q('Godrej','Q1 FY27','booking_area_Godrej Regal Pavilion')}", "=C15/2", f"={q('Godrej','Q4 FY26','booking_area_Godrej Regal Pavilion')}", "Base = Regal Pavilion Q1 FY27 sales; Fast = its Q4 FY26 sales; Slow = half of Base (illustrative)"),
    ("Price change on unsold stock", 0, -0.05, 0.05, "Illustrative"),
    ("Construction cost as share of sale value", f"={b('est_total_cost')}/{b('est_sale_value')}", "=C17+0.05", "=C17-0.03", "Base = Brigade ongoing projects, estimated cost / sale value (a benchmark, not Godrej's cost). Slow/Fast illustrative"),
    ("Cost already incurred (share of total)", f"={b('cost_incurred')}/{b('est_total_cost')}", "=C18", "=C18", "Brigade ongoing projects, incurred / estimated cost (benchmark)"),
    ("Quarters to completion", 10, 12, 8, "Illustrative; Godrej does not disclose Regal Pavilion completion date"),
    ("Discount rate (annual)", 0.12, 0.12, 0.12, "Illustrative"),
]
for k, (nm, base, slow, fast, note) in enumerate(drv):
    r = 15 + k
    ws.cell(r, 1, nm); ws.cell(r, 3, base); ws.cell(r, 4, slow); ws.cell(r, 5, fast)
    ws.cell(r, 2, f"=CHOOSE($B$13,C{r},D{r},E{r})").font = CALC
    for c in (3, 4, 5): ws.cell(r, c).fill = ASSUME; ws.cell(r, c).font = INP
    ws.cell(r, 6, note).font = NOTE; ws.cell(r, 6).alignment = Alignment(indent=1)
fmt(ws, "B15:E15", "0.000"); fmt(ws, "B16:E16", "0.0%"); fmt(ws, "B17:E18", "0.0%"); fmt(ws, "B19:E19", "0"); fmt(ws, "B20:E20", "0.0%")
ws["A22"], ws["A22"].font = "Derived", Font(name="Calibri", bold=True, color=NAVY)
der = [(23, "Price on unsold stock (INR per sft)", "=B8*(1+B16)"), (24, "Estimated total sale value (INR cr)", "=B6+B9*B23/10"),
       (25, "Estimated total cost (INR cr)", "=B17*B24"), (26, "Cost to complete (INR cr)", "=B25*(1-B18)")]
for r, t, fm in der: ws.cell(r, 1, t); ws.cell(r, 2, fm)
fmt(ws, "B23:B26", "#,##0")
fmt(ws, "B4:B5", "0.00"); fmt(ws, "B6:B7", "#,##0"); fmt(ws, "B8", "#,##0"); fmt(ws, "B9", "0.00"); fmt(ws, "B10", "#,##0")
NQ = model.HORIZON; C0 = 3
ws.cell(28, 1, "Quarterly schedule").font = Font(name="Calibri", bold=True, color=NAVY)
labels = {29: "Quarter", 30: "Area sold (mn sft)", 31: "New bookings (INR cr)", 32: "Booked not collected, opening", 33: "Collections",
          34: "Booked not collected, closing", 35: "Construction outflow", 36: "Net operating cash flow", 37: "Cumulative net cash flow", 38: "Discount factor"}
for r, t in labels.items(): ws.cell(r, 1, t)
for t in range(1, NQ + 1):
    c = C0 + t - 1; col = L(c); prev = L(c - 1)
    ws.cell(29, c, t).font = Font(name="Calibri", bold=True)
    sold_prev = f"SUM($C$30:{prev}30)" if t > 1 else "0"
    ws.cell(30, c, f"=MIN($B$15,$B$9-{sold_prev})")
    ws.cell(31, c, f"={col}30*$B$23/10")
    ws.cell(32, c, "=$B$10" if t == 1 else f"={prev}34")
    ws.cell(33, c, f"=IF({col}29<$B$19,({col}32+{col}31)/($B$19-{col}29+1),{col}32+{col}31)")
    ws.cell(34, c, f"={col}32+{col}31-{col}33")
    ws.cell(35, c, f"=IF({col}29<=$B$19,$B$26/$B$19,0)")
    ws.cell(36, c, f"={col}33-{col}35")
    ws.cell(37, c, f"={col}36" if t == 1 else f"={prev}37+{col}36")
    ws.cell(38, c, f"=1/(1+$B$20)^({col}29/4)")
last = L(C0 + NQ - 1)
fmt(ws, f"C30:{last}30", "0.00"); fmt(ws, f"C31:{last}37", "#,##0"); fmt(ws, f"C38:{last}38", "0.000")
ws["A40"], ws["A40"].font = "Outputs (selected scenario)", Font(name="Calibri", bold=True, color=NAVY)
outs = [(41, "Collections over the horizon (INR cr)", f"=SUM(C33:{last}33)"), (42, "Cost to complete (INR cr)", "=B26"),
        (43, "Net operating cash flow, undiscounted (INR cr)", "=B41-B42"), (44, "NPV at the discount rate (INR cr)", f"=SUMPRODUCT(C36:{last}36,C38:{last}38)"),
        (45, "Peak funding need (INR cr; 0 = self-funding)", f"=MIN(0,MIN(C37:{last}37))"), (46, "Collections cover cost-to-complete (x)", "=B41/B42"),
        (47, "Area still unsold at horizon (mn sft)", f"=B9-SUM(C30:{last}30)")]
for r, t, fm in outs: ws.cell(r, 1, t); ws.cell(r, 2, fm).font = Font(name="Calibri", bold=True)
fmt(ws, "B41:B45", "#,##0"); fmt(ws, "B46", "0.00"); fmt(ws, "B47", "0.00")
ws["A49"], ws["A49"].font = "Scenario summary (values from src/model.py; rerun to refresh)", Font(name="Calibri", bold=True, color=NAVY)
head(ws, 50, ["Metric", "Base", "Slow", "Fast"], None)
F = model.facts(); ci = model.case_inputs(F); scs = model.scenarios(ci); res = {k: model.run(ci, s) for k, s in scs.items()}
for i, (t, key, nf) in enumerate([("Collections (INR cr)", "collections", "#,##0"), ("Cost to complete (INR cr)", "to_complete", "#,##0"),
                                  ("Net operating cash flow (INR cr)", "net", "#,##0"), ("NPV (INR cr)", "npv", "#,##0"),
                                  ("Peak funding need (INR cr)", "peak", "#,##0"), ("Collections / cost to complete (x)", "coverage", "0.00"),
                                  ("Unsold at horizon (mn sft)", "unsold_end", "0.00")], 51):
    ws.cell(i, 1, t)
    for k in (1, 2, 3): c = ws.cell(i, 1 + k, round(res[k][key], 4)); c.number_format = nf
ws["A59"], ws["A59"].font = "Not modelled: land cost, financing cost, GST, approvals, overheads, or Godrej's actual cost. Brigade's ratios are a stand-in and mostly Bengaluru.", NOTE
ws.freeze_panes = "B4"

# ---- Checks
ws = wb.create_sheet("Checks")
title(ws, "Reconciliation checks", "Each check recomputes a printed total from its printed parts. TRUE = ties.")
head(ws, 4, ["Check", "Recomputed", "Printed", "Difference", "Tolerance", "Ties?"], [64, 14, 14, 12, 11, 8])
chk = [
    ("Prestige Q1 FY27: six city sales sum to total (INR mn)", "=" + "+".join(q("Prestige", "Q1 FY27", "presales_" + c) for c in ["Hyderabad", "Bengaluru", "Mumbai", "NCR", "Chennai", "Others"]), "=" + q("Prestige", "Q1 FY27", "presales_Total"), 0),
    ("Godrej Q1 FY27: six city bookings sum to total (INR cr)", "=" + "+".join(q("Godrej", "Q1 FY27", "booking_" + c) for c in ["Hyderabad", "Bengaluru", "MMR", "NCR", "Pune", "Others"]), "=" + q("Godrej", "Q1 FY27", "booking_Total"), 0),
    ("Prestige Q1 FY27: Hyderabad share vs printed 49% (pts x100)", "=ROUND(Share!E5*100,0)", 49, 0),
    ("Godrej Q1 FY27: Hyderabad share vs printed 5% (pts x100)", "=ROUND(Share!E8*100,0)", 5, 0),
    ("Godrej Regal Pavilion: FY26 area/value tie to Q4 FY26 project table", "=" + q("Godrej", "FY26", "booking_Godrej Regal Pavilion"), 2328, 0),
    ("Prestige FY26 Hyderabad share vs printed 8% (pts x100)", "=ROUND(Share!E7*100,0)", 8, 0),
    ("Godrej Regal Pavilion: booked to date (register) vs FY26 bookings + Q1 FY27 bookings (INR cr, rounding)", "=" + q("Godrej", "30 Jun 2026", "booking_value_ptd_Godrej Regal Pavilion"), "=" + q("Godrej", "FY26", "booking_Godrej Regal Pavilion") + "+" + q("Godrej", "Q1 FY27", "booking_Godrej Regal Pavilion"), 2),
    ("CashFlow: collections + closing balance = opening balance + bookings", f"=CashFlow!B41+CashFlow!{last}34", "=CashFlow!B10+SUM(CashFlow!C31:" + last + "31)", 0.001),
]
for i, (t, a, bb, tol) in enumerate(chk, 5):
    ws.cell(i, 1, t).alignment = Alignment(wrap_text=True); ws.cell(i, 2, a); ws.cell(i, 3, bb); ws.cell(i, 4, f"=B{i}-C{i}"); ws.cell(i, 5, tol); ws.cell(i, 6, f"=ABS(D{i})<=E{i}")
fmt(ws, "B5:D12", "#,##0.00")

# ---- Sources
ws = wb.create_sheet("Sources")
title(ws, "Sources", "All documents are the developers' own investor-relations publications, downloaded from their websites.")
head(ws, 4, ["Developer", "Document", "File"], [12, 52, 52])
docs = sorted({r["source_file"] for r in rows})
names = {"prestige": "Prestige Estates Projects", "godrej": "Godrej Properties", "brigade": "Brigade Enterprises"}
for i, d in enumerate(docs, 5):
    ws.cell(i, 1, names[d.split("_")[0]]); ws.cell(i, 2, d.replace(".pdf", "").split("_", 1)[1].replace("_", " ")); ws.cell(i, 3, d)

wb.move_sheet("Inputs", offset=len(wb.sheetnames))  # Inputs to the back; results first
from openpyxl.worksheet.properties import PageSetupProperties
for w in wb.worksheets:
    w.sheet_view.showGridLines = False
    w.page_setup.orientation = "landscape"; w.page_setup.fitToWidth = 1; w.page_setup.fitToHeight = 0
    w.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
wb.save(OUT); print("saved", OUT.name, [w.title for w in wb.worksheets])

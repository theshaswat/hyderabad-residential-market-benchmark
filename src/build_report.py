"""Build output/Hyderabad_Residential_Benchmark.pdf from the sourced facts and the model."""
from pathlib import Path
import matplotlib
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether, PageBreak, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle)
import model

ROOT = Path(__file__).resolve().parents[1]
CH = ROOT / "output" / "charts"
fd = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
pdfmetrics.registerFont(TTFont("DV", str(fd / "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DV-B", str(fd / "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B")

NAVY, AMBER, INK, MUT, HAIR, SURF = (colors.HexColor(x) for x in ("#0d253d", "#f7a501", "#161616", "#525252", "#d9d9d9", "#f4f4f4"))
S = dict(
    h1=ParagraphStyle("h1", fontName="DV-B", fontSize=15, leading=19, textColor=NAVY, spaceAfter=3, keepWithNext=1),
    sub=ParagraphStyle("sub", fontName="DV", fontSize=9, leading=13, textColor=MUT, spaceAfter=8, keepWithNext=1),
    body=ParagraphStyle("body", fontName="DV", fontSize=9, leading=13.2, textColor=INK, spaceAfter=5, alignment=TA_LEFT),
    num=ParagraphStyle("num", fontName="DV", fontSize=9, leading=13.2, textColor=INK, leftIndent=14, firstLineIndent=-14, spaceAfter=5),
    small=ParagraphStyle("small", fontName="DV", fontSize=7.4, leading=10.2, textColor=MUT, spaceAfter=3),
    cell=ParagraphStyle("cell", fontName="DV", fontSize=7.8, leading=10.4, textColor=INK),
    cellb=ParagraphStyle("cellb", fontName="DV-B", fontSize=7.8, leading=10.4, textColor=colors.white),
)
P = lambda t, s="body": Paragraph(t, S[s])

F = model.facts(); ci = model.case_inputs(F); sc = model.scenarios(ci); res = {k: model.run(ci, s) for k, s in sc.items()}
g = lambda d, p, m: F[(d, p, m)]
n0 = lambda v: f"{v:,.0f}"
pre = lambda p: g("Prestige", p, "presales_Hyderabad") / g("Prestige", p, "presales_Total")
gg = g("Prestige", "Q1 FY27", "sales_Prestige Golden Grove")
pre_hy_q1 = g("Prestige", "Q1 FY27", "presales_Hyderabad")
gl_tot_fy = sum(g("Godrej", "FY26", "booking_" + c) for c in ["MMR", "Bengaluru", "NCR", "Pune", "Hyderabad", "Others"])
psf_regal = g("Godrej", "30 Jun 2026", "booking_value_ptd_Godrej Regal Pavilion") * 10 / g("Godrej", "30 Jun 2026", "sold_Godrej Regal Pavilion")
psf_mad = g("Godrej", "30 Jun 2026", "booking_value_ptd_Godrej Madison Avenue") * 10 / g("Godrej", "30 Jun 2026", "sold_Godrej Madison Avenue")
psf_brk = g("Godrej", "Q1 FY27", "booking_Godrej Brooklyn Avenue") * 10 / g("Godrej", "Q1 FY27", "booking_area_Godrej Brooklyn Avenue")
psf_gl = g("Godrej", "Q1 FY27", "booking_Total") * 10 / g("Godrej", "Q1 FY27", "booking_area_Total")
psf_stock = g("Prestige", "Q1 FY27", "stock_value_Hyderabad") / g("Prestige", "Q1 FY27", "stock_area_Hyderabad")
psf_launch = g("Godrej", "FY26", "hyderabad_launch_value") * 10 / g("Godrej", "FY26", "hyderabad_launch_area")
neo = g("Godrej", "FY26", "bd_value_Neopolis (Kokapet)") * 10 / g("Godrej", "FY26", "bd_area_Neopolis (Kokapet)")
kuk = g("Godrej", "FY26", "bd_value_Kukatpally") * 10 / g("Godrej", "FY26", "bd_area_Kukatpally")
b = res[1]

def tbl(data, widths, align_right=(), hdr=True):
    rows = [[Paragraph(str(c), S["cellb"] if (hdr and i == 0) else S["cell"]) for c in r] for i, r in enumerate(data)]
    t = Table(rows, colWidths=[w * mm for w in widths], repeatRows=1 if hdr else 0)
    st = [("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 3.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.2),
          ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
          ("LINEBELOW", (0, 0), (-1, -1), 0.4, HAIR)]
    if hdr: st += [("BACKGROUND", (0, 0), (-1, 0), NAVY)]
    for i in range(2, len(rows), 2): st.append(("BACKGROUND", (0, i), (-1, i), SURF))
    t.setStyle(TableStyle(st)); return t

def fig(name, w=174):
    from PIL import Image as PI
    pw, ph = PI.open(CH / name).size
    return Image(str(CH / name), width=w * mm, height=w * mm * ph / pw)

def frame_pages(c, d):
    c.saveState()
    if d.page == 1:
        c.setFillColor(NAVY); c.rect(0, A4[1] - 34 * mm, A4[0], 34 * mm, stroke=0, fill=1)
        c.setFillColor(AMBER); c.rect(18 * mm, A4[1] - 34 * mm, 26 * mm, 1.6 * mm, stroke=0, fill=1)
        c.setFillColor(colors.white); c.setFont("DV-B", 20); c.drawString(18 * mm, A4[1] - 16 * mm, "Hyderabad Residential Market Benchmark")
        c.setFont("DV", 9.5); c.drawString(18 * mm, A4[1] - 24 * mm, "What three listed developers disclose about selling and building homes in Hyderabad, to June 2026")
    c.setFont("DV", 7.2); c.setFillColor(MUT)
    c.drawString(18 * mm, 10 * mm, "Shaswat Sharma"); c.drawRightString(A4[0] - 18 * mm, 10 * mm, f"{d.page}")
    c.setStrokeColor(HAIR); c.setLineWidth(0.4); c.line(18 * mm, 14 * mm, A4[0] - 18 * mm, 14 * mm)
    c.restoreState()

doc = BaseDocTemplate(str(ROOT / "output" / "Hyderabad_Residential_Benchmark.pdf"), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                      topMargin=16 * mm, bottomMargin=20 * mm, title="Hyderabad Residential Market Benchmark", author="Shaswat Sharma")
W, Hh = A4
doc.addPageTemplates([PageTemplate("first", [Frame(18 * mm, 20 * mm, W - 36 * mm, Hh - 20 * mm - 40 * mm, id="f1", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=frame_pages),
                      PageTemplate("rest", [Frame(18 * mm, 20 * mm, W - 36 * mm, Hh - 20 * mm - 16 * mm, id="f2", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=frame_pages)])
from reportlab.platypus import NextPageTemplate
E = [NextPageTemplate("rest")]

# ---- page 1
E += [P("What the filings show", "h1"),
      P("Prestige, Godrej and Brigade each publish quarterly sales by city, project registers and launch pipelines. This brief reads those documents for Hyderabad. It covers three listed developers, not the whole market.", "sub")]
finds = [
    f"Prestige's Hyderabad share of sales went from <b>{pre('Q4 FY26'):.1%}</b> in Q4 FY26 to <b>{pre('Q1 FY27'):.1%}</b> in Q1 FY27. One launch, Golden Grove in Tellapur, sold ₹{gg/10:,.0f} crore, which is {gg/pre_hy_q1:.0%} of Prestige's Hyderabad sales that quarter.",
    f"The other two are far less exposed. Brigade printed a Hyderabad share of {g('Brigade','Q1 FY27','hyderabad_share_printed'):.0f}% of its ₹{g('Brigade','Q1 FY27','presales_Total'):,.0f} crore residential pre-sales. Godrej booked ₹{g('Godrej','Q1 FY27','booking_Hyderabad'):,.0f} crore in Hyderabad, {g('Godrej','Q1 FY27','booking_Hyderabad')/g('Godrej','Q1 FY27','booking_Total'):.1%} of its ₹{g('Godrej','Q1 FY27','booking_Total'):,.0f} crore.",
    f"Across FY26, Hyderabad was {g('Prestige','FY26','presales_Hyderabad')/g('Prestige','FY26','presales_Total'):.1%} of Prestige's sales and {g('Godrej','FY26','booking_Hyderabad')/gl_tot_fy:.1%} of Godrej's (₹{g('Godrej','FY26','booking_Hyderabad'):,.0f} crore of ₹{gl_tot_fy:,.0f} crore).",
    f"Godrej's Regal Pavilion has sold at ₹{psf_regal:,.0f} per sq ft, {1-psf_regal/psf_gl:.0%} below Godrej's company-wide ₹{psf_gl:,.0f}. Madison Avenue in Kokapet has sold at ₹{psf_mad:,.0f}, {psf_mad/psf_regal-1:.0%} above Regal Pavilion.",
    f"For projects not yet selling, Godrej's own estimates are ₹{neo:,.0f} per sq ft at Neopolis in Kokapet and ₹{kuk:,.0f} at Kukatpally, a {neo/kuk-1:.0%} gap.",
    f"A cash-flow view of Regal Pavilion, using disclosed sales and collections to 30 June 2026, shows ₹{n0(b['collections'])} crore of collections against ₹{n0(b['to_complete'])} crore of cost still to spend ({b['coverage']:.1f}x). The cost inputs are benchmarks, so treat this as a range test.",
]
for i, t in enumerate(finds, 1): E.append(Paragraph(f"<b>{i}.</b>&nbsp;&nbsp;{t}", S["num"]))
E += [Spacer(1, 4), KeepTogether([fig("01_share_of_sales.png"), P("Sources: Prestige Q1 FY27 and Q4 FY26 investor presentations; Godrej Q1 FY27 press release; Brigade Q1 FY27 presentation. Brigade prints the share only.", "small")])]

# ---- page 2 price
E += [PageBreak(), P("Price per sq ft", "h1"),
      P("Value divided by area for Godrej's Hyderabad projects, set against each developer's company-wide figure. The bars are not all the same kind of number, so read the key under the chart.", "sub"),
      fig("02_price_per_sqft.png"),
      Spacer(1, 6)]
E.append(KeepTogether([tbl([
    ["Project or scope", "Micro-market as stated", "₹ per sq ft", "Value ₹ cr", "Area mn sft", "Basis"],
    ["Regal Pavilion", "Not stated", n0(psf_regal), n0(g("Godrej","30 Jun 2026","booking_value_ptd_Godrej Regal Pavilion")), f"{g('Godrej','30 Jun 2026','sold_Godrej Regal Pavilion'):.2f}", "Booked to 30 Jun 2026"],
    ["Madison Avenue", "Kokapet", n0(psf_mad), n0(g("Godrej","30 Jun 2026","booking_value_ptd_Godrej Madison Avenue")), f"{g('Godrej','30 Jun 2026','sold_Godrej Madison Avenue'):.2f}", "Booked to 30 Jun 2026"],
    ["Brooklyn Avenue", "Kukatpally", n0(psf_brk), n0(g("Godrej","Q1 FY27","booking_Godrej Brooklyn Avenue")), f"{g('Godrej','Q1 FY27','booking_area_Godrej Brooklyn Avenue'):.2f}", "Launch quarter, Q1 FY27"],
    ["Hyderabad launches, FY26", "Hyderabad", n0(psf_launch), n0(g("Godrej","FY26","hyderabad_launch_value")), f"{g('Godrej','FY26','hyderabad_launch_area'):.1f}", "Launch value / launch area"],
    ["Prestige unsold stock", "Hyderabad", n0(psf_stock), n0(g("Prestige","Q1 FY27","stock_value_Hyderabad")/10), f"{g('Prestige','Q1 FY27','stock_area_Hyderabad'):.1f}", "Stock value / stock area"],
], [40, 30, 20, 20, 20, 44], ), P("Areas are printed to two decimals (one for the last two rows), so a per-sq-ft figure can move by roughly the rounding share of the area: about 2% for Brooklyn Avenue's 0.26 mn sft, under 1% elsewhere. Prestige's stock figure is an asking-price view of unsold inventory. It is not a sales realisation.", "small")]))
E.append(Spacer(1, 6))
E.append(P(f"Godrej does not name the micro-market for Regal Pavilion in these filings, so this brief does not either. The gap between it and Madison Avenue is a fact about two Godrej projects; it is not a claim about a location premium.", "body"))

# ---- page 3 pipeline
E += [PageBreak(), P("Pipeline and land", "h1"),
      P("Prestige added six Hyderabad parcels in FY26. Godrej added two large Hyderabad sites. Values are the developers' own estimates, not sales.", "sub"),
      fig("03_land_adds.png"), Spacer(1, 6)]
rows = [["Developer", "Project", "Market", "Area mn sft", "Value ₹ cr", "₹ / sq ft", "Basis"]]
for nm, mkt, ar, gd, basis in [("Golden Grove (launched Q1 FY27)", "Tellapur", g("Prestige","Q1 FY27","launch_tda_Prestige Golden Grove"), g("Prestige","Q1 FY27","launch_gdv_Prestige Golden Grove")/10, "GDV, developable area"),
                              ("Rock Cliff (planned, luxury)", "Hyderabad", g("Prestige","Q1 FY27","launch_tda_Prestige Rock Cliff"), g("Prestige","Q1 FY27","launch_gdv_Prestige Rock Cliff")/10, "GDV, developable area"),
                              ("The Prestige Place (planned)", "Hyderabad", g("Prestige","Q1 FY27","launch_tda_The Prestige Place"), g("Prestige","Q1 FY27","launch_gdv_The Prestige Place")/10, "GDV, developable area")]:
    rows.append(["Prestige", nm, mkt, f"{ar:.2f}", n0(gd), n0(gd * 10 / ar), basis])
rows.append(["Godrej", "Neopolis (added FY26)", "Kokapet", f"{g('Godrej','FY26','bd_area_Neopolis (Kokapet)'):.2f}", n0(g("Godrej","FY26","bd_value_Neopolis (Kokapet)")), n0(neo), "Expected booking value, saleable area"])
rows.append(["Godrej", "Kukatpally site (added FY26)", "Kukatpally", f"{g('Godrej','FY26','bd_area_Kukatpally'):.2f}", n0(g("Godrej","FY26","bd_value_Kukatpally")), n0(kuk), "Expected booking value, saleable area"])
rows.append(["Brigade", "Enclave and Manor (planned)", "Hyderabad", f"{g('Brigade','Q1 FY27','upcoming_launch_area_Hyderabad'):.2f}", "n/d", "n/d", "Planned launch area; 22 acres held in the city"])
E.append(KeepTogether([tbl(rows, [21, 40, 20, 17, 17, 17, 42]), P("Prestige lines use gross development value on total developable area, which includes space that is not sold, so they read low against Godrej's saleable-area figures. Do not compare the two directly. n/d: not disclosed.", "small")]))

# ---- page 4 cash flow
E += [PageBreak(), P("Project cash-flow view: Godrej Regal Pavilion", "h1"),
      P("Disclosed position at 30 June 2026, then quarter-by-quarter collections and construction spend under three scenarios. All figures ₹ crore unless stated.", "sub"), fig("04_cash_flow.png"), Spacer(1, 6)]
E.append(KeepTogether([tbl([
    ["Disclosed at 30 Jun 2026", "Value", "Assumption", "Base", "Slow", "Fast"],
    ["Total saleable area", f"{ci['total']:.2f} mn sft", "Sales, mn sft a quarter", f"{sc[1]['vel']:.3f}", f"{sc[2]['vel']:.3f}", f"{sc[3]['vel']:.2f}"],
    ["Sold to date", f"{ci['sold']:.2f} mn sft", "Price change on unsold", "0%", f"{sc[2]['price']:.0%}", f"+{sc[3]['price']:.0%}"],
    ["Booking value to date", n0(ci['booked']), "Cost as share of sale value", f"{sc[1]['cost']:.1%}", f"{sc[2]['cost']:.1%}", f"{sc[3]['cost']:.1%}"],
    ["Collected to date", n0(ci['collected']), "Cost already incurred", f"{ci['progress']:.1%}", f"{ci['progress']:.1%}", f"{ci['progress']:.1%}"],
    ["Realised price", f"₹{ci['psf']:,.0f} per sft", "Quarters to completion", f"{sc[1]['T']}", f"{sc[2]['T']}", f"{sc[3]['T']}"],
], [38, 30, 44, 20, 20, 20]),
    P("Sales pace comes from Regal Pavilion's own Q1 FY27 (0.11 mn sft) and Q4 FY26 (0.42 mn sft) sales. Cost share and cost incurred are Brigade's ongoing-project ratios (₹14,874 cr estimated cost against ₹23,363 cr sale value; ₹5,900 cr incurred), used as a benchmark because Godrej does not publish project costs. The remaining assumptions are illustrative. Godrej does not disclose a completion date.", "small")]))
E.append(Spacer(1, 6))
E.append(KeepTogether([tbl([
    ["₹ crore", "Base", "Slow", "Fast"],
    ["Collections over 14 quarters"] + [n0(res[k]["collections"]) for k in (1, 2, 3)],
    ["Cost to complete"] + [n0(res[k]["to_complete"]) for k in (1, 2, 3)],
    ["Net operating cash flow"] + [n0(res[k]["net"]) for k in (1, 2, 3)],
    ["NPV at 12% a year"] + [n0(res[k]["npv"]) for k in (1, 2, 3)],
    ["Peak funding need"] + ["None" if res[k]["peak"] == 0 else n0(-res[k]["peak"]) for k in (1, 2, 3)],
    ["Collections / cost to complete"] + [f"{res[k]['coverage']:.2f}x" for k in (1, 2, 3)],
    ["Area unsold at quarter 14, mn sft"] + [f"{res[k]['unsold_end']:.2f}" for k in (1, 2, 3)],
], [84, 30, 30, 30])]))
E.append(Spacer(1, 6))
E.append(P(f"The project does not need outside funding in any of the three cases. Collections already owed on sold flats (₹{n0(ci['booked']-ci['collected'])} crore) are larger than the cost left to spend in the base case. In the slow case {res[2]['unsold_end']:.2f} mn sft is still unsold after 14 quarters. The model leaves out land cost, financing, GST, approvals and overheads, and it does not use Godrej's actual cost, so the coverage ratio is an upper bound on comfort, not a forecast.", "body"))

# ---- page 5 method
E += [PageBreak(), P("Method and sources", "h1"), P("Every input is a figure printed in a developer's own investor document.", "sub")]
E.append(P("<b>Documents.</b> Investor presentations, performance updates and press releases from Prestige Estates Projects (Q2 FY26 to Q1 FY27), Godrej Properties (Q2 FY26 to Q1 FY27, plus the FY26 integrated annual report) and Brigade Enterprises (Q2 FY26 to Q1 FY27). They were downloaded from each company's investor-relations site.", "body"))
E.append(P("<b>Extraction.</b> 103 figures were typed into one table with the source file and PDF page. A script confirms each figure sits on the stated page with its label and stops if not. Shares, price per sq ft and value per acre are calculated in the workbook from those inputs.", "body"))
E.append(P("<b>Checks.</b> Eight reconciliations tie in the workbook: Prestige's six city sales sum to its printed total (₹65,793 mn), Godrej's six city bookings sum to ₹8,651 crore, Hyderabad shares match the percentages the companies print, and the cash-flow rows conserve cash. The workbook was recalculated in LibreOffice and compared with an independent Python model for all three scenarios; they agree.", "body"))
E.append(P("<b>Where the numbers are soft.</b> Brigade's Hyderabad share is read from a chart and printed only as a percentage. Prestige's Q2 and Q3 FY26 shares are also printed only as percentages. Godrej's Hyderabad area for Q1 FY27 is printed to one decimal, so no per-sq-ft figure is drawn from it.", "body"))
E.append(P("<b>What is not here.</b> RERA registrations and listing prices for the whole city. Telangana RERA's project search requires a CAPTCHA, and this brief does not use scraped or estimated listings. It says what three developers disclose, and that is all it says.", "body"))
E.append(Spacer(1, 4))
E.append(KeepTogether([tbl([["Developer", "Documents reviewed"], ["Prestige Estates Projects", "Q2 FY26, Q3 FY26, Q4 FY26, Q1 FY27: presentation and performance update"],
    ["Godrej Properties", "Q2 FY26, Q3 FY26, Q4 FY26, Q1 FY27: results presentation and press release; FY26 integrated annual report"],
    ["Brigade Enterprises", "Q2 FY26, Q3 FY26, Q4 FY26, Q1 FY27: investor presentation"]], [55, 119])]))
doc.build(E); print("pdf built")

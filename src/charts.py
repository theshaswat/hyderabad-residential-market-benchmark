"""Charts for the brief. Reads the sourced facts and the model; never retypes a number."""
from pathlib import Path
import matplotlib.pyplot as plt
from chartstyle import apply, C, save
import model

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "charts"; OUT.mkdir(parents=True, exist_ok=True)
NAVY, AMBER, GREY, LGREY = "#0d253d", "#f7a501", "#8c8c8c", "#d0d0d0"
F = model.facts()
g = lambda d, p, m: F[(d, p, m)]
apply(grid="none")

def bar_labels(ax, bars, fmtf, pad=0.01, horizontal=True):
    for b in bars:
        v = b.get_width() if horizontal else b.get_height()
        if horizontal: ax.text(v + pad, b.get_y() + b.get_height() / 2, fmtf(v), va="center", fontsize=9, color=C["ink"])
        else: ax.text(b.get_x() + b.get_width() / 2, v + pad, fmtf(v), ha="center", fontsize=9, color=C["ink"])

# 1. share of sales
pre = lambda p: g("Prestige", p, "presales_Hyderabad") / g("Prestige", p, "presales_Total")
share_now = {"Prestige": pre("Q1 FY27"),
             "Brigade": g("Brigade", "Q1 FY27", "hyderabad_share_printed") / 100,
             "Godrej": g("Godrej", "Q1 FY27", "booking_Hyderabad") / g("Godrej", "Q1 FY27", "booking_Total")}
qs = ["Q2 FY26", "Q3 FY26", "Q4 FY26", "Q1 FY27"]
ps = [g("Prestige", "Q2 FY26", "hyderabad_share_printed") / 100, g("Prestige", "Q3 FY26", "hyderabad_share_printed") / 100, pre("Q4 FY26"), pre("Q1 FY27")]
fig, (a, b) = plt.subplots(1, 2, figsize=(10, 3.8), gridspec_kw={"width_ratios": [1, 1.15]})
names = list(share_now)
bars = a.barh(names[::-1], [share_now[n] for n in names][::-1], color=[LGREY, LGREY, NAVY], height=0.55)
bar_labels(a, bars, lambda v: f"{v:.1%}", pad=0.008); a.set_xlim(0, 0.62); a.set_xticks([]); a.spines["bottom"].set_visible(False)
a.set_title("Share of sales in Hyderabad, Q1 FY27", fontsize=12)
bars = b.bar(qs, ps, color=[LGREY, LGREY, LGREY, AMBER], width=0.55)
bar_labels(b, bars, lambda v: f"{v:.0%}" if v > 0.1 else f"{v:.1%}", pad=0.012, horizontal=False)
b.set_ylim(0, 0.6); b.set_yticks([]); b.spines["left"].set_visible(False)
b.set_title("Prestige, quarter by quarter", fontsize=12)
gg = g("Prestige", "Q1 FY27", "sales_Prestige Golden Grove") / g("Prestige", "Q1 FY27", "presales_Hyderabad")
b.annotate(f"Golden Grove, Tellapur:\n{gg:.0%} of Hyderabad sales", xy=(3, ps[3]), xytext=(-0.35, 0.43), fontsize=9, color=C["ink_mut"])
fig.tight_layout(); save(fig, str(OUT / "01_share_of_sales.png"))

# 2. price ladder
psf = lambda v, a: v * 10 / a
items = [("Godrej Regal Pavilion", psf(g("Godrej", "30 Jun 2026", "booking_value_ptd_Godrej Regal Pavilion"), g("Godrej", "30 Jun 2026", "sold_Godrej Regal Pavilion")), NAVY),
         ("Godrej Hyderabad launches, FY26", psf(g("Godrej", "FY26", "hyderabad_launch_value"), g("Godrej", "FY26", "hyderabad_launch_area")), NAVY),
         ("Godrej Madison Avenue (Kokapet)", psf(g("Godrej", "30 Jun 2026", "booking_value_ptd_Godrej Madison Avenue"), g("Godrej", "30 Jun 2026", "sold_Godrej Madison Avenue")), NAVY),
         ("Godrej Brooklyn Avenue (Kukatpally)", psf(g("Godrej", "Q1 FY27", "booking_Godrej Brooklyn Avenue"), g("Godrej", "Q1 FY27", "booking_area_Godrej Brooklyn Avenue")), NAVY),
         ("Prestige unsold Hyderabad stock", g("Prestige", "Q1 FY27", "stock_value_Hyderabad") / g("Prestige", "Q1 FY27", "stock_area_Hyderabad"), AMBER),
         ("Godrej, all cities, Q1 FY27", psf(g("Godrej", "Q1 FY27", "booking_Total"), g("Godrej", "Q1 FY27", "booking_area_Total")), LGREY),
         ("Brigade, all cities, Q1 FY27", g("Brigade", "Q1 FY27", "avg_realisation_total"), LGREY),
         ("Prestige apartments, all cities, Q1 FY27", g("Prestige", "Q1 FY27", "avg_realisation_apartments"), LGREY)]
items.sort(key=lambda x: (x[2] == LGREY, -x[1]))
fig, ax = plt.subplots(figsize=(10, 4.2))
bars = ax.barh([i[0] for i in items][::-1], [i[1] for i in items][::-1], color=[i[2] for i in items][::-1], height=0.62)
bar_labels(ax, bars, lambda v: f"{v:,.0f}", pad=150); ax.set_xlim(0, 16500); ax.set_xticks([]); ax.spines["bottom"].set_visible(False)
ax.set_title("Price per sq ft (INR): Hyderabad projects against company-wide averages")
fig.text(0.01, 0.01, "Navy: Godrej Hyderabad, sales value / area sold. Amber: Prestige unsold stock value / stock area (asking view). Grey: company-wide.", fontsize=8, color=C["ink_sub"])
fig.tight_layout(rect=(0, 0.04, 1, 1)); save(fig, str(OUT / "02_price_per_sqft.png"))

# 3. land adds
land = [("Tellapur", "Q1 FY26"), ("Raidurg", "Q2 FY26"), ("Rajendra Nagar", "Q3 FY26"), ("Kompally", "Q4 FY26"), ("Pulimamidi", "Q1 FY26"), ("Lakdaram", "Q3 FY26")]
rows = []
for nm, qq in land:
    key = "Tellapur (Prestige Golden Grove)" if nm == "Tellapur" else nm
    rows.append((nm, g("Prestige", qq, "land_gdv_" + key) / 10, g("Prestige", qq, "land_acres_" + key)))
rows.sort(key=lambda r: -r[1])
fig, ax = plt.subplots(figsize=(10, 3.6))
bars = ax.bar([r[0] for r in rows], [r[1] for r in rows], color=[NAVY] + [LGREY] * 5, width=0.55)
for b, r in zip(bars, rows):
    ax.text(b.get_x() + b.get_width() / 2, r[1] + 150, f"{r[1]:,.0f}\n{r[2]:.0f} acres", ha="center", fontsize=9)
ax.set_ylim(0, 11500); ax.set_yticks([]); ax.spines["left"].set_visible(False)
ax.set_title("Prestige: Hyderabad land added in FY26, tentative GDV (INR cr)")
fig.tight_layout(); save(fig, str(OUT / "03_land_adds.png"))

# 4. cash flow
ci = model.case_inputs(F); sc = model.scenarios(ci); res = {k: model.run(ci, s) for k, s in sc.items()}
fig, (a, b) = plt.subplots(1, 2, figsize=(10, 3.7), gridspec_kw={"width_ratios": [1.2, 1]})
r = res[1]["rows"]; x = [q["t"] for q in r]
a.bar([i - 0.2 for i in x], [q["col"] for q in r], width=0.4, color=NAVY, label="Collections")
a.bar([i + 0.2 for i in x], [-q["cost"] for q in r], width=0.4, color=AMBER, label="Construction outflow")
a.axhline(0, color=GREY, lw=0.8); a.set_xticks(x); a.set_xlabel("Quarters from 30 Jun 2026"); a.set_yticks([-200, 0, 200, 400])
a.set_title("Base case, INR cr per quarter"); a.legend(loc="upper left")
for k, col, lab in [(1, NAVY, "Base"), (2, GREY, "Slow"), (3, AMBER, "Fast")]:
    b.plot(x, [q["cum"] for q in res[k]["rows"]], color=col, label=lab)
b.set_xticks(x[::2]); b.set_xlabel("Quarters from 30 Jun 2026"); b.set_title("Cumulative net cash, INR cr"); b.legend(loc="upper left")
fig.tight_layout(); save(fig, str(OUT / "04_cash_flow.png"))
print("charts written")

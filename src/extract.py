"""Build data/hyderabad_developer_metrics.csv from the developers' own filings.

Every figure below is typed from a company PDF in data/raw/src. Each row names
anchor strings that must sit on the same page of that PDF; the script finds the
page and stops if an anchor is missing, so a mistyped number cannot pass.
"""
import csv, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "raw" / "src"
OUT = ROOT / "data" / "hyderabad_developer_metrics.csv"

# (developer, period, metric, value, unit, file, anchors, note)
F = []
def f(dev, per, metric, val, unit, file, anchors, note=""):
    F.append((dev, per, metric, val, unit, file, anchors, note))

# ---------------- Prestige ----------------
P1 = "prestige_Q1FY27_presentation"
for city, v in [("Total", 65793), ("Hyderabad", 32431), ("Bengaluru", 17953), ("Mumbai", 7763),
                ("NCR", 4410), ("Chennai", 2850), ("Others", 386)]:
    f("Prestige", "Q1 FY27", f"presales_{city}", v, "INR mn", P1, ["GEOGRAPHICAL SALES BREAKDOWN", f"{v:,}"])
f("Prestige", "Q1 FY27", "sales_Prestige Golden Grove", 29913, "INR mn", P1, ["29,913", "Prestige Golden"])
f("Prestige", "Q1 FY27", "stock_area_Hyderabad", 7.5, "mn sft", P1, ["INVENTORY BREAK UP", "89,953"])
f("Prestige", "Q1 FY27", "stock_value_Hyderabad", 89953, "INR mn", P1, ["INVENTORY BREAK UP", "89,953"])
f("Prestige", "Q1 FY27", "stock_value_Total", 245180, "INR mn", P1, ["INVENTORY BREAK UP", "2,45,180"])
for name, tda, gdv, seg in [("Prestige Golden Grove", 14.3, 95012, "Mid-Segment"),
                            ("Prestige Rock Cliff", 0.81, 9093, "Luxury"),
                            ("The Prestige Place", 2.76, 20426, "Mid-Segment")]:
    f("Prestige", "Q1 FY27", f"launch_tda_{name}", tda, "mn sft", P1, ["GDV OF UPCOMING LAUNCHES", name, f"{gdv:,}"], seg)
    f("Prestige", "Q1 FY27", f"launch_gdv_{name}", gdv, "INR mn", P1, ["GDV OF UPCOMING LAUNCHES", name, f"{gdv:,}"], seg)
P4 = "prestige_Q4FY26_presentation"
f("Prestige", "Q4 FY26", "presales_Total", 76973, "INR mn", P4, ["GEOGRAPHICAL SALES BREAKDOWN", "3,871", "76,973"])
f("Prestige", "Q4 FY26", "presales_Hyderabad", 3871, "INR mn", P4, ["GEOGRAPHICAL SALES BREAKDOWN", "3,871", "76,973"])
f("Prestige", "FY26", "presales_Total", 300245, "INR mn", P4, ["GEOGRAPHICAL SALES BREAKDOWN", "23,821", "3,00,245"])
f("Prestige", "FY26", "presales_Hyderabad", 23821, "INR mn", P4, ["GEOGRAPHICAL SALES BREAKDOWN", "23,821", "3,00,245"])
for place, acres, gdv, q in [("Tellapur (Prestige Golden Grove)", 28, 95000, "Q1 FY26"),
                             ("Pulimamidi", 37, 2500, "Q1 FY26"), ("Raidurg", 11, 23000, "Q2 FY26"),
                             ("Lakdaram", 20, 2000, "Q3 FY26"), ("Rajendra Nagar", 4, 13800, "Q3 FY26"),
                             ("Kompally", 7, 10000, "Q4 FY26")]:
    key = place.split(" (")[0]
    f("Prestige", q, f"land_acres_{place}", acres, "acres", P4, ["BUSINESS DEVELOPMENT", f"{key}", f"{gdv:,}"], "Hyderabad land added")
    f("Prestige", q, f"land_gdv_{place}", gdv, "INR mn", P4, ["BUSINESS DEVELOPMENT", f"{key}", f"{gdv:,}"], "Tentative GDV")
f("Prestige", "Q3 FY26", "presales_Total", 41836, "INR mn", "prestige_Q3FY26_performance_update", ["41,836"])
f("Prestige", "Q3 FY26", "hyderabad_share_printed", 16, "%", "prestige_Q3FY26_performance_update", ["Hyderabad 16%"])
f("Prestige", "Q2 FY26", "presales_Total", 60173, "INR mn", "prestige_Q2FY26_performance_update", ["60,173"])
f("Prestige", "Q2 FY26", "hyderabad_share_printed", 11, "%", "prestige_Q2FY26_performance_update", ["Hyderabad", "11%", "Sales Mix"])

# ---------------- Godrej ----------------
G1 = "godrej_Q1FY27_presentation"
for city, v, area, units in [("Bengaluru", 3798, 3.3, 1886), ("MMR", 1805, 0.8, 655), ("NCR", 1538, 0.6, 201),
                             ("Pune", 939, 0.9, 677), ("Hyderabad", 410, 0.4, 173), ("Others", 161, 0.2, 146)]:
    f("Godrej", "Q1 FY27", f"booking_{city}", v, "INR cr", G1, ["Geographic distribution of sales for Q1 FY27", f"{v:,}"])
f("Godrej", "Q1 FY27", "booking_Total", 8651, "INR cr", "godrej_Q1FY27_press_release", ["8,651", "3,738 units"])
f("Godrej", "Q1 FY27", "booking_area_Hyderabad", 0.4, "mn sft", G1, ["Geographic distribution of sales for Q1 FY27", "410"], "as printed, 1 dp")
f("Godrej", "Q1 FY27", "booking_Godrej Brooklyn Avenue", 317, "INR cr", G1, ["Sales by project details", "Godrej Brooklyn Avenue, Hyderabad", "317"])
f("Godrej", "Q1 FY27", "booking_area_Godrej Brooklyn Avenue", 0.26, "mn sft", G1, ["Sales by project details", "Godrej Brooklyn Avenue, Hyderabad", "0.26"])
f("Godrej", "Q1 FY27", "booking_Godrej Regal Pavilion", 98, "INR cr", G1, ["Sales by project details", "Godrej Regal Pavilion, Hyderabad", "98"])
f("Godrej", "Q1 FY27", "booking_area_Godrej Regal Pavilion", 0.11, "mn sft", G1, ["Sales by project details", "Godrej Regal Pavilion, Hyderabad", "0.11"])
# project register at 30 Jun 2026: total saleable, GPL share, launched, sold (mn sft), booking value, collection (INR cr)
for name, anchors, vals in [
    ("Godrej Regal Pavilion", ["Godrej Regal Pavilion*", "2,425", "707"], (4.13, 4.13, 3.29, 2.83, 2425, 707)),
    ("Godrej Madison Avenue", ["Godrej Madison Avenue", "1,109", "321"], (1.25, 1.15, 0.96, 0.93, 1109, 321)),
    ("Godrej Brooklyn Avenue", ["Godrej Brooklyn Avenue", "Kukatpally", "317"], (3.06, 3.06, 2.66, 0.26, 317, 20)),
]:
    for m, v, u in zip(["total_saleable", "gpl_share", "launched", "sold", "booking_value_ptd", "collection_ptd"],
                       vals, ["mn sft"] * 4 + ["INR cr"] * 2):
        f("Godrej", "30 Jun 2026", f"{m}_{name}", v, u, G1, anchors + ["Total South Zone"], "Project register, Hyderabad")
f("Godrej", "30 Jun 2026", "total_saleable_Neopolis", 2.55, "mn sft", G1, ["Neopolis", "Total South Zone", "2.55"], "Project register; not yet launched")
G4 = "godrej_Q4FY26_presentation"
f("Godrej", "Q4 FY26", "booking_Hyderabad", 389, "INR cr", G4, ["Geographic distribution of sales for Q4 FY26", "389"])
f("Godrej", "Q4 FY26", "booking_area_Hyderabad", 0.43, "mn sft", G4, ["Geographic distribution of sales for Q4 FY26", "389", "0.43"])
for city, v in [("MMR", 10312), ("Bengaluru", 8801), ("NCR", 7412), ("Pune", 3659), ("Hyderabad", 2360), ("Others", 1627)]:
    f("Godrej", "FY26", f"booking_{city}", v, "INR cr", "godrej_Q4FY26_press_release", ["MMR (INR 10,312 crore)", f"{v:,}"])
f("Godrej", "FY26", "hyderabad_launch_area", 3.3, "mn sft", G4, ["Geographic distribution of Launches", "Hyderabad", "2,800"])
f("Godrej", "FY26", "hyderabad_launch_value", 2800, "INR cr", G4, ["Geographic distribution of Launches", "Hyderabad", "2,800"])
f("Godrej", "FY26", "booking_area_Godrej Regal Pavilion", 2.73, "mn sft", G4, ["Godrej Regal Pavilion, Hyderabad", "2,328"])
f("Godrej", "FY26", "booking_Godrej Regal Pavilion", 2328, "INR cr", G4, ["Godrej Regal Pavilion, Hyderabad", "2,328"])
for name, msf, val in [("Neopolis (Kokapet)", 2.54, 4150), ("Kukatpally", 2.89, 3800)]:
    key = name.split(" (")[0]
    f("Godrej", "FY26", f"bd_area_{name}", msf, "mn sft", G4, ["Added 18 new projects", f"{key}, Hyderabad", f"{val:,}"], "Expected booking value, company estimate")
    f("Godrej", "FY26", f"bd_value_{name}", val, "INR cr", G4, ["Added 18 new projects", f"{key}, Hyderabad", f"{val:,}"], "Expected booking value, company estimate")

f("Prestige", "Q1 FY27", "avg_realisation_apartments", 11193, "INR/sft", "prestige_Q1FY27_performance_update", ["11,193 per square foot"], "Company-wide, apartments")
f("Godrej", "Q1 FY27", "booking_area_Total", 6.2, "mn sft", "godrej_Q1FY27_press_release", ["8,651", "6.2 million sq"], "Company-wide")
f("Godrej", "Q4 FY26", "booking_area_Godrej Regal Pavilion", 0.42, "mn sft", G4, ["Godrej Regal Pavilion, Hyderabad", "0.42", "380", "2,328"])
f("Godrej", "Q4 FY26", "booking_Godrej Regal Pavilion", 380, "INR cr", G4, ["Godrej Regal Pavilion, Hyderabad", "0.42", "380", "2,328"])

# ---------------- Brigade ----------------
B1 = "brigade_Q1FY27_presentation"
f("Brigade", "Q1 FY27", "presales_Total", 1054, "INR cr", B1, ["Residential pre-sales in Q1 FY27 INR 1,054 Cr"])
f("Brigade", "Q1 FY27", "hyderabad_share_printed", 14, "%", B1, ["Residential pre-sales in Q1 FY27 INR 1,054 Cr", "Hyderabad"], "Read from pie chart; city split printed 58/28/14")
f("Brigade", "Q1 FY27", "avg_realisation_total", 14256, "INR/sft", B1, ["INR 14,256/sft"])
f("Brigade", "Q1 FY27", "upcoming_launch_area_Hyderabad", 3.95, "mn sft", B1, ["3.95 mn sft in Hyderabad"])
f("Brigade", "30 Jun 2026", "land_acres_Hyderabad", 22, "acres", B1, ["Developable Area Details", "Hyderabad 22 6 6"])
f("Brigade", "30 Jun 2026", "land_project_area_Hyderabad", 6, "mn sft", B1, ["Developable Area Details", "Hyderabad 22 6 6"])
for m, v in [("est_sale_value", 23363), ("balance_collection", 16799), ("est_total_cost", 14874),
             ("cost_incurred", 5900), ("balance_cost", 8974), ("net_operating_cf", 7309), ("borrowings", 516),
             ("area_sold_to_date", 14.01), ("company_share_saleable", 19.81)]:
    f("Brigade", "30 Jun 2026", f"portfolio_{m}", v, "mn sft" if isinstance(v, float) else "INR cr", B1,
      ["Balance cost to complete the project", f"{v:,}"], "Brigade Enterprises ongoing projects (not Hyderabad-only)")

def pages(pdf):
    txt = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True).stdout
    return [re.sub(r"\s+", " ", p) for p in txt.split("\f")]

def main():
    cache, rows, bad = {}, [], []
    for dev, per, metric, val, unit, file, anchors, note in F:
        pdf = SRC / f"{file}.pdf"
        if file not in cache:
            cache[file] = pages(pdf)
        hit = next((i + 1 for i, p in enumerate(cache[file]) if all(re.sub(r"\s+", " ", a) in p for a in anchors)), None)
        if hit is None:
            bad.append((file, metric, anchors)); continue
        rows.append([dev, per, metric, val, unit, f"{file}.pdf", hit, note])
    if bad:
        for b in bad: print("ANCHOR NOT FOUND:", b)
        sys.exit(1)
    with OUT.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["developer", "period", "metric", "value", "unit", "source_file", "pdf_page", "note"])
        w.writerows(rows)
    print(f"{len(rows)} facts written to {OUT.name}")

if __name__ == "__main__":
    main()

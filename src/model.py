"""Python twin of the CashFlow sheet. The workbook is the deliverable; this file exists
so the workbook can be recalculated and checked against an independent implementation."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HORIZON = 14  # quarters modelled

def facts():
    with (ROOT / "data" / "hyderabad_developer_metrics.csv").open() as fh:
        return {(r["developer"], r["period"], r["metric"]): float(r["value"]) for r in csv.DictReader(fh)}

def get(F, dev, per, metric):
    return F[(dev, per, metric)]

def case_inputs(F):
    """Disclosed inputs for Godrej Regal Pavilion (30 Jun 2026) and the Brigade cost benchmarks."""
    g = lambda m: get(F, "Godrej", "30 Jun 2026", m + "_Godrej Regal Pavilion")
    b = lambda m: get(F, "Brigade", "30 Jun 2026", "portfolio_" + m)
    total, sold = g("total_saleable"), g("sold")
    booked, coll = g("booking_value_ptd"), g("collection_ptd")
    return dict(total=total, sold=sold, booked=booked, collected=coll,
                psf=booked * 10 / sold,
                cost_ratio=b("est_total_cost") / b("est_sale_value"),
                progress=b("cost_incurred") / b("est_total_cost"),
                v_base=get(F, "Godrej", "Q1 FY27", "booking_area_Godrej Regal Pavilion"),
                v_fast=get(F, "Godrej", "Q4 FY26", "booking_area_Godrej Regal Pavilion"))

def scenarios(ci):
    # velocity, price change on unsold stock, cost ratio, quarters to completion
    return {1: dict(name="Base", vel=ci["v_base"], price=0.0, cost=ci["cost_ratio"], T=10),
            2: dict(name="Slow", vel=ci["v_base"] / 2, price=-0.05, cost=ci["cost_ratio"] + 0.05, T=12),
            3: dict(name="Fast", vel=ci["v_fast"], price=0.05, cost=ci["cost_ratio"] - 0.03, T=8)}

def run(ci, sc, disc=0.12):
    unsold = ci["total"] - ci["sold"]
    price = ci["psf"] * (1 + sc["price"])
    est_total = ci["booked"] + unsold * price / 10
    cost_total = sc["cost"] * est_total
    to_complete = cost_total * (1 - ci["progress"])
    open_bal = ci["booked"] - ci["collected"]
    sold_cum, cum, rows = 0.0, 0.0, []
    for t in range(1, HORIZON + 1):
        a = min(sc["vel"], unsold - sold_cum); sold_cum += a
        book = a * price / 10
        bal = open_bal + book
        col = bal / (sc["T"] - t + 1) if t < sc["T"] else bal
        cost = to_complete / sc["T"] if t <= sc["T"] else 0.0
        net = col - cost; cum += net; open_bal = bal - col
        rows.append(dict(t=t, area=a, book=book, col=col, cost=cost, net=net, cum=cum))
    npv = sum(r["net"] / (1 + disc) ** (r["t"] / 4) for r in rows)
    return dict(rows=rows, est_total=est_total, cost_total=cost_total, to_complete=to_complete,
                collections=sum(r["col"] for r in rows), net=sum(r["net"] for r in rows),
                peak=min(0.0, min(r["cum"] for r in rows)), npv=npv, unsold_end=unsold - sold_cum,
                coverage=sum(r["col"] for r in rows) / to_complete)

if __name__ == "__main__":
    F = facts(); ci = case_inputs(F)
    print({k: round(v, 4) for k, v in ci.items()})
    for k, sc in scenarios(ci).items():
        r = run(ci, sc)
        print(sc["name"], {x: round(r[x], 1) for x in ("est_total", "to_complete", "collections", "net", "peak", "npv", "unsold_end")}, round(r["coverage"], 3))

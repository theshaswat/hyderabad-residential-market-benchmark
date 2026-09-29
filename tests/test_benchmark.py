"""Run: python3 tests/test_benchmark.py"""
import csv, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import model

F = model.facts()
g = lambda d, p, m: F[(d, p, m)]

def test_table():
    rows = list(csv.DictReader((ROOT / "data" / "hyderabad_developer_metrics.csv").open()))
    assert len(rows) == 103, len(rows)
    assert all(int(r["pdf_page"]) > 0 for r in rows)

def test_city_sums():
    cities = ["Hyderabad", "Bengaluru", "Mumbai", "NCR", "Chennai", "Others"]
    assert sum(g("Prestige", "Q1 FY27", "presales_" + c) for c in cities) == g("Prestige", "Q1 FY27", "presales_Total")
    gc = ["Hyderabad", "Bengaluru", "MMR", "NCR", "Pune", "Others"]
    assert sum(g("Godrej", "Q1 FY27", "booking_" + c) for c in gc) == g("Godrej", "Q1 FY27", "booking_Total")

def test_shares_match_printed():
    assert round(g("Prestige", "Q1 FY27", "presales_Hyderabad") / g("Prestige", "Q1 FY27", "presales_Total") * 100) == 49
    assert round(g("Godrej", "Q1 FY27", "booking_Hyderabad") / g("Godrej", "Q1 FY27", "booking_Total") * 100) == 5

def test_cash_conserved():
    ci = model.case_inputs(F)
    for sc in model.scenarios(ci).values():
        r = model.run(ci, sc)
        booked = sum(x["book"] for x in r["rows"])
        # every scenario completes inside the horizon, so all booked value is collected
        assert abs(r["collections"] - (ci["booked"] - ci["collected"] + booked)) < 1e-6
        assert r["peak"] <= 0

def test_workbook_matches_model():
    if not shutil.which("soffice"):
        print("skip: soffice not installed"); return
    from openpyxl import load_workbook
    ci = model.case_inputs(F); scs = model.scenarios(ci)
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        for k in (1, 2, 3):
            wb = load_workbook(ROOT / "output" / "Hyderabad_Residential_Benchmark.xlsx")
            wb["CashFlow"]["B13"] = k; wb.save(d / f"s{k}.xlsx")
        subprocess.run(["soffice", "--headless", "--convert-to", "xlsx", "--outdir", str(d / "out")] + [str(d / f"s{k}.xlsx") for k in (1, 2, 3)],
                       capture_output=True, check=True)
        for k in (1, 2, 3):
            ws = load_workbook(d / "out" / f"s{k}.xlsx", data_only=True)["CashFlow"]
            r = model.run(ci, scs[k])
            for cell, key in [("B41", "collections"), ("B42", "to_complete"), ("B43", "net"), ("B44", "npv"), ("B46", "coverage")]:
                assert abs(ws[cell].value - r[key]) < 1e-6, (k, cell, ws[cell].value, r[key])
        wb = load_workbook(d / "out" / "s1.xlsx", data_only=True)
        bad = [(w.title, c.coordinate) for w in wb.worksheets for row in w.iter_rows() for c in row if isinstance(c.value, str) and c.value.startswith("#")]
        assert not bad, bad
        assert all(r[5].value is True for r in wb["Checks"].iter_rows(min_row=5, max_row=12)), "a reconciliation check failed"

if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn(); print("ok", name)

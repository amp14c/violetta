"""Step 2 — Parse the PATH *Monthly* Ridership Report PDFs into a tidy table.

Each monthly report has one page per month plus a "Year To Date" page. A page holds
two tables, one row per station:

  Table A: monthly total | avg weekday | avg Saturday | avg Sunday | avg holiday
  Table B: avg daily     | weekday total | Saturday total | Sunday total | holiday total

and a row with the number of weekdays / Saturdays / Sundays / holidays in the month.

Output: data/processed/path_monthly_by_station.csv  (one row per month x station)
        data/processed/path_monthly_system.csv      (one row per month, system total;
                                                      2012 filled from NY Open Data)
Validation (fails loudly): station rows must sum to the NY / NJ subtotals and to the
MONTHLY TOTAL; weekday+Sat+Sun+holiday totals must equal the monthly total.
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
PDF_DIR = ROOT / "data" / "raw" / "pdf"
OUT = ROOT / "data" / "processed"

MONTHS = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July", "August",
     "September", "October", "November", "December"], start=1)}

# Canonical station names (the reports renamed "Pavonia/ Newport" to "Newport").
STATIONS = {
    "Christopher Street": ("Christopher Street", "NY"),
    "9th Street": ("9th Street", "NY"),
    "14th Street": ("14th Street", "NY"),
    "23rd Street": ("23rd Street", "NY"),
    "33rd Street": ("33rd Street", "NY"),
    "WTC": ("World Trade Center", "NY"),
    "World Trade Center": ("World Trade Center", "NY"),
    "Newark": ("Newark", "NJ"),
    "Harrison": ("Harrison", "NJ"),
    "Journal Square": ("Journal Square", "NJ"),
    "Grove Street": ("Grove Street", "NJ"),
    "Exchange Place": ("Exchange Place", "NJ"),
    "Pavonia/ Newport": ("Newport", "NJ"),
    "Pavonia/Newport": ("Newport", "NJ"),
    "Newport": ("Newport", "NJ"),
    "Hoboken": ("Hoboken", "NJ"),
    "UPTOWN SUBTOTAL": ("UPTOWN SUBTOTAL", None),
    "NEW YORK SUBTOTAL": ("NEW YORK SUBTOTAL", None),
    "NEW JERSEY SUBTOTAL": ("NEW JERSEY SUBTOTAL", None),
    "MONTHLY TOTAL": ("SYSTEM TOTAL", None),
}

ROW = re.compile(r"^(?P<name>[A-Za-z0-9/ .]+?)\s+(?P<nums>(?:-?[\d,]+\s*){5})$")
NUM = re.compile(r"-?[\d,]+")
DAYS = re.compile(r"(?:^|Totals\s+)(\d{1,2})\s+(\d{1,2})\s+(\d{1,2})\s+(\d{1,2})\s*$")

A_COLS = ["total", "avg_weekday", "avg_saturday", "avg_sunday", "avg_holiday"]
B_COLS = ["avg_daily", "weekday_total", "saturday_total", "sunday_total", "holiday_total"]


def to_int(s: str) -> int:
    return int(s.replace(",", ""))


def parse_page(text: str, year: int):
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    period = lines[1]
    m = re.match(r"(\w+)\s+(\d{4})$", period)
    if not m or m.group(1) not in MONTHS:
        return None  # Year-to-date page: skipped, we recompute annual totals ourselves
    month = MONTHS[m.group(1)]
    assert int(m.group(2)) == year, (period, year)

    days = None
    seen: dict[str, int] = {}
    rows: dict[str, dict] = {}
    for ln in lines[2:]:
        if days is None and (d := DAYS.search(ln)):
            days = dict(zip(["n_weekdays", "n_saturdays", "n_sundays", "n_holidays"],
                            map(int, d.groups())))
            continue
        r = ROW.match(ln)
        if not r:
            continue
        raw_name = r.group("name").strip()
        if raw_name not in STATIONS:
            continue
        name, state = STATIONS[raw_name]
        nums = [to_int(x) for x in NUM.findall(r.group("nums"))]
        k = seen.get(name, 0)
        seen[name] = k + 1
        rec = rows.setdefault(name, {"station": name, "state": state})
        rec.update(dict(zip(A_COLS if k == 0 else B_COLS, nums)))
    assert days, f"no day counts on {period}"
    out = []
    for rec in rows.values():
        rec |= {"year": year, "month": month, **days}
        out.append(rec)
    return out


def validate(df: pd.DataFrame) -> None:
    stations = df[df.state.notna()]
    for (y, m), g in df.groupby(["year", "month"]):
        st = stations[(stations.year == y) & (stations.month == m)]
        tot = g.set_index("station")
        assert len(st) == 13, (y, m, len(st))
        assert st.total.sum() == tot.loc["SYSTEM TOTAL", "total"], (y, m)
        assert st[st.state == "NY"].total.sum() == tot.loc["NEW YORK SUBTOTAL", "total"], (y, m)
        assert st[st.state == "NJ"].total.sum() == tot.loc["NEW JERSEY SUBTOTAL", "total"], (y, m)
    parts = df[["weekday_total", "saturday_total", "sunday_total", "holiday_total"]].sum(axis=1)
    bad = df[(parts - df.total).abs() > 2]  # allow rounding of 1-2 riders
    assert bad.empty, bad[["year", "month", "station", "total"]]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    for pdf in sorted(PDF_DIR.glob("monthly_*.pdf")):
        year = int(pdf.stem.split("_")[1])
        with pdfplumber.open(pdf) as doc:
            for page in doc.pages:
                if (recs := parse_page(page.extract_text() or "", year)):
                    records += recs
        print(f"parsed {pdf.name}")

    df = pd.DataFrame(records)
    df.insert(0, "date", pd.to_datetime(dict(year=df.year, month=df.month, day=1)))
    validate(df)
    print("validation passed: station rows sum to subtotals/totals for every month")

    by_station = df[df.state.notna()].sort_values(["date", "state", "station"])
    by_station.to_csv(OUT / "path_monthly_by_station.csv", index=False)

    system = df[df.station == "SYSTEM TOTAL"].drop(columns=["station", "state"]).copy()
    system = system.sort_values("date")
    system.to_csv(OUT / "path_monthly_system.csv", index=False)

    # Independent cross-checks against two machine-readable system-total sources.
    raw = ROOT / "data" / "raw"
    nyod = pd.read_csv(raw / "ny_open_data_path_monthly.csv")
    nyod.columns = ["year", "month", "nyod_thousands"]
    ntd = pd.read_csv(raw / "ntd_path_monthly.csv", parse_dates=["date"])
    ntd = ntd[ntd["mode"] == "HR"][["date", "upt"]]  # HR = heavy rail (PATH trains)
    chk = (system[["date", "year", "month", "total"]]
           .merge(nyod, on=["year", "month"], how="left")
           .merge(ntd, on="date", how="left"))
    chk["diff_nyod_pct"] = (chk.total / (chk.nyod_thousands * 1000) - 1) * 100
    chk["diff_ntd_pct"] = (chk.total / chk.upt - 1) * 100
    chk.to_csv(OUT / "crosscheck_system_totals.csv", index=False)
    for col, name in [("diff_nyod_pct", "NY Open Data"), ("diff_ntd_pct", "NTD")]:
        s = chk[col].dropna().abs()
        print(f"cross-check vs {name}: {len(s)} months, median |diff| {s.median():.2f}%, "
              f"max {s.max():.2f}%")
    print(f"wrote {len(by_station):,} station-month rows, {len(system)} system months "
          f"({system.date.min():%Y-%m} to {system.date.max():%Y-%m})")


if __name__ == "__main__":
    main()

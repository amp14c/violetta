"""Step 3 — Parse the PATH *Hourly* Ridership Report PDFs into a tidy table.

Each hourly report (2017 onward) has a year-to-date section and one section per month.
Each section has 14 pages: 13 stations + "System-wide". A page is a 24-hour table of
average entries and exits:

  Hour | Avg Weekday Entry | Avg Saturday Entry | Avg Sunday Entry |
         Avg Weekday Exit  | Avg Saturday Exit  | Avg Sunday Exit  |
         Avg Holiday Entries | Avg Holiday Exits

The 2014 report is a one-off snapshot of July 2014 only, same column order.

Output: data/processed/path_hourly.csv in long format
        (period, year, month, station, hour, day_type, direction, avg_count)
Validation: the hour rows of each column must add up to the page's "Total" row.
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
COLS = [("weekday", "entry"), ("saturday", "entry"), ("sunday", "entry"),
        ("weekday", "exit"), ("saturday", "exit"), ("sunday", "exit"),
        ("holiday", "entry"), ("holiday", "exit")]
STATION_FIX = {
    "Christopher St.": "Christopher Street", "Christopher St": "Christopher Street",
    "WTC": "World Trade Center", "Pavonia/Newport": "Newport", "Pavonia/ Newport": "Newport",
    "Newport/Pavonia": "Newport", "System-wide": "System-wide", "Systemwide": "System-wide",
}
HOUR = re.compile(r"^(\d{1,2}):00:00 ([AP]M)\s+(.*)$")
NUM = re.compile(r"-?[\d,]+")


def norm(s: str) -> str:
    # The PDFs mix ASCII and Unicode hyphens/dashes.
    return s.replace("‐", "-").replace("‑", "-").replace("–", "-").strip()


def hour24(h: str, ap: str) -> int:
    h = int(h) % 12
    return h + 12 if ap == "PM" else h


def parse_page(text: str, year: int, issues: list):
    lines = [norm(ln) for ln in text.split("\n") if ln.strip()]
    based = next((ln for ln in lines[:4] if ln.startswith("(Based on")), None)
    if based is None:
        return []  # contents / section divider page
    # Section labels seen: "January 2021", "Jun 2025", "2026-Jan" (monthly) and
    # "YTD 2019", "2025 Annual", "2026 YTD" (whole-year / year-to-date).
    m = (re.search(r"Based on ([A-Za-z]+) \d{4}", based)
         or re.search(r"Based on \d{4}-([A-Za-z]+)", based))
    abbr = {k[:3]: v for k, v in MONTHS.items()}
    if m and m.group(1)[:3] in abbr:
        period, month = "month", abbr[m.group(1)[:3]]
    else:
        period, month = "annual", None
    hdr = next((i for i, ln in enumerate(lines)
                if ln.startswith(("Avg Weekday", "Sum of Avg", "Total Sum of", "Hour"))), None)
    if hdr is None:
        issues.append((year, period, month, "?", "no table header"))
        return []
    prev = lines[hdr - 1]
    # The 2014 system-wide page has no station label above its (different) header.
    station = "System-wide" if prev.startswith(("(", "Weekend")) else STATION_FIX.get(prev, prev)

    # In months with no holiday (e.g. Mar/Apr/Aug 2026) the two holiday cells are
    # blank, so a row has 6 values: they are the six non-holiday columns.
    rows, total = [], None
    for ln in lines[hdr:]:
        if (h := HOUR.match(ln)):
            nums = [int(x.replace(",", "")) for x in NUM.findall(h.group(3))]
            if len(nums) not in (6, 8):
                issues.append((year, period, month, station, ln))
                continue
            rows.append((hour24(h.group(1), h.group(2)), nums))
        elif ln.startswith("Total "):
            total = [int(x.replace(",", "")) for x in NUM.findall(ln)]
    if len(rows) != 24:
        issues.append((year, period, month, station, f"only {len(rows)} hour rows"))
    elif total:
        n = min(len(total), *(len(r[1]) for r in rows))
        sums = [sum(r[1][i] for r in rows) for i in range(n)]
        off = max(abs(a - b) for a, b in zip(sums, total))
        if off > 30:  # each cell is rounded, so allow small drift
            issues.append((year, period, month, station, f"total mismatch {off}"))

    out = []
    for hour, nums in rows:
        for (day_type, direction), v in zip(COLS, nums):
            out.append(dict(year=year, period=period, month=month, station=station,
                            hour=hour, day_type=day_type, direction=direction, avg_count=v))
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    recs, issues = [], []
    for pdf in sorted(PDF_DIR.glob("hourly_*.pdf")):
        year = int(pdf.stem.split("_")[1])
        with pdfplumber.open(pdf) as doc:
            for page in doc.pages:
                recs += parse_page(page.extract_text() or "", year, issues)
        print(f"parsed {pdf.name}")
    df = pd.DataFrame(recs)
    df["month"] = df.month.astype("Int64")
    df.to_csv(OUT / "path_hourly.csv", index=False)

    pages = df.groupby(["year", "period", "month", "station"], dropna=False).ngroups
    print(f"wrote {len(df):,} rows from {pages} station-pages")
    print(f"{len(issues)} rows/pages flagged (see data/processed/hourly_parse_issues.csv)")
    pd.DataFrame(issues, columns=["year", "period", "month", "station", "detail"]).to_csv(
        OUT / "hourly_parse_issues.csv", index=False)


if __name__ == "__main__":
    main()

"""Step 1 — Download the raw PATH ridership reports.

Sources
-------
* PANYNJ PATH statistics page: https://www.panynj.gov/path/en/about/stats.html
  The PDFs live under https://www.panynj.gov/content/dam/path/about/statistics/
  (file names are not fully consistent year to year, so they are listed explicitly).
* NY Open Data, "Port Authority Trans-Hudson (PATH) Monthly Ridership: Beginning 1996"
  (dataset id v5t9-im68) — system totals only, last updated 2016. Cross-check only.
* FTA National Transit Database (NTD), "Complete Monthly Ridership (with Adjustments and
  Estimates)" (data.transportation.gov 8bui-9xvu), PATH = NTD ID 20098. System totals
  only (unlinked passenger trips). Cross-check only.

Output: data/raw/pdf/{monthly,hourly}_{year}.pdf, data/raw/ny_open_data_path_monthly.csv,
        data/raw/ntd_path_monthly.csv
Re-run any time; existing files are skipped unless --force is passed.
"""
from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PDF_DIR = RAW / "pdf"
BASE = "https://www.panynj.gov/content/dam/path/about/statistics"
UA = {"User-Agent": "Mozilla/5.0 (portfolio data pipeline)"}

# Official file names, as published (checked Nov 2026).
MONTHLY = {y: f"{y}-PATH-Monthly-Ridership-Report" for y in [2013, 2014, *range(2017, 2027)]}
MONTHLY |= {2012: "2012_PATH_Ridership_Report",
            2015: "2015-PATH-Ridership-Report", 2016: "2016-PATH-Ridership-Report"}
HOURLY = {y: f"{y}-PATH-hourly-Ridership-Report" for y in [2014, *range(2017, 2023)]}
HOURLY |= {y: f"{y}-PATH-Hourly-Ridership-Report" for y in range(2023, 2027)}
HOURLY |= {2016: "2016-PATH-hourly-ridership_november"}  # one-month snapshot

NY_OPEN_DATA = "https://data.ny.gov/api/views/v5t9-im68/rows.csv?accessType=DOWNLOAD"
# FTA National Transit Database, "Complete Monthly Ridership" (data.transportation.gov
# dataset 8bui-9xvu), filtered to PATH (NTD ID 20098). Machine-readable, system total only.
NTD = ("https://data.transportation.gov/resource/8bui-9xvu.csv?"
       "$select=date,mode,tos,upt,vrm,vrh,voms&$where=ntd_id=%2720098%27"
       "&$order=date&$limit=50000")


def fetch(url: str, dest: Path, force: bool) -> None:
    if dest.exists() and not force:
        print(f"skip  {dest.name}")
        return
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read()
    if dest.suffix == ".pdf" and not data.startswith(b"%PDF"):
        raise RuntimeError(f"{url} did not return a PDF")
    dest.write_bytes(data)
    print(f"saved {dest.name} ({len(data):,} bytes)")


def main() -> None:
    force = "--force" in sys.argv
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    for year, name in sorted(MONTHLY.items()):
        fetch(f"{BASE}/{name}.pdf", PDF_DIR / f"monthly_{year}.pdf", force)
    for year, name in sorted(HOURLY.items()):
        fetch(f"{BASE}/{name}.pdf", PDF_DIR / f"hourly_{year}.pdf", force)
    fetch(NY_OPEN_DATA, RAW / "ny_open_data_path_monthly.csv", force)
    fetch(NTD, RAW / "ntd_path_monthly.csv", force=True)  # small; always refresh


if __name__ == "__main__":
    main()

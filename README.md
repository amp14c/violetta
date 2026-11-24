# Data Projects Portfolio

A [Quarto](https://quarto.org) website of data projects. Each project has an interactive [Plotly](https://plotly.com/python/) dashboard, a slide deck, and a methodology page.

**Live site:** _add your GitHub Pages URL here after publishing_

## Projects

### PATH ridership, 2012–present
The Port Authority publishes PATH train ridership only as PDF reports. This project:

1. downloads every available monthly and hourly report (`scripts/01_download.py`)
2. extracts and validates the tables (`scripts/02_parse_monthly.py`, `scripts/03_parse_hourly.py`)
3. presents it as a dashboard (`path/dashboard.qmd`), slides (`path/slides.qmd`) and a methodology page (`path/methodology.qmd`); all charts live in `pathviz.py`

Clean datasets are in `data/processed/`. Feel free to reuse them, with credit to the
Port Authority of NY & NJ as the original source:

| File | Grain | Coverage |
|---|---|---|
| `path_monthly_by_station.csv` | station × month | Jan 2012 – latest |
| `path_monthly_system.csv` | month (system total) | Jan 2012 – latest |
| `path_hourly.csv` | station × hour × day type × entry/exit, per month and per year | Jul 2014; Nov 2016; Jan 2017 – latest |
| `crosscheck_system_totals.csv` | month | PDF totals vs NY Open Data and the National Transit Database |

Full sources, definitions, validation checks and limitations are on the
**Methodology & data** page (`path/methodology.qmd`).

## Run it locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/01_download.py
python scripts/02_parse_monthly.py
python scripts/03_parse_hourly.py
QUARTO_PYTHON=.venv/bin/python quarto render   # site is written to _site/
```

> **Note:** Quarto caches executed pages in `_freeze/` and only re-runs a page when that
> page changes. If you edit `pathviz.py` (the shared chart code), delete `_freeze/` before
> `quarto render` so every page picks up the change.

## Updating with new months
PANYNJ updates the current-year PDFs each month. Re-run the three scripts with
`python scripts/01_download.py --force` to fetch the latest versions, then `quarto render`.

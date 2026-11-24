# violetta: AP's projects

This repository holds two independent projects:

| Project | Where | Deployed to |
|---|---|---|
| **Next.js app** | `app/`, `components/`, `lib/`, `public/`, `package.json` | [Vercel](https://violetta-mu.vercel.app) |
| **Data portfolio** (Quarto website) | `index.qmd`, `path/`, `scripts/`, `data/`, `pathviz.py`, `_quarto.yml` | [GitHub Pages](https://amp14c.github.io/violetta/) |

They don't share code. Vercel builds only the Next.js app, and the
`.github/workflows/publish.yml` workflow builds only the Quarto site.

---

## Data portfolio

A [Quarto](https://quarto.org) website of data projects. Each project has an interactive [Plotly](https://plotly.com/python/) dashboard, a slide deck, and a methodology page.

**Live site:** https://amp14c.github.io/violetta/

### Projects

#### PATH ridership, 2012–present
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

### Run it locally

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

### Updating with new months
PANYNJ updates the current-year PDFs each month. Re-run the three scripts with
`python scripts/01_download.py --force` to fetch the latest versions, then `quarto render`.

---

## Next.js app

This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

### Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

### Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

### Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.

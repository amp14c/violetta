"""PATH ridership: data loaders, one Plotly theme, and every chart used by the
dashboard (path/dashboard.qmd) and the slides (path/slides.qmd).

Colour meanings are fixed across the project so a colour never means two things:
  * New Jersey stations = blue, New York stations = orange
  * Entries (trip starts here) = aqua, Exits (trip ends here) = violet
  * Years in the hour-of-day chart: 2019 = grey (baseline), 2021 = light orange, latest = blue
  * Magnitude (heatmaps) = one blue ramp, light -> dark
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "processed"

BLUE, ORANGE = "#2a78d6", "#eb6834"
NJ_COLOR, NY_COLOR = BLUE, ORANGE
ENTRY_COLOR, EXIT_COLOR = "#1baf7a", "#6250d6"
SEQ_BLUE = ["#f4f8fd", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5",
            "#256abf", "#184f95", "#0d366b"]
GRAY = "#8a8984"
EVENT = "#c0312f"   # event markers (Hurricane Sandy, COVID-19): a strong red, used for nothing else
TEXT, TEXT2, GRID = "#0b0b0b", "#52514e", "#ebeae6"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

STATION_ORDER = [  # west -> east: NJ then NY
    "Newark", "Harrison", "Journal Square", "Grove Street", "Exchange Place",
    "Newport", "Hoboken", "World Trade Center", "Christopher Street",
    "9th Street", "14th Street", "23rd Street", "33rd Street",
]
NJ_STATIONS = set(STATION_ORDER[:7])
HOURS = [pd.Timestamp(2000, 1, 1, h).strftime("%-I %p").lower() for h in range(24)]

pio.templates["path"] = go.layout.Template(
    layout=dict(
        font=dict(family="system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif", size=13, color=TEXT2),
        title=dict(font=dict(size=15, color=TEXT), x=0, xanchor="left"),
        colorway=[BLUE, ORANGE, ENTRY_COLOR, "#eda100", "#e87ba4", "#008300", EXIT_COLOR],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=20, t=50, b=90),
        hoverlabel=dict(bgcolor="white", bordercolor=GRID, font=dict(color=TEXT)),
        xaxis=dict(showgrid=False, linecolor="#cfcec9", ticks="outside",
                   tickcolor="#cfcec9", zeroline=False, automargin=True),
        yaxis=dict(gridcolor=GRID, zeroline=False, rangemode="tozero", automargin=True),
        legend=dict(orientation="h", yanchor="top", y=-0.16, xanchor="left", x=0,
                    title_text="", entrywidth=190, entrywidthmode="pixels"),
    ),
    data=dict(scatter=[go.Scatter(line=dict(width=2))]),
)
pio.templates.default = "plotly_white+path"
CONFIG = {"displaylogo": False, "responsive": True,
          "modeBarButtonsToRemove": ["lasso2d", "select2d"]}


def show(fig: go.Figure) -> None:
    fig.show(config=CONFIG)


def _menu(buttons, y=1.0):
    return [dict(buttons=buttons, direction="down", x=1, xanchor="right", y=y,
                 yanchor="bottom", bgcolor="white", bordercolor=GRID,
                 font=dict(color=TEXT))]


# ---------------------------------------------------------------- data loaders
def monthly_system() -> pd.DataFrame:
    return pd.read_csv(DATA / "path_monthly_system.csv", parse_dates=["date"])


def monthly_station() -> pd.DataFrame:
    return pd.read_csv(DATA / "path_monthly_by_station.csv", parse_dates=["date"])


def hourly() -> pd.DataFrame:
    df = pd.read_csv(DATA / "path_hourly.csv")
    df["month"] = df.month.astype("Int64")
    return df


def latest_full_year(h: pd.DataFrame) -> int:
    n = h[h.period == "month"].groupby("year").month.nunique()
    return int(n[n == 12].index.max())


def fmt_m(x: float) -> str:
    return f"{x / 1e6:.1f}M"


def headline(sysm: pd.DataFrame, h: pd.DataFrame) -> dict:
    """Numbers quoted in value boxes and slide titles."""
    yr = sysm.groupby("year").agg(total=("total", "sum"), months=("month", "count"))
    full = yr[yr.months == 12]
    latest = int(full.index.max())
    low = sysm.loc[sysm.total.idxmin()]
    x = h[(h.station == "System-wide") & (h.period == "annual")
          & (h.day_type == "weekday") & (h.direction == "entry")]
    peak = (x[x.hour.isin([7, 8, 17, 18])].groupby("year").avg_count.sum()
            / x.groupby("year").avg_count.sum() * 100)
    high = sysm.loc[sysm.total.idxmax()]
    last = sysm.date.max()
    cy = last.year

    def ytd(y):  # Jan..(latest published month), so both years cover the same months
        return sysm[(sysm.year == y) & (sysm.month <= last.month)].total.sum()

    return dict(
        cy=cy, ytd=ytd(cy), ytd_prev=ytd(cy - 1), ytd_change=(ytd(cy) / ytd(cy - 1) - 1) * 100,
        ytd_span=f"Jan–{last:%b}", high_month=high.date, high_total=high.total,
        first=sysm.date.min(), last=last, latest=latest,
        t2019=yr.loc[2019, "total"], t2020=yr.loc[2020, "total"],
        tlatest=yr.loc[latest, "total"], pct=yr.loc[latest, "total"] / yr.loc[2019, "total"] * 100,
        drop=(1 - yr.loc[2020, "total"] / yr.loc[2019, "total"]) * 100,
        low_month=low.date, low_total=low.total,
        peak2019=peak[2019], peak_latest=peak[latest],
    )


# ---------------------------------------------------------------- monthly charts
def fig_system_trend(sysm: pd.DataFrame, height: int = 400) -> go.Figure:
    s = sysm.set_index("date").total
    roll = s.rolling(12).mean()
    fig = go.Figure()
    fig.add_scatter(x=s.index, y=s, name="Trips that month", mode="lines",
                    line=dict(color=BLUE, width=1.2), opacity=0.5,
                    hovertemplate="%{x|%b %Y}: %{y:,.0f} trips<extra></extra>")
    fig.add_scatter(x=roll.index, y=roll, name="12-month average", mode="lines",
                    line=dict(color=BLUE, width=2.5),
                    hovertemplate="12-month avg: %{y:,.0f}<extra></extra>")
    events = [("2012-10-29", "Hurricane Sandy", "left"),
              ("2020-03-01", "COVID-19", "left"),
              # Tournament ran Jun 11 – Jul 19, 2026; the final was at MetLife Stadium, NJ.
              # Label sits left of the line so it stays inside the chart's right edge.
              ("2026-06-11", "FIFA World Cup", "right")]
    for d, *_ in events:
        fig.add_vline(x=d, line=dict(color=EVENT, width=2, dash="dash"))
    # Labels as a text-only trace, not annotations: Plotly (4.1 in these pages) measures
    # annotation widths as ~0 here, which centres them on the line and clips the last one.
    # Scatter text is anchored natively ("middle right" = starts at the point).
    top = s.max() * 1.07
    fig.add_scatter(
        x=[pd.Timestamp(d) for d, *_ in events], y=[top] * len(events),
        text=[f" <b>{label}</b>" if side == "left" else f"<b>{label}</b> "
              for _, label, side in events],  # non-breaking space = gap from the line
        textposition=["middle right" if side == "left" else "middle left"
                      for *_, side in events],
        mode="text", textfont=dict(size=13, color=EVENT), cliponaxis=False,
        hoverinfo="skip", showlegend=False)
    fig.update_yaxes(range=[0, s.max() * 1.12])
    fig.update_layout(title="Trips per month, all 13 stations", height=height,
                      hovermode="x unified",
                      yaxis=dict(tickformat=".2s", showgrid=False, ticks="outside",
                                 tickcolor="#cfcec9", linecolor="#cfcec9", showline=True))
    return fig


def fig_heatmap(sysm: pd.DataFrame, height: int = 520) -> go.Figure:
    grid = sysm.pivot(index="year", columns="month", values="total")
    fig = go.Figure(go.Heatmap(
        z=grid.values, x=MONTHS, y=grid.index.astype(str), colorscale=SEQ_BLUE,
        xgap=2, ygap=2, colorbar=dict(title="Trips", tickformat=".2s", thickness=12),
        hovertemplate="%{x} %{y}: %{z:,.0f} trips<extra></extra>"))
    fig.update_layout(title="Trips per month: each row is a year", height=height,
                      yaxis=dict(autorange="reversed", type="category", showgrid=False))
    return fig


def station_weekday_latest(st: pd.DataFrame) -> pd.Series:
    last = st.date.max()
    recent = st[st.date > last - pd.DateOffset(months=12)]
    return recent.groupby("station").avg_weekday.mean().sort_values()


def fig_station_totals(st: pd.DataFrame, height: int = 470) -> go.Figure:
    """Average weekday ENTRIES by station: where trips begin."""
    v = station_weekday_latest(st)
    last = st.date.max()
    first = last - pd.DateOffset(months=11)
    fig = go.Figure()
    for state, color, name in [("NJ", NJ_COLOR, "New Jersey station"),
                               ("NY", NY_COLOR, "New York station")]:
        r = v[[(s in NJ_STATIONS) == (state == "NJ") for s in v.index]]
        # Legend text wears the same colour as its bars (Gestalt similarity).
        fig.add_bar(y=r.index, x=r.values, orientation="h",
                    name=f"<span style='color:{color}'><b>{name}</b></span>",
                    marker_color=color, marker_cornerradius=4,
                    hovertemplate="%{y}: %{x:,.0f} people enter on an average weekday"
                                  "<extra></extra>")
    for s, x in v.items():  # value labels (annotations render reliably; bar text did not)
        fig.add_annotation(x=x, y=s, text=f"{x:,.0f}", showarrow=False, xanchor="left",
                           xshift=6, font=dict(color=TEXT2, size=12))
    # Station names coloured by state, so the axis reads like the legend.
    ticktext = [f"<span style='color:{NJ_COLOR if s in NJ_STATIONS else NY_COLOR}'>{s}</span>"
                for s in v.index]
    fig.update_layout(
        title=f"Where trips start: average weekday entries, {first:%b %Y}–{last:%b %Y}",
        height=height, bargap=0.25, margin=dict(t=80, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0,
                    entrywidth=170, entrywidthmode="pixels", font=dict(size=13)),
        xaxis=dict(visible=False, range=[0, v.max() * 1.15]),
        yaxis=dict(categoryorder="array", categoryarray=list(v.index), showgrid=False,
                   tickmode="array", tickvals=list(v.index), ticktext=ticktext))
    return fig


def fig_station_explorer(st: pd.DataFrame, height: int = 420) -> go.Figure:
    fig = go.Figure()
    for i, name in enumerate(STATION_ORDER):
        d = st[st.station == name]
        color = NJ_COLOR if name in NJ_STATIONS else NY_COLOR
        for col, label, dash in [("avg_weekday", "Average weekday", "solid"),
                                 ("avg_saturday", "Average Saturday", "dot")]:
            fig.add_scatter(x=d.date, y=d[col], name=label, mode="lines",
                            line=dict(color=color, dash=dash), visible=(i == 0),
                            hovertemplate=f"{label}: %{{y:,.0f}} entries<extra></extra>")
    n = len(STATION_ORDER)
    buttons = [dict(label=name, method="update",
                    args=[{"visible": [j // 2 == i for j in range(2 * n)]},
                          {"title.text": f"{name}: people entering per day"}])
               for i, name in enumerate(STATION_ORDER)]
    fig.update_layout(title=f"{STATION_ORDER[0]}: people entering per day", height=height,
                      hovermode="x unified", yaxis_tickformat=",.0f",
                      updatemenus=_menu(buttons, y=1.08), margin=dict(t=80),
                      )
    return fig


# ---------------------------------------------------------------- hourly charts
def fig_day_curve(h: pd.DataFrame, height: int = 420) -> go.Figure:
    annual = h[(h.station == "System-wide") & (h.period == "annual")]
    latest = latest_full_year(h)
    series = [(2019, GRAY, "dot"), (2021, "#f3b597", "solid"), (latest, BLUE, "solid")]
    day_types = ["weekday", "saturday", "sunday"]
    fig = go.Figure()
    for di, dt in enumerate(day_types):
        for y, c, dash in series:
            d = annual[(annual.year == y) & (annual.day_type == dt)
                       & (annual.direction == "entry")].sort_values("hour")
            fig.add_scatter(x=HOURS, y=d.avg_count, name=str(y), mode="lines",
                            line=dict(color=c, dash=dash, shape="spline", smoothing=0.6,
                                      width=2.5 if y == latest else 2),
                            visible=(di == 0),
                            hovertemplate=f"{y}: %{{y:,.0f}} entries<extra></extra>")
    k = len(series)
    buttons = [dict(label=dt.title(), method="update",
                    args=[{"visible": [j // k == i for j in range(len(day_types) * k)]},
                          {"title.text": f"People entering PATH each hour, average {dt}"}])
               for i, dt in enumerate(day_types)]
    fig.update_layout(title="People entering PATH each hour, average weekday", height=height,
                      hovermode="x unified", yaxis_tickformat=",.0f",
                      xaxis=dict(tickvals=HOURS[::3]),
                      updatemenus=_menu(buttons, y=1.08), margin=dict(t=80),
                      )
    return fig


def peak_share(h: pd.DataFrame) -> pd.DataFrame:
    m = h[(h.station == "System-wide") & (h.period == "month")
          & (h.day_type == "weekday") & (h.direction == "entry") & (h.year >= 2017)]
    tot = m.groupby(["year", "month"]).avg_count.sum()
    pk = m[m.hour.isin([7, 8, 17, 18])].groupby(["year", "month"]).avg_count.sum()
    s = (pk / tot * 100).reset_index(name="share")
    s["date"] = pd.to_datetime(dict(year=s.year, month=s.month, day=1))
    return s


def fig_peak_share(h: pd.DataFrame, height: int = 400) -> go.Figure:
    s = peak_share(h)
    pre = s[s.year <= 2019].share.mean()
    fig = go.Figure()
    fig.add_scatter(x=s.date, y=s.share, mode="lines+markers", name="Peak-hour share",
                    line=dict(color=BLUE), marker=dict(size=5),
                    hovertemplate="%{x|%b %Y}: %{y:.1f}% of weekday entries<extra></extra>")
    fig.add_hline(y=pre, line=dict(color=GRAY, width=1, dash="dot"),
                  annotation_text=f"2017–19 average: {pre:.1f}%",
                  annotation_position="bottom left", annotation_font_color=TEXT2)
    fig.update_layout(title="Share of weekday entries in the 4 rush hours (7–9 am, 5–7 pm)",
                      height=height, hovermode="x unified", showlegend=False,
                      yaxis=dict(ticksuffix="%", rangemode="normal"))
    return fig


def fig_hour_month(h: pd.DataFrame, height: int = 680) -> go.Figure:
    m = h[(h.station == "System-wide") & (h.period == "month")
          & (h.day_type == "weekday") & (h.direction == "entry") & (h.year >= 2017)].copy()
    m["ym"] = pd.to_datetime(dict(year=m.year, month=m.month, day=1)).dt.strftime("%Y-%m")
    grid = m.pivot(index="ym", columns="hour", values="avg_count")
    fig = go.Figure(go.Heatmap(
        z=grid.values, x=HOURS, y=grid.index, colorscale=SEQ_BLUE, xgap=1,
        colorbar=dict(title="Entries", tickformat=",.0f", thickness=12),
        hovertemplate="%{y}, %{x}: %{z:,.0f} people entering<extra></extra>"))
    fig.update_layout(title="Weekday entries by hour (columns) and month (rows)",
                      height=height, xaxis=dict(tickvals=HOURS[::3]),
                      yaxis=dict(autorange="reversed", type="category", showgrid=False,
                                 nticks=12))
    return fig


def fig_station_hour(h: pd.DataFrame, height: int = 500, toggle: bool = True) -> go.Figure:
    year = latest_full_year(h)
    a = h[(h.period == "annual") & (h.year == year) & (h.day_type == "weekday")
          & (h.station != "System-wide")]
    labels = {"entry": "Entries: trip STARTS here", "exit": "Exits: trip ENDS here"}
    fig = go.Figure()
    for i, direction in enumerate(["entry", "exit"]):
        d = a[a.direction == direction].pivot(index="station", columns="hour", values="avg_count")
        d = d.loc[STATION_ORDER]
        d = d.div(d.sum(axis=1), axis=0) * 100
        ylab = [f"{s} (NJ)" if s in NJ_STATIONS else f"{s} (NY)" for s in d.index]
        fig.add_heatmap(z=d.values, x=HOURS, y=ylab, colorscale=SEQ_BLUE, xgap=1, ygap=2,
                        visible=(i == 0), zmin=0, zmax=25,
                        colorbar=dict(ticksuffix="%", thickness=12, y=0.45, len=0.9),
                        hovertemplate="%{y}, %{x}: %{z:.1f}% of the station's daily "
                                      + direction + "s<extra></extra>")
    buttons = [dict(label=labels[dr], method="update",
                    args=[{"visible": [j == i for j in range(2)]},
                          {"title.text": f"{labels[dr]}: share of each station's weekday "
                                         f"{dr}s by hour ({year})"}])
               for i, dr in enumerate(["entry", "exit"])]
    fig.update_layout(
        title=f"{labels['entry']}: share of each station's weekday entries by hour ({year})",
        height=height, xaxis=dict(tickvals=HOURS[::3]),
        yaxis=dict(autorange="reversed", showgrid=False),
        updatemenus=_menu(buttons, y=1.06) if toggle else None, margin=dict(t=80))
    # NJ / NY divider between Hoboken and WTC
    fig.add_hline(y=6.5, line=dict(color="white", width=4))
    return fig


def fig_hourly_explorer(h: pd.DataFrame, height: int = 420) -> go.Figure:
    year = latest_full_year(h)
    wk = h[(h.period == "annual") & (h.day_type == "weekday")]
    names = STATION_ORDER + ["System-wide"]
    lines = [(year, "entry", ENTRY_COLOR, "solid", f"Entries {year} (trip starts here)"),
             (year, "exit", EXIT_COLOR, "solid", f"Exits {year} (trip ends here)"),
             (2019, "entry", GRAY, "dot", "Entries 2019")]
    fig = go.Figure()
    for i, name in enumerate(names):
        for y, direction, color, dash, label in lines:
            d = wk[(wk.station == name) & (wk.year == y)
                   & (wk.direction == direction)].sort_values("hour")
            fig.add_scatter(x=HOURS, y=d.avg_count, name=label, mode="lines",
                            line=dict(color=color, dash=dash, width=2.5 if dash == "solid" else 1.5),
                            visible=(i == 0),
                            hovertemplate=f"{label}: %{{y:,.0f}}<extra></extra>")
    k = len(lines)
    buttons = [dict(label=n, method="update",
                    args=[{"visible": [j // k == i for j in range(k * len(names))]},
                          {"title.text": f"{n}: people entering and exiting each hour, "
                                         f"average weekday"}])
               for i, n in enumerate(names)]
    fig.update_layout(title=f"{names[0]}: people entering and exiting each hour, average weekday",
                      height=height, hovermode="x unified", yaxis_tickformat=",.0f",
                      xaxis=dict(tickvals=HOURS[::3]),
                      updatemenus=_menu(buttons, y=1.08), margin=dict(t=80),
                      )
    return fig


# ---------------------------------------------------------------- multi-select station pickers
# Plotly's own menus are single-select, so the pickers are a small HTML control panel
# (checkboxes + dropdowns) that redraws a Plotly chart in the browser. All data is
# embedded in the page; nothing is fetched at runtime.
import json as _json
import uuid as _uuid

_PICKER_JS = r"""
window.PATHPicker = window.PATHPicker || function (uid, P) {
  const root = document.getElementById(uid);
  const plot = root.querySelector(".pp-plot");
  const color = s => (P.nj.includes(s) ? P.colors.NJ : P.colors.NY);
  const key = () => P.selects.map(s => root.querySelector(`select[data-k="${s.id}"]`).value).join("|");
  const chosen = () => [...root.querySelectorAll("input.pp-st:checked")].map(i => i.value);
  const fmt = v => v == null ? "–" : Math.round(v).toLocaleString();

  function labels() {
    // Name each line at its right end; nudge labels apart so they don't overlap.
    const fl = plot._fullLayout; if (!fl || !fl.yaxis) return;
    const ya = fl.yaxis, h = fl._size.h, [y0, y1] = ya.range;
    const px = v => h - (v - y0) / (y1 - y0) * h;
    const items = (plot.data || []).map(t => {
      let i = t.y.length - 1; while (i >= 0 && t.y[i] == null) i--;
      return i < 0 ? null : { name: t.name, x: t.x[i], y: t.y[i], p: px(t.y[i]) };
    }).filter(Boolean).sort((a, b) => a.p - b.p);
    for (let i = 1; i < items.length; i++) if (items[i].p - items[i - 1].p < 15) items[i].p = items[i - 1].p + 15;
    const ann = items.map(it => ({
      x: it.x, xref: "x", xanchor: "left", xshift: 6, yref: "paper", yanchor: "middle",
      y: 1 - it.p / h, showarrow: false, text: `<b>${it.name}</b>`,
      font: { color: color(it.name), size: 12 } }));
    Plotly.relayout(plot, { annotations: ann });
  }

  function draw() {
    const data = P.series[key()] || {};
    const xs = P.xs[key()] || P.x;
    const names = chosen();
    const traces = names.map(n => ({
      x: xs, y: data[n] || [], name: n, type: "scatter", mode: "lines",
      line: { color: color(n), width: 2 },
      hovertemplate: `<span style="color:${color(n)}">${n}</span>: %{y:,.0f}<extra></extra>` }));
    const title = P.title(root, key());
    const layout = {
      title: { text: title, x: 0, xanchor: "left", font: { size: 15, color: "#0b0b0b" } },
      height: P.height, margin: { l: 60, r: 150, t: 50, b: 50 },
      paper_bgcolor: "rgba(0,0,0,0)", plot_bgcolor: "rgba(0,0,0,0)",
      font: { family: "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif", size: 13, color: "#52514e" },
      showlegend: false, hovermode: "x unified",
      hoverlabel: { bgcolor: "white", bordercolor: "#ebeae6" },
      xaxis: Object.assign({ showgrid: false, linecolor: "#cfcec9", ticks: "outside", tickcolor: "#cfcec9" }, P.xaxis || {}),
      yaxis: { gridcolor: "#ebeae6", zeroline: false, rangemode: "tozero", tickformat: ",.0f" },
      annotations: names.length ? [] : [{ text: "Pick one or more stations above", showarrow: false,
        xref: "paper", yref: "paper", x: 0.5, y: 0.5, font: { size: 15, color: "#8a8984" } }] };
    Plotly.react(plot, traces, layout, { displaylogo: false, responsive: true,
      modeBarButtonsToRemove: ["lasso2d", "select2d"] }).then(() => { if (names.length) labels(); });
    root.querySelector(".pp-count").textContent =
      names.length === P.stations.length ? "All 13 stations" : `${names.length} selected`;
  }

  function setAll(pred) { root.querySelectorAll("input.pp-st").forEach(i => { i.checked = pred(i.value); }); draw(); }
  root.querySelectorAll("select").forEach(s => s.addEventListener("change", draw));
  root.querySelectorAll("input.pp-st").forEach(i => i.addEventListener("change", draw));
  root.querySelector(".pp-all").addEventListener("click", () => setAll(() => true));
  root.querySelector(".pp-nj").addEventListener("click", () => setAll(s => P.nj.includes(s)));
  root.querySelector(".pp-ny").addEventListener("click", () => setAll(s => !P.nj.includes(s)));
  root.querySelector(".pp-none").addEventListener("click", () => setAll(() => false));
  (function wait() { if (window.Plotly) { draw(); window.addEventListener("resize", () => setTimeout(labels, 200)); }
                     else setTimeout(wait, 100); })();
  document.addEventListener("shown.bs.tab", () => setTimeout(() => { Plotly.Plots.resize(plot); labels(); }, 80));
};
"""


def _picker(payload: dict, selects: list[dict], defaults: list[str], title_js: str,
            height: int) -> "HTML":
    from IPython.display import HTML
    uid = "pp-" + _uuid.uuid4().hex[:8]
    sel_html = "".join(
        f'<label class="pp-sel">{s["label"]}<select data-k="{s["id"]}">'
        + "".join(f'<option value="{o[0]}"{" selected" if o[0] == s.get("default") else ""}>{o[1]}</option>'
                  for o in s["options"])
        + "</select></label>" for s in selects)

    def boxes(names, cls, color):
        return "".join(
            f'<label class="pp-pill {cls}" style="--c:{color}"><input type="checkbox" class="pp-st" '
            f'value="{n}"{" checked" if n in defaults else ""}><span>{n}</span></label>' for n in names)

    html = f"""
<div id="{uid}" class="pp">
  <div class="pp-row">{sel_html}
    <span class="pp-btns"><button type="button" class="pp-all">All stations</button><button type="button" class="pp-nj">All NJ</button><button type="button" class="pp-ny">All NY</button><button type="button" class="pp-none">Clear</button>
    <span class="pp-count"></span></span>
  </div>
  <div class="pp-row"><span class="pp-grp" style="color:{NJ_COLOR}">New Jersey</span>{boxes(STATION_ORDER[:7], "nj", NJ_COLOR)}</div>
  <div class="pp-row"><span class="pp-grp" style="color:{NY_COLOR}">New York</span>{boxes(STATION_ORDER[7:], "ny", NY_COLOR)}</div>
  <div class="pp-plot"></div>
</div>
<script>{_PICKER_JS}
(function(){{ const P = {_json.dumps(payload, separators=(",", ":"))};
  P.title = {title_js}; P.selects = {_json.dumps([{"id": s["id"]} for s in selects])}; P.height = {height};
  PATHPicker("{uid}", P); }})();
</script>"""
    return HTML(html)


def _base_payload() -> dict:
    return dict(nj=STATION_ORDER[:7], stations=STATION_ORDER,
                colors=dict(NJ=NJ_COLOR, NY=NY_COLOR), xs={})


def picker_monthly(st: pd.DataFrame, height: int = 440):
    measures = [("avg_weekday", "Average weekday"), ("avg_saturday", "Average Saturday"),
                ("avg_sunday", "Average Sunday"), ("total", "Monthly total")]
    dates = sorted(st.date.unique())
    x = [pd.Timestamp(d).strftime("%Y-%m-%d") for d in dates]
    series = {}
    for col, _ in measures:
        g = st.pivot(index="date", columns="station", values=col).reindex(dates)
        series[col] = {s: [None if pd.isna(v) else float(v) for v in g[s]] for s in STATION_ORDER}
    P = _base_payload() | dict(x=x, series=series, xaxis={"type": "date"})
    title_js = ('(root, k) => "People entering at each station: " + '
                'root.querySelector("select[data-k=m]").selectedOptions[0].text.toLowerCase() '
                '+ (k === "total" ? "" : " per day")')
    return _picker(P, [dict(id="m", label="Measure", options=measures, default="avg_weekday")],
                   ["Journal Square", "Hoboken", "World Trade Center", "33rd Street"], title_js, height)


def _hourly_periods(h: pd.DataFrame) -> list[tuple[str, str]]:
    """(key, label) for every period with hourly data: full years, the partial current
    year, and the one-month snapshot reports."""
    ann = sorted(h[h.period == "annual"].year.unique())
    full = h[h.period == "month"].groupby("year").month.nunique()
    out = []
    for y in ann:
        n = int(full.get(y, 0))
        out.append((str(y), f"{y}" if n == 12 else f"{y} YTD (Jan–{MONTHS[n - 1]})"))
    for y in sorted(set(h.year) - set(ann)):  # snapshot years
        m = int(h[h.year == y].month.dropna().iloc[0])
        out.append((f"{y}-{m:02d}", f"{MONTHS[m - 1]} {y} (one month)"))
    return sorted(out, key=lambda kv: kv[0], reverse=True)


def _hourly_slice(h: pd.DataFrame, key: str) -> pd.DataFrame:
    if "-" in key:
        y, m = map(int, key.split("-"))
        return h[(h.year == y) & (h.period == "month") & (h.month == m)]
    return h[(h.year == int(key)) & (h.period == "annual")]


def picker_hourly(h: pd.DataFrame, height: int = 440):
    periods = _hourly_periods(h)
    day_types = [("weekday", "Average weekday"), ("saturday", "Average Saturday"),
                 ("sunday", "Average Sunday")]
    dirs = [("entry", "Entries: trip starts here"), ("exit", "Exits: trip ends here")]
    series = {}
    for pk, _ in periods:
        sl = _hourly_slice(h, pk)
        for dt, _ in day_types:
            for dr, _ in dirs:
                g = sl[(sl.day_type == dt) & (sl.direction == dr)].pivot(
                    index="hour", columns="station", values="avg_count").reindex(range(24))
                series[f"{pk}|{dt}|{dr}"] = {
                    s: [None if pd.isna(v) else float(v) for v in g[s]] if s in g else []
                    for s in STATION_ORDER}
    P = _base_payload() | dict(x=HOURS, series=series,
                               xaxis={"type": "category", "tickvals": HOURS[::3]})
    title_js = ('(root, k) => { const t = s => root.querySelector(`select[data-k=${s}]`).selectedOptions[0].text;'
                ' return t("d") + " by hour · " + t("t").toLowerCase() + " · " + t("p"); }')
    latest = str(latest_full_year(h))
    return _picker(P, [dict(id="p", label="Period", options=periods, default=latest),
                       dict(id="t", label="Day", options=day_types, default="weekday"),
                       dict(id="d", label="Show", options=dirs, default="entry")],
                   ["Journal Square", "World Trade Center", "33rd Street"], title_js, height)


# ---------------------------------------------------------------- entries vs exits
def entry_exit_table(h: pd.DataFrame, day_type: str = "weekday") -> pd.DataFrame:
    rows = []
    for key, label in _hourly_periods(h):
        sl = _hourly_slice(h, key)
        d = (sl[sl.day_type == day_type].groupby(["station", "direction"]).avg_count.sum()
             .unstack().reset_index())
        d["key"], d["label"] = key, label
        rows.append(d)
    t = pd.concat(rows, ignore_index=True)
    t["diff_pct"] = (t.exit / t.entry - 1) * 100
    return t


def _spread(vals: list[float], gap: float) -> list[float]:
    """Nudge sorted label positions apart by at least `gap` (keeps original order)."""
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    out = list(vals)
    for a, b in zip(order, order[1:]):
        if out[b] - out[a] < gap:
            out[b] = out[a] + gap
    return out


def fig_entry_exit_slope(h: pd.DataFrame, height: int = 620) -> go.Figure:
    import math
    t = entry_exit_table(h)
    t = t[t.station != "System-wide"]
    periods = _hourly_periods(h)
    latest = str(latest_full_year(h))
    fig = go.Figure()
    menus, n = [], len(STATION_ORDER)
    for pi, (pk, plabel) in enumerate(periods):
        d = t[t.key == pk].set_index("station").reindex(STATION_ORDER)
        lo = math.log10(min(d.entry.min(), d.exit.min()) * 0.85)
        hi = math.log10(max(d.entry.max(), d.exit.max()) * 1.12)
        gap = (hi - lo) * 0.038
        ly = _spread([math.log10(v) for v in d.entry], gap)
        ry = _spread([math.log10(v) for v in d.exit], gap)
        anns = []
        for i, (s, r) in enumerate(d.iterrows()):
            c = NJ_COLOR if s in NJ_STATIONS else NY_COLOR
            big = abs(r.diff_pct) >= 20
            fig.add_scatter(
                x=[0, 1], y=[r.entry, r.exit], mode="lines+markers", name=s,
                line=dict(color=c, width=3.5 if big else 1.8),
                marker=dict(size=8, color=c, line=dict(color="white", width=2)),
                opacity=1 if big else 0.55, visible=(pk == latest), showlegend=False,
                customdata=[[r.diff_pct]] * 2,
                hovertemplate=(f"<b>{s}</b><br>Entries: {r.entry:,.0f}<br>Exits: {r.exit:,.0f}"
                               f"<br>Exits vs entries: {r.diff_pct:+.0f}%<extra></extra>"))
            anns.append(dict(x=0, y=ly[i], xref="x", yref="y", xanchor="right", xshift=-10,
                             showarrow=False, text=f"<b>{s}</b>  {r.entry:,.0f}",
                             font=dict(color=c, size=12)))
            anns.append(dict(x=1, y=ry[i], xref="x", yref="y", xanchor="left", xshift=10,
                             showarrow=False,
                             text=f"{r.exit:,.0f}  <b>{r.diff_pct:+.0f}%</b>  {s}",
                             font=dict(color=c, size=12)))
        vis = [False] * (n * len(periods))
        vis[pi * n:(pi + 1) * n] = [True] * n
        menus.append(dict(label=plabel, method="update",
                          args=[{"visible": vis},
                                {"annotations": anns, "yaxis.range": [lo, hi],
                                 "title.text": f"Entries vs. exits per station, average weekday · {plabel}"}]))
        if pk == latest:
            cur = (anns, lo, hi, plabel)
    anns, lo, hi, plabel = cur
    fig.update_layout(
        title=f"Entries vs. exits per station, average weekday · {plabel}",
        height=height, annotations=anns, showlegend=False, margin=dict(l=220, r=260, t=90, b=50),
        xaxis=dict(range=[-0.08, 1.08], tickvals=[0, 1], showline=False, ticks="",
                   ticktext=["<b>Entries</b><br>trip starts here", "<b>Exits</b><br>trip ends here"],
                   side="top", fixedrange=True),
        yaxis=dict(type="log", range=[lo, hi], visible=False, fixedrange=True),
        updatemenus=[dict(buttons=menus, direction="down", x=1, xanchor="right", y=1.12,
                          yanchor="bottom", bgcolor="white", bordercolor=GRID,
                          active=[p[0] for p in periods].index(latest))])
    return fig


def fig_entry_exit_heatmap(h: pd.DataFrame, height: int = 520) -> go.Figure:
    t = entry_exit_table(h)
    periods = sorted(_hourly_periods(h), key=lambda kv: kv[0])
    rows = STATION_ORDER + ["System-wide"]
    g = t.pivot(index="station", columns="key", values="diff_pct").reindex(rows)[[p[0] for p in periods]]
    cols = [p[1].replace(" (one month)", "*").replace(" YTD", "<br>YTD").split(" (")[0] for p in periods]
    ylab = [f"<span style='color:{NJ_COLOR if s in NJ_STATIONS else (NY_COLOR if s != 'System-wide' else TEXT)}'>"
            f"{'<b>System-wide</b>' if s == 'System-wide' else s}</span>" for s in rows]
    diverging = [[0, "#184f95"], [0.25, "#6da7ec"], [0.5, "#f0efec"], [0.75, "#ee8a89"], [1, "#a8282a"]]
    fig = go.Figure(go.Heatmap(
        z=g.values, x=cols, y=ylab, colorscale=diverging, zmid=0, zmin=-40, zmax=40,
        xgap=2, ygap=2, texttemplate="%{z:+.0f}%", textfont=dict(size=11),
        colorbar=dict(title="Exits vs.<br>entries", ticksuffix="%", thickness=12),
        hovertemplate="%{y} · %{x}: exits are %{z:+.1f}% vs. entries<extra></extra>"))
    fig.update_layout(title="Exits vs. entries, % difference, average weekday, every period available",
                      height=height, xaxis=dict(side="top", type="category"),
                      yaxis=dict(autorange="reversed", showgrid=False), margin=dict(t=90, b=30))
    fig.add_hline(y=6.5, line=dict(color="white", width=4))
    fig.add_hline(y=12.5, line=dict(color="white", width=4))
    return fig


# ---------------------------------------------------------------- KPI tiles
def kpi_tiles(k: dict):
    """Four headline tiles. Plain HTML so each tile can carry a context line under the
    number (Quarto's built-in value boxes only take a title and a value)."""
    from IPython.display import HTML
    span = f"{k['first']:%b %Y}–{k['last']:%b %Y}"
    tiles = [
        ("train-front", True, f"Trips, CY{k['cy']} year-to-date", fmt_m(k["ytd"]),
         f"{k['ytd_span']} {k['cy']}, all 13 stations"),
        ("arrow-down", False, "Lowest month", f"{k['low_total'] / 1e3:,.0f}K",
         f"{k['low_month']:%B %Y} · lowest of all months, {span}"),
        ("arrow-up", False, "Highest month", f"{k['high_total'] / 1e6:.2f}M",
         f"{k['high_month']:%B %Y} · highest of all months, {span}"),
        ("graph-up-arrow", False, f"Change, CY{k['cy'] - 1} → CY{k['cy']}",
         f"{k['ytd_change']:+.1f}%",
         f"{k['ytd_span']} {k['cy']} vs. {k['ytd_span']} {k['cy'] - 1} "
         f"({fmt_m(k['ytd'])} vs. {fmt_m(k['ytd_prev'])}), same months"),
    ]
    html = "".join(
        f'<div class="kpi-tile{" kpi-primary" if primary else ""}">'
        f'<i class="bi bi-{icon}"></i><div><div class="kpi-t">{t}</div>'
        f'<div class="kpi-v">{v}</div><div class="kpi-n">{n}</div></div></div>'
        for icon, primary, t, v, n in tiles)
    return HTML(f'<div class="kpi-tiles">{html}</div>')

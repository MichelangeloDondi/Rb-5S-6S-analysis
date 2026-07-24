#!/usr/bin/env python3
"""
The program on its recovered clock — docs/apparatus/program_timeline.png.

Three panels, one per session, every mark an actual acquisition from
data_recovered/CLOCK.csv (the committed clock; addenda 1–11): the LeCroy
dress rehearsal, the pilot morning (ruler commissioning → Def → 91 °C sweep),
and the campaign itself with its power ladders, temperature dwells, the
9.6 h break, and the evidence-backed etalon-transient windows shaded.

Regenerate with:  .venv/bin/python scripts/make_timeline_figure.py
Deterministic input; matplotlib output (byte-identity across matplotlib
versions is not guaranteed, so the guard checks existence + freshness of the
embed, not bytes).
"""

from __future__ import annotations

import csv
import datetime as dt
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "apparatus" / "program_timeline.png"

SURFACE = "#fcfcfb"
C_SCI = "#2a78d6"       # categorical slot 1 — science acquisitions
C_RUL = "#eb6834"       # categorical slot 2 — EOM-ruler acquisitions
INK = "#2b2b2a"
INK2 = "#6b6b69"
GRID = "#e3e3e0"
BAND = "#d8d8d4"        # neutral phase band (etalon transient), not a status color

JST = dt.timezone(dt.timedelta(hours=9))


def jst(epoch: int) -> dt.datetime:
    return dt.datetime.fromtimestamp(epoch, tz=JST)


def load():
    rows = list(csv.DictReader(open(ROOT / "data_recovered" / "CLOCK.csv")))
    ev = {"rehearsal": [], "pilot": [], "campaign": []}
    for r in rows:
        t = jst(int(r["mtime_epoch"]))
        src, path, mf = r["source"], r["path"], r["manifest_file"]
        if src == "prehistory" and path.startswith("2025-07-04/"):
            ev["rehearsal"].append((t, "sci", path))
        elif src == "prehistory" and path.startswith("2025-07-03/"):
            ev["rehearsal"].append((t, "rul", path))       # EOM first trials
        elif src == "pilot":
            kind = "rul" if "EOM ruler" in path else "sci"
            ev["pilot"].append((t, kind, path))
        elif src == "main" and mf:
            top = mf.split("/")[0]
            if top in ("p_sweep", "t_sweep"):
                ev["campaign"].append((t, "sci", mf))
            elif top in ("rulers_p", "rulers_t", "temperature_EOM", "power_eom"):
                ev["campaign"].append((t, "rul", mf))
    for k in ev:
        ev[k].sort()
    return ev


def ticks(ax, events, kind, y0, y1):
    xs = [t for t, k, _ in events if k == kind]
    color = C_SCI if kind == "sci" else C_RUL
    ax.vlines(xs, y0, y1, color=color, lw=1.0, alpha=0.9)


def panel(ax, events, t0, t1, title):
    ax.set_xlim(t0, t1)
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=JST))
    ax.grid(axis="x", color=GRID, lw=0.6, alpha=0.7)
    ax.set_facecolor(SURFACE)
    ax.text(0.0, 1.18, title, transform=ax.transAxes, fontsize=10,
            color=INK, fontweight="bold", va="bottom")
    ticks(ax, events, "sci", 0.16, 0.62)
    ticks(ax, events, "rul", 0.70, 0.94)


def label(ax, when, y, text, color=INK2, size=7.5, ha="center", weight="normal"):
    ax.text(when, y, text, fontsize=size, color=color, ha=ha, va="center",
            fontweight=weight)


def main() -> int:
    ev = load()
    fig, axes = plt.subplots(
        3, 1, figsize=(12.5, 6.4), facecolor=SURFACE,
        gridspec_kw=dict(height_ratios=[1, 1, 1.35], hspace=0.78))

    D = dt.timedelta

    # -- rehearsal ----------------------------------------------------------
    ax = axes[0]
    r0 = dt.datetime(2025, 7, 4, 22, 10, tzinfo=JST)
    r1 = dt.datetime(2025, 7, 5, 1, 55, tzinfo=JST)
    reh = [e for e in ev["rehearsal"] if e[0] >= r0]
    panel(ax, reh, r0, r1,
          "2025-07-04 → 05 · dress rehearsal — LeCroy, 4 peaks × 90/180/270 mW"
          " (in-file trigger clock)")
    label(ax, dt.datetime(2025, 7, 4, 22, 33, tzinfo=JST), 0.04,
          "22:31 first trigger", ha="left")
    label(ax, dt.datetime(2025, 7, 5, 1, 36, tzinfo=JST), 0.04,
          "01:38 last", ha="right")
    label(ax, dt.datetime(2025, 7, 4, 23, 20, tzinfo=JST), 0.50,
          "EOM first trials ran earlier that morning,\n03:37–03:43 JST — the ruler idea is\nthirteen days older than its final form",
          size=7.5, ha="center")

    # -- pilot --------------------------------------------------------------
    ax = axes[1]
    p0 = dt.datetime(2025, 7, 17, 4, 0, tzinfo=JST)
    p1 = dt.datetime(2025, 7, 17, 7, 30, tzinfo=JST)
    panel(ax, ev["pilot"], p0, p1,
          "2025-07-17 morning · pilot — ruler commissioning, then 4192 nm @ 91 °C")
    for when, txt in ((dt.datetime(2025, 7, 17, 4, 21, tzinfo=JST), "Initial attempts"),
                      (dt.datetime(2025, 7, 17, 6, 18, tzinfo=JST), "adjusted"),
                      (dt.datetime(2025, 7, 17, 6, 33, tzinfo=JST), "Def")):
        label(ax, when, 0.45, txt, color=C_RUL, size=7.5)
    label(ax, dt.datetime(2025, 7, 17, 7, 3, tzinfo=JST), 0.04,
          "210 → 035 → 070 → 105 mW  (widths flat; amplitudes ×34 vs ×36 P²)")

    # -- campaign -----------------------------------------------------------
    ax = axes[2]
    c0 = dt.datetime(2025, 7, 17, 23, 15, tzinfo=JST)
    c1 = dt.datetime(2025, 7, 18, 20, 55, tzinfo=JST)
    panel(ax, ev["campaign"], c0, c1,
          "2025-07-17 → 18 · the campaign — the frozen archive’s 297 traces")
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=2, tz=JST))

    # evidence-backed etalon-transient windows
    s0 = dt.datetime(2025, 7, 17, 23, 47, tzinfo=JST)
    relock = dt.datetime(2025, 7, 18, 17, 3, tzinfo=JST)
    for a in (s0, relock):
        ax.axvspan(a, a + D(hours=2), color=BAND, alpha=0.55, lw=0)
    label(ax, s0 + D(minutes=62), 1.03, "etalon transient (~2 h)", size=7.5)
    label(ax, relock + D(minutes=62), 1.03, "re-lock 17:03 → fresh transient", size=7.5)

    # the break
    b0 = dt.datetime(2025, 7, 18, 7, 55, tzinfo=JST)
    label(ax, b0 + D(hours=4, minutes=45), 0.40,
          "9.6 h daytime break\n(lock down; IMG_2896 catches the 17:03 re-lock)",
          size=8)

    # ladders and dwells
    for when, txt in ((dt.datetime(2025, 7, 17, 23, 58, tzinfo=JST), "4192"),
                      (dt.datetime(2025, 7, 18, 0, 41, tzinfo=JST), "4207"),
                      (dt.datetime(2025, 7, 18, 3, 39, tzinfo=JST), "4154"),
                      (dt.datetime(2025, 7, 18, 4, 35, tzinfo=JST), "4121")):
        label(ax, when, 0.04, txt, size=7.5, weight="bold")
    label(ax, dt.datetime(2025, 7, 18, 2, 25, tzinfo=JST), 0.42,
          "four power ladders\n(225→25 mW each)")
    for when, txt in ((dt.datetime(2025, 7, 18, 7, 15, tzinfo=JST), "110 °C"),
                      (dt.datetime(2025, 7, 18, 17, 50, tzinfo=JST), "90 °C"),
                      (dt.datetime(2025, 7, 18, 19, 45, tzinfo=JST), "70 °C")):
        label(ax, when, 0.04, txt, size=7.5, weight="bold")

    # legend (identity never color-alone: lanes + legend)
    from matplotlib.lines import Line2D
    fig.legend(handles=[
        Line2D([], [], color=C_SCI, lw=2, label="science acquisition (lower lane)"),
        Line2D([], [], color=C_RUL, lw=2, label="EOM-ruler acquisition (upper lane)"),
        matplotlib.patches.Patch(color=BAND, alpha=0.55,
                                 label="etalon thermal transient (~2 h)")],
        loc="upper right", bbox_to_anchor=(0.99, 1.00), frameon=False,
        fontsize=8, labelcolor=INK)

    fig.suptitle("The 5S→6S program on its recovered clock — every acquisition, "
                 "from data_recovered/CLOCK.csv (times JST)",
                 x=0.01, ha="left", fontsize=11.5, color=INK, fontweight="bold")
    fig.text(0.01, 0.005,
             "Sessions: LeCroy dress rehearsal (in-file trigger times) · pilot "
             "(FAT mtimes) · campaign (FAT mtimes, instrument-validated to "
             "seconds — addendum 11). The archive was take four.",
             fontsize=7.5, color=INK2)
    fig.savefig(OUT, dpi=150, bbox_inches="tight", facecolor=SURFACE)
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

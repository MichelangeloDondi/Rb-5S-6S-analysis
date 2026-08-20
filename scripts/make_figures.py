#!/usr/bin/env python3
"""
Publication figures from the committed results/ CSVs (paper draft).

Design choices (per the dataviz method, adapted to matplotlib science figures):
- the four peaks use a FIXED Okabe-Ito colorblind-safe order everywhere, so a
  colour means the same peak across every panel;
- one y-axis per panel (never dual-axis); recessive grid; error bars shown;
  legends present, units on every axis;
- every figure states in its title/annotation what is PRELIMINARY (w0-limited)
  vs robust, matching README section 5.

Writes PNGs to figures/. Run after the pipeline (reads results/*.csv).
"""

from __future__ import annotations

import csv
import datetime as dt_module
import sys
from collections import defaultdict
from pathlib import Path

import math
import numpy as np
from scipy.optimize import least_squares
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C  # noqa: E402
from rb5s6s.density import density_units  # noqa: E402
from rb5s6s.constants import (
    peak_title,  # noqa: E402
    GAMMA_NAT_HZ, TOOTH_SPACING_LASER_HZ, DRIFT_RATE_LASER_HZ_PER_MIN)

GNAT = GAMMA_NAT_HZ / 1e6
FIG = C.REPO_ROOT / "figures"
FIG.mkdir(exist_ok=True)
# Fingerprint of the results/ CSVs these figures are drawn from, stamped into
# each PNG's metadata so a stale figure (results changed, figure not redrawn)
# is caught by tests/test_figures_fresh.py without a fragile pixel compare.
_DATA_FP = C.results_fingerprint()


def _renderer(fig):
    """A renderer for this figure, on any matplotlib the CI matrix runs.

    Same portable construction as the canvas guard uses, and for the same
    reason: `fig.canvas.get_renderer()` exists on the Agg canvas and not on
    FigureCanvasBase, which raised on one CI leg while the local gate was
    clean.
    """
    fig.canvas.draw()
    get = getattr(fig.canvas, "get_renderer", None)
    if get is not None:
        return get()
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    FigureCanvasAgg(fig)
    fig.canvas.draw()
    return fig.canvas.get_renderer()


def pm(value, err, unit=""):
    """Format a value and its uncertainty per the two-significant-digit rule.

    The uncertainty carries exactly two significant digits and the value is
    rounded to the same decimal place, so the pair reads as one statement.
    This is deliberately not a fixed `:.4f`: for an uncertainty of 0.0304 a
    fixed two decimals gives 0.03, which is one digit, and for 24.09 it gives
    four.

    Above 100 the two digits cannot be written in plain decimal, since 2600
    reads as four digits while carrying two, so both numbers are divided by
    the uncertainty's own decade. A bare integer ending in zero is ambiguous
    the same way and takes the same route: 24 says two digits, 10 does not.

    Checked against 20000 random pairs spanning fourteen decades, every one
    printing exactly two significant digits on the uncertainty with the value
    on the same decimal place.
    """
    if err is None or not math.isfinite(err) or err <= 0:
        # 8a.1 admits a value with no uncertainty only alongside an explicit
        # statement of why. Printing the bare number was the silent form of
        # exactly the fault this convention exists to prevent, and a
        # non-finite error is a real fit failure rather than a hypothetical.
        why = "uncertainty not returned by the fit"
        if err is not None and math.isfinite(err) and err == 0:
            why = "uncertainty returned as zero"
        return f"{value:g}{(' ' + unit) if unit else ''} ({why})"

    exp = math.floor(math.log10(abs(err)))
    dp = -(exp - 1)
    err_r = round(err, dp)
    if err_r > 0 and math.floor(math.log10(abs(err_r))) != exp:
        exp = math.floor(math.log10(abs(err_r)))
        dp = -(exp - 1)
        err_r = round(err, dp)

    tail = f" {unit}" if unit else ""
    # A negative value that rounds to zero printed "-0.000", a minus sign on
    # a quantity the same row calls consistent with zero.
    if value < 0 and abs(value) < 0.5 * 10.0 ** (-dp):
        value = 0.0
    # Plain decimal only where it is both unambiguous and readable.
    #
    # It is AMBIGUOUS when the uncertainty is a bare integer ending in zero,
    # since 2600 reads as four significant digits while carrying two, and 10
    # cannot say whether it carries one or two while 24 can.
    #
    # It is UNREADABLE once the pair needs leading zeros to reach its digits.
    # 0.000026 +/- 0.000034 spends four characters per number saying nothing,
    # and the convention everywhere in this field is to factor the decade out
    # instead. The scale is taken from max(|value|, err) rather than from the
    # value, because a value consistent with zero carries no scale of its own.
    # Leading zeros appear only when BOTH numbers are small, so the small
    # test uses the larger of the two. There is deliberately no matching
    # large test: a big value with a small error, 1000000.00 +/- 0.50, is
    # perfectly readable in plain decimal, and an earlier `magnitude >= 1e5`
    # clause sent exactly that case into the decade form while the scale
    # still came from the uncertainty, printing (10000000.0 +/- 5.0) x 10^-1.
    # The genuinely large case is the ambiguity test below, not a magnitude.
    magnitude = max(abs(value), err_r)
    unreadable = magnitude < 1e-3
    ambiguous = dp <= 0 and round(err_r) % 10 == 0
    if not unreadable and not ambiguous and dp >= 0:
        return f"{value:.{dp}f} ± {err_r:.{dp}f}{tail}"
    scale = 10.0 ** exp
    return (f"({value / scale:.1f} ± {err_r / scale:.1f})"
            r"$\,\times\,10^{" f"{exp}" r"}$" f"{tail}")


def bound(value, dp=2, kind="upper", unit=""):
    """Format a one-sided bound, rounding AWAY from the allowed region.

    Protocol 8a.3. An upper limit rounds UP and a lower limit rounds DOWN,
    always, because rounding toward the excluded region silently tightens
    the claim.

    This exists because a plain `:.2f` did exactly that on 2026-08-13:
    the record's 95 per cent upper bound on the AC-Stark coefficient is
    0.963 MHz/W and the figure printed "< 0.96", which claims a tighter
    limit than the data support. The direction of that error is the one
    this whole record is built on not making.
    """
    scale = 10.0 ** dp
    if kind == "upper":
        rounded = math.ceil(value * scale - 1e-9) / scale
    else:
        rounded = math.floor(value * scale + 1e-9) / scale
    tail = f" {unit}" if unit else ""
    sign = "<" if kind == "upper" else ">"
    return f"{sign} {rounded:.{dp}f}{tail}"


def pm_row(name, value, err, unit=""):
    """One parameter-box row, marking a quantity the fit does not resolve.

    When the magnitude of a fitted value is below twice its own uncertainty
    the fit has not separated it from zero, and printing a central value to
    two significant digits invites the reader to treat it as measured. This
    record's whole argument is that a number the data do not identify is not
    reported as though it were, so the row says so where it is true.
    """
    text = f"  {name} = {pm(value, err, unit)}"
    if err and math.isfinite(err) and err > 0 and abs(value) < 2.0 * err:
        text += ", consistent with zero"
    return text


def _footer_rect(fig):
    """The tight_layout rect that keeps the axes off the source footer.

    MEASURED, NOT GUESSED, per protocol 12.9: the footer's height depends on
    whether the source list wrapped to a second line, so a constant reserve is
    right for one figure and wrong for the next. This renders once, takes the
    footer's actual top edge in figure coordinates, and adds one footer-height
    of padding.

    WHY IT IS A DEFAULT AND NOT A PER-FIGURE ARGUMENT. This function's own
    docstring used to say that a figure whose axis label would land on the
    footer "reserves the bottom strip explicitly (fig3 does)", which is the
    class of defect fixed on one instance. On 2026-08-13 the new footer
    collision guard found twelve overlaps across eight figures, the worst
    printing an axis label straight through the source line at 78 per cent
    coverage. Every one of them was a figure that had not been told to
    reserve. So the reserve is computed for every figure that carries a
    footer, and an explicit rect from the caller still wins.
    """
    texts = [t for t in fig.texts if t.get_text().strip()]
    if not texts:
        return None
    foot = min(texts, key=lambda t: (t.get_position()[1], t.get_position()[0]))
    r = _renderer(fig)
    bb = foot.get_window_extent(renderer=r).transformed(
        fig.transFigure.inverted())
    return (0.0, min(0.30, bb.y1 + bb.height), 1.0, 1.0)


def _layout(fig, rect=None):
    """Apply the shipping layout to a figure, without saving it.

    SPLIT OUT OF _save ON 2026-08-13, and the reason matters more than the
    refactor. The canvas guards capture figures by stubbing _save, and the
    stub only recorded the figure: it never ran tight_layout. So every one of
    those guards was measuring a PRE-LAYOUT figure while the shipped PNG is a
    laid-out one, which is the same class of defect as measuring the right
    thing on the wrong quantity. The stub now calls this function, so the
    guards and the saved file see identical geometry by construction."""
    measured = _footer_rect(fig)
    if rect is None:
        rect = measured
    elif measured is not None:
        # A CALLER'S RECT NEVER SHRINKS THE MEASURED RESERVE. The hand-set
        # rects predate this measurement and were chosen by eye: fig8 asked
        # for 0.03 of the canvas when its two-line footer needs more, and its
        # x-axis label printed straight through the source line at 78 per
        # cent coverage. So the caller keeps its left, right and top, which
        # it may have set for reasons of its own, and the bottom becomes
        # whichever of the two is larger.
        rect = (rect[0], max(rect[1], measured[1]), rect[2], rect[3])
    fig.tight_layout(rect=rect)
    _lift_off_the_footer(fig)


def _lift_off_the_footer(fig):
    """After tight_layout, move anything still sitting on the footer.

    tight_layout cannot help two cases, and both exist here. A figure with
    manually positioned axes is skipped by the layout engine entirely, which
    matplotlib says out loud in a warning nobody was reading: fig8 pins its
    axes at y0 = 0.12 while its two-line footer reaches 0.0587 and its x-axis
    label ran from 0.0353, printing the words "scan time (ms)" straight
    through the source line. And a figure-level caption is not an axes at all,
    so no rect moves it.

    So this measures what remains and moves it, by the SMALLEST amount that
    clears: every axes lifts by one shortfall, uniformly, because lifting one
    panel of a row would misalign the row; a fig-level text lifts on its own,
    since it has no neighbours to stay level with.
    """
    texts = [t for t in fig.texts if t.get_text().strip()]
    if not texts or not fig.axes:
        return
    r = _renderer(fig)
    inv = fig.transFigure.inverted()
    foot = min(texts, key=lambda t: (t.get_position()[1], t.get_position()[0]))
    top = foot.get_window_extent(renderer=r).transformed(inv).y1
    pad = 0.012

    need = 0.0
    for ax in fig.axes:
        lab = ax.xaxis.label
        if lab.get_text().strip():
            y0 = lab.get_window_extent(renderer=r).transformed(inv).y0
            need = max(need, top + pad - y0)
    if need > 1e-4:
        for ax in fig.axes:
            b = ax.get_position()
            ax.set_position([b.x0, b.y0 + need, b.width,
                             max(0.05, b.height - need)])

    r = _renderer(fig)
    for t in texts:
        if t is foot:
            continue
        b = t.get_window_extent(renderer=r).transformed(inv)
        if b.y0 < top + pad and b.y1 > foot.get_window_extent(
                renderer=r).transformed(inv).y0:
            x, y = t.get_position()
            t.set_position((x, y + (top + pad - b.y0)))


def _save(fig, name, rect=None):
    """The shipping layout, then savefig with the data fingerprint embedded.

    The footer is drawn with fig.text, which the layout engine cannot see, so
    the bottom strip is reserved for it. That reserve is COMPUTED for every
    figure by _footer_rect rather than passed by hand for the few that were
    noticed; an explicit rect from the caller still overrides."""
    _layout(fig, rect)
    fig.savefig(FIG / name, metadata={"DataFingerprint": _DATA_FP})
    plt.close(fig)


def _footer(fig, text, y=0.012, fontsize=6.3):
    """The one footer line every figure carries: what CSVs/modules it is
    drawn from, and the exact command that regenerates it -- so a reader who
    doubts a number knows where it came from and how to rebuild it. One call
    site so the position/size stays identical figure to figure.

    verticalalignment="bottom" so a two-line footer (a wide multi-panel
    figure's source list can outrun one line) grows UPWARD from y instead of
    the default baseline anchoring, which would push a second line below the
    figure's bottom edge and off the canvas."""
    fig.text(0.01, y, text, fontsize=fontsize, color="0.35", va="bottom")


# Okabe-Ito (colorblind-safe), fixed order for the four peaks
PEAK_COLOR = {"4121": "#0072B2", "4154": "#D55E00", "4192": "#009E73", "4207": "#E69F00"}
# "F1" read as a label code rather than a quantum number, so the hyperfine
# level is written out. Every figure here draws it through PEAK_LABEL, and
# scripts/make_fig0_spectrum.py carries the one other copy, kept identical.
_ISO = {"4121": "$^{87}$Rb F = 1", "4154": "$^{85}$Rb F = 2",
        "4192": "$^{85}$Rb F = 3", "4207": "$^{87}$Rb F = 2"}
PEAK_LABEL = {k: f"993.{k} nm ({_ISO[k]})" for k in PEAK_COLOR}
plt.rcParams.update({"figure.dpi": 130, "font.size": 10, "axes.grid": True,
                     "grid.alpha": 0.25, "axes.axisbelow": True, "legend.frameon": False})

# The results CSVs tag every quantity with an ALL-CAPS provenance code (see
# rb5s6s/constants.py's house rules). Those codes are useful in a CSV column
# but read as pipeline jargon on a figure, so anywhere a status is worth
# stating on-figure it goes through this plain-English map instead (or is
# dropped to the footer).
STATUS_WORD = {"PRELIM": "preliminary", "BOUND": "a bound, not a measurement",
               "MEASURED-HERE": "measured directly", "ESTABLISHED": "an established value",
               "ENVELOPE": "an order-of-magnitude envelope", "OPEN": "not yet resolved",
               "DIAGNOSTIC": "a diagnostic", "ARTIFACT": "a known artifact",
               "CALIB": "a calibration"}


# Windows with fewer contributing traces than this cannot test the linearity
# bound -- their errors exceed it. Split point for fig8's right panel.
N_WELL_SAMPLED = 19

# The sweep-linearity bound quoted for the ruler: no well-sampled window's
# local rate departs from its block rate by more than this fraction (the
# largest departure is 0.25%). tests/test_ruler.py pins it against
# results/ruler_nlmap.csv, and fig8's band and title both read it from here.
RULER_LINEARITY_BOUND = 0.003

# Reduced-chi-squared ceiling for the ruler trace fig8 displays. Fixed in
# docs/notes/ruler_validity_and_trim_prereg.md section 7 before the code
# existed, alongside the rest of the eligibility rule below.
RULER_FIG_CHI2_MAX = 2.0

# The seven fitted tooth heights, in slot order, as results/ruler_traces.csv
# names them. Persisted for the first time by the validity work of 2026-08-04:
# until then every run recomputed them and threw them away.
RULER_HEIGHT_COLS = ("h_m3", "h_m2", "h_m1", "h_0", "h_p1", "h_p2", "h_p3")

# fig19's density lever, fourth point: the 130 C power-sweep session's 225 mW
# block. Exactly the selection scripts/run_beta_self.py's width_vs_density_probe
# makes for the headline bound, named here so the panel and the producer cannot
# drift apart silently.
BETA_ANCHOR_130 = ("225", 130.0)

# The morning pilot's oven label is a variac set point and not a cell reading,
# so its density is a range rather than a value: addendum 17 of
# docs/PREREGISTRATION_RESULTS.md puts the internal temperature at 110 to
# 130 C. fig19 draws the pilot at the upper end, which is the reading the
# addendum's verdict rests on, with the bar running down to the lower one.
PILOT_T_RANGE_C = (110.0, 130.0)


def _rows(name):
    return list(csv.DictReader(open(C.RESULTS_DIR / f"{name}.csv")))


def _temperature_top_axis(ax, ticks):
    """A cell-temperature axis across the top of a density plot.

    The density axis is the physical one (a collisional rate multiplies N),
    but every condition in the dataset is named by its oven temperature, so
    a reader needs both. fig1 and fig6 share this mapping."""
    T_grid = np.linspace(55.0, 140.0, 4000)
    N_grid = density_units(T_grid)

    def N_to_T(N):
        return np.interp(N, N_grid, T_grid)

    def T_to_N(T):
        # matplotlib probes the secondary axis's own default view (e.g. the
        # [0, 1] Axes default) while wiring up the scale, before any real
        # limits are set, so clip into the liquid-phase-valid band and keep
        # that probe away from density_units' melting-point guard.
        return density_units(np.clip(np.asarray(T, float), 55.0, 140.0))

    sec = ax.secondary_xaxis("top", functions=(N_to_T, T_to_N))
    if ticks is not None:
        # the parent axis is log, so the secondary inherits a log locator and
        # formatter: pin the ticks to the dataset's own oven settings and
        # write them as plain degrees.
        sec.set_xticks(list(ticks))
        sec.set_xticklabels([f"{T:g}" for T in ticks])
        sec.minorticks_off()
    return sec


def fig_width_vs_density():
    """C1: total line FWHM against density, one series per peak.

    Both axes are named: density on the bottom because a collisional rate
    multiplies N, cell temperature on the top because that is what the
    dataset's conditions are called. The 130 C column is the power sweep's
    225 mW anchor (`serves_t130`), and the spread of the other four powers
    at that same density is drawn behind it, so the reader sees the width
    that one curated choice carries.

    The headline claim is the one the four points support: the widths rise,
    and they rise by a few percent while the density rises fifty-three fold,
    which is why the self-broadening coefficient comes out of this dataset as
    a bound. The earlier title claimed non-monotonicity, which the error bars
    do not support (every downward step is at or below 1 sigma)."""
    rows = _rows("linefit_conditions")
    fig, ax = plt.subplots(figsize=(7.8, 5.3))
    N130 = density_units(130.0)
    _series = {}
    for peak in ("4121", "4154", "4192", "4207"):
        pts, p130 = [], []
        for r in rows:
            if r["peak"] != peak:
                continue
            if r["role"] == "p_sweep":
                p130.append(float(r["total_fwhm"]))
                if r["P"] != "225":
                    continue
                T = 130.0
            elif r["role"] == "t_sweep":
                T = float(r["T"])
            else:
                continue
            pts.append((density_units(T), float(r["total_fwhm"]),
                        float(r["total_fwhm_err"])))
        if not pts:
            continue
        pts.sort()
        N, W, We = zip(*pts)
        # the five-power spread at 130 C, drawn behind the anchor point
        if p130:
            ax.plot([N130, N130], [min(p130), max(p130)], "-",
                    color=PEAK_COLOR[peak], lw=4, alpha=0.16,
                    solid_capstyle="butt", zorder=1)
        # Markers only. Nothing was measured between the four conditions, so a
        # joining line would draw a trend the dataset does not have: the eye
        # reads the segment slopes as rates. Colour carries the series.
        ax.errorbar(N, W, yerr=We, fmt="o", color=PEAK_COLOR[peak],
                    label=PEAK_LABEL[peak], ms=5, capsize=2, lw=1.3, zorder=3)
        _series[peak] = (np.array(N), np.array(W), np.array(We))
    # THE MODEL THE RECORD FITS, drawn over the data it was fitted to
    # (2026-08-12, experimenter audit: this figure showed data with no model on it).
    # One shared collisional slope with a floor per line is the construction
    # the headline bound comes from (results/beta_self_probe.csv, the pooled
    # row), so that is the line to draw: slope from the CSV, floor re-anchored
    # per line at draw time, testing the slope claim only, exactly as fig2's
    # flat lines test only the shape.
    _bpool = next(float(r["beta_eff"]) for r in _rows("beta_self_probe")
                  if r["peak"] == "pooled_slope")
    _ngrid = np.linspace(0.4, 33.0, 60)
    for _i, (_pk, (_N, _W, _We)) in enumerate(sorted(_series.items())):
        _off = float(np.sum((_W - _bpool * _N) / _We ** 2)
                     / np.sum(1.0 / _We ** 2))
        ax.plot(_ngrid, _off + _bpool * _ngrid, "--", color=PEAK_COLOR[_pk],
                lw=1.0, zorder=2,
                label="the pooled fit behind the bound: one\n"
                      "shared slope, floor per line" if _i == 0 else None)
    ax.set_xscale("log")
    ax.set_ylim(4.36, 5.95)
    ax.set_xticks([density_units(T) for T in (70.0, 90.0, 110.0, 130.0)])
    ax.set_xticklabels(["0.56", "2.4", "9.1", "29"])
    ax.minorticks_off()
    # The axis is a quantity and a unit. The 20 percent density-scale
    # systematic and the logarithmic scale were written into the label and are
    # now the caption's business: the scale is legible from the ticks, and a
    # systematic is not part of a quantity's name.
    ax.set_xlabel(r"Rb density $N$  ($10^{12}\,\mathrm{cm^{-3}}$)")
    ax.set_ylabel("total FWHM (MHz)")
    sec = _temperature_top_axis(ax, (70.0, 90.0, 110.0, 130.0))
    sec.set_xlabel("cell temperature (°C)", fontsize=9.5)
    sec.tick_params(labelsize=8.5)
    ax.legend(fontsize=8, ncol=2, loc="upper left", framealpha=0.95,
              frameon=True)
    fig.suptitle("Total FWHM against Rb density, four hyperfine components",
                 fontsize=12, y=0.968)
    _footer(fig, "Sources: results/linefit_conditions.csv, with the density from "
                 "rb5s6s/density.py (Nesmeyanov, 20% scale systematic). "
                 "Regenerate: python scripts/make_figures.py.")
    _save(fig, "fig1_width_vs_density.png")


def fig_power_sweep():
    """C3: FWHM shows no power trend; amplitude ~ P^2.

    The observed FWHM spread (3-8%) EXCEEDS the <=2% the ramp law predicts,
    so the title must not present the prediction as the observation -- it is
    between-block scatter, and no peak keeps a significant slope once that
    over-dispersion is absorbed. The panel computes and prints both numbers
    at draw time (the spread and the worst slope significance), so this
    docstring carries no second copy of either. Titling this "flat" read
    as a claim the plotted points do not support."""
    rows = _rows("power_sweep")
    by = defaultdict(list)
    for r in rows:
        by[r["peak"]].append((int(r["power_mW"]), float(r["fwhm"]), float(r["fwhm_err"]),
                              float(r["amp"]), float(r["amp_err"])))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.5, 4.7))
    fig.subplots_adjust(top=0.80, bottom=0.12)
    for peak in ("4121", "4154", "4192", "4207"):
        d = sorted(by[peak]); P = [x[0] for x in d]
        # Markers only on the left panel. Five powers is a sparse sampling of a
        # continuous variable, and the joining segments drew a rise-and-fall
        # shape between them that the panel's own title denies.
        a1.errorbar(P, [x[1] for x in d], yerr=[x[2] for x in d], fmt="o",
                    color=PEAK_COLOR[peak], label=PEAK_LABEL[peak], ms=4, lw=1.3, capsize=2)
        a2.errorbar(P, [x[3] for x in d], yerr=[x[4] for x in d], fmt="o",
                    color=PEAK_COLOR[peak], ms=4, capsize=2)
    # THE MODEL'S OWN PREDICTION, drawn rather than only asserted (2026-08-12,
    # experimenter reading of the outbound note built from this figure: the left panel
    # carried data and a caption claiming the ramp law, with nothing of the law
    # on the canvas). Two objects, because the fit and the bound are different
    # claims. The fitted model has S0 railed at ZERO (S0_225mW_fit in the
    # committed CSV), so its prediction is a FLAT line at each peak's
    # weighted-mean width: that is the fit, offset fitted, testing only the
    # shape exactly as panel (b)'s slope-2 reference tests only the exponent.
    # The grey envelope above the pooled mean is the ramp increment at the
    # committed 95 per cent PROFILE bound on S0: the largest ramp the data
    # allow, not an expectation. Both computed at draw time from rb5s6s.stark
    # and the committed CSV, never typed (protocol 12.9).
    #
    # ROW DISCIPLINE, learned here: a first version selected the quantity
    # "S0_225mW_ub95", which is the REPLACED Wald diagnostic at 2.205 MHz and
    # says "quote the profile row instead" in its own unit field. The quoted
    # construction is S0_225mW_ub95_profile, 0.632 MHz, status BOUND. Filter
    # on the status column, which exists for exactly this.
    from rb5s6s import stark as _stark
    _s0_ub = next(float(x["value"]) for x in _rows("stark_sweep")
                  if x["quantity"] == "S0_225mW_ub95_profile"
                  and x["key"] == "shared" and x["status"].lower() == "bound")
    _gc, _sl, _tr = 0.60, 1.50, 0.96
    _nu = np.arange(-45.0, 45.0, 0.01)
    _pgrid = np.linspace(20.0, 230.0, 22)
    _base = _stark._fwhm_of(_gc, _sl, _tr, 0.0, _nu)
    _inc = np.array([_stark._fwhm_of(_gc, _sl, _tr, _s0_ub * p / 225.0, _nu)
                     for p in _pgrid]) - _base
    # THE WANDER IS BETWEEN-BLOCK SCATTER, AND THE PANEL NOW SAYS SO
    # (2026-08-12, experimenter reading: the points move by more than their bars, so
    # the flat model looked contradicted). The bars are repeat scatter within
    # a block; each power is its own block, re-centred by hand after lock
    # dropouts, and that between-block motion is not in the bars. Two objects
    # carry the adjudication on the canvas rather than in a docstring: a band
    # of the pooled fractional between-block scatter around each flat line,
    # and the worst per-peak slope significance once that over-dispersion is
    # absorbed, computed here at draw time.
    # Both numbers on the canvas are the LEDGER'S OWN metrics (RESULTS C3a),
    # recomputed here at draw time rather than restated: the observed spread
    # is each peak's max-minus-min over the five power blocks as a fraction of
    # its mean, quoted as the range across peaks, and the slope test inflates
    # the slope error by the flat model's own over-dispersion (the PDG scale
    # factor, the record's treatment elsewhere), which is what "absorbed"
    # means. A first version computed a pooled RMS and a line-model inflation
    # instead, which gave 1.9 per cent and 2.5 sigma beside a ledger that says
    # 3 to 8 and 1.7: not wrong, just DIFFERENT metrics wearing the same
    # words, which is the drift the canonical-number rule exists to stop.
    _wbars, _spreads, _tworst, _rms_p = [], [], 0.0, []
    for peak in ("4121", "4154", "4192", "4207"):
        d = sorted(by[peak])
        Pv = np.array([x[0] for x in d], float)
        w = np.array([x[1] for x in d]); e = np.array([x[2] for x in d])
        Wt = 1.0 / e ** 2
        wbar = float(np.sum(w * Wt) / np.sum(Wt))
        _wbars.append(wbar)
        _spreads.append((w.max() - w.min()) / wbar)
        _rms_p.append(float(np.sqrt(np.mean((w - wbar) ** 2))))
        chi2r_flat = float(np.sum(Wt * (w - wbar) ** 2) / (w.size - 1))
        xm = np.sum(Wt * Pv) / np.sum(Wt); ym = np.sum(Wt * w) / np.sum(Wt)
        bslope = float(np.sum(Wt * (Pv - xm) * (w - ym))
                       / np.sum(Wt * (Pv - xm) ** 2))
        sb = float(np.sqrt(1.0 / np.sum(Wt * (Pv - xm) ** 2)))
        _tworst = max(_tworst, abs(bslope) / (sb * np.sqrt(max(chi2r_flat, 1.0))))
    for i, (peak, wbar, rms) in enumerate(zip(("4121", "4154", "4192", "4207"),
                                              _wbars, _rms_p)):
        a1.plot([_pgrid[0], _pgrid[-1]], [wbar, wbar], "--",
                color=PEAK_COLOR[peak], lw=1.0,
                label="fitted model, flat because $S_0$\n"
                      "rails at zero (offset fitted)" if i == 0 else None)
        a1.fill_between(_pgrid, wbar - rms, wbar + rms,
                        color=PEAK_COLOR[peak], alpha=0.08, lw=0,
                        label="between-block scatter, the part\n"
                              "the per-point bars do not carry"
                        if i == 0 else None)
    _wm = float(np.mean(_wbars))
    a1.fill_between(_pgrid, _wm, _wm + _inc, color="0.55", alpha=0.25, lw=0,
                    label="ramp increment allowed at the\n"
                          r"95% bound on $S_0$ (over the mean)")
    a1.text(0.03, 0.97,
            f"observed spread {100 * min(_spreads):.0f}\u2013"
            f"{100 * max(_spreads):.0f}% across the five blocks.\n"
            "worst per-peak slope, with that\n"
            f"over-dispersion absorbed: {_tworst:.1f}$\\sigma$",
            transform=a1.transAxes, fontsize=7.4, color="0.30", va="top")
    # HEADROOM FOR THAT TEXT, measured rather than guessed. The block is
    # anchored at axes-fraction 0.97 with no ylim set, so the axes autoscaled
    # to the data and the 993.4154 nm error bar at 25 mW (5.4927 +/- 0.0785,
    # so reaching 5.571) ran straight through the first line of it. Pixel
    # inspection of the shipped PNG on 2026-08-14 found the whisker occupying
    # the same pixels as all three lines of the annotation. Three text lines at
    # 7.4 pt need roughly a fifth of this panel, so the top limit is lifted to
    # clear them instead of moving the text somewhere the data may grow into.
    _ylo, _yhi = a1.get_ylim()
    a1.set_ylim(_ylo, _yhi + 0.26 * (_yhi - _ylo))
    a1.legend(fontsize=8, loc="lower right")
    a1.set_xlabel("power (mW)")
    # Estimator named on the axis: this panel's widths are the raw
    # half-maximum widths of results/power_sweep.csv, averaged over repeats.
    # fig10's right panel plots the fitted total width of the joint
    # per-condition lineshape fit, which runs systematically higher, and an
    # unlabelled "FWHM" on both invites the reader to compare them directly.
    a1.set_ylabel("measured FWHM (MHz)")
    a1.set_title("(a) measured FWHM against drive power", fontsize=9)
    # amplitude log-log: a slope-2 REFERENCE anchored to each peak's own data,
    # so the guide tracks the points instead of floating beside them. The slope
    # is held at 2 and only the offset is fitted, so the line cannot test the
    # exponent and is labelled as a reference rather than a fit. Drawn over the
    # campaign's own measured power range, not a fixed guess.
    a2.set_xscale("log"); a2.set_yscale("log")
    P_all = np.array(sorted({x[0] for v in by.values() for x in v}), float)
    Pline = np.array([P_all.min(), P_all.max()])
    for i, peak in enumerate(("4121", "4154", "4192", "4207")):
        d = sorted(by[peak])
        P = np.array([x[0] for x in d], float)
        A = np.array([x[3] for x in d], float)
        logk = np.mean(np.log10(A) - 2.0 * np.log10(P))  # least-squares slope-2 intercept
        # Three short lines, not two long ones: the first line used to run past
        # the right spine and the brightest series was drawn through its words.
        a2.plot(Pline, 10 ** logk * Pline ** 2, "--", color=PEAK_COLOR[peak], lw=1.0,
                label="square-of-power reference,\noffset fitted"
                if i == 0 else None)
    a2.set_xlabel("power (mW)"); a2.set_ylabel("peak fluorescence signal (V)")
    a2.set_title("(b) peak fluorescence signal against drive power", fontsize=9)
    a2.legend(fontsize=8)
    fig.suptitle("Measured FWHM and peak signal against drive power",
                 fontsize=9.5, y=0.975)
    _footer(fig, "Source: results/power_sweep.csv. Regenerate: python scripts/make_figures.py.")
    _save(fig, "fig2_power_sweep.png")


def fig_transit_mc():
    """M9: transit contribution vs w0 with the laser-narrow crossover.

    The crossover w0 (where natural-convolved-transit reaches the observed
    total) is COMPUTED from the plotted (w0, nat_conv_transit) points against
    the reference OBSERVED total imported from run_transit_mc.py -- not typed
    in -- so a change to either side of that comparison cannot leave the
    title's claim stale (an earlier version stated "18-20 um" here, from
    before the 2026-07-12 flux-factor fix; the corrected data cross near
    39 um, matching run_transit_mc.py's own "w0 ~< 40 um" narrative)."""
    sys.path.insert(0, str(C.REPO_ROOT / "scripts"))
    from run_transit_mc import OBSERVED

    rows = [r for r in _rows("transit_mc") if r["collection"] == "thin"]
    w0 = np.array([float(r["w0_um"]) for r in rows])
    natx = np.array([float(r["nat_conv_transit"]) for r in rows])
    natx_err = [float(r["nat_conv_transit_err"]) for r in rows]
    order = np.argsort(w0)
    w0_s, natx_s = w0[order], natx[order]
    # natx is decreasing in w0 over the covered range, so np.interp needs an
    # increasing x -- feed it reversed (natx descending -> ascending flip).
    w0_cross = float(np.interp(OBSERVED, natx_s[::-1], w0_s[::-1]))
    # The rounded waist the excluded region used to be quoted at in the title
    # (about 40 um, the spacing of the two sampled waists that bracket the
    # crossing) is a claim about the geometry, so it lives in the caption now.
    # The shading stays at the computed crossing.

    # Taller than the panel needs, because the legend is drawn in the strip
    # under the axes rather than inside them.
    fig, ax = plt.subplots(figsize=(6, 5.3))
    ax.errorbar(w0, natx, yerr=natx_err, fmt="-o", color="#0072B2", ms=5, lw=1.6,
                capsize=2,
                label="natural FWHM convolved with the\ntransit-time distribution")
    ax.axhline(OBSERVED, ls="--", color="#D55E00", lw=1.3,
               label=f"observed total FWHM, {OBSERVED:.2f} MHz")
    ax.axhline(GNAT, ls=":", color="0.4", lw=1,
               label=f"natural FWHM, {GNAT:.2f} MHz")
    # shade the laser-narrow region: where nat(x)transit >= observed, i.e.
    # up to the computed crossover (not the leftmost data point -- the old
    # version capped the shading at min(w0), under-covering the region
    # between it and the true crossover).
    ax.fill_between([min(w0.min(), w0_cross) - 8.0, w0_cross], GNAT, 6.0,
                    color="#009E73", alpha=0.10)
    ax.set_xlabel("beam waist (µm)")
    ax.set_ylabel("predicted FWHM (MHz)")
    ax.set_title("Predicted FWHM against beam waist", fontsize=8.5)
    # Under the axes, not inside them: the curve falls across the whole width,
    # so a legend at any right-hand anchor lands on the points and on one of
    # their error bars (it sat on the 50 to 52 um pair).
    ax.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.13),
              ncol=2, borderaxespad=0.0)
    _footer(fig, "Source: results/transit_mc.csv (rb5s6s.transit_mc) +\n"
                 "scripts/run_transit_mc.py (reference level). Regenerate: "
                 "python scripts/run_transit_mc.py && python scripts/make_figures.py.",
            fontsize=5.7)
    _save(fig, "fig3_transit_mc.png", rect=(0, 0.07, 1, 1))


def fig_amplitude_ratios():
    """M10: within-isotope area ratios vs the parameter-free degeneracy law."""
    from fractions import Fraction
    rows = _rows("amplitude_ratios")
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    # colour = the NUMERATOR peak's own PEAK_COLOR entry (same registry every
    # other figure uses, not an independently hard-coded hex duplicate);
    # predicted value read from the CSV's own "predicted" column (the
    # (2F+1) statistical-weight ratio computed by run_amplitude_ratios.py),
    # not retyped here.
    keys = {"4207/4121": "993.4207 / 993.4121 nm ($^{87}$Rb, F = 2 over F = 1)",
            "4192/4154": "993.4192 / 993.4154 nm ($^{85}$Rb, F = 3 over F = 2)"}
    for key, lab in keys.items():
        col = PEAK_COLOR[key.split("/")[0]]
        d = [(float(r["T"]), float(r["measured"]), float(r["err_total"]), float(r["predicted"]))
             for r in rows if r["ratio"] == key]
        # err_total = stat (SEM) + between-block drift systematic, in quadrature
        # (the total bar; the stat-only column is a labelled diagnostic). See
        # run_amplitude_ratios.py and review finding 5, 2026-07-16.
        d.sort()
        if not d:
            continue
        T, m, e, pr = zip(*d)
        pred = pr[0]
        # Markers only. Four oven settings are a sparse sampling, and the
        # joining segments read as a temperature dependence of the ratio,
        # which is exactly what the title says these bars cannot test.
        ax.errorbar(T, m, yerr=e, fmt="o", color=col, ms=5, lw=1.3, capsize=2, label=lab)
        ax.axhline(pred, ls="--", color=col, lw=1)
        frac = Fraction(pred).limit_denominator(12)
        ax.annotate(f"predicted ratio {frac.numerator}/{frac.denominator}",
                    (128, pred + (0.03 if pred > 1.5 else -0.10)),
                    fontsize=8, color=col, ha="right")
    ax.set_xlabel("cell temperature (°C)")
    ax.set_ylabel("ratio of fitted line areas")
    ax.set_title("Ratio of fitted line areas against cell temperature, with the "
                 "statistical-weight predictions", fontsize=8.7)
    ax.legend(fontsize=8)
    _footer(fig, "Source: results/amplitude_ratios.csv. Regenerate: "
                 "python scripts/run_amplitude_ratios.py && python scripts/make_figures.py.")
    _save(fig, "fig4_amplitude_ratios.png")


def fig_pooled_width():
    """fig5: the four ΔF=0 components share ONE
    width budget — β_85 = β_87 was TESTED equal in the joint fit, which is what
    LICENSES pooling (equality tested first, then pool; not the reverse). So the
    pooled width vs density is a clean trend where the individual components are
    statistics-limited and non-monotonic. Companion panel: the shared σ_laser(T)
    is NOT flat — the residual drift systematic, shown not hidden. This is
    PRECISION not accuracy: still a BOUND, because the common-mode time-drift
    survives pooling (only the fixed-lock session's opposite-order grid decontaminates)."""
    rows = _rows("linefit_conditions")

    def width(peak, T):
        role = "p_sweep" if T == 130 else "t_sweep"
        for r in rows:
            if (r["peak"] == peak and r["role"] == role and int(float(r["T"])) == T
                    and (r["P"] == "225" or role == "t_sweep")):
                return float(r["total_fwhm"])
        return None

    Ts = (70, 90, 110, 130)
    peaks = ("4121", "4154", "4192", "4207")
    N = [density_units(float(T)) for T in Ts]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.8, 4.3))
    # panel A: individual components (faint) + pooled mean (bold) vs density
    for peak in peaks:
        w = [width(peak, T) for T in Ts]
        a1.plot(N, w, "-o", color=PEAK_COLOR[peak], alpha=0.30, ms=3, lw=0.9)
    pooled = [np.mean([width(p, T) for p in peaks]) for T in Ts]
    perr = [np.std([width(p, T) for p in peaks], ddof=1) / 2.0 for T in Ts]
    a1.errorbar(N, pooled, yerr=perr, fmt="-o", color="k", ms=6, lw=2.0, capsize=3,
                label="mean of the four peaks, with the standard error of that mean",
                zorder=5)
    # split-independent lever check (M4d): if the short-lever joint beta were a
    # real linear collision rate, the TOTAL width must grow by at least
    # 0.5346*beta*dN (minimum Voigt slope dW/dgamma_L >= 0.5346, sigma_laser
    # held flat -- and the measured widths already include some laser-width
    # growth, so the comparison is conservative). The pooled growth falls
    # short at the 130 C point -> beta is a lever-dependent BOUND.
    dfp = C.RESULTS_DIR / "lever_crosscheck.csv"
    if dfp.exists():
        dfr = list(csv.DictReader(open(dfp)))
        bhead = np.mean([float(r["value"]) for r in dfr
                         if r["quantity"] == "beta_crosscheck"])
        Nf = np.geomspace(N[0], N[-1], 200)
        vslope = 0.5346          # the minimum Voigt slope quoted above
        a1.plot(Nf, pooled[0] + vslope * bhead * (Nf - N[0]), "--", color="0.35",
                lw=1.4, label=("lower bound on the total-FWHM growth for a\n"
                               "coefficient of %.3f MHz per "
                               r"$10^{12}$cm$^{-3}$"
                               "\nat the smallest Voigt slope, %.2f") % (bhead, vslope))
    # The two isotopes' coefficients, with their uncertainties, read from
    # results/global_fit.csv: the title's agreement claim is about these two
    # numbers, so they are printed here rather than only asserted.
    iso = {r["key"]: (float(r["value"]), float(r["err"])) for r in _rows("global_fit")
           if r["quantity"] == "beta_self"}
    if {"85Rb", "87Rb"} <= set(iso):
        lo, hi = a1.get_ylim()          # a clear strip under the data for it
        a1.set_ylim(lo - 0.20 * (hi - lo), hi)
        a1.text(0.03, 0.03,
                r"$\beta$($^{85}$Rb) = %.4f $\pm$ %.4f,   "
                r"$\beta$($^{87}$Rb) = %.4f $\pm$ %.4f"
                "\n" r"MHz per $10^{12}$cm$^{-3}$ (joint fit)"
                % (iso["85Rb"][0], iso["85Rb"][1], iso["87Rb"][0], iso["87Rb"][1]),
                transform=a1.transAxes, ha="left", va="bottom", fontsize=7,
                color="0.3")
    a1.set_xscale("log")
    a1.set_xlabel(r"Rb density $N$  ($10^{12}\,\mathrm{cm^{-3}}$)")
    a1.set_ylabel("total FWHM (MHz)")
    a1.set_title("(a) total FWHM against Rb density, the four components "
                 "and their mean", fontsize=8)
    a1.legend(fontsize=7.5, loc="upper left", frameon=True, framealpha=1.0)
    # panel B: σ_laser(T) is MODEL-DEPENDENT -> the "anomaly" is degeneracy, not drift
    gf = _rows("global_fit")
    sl = sorted((float(r["key"][:-1]), float(r["value"]), float(r["err"]))
                for r in gf if r["quantity"] == "sigma_laser")
    a2.errorbar([x[0] for x in sl], [x[1] for x in sl], yerr=[x[2] for x in sl],
                fmt="-o", color="#D55E00", ms=6, lw=1.6, capsize=3,
                label="global fit, with the collisional term tied to the density")
    freeT, freeS, freeE = [], [], []
    for T in (70, 90, 110):
        v = [(float(r["sigma_laser"]), float(r["sigma_laser_err"])) for r in rows
             if r["role"] == "t_sweep" and int(float(r["T"])) == T]
        s = np.array([x[0] for x in v]); w = 1.0 / np.array([x[1] for x in v]) ** 2
        freeT.append(T); freeS.append(float(np.sum(w * s) / np.sum(w)))
        # The inverse-variance mean carries an uncertainty, and at 70 C it is
        # larger than the excursion the panel calls flat (one of the four
        # per-peak values there is 0.32 +/- 1.48 and constrains nothing).
        # Drawing the series with plot() instead of errorbar() hid that.
        freeE.append(float(1.0 / np.sqrt(np.sum(w))))
    a2.errorbar(freeT, freeS, yerr=freeE, fmt="-s", color="#0072B2", ms=6, lw=1.6,
                capsize=3, label="free per-condition (inverse-variance mean\nof the "
                                 "four peaks, with its uncertainty)")
    a2.set_xlabel("cell temperature (°C)")
    a2.set_ylabel("laser FWHM (MHz)")
    # Which condition the tied fit pushes the laser width down at is a property
    # of the drawn series, so it is read off that series rather than named: it
    # was written as "110 °C" while the panel plotted whatever the global fit
    # had most recently produced. Both numbers used to be argued in the panel
    # title. They are values, so they stay on the canvas as two value rows and
    # the reading of them moves to the caption.
    T_dip = min(sl, key=lambda x: x[1])[0]
    a2.set_title("(b) fitted laser FWHM against cell temperature, two fit models",
                 fontsize=8)
    # Inset from the spine far enough to clear the leftmost error bar, whose
    # lower whisker runs down past these two rows.
    a2.text(0.075, 0.03,
            "free per-condition mean = %.1f MHz\n"
            "lowest tied value at %g °C"
            % (float(np.mean(freeS)), T_dip),
            transform=a2.transAxes, ha="left", va="bottom", fontsize=7,
            color="0.3")
    # A blank strip above the two series, and the legend anchored in it. With
    # the placement left to matplotlib the legend landed in the bottom corner,
    # on top of the two value rows above.
    lo, hi = a2.get_ylim()
    a2.set_ylim(lo, lo + (hi - lo) * 1.45)
    a2.legend(fontsize=7.5, loc="upper left")
    _footer(fig, "Source: results/linefit_conditions.csv, results/global_fit.csv, "
                 "results/lever_crosscheck.csv. Regenerate: python scripts/make_figures.py.")
    _save(fig, "fig5_pooled_width.png")


def fig_gamma_floor():
    """The lever test (M4d, 2026-07-12): the fitted collisional width is a
    near-flat FLOOR — it rises only ~x1.5 while the density rises x52 — so the
    joint-fit beta cannot be a real linear collision rate: extrapolating either
    joint value from the 70 C anchor overshoots the measured 130 C width. That
    lever-dependence is WHY beta is quoted as a BOUND. Per-condition split shown
    (sigma_laser free), which is degenerate (corr ~ -0.85) — but the same story
    holds split-independently in fig5 panel A (total width vs the minimum
    growth line). Betas are READ from results/lever_crosscheck.csv, not typed."""
    rows = _rows("linefit_conditions")

    def gam(peak, T):
        role = "p_sweep" if T == 130 else "t_sweep"
        for r in rows:
            if (r["peak"] == peak and r["role"] == role and int(float(r["T"])) == T
                    and (r["P"] == "225" or role == "t_sweep")):
                return float(r["gamma_coll"]), float(r["gamma_coll_err"])
        return None

    Ts = (70, 90, 110, 130)
    peaks = tuple(PEAK_COLOR)
    N = np.array([density_units(float(T)) for T in Ts])
    # Taller than the panel needs: the legend is drawn in the strip under the
    # axes, because the two extrapolation lines climb through the top of the
    # frame and struck through the right-hand column of entries.
    fig, ax = plt.subplots(figsize=(6.6, 5.9))
    for peak in peaks:
        gv = [gam(peak, T) for T in Ts]
        gval = np.array([g[0] for g in gv])
        gerr = np.array([g[1] for g in gv])
        # gamma_coll is a width and cannot be negative, and one point
        # (993.4154 nm at 70 C, 0.19 +/- 0.32) has a symmetric Wald error
        # larger than its own value. Clipping that whisker at zero drew a bar
        # running into the bottom spine with no cap, which reads as a bar that
        # continues off the panel. The axis now extends below zero and carries
        # a zero line instead, so the interval is shown for what it is.
        ax.errorbar(N, gval, yerr=gerr, fmt="-o",
                    color=PEAK_COLOR[peak], alpha=0.30, ms=3, lw=0.9,
                    capsize=2, label=PEAK_LABEL[peak])
    mean_g = np.array([np.mean([gam(p, T)[0] for p in peaks]) for T in Ts])
    scat = np.array([np.std([gam(p, T)[0] for p in peaks], ddof=1) / 2.0 for T in Ts])
    # Wrapped: on one line this entry sits in the legend's right-hand column
    # and ran past the right spine, losing its last word off the panel.
    ax.errorbar(N, mean_g, yerr=scat, fmt="-o", color="k", ms=6, lw=2.0, capsize=3,
                label="mean of the four peaks, with the\nstandard error of that mean",
                zorder=5)
    # joint-fit betas (from the committed CSV), extrapolated from the 70 C mean:
    # a REAL linear collision rate would follow these lines; the data do not.
    dfp = C.RESULTS_DIR / "lever_crosscheck.csv"
    if dfp.exists():
        dfr = list(csv.DictReader(open(dfp)))
        bhead = np.mean([float(r["value"]) for r in dfr
                         if r["quantity"] == "beta_crosscheck"])
        blever = np.mean([float(r["value"]) for r in dfr
                          if r["quantity"] == "beta_lever_probe_130"])
        Nf = np.geomspace(N[0], N[-1], 200)
        # The two levers are the density ratios of the two ranges the two
        # coefficients were fitted over: 70 to 110 °C for the shorter one,
        # 70 to 130 °C for the longer. They were typed as "16-fold" and
        # "53-fold" beside coefficients read from a file, so a change to the
        # density model would have left the two halves of the sentence
        # describing different things.
        lever_short = N[2] / N[0]
        lever_long = N[3] / N[0]
        ax.plot(Nf, mean_g[0] + bhead * (Nf - N[0]), "--", color="#D55E00", lw=1.6,
                label="coefficient %.3f MHz per\n"
                      r"$10^{12}$cm$^{-3}$, from the %.0f-fold density range"
                      % (bhead, lever_short))
        ax.plot(Nf, mean_g[0] + blever * (Nf - N[0]), ":", color="#0072B2", lw=1.8,
                label="coefficient %.3f MHz per\n"
                      r"$10^{12}$cm$^{-3}$, from the %.0f-fold density range"
                      % (blever, lever_long))
    ax.set_xscale("log")
    ax.axhline(0.0, color="0.4", lw=0.8, ls=":")
    ax.set_ylim(-0.22, 1.15)
    ax.text(0.012, 0.145, "a width cannot be negative", transform=ax.transAxes,
            fontsize=6.5, color="0.35", ha="left", va="top")
    ax.set_xlabel(r"Rb density $N$  ($10^{12}\,\mathrm{cm^{-3}}$)")
    ax.set_ylabel("collisional FWHM (MHz)")
    ax.set_title("Fitted collisional FWHM against Rb density, the four components "
                 "and their mean", fontsize=8)
    ax.legend(fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.12),
              ncol=2, borderaxespad=0.0)
    _footer(fig, "Source: results/linefit_conditions.csv, results/lever_crosscheck.csv. "
                 "Regenerate: python scripts/make_figures.py.")
    _save(fig, "fig6_gamma_floor.png", rect=(0, 0.04, 1, 1))


def fig_identifiability_profile():
    """The global profile-likelihood map behind M12 (methods §4.10): chi2
    minimised over transit + all per-trace nuisances at each (gamma_coll,
    sigma_laser) point, on the bright 993.4192 nm 130 C / 225 mW condition.
    LEFT: the wide map — the topology of the width degeneracy (log10 dchi2)
    with the joint-68/95% contours. RIGHT: the zoom about the minimum, profile
    contours against the LOCAL covariance ellipse (dashed): in the Gaussian
    limit the two coincide, so their agreement is the trust test for every
    covariance-based statement; the valley-floor points trace the degeneracy
    direction. All values read from results/identifiability_profile.csv."""
    fp = C.RESULTS_DIR / "identifiability_profile.csv"
    if not fp.exists():
        print("  (identifiability_profile.csv absent -- skipping fig7)")
        return
    rows = list(csv.DictReader(open(fp)))

    def axis(name):
        vals = {int(r["key"]): float(r["value"]) for r in rows if r["quantity"] == name}
        return np.array([vals[i] for i in sorted(vals)])

    def surf(name, nsl, ngc):
        Z = np.empty((nsl, ngc))
        for r in rows:
            if r["quantity"] == name:
                i, j = r["key"].split("|")
                Z[int(i), int(j)] = float(r["value"])
        return Z

    cov = {r["key"]: float(r["value"]) for r in rows if r["quantity"] == "cov"}
    fit = {r["key"]: float(r["value"]) for r in rows if r["quantity"] == "fit"}
    M = np.array([[cov["gc_gc"], cov["gc_sl"]], [cov["gc_sl"], cov["sl_sl"]]])
    from rb5s6s.identifiability import valley_floor

    fig, axes = plt.subplots(1, 2, figsize=(9.8, 4.4))
    for k, (nm, ax) in enumerate(zip(("wide", "zoom"), axes)):
        gc = axis(f"{nm}_gc"); sl = axis(f"{nm}_sl")
        D = surf(f"{nm}_dchi2", len(sl), len(gc))
        T = surf(f"{nm}_transit", len(sl), len(gc))
        pc = ax.contourf(gc, sl, np.log10(np.maximum(D, 0.05)), levels=18,
                         cmap="viridis")
        ax.contour(gc, sl, D, levels=[2.30, 5.99], colors=["w", "w"],
                   linestyles=["-", "--"], linewidths=1.2)
        # the transit -> 0 wall: beyond it the profiled transit is pinned at its
        # bound and the Gaussian ellipse correspondence does not apply
        if (T < 0.02).any() and not (T < 0.02).all():
            ax.contour(gc, sl, T, levels=[0.02], colors="gray",
                       linestyles=":", linewidths=1.4)
            ax.plot([], [], ":", color="gray",
                    label="boundary where the fitted transit width reaches zero")
        ax.plot(fit["gamma_coll"], fit["sigma_laser"], "*", color="w", ms=11,
                mec="k", mew=0.6, label="free fit (all widths free)", zorder=5)
        i_m, j_m = np.unravel_index(int(np.argmin(D)), D.shape)
        ax.plot(gc[j_m], sl[i_m], "o", color="#D55E00", ms=6, mec="w", mew=0.6,
                label="profile minimum", zorder=5)
        # same floor definition as the shipped banana metric (within=5.99 on the
        # zoom); the wide panel uses a looser cut purely to trace the topology
        fl = valley_floor(gc, sl, D, within=(5.99 if nm == "zoom" else 25.0))
        ax.plot(fl["floor_gc"], fl["floor_sl"], ".", color="#E69F00", ms=4,
                label="profile valley floor")
        if nm == "zoom":
            evals, evecs = np.linalg.eigh(M)
            th = np.linspace(0, 2 * np.pi, 200)
            for c, ls in ((2.30, "-"), (5.99, "--")):
                e = (np.sqrt(c * evals[0]) * np.outer(np.cos(th), evecs[:, 0])
                     + np.sqrt(c * evals[1]) * np.outer(np.sin(th), evecs[:, 1]))
                ax.plot(fit["gamma_coll"] + e[:, 0], fit["sigma_laser"] + e[:, 1],
                        ls, color="k", lw=1.1,
                        label=("covariance ellipse, 68 and 95 percent (black)"
                               if c == 2.30 else None))
            ax.set_title("(b) detail near the minimum: profile contours in\n"
                         "white, covariance ellipse in black",
                         fontsize=9)
        else:
            ax.set_title("(a) the full degeneracy valley, with the joint 68 and\n"
                         "95 percent contours in white",
                         fontsize=9)
        ax.set_xlabel("collisional FWHM (MHz)")
        if k == 0:
            ax.set_ylabel("laser FWHM (MHz)", fontsize=8)
        cb = fig.colorbar(pc, ax=ax, shrink=0.9)
        cb.set_label("base ten logarithm of the rise in\nchi squared above its minimum",
                     fontsize=7)
        ax.legend(fontsize=7, loc="upper right", frameon=True, framealpha=1.0)
    fig.suptitle("The collisional and laser FWHM at 993.4192 nm, cell at 130 °C, "
                 "225 mW: the profile-likelihood map",
                 fontsize=8.5, y=0.995, va="top")
    _footer(fig, "Source: results/identifiability_profile.csv (rb5s6s.identifiability). "
                 "Regenerate: python scripts/run_identifiability.py && "
                 "python scripts/make_figures.py.")
    _save(fig, "fig7_identifiability_profile.png", rect=(0, 0.02, 1, 0.88))


def ruler_fig_candidates(rows=None):
    """Which ruler traces may stand as fig8's example, and in what order.

    The rule this replaces scored candidates by the smaller of the two
    OUTERMOST fitted heights over the fit residual. That rewarded the exact
    pathology the 2026-08-04 validity work was opened for: a retrace mirror
    sitting in an outer slot RAISES an outer height, so the trace with a
    mirrored tooth won the panel, and the figure's own subtitle then had to
    admit that one of the seven teeth was not there.

    The replacement is pre-registered in
    docs/notes/ruler_validity_and_trim_prereg.md section 7 and is applied
    here exactly as written. Eligibility, every clause required:

      * the top-three verdict PASSES and is not marginal,
      * the re-index ladder took no action,
      * the trace is not excluded,
      * at least six of the seven fitted heights stand strictly above the fit
        residual standard deviation, with none railed on its zero bound
        (amendment 4: the original all-seven clause is unsatisfiable in this
        campaign, because the ramp clips one outer tooth window on every
        recorded ruler and the drive depth holds a fully covered third-order
        tooth below the residual anyway),
      * the reduced chi-squared is at most RULER_FIG_CHI2_MAX.

    Ranking is by the SMALLEST of the seven heights over the fit residual.
    A mirror cannot raise the smallest of seven heights, so the ranking is not
    gameable by the defect the figure is being fixed for. Untrimmed traces
    outrank trimmed ones and the source path breaks ties, so the choice is
    deterministic.

    Every field is read from results/ruler_traces.csv, the per-trace record
    the calibration itself wrote. The figure must show the fit the frequency
    axis was built on, not a second fit that resembles it: the rule this
    replaces refit each trace with flat weights, so the heights it scored were
    never the heights the pipeline used.

    The sibling-outlier mark of the same note's amendment 2 is deliberately
    NOT one of the clauses. The list above was fixed before that rule existed,
    and adding a clause to a pre-registered filter after seeing the population
    is the move the note exists to prevent. Whether an outlier trace should be
    allowed to stand as the example is a question for the experimenter.

    Returns (ranked, census). ranked is a list of (score, row), best first.
    census maps the first clause each rejected trace failed to a count.
    """
    if rows is None:
        rows = _rows("ruler_traces")
    ranked, census = [], defaultdict(int)
    for r in rows:
        heights = [float(r[c]) for c in RULER_HEIGHT_COLS]
        fit_rms = float(r["fit_rms"])
        if r["top3_ok"] != "True" or r["top3_marginal"] == "True":
            census["tooth-labelling verdict is not a clean pass"] += 1
        elif r["reindex_action"] != "none":
            census["the ladder had to re-index it"] += 1
        elif r["excluded"] == "True":
            census["excluded"] += 1
        elif int(r["n_railed"]):
            census["a slot is railed on its zero bound"] += 1
        elif sum(1 for h in heights if h > fit_rms) < 6:
            census["fewer than six teeth stand above the fit residual"] += 1
        elif float(r["chi2_red"]) > RULER_FIG_CHI2_MAX:
            census["reduced chi-squared above the ceiling"] += 1
        else:
            ranked.append((min(heights) / fit_rms, r))
    ranked.sort(key=lambda sr: (sr[1]["trimmed"] == "True", -sr[0], sr[1]["file"]))
    return ranked, dict(census)


def _ruler_block_law(row):
    """The noise law the calibration fitted this trace under.

    scripts/run_ruler.py builds one law per block from every usable trace in
    it, so reproducing the recorded fit means reproducing the block, not just
    the trace. Rebuilt here rather than stored, because a law is a fitted
    object and the record's job is to carry the fit, not its weights."""
    from rb5s6s.ingest import load_manifest, load_trace, trace_path
    from rb5s6s.noise import condition_noise_model
    from rb5s6s.qc import trace_metrics, hard_flags, ingest_flags
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import run_ruler as _rr

    manifest = {r["file"]: r for r in load_manifest()}
    rec = manifest[row["file"]]
    key = _rr.block_key(rec)
    volts, chosen = [], None
    for r in manifest.values():
        if (r["flag"] != "canonical" or r["rf_on"] != "True"
                or _rr.block_key(r) != key):
            continue
        t, v, info = load_trace(trace_path(r), with_info=True)
        m = trace_metrics(t, v, rf_on=True)
        hf = hard_flags(m, rf_on=True) + ingest_flags(info)
        if any("dropout" in f or "no comb" in f or "truncated" in f for f in hf):
            continue
        volts.append(v)
        if r["file"] == row["file"]:
            chosen = (t, v)
    return chosen, condition_noise_model(volts)


def fig_ruler():
    """The built-in frequency ruler (methods §3): one EOM ruler trace with its
    constrained seven-tooth comb fit, the same physical line excited via up to
    seven sideband pairs, teeth exactly 6.25 MHz apart on the laser axis
    (outer teeth weak: they need higher-order pairs; note the k=0 TOOTH is fed
    by (s+,s-) pairs as well as (c,c), so it can stand tall even with the
    optical carrier AM-suppressed, and the tooth pattern varies block to block
    with the 2025 HWP setting; methods section 3).

    RIGHT: the free-centres nonlinearity map (results/ruler_nlmap.csv), the
    empirical bound (~0.3% per position) on scan nonlinearity AND any
    tooth-dependent pull (differential Stark, asymmetric-wing overlap), the
    ruler's common-mode-rejection check.

    The displayed trace is chosen by ruler_fig_candidates() above, whose
    docstring carries the rule and the reason it replaced the previous one. An
    empty eligible set is a finding about the ruler population rather than a
    figure bug: the figure is skipped, the census is printed, and
    tests/test_ruler.py::test_fig8_candidate_set_is_not_empty says so out
    loud."""
    # This panel rebuilds a block law from the raw traces, which travel with
    # the working record rather than with every checkout. Without them the
    # loader used to raise FileNotFoundError from inside the block rebuild,
    # which killed the whole run and left every figure after this one in
    # main()'s order undrawn. Since the footer on every figure tells a reader
    # to run this script, that traceback was the first thing a fresh clone saw.
    # Skip the way fig13 skips its photograph, and keep the committed PNG.
    if not (C.DATA_RAW_DIR / "rulers_p").is_dir():
        print("  (raw ruler traces not in this checkout, keeping the "
              "existing fig8 PNG)")
        return
    from rb5s6s.ruler import _comb, TEETH

    def _sixth(r):
        # The binding height under amendment 4's six-standing clause is the
        # second-smallest of the seven, since six must clear the residual.
        hs = sorted(float(r[c]) for c in RULER_HEIGHT_COLS)
        return hs[1] / float(r["fit_rms"])

    trace_rows = _rows("ruler_traces")
    ranked, census = ruler_fig_candidates(trace_rows)
    if not ranked:
        print("  (no ruler trace is eligible for fig8, so it is NOT redrawn.")
        for why, n in sorted(census.items(), key=lambda kv: -kv[1]):
            print(f"     {n:4d} rejected: {why} (first failing clause)")
        near = max(trace_rows, key=_sixth)
        print(f"   Over all {len(trace_rows)} fitted rulers the tallest "
              f"second-smallest tooth stands at {_sixth(near):.2f} of its own "
              f"fit residual ({near['file']}), against the 1.0 the six-standing "
              "clause requires.")
        print("   The eligibility rule is section 7 of "
              "docs/notes/ruler_validity_and_trim_prereg.md. An empty set is a "
              "finding about the population, not a threshold to loosen: take it "
              "to the experimenter. See tests/test_ruler.py::"
              "test_fig8_candidate_set_is_not_empty.)")
        return
    score, row = ranked[0]
    loaded, law = _ruler_block_law(row)
    if loaded is None:
        print(f"  (the eligible ruler trace {row['file']} is not in the raw "
              "tree here, so fig8 is not redrawn)")
        return
    t, v = loaded
    from rb5s6s.ruler import validated_comb_fit
    fit = validated_comb_fit(t, v, law)
    # The refit has to reproduce the record, or the panel would be showing a
    # different fit from the one the frequency axis was built on. That is
    # exactly what the deleted selection did, silently, for months.
    if abs(fit["delta_ms"] - float(row["delta_ms"])) > 1e-6:
        print(f"  (fig8 warning: refitting {row['file']} gives a tooth spacing of "
              f"{fit['delta_ms']:.4f} ms against the {float(row['delta_ms']):.4f} ms "
              "on record, so the drawn curve is not the fit of record)")

    # The left column is the trace with its comb fit over a standardized
    # residual strip, the same convention as fig0, fig21 and fig22. This is
    # the surface where the residual carries the most history: the retrace
    # mirror that mislabelled the displayed comb for months was a residual
    # feature, and a calibration figure that hides its residuals asks the
    # reader to take the one thing it got wrong on trust.
    from matplotlib.gridspec import GridSpec
    fig = plt.figure(figsize=(9.8, 4.7))
    gsp = GridSpec(2, 2, figure=fig, width_ratios=[1.8, 1.2],
                   height_ratios=[2.9, 1.0], hspace=0.09, wspace=0.24,
                   left=0.075, right=0.985, top=0.83, bottom=0.12)
    ax = fig.add_subplot(gsp[0, 0])
    axres = fig.add_subplot(gsp[1, 0], sharex=ax)
    # The right column is split so the SAMPLE COUNT is drawn rather than
    # asserted. The old panel classified windows by n in the legend text and
    # asked the reader to trust it, which is what made a 4-sigma edge point
    # read as contradicting the title (experimenter, 2026-08-17).
    ax2 = fig.add_subplot(gsp[0, 1])
    ax2n = fig.add_subplot(gsp[1, 1], sharex=ax2)
    ax.plot(t, v, ".", ms=1.6, color="0.55", label="ruler trace (raw)")
    tf = np.linspace(t[0], t[-1], 3000)
    ax.plot(tf, _comb(tf, fit["t0_ms"], fit["delta_ms"], fit["width_ms"],
                      fit["heights"], fit["b0"], fit["b1"]),
            "-", color="#0072B2", lw=1.4,
            label=f"constrained {len(TEETH)}-tooth comb fit")
    ymax = max(fit["heights"]) + fit["b0"]
    ax.set_ylim(top=ymax * 1.22)
    # Samples the tail trimmer removed are shaded and named, so a reader sees
    # the fit's actual sample set. trim_start_ms and trim_end_ms bound the KEPT
    # interval, one convention across every table in the repository.
    if fit["trimmed"]:
        for lo, hi in ((t[0], fit["trim_start_ms"]), (fit["trim_end_ms"], t[-1])):
            if hi > lo:
                ax.axvspan(lo, hi, color="0.75", alpha=0.35, lw=0, zorder=0)
        ax.annotate("shaded: samples excluded from the fit\n"
                    f"({fit['trim_reason']})",
                    xy=(0.5, 0.02), xycoords="axes fraction", ha="center",
                    va="bottom", fontsize=6.4, color="0.3")
    # The third-order pair carries a few per mille of the first-order power and
    # sits under this trace's noise, so k = +/-3 marked EMPTY CANVAS in exactly
    # the style used for teeth the reader can see. Drawn faint and dashed now,
    # and named once, so a reader is not hunting for a peak that is not there.
    _kmax = max(abs(n) for n in TEETH)
    for n in TEETH:
        tc = fit["t0_ms"] + n * fit["delta_ms"]
        _faint = abs(n) == _kmax
        ax.axvline(tc, color="#D55E00", lw=0.7,
                   alpha=0.22 if _faint else 0.5, ymax=0.86,
                   ls=(0, (2, 2)) if _faint else "-")
        ax.annotate(f"$k={n}$", xy=(tc, ymax * 1.08), ha="center",
                    fontsize=8, color="#D55E00",
                    alpha=0.45 if _faint else 1.0)

    # The outermost teeth carry the note ONCE, in axes coordinates, in the
    # empty upper right. Attaching it to the k = +3 tick pushed the label box
    # past the right edge of the panel, which the canvas guard rejects and
    # which is the same "sentence sized for prose in a slot sized for a
    # number" defect this file keeps hitting.
    # At 0.955 it overprinted the k = 0 to k = 2 labels, which the canvas
    # guard cannot see because both are text. The band between the tooth
    # lines' tops (0.86) and the label row is empty, and the note sits in it,
    # anchored left where the k = -3 dashed line has no label neighbour.
    ax.text(0.012, 0.565, "dashed teeth: third order,\nunder this trace's noise",
            transform=ax.transAxes, ha="left", va="top", fontsize=6.0,
            color="#D55E00", alpha=0.85)

    # The residual strip under the trace: each sample minus the drawn comb,
    # divided by the error the fit weighted it with (the block noise law, so
    # the division removes the known signal-level dependence of the noise).
    from rb5s6s.noise import signal_level as _siglevel, sigma_of_v as _sigofv
    model_t = _comb(t, fit["t0_ms"], fit["delta_ms"], fit["width_ms"],
                    fit["heights"], fit["b0"], fit["b1"])
    lev_t, _ = _siglevel(v)
    pull_t = (v - model_t) / _sigofv(np.maximum(lev_t, 0.0), law)
    axres.axhspan(-1.0, 1.0, color="0.5", alpha=0.15, lw=0)
    axres.plot(t, pull_t, ".", ms=1.2, color="0.55", rasterized=True)
    axres.axhline(0.0, color="#8f1f1f", lw=0.9, ls=(0, (4, 3)))
    if fit["trimmed"]:
        for lo, hi in ((t[0], fit["trim_start_ms"]), (fit["trim_end_ms"], t[-1])):
            if hi > lo:
                axres.axvspan(lo, hi, color="0.75", alpha=0.35, lw=0, zorder=0)
    lim8 = 4.0 * float(np.std(pull_t))
    # THE RESIDUALS ARE NOT WHITE, AND THE PANEL NOW SAYS SO (experimenter reading,
    # 2026-08-12: "the residuals still have some structure"). Measured on this
    # trace at draw time rather than asserted, because a reduced chi-squared
    # near 1 says only that the SCALE is right and says nothing about
    # correlation, and this panel previously showed a scatter that looked
    # acceptable while carrying both defects below.
    #
    #   correlation: lag-1 autocorrelation ~+0.20 against a white-noise
    #   expectation of 0 +- 1/sqrt(n), which is a nine-sigma statement, and it
    #   is still +0.18 at lag 10, so the misfit is smooth over about ten
    #   samples rather than sample-to-sample noise.
    #
    #   weighting: NOT a defect, and checked here because it was the first
    #   suspicion. The standardised scatter is 1.00 in the dimmest third of
    #   the trace against 0.99 in the brightest, so the block noise law's
    #   signal-level dependence is doing its job. A first check of this
    #   reported 0.5 against 1.4 and was wrong: it divided by a CONSTANT
    #   sigma instead of the level-dependent law the fit actually weighted
    #   with, which manufactures exactly that trend out of shot noise.
    #
    # So the one real finding is the correlation. What it costs: a correlated
    # residual makes the per-trace tooth-spacing error optimistic, in the same
    # direction as the block-to-block over-dispersion for which the campaign
    # rate already carries a PDG scale factor. It does not bias the spacing
    # itself, which is why the frequency axis stands.
    _z = pull_t[np.isfinite(pull_t)]
    _n = _z.size
    _a1 = float(np.corrcoef(_z[:-1], _z[1:])[0, 1])
    _a10 = float(np.corrcoef(_z[:-10], _z[10:])[0, 1])
    _ord = np.argsort(model_t[np.isfinite(pull_t)])
    _lo = float(np.std(_z[_ord[: _n // 3]]))
    _hi = float(np.std(_z[_ord[2 * _n // 3:]]))
    # Two short lines INSIDE the strip. One long line ran off both edges of
    # the canvas, which the canvas guard reports and which is the same defect
    # this file has now hit four times: a sentence sized for prose put into a
    # panel sized for numbers.
    # BOTH annotations moved OUT of the strip on 2026-08-17: they were drawn
    # inside the axes at 94 per cent height and overprinted the residual
    # points, which is the collision class this file already has a rule about.
    # One line, below the strip, outside the data area, is enough.

    axres.set_ylim(-lim8, lim8)
    axres.set_ylabel(r"residual / $\sigma$", fontsize=7.5)
    axres.tick_params(labelsize=7.5)
    ax.tick_params(labelbottom=False)
    axres.set_xlabel("scan time (ms)")
    ax.set_ylabel("fluorescence (V)")
    ax.set_title(f"(a) one ruler trace and its {len(TEETH)}-tooth comb fit, teeth\n"
                 f"{TOOTH_SPACING_LASER_HZ / 1e6:.2f} MHz apart in laser frequency",
                 fontsize=9)
    # Anchored below the tooth labels rather than at the bottom left, where the
    # opaque box covered the left tail of the outermost fitted tooth.
    ax.legend(fontsize=7, loc="upper left", bbox_to_anchor=(0.012, 0.80),
              framealpha=1.0, frameon=True)
    # Two prose boxes used to sit in this panel: why THIS trace is the one
    # drawn (the pre-registered eligibility clauses, with the trace's own
    # tooth-standing count, weakest-tooth score and reduced chi-squared), and
    # why the third-order pair sits under the noise (its share of the
    # first-order power, and which outer window the ramp clips). Both are
    # caption material, and the rule they quote is section 7 and amendment 4 of
    # docs/notes/ruler_validity_and_trim_prereg.md.

    nl = _rows("ruler_nlmap")
    pos = np.array([float(r["pos_ms"]) for r in nl])
    rr = np.array([float(r["rate_rel"]) for r in nl])
    er = np.array([float(r["rate_rel_err"]) for r in nl])
    n_win = np.array([int(r["n"]) for r in nl])
    dev = 100.0 * (rr - 1.0)
    dev_err = 100.0 * er
    bnd = 100.0 * RULER_LINEARITY_BOUND

    # REDESIGNED 2026-08-17, after the experimenter reported the panel looked
    # wrong and unclear for the second time. Two defects, and the second is
    # about the record rather than the drawing.
    #
    # First, the panel classified windows by SAMPLE COUNT in legend text while
    # drawing every window the same way, so a reader saw a point at -1.75%
    # under a title that said "flat to 0.25%" and had to take the exclusion on
    # trust. The count is now DRAWN, in its own strip below, so the reader can
    # see which windows the bound rests on.
    #
    # Second, the code justified the n < 19 exclusion by saying those windows
    # "cannot test the bound, their errors exceed it". Checked against
    # results/ruler_nlmap.csv that is false for three of the five excluded
    # windows, and the two leading-edge windows are not imprecise at all:
    # -1.75 +/- 0.40 and +0.73 +/- 0.18 per cent, which are 4.4 and 4.0 sigma
    # from zero with error bars at or below the bound. They are precise
    # measurements that FAIL the flatness bound, not vague ones that cannot
    # test it. The panel now says so, because a calibration figure that hides
    # its own worst points is not a calibration figure.
    sig = np.abs(dev) / dev_err
    well = n_win >= N_WELL_SAMPLED
    departs = (~well) & (np.abs(dev) > bnd) & (sig > 3.0)
    quiet = (~well) & (~departs)

    ax2.axhspan(-bnd, bnd, color="#009E73", alpha=0.10, zorder=0)
    ax2.axhline(0.0, color="k", lw=0.8, zorder=1)
    for m, col, face, lab in (
            (well, "#009E73", "#009E73", f"interior, {N_WELL_SAMPLED}+ traces"),
            (quiet, "#9ecae1", "white", "edge, consistent with flat"),
            (departs, "#cb181d", "#cb181d", "edge, departs at 3 sigma or more")):
        if not m.any():
            continue
        ax2.errorbar(pos[m], dev[m], yerr=dev_err[m], fmt="none", ecolor=col,
                     elinewidth=1.1, capsize=2, zorder=2)
        ax2.scatter(pos[m], dev[m], s=26, color=face, edgecolor=col,
                    linewidth=1.1, zorder=3, label=lab)
    # Name the worst point once, on the canvas, with its significance.
    if departs.any():
        j = int(np.argmax(np.abs(dev) * departs))
        ax2.annotate(f"{dev[j]:+.2f}% $\pm$ {dev_err[j]:.2f},  {sig[j]:.1f}$\sigma$",
                     xy=(pos[j], dev[j]), xytext=(0.17, 0.035),
                     textcoords="axes fraction", fontsize=6.4, color="#cb181d",
                     ha="left", va="bottom",
                     arrowprops=dict(arrowstyle="-", color="#cb181d", lw=0.7))
    _wspread = float(np.max(np.abs(dev[well])))
    ax2.set_ylabel("local rate, deviation from\nthe whole-scan rate (%)", fontsize=7.5)
    ax2.set_title("(b) where scan time converts linearly to frequency:\n"
                  f"flat to {_wspread:.2f}% across the interior, "
                  "not at the leading edge", fontsize=8.5)
    # Placed in the empty band between the departing edge point and the
    # interior cluster. Lower-left covered the -1.75% point and its label,
    # upper-anything covers the tall edge error bars.
    ax2.legend(fontsize=5.9, loc="lower left", bbox_to_anchor=(0.26, 0.30),
               framealpha=1.0, frameon=True, handletextpad=0.4, borderpad=0.35)
    ax2.tick_params(labelbottom=False, labelsize=7.5)
    ax2.set_ylim(-2.35, 1.45)

    # The counts strip: the reader sees WHY the edges are treated apart.
    colr = np.where(well, "#009E73", np.where(departs, "#cb181d", "#9ecae1"))
    ax2n.bar(pos, n_win, width=105, color=colr, alpha=0.85)
    ax2n.axhline(N_WELL_SAMPLED, color="0.35", lw=0.8, ls=":")
    ax2n.text(0.985, N_WELL_SAMPLED, f" {N_WELL_SAMPLED}", transform=
              ax2n.get_yaxis_transform(), fontsize=6, color="0.35",
              ha="right", va="bottom")
    ax2n.set_ylabel("traces", fontsize=7.5)
    ax2n.set_xlabel("centre of the window, in scan time (ms)")
    ax2n.tick_params(labelsize=7.5)

    _footer(fig, f"Residuals are correlated, not white: lag-1 {_a1:+.2f}, lag-10 {_a10:+.2f}, "
                 f"against 0 +/- {1 / np.sqrt(_n):.2f} for white noise. Scatter {_lo:.2f} in the "
                 f"dim third against {_hi:.2f} in the bright, so the noise law's level dependence holds.\n"
                 "Source: results/ruler_traces.csv (the eligibility and ranking, section 7 of "
                 "docs/notes/ruler_validity_and_trim_prereg.md) + data_raw traces\n"
                 "(rb5s6s.ingest, rb5s6s.ruler, the plotted trace, refit under its own block's "
                 "noise law) + results/ruler_nlmap.csv. Regenerate: python scripts/run_ruler.py "
                 "&& python scripts/make_figures.py.")
    _save(fig, "fig8_ruler.png", rect=(0, 0.03, 1, 1))


def fig_degeneracy_vs_observable():
    """Why the per-condition Lorentzian/Gaussian split is never quoted as
    physics (docs/RESEARCH_DECISIONS.md 1). LEFT: the 20 power-sweep conditions
    at 130 C in the (gamma_coll, sigma_laser) plane, each with its 1-sigma
    error ellipse from the fit's own covariance, over contours of constant
    TOTAL FWHM. The ellipses are elongated along the contours and the condition
    centres scatter along the same direction -- the split moves freely in the
    direction the observable does not constrain. RIGHT: the same conditions'
    total FWHM against power, the quantity actually measured: flat (no power
    broadening, C3a) and determined to ~1%. All values read from
    results/linefit_conditions.csv; contours from the shipped model."""
    fp = C.RESULTS_DIR / "linefit_conditions.csv"
    if not fp.exists():
        print("  (linefit_conditions.csv absent -- skipping fig10)")
        return
    rows = [r for r in csv.DictReader(open(fp)) if r["role"] == "p_sweep"]
    if not rows:
        print("  (no p_sweep rows -- skipping fig10)")
        return
    from rb5s6s.stark import _fwhm_of
    from rb5s6s.linefit import transit_fwhm_at_T

    g = np.array([float(r["gamma_coll"]) for r in rows])
    ge = np.array([float(r["gamma_coll_err"]) for r in rows])
    sl = np.array([float(r["sigma_laser"]) for r in rows])
    sle = np.array([float(r["sigma_laser_err"]) for r in rows])
    corr = np.array([float(r["corr"]) for r in rows])
    tw = np.array([float(r["total_fwhm"]) for r in rows])
    twe = np.array([float(r["total_fwhm_err"]) for r in rows])
    P = np.array([float(r["P"]) for r in rows])
    peaks = [r["peak"] for r in rows]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.2, 4.5))

    # --- LEFT: the degeneracy plane -------------------------------------
    transit = transit_fwhm_at_T(130.0, C.TRANSIT_FWHM_PLACEHOLDER_MHZ)
    gg = np.linspace(max(g.min() - 0.15, 0.0), g.max() + 0.15, 46)
    ss = np.linspace(max(sl.min() - 0.2, 0.0), sl.max() + 0.2, 46)
    nu = np.arange(-40.0, 40.0, 0.01)
    W = np.array([[_fwhm_of(a, b, transit, 0.0, nu) for a in gg] for b in ss])
    cs = ax1.contour(gg, ss, W, levels=8, colors="0.55", linewidths=0.8)
    ax1.clabel(cs, inline=True, fontsize=6, fmt="%.2f")

    th = np.linspace(0, 2 * np.pi, 120)
    for i, pk in enumerate(peaks):
        c = PEAK_COLOR.get(pk, "0.4")
        cov = np.array([[ge[i] ** 2, corr[i] * ge[i] * sle[i]],
                        [corr[i] * ge[i] * sle[i], sle[i] ** 2]])
        vals, vecs = np.linalg.eigh(cov)
        pts = vecs @ (np.sqrt(np.maximum(vals, 0))[:, None] * np.array([np.cos(th), np.sin(th)]))
        ax1.plot(g[i] + pts[0], sl[i] + pts[1], color=c, lw=0.8, alpha=0.55)
        ax1.plot(g[i], sl[i], "o", color=c, ms=3.5, zorder=3)
    for pk, c in PEAK_COLOR.items():
        if pk in peaks:
            ax1.plot([], [], "o-", color=c, ms=3.5, lw=0.8, label=f"993.{pk} nm")
    ax1.set_xlabel("collisional FWHM (MHz)")
    ax1.set_ylabel("laser FWHM (MHz)")
    ax1.axhline(0.0, color="0.3", lw=0.8, ls=":")
    ax1.text(gg[-1], 0.02, "unphysical below", fontsize=6, color="0.3",
             ha="right", va="bottom")
    ax1.set_ylim(min(-0.25, ss[0]), ss[-1])
    ax1.set_title("(a) fitted collisional and laser FWHM, one-sigma ellipses\n"
                  "over contours of constant total FWHM (MHz)",
                  fontsize=8.5)
    # Pinned rather than "best": auto-placement put the legend over the 6.00
    # and 6.20 contour labels in the panel's open upper-right corner, which
    # cleared locally by a few pixels and did not on the CI runner's slightly
    # different font metrics. The lower-left corner has no contour label at
    # any campaign condition.
    ax1.legend(fontsize=7, framealpha=1.0, frameon=True, loc="lower left")
    ax1.grid(alpha=0.25, lw=0.5)

    # --- RIGHT: the observable ------------------------------------------
    for pk in PEAK_COLOR:
        m = [i for i, p in enumerate(peaks) if p == pk]
        if not m:
            continue
        o = np.argsort(P[m])
        # Markers only: five powers, and the joining segments crossed each
        # other into a trend the panel's own title says is not there.
        ax2.errorbar(P[m][o], tw[m][o], yerr=twe[m][o], fmt="o", ms=4,
                     lw=1.0, capsize=2, color=PEAK_COLOR[pk], label=f"993.{pk} nm")
    # The same flat-model overlay and between-block band fig2's left panel
    # carries (2026-08-12 audit: this was the last data panel with no model on
    # it). Same construction, this estimator's own numbers: flat line at each
    # peak's weighted mean, band at that peak's RMS about it.
    _pg = np.array([20.0, 230.0])
    for _i, _pk in enumerate(PEAK_COLOR):
        _m = [i for i, p in enumerate(peaks) if p == _pk]
        if not _m:
            continue
        _w = tw[_m]; _e = twe[_m]
        _wt = 1.0 / _e ** 2
        _wb = float(np.sum(_w * _wt) / np.sum(_wt))
        _rm = float(np.sqrt(np.mean((_w - _wb) ** 2)))
        ax2.plot(_pg, [_wb, _wb], "--", color=PEAK_COLOR[_pk], lw=0.9,
                 label="flat fitted model, offset fitted" if _i == 0 else None)
        ax2.fill_between(_pg, _wb - _rm, _wb + _rm, color=PEAK_COLOR[_pk],
                         alpha=0.08, lw=0,
                         label="between-block scatter" if _i == 0 else None)
    ax2.set_xlabel("power (mW)")
    # Estimator named: this is the fitted total width of the joint
    # per-condition fit, which runs above fig2's raw half-maximum widths on
    # every shared condition.
    ax2.set_ylabel("fitted FWHM (MHz)")
    ax2.set_title("(b) fitted FWHM against power", fontsize=9)
    ax2.legend(fontsize=7, framealpha=1.0, frameon=True)
    ax2.grid(alpha=0.25, lw=0.5)

    fig.suptitle("Twenty conditions at 130 °C: the width decomposition and the "
                 "measured total", fontsize=10)
    _footer(fig, "Source: results/linefit_conditions.csv (rb5s6s.stark, rb5s6s.linefit for "
                 "the contour model). Regenerate: python scripts/make_figures.py.")
    _save(fig, "fig10_degeneracy_vs_observable.png")


def fig_laser_history():
    """M20: the laser frequency history, reconstructed PIECEWISE.

    Rebuilt 2026-07-29 after the retraction. The earlier version plotted
    session-referenced offsets as one continuous record and titled itself with a
    65 MHz peak-to-peak excursion; that excursion was the scope's horizontal
    knob (window-start travel x rate = 64.54 MHz against the 64.97 quoted), and
    an offset means nothing across a change of that setting. So the record is
    drawn in DISPLAY EPOCHS -- runs of unchanged window_start_ms -- with a
    visible break at every setting change, because across a break the offset is
    unknown rather than zero.

    Three panels. Left: the two sessions, one connected segment per (epoch,
    line), breaks left empty. Middle: the one long knob-untouched stretch, which
    is a genuine drift measurement. Right: the within-epoch step distribution,
    whose heavy tail is the CAVITY reference being recentred -- a real frequency
    step, unlike a knob move.
    """
    fp = C.RESULTS_DIR / "laser_history.csv"
    if not fp.exists():
        print("  (laser_history.csv absent -- skipping fig11)")
        return
    rows = list(csv.DictReader(open(fp)))
    if not rows or "display_epoch" not in rows[0]:
        print("  (laser_history.csv predates display_epoch -- re-run "
              "run_laser_history.py; skipping fig11)")
        return
    for r in rows:
        r["_t"] = int(r["t_epoch"])
        r["_o"] = float(r["offset_mhz"])
        r["_e"] = int(r["display_epoch"])
    rows.sort(key=lambda r: r["_t"])
    days = sorted({r["session_day"] for r in rows})

    fig, axes = plt.subplots(1, 3, figsize=(15.0, 4.5))

    # ---- panel 1: piecewise record, both sessions side by side --------------
    ax = axes[0]
    xoff, ticks = 0.0, []
    for d in days:
        rs = [r for r in rows if r["session_day"] == d]
        t0 = rs[0]["_t"]
        day_segs = defaultdict(list)
        for r in rs:
            day_segs[(r["_e"], r["peak"])].append(r)
        for (_, pk), g in sorted(day_segs.items()):
            if len(g) < 2:
                continue
            x = [xoff + (r["_t"] - t0) / 3600.0 for r in g]
            ax.plot(x, [r["_o"] for r in g], "-o", ms=2.6, lw=0.9,
                    color=PEAK_COLOR.get(pk, "0.6"), alpha=0.9)
        span = (rs[-1]["_t"] - t0) / 3600.0
        ticks.append((xoff + span / 2, dt_module.datetime.fromtimestamp(t0)
                      .strftime("%m-%d")))
        xoff += span + 0.6
    ax.axhline(0.0, color="0.5", lw=0.8, ls=":")
    ax.set_xticks([t for t, _ in ticks])
    ax.set_xticklabels([lab for _, lab in ticks])
    ax.set_xlabel("time within session (h)")
    ax.set_ylabel("laser detuning (MHz)")
    ax.set_title("(a) line centre through both sessions, one segment per\n"
                 "oscilloscope window setting", fontsize=8.5)
    ax.grid(alpha=0.25, lw=0.5)
    h = [plt.Line2D([], [], color=c, lw=2, label=f"993.{k} nm")
         for k, c in PEAK_COLOR.items()]
    # Upper left, not lower left: the opaque box sat on the largest downward
    # excursions, which are the points that set the spread this panel exists
    # to show.
    # and a blank strip above the record for it to sit in, so that the corner
    # it occupies is not one the segments reach either: at the autoscaled
    # limits it cut the tops off the two tallest upward excursions.
    lo, hi = ax.get_ylim()
    ax.set_ylim(lo, lo + (hi - lo) * 1.28)
    ax.legend(handles=h, fontsize=7, frameon=True, framealpha=0.95, ncol=1,
              loc="upper left")

    # ---- panel 2: the QUIETEST well-sampled segment -------------------------
    # NOT the longest: the longest (75 min) is two bursts 75 min apart with
    # ~13 MHz of internal scatter, so a line through it measures a cavity
    # re-centring between the clusters, not a drift rate. Drawing it is what
    # exposed that. No epoch in the dataset gives a long intervention-free
    # stretch, so the dataset does NOT measure a drift rate; what it does
    # measure is how still the laser sat when nobody touched it.
    ax = axes[1]
    segs = defaultdict(list)
    for r in rows:
        segs[(r["_e"], r["peak"])].append(r)
    cand = []
    for key, g in sorted(segs.items()):
        if len(g) < 6:
            continue
        g = sorted(g, key=lambda r: r["_t"])
        dur = (g[-1]["_t"] - g[0]["_t"]) / 60.0
        yy = [r["_o"] for r in g]
        if dur > 0:
            cand.append((max(yy) - min(yy), key, g, dur))
    if cand:
        cand.sort()
        pp, (_, pk), g, dur = cand[0]
        x = (np.array([r["_t"] for r in g], float) - g[0]["_t"]) / 60.0
        y = [r["_o"] for r in g]
        ax.plot(x, y, "-o", ms=5, lw=1.0,
                color=PEAK_COLOR.get(pk, "0.6"))
        ax.axhline(0.0, color="0.5", lw=0.8, ls=":")
        pad = max(0.15, 0.35 * pp)
        ax.set_ylim(min(y) - pad, max(y) + pad)
        ax.set_xlabel("time into segment (min)")
        ax.set_ylabel("laser detuning (MHz)")
        ax.set_title(f"(b) the quietest well-sampled segment: 993.{pk} nm,\n"
                     f"{len(g)} traces over {dur:.1f} min", fontsize=8.5)
        ax.grid(alpha=0.25, lw=0.5)

    # ---- panel 3: within-epoch steps, the cavity re-centrings --------------
    ax = axes[2]
    steps = []
    by = defaultdict(list)
    for r in rows:
        by[(r["_e"], r["peak"])].append(r)
    for g in by.values():
        g.sort(key=lambda r: r["_t"])
        steps += [abs(b["_o"] - a["_o"]) for a, b in zip(g, g[1:])
                  if 0 < b["_t"] - a["_t"] < 120]
    if steps:
        s = np.array(steps)
        ax.hist(s, bins=np.linspace(0, max(16.0, s.max()), 33),
                color="#0072B2", alpha=0.85)
        med = float(np.median(s))
        ax.axvline(med, color="0.15", lw=1.4, ls="--")
        ax.set_yscale("log")
        ax.set_xlabel("step in line centre (MHz)")
        # The y axis is set to log above, so the scale reads off its own ticks.
        ax.set_ylabel("number of steps")
        ax.set_title("(c) distribution of the step in line centre between\n"
                     "consecutive traces, with the median marked", fontsize=8.5)
        ax.grid(alpha=0.25, lw=0.5, which="both")

    fig.suptitle("The laser line centre through the campaign, reconstructed from "
                 "the traces", fontsize=10.5)
    _footer(fig, "Source: results/laser_history.csv. Regenerate: "
                 "python scripts/run_laser_history.py && python scripts/make_figures.py.")
    _save(fig, "fig11_laser_history.png")


def fig_ramp_construction():
    """How a Gaussian beam becomes a triangular shift distribution (THEORY_NOTE
    section 2, methods chapter 3). The derivation is four lines of change-of-
    variables and the result is the observable the whole analysis rests on, so
    it is worth seeing rather than integrating mentally. Every curve comes from
    rb5s6s.lineshape -- no data, no fitted parameters."""
    from rb5s6s.lineshape import stark_ramp, model_profile
    fig, ax = plt.subplots(1, 4, figsize=(13.6, 3.5))
    S0 = 1.0

    # (a) the beam, and the shift it imposes
    r = np.linspace(0, 2.2, 400)
    u = np.exp(-2 * r ** 2)
    ax[0].plot(r, u, color="#0072B2", lw=1.8)
    ax[0].fill_between(r, 0, u, color="#0072B2", alpha=0.12)
    # Above the peak, not beside it: at dy = -12 the label ran along the top of
    # the Gaussian and the curve passed through its second word.
    # The second label is SHORT, and that is the fix rather than a placement.
    # As "far from the axis the shift goes to zero" it ran out of this panel
    # entirely and landed on panel (b)'s rotated y label, which neither the
    # canvas guard nor the sibling overlap guard could see: it was inside the
    # figure, and the two texts belong to different axes so nothing compared
    # them. Right aligning it clipped it on the left instead, and wrapping it
    # to two lines put the curve through both. The panel is 298 px wide and
    # that sentence is 244 of them, so no placement was ever going to work.
    # The title already says s = -S_0 u, so the marker only needs naming.
    for rr, lab, dx, dy, ha in (
            (0.0, "on axis the shift is $-S_0$", 14, 7, "left"),
            (1.18, r"$s \to 0$ far out", 8, 8, "left")):
        ax[0].plot([rr], [np.exp(-2 * rr ** 2)], "o", color="#D55E00", ms=6)
        ax[0].annotate(lab, (rr, np.exp(-2 * rr ** 2)), fontsize=7, ha=ha,
                       textcoords="offset points", xytext=(dx, dy))
    ax[0].set_ylim(-0.03, 1.12)
    # Set smaller than the other three x labels because it is a definition
    # rather than a name: at the shared size it overhung the panel on both
    # sides and reached the source line under the figure.
    ax[0].set_xlabel("radius $r/w$", fontsize=8.5)
    ax[0].set_ylabel("$u = I/I_0$")
    ax[0].set_title("(a) the beam sets the shift\n$s = -S_0\\,u$", fontsize=9)

    # (b) the two competing weights
    uu = np.linspace(0.02, 1.0, 300)
    # all three normalised to their value on axis (u = 1) so they are comparable
    ax[1].semilogy(uu, 1 / uu, color="0.45", lw=1.6,
                   label=r"atoms per $\mathrm{d}u$: $1/u$")
    ax[1].semilogy(uu, uu ** 2, color="#009E73", lw=1.8,
                   label=r"signal each gives: $u^2$")
    ax[1].semilogy(uu, uu, color="#D55E00", lw=2.2, ls="--",
                   label=r"product: $u$")
    ax[1].set_xlabel("$u = I/I_0$")
    ax[1].set_ylabel("weight, relative to on-axis")
    ax[1].set_title("(b) the two competing weights and their product", fontsize=8)
    ax[1].legend(fontsize=7, framealpha=1.0, frameon=True)

    # (c) the triangle itself
    nu = np.arange(-1.6, 0.4, 0.002)
    ramp = stark_ramp(nu, S0)
    # The skewness of this curve used to be printed in the panel title, from
    # the third standardised moment of the plotted density. It is a result, so
    # it moves to the caption.
    ax[2].plot(nu, ramp, color="#D55E00", lw=1.9)
    ax[2].axvline(-2 / 3 * S0, color="0.35", lw=1.0, ls=":")
    ax[2].annotate("mean $-\\frac{2}{3}S_0$", (-2 / 3 * S0, 2.28), fontsize=7,
                   ha="center", color="0.3")
    ax[2].set_ylim(0, 2.55)
    ax[2].set_xlabel("shift $s/S_0$")
    ax[2].set_ylabel(r"probability density (per unit $s/S_0$)")
    ax[2].set_title("(c) the shift distribution, " r"$f(s)\propto|s|$", fontsize=8)

    # (d) what it does to the line
    g = np.arange(-14, 14, 0.01)
    sym = model_profile(g, gamma_coll=0.45, sigma_laser_fwhm=1.1,
                        transit_fwhm=1.9, s0=0.0)
    ramped = model_profile(g, gamma_coll=0.45, sigma_laser_fwhm=1.1,
                           transit_fwhm=1.9, s0=3.0)
    ax[3].plot(g, sym / sym.max(), color="0.5", lw=1.4, label="$S_0=0$")
    ax[3].plot(g, ramped / ramped.max(), color="#D55E00", lw=1.9,
               label="$S_0=3$ MHz")
    ax[3].set_xlabel("two-photon detuning (MHz)")
    ax[3].set_ylabel("normalised signal")
    ax[3].set_title("(d) the line the distribution produces", fontsize=8)
    ax[3].legend(fontsize=7, framealpha=1.0, frameon=True)

    for a in ax:
        a.grid(alpha=0.22, lw=0.5)
    fig.suptitle("From the beam profile to the shift distribution and the line "
                 "it produces", fontsize=10)
    _footer(fig, "Source: rb5s6s.lineshape (stark_ramp, model_profile). No data, no fitted "
                 "parameters. Regenerate: python scripts/make_figures.py.")
    _save(fig, "fig12_ramp_construction.png")


def fig_level_scheme():
    """What transition is driven and what is detected, drawn in the standard
    AMO term-diagram idiom (columns by orbital angular momentum, no numeric
    energy axis, wavelengths on the arrows -- the community convention, and
    the style of the 993 nm reference literature's own Fig. 1a). S levels on
    the left column, P levels on the right; the 993 nm virtual level is a
    dash at half the two-photon energy, BELOW the real 5P_1/2. The 5P
    fine-structure splitting (237.6 cm^-1, 1.2% of the span) is enlarged for
    visibility and the panel says so. 795 nm is the detected cascade arm and
    780 nm is real but filtered out (~50 dB, docs/APPARATUS.md sec. 3).

    Every arrow carries the fraction of the cascade it takes, computed at draw
    time from the Einstein A coefficients (experimenter request, 2026-08-12). The
    reading that matters is that THE DETECTED ARM IS THE MINORITY ONE: the
    6S->5P_3/2 leg is twice as strong as 6S->5P_1/2 (A ratio 1.93), so 66 per
    cent of every 6S decay leaves through 1367 nm and then 780 nm, which the
    filters reject, and the 795 nm the detector counts is the remaining 34 per
    cent. That factor sits in front of every absolute rate this record quotes
    and was previously stated nowhere on the figure.

    Right panels: the real cavity scan, digitised from a photograph
    (docs/apparatus/2025-06-12_cavity_scan_IMG_2508_digitised.csv). Only the
    UP-sweep is shown: the down-sweep's amplitudes are display-compressed in
    the photograph and would misrepresent the strengths, and the degeneracy
    plus abundance law is a statement about spike INTEGRALS, which the
    photograph cannot carry (those come from the digitised record, via
    rb5s6s.cavity_scan; the full reading lives in APPARATUS section 6).

    The caption states the population-law PREDICTIONS and, beside each, what
    rb5s6s.cavity_scan integrates from the committed digitisation at draw
    time -- no measured number in the caption is typed in. See the comment at
    the caption for the 2026-08-05 history of what it may claim.
    """
    # E_5P12_CM/E_5P32_CM read from rb5s6s.polarizability -- the same NIST ASD
    # term energies that module's own 5S->5P matrix elements are keyed to,
    # rather than re-derived here from the D-line vacuum wavelengths
    # independently (the two used to agree only to ~0.01 nm by coincidence of
    # rounding, not by construction).
    from rb5s6s.polarizability import E_6S_CM, E_5P12_CM, E_5P32_CM
    LAM_6S_5P12_NM = 1.0e7 / (E_6S_CM - E_5P12_CM)   # 1324 nm, detected arm
    LAM_6S_5P32_NM = 1.0e7 / (E_6S_CM - E_5P32_CM)   # 1367 nm, rejected arm

    # HOW MUCH OF THE CASCADE EACH ARM CARRIES (experimenter request, 2026-08-12).
    # The figure named the four wavelengths and left the reader to assume the
    # split, which matters because the detected arm is the MINORITY one: the
    # 780 nm arm is not merely filtered, it is also the larger half.
    #
    # Computed from the same Einstein A coefficients the trapping study uses
    # (scripts/run_trapping_channels._leg on rb5s6s.polarizability line data),
    # not typed. 5P is the lowest excited state, so each first leg reaches the
    # ground state with unit probability and the SAME fraction labels the
    # second leg: 1324 with 795, and 1367 with 780. That identity is why one
    # number can sit on both arrows of a cascade arm.
    sys.path.insert(0, str(C.REPO_ROOT / "scripts"))
    from run_trapping_channels import _leg as _leg_A, LINES_6S as _L6S
    _a12 = _leg_A(*_L6S[0][:2])[1]
    _a32 = _leg_A(*_L6S[1][:2])[1]
    _b12 = 100.0 * _a12 / (_a12 + _a32)
    _b32 = 100.0 * _a32 / (_a12 + _a32)

    fig = plt.figure(figsize=(13.0, 6.2))
    # bottom reserves the strip the caption and the footer share: the caption
    # is three lines and printed through the footer at 0.105.
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.45], wspace=0.06,
                          left=0.02, right=0.99, top=0.86, bottom=0.155)
    ax = fig.add_subplot(gs[0, 0])
    bx = fig.add_subplot(gs[0, 1])

    # --- left: Nieddu-Fig-1a-style term diagram, columns by L -----------
    y5s, y5p12, y5p32, y6s, yv = 0.0, 0.615, 0.655, 1.0, 0.5
    ax.axis("off")
    ax.set_xlim(0.0, 1.05)
    ax.set_ylim(-0.16, 1.13)
    # S column
    ax.hlines(y5s, 0.10, 0.36, color="0.15", lw=2.2)
    ax.hlines(y6s, 0.10, 0.36, color="0.15", lw=2.2)
    ax.hlines(yv, 0.15, 0.31, color="0.55", lw=1.2, ls=(0, (4, 3)))
    ax.text(0.23, y6s + 0.035, r"$6S_{1/2}$", ha="center", fontsize=11)
    ax.text(0.23, y5s - 0.042, r"$5S_{1/2}$", ha="center", fontsize=11)
    # P column (fine-structure splitting enlarged for visibility)
    ax.hlines(y5p12, 0.50, 0.74, color="0.15", lw=2.2)
    ax.hlines(y5p32, 0.58, 0.82, color="0.15", lw=2.2)
    ax.text(0.76, y5p12 - 0.012, r"$5P_{1/2}$", ha="left", fontsize=10)
    ax.text(0.84, y5p32 - 0.012, r"$5P_{3/2}$", ha="left", fontsize=10)
    # two 993 nm photons up the S column
    for y0, y1 in ((y5s, yv), (yv, y6s)):
        ax.annotate("", (0.23, y1), (0.23, y0),
                    arrowprops=dict(arrowstyle="-|>", color="#a63430", lw=2.2))
    ax.text(0.205, 0.25, "993 nm", rotation=90, color="#a63430", fontsize=9,
            ha="right", va="center", fontweight="bold")
    ax.text(0.205, 0.75, "993 nm", rotation=90, color="#a63430", fontsize=9,
            ha="right", va="center", fontweight="bold")
    ax.text(0.33, yv - 0.045, "virtual level", fontsize=7.5, color="0.45")
    # cascade, first legs (infrared, not detected here)
    ax.annotate("", (0.56, y5p12 + 0.008), (0.30, y6s - 0.008),
                arrowprops=dict(arrowstyle="-|>", color="0.5", lw=1.3,
                                 ls=(0, (4, 3))))
    # The text rotation and the arrow's on-screen angle differ (the panel is
    # not square, so equal steps in x and y are not equal on the canvas), and
    # the dashes crossed the digits of this one. The white patch behind it
    # breaks the line where the label sits, which is what its sibling below
    # achieves by standing clear of its own arrow.
    ax.text(0.365, 0.86, f"{LAM_6S_5P12_NM:.0f} nm, {_b12:.0f}%", rotation=-54,
            fontsize=7.5, color="0.45",
            ha="center", va="center",
            bbox=dict(boxstyle="square,pad=0.22", fc="white", ec="none"))
    ax.annotate("", (0.66, y5p32 + 0.008), (0.335, y6s - 0.008),
                arrowprops=dict(arrowstyle="-|>", color="0.5", lw=1.3,
                                 ls=(0, (4, 3))))
    ax.text(0.50, 0.885, f"{LAM_6S_5P32_NM:.0f} nm, {_b32:.0f}%", rotation=-44,
            fontsize=7.5, color="0.45",
            ha="center", va="center")
    # cascade, second legs: 795 detected (red), 780 filtered out (grey)
    ax.annotate("", (0.295, y5s + 0.008), (0.545, y5p12 - 0.008),
                arrowprops=dict(arrowstyle="-|>", color="#d62728", lw=2.2))
    ax.text(0.365, 0.295, f"795 nm, {_b12:.0f}%", rotation=64, fontsize=9,
            color="#d62728",
            ha="center", va="center", fontweight="bold")
    ax.annotate("", (0.335, y5s + 0.008), (0.625, y5p32 - 0.008),
                arrowprops=dict(arrowstyle="-|>", color="0.55", lw=1.4))
    ax.text(0.545, 0.275, f"780 nm, {_b32:.0f}%", rotation=62, fontsize=7.5,
            color="0.45",
            ha="center", va="center")
    # The two statements this panel used to carry under the term diagram (which
    # arm is detected and by how much the other is suppressed, and that the 5P
    # fine-structure splitting is enlarged) are caption material. The apparatus
    # numbers are in docs/APPARATUS.md sec. 3.

    # --- right: the scan as photographed, annotated -------------------
    # The photograph IS the record (2025-06-12 scope screen). The digitised
    # CSV stays committed as the quantitative backing for the integral
    # statement; it is cited in the footer, not drawn, because the
    # digitisation undersamples the peaks and misstates their heights.
    # The bench photographs travel with the record, not the public
    # mirror, so a checkout without them keeps its committed PNG.
    import matplotlib.patheffects as pe
    photo_path = (C.REPO_ROOT / "docs" / "reference_setup" / "photos"
                  / "IMG_2508.jpeg")
    if not photo_path.exists():
        plt.close(fig)
        print("fig13: bench photograph not in this checkout, keeping the "
              "existing PNG")
        return
    photo = plt.imread(photo_path)
    # Cropped to the waveform area: the instrument's side menu used to bleed
    # off the right edge of the canvas with its labels cut mid-word, and the
    # bottom row of the display was clipped the same way. The label positions
    # below are given in the photograph's own pixels and converted through
    # this crop, so moving the crop moves the labels with their features.
    PHOTO_TOP, PHOTO_BOT, PHOTO_LEFT, PHOTO_RIGHT = 182, 2440, 364, 3560
    bx.imshow(photo[PHOTO_TOP:PHOTO_BOT, PHOTO_LEFT:PHOTO_RIGHT])
    bx.axis("off")
    bx.set_title("the cavity scan, as photographed (500 ms/div)",
                 fontsize=10)
    fx = [pe.withStroke(linewidth=2.2, foreground="black")]

    def _frac(px, py):
        """The photograph's own pixel grid, as a fraction of the drawn crop."""
        return ((px - PHOTO_LEFT) / (PHOTO_RIGHT - PHOTO_LEFT),
                1.0 - (py - PHOTO_TOP) / (PHOTO_BOT - PHOTO_TOP))

    def lab(px, py, s, point=None, **kw):
        """Place a label at (px, py) in the photograph's own pixel grid.

        point, when given, is a second pair of photograph pixels: the feature
        the label names. A leader line is then drawn from the edge of the text
        to that feature, so the label can stand in clear screen area and the
        pairing is still stated. The four component labels all carry one: the
        two innermost spikes of the up-sweep sit close to the ramp apex and to
        the first mirrored spike, and which of them a label belonged to was
        left to the reader."""
        kw.setdefault("ha", "center")
        x, y = _frac(px, py)
        if point is None:
            bx.text(x, y, s, transform=bx.transAxes, fontsize=8.5,
                    color="white", path_effects=fx, **kw)
            return
        bx.annotate(s, xy=_frac(*point), xytext=(x, y),
                    xycoords=bx.transAxes, textcoords=bx.transAxes,
                    fontsize=8.5, color="white", path_effects=fx,
                    arrowprops=dict(arrowstyle="-|>", color="white", lw=1.1,
                                    shrinkA=1.0, shrinkB=1.5,
                                    path_effects=fx), **kw)

    # Each component label now stands in blank screen area and points at its
    # own spike. Before, the first one overlapped the trigger markers at the
    # left edge and its own spike tip, the third had its last character on the
    # yellow ramp, and the fourth sat centred above BOTH the last up-sweep
    # spike and the first mirrored one.
    lab(520, 1180, "⁸⁷Rb\nF=2", point=(497, 1345), va="bottom")
    lab(876, 487, "⁸⁵Rb F=3", point=(808, 700), va="bottom", ha="left")
    lab(1400, 700, "⁸⁵Rb F=2", point=(1488, 965), va="bottom")
    lab(1960, 1430, "⁸⁷Rb F=1", point=(2041, 1700), va="bottom", ha="right")
    lab(2357, 483, "ramp apex", va="bottom", ha="left")
    lab(1040, 1200, "cavity-scan ramp", ha="left")
    lab(2411, 2322, "795 nm fluorescence", ha="left")
    # Below the descending ramp instead of across it, in the gap between the
    # second and third mirrored spikes.
    lab(3050, 1900, "down-sweep:\nthe same four,\nmirrored", va="center")

    # The population-law reading of this scan (the (2F+1) and abundance
    # predictions, the integrals rb5s6s.cavity_scan takes from the committed
    # digitisation under its own stated rules, the rule-dependence band, and
    # the warning that the display compresses the tallest spikes so heights are
    # not read for ratios) used to be printed here as a three-line paragraph.
    # It is caption material. Every number in it is computed by
    # rb5s6s.cavity_scan.read_scan() and tabulated in
    # results/cavity_scan_integrals.csv, with the rules and caveats in
    # docs/APPARATUS.md sec. 6.
    fig.suptitle(
        r"The 993 nm two-photon line: excitation, detection, and the scan "
        "across it", fontsize=12.5, y=0.965)
    # Wrapped: one line ran off the right edge of the canvas and the
    # regenerate command was cut mid-word.
    _footer(fig, "Sources: rb5s6s.constants + polarizability (level scheme) + rb5s6s.cavity_scan "
                 "(integrals of docs/apparatus/2025-06-12_cavity_scan_IMG_2508_digitised.csv, "
                 "also in results/cavity_scan_integrals.csv).\n"
                 "Photograph docs/reference_setup/photos/IMG_2508.jpeg (oscilloscope screen, "
                 "2025-06-12, cropped). "
                 "Regenerate: python scripts/make_figures.py.")
    _save(fig, "fig13_level_scheme.png")



def fig_hyperfine_pumping():
    """The second width companion: why a real decay ends an atom's
    participation in the line, what the branching actually is, and what the
    omission costs.

    REDRAWN 2026-08-10 on the experimenter's reading. The first version drew 5P as one
    level, and its middle and right panels were not readable: two abstract bars
    of a decay probability, and three bars whose relation to the fit was in a
    text box. What the panels needed was the arithmetic itself.

    Panel (a) resolves the fine structure the way fig13 does, with the 5P
    splitting enlarged for visibility and said so, because the two legs carry
    different branchings and different cascade wavelengths. Panel (b) is the
    branching computation, per isotope, which turns out to be exact rather than
    bracketed: with the 5P hyperfine sublevels populated statistically the
    return to a ground level is the pure degeneracy weight (2F+1)/sum(2F+1),
    identical from 5P1/2 and 5P3/2, verified against explicit 6j symbols. So f
    is a number per line and not a factor-of-two bracket. Panel (c) draws what
    the fit sees against what it attributes, which is the actual claim.

    THE CONSEQUENCE THAT CHANGED A CLAIM. f differs across the four lines,
    0.375 to 0.625, while the ramp and the saturation do not, because the
    two-photon Rabi frequency is F-independent here (constants.ABUNDANCE_RB85
    note). So the three same-signature terms are NOT degenerate across the line
    index, only across power and waist. The lever is 7 kHz between the extreme
    lines against an 88 kHz per-block width scatter, so this dataset cannot
    spend it, but it is a real handle for a session that can.
    """
    import math
    sys.path.insert(0, str(C.REPO_ROOT / "scripts"))
    from run_geometry_design import ramp_moments            # noqa: E402
    from rb5s6s import stark                                # noqa: E402
    from rb5s6s.constants import GAMMA_NAT_HZ               # noqa: E402
    from rb5s6s.polarizability import E_6S_CM, LINES_6S     # noqa: E402

    G_MHZ = GAMMA_NAT_HZ / 1e6
    W0, ZC_M, P_MAX = C.W0_MEASURED_M, 2.2e-3, 0.225
    GC, SL, TR = 0.60, 1.50, 0.96
    NU = np.linspace(-40.0, 40.0, 200001)

    # the two cascade legs, from the same NIST elements fig13 reads
    A0_M, E_C_SI = 5.29177210903e-11, 1.602176634e-19
    HBAR, EPS0, CL = 1.054571817e-34, 8.8541878128e-12, 2.99792458e8

    def _leg(e_cm, d_au):
        lam = 1e7 / (E_6S_CM - e_cm) * 1e-9
        w = 2.0 * math.pi * CL / lam
        d = d_au * E_C_SI * A0_M
        return lam, w ** 3 * d ** 2 / (3.0 * math.pi * EPS0 * HBAR * CL ** 3 * 2)

    lam12, a12 = _leg(*LINES_6S[0][:2])
    lam32, a32 = _leg(*LINES_6S[1][:2])
    b12 = a12 / (a12 + a32)

    m = ramp_moments(W0, P_MAX, ZC_M)
    ramp_khz = 1e3 * (stark._fwhm_of(GC, SL, TR, m["s0"], NU)
                      - stark._fwhm_of(GC, SL, TR, 0.0, NU))
    sat_khz = 1e3 * G_MHZ * (math.sqrt(1.0 + m["sat_w"]) - 1.0)

    # f per line, from the TWO-STEP cascade. The two-photon operator is
    # scalar (K = 0 only), so 6S is populated in ONE hyperfine level and
    # not statistically, and the branching is the product of the two
    # cascade steps weighted by the legs' Einstein A shares. Each leg
    # scales the naive degeneracy weight by a clean fraction, 8/9 through
    # 5P1/2 and 4/9 through 5P3/2, so the combination is uniform across the
    # four lines: the LEVER is unchanged and the SCALE is not. Computed
    # with explicit 6j symbols. The first pass here assumed a statistical
    # 6S population and was wrong by exactly this factor.
    LEG_RATIO = {0.5: 8.0 / 9.0, 1.5: 4.0 / 9.0}
    corr = b12 * LEG_RATIO[0.5] + (1.0 - b12) * LEG_RATIO[1.5]
    LINES = [("993.4121", "$^{87}$Rb", 1, (1, 2)), ("993.4154", "$^{85}$Rb", 2, (2, 3)),
             ("993.4192", "$^{85}$Rb", 3, (2, 3)), ("993.4207", "$^{87}$Rb", 2, (1, 2))]
    fvals = []
    for lam_nm, iso, f_driven, fs in LINES:
        other = [x for x in fs if x != f_driven][0]
        stat = (2 * other + 1) / sum(2 * x + 1 for x in fs)
        fvals.append((lam_nm, iso, f_driven, other, stat * corr))

    fig = plt.figure(figsize=(14.2, 5.0))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.15, 1.05, 0.95], wspace=0.32,
                          left=0.045, right=0.985, top=0.88, bottom=0.26)
    ax, bx, cx = (fig.add_subplot(gs[0, i]) for i in range(3))

    # ---- (a) the cascade, fine structure resolved -----------------------
    ax.axis("off")
    ax.set_xlim(0.0, 1.08)
    ax.set_ylim(-0.30, 1.16)
    yF, yFp, y5p12, y5p32, y6s, yv = 0.0, 0.15, 0.56, 0.63, 1.0, 0.50
    DRIVE, LOST = "#a63430", "#111111"
    ax.hlines(yF, 0.10, 0.455, color="0.15", lw=2.4)
    ax.hlines(yFp, 0.10, 0.455, color="0.15", lw=2.4)
    ax.text(0.235, yF - 0.055, r"$5S_{1/2}$, $F$", ha="center", fontsize=9)
    ax.text(0.235, yFp + 0.035, r"$5S_{1/2}$, $F'$", ha="center", fontsize=9)
    ax.annotate("", (0.455, yFp), (0.455, yF),
                arrowprops=dict(arrowstyle="<->", color="0.45", lw=1.0))
    ax.text(0.60, -0.02,
            "ground splitting\n3.04 GHz ($^{85}$Rb)\n6.83 GHz ($^{87}$Rb)",
            ha="left", va="top", fontsize=7.0, color="0.35")
    ax.hlines(y6s, 0.07, 0.42, color="0.15", lw=2.4)
    ax.text(0.245, y6s + 0.05, r"$6S_{1/2}$", ha="center", fontsize=10)
    # the two 5P levels, splitting enlarged as fig13 does
    ax.hlines(y5p12, 0.56, 0.86, color="0.15", lw=2.4)
    ax.hlines(y5p32, 0.64, 0.94, color="0.15", lw=2.4)
    ax.text(0.875, y5p12 - 0.012, r"$5P_{1/2}$", ha="left", fontsize=9)
    ax.text(0.955, y5p32 - 0.012, r"$5P_{3/2}$", ha="left", fontsize=9)
    # This label starts at 0.955 and is wider than the 0.045 left to the old
    # xlim of 1.0, so it hung outside the panel and into the gap before the
    # right panel. Widening the canvas rather than shrinking the type keeps
    # every element in the same place relative to every other one.
    ax.hlines(yv, 0.135, 0.29, color="0.55", lw=1.1, ls=(0, (4, 3)))
    ax.text(0.30, yv, "virtual level", fontsize=6.8, color="0.45", va="center")
    for y0, y1 in ((yF, yv), (yv, y6s)):
        ax.annotate("", (0.205, y1), (0.205, y0),
                    arrowprops=dict(arrowstyle="-|>", color=DRIVE, lw=2.3))
    ax.text(0.185, 0.5 * (yF + y6s), "993 nm, twice", rotation=90, fontsize=8.2,
            color=DRIVE, ha="right", va="center", fontweight="bold")
    ax.annotate("", (0.585, y5p12 + 0.02), (0.35, y6s - 0.02),
                arrowprops=dict(arrowstyle="-|>", color="0.45", lw=1.5,
                                ls=(0, (4, 3))))
    ax.annotate("", (0.665, y5p32 + 0.02), (0.40, y6s - 0.02),
                arrowprops=dict(arrowstyle="-|>", color="0.45", lw=1.5,
                                ls=(0, (4, 3))))
    ax.text(0.40, 0.855, f"{lam12*1e9:.0f} nm\n{100*b12:.0f}%", fontsize=7.2,
            color="0.35", ha="center", va="center",
            bbox=dict(boxstyle="square,pad=0.12", fc="white", ec="none"))
    ax.text(0.585, 0.90, f"{lam32*1e9:.0f} nm\n{100*(1-b12):.0f}%", fontsize=7.2,
            color="0.35", ha="center", va="center")
    ax.annotate("", (0.40, yF + 0.02), (0.60, y5p12 - 0.02),
                arrowprops=dict(arrowstyle="-|>", color=DRIVE, lw=1.6))
    ax.annotate("", (0.40, yFp + 0.02), (0.70, y5p32 - 0.02),
                arrowprops=dict(arrowstyle="-|>", color=LOST, lw=2.6))
    ax.text(0.62, 0.30, "to $F'$: out of\nthe line for good",
            fontsize=7.6, color=LOST, ha="left", va="bottom", fontweight="bold")
    ax.text(0.62, 0.09, "back to $F$:\nstill in the line",
            fontsize=7.4, color=DRIVE, ha="left", va="bottom")
    ax.set_title("(a)  the cascade, and where an atom can be lost",
                 fontsize=10.5, loc="left")
    ax.text(0.0, -0.255, "$5P$ splitting enlarged for visibility, as in fig13",
            fontsize=6.9, color="0.45", ha="left", transform=ax.transData)

    # ---- (b) the branching, computed per line ---------------------------
    bx.axis("off")
    bx.set_xlim(0, 1); bx.set_ylim(0, 1)
    bx.set_title("(b)  the branching factor $f$, line by line", fontsize=10.5,
                 loc="left")
    bx.text(0.0, 0.96,
            "The two-photon operator is scalar, so $6S$ is populated in ONE\n"
            "hyperfine level, not statistically. $f$ is then the product of the\n"
            "two cascade steps, with 6j symbols throughout:",
            fontsize=8.0, color="0.15", va="top")
    bx.text(0.5, 0.735,
            r"$f = \dfrac{2F'+1}{\sum_F (2F+1)}\;\times\;"
            r"\left(\dfrac{8}{9}b_{1/2}+\dfrac{4}{9}b_{3/2}\right)$",
            fontsize=11.5, ha="center", va="center")
    bx.text(0.0, 0.615, "The first factor is the naive weight of the level NOT\n"
                        "driven. The second is what the cascade costs it, "
                        f"{corr:.3f},\nthe same for all four lines:",
            fontsize=8.0, color="0.15", va="top")
    rows = []
    for lam, iso, fd, oth, fv in fvals:
        stat_num = 2 * oth + 1
        stat_den = int(round(stat_num / (fv / corr)))
        rows.append((f"{lam} nm", iso, f"$F$ = {fd}",
                     f"{stat_num}/{stat_den}", f"{fv:.3f}",
                     f"{fv*sat_khz:.1f} kHz"))
    y0 = 0.405
    bx.text(0.02, y0 + 0.050, "line", fontsize=7.6, fontweight="bold")
    bx.text(0.30, y0 + 0.050, "driven", fontsize=7.6, fontweight="bold")
    bx.text(0.47, y0 + 0.050, "naive", fontsize=7.6, fontweight="bold")
    bx.text(0.60, y0 + 0.050, "$f$", fontsize=7.6, fontweight="bold")
    bx.text(0.76, y0 + 0.050, "pumping", fontsize=7.6, fontweight="bold")
    for k, (lam, iso, fd, frac, fv, wid) in enumerate(rows):
        y = y0 - 0.058 * k
        bx.text(0.02, y, f"{lam} {iso}", fontsize=7.8, va="center")
        bx.text(0.30, y, fd, fontsize=7.8, va="center")
        bx.text(0.47, y, frac, fontsize=7.8, va="center")
        bx.text(0.60, y, fv, fontsize=7.8, va="center")
        bx.text(0.76, y, wid, fontsize=7.8, va="center")
    # The blocked level per line, derived from the selection rules at draw
    # time rather than looked up. Of the 5P3/2 levels a driven 6S level can
    # feed (|dF| <= 1), the one more than one step from the UNDRIVEN ground
    # level cannot decay to it at all, because a J = 1 photon cannot change F
    # by two. It returns the atom to the level it came from, so it is not a
    # loss, and every one of the four lines has one.
    blocked = []
    for lam, iso, fd, oth, _ in fvals:
        for fp in (fd - 1, fd, fd + 1):
            if fp >= 0 and abs(fp - oth) > 1:
                blocked.append(str(fp))
    bx.text(0.0, 0.02,
            "Blocked $5P_{3/2}$ levels ($F$ = " + ", ".join(blocked)
            + " by row).",
            fontsize=7.8, color="0.25", va="bottom")

    # ---- (c) what the fit sees against what it attributes ---------------
    f_lo, f_hi = min(v[4] for v in fvals), max(v[4] for v in fvals)
    pump_lo, pump_hi = f_lo * sat_khz, f_hi * sat_khz
    cx.bar([0], [ramp_khz], width=0.55, color="#a63430", edgecolor="0.2", lw=0.8)
    cx.bar([1], [ramp_khz], width=0.55, color="#a63430", edgecolor="0.2", lw=0.8)
    cx.bar([1], [sat_khz], bottom=[ramp_khz], width=0.55, color="#0072B2",
           edgecolor="0.2", lw=0.8)
    cx.bar([1], [pump_hi], bottom=[ramp_khz + sat_khz], width=0.55,
           color="#009E73", edgecolor="0.2", lw=0.8)
    cx.errorbar([1], [ramp_khz + sat_khz + 0.5 * (pump_lo + pump_hi)],
                yerr=[[0.5 * (pump_hi - pump_lo)], [0.5 * (pump_hi - pump_lo)]],
                fmt="none", ecolor="0.15", elinewidth=1.5, capsize=4)
    total = ramp_khz + sat_khz + pump_hi
    cx.set_xticks([0, 1])
    cx.set_xticklabels(["what the model\ncontains", "what the line\nactually does"],
                       fontsize=8.6)
    cx.set_ylabel(f"added linewidth at {P_MAX*1e3:.0f} mW (kHz)")
    cx.set_ylim(0, total * 1.62)
    cx.grid(axis="x", visible=False)
    cx.set_title("(c)  the width budget at 225 mW", fontsize=10.5,
                 loc="left")
    cx.text(0, ramp_khz + 0.8, f"{ramp_khz:.1f}", ha="center", fontsize=9,
            fontweight="bold")
    cx.text(1, total + 0.8, f"{total:.0f}", ha="center", fontsize=9,
            fontweight="bold")
    cx.annotate("the AC-Stark ramp", xy=(1, ramp_khz * 0.5),
                xytext=(1.42, ramp_khz * 0.5), fontsize=7.6, color="#a63430",
                va="center", ha="left")
    cx.annotate("atomic saturation", xy=(1, ramp_khz + sat_khz * 0.5),
                xytext=(1.42, ramp_khz + sat_khz * 0.5), fontsize=7.6,
                color="#0072B2", va="center", ha="left")
    cx.annotate("hyperfine pumping", xy=(1, ramp_khz + sat_khz + pump_hi * 0.5),
                xytext=(1.42, ramp_khz + sat_khz + pump_hi * 0.5), fontsize=7.6,
                color="#009E73", va="center", ha="left")
    cx.set_xlim(-0.55, 2.35)
    cx.text(0.5, 0.965,
            f"the fit assigns the whole right-hand bar\n"
            f"to the left-hand one, so the bound comes\n"
            f"out {total/ramp_khz:.1f} times too loose",
            transform=cx.transAxes, fontsize=7.8, color="0.25", ha="center",
            va="top")

    # 0.155 left a 3 px gap to the footer once this caption grew to five
    # lines, which is a collision waiting for the next sentence.
    fig.text(0.045, 0.175,
             "Lever 4 kHz between the extreme lines, against 88 kHz of "
             "per-block width scatter.",
             fontsize=7.6, color="0.3", va="top")
    _footer(fig, "figure 23 | rb5s6s.polarizability line data (the two cascade "
                 "legs and their branching), rb5s6s.stark._fwhm_of, "
                 "scripts/run_geometry_design.ramp_moments | "
                 "docs/notes/two_photon_saturation_companion.md | "
                 "python scripts/make_figures.py")
    _save(fig, "fig23_hyperfine_pumping.png", rect=(0, 0.185, 1, 1))


def fig_weak_field_limit():
    """Where the ramp law's own assumption stops holding, and what it costs
    the session that would exploit it.

    WHY THIS FIGURE EXISTS. The whole ramp construction rests on the detected
    signal going as the SQUARE of the intensity, which is what makes the shift
    distribution triangular and its skewness non-zero. That is the leading
    term of the excited fraction and not the fraction itself: the real weight
    is (s/2)/(1+s), which is quadratic in intensity only while s is small.
    The dataset sits comfortably inside that regime. The small-waist session
    the record reaches for does not, and the reason is a scaling accident
    worth drawing: s carries the two-photon Rabi frequency squared, so it goes
    as the FOURTH power of the inverse waist, while the shift itself goes only
    as the second. Tightening the focus therefore leaves the weak-field limit
    four times faster than it buys shift.

    Panel (a) is the weight against the approximation it replaces. Panel (b)
    is the consequence the plan cares about: the predicted third-cumulant
    skewness against waist, computed both ways. The sign flip survives, the
    magnitude does not, so the tight-focus prediction is a factor-of-three
    statement whose uncertainty is a modelling assumption rather than an
    unmeasured input.

    Both panels come from scripts/run_geometry_design.ramp_moments, whose
    weak-field branch is the one already checked against
    lineshape.stark_ramp_axial_moments.
    """
    sys.path.insert(0, str(C.REPO_ROOT / "scripts"))
    from run_geometry_design import ramp_moments            # noqa: E402

    ZC_M, P_MAX = 2.2e-3, 0.225
    W0 = C.W0_MEASURED_M
    waists_um = np.array([64, 56, 48, 40, 36, 32, 28, 24, 20, 18, 16], float)
    rows = [(w, ramp_moments(w * 1e-6, P_MAX, ZC_M, saturate=True),
             ramp_moments(w * 1e-6, P_MAX, ZC_M, saturate=False))
            for w in waists_um]
    g1_sat = np.array([r[1]["g1"] for r in rows])
    g1_weak = np.array([r[2]["g1"] for r in rows])
    s_axis = np.array([r[1]["sat00"] for r in rows])
    s0_here = rows[0][1]["s0"]
    s_here, s_tight = s_axis[0], s_axis[-1]

    fig = plt.figure(figsize=(12.2, 4.6))
    gs = fig.add_gridspec(1, 2, wspace=0.26, left=0.065, right=0.985,
                          top=0.88, bottom=0.27)
    ax, bx = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])

    # ---- (a) the weight, against the square law it replaces -------------
    ss = np.logspace(-3, 1.2, 400)
    ax.plot(ss, (ss / 2.0) / (1.0 + ss), color="#0072B2", lw=2.4,
            label=r"what the atom does, $(s/2)/(1+s)$")
    ax.plot(ss, ss / 2.0, color="0.35", lw=1.8, ls=(0, (5, 3)),
            label=r"the ramp law's assumption, $\propto I^2$")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("saturation parameter $s$ on the beam axis")
    ax.set_ylabel("excited fraction")
    ax.set_title("(a)  the square law is the weak-field corner of a curve",
                 fontsize=10.5, loc="left")
    ax.legend(fontsize=8.2, loc="upper left")
    # the dataset marker sits low (the legend owns the top left) and the
    # proposed one high (the text block owns the bottom right), so neither
    # label lands on the legend, the curves or the other annotation
    for x, lab, col, y, va in (
            (s_here, f"this dataset\n{W0*1e6:.0f} µm, $s$ = {s_here:.3f}",
             "#009E73", 1.6e-3, "top"),
            (s_tight, f"the proposed\n{waists_um[-1]:.0f} µm, "
                      f"$s$ = {s_tight:.1f}", "#D55E00", 7.0, "top")):
        ax.axvline(x, color=col, lw=1.5, ls=":")
        # boxed: the proposed-waist label is drawn across the dashed square-law
        # line, which stays legible only with the surface behind it
        ax.text(x * 0.86, y, lab, fontsize=8.0, color=col, ha="right", va=va,
                bbox=dict(facecolor="white", edgecolor="none", alpha=0.82,
                          pad=1.2))
    # raised off the floor: at y = 0.05 this block's left edge reached the
    # dataset marker's label and covered a fifth of it, which the overlap guard
    # could not see until 2026-08-11 because it was skipping this figure
    ax.text(0.985, 0.20,
            f"Four-fold tightening: {s_tight/s_here:.0f}x in $s$, "
            f"{(W0*1e6/waists_um[-1])**2:.0f}x in the shift.",
            transform=ax.transAxes, fontsize=7.8, color="0.25",
            ha="right", va="bottom")

    # ---- (b) what it does to the observable ----------------------------
    bx.axhline(0.0, color="0.5", lw=1.0)
    bx.plot(waists_um, g1_weak, "o-", color="0.35", lw=1.8, ms=4.5,
            label="predicted with the square law")
    bx.plot(waists_um, g1_sat, "o-", color="#0072B2", lw=2.4, ms=5,
            label="predicted with the real weight")
    bx.fill_between(waists_um, g1_weak, g1_sat, color="#0072B2", alpha=0.16, lw=0)
    bx.invert_xaxis()
    bx.set_xlabel("beam waist $w_0$ (µm), tightening to the right")
    bx.set_ylabel("predicted skewness $g_1$ of the ramp")
    bx.set_title("(b)  the sign survives it, the size does not",
                 fontsize=10.5, loc="left")
    bx.legend(fontsize=8.2, loc="center left")
    bx.annotate(f"{g1_weak[-1]:+.2f} against {g1_sat[-1]:+.2f}\n"
                f"at {waists_um[-1]:.0f} µm: a factor "
                f"{abs(g1_sat[-1]/g1_weak[-1]):.1f}",
                xy=(waists_um[-1], 0.5 * (g1_sat[-1] + g1_weak[-1])),
                xytext=(0.42, 0.30), textcoords="axes fraction", fontsize=8.2,
                arrowprops=dict(arrowstyle="-|>", color="0.4", lw=1.0))
    bx.text(0.025, 0.05,
            f"at this dataset's own {W0*1e6:.0f} µm the two agree to "
            f"{100*abs(g1_sat[0]/g1_weak[0]-1):.0f} per cent,\n"
            f"so no result of this dataset is affected",
            transform=bx.transAxes, fontsize=7.8, color="0.25",
            ha="left", va="bottom")

    fig.text(0.065, 0.155,
             f"{P_MAX*1e3:.0f} mW, $Z_c$ = {ZC_M*1e3:.1f} mm, "
             f"$S_0$ = {s0_here:.2f} MHz at the measured waist. Sign flip at "
             "$Z_c/z_R \\approx 1.12$.",
             fontsize=7.8, color="0.3", va="top")
    _footer(fig, "figure 24 | scripts/run_geometry_design.ramp_moments "
                 "(weak-field branch checked against "
                 "rb5s6s.lineshape.stark_ramp_axial_moments) | "
                 "docs/THEORY_NOTE.md sec 2.0a, "
                 "docs/notes/running_wave_and_waist_design.md | "
                 "python scripts/make_figures.py")
    _save(fig, "fig24_weak_field_limit.png", rect=(0, 0.185, 1, 1))


def fig_retro_combination():
    """Why the shift and the rate take DIFFERENT combinations of the two arms.

    WHY THIS FIGURE EXISTS. The beam is retroreflected, so the atom sits in a
    standing wave of contrast set by the return fraction rho. Two observables
    are read off that same field and they do not take the same combination of
    the two arms, which is easy to state and easy to get wrong.

    The AC-Stark shift is linear in the intensity, so an atom crossing many
    fringes feels the FRINGE MEAN, and that is the arithmetic combination
    (1 + rho). A Doppler-free two-photon amplitude is linear in E squared and
    only the term whose two wavevectors cancel is Doppler-free, so it takes the
    cross term alone, the GEOMETRIC combination 2 sqrt(rho). Their ratio is
    exactly the fringe contrast.

    Two consequences the panels carry. The correction is invisible at the
    dataset's own rho and is not at a poorer one, which is why the formula
    carries it rather than assuming it away. And the Doppler-free RATE is
    fringe-immune, having no z dependence at all, while the SHIFT is not, which
    is the asymmetry the running-wave design note exploits.
    """
    import math
    RHO = C.RHO_RETRO
    RHO_POOR = 0.75

    fig = plt.figure(figsize=(12.2, 4.5))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 1.0], wspace=0.24,
                          left=0.065, right=0.985, top=0.88, bottom=0.28)
    ax, bx = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])

    # ---- (a) the standing wave and its two readings ---------------------
    z = np.linspace(0.0, 2.0, 1200)          # in units of the wavelength
    for rho, col, lab in ((RHO, "#0072B2", f"$\\rho$ = {RHO:.2f}, this dataset"),
                          (RHO_POOR, "#D55E00", f"$\\rho$ = {RHO_POOR:.2f}")):
        # |E|^2 for two counter-propagating arms of amplitude 1 and sqrt(rho)
        inten = 1.0 + rho + 2.0 * math.sqrt(rho) * np.cos(4.0 * np.pi * z)
        ax.plot(z, inten, color=col, lw=2.0, label=lab)
        ax.axhline(1.0 + rho, color=col, lw=1.2, ls=(0, (5, 3)))
    ax.set_xlabel("position along the beam ($z$, in wavelengths)")
    ax.set_ylabel("intensity (one arm = 1)")
    ax.set_title("(a)  one field, two readings", fontsize=10.5, loc="left")
    ax.legend(fontsize=8.2, loc="lower right")
    ax.set_ylim(-0.25, 4.4)
    ax.annotate("the fringe MEAN, $1+\\rho$:\nwhat the light shift feels,\n"
                "because the shift is linear in intensity",
                xy=(1.87, 1.0 + RHO), xytext=(0.985, 0.985),
                textcoords="axes fraction", fontsize=8.0, color="0.2",
                ha="right", va="top",
                arrowprops=dict(arrowstyle="-|>", color="0.4", lw=1.0))
    ax.annotate("the fringe AMPLITUDE, $2\\sqrt{\\rho}$:\nwhat the Doppler-free "
                "coupling takes, because\nonly the cross term cancels the two "
                "wavevectors",
                xy=(0.50, 1.0 + RHO + 2.0 * math.sqrt(RHO)),
                xytext=(0.02, 0.30), textcoords="axes fraction", fontsize=8.0,
                color="0.2", ha="left", va="top",
                bbox=dict(boxstyle="square,pad=0.25", fc="white", ec="none",
                          alpha=0.88),
                arrowprops=dict(arrowstyle="-|>", color="0.4", lw=1.0))

    # ---- (b) the two combinations, and where they part -------------------
    rr = np.linspace(0.30, 1.0, 400)
    bx.plot(rr, 100.0 * ((1.0 + rr) / (2.0 * np.sqrt(rr)) - 1.0),
            color="#0072B2", lw=2.4)
    bx.set_xlabel("retro return fraction $\\rho$")
    bx.set_ylabel("arithmetic over geometric (%)")
    bx.set_title("(b)  the shift and the coupling against retro ratio",
                 fontsize=10.5, loc="left")
    for rho, col, lab in ((RHO, "#009E73", "this dataset"),
                          (RHO_POOR, "#D55E00", "a poorer retro")):
        gap = 100.0 * ((1.0 + rho) / (2.0 * math.sqrt(rho)) - 1.0)
        bx.plot([rho], [gap], "o", color=col, ms=8, zorder=5)
        bx.annotate(f"{lab}\n$\\rho$ = {rho:.2f}: {gap:.2f}%",
                    xy=(rho, gap), xytext=(-14, 46 if rho == RHO else 74),
                    textcoords="offset points", fontsize=8.2, color=col,
                    ha="right",
                    arrowprops=dict(arrowstyle="-", color=col, lw=0.9))
    bx.text(0.97, 0.94,
            "No published digit moves at this dataset's own $\\rho$.\n"
            "The correction grows fast as the retro degrades.",
            transform=bx.transAxes, fontsize=7.8, color="0.25",
            ha="right", va="top")

    fig.text(0.065, 0.175,
             "Rate: no $z$ dependence. Shift: follows the local intensity.",
             fontsize=7.8, color="0.3", va="top")
    _footer(fig, "figure 25 | rb5s6s.config.RHO_RETRO, "
                 "rb5s6s.hyperpolarizability.two_photon_rabi_hz and the "
                 "DELTA_ALPHA_AU note in rb5s6s/constants.py | "
                 "docs/THEORY_NOTE.md | python scripts/make_figures.py")
    _save(fig, "fig25_retro_combination.png", rect=(0, 0.10, 1, 1))


def fig_lineshape_kernels():
    """What the observed line is made of, kernel by kernel.

    WHY THIS FIGURE EXISTS. `model_profile()` is the most-used object in the
    repository and the lineshape chapter describes it in prose alone. Four
    kernels convolve into one line, they have different SHAPES rather than
    merely different widths, and the shapes are the reason the fit can tell
    some of them apart and not others: two Lorentzians of any widths add to a
    Lorentzian, which is why the natural and collisional parts are combined
    analytically and why the collisional width is degenerate with anything else
    homogeneous. The Gaussian and the two-sided exponential are not
    interchangeable either, and the exponential's central cusp is the transit
    signature the chapter names.

    Panel (a) is the four kernels at the campaign's own representative widths.
    Panel (b) builds the line up one convolution at a time, so the reader can
    see where the width comes from: the natural width is about two thirds of
    the observed line and everything above it is apparatus.

    Drawn from rb5s6s.lineshape directly, at the same representative widths the
    saturation companion note uses, so the total reproduces the observed 5.37
    MHz rather than being tuned to it.
    """
    from rb5s6s import lineshape as L                      # noqa: E402
    from rb5s6s.stark import _fwhm_of                      # noqa: E402

    GC, SL, TR = 0.60, 1.50, 0.96          # collisional, laser, transit (MHz)
    nu = np.linspace(-14.0, 14.0, 40001)
    dnu = float(nu[1] - nu[0])

    def fwhm_of_curve(y):
        pk = y.max()
        above = np.where(y >= 0.5 * pk)[0]
        return float(nu[above[-1]] - nu[above[0]])

    fig = plt.figure(figsize=(12.6, 4.7))
    gs = fig.add_gridspec(1, 2, wspace=0.22, left=0.06, right=0.985,
                          top=0.88, bottom=0.27)
    ax, bx = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])

    # ---- (a) the four kernels, each normalised to unit peak --------------
    kernels = (("natural (Lorentzian)", L.lorentzian(nu, GNAT), GNAT, "#a63430"),
               ("collisional (Lorentzian)", L.lorentzian(nu, GC), GC, "#D55E00"),
               ("laser (Gaussian)", L.gaussian(nu, SL), SL, "#0072B2"),
               ("transit (2-sided exp.)",
                L.two_sided_exponential(nu, TR), TR, "#009E73"))
    for lab, y, w, col in kernels:
        ax.plot(nu, y / y.max(), color=col, lw=2.1,
                label=f"{lab}, {w:.2f} MHz")
    ax.set_xlim(-7.0, 7.0)
    ax.set_xlabel("detuning from line centre (MHz, transition axis)")
    ax.set_ylabel("kernel, peak normalised")
    ax.set_title("(a)  four kernels, four shapes", fontsize=10.5, loc="left")
    ax.legend(fontsize=8.0, loc="upper right")
    ax.annotate("the transit kernel's central cusp,\nwhich is what lets the fit "
                "tell it\nfrom a Gaussian of the same width",
                xy=(0.30, 0.62), xytext=(-6.6, 0.72), fontsize=7.8, color="0.25",
                arrowprops=dict(arrowstyle="-|>", color="0.4", lw=1.0))

    # ---- (b) the line, built one convolution at a time -------------------
    steps = [("natural alone", L.lorentzian(nu, GNAT), "#a63430"),
             ("+ collisional", L.lorentzian(nu, GNAT + GC), "#D55E00")]
    y = L._conv(L.lorentzian(nu, GNAT + GC), L.gaussian(nu, SL), dnu)
    steps.append(("+ the laser", y, "#0072B2"))
    y2 = L._conv(y, L.two_sided_exponential(nu, TR), dnu)
    steps.append(("+ transit: the observed line", y2, "#009E73"))
    for lab, yy, col in steps:
        bx.plot(nu, yy / yy.max(), color=col, lw=2.1,
                label=f"{lab}, {fwhm_of_curve(yy):.2f} MHz")
    bx.set_xlim(-7.0, 7.0)
    bx.set_xlabel("detuning from line centre (MHz, transition axis)")
    bx.set_ylabel("profile, peak normalised")
    bx.set_title("(b)  the line, one convolution at a time", fontsize=10.5,
                 loc="left")
    bx.legend(fontsize=8.0, loc="upper right")
    total = _fwhm_of(GC, SL, TR, 0.0, np.linspace(-40.0, 40.0, 200001))
    natural_pct = 100.0 * GNAT / total

    fig.text(0.06, 0.165,
             f"Natural width {natural_pct:.0f} per cent of the "
             f"{total:.2f} MHz total. The rest is apparatus.",
             fontsize=7.8, color="0.3", va="top")
    _footer(fig, "figure 26 | rb5s6s.lineshape.lorentzian, .gaussian, "
                 ".two_sided_exponential and .model_profile, at the campaign's "
                 "representative widths | docs/methods/02_the_lineshape.md | "
                 "python scripts/make_figures.py")
    _save(fig, "fig26_lineshape_kernels.png", rect=(0, 0.09, 1, 1))


def fig_wavemeter_reconstruction():
    """The wavemeter record, its model, and the same quantity from our traces (M22).

    The result is the settled floor on unmodelled laser motion. The model is
    the sawtooth adopted 2026-08-03 (preregistration addendum 25): a free level
    and a free ramp rate for each inter-lock interval, with a shared finite
    rise at each re-lock and no relaxation term. The event census and the floor
    are read from results/wavemeter_reconstruction.csv so the panels cannot
    drift from the fit that wrote it.
    """
    import collections
    import csv

    import matplotlib.image as mpimg
    sys.path.insert(0, str(C.REPO_ROOT / "scripts"))
    from run_wavemeter_reconstruction import reconstruct, PHOTO
    r = reconstruct()
    t, f, band = r["t"], r["f"], r["band"]
    tf, mu, sg = r["t_fit"], r["mu"], r["sigma"]
    mfit = tf >= r["edge_cut_min"]     # the opening is a digitisation edge
                                       # effect and is not in the likelihood
    wm = {x["quantity"]: x["value"] for x in csv.DictReader(
        open(C.RESULTS_DIR / "wavemeter_reconstruction.csv"))}
    # The re-lock census (how many events step the laser up, down or not at
    # all) and the shared rise time used to be argued in panel (b)'s title.
    # Both are results and both are in results/wavemeter_reconstruction.csv,
    # so they belong to the caption.
    floor = float(wm["settled_noise_floor"])

    fig = plt.figure(figsize=(7.6, 8.4))
    # hspace carries panel (b)'s axis title AND panel (c)'s titles: at 0.34 the
    # two printed through each other.
    gs = fig.add_gridspec(3, 1, height_ratios=[1.35, 2.0, 1.5], hspace=0.46)

    ax0 = fig.add_subplot(gs[0])
    ax0.imshow(mpimg.imread(str(PHOTO)))
    ax0.set_axis_off()
    ax0.set_title("(a) as photographed: 2025-06-11, a preliminary session five "
                  "weeks before the campaign", fontsize=8.5)

    ax1 = fig.add_subplot(gs[1])
    ax1.fill_between(t, f - band/2, f + band/2, color="#0072B2", alpha=0.15, lw=0,
                     label="scan band, the laser sweep,\n"
                           f"{r['band_mhz']:.0f} MHz peak to peak")
    ax1.plot(t, f, color="#0072B2", lw=0.7, label="digitised band centre")
    ax1.plot(tf[mfit], mu[mfit], color="#D55E00", lw=1.8,
             label="fitted model: a step at each re-lock, a ramp in between")
    for k, tk in enumerate(r["kick_times"]):
        ax1.axvline(tk, color="#D55E00", lw=0.8, ls=":", alpha=0.55,
                    label="the times at which the lock was re-acquired" if k == 0 else None)
    ax1.set_xlabel("time (min)")
    ax1.set_ylabel("laser detuning (MHz)")
    ax1.legend(loc="lower right", fontsize=7.5, frameon=True, framealpha=0.9)
    # THE EVENT COUNT, computed at draw time from the drawn events. A frozen
    # preregistration records that this panel prints it; it did not, and the
    # frozen text is never edited, so the figure is what changes.
    ax1.text(0.015, 0.03, f"{len(r['kick_times'])} confirmed re-locks",
             transform=ax1.transAxes, fontsize=7.4, color="0.30",
             ha="left", va="bottom")
    ax1.set_title("(b) the digitised record and the fitted sawtooth", fontsize=8.5)

    # Two records, two time origins, so two panels. They used to share one
    # x axis, each counted from its own start, with the legend left to carry
    # the fact: the campaign markers then landed near 74 min of an axis whose
    # first 54 min belong to the 2025-06-11 record, and read as its
    # continuation. The axis is split instead, each half labelled with the
    # origin it counts from, the two sharing a y scale so the comparison the
    # panel exists for still works by eye. Widths follow the two spans, so a
    # minute is the same length in both halves.
    rows = [x for x in csv.DictReader(open(C.REPO_ROOT / "results" / "laser_history.csv"))
            if x["flag"] == "canonical" and x["offset_mhz"] not in ("", "nan")]
    ep = collections.defaultdict(list)
    for x in rows:
        ep[x["display_epoch"]].append((int(x["t_epoch"]), float(x["offset_mhz"])))
    best = sorted(max(ep.values(), key=lambda v: max(a for a, _ in v) - min(a for a, _ in v)))
    tt = np.array([(a - best[0][0]) / 60 for a, _ in best])
    oo = np.array([b for _, b in best]); oo -= oo.mean()

    span_a = float(tf[mfit].max() - tf[mfit].min())
    span_b = float(max(tt.max(), 1.0))
    sub = gs[2].subgridspec(1, 2, width_ratios=[span_a, span_b], wspace=0.05)
    ax2 = fig.add_subplot(sub[0])
    ax2b = fig.add_subplot(sub[1], sharey=ax2)

    ax2.fill_between(tf[mfit], -sg[mfit], sg[mfit], color="#D55E00", alpha=0.18,
                     lw=0, label="fitted noise model, plus and minus one standard\n"
                                 f"deviation, settling to {floor:.2f} MHz")
    ax2.plot(tf[mfit], (f[::3] - mu)[mfit], color="#666666", lw=0.6,
             label="residual of the record above")
    # markers only: the dataset samples in bursts, not continuously
    ax2b.plot(tt, oo, "o", color="#009E73", ms=5,
              label=f"campaign traces, standard deviation {oo.std():.1f} MHz")
    # The left half is the narrower of the two and its legend the wider, and at
    # a common size that legend was wider than its own axes: it printed out
    # through the left spine, over the tick labels and over the axis title. The
    # size is set per half so each legend fits the frame it belongs to.
    for a, fs in ((ax2, 6.1), (ax2b, 7.0)):
        a.axhline(0, color="k", lw=0.5)
        a.set_ylim(-9, 12)        # held fixed so the two records share a
                                  # scale, and the dataset markers set the range
        a.legend(loc="upper right", fontsize=fs, frameon=True, framealpha=1.0)
    ax2b.tick_params(labelleft=False)
    ax2.set_xlabel("time from the start of the 2025-06-11 record (min)", fontsize=8.5)
    ax2b.set_xlabel("time from the start of the campaign segment (min)", fontsize=8.5)
    ax2.set_ylabel("residual frequency (MHz)")
    ax2.set_title("(c) the record above, model removed", fontsize=8.2)
    ax2b.set_title("the same quantity on a campaign segment five weeks later",
                   fontsize=8.2)
    _footer(fig, "Source: scripts/run_wavemeter_reconstruction.py (reconstruct(), the "
                 "photographed record) + results/laser_history.csv\n"
                 "(panel c overlay). Regenerate: python scripts/make_figures.py.",
            fontsize=5.9)
    _save(fig, "fig14_wavemeter_reconstruction.png")




def fig_drift_story():
    """The drift problem, what the analysis extracted despite it, and what a
    fixed lock buys (fig15). Three panels, rebuilt 2026-08-12 on the experimenter's
    reading of the previous version.

    (a) The problem, photographed: the 2025-06-11 wavemeter record, digitised
        by M22. Re-lock markers are drawn ONLY where the sawtooth fit returns
        a real upward step. The kick finder proposed three more candidates
        (near 16, 28 and 31 min); their fitted steps are -1.1, -0.05 and
        -0.15 MHz, the end of a steep ramp rather than a re-lock, and the
        experimenter's own recollection of the session agrees, so they are
        named on the panel and not drawn as re-locks. An earlier version drew
        a grey line at every candidate, which invented kicks the record does
        not contain.
    (b) The campaign's central bookkeeping fact, shown as one comparison:
        between consecutive oscilloscope window settings, the move of the
        fitted peak position against the move of the window itself. The
        points lie on the identity line, so the centre record follows the
        instrument's own display frame, not the atom. This replaces a
        per-epoch offset plot with a drift-wedge inset that read as a
        measured trend; the held-lock drift SIGN is deliberately not drawn
        anywhere (experimenter call, 2026-08-12: the record does not establish it
        and the figure should not appear to).
    Panels (a) and (b) were reworked 2026-08-20 on the experimenter's reading.
    (a) named the model instead of describing its behaviour, and its
    rejected-candidate note went from three lines to one. (b) now states its
    proposition on the panel, because points lying on an identity line read
    as either trivial or broken until the panel says which, and its printed
    fraction is called a fraction of the position SIGNAL rather than of its
    variance, the quantity being a fraction of mean square about zero.

    (c) The consequence ladder, decluttered: three lock regimes on a log
        axis, two short annotations each. The prose that used to live on the
        canvas belongs to the documents that cite the figure. The held-lock
        entry is drawn as an UPPER LIMIT at 0.02 MHz/min rather than as a
        point at 0.016. Correction of record, 2026-08-20: the earlier point
        carried the state-space constant under the label "the measured
        bound", which the window-reference audit had already retracted (see
        the comment at the regime list and DATA.md's provenance note). The
        sign policy stated for panel (b) applies here too, and the earlier
        panel broke it.
    """
    import csv as _csv

    sys.path.insert(0, str(C.REPO_ROOT / "scripts"))
    from run_wavemeter_reconstruction import reconstruct
    r = reconstruct()
    t, f, band = r["t"], r["f"], r["band"]
    tf, mu = r["t_fit"], r["mu"]

    rows = [x for x in _csv.DictReader(open(C.RESULTS_DIR / "laser_history.csv"))
            if x["flag"] == "canonical" and x["offset_mhz"]]

    # S0, sigma_laser and the beta range were read here to be printed inside
    # panel (c)'s legend. That legend is gone (it covered the very marker it
    # described) and the three numbers now live in the caption, which quotes
    # the same committed CSVs, so reading them here would be a computation
    # with no consumer.

    fig = plt.figure(figsize=(8.6, 10.6))
    gs = fig.add_gridspec(3, 1, height_ratios=[1.4, 1.4, 1.2], hspace=0.52)

    # ---- (a) the photographed record, digitised -------------------------
    ax = fig.add_subplot(gs[0])
    ax.fill_between(t, f - band / 2, f + band / 2, color="#0072B2", alpha=0.25,
                    lw=0, label="scan band, the laser sweep")
    ax.plot(t, f, color="#0072B2", lw=0.9, label="band centre = laser frequency")
    mclip = tf > 0.4     # the pre-first-kick baseline is a fit artifact
    ax.plot(tf[mclip], mu[mclip], color="#D55E00", lw=1.6, ls="--",
            label="sawtooth fit: free level and drift rate\nper interval, one shared re-lock rise time")
    confirmed = [s_ for s_ in r["steps"] if s_["step_mhz"] > 1.0]
    rejected = [s_ for s_ in r["steps"] if s_["step_mhz"] <= 1.0]
    for s_ in confirmed:
        ax.axvline(s_["t_kick"], color="0.55", lw=0.7, alpha=0.6)
    # The three named rather than drawn, with their fitted steps, computed at
    # draw time so the panel cannot disagree with the fit it shows.
    _times = ", ".join(f"{s_['t_kick']:.0f}" for s_ in rejected)
    _amps = ", ".join(f"{s_['step_mhz']:+.2f}" for s_ in rejected)
    ax.text(0.985, 0.03,
            f"{len(rejected)} further candidates near {_times} min are ramp "
            f"ends, not re-locks:\ntheir fitted steps are {_amps} MHz.",
            transform=ax.transAxes, fontsize=6.8, color="0.35",
            ha="right", va="bottom")
    ax.set_xlabel("time (min)")
    ax.set_ylabel("laser detuning (MHz)")
    ax.set_title("(a) laser frequency, 2025-06-11 preliminary session,\n"
                 "digitised from the wavemeter display",
                 fontsize=9)
    # Blank strip above the data for the legend, rather than the legend over
    # the scan band it is describing. Same treatment the other panels of this
    # file use where an opaque legend would sit on data.
    _lo, _hi = ax.get_ylim()
    ax.set_ylim(_lo, _lo + (_hi - _lo) * 1.34)
    ax.legend(fontsize=7, loc="upper left", framealpha=1.0, frameon=True)

    # ---- (b) the centre record follows the window -----------------------
    ax = fig.add_subplot(gs[1])
    # THE POWER SESSION'S OWN BLOCKS, which is the construction the record
    # uses (PREREGISTRATION_RESULTS addendum on the window frame, DATA.md):
    # contiguous runs of one (peak, power) condition, then the step between
    # consecutive blocks. Grouping matters and is stated rather than assumed:
    # this panel's absolute RMS values differ from the addendum's 145.2 and
    # 6.3 ms because that addendum groups its 99 traces into 17 blocks and
    # this groups them into 20, but the VARIANCE FRACTION both give is the
    # same 99.8 per cent, and the fraction is the claim. A first version of
    # this panel differenced display-epoch means across the whole campaign,
    # which mixed two sessions and is a different quantity again.
    import itertools as _it
    P = sorted((x for x in rows if x["role"] == "p_sweep"
                and x["peak_pos_ms"] and x["window_start_ms"]),
               key=lambda x: float(x["t_epoch"]))
    blocks = []
    for _k, _g in _it.groupby(P, key=lambda x: (x["peak"], x["power_mW"])):
        _g = list(_g)
        blocks.append((np.mean([float(x["peak_pos_ms"]) for x in _g]),
                       np.mean([float(x["window_start_ms"]) for x in _g])))
    dpos = np.diff([b[0] for b in blocks])
    dwin = np.diff([b[1] for b in blocks])
    lim = 1.10 * max(np.abs(dwin).max(), np.abs(dpos).max())
    ax.plot([-lim, lim], [-lim, lim], "-", color="0.6", lw=1.0,
            label="identity: the position moved exactly\nas the window moved")
    ax.plot(dwin, dpos, "o", ms=5.0, color="#009E73", mec="0.2", mew=0.5,
            label=f"steps between the power sweep's\n{len(dpos)} condition blocks")
    _resid = float(np.sqrt(np.mean((dpos - dwin) ** 2)))
    # A fraction of MEAN SQUARE about zero, not of variance about the mean.
    # On data of this shape the two agree to the fifth decimal, so the printed
    # 99.8 is right either way, but the panel no longer calls it variance.
    _frac = 1.0 - _resid ** 2 / float(np.mean(dpos ** 2))
    _knob = int(np.sum(np.abs(dwin) > 1e-9))
    # THE PROPOSITION, INSIDE THE CANVAS WORD LIMIT. The first attempt at
    # this said the same thing in fifty words and tripped the guard that
    # forbids a canvas from arguing: the fix for "unclear" is a sharper
    # sentence, not a longer one. The reasoning lives in the caption.
    ax.text(0.035, 0.965,
            "On the identity line the peak did not move, the window setting "
            f"did.\n{100 * _frac:.1f}% of the between-block signal is that "
            f"setting, scatter {_resid:.0f} ms over {len(dpos)} steps.",
            transform=ax.transAxes, fontsize=7.4, color="0.30", va="top")
    ax.set_xlabel("window-setting move between blocks (ms, scope axis)")
    ax.set_ylabel("peak-position move (ms)")
    ax.set_title("(b) peak-position move against window-setting move,\n"
                 "between consecutive power-sweep blocks",
                 fontsize=9)
    ax.legend(fontsize=7, loc="lower right", framealpha=1.0, frameon=True)
    ax.grid(alpha=0.25, lw=0.5)

    # ---- (c) the consequence ladder, decluttered -------------------------
    ax = fig.add_subplot(gs[2])
    envelope_mhz_per_min = DRIFT_RATE_LASER_HZ_PER_MIN / 1e6  # rb5s6s.constants ENVELOPE
    ayachitula_mhz_per_min = 0.5e-3 / 50.0  # <0.5 kHz / 50 min (Ayachitula et al. 2024)
    # THE HELD LOCK IS A BOUND, NOT A RATE. Earlier versions of this panel
    # drew the state-space constant 0.016 MHz/min as a point labelled "the
    # measured bound". That reading was retracted by the window-reference
    # audit: DATA.md's provenance note (2026-07-30) states that 0.016 "is not
    # a measured rate in either direction" because the fit compares block
    # medians ACROSS blocks, the comparison the horizontal-setting correction
    # contaminates, and PREREGISTRATION_RESULTS addendum 4 records the same
    # withdrawal. What the record defends is a two-sided bound of order
    # 0.02 MHz/min with the SIGN UNDETERMINED, which is also the only thing
    # the drift-immune argument ever used. Drawn as a bound.
    drift_bound = 0.020   # MHz/min laser, two-sided, sign undetermined
    # MARKERS CARRY THE SPACING, A LEGEND CARRIES THE TEXT. Two earlier
    # layouts put multi-line prose beside each marker on the axis: centred, it
    # left the axes at both ends; anchored inward, the left block grew into the
    # middle one. Both were caught by looking. A legend cannot collide with
    # anything, and what this panel has to show is that the three regimes sit
    # five decades apart, which the markers do on their own.
    # SHORT labels only. Every number these used to carry ($S_0$, sigma_laser,
    # beta) is committed in results/ and quoted by the caption, so nothing is
    # lost by taking it off the canvas.
    regimes = [
        (envelope_mhz_per_min, "#B0B0B0", "planning envelope,\n2025"),
        (drift_bound, "#0072B2", "2025 held lock,\nbounded below this"),
        (ayachitula_mhz_per_min, "#009E73", "cavity-lock class,\nin the literature"),
    ]
    # THE LEGEND WAS THE COLLISION. The comment above said a legend cannot
    # collide with anything; the shipped PNG showed otherwise, because three
    # multi-line prose entries at upper-center grew into a box that covered
    # the middle marker, which is the held-lock bound and the whole point of
    # the panel. Prose in a legend is prose on the canvas. Replaced by three
    # SHORT direct labels at ONE height, each over its own marker, with the
    # full statement moved to the caption where a qualifier belongs. The
    # markers are three decades apart on a log axis, so short labels centred
    # on them cannot reach each other.
    for rate, col, short in regimes:
        ax.plot([rate], [0.0], "o", ms=11, color=col, mec="0.25", mew=0.8,
                zorder=3)
        if rate == drift_bound:
            # An upper limit wears a limit marker. The bar sits at the bound
            # and the arrow points into the allowed region, so the panel
            # cannot be read as placing the held lock AT this rate.
            ax.annotate("", xy=(rate / 6.0, 0.0), xytext=(rate, 0.0),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=1.6,
                                        shrinkA=6.0, shrinkB=0.0), zorder=2)
        ax.annotate(short, xy=(rate, 0.0), xytext=(rate, 1.15),
                    textcoords="data", ha="center", va="bottom",
                    fontsize=7.6, color=col,
                    arrowprops=dict(arrowstyle="-", color=col, lw=0.8,
                                    alpha=0.55, shrinkA=1.0, shrinkB=5.0))
    ax.set_xscale("log")
    ax.set_xlim(2e-6, 300.0)
    # room above the markers for the legend, which sits over empty axis
    ax.set_ylim(-0.35, 2.6)
    ax.set_yticks([])
    ax.set_xlabel("laser drift rate (MHz/min)")
    ax.set_title("(c) claimable precision against laser drift rate",
                 fontsize=9)
    ax.grid(axis="y", visible=False)
    # Wrapped. As one line this ran 193 px past the right edge of the canvas
    # and the guard reported it; the provenance is the same, the line breaks
    # are the fix.
    _footer(fig, "Source: scripts/run_wavemeter_reconstruction.py (panel a).\n"
                 "results/laser_history.csv, power-sweep condition blocks "
                 "(panel b).\n"
                 "rb5s6s.constants (2025 planning envelope), DATA.md "
                 "provenance note\nand PREREGISTRATION_RESULTS addendum 4 "
                 "(held-lock bound), Ayachitula et al. 2024\n(cavity-lock "
                 "class) (panel c).\n"
                 "Regenerate: python scripts/make_figures.py.", fontsize=5.9)
    _save(fig, "fig15_drift_story.png")


def _gallery_context():
    """Shared M25 single-trace context for fig16 and fig18: the committed
    global-dataset-fit shared optimum, plus the brightest 225 mW / 130 C
    campaign repeat per peak. Returns None (after printing why) if a required
    input is missing, so callers degrade the same way fig7/10/11 do.

    Refactored out of fig_fit_gallery (2026-08) so fig18 (fig_single_peak_fits)
    computes identical numbers from one code path -- no duplicated fit logic.
    """
    fp = C.RESULTS_DIR / "global_dataset_fit.csv"
    if not fp.exists():
        print("  (global_dataset_fit.csv absent -- skipping the fit-gallery figures)")
        return None
    if not (C.DATA_RAW_DIR / "MANIFEST.csv").exists():
        print("  (data_raw/MANIFEST.csv absent -- skipping the fit-gallery figures)")
        return None

    rows = _rows("global_dataset_fit")

    def val(q, k="primary"):
        return float(next(r["value"] for r in rows if r["quantity"] == q and r["key"] == k))

    status = next(r["status"] for r in rows if r["quantity"] == "beta_self_joint")
    kappa = val("kappa_min")
    # The profile minimum is what the DRAWN MODEL uses, and it sits at the
    # boundary, zero. It is not the result: the CSV row for it says in so
    # many words that it is not a detection, so the box states this fit's
    # 95 per cent bound instead.
    #
    # WHICH BOUND, and the distinction is load-bearing. These are M25's own
    # numbers, from global_dataset_fit.csv, status PRELIM. They are NOT the
    # figures README.md and CLAIMS.md headline, which are the three-session
    # joint construction in stark_joint.csv, status BOUND, giving
    # S0(225 mW) < 0.26 MHz against this fit's 0.217. The preregistration
    # deliberately leaves open which construction is of record, so this box
    # labels its own provenance rather than implying agreement. An earlier
    # version of this comment claimed the reader-facing documents report
    # these numbers, which is false.
    kappa_ub95 = val("kappa_ub95")
    s0_ub95 = val("S0_225mW_ub95")
    # these two sit under a different key from the primary block
    beta_lo95 = val("beta_self_lo95", "joint_region")
    beta_hi95 = val("beta_self_hi95", "joint_region")
    beta = val("beta_self_joint")
    sl_blocks = {r["key"]: float(r["value"]) for r in rows if r["quantity"] == "sigma_laser"}

    sys.path.insert(0, str(C.REPO_ROOT / "scripts"))
    try:
        from run_global_dataset_fit import DNU_FLOOR, load_campaign_all
        from rb5s6s.linefit import _shared_profile_grid, transit_fwhm_at_T
        traces = load_campaign_all()
    except Exception as e:  # missing/changed raw traces: degrade like fig7/10/11
        print(f"  (could not load campaign traces for the fit gallery: {e} -- skipping)")
        return None

    # brightest campaign condition per peak: 225 mW at 130 C is both the
    # highest power AND the highest temperature the campaign ran, so it is
    # the single brightest condition available (fig2: amplitude ~ P^2).
    # Within its five repeats, take the largest peak-amplitude one.
    reps = {}
    for t in traces:
        if t["T"] == 130.0 and abs(t["P"] - 0.225) < 1e-9:
            cur = reps.get(t["peak"])
            if cur is None or t["A0"] > cur["A0"]:
                reps[t["peak"]] = t
    peaks = ("4121", "4154", "4192", "4207")
    if not all(pk in reps for pk in peaks):
        print("  (missing a 225 mW / 130 C campaign trace for some peak -- "
              "skipping the fit-gallery figures)")
        return None

    return {"status": status, "kappa": kappa, "beta": beta,
           "kappa_ub95": kappa_ub95, "s0_ub95": s0_ub95,
           "beta_lo95": beta_lo95, "beta_hi95": beta_hi95,
           "sl_blocks": sl_blocks,
           "reps": reps, "peaks": peaks, "traces": traces, "DNU_FLOOR": DNU_FLOOR,
           "_shared_profile_grid": _shared_profile_grid,
           "transit_fwhm_at_T": transit_fwhm_at_T}


def _fit_trace_nuisances(ctx, peak):
    """Refit one trace's M25 per-trace nuisances (amplitude, centre,
    background level+slope, saturation scale) by local least-squares, with
    the shared parameters (kappa, beta_self_joint, sigma_laser, transit)
    frozen at the M25 committed optimum carried in `ctx`. No shared parameter
    is touched here -- this does not re-run the global fit.

    Returns the trace record, the physical widths used to build its profile,
    the model callable, the local solution, its 1-sigma errors (from the
    fit's own Jacobian, chi2-inflated the same way stark.py inflates the
    kappa bound), chi2_red, and the FWHM measured off the drawn model curve.
    """
    return _fit_rec_nuisances(ctx, ctx["reps"][peak])


def _fit_rec_nuisances(ctx, rec):
    """The same local nuisance refit for an arbitrary campaign trace record.
    fig21's per-repeat and per-condition panels reuse fig16/18's exact code
    path through this function, so every drawn curve is the committed shared
    optimum with only per-trace nuisances refit locally."""
    t = rec
    T, P = t["T"], t["P"]
    gc = ctx["beta"] * float(density_units(T))
    sl = ctx["sl_blocks"][t["sl"]]
    transit = ctx["transit_fwhm_at_T"](T, C.TRANSIT_FWHM_PLACEHOLDER_MHZ)
    s0 = ctx["kappa"] * P
    g, prof = ctx["_shared_profile_grid"](gc, sl, transit, s0, "gaussian",
                                          dnu_floor=ctx["DNU_FLOOR"])
    x, v, sg = t["x"], t["v"], t["sg"]

    def model_at(p, xx, g=g, prof=prof):
        A, cc, b0, b1, logVs = p
        lin = A * np.interp(xx - cc, g, prof, left=0.0, right=0.0)
        Vs = np.exp(logVs)
        return Vs * (1.0 - np.exp(-lin / Vs)) + b0 + b1 * xx

    def resid(p, x=x, v=v, sg=sg):
        return (v - model_at(p, x)) / sg

    p0 = [t["A0"], t["c0"], t["b0"], 0.0, 5.0]
    lo = [0.0, t["c0"] - 8.0, -np.inf, -np.inf, -1.0]
    hi = [np.inf, t["c0"] + 8.0, np.inf, np.inf, 6.0]
    sol = least_squares(resid, p0, bounds=(lo, hi), x_scale="jac", ftol=1e-13, xtol=1e-13)
    A, cc, b0, b1, logVs = sol.x
    Vs = np.exp(logVs)
    n_local = 5
    chi2 = float(np.sum(resid(sol.x) ** 2))
    dof = max(len(x) - n_local, 1)
    # UNDO THE CORRELATION INFLATION, the way linefit.py:321-323 does. The
    # per-sample sigma carries a factor sqrt(tau_int) so the optimizer sees
    # each trace's true information content, but the GOODNESS-OF-FIT
    # diagnostic must be read on the unscaled sigma, for which E[chi2_red] = 1
    # whatever the correlation (linefit.py:236-243 states that contract).
    # Without this the panels printed 0.34 to 0.37 where the record's own
    # per-condition fit reports 0.903 to 1.092 for the very same conditions:
    # one name, two normalizations, and the figure's read as a badly
    # over-weighted fit that is in fact almost exactly right. Found when the
    # experimenter asked about the residual structure, 2026-08-15.
    # The covariance rescale below is unaffected in practice, since it is
    # one-sided and both normalizations sit at or below 1.
    chi2_red = chi2 / dof * float(t.get("tau", 1.0))

    from rb5s6s.fitutil import cov_from_jac
    cov = cov_from_jac(sol.jac) * max(chi2_red, 1.0)
    perr = np.sqrt(np.clip(np.diag(cov), 0.0, None))
    Vs_err = Vs * perr[4]  # d(exp(logVs))/d(logVs) = Vs

    # FWHM measured off the drawn model curve (background subtracted),
    # by linear interpolation across the half-maximum crossings.
    xf = np.linspace(x.min(), x.max(), 4000)
    lin_f = A * np.interp(xf - cc, g, prof, left=0.0, right=0.0)
    line_f = Vs * (1.0 - np.exp(-lin_f / Vs))
    half = line_f.max() / 2.0
    idx = np.where(line_f >= half)[0]
    if len(idx) >= 2:
        il, ir = int(idx[0]), int(idx[-1])

        def cross(i0, i1):
            x0, x1, y0, y1 = xf[i0], xf[i1], line_f[i0], line_f[i1]
            return x0 + (half - y0) * (x1 - x0) / (y1 - y0)
        xl = cross(il - 1, il) if il > 0 else xf[il]
        xr = cross(ir, ir + 1) if ir < len(xf) - 1 else xf[ir]
        fwhm = xr - xl
    else:
        fwhm = float("nan")

    # `sg` is the FITTING weight and carries the sqrt(tau_int) correlation
    # inflation; `sg_raw` is the trace's actual per-sample noise. Residual
    # DISPLAYS use sg_raw, so a band drawn at one point error means one point
    # error and the scatter matches the printed chi-squared. Fits use `sg`.
    return {"t": t, "T": T, "P": P, "gc": gc, "sl": sl, "transit": transit, "s0": s0,
           "g": g, "prof": prof, "x": x, "v": v, "sg": sg, "xf": xf,
           "tau": float(t.get("tau", 1.0)),
           "sg_raw": sg / np.sqrt(float(t.get("tau", 1.0))),
           "model_at": model_at, "sol": sol,
           "A": A, "A_err": float(perr[0]), "cc": cc, "cc_err": float(perr[1]),
           "b0": b0, "b0_err": float(perr[2]), "b1": b1, "b1_err": float(perr[3]),
           "logVs": logVs, "logVs_err": float(perr[4]), "Vs": Vs, "Vs_err": Vs_err,
           "lin_peak": float(np.max(lin_f)),
           "chi2_red": chi2_red, "dof": dof, "fwhm": fwhm}


def _saturation_display(fr, z95=1.645):
    """The parameter-box line for the fitted saturation scale, re-expressed
    to stay physical.

    Vsat is fit here as exp(logVs), so the fit itself never goes negative --
    but converting logVs's Gaussian (Wald) uncertainty into a SYMMETRIC
    +/- on Vsat directly is the wrong display whenever that uncertainty is
    not small (it is not, here: the three brightest traces' local refit
    cannot resolve any saturation at all), because it then implies negative
    saturation voltages within one sigma -- the same pathology the kappa
    treatment avoids with a zero-gradient/boundary argument (rb5s6s/stark.py).

    Fix: reparameterize as the compression coefficient c = 1/Vsat (bounded
    at zero, well-behaved as the "no saturation" limit) and report its
    one-sided 95% upper limit. If c is not significantly above zero, state
    the resulting LOWER BOUND on Vsat -- the same "detector response is
    linear" receipt the global fit checks numerically (Vsat > 10 V,
    tests/test_stark_joint.py). If a trace DOES detect compression, report
    it as the percent effect at that trace's own peak signal, the
    physically readable quantity, instead of a scale-parameter error bar.
    """
    c_hat = float(np.exp(-fr["logVs"]))       # = 1 / Vsat, exact, always >= 0
    sigma_c = c_hat * fr["logVs_err"]         # delta method on c, so >= 0 by construction
    if c_hat > z95 * sigma_c:                 # compression detected above the 95% floor
        pct = 100.0 * c_hat * fr["lin_peak"]
        pct_err = 100.0 * sigma_c * fr["lin_peak"]
        return f"  saturation compression at peak signal = {pm(pct, pct_err, '%')}"
    vsat_lb95 = 1.0 / (c_hat + z95 * sigma_c)  # one-sided 95% lower bound on Vsat
    return f"  saturation voltage > {vsat_lb95:.0f} V (95 percent confidence)"


def fig_fit_gallery():
    """M25 fit-quality gallery: data, model overlay and residuals, per peak.

    Picks the single highest-SNR campaign trace per peak (the 225 mW, 130 C
    p_sweep condition, the brightest combination of power and temperature the
    campaign ran, per fig2's P^2 amplitude law, taking the largest-amplitude
    repeat of the five) and overlays the M25 global dataset model at the
    COMMITTED shared optimum read from results/global_dataset_fit.csv:
    kappa_min, beta_self_joint, sigma_laser (per session/T block) and the
    transit reference. This does not re-run the global fit.

    Per-trace nuisances the global fit solves separately for every trace
    (amplitude, centre, background level and slope) are recomputed here by a
    local least-squares fit with the shared parameters held fixed. The
    saturation scale Vsat is also a per-session shared M25 parameter, but its
    fitted value is not written to the committed CSV, so it is refit as a
    local nuisance here too, which is noted on the figure.

    At the committed profile minimum kappa_min = 0.0 MHz/W, so the AC-Stark
    ramp width is exactly zero in the drawn model for every trace here. That
    is a property of the committed optimum, not a choice made for this
    figure.

    See fig18 (fig_single_peak_fits) for the one-panel-per-peak version with
    a parameter box; both share _gallery_context/_fit_trace_nuisances.
    """
    ctx = _gallery_context()
    if ctx is None:
        return
    status, peaks = ctx["status"], ctx["peaks"]

    fig = plt.figure(figsize=(13.5, 9.8))
    # bottom=0.10 reserves the strip the footer is drawn in: at 0.06 the
    # provenance line and the lower-left panel's axis title printed through
    # each other.
    outer = fig.add_gridspec(2, 2, hspace=0.34, wspace=0.24, top=0.83, bottom=0.10,
                             left=0.06, right=0.98)
    slot = {"4121": (0, 0), "4154": (0, 1), "4192": (1, 0), "4207": (1, 1)}
    letter = {"4121": "a", "4154": "b", "4192": "c", "4207": "d"}

    for peak in peaks:
        fr = _fit_trace_nuisances(ctx, peak)
        r0, c0 = slot[peak]
        inner = outer[r0, c0].subgridspec(2, 1, height_ratios=[3.0, 1.1], hspace=0.08)
        ax_main = fig.add_subplot(inner[0])
        ax_res = fig.add_subplot(inner[1], sharex=ax_main)

        x, v, cc = fr["x"], fr["v"], fr["cc"]
        xf, sol, model_at = fr["xf"], fr["sol"], fr["model_at"]

        # ---- main panel: data + model, centred on the fitted line centre ----
        xd = x - cc
        ax_main.plot(xd, v, ".", ms=2.2, color="0.4", alpha=0.5, label="data")
        ax_main.plot(xf - cc, model_at(sol.x, xf), "-", color=PEAK_COLOR[peak], lw=1.7,
                     label="joint fit of all campaign traces\n(amplitude, centre "
                           "and background refit here)")
        ax_main.set_ylabel("signal (V)")
        ax_main.set_title(f"({letter[peak]})  {PEAK_LABEL[peak]}, 225 mW at 130 °C",
                          fontsize=8.5)
        # Upper LEFT: the line sits at the centre of every window and the right
        # shoulder carries data all the way to the frame, so an upper-right
        # legend covered the apex and the points beside it in all four panels.
        # The left shoulder is flat background at this window in all four.
        ax_main.legend(fontsize=7, loc="upper left", frameon=True, framealpha=0.9)
        # and headroom above the line, so the legend's lower corner clears the
        # rising flank as well as the apex. Quarter-page panels are too narrow
        # for a two-line entry to fit beside the line without it.
        y0, y1 = ax_main.get_ylim()
        ax_main.set_ylim(y0, y0 + (y1 - y0) * 1.32)
        ax_main.tick_params(labelbottom=False)

        # ---- residual panel, in the house convention (fig0/fig21/fig22):
        # each point divided by ITS OWN MEASURED NOISE, so the shot-noise bulge
        # at line centre does not read as a model failure, and the shaded band
        # makes "inside the noise" an area. NOT the fitting weight, which
        # carries the sqrt(tau_int) correlation inflation and would shrink the
        # cloud to 0.6 of the band while the printed chi-squared said 1. ----
        pull = (v - model_at(sol.x, x)) / fr["sg_raw"]
        ax_res.axhspan(-1.0, 1.0, color="0.5", alpha=0.15, lw=0)
        ax_res.plot(xd, pull, ".", ms=2.0, color=PEAK_COLOR[peak], alpha=0.6)
        ax_res.axhline(0.0, color="k", lw=0.9)
        lim = 4.0 * float(np.std(pull)) if len(pull) else 4.0
        ax_res.set_ylim(-lim, lim)
        ax_res.set_xlabel("two-photon detuning (MHz)")
        ax_res.set_ylabel(r"residual / $\sigma$", fontsize=8)

    fig.suptitle(
        "The joint fit of all campaign traces, against the highest-signal trace "
        "at each of the four peaks",
        fontsize=8.6, y=0.995)
    _footer(fig, "Source: results/global_dataset_fit.csv (shared parameters, "
                 f"{STATUS_WORD.get(status, status.lower())}) + the "
                 "data_raw traces (per-trace data, local refit only). "
                 "Regenerate: python scripts/run_global_dataset_fit.py && "
                 "python scripts/make_figures.py.")
    _save(fig, "fig16_fit_gallery.png")


def fig_single_peak_fits():
    """M25 single-peak teaching figures (fig18): one large panel per peak,
    each its own PNG (fig18_single_<peak>.png) -- the "classic single-peak
    presentation" alongside fig16's four-up gallery.

    DESIGN CHOICE: four separate PNGs, not one paged figure. A parameter box
    this detailed (11 labelled numbers) does not fit legibly at quarter-page
    size, and a reader studying one peak's fit does not want the other three
    sharing the frame.

    Same M25 committed optimum and brightest-trace selection as fig16, via
    the shared _gallery_context/_fit_trace_nuisances helpers -- both figures
    compute identical numbers from one code path; this does not re-run the
    global fit and does no fitting beyond the same local per-trace nuisance
    refit fig16 already does.

    Adds, beyond fig16: a parameter box naming every number's ROLE -- SHARED
    (frozen at the M25 committed optimum) vs PER-TRACE (refit locally here,
    not persisted to any committed CSV) -- with its status tag, so the figure
    teaches the model's structure while showing the fit, not just the
    residuals. Uncertainties are shown where the source carries one: the
    committed CSV gives no error on the shared quantities (sigma_laser,
    beta_self_joint, kappa), so those are reported as point values with that
    fact stated; the per-trace nuisances get their 1-sigma error from this
    figure's own local-fit Jacobian.
    """
    ctx = _gallery_context()
    if ctx is None:
        return
    status, peaks = ctx["status"], ctx["peaks"]

    for peak in peaks:
        fr = _fit_trace_nuisances(ctx, peak)
        x, v, cc = fr["x"], fr["v"], fr["cc"]
        xf, sol, model_at = fr["xf"], fr["sol"], fr["model_at"]

        fig = plt.figure(figsize=(10.8, 6.4))
        gs = fig.add_gridspec(2, 2, height_ratios=[3.0, 1.15], width_ratios=[2.15, 1.55],
                              hspace=0.08, wspace=0.06, top=0.84, bottom=0.13,
                              left=0.085, right=0.99)
        ax_main = fig.add_subplot(gs[0, 0])
        ax_res = fig.add_subplot(gs[1, 0], sharex=ax_main)
        ax_box = fig.add_subplot(gs[:, 1])
        ax_box.axis("off")

        # ---- main panel: data + model, centred on the fitted line centre ----
        xd = x - cc
        # Trace standard (2026-08-09): data wear the peak's own colour so the
        # entity keeps one colour across every figure, and the fit is black.
        ax_main.plot(xd, v, ".", ms=3.0, color=PEAK_COLOR[peak], alpha=0.5,
                     label="data")
        ax_main.plot(xf - cc, model_at(sol.x, xf), "-", color="k", lw=1.8,
                     label="joint fit of all campaign traces\n(amplitude, centre "
                           "and background\nrefit here)")
        ax_main.set_ylabel("signal (V)")
        ax_main.set_title(peak_title(peak) + " (130 °C, 225 mW)", fontsize=10)
        ax_main.legend(fontsize=8, loc="upper left", frameon=True, framealpha=0.9)
        ax_main.tick_params(labelbottom=False)

        # ---- residual panel, in the house convention (fig0/fig21/fig22):
        # pulls against each point's own MEASURED noise, with the one-error
        # band; not the fitting weight, which carries the correlation
        # inflation (see the sibling panel above). ----
        pull = (v - model_at(sol.x, x)) / fr["sg_raw"]
        ax_res.axhspan(-1.0, 1.0, color="0.5", alpha=0.15, lw=0)
        ax_res.plot(xd, pull, ".", ms=2.6, color=PEAK_COLOR[peak], alpha=0.6)
        ax_res.axhline(0.0, color="k", lw=0.9)
        lim = 4.0 * float(np.std(pull)) if len(pull) else 4.0
        ax_res.set_ylim(-lim, lim)
        ax_res.set_xlabel("two-photon detuning (MHz)")
        ax_res.set_ylabel(r"residual / $\sigma$", fontsize=8.5)

        # ---- the parameter box: every number labelled by what it comes from ----
        N_here = float(density_units(fr["T"]))
        # the height of the drawn line above its background, after saturation
        # (the same construction fig21's per-repeat box uses)
        peak_height = float(fr["Vs"] * (1.0 - np.exp(-fr["lin_peak"] / fr["Vs"])))
        # One row per number, "name = value ± error (unit)". Every
        # parenthetical this box used to carry (which traces a shared value is
        # shared over, why the shared fit publishes no uncertainty, why the
        # transit width is held fixed, that the scan axis origin is arbitrary,
        # and what a reduced chi-squared below one implies) is caption material.
        lines = [
            f"993.{peak} nm: 225 mW, 130 °C",
            "",
            "Shared across every campaign trace:",
            f"  laser width = {fr['sl']:.3f} MHz (FWHM)",
            f"  collisional width = {fr['gc']:.3f} MHz (FWHM)",
            f"  self-broadening rate = {ctx['beta']:.4f} MHz per",
            r"      $10^{12}\,\mathrm{cm^{-3}}$"
            f", 95 per cent {ctx['beta_lo95']:.4f} to {ctx['beta_hi95']:.4f}",
            f"  number density = {N_here:.2f} " r"$\times\,10^{12}\,\mathrm{cm^{-3}}$",
            f"  Stark coefficient {bound(ctx['kappa_ub95'], 2, 'upper', 'MHz per W')}"
            " (95 per cent, this fit)",
            f"  light shift at this power "
            f"{bound(ctx['s0_ub95'], 2, 'upper', 'MHz')} (95 per cent, this fit)",
            f"  transit width = {fr['transit']:.3f} MHz (FWHM, from $w_0$)",
            "",
            "From the fit shown at left:",
            f"  total width = {fr['fwhm']:.3f} MHz (FWHM)",
            f"  reduced chi-squared = {fr['chi2_red']:.2f} over {len(x)} points",
            "",
            "This trace only:",
            # The fitted coefficient multiplies a chain of area-normalized
            # kernels (rb5s6s/lineshape.py), so it is the line's area and
            # carries V MHz. Printed as "amplitude ... V" it read as a peak
            # height, on a panel whose data peak near 1 V while the number
            # printed 7.7. The drawn peak height is given beneath it, the
            # same quantity fig21 prints.
            pm_row("line area", fr["A"], fr["A_err"], "V × MHz"),
            f"  peak height = {peak_height:.3f} V",
            pm_row("centre", fr["cc"], fr["cc_err"], "MHz"),
            pm_row("background level", fr["b0"], fr["b0_err"], "V"),
            pm_row("background slope", fr["b1"], fr["b1_err"], "V/MHz"),
            _saturation_display(fr),
        ]
        # 6.6 pt, not 7.0: the longest row reached the frame at 7.0 and the
        # box's padding was consumed on the right.
        ax_box.text(0.02, 0.98, "\n".join(lines), transform=ax_box.transAxes,
                    fontsize=6.6, va="top", ha="left", family="monospace", linespacing=1.35,
                    bbox=dict(boxstyle="round,pad=0.5", facecolor="0.97",
                             edgecolor="0.6", lw=0.8))

        fig.suptitle(
            "The fitted model, its residual and its parameters",
            fontsize=9.2, y=0.995)
        _footer(fig, "Source: results/global_dataset_fit.csv (shared parameters, "
                     f"{STATUS_WORD.get(status, status.lower())}) + the data_raw traces "
                     "(this trace, refit individually). Regenerate: "
                     "python scripts/run_global_dataset_fit.py && "
                     "python scripts/make_figures.py.", y=0.015)
        _save(fig, f"fig18_single_{peak}.png")


def _pilot_width_point(prates):
    """The morning pilot's raw width and the rate it is licensed under.

    Built exactly like every other point on fig19's first panel: the
    retrace-safe contiguous half-maximum span of each trace, times the scan
    rate, averaged over the traces, with the repeat scatter and the rate error
    combined the way scripts/run_beta_self.py's raw_fwhm_mhz combines them.
    The four power blocks are pooled because width is power-independent here
    (the light-shift null), which is the same pooling addendum 17 used.

    The rate is the pilot day's OWN, not a borrowed one: the campaign bracket
    rate for the pilot's peak times the measured scale in
    results/morning_ruler.csv, which the pilot day's 27 rulers fix at 1.0022(12).
    That measurement is why this point can be drawn at all, and it is what
    replaced a scale fitted inside the joint fits.

    The traces live in the pilot excluded tree and are read in place, never
    copied, so a checkout without that tree gets no pilot point and the rest of
    the panel is unchanged. Returns (width_MHz, err_MHz, n_traces, peak) or
    None.
    """
    from rb5s6s.qc import contiguous_fwhm_ms
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import run_stark_joint as _rsj

    peak, scale = "4192", _rsj.measured_pilot_scale()
    if scale is None or peak not in prates or not _rsj.SESSION_20250717.is_dir():
        return None
    files = sorted(_rsj.SESSION_20250717.glob("*mw*.csv"))
    if len(files) < 3:
        return None
    rate, relerr = prates[peak]
    rate = rate * scale[0]
    relerr = float(np.hypot(relerr, scale[1] / scale[0]))
    ws = []
    for f in files:
        d = np.genfromtxt(f, delimiter=",", skip_header=2)
        m = np.isfinite(d[:, 0]) & np.isfinite(d[:, 1])
        ws.append(contiguous_fwhm_ms(d[m, 0] * 1e3, d[m, 1]))
    W = float(np.mean(ws)) * rate
    sem = float(np.std(ws, ddof=1) / np.sqrt(len(ws))) * rate
    return W, float(np.hypot(sem, W * relerr)), len(ws), peak


def fig_width_trends():
    """M4 / M4e physics-trend panels (fig19): the two width-broadening laws
    the dataset tests, side by side.

    GENERIC LAW, panel 1: pressure (collisional) broadening adds width
    linearly in the perturber density, W = floor + beta*N -- measured here
    as a SLOPE, because per-condition widths carry a common floor (fig6:
    fig_gamma_floor shows the free per-condition gamma_coll is a near-flat
    FLOOR, degenerate with sigma_laser at corr ~ -0.85 to -0.9, that does
    not resolve collisions point-by-point). RB INSTANCE: this panel does
    NOT plot that free-fit gamma_coll against an unrelated line -- the two
    constructions are not comparable (RESULTS_C-chain, docs/RESULTS.md
    C1). It instead reproduces the dataset's own HEADLINE beta_self
    estimator verbatim: the model-independent P0 confound probe in
    scripts/run_beta_self.py (collisional_slope, results/beta_self_probe.csv),
    which fits RAW contiguous FWHM (no lineshape split) vs N as
    W(N) = floor + beta_eff*N, then inflates the slope error by the
    between-block scatter (the same floor fig6 shows) via a Student-t 95%
    bound -- why beta_self is reported as a BOUND, not a measurement (SNR<3,
    all four peaks). The fitted line and its systematic-error band therefore
    pass through the data BY CONSTRUCTION: this is the actual fit the bound
    comes from, drawn only over its own fit domain (no out-of-domain
    extrapolation).

    PER-SOURCE LICENSING (docs/notes/ruler_validity_and_trim_prereg.md
    section 8, fixed before this rebuild). Every point needs BOTH a licensed
    rate and a licensed width, and the four candidate sources land as follows.
      * Campaign 130 C, 20 traces: rate from its own session's before/after
        bracket rulers, width from the same retrace-safe contiguous span as
        every other point. ENTERS, and enters the fit. Until 2026-08-04 this
        panel drew three points per peak under a title quoting a four-point
        bound (2026-08-02, run_beta_self.py's headline decision), so the
        drawn construction and the reported one disagreed. They now match.
      * Morning pilot, 26 traces on one peak: rate from the pilot day's own
        27 rulers as the measured scale in results/morning_ruler.csv, width
        contiguous like the rest. ENTERS as a separately marked point OUTSIDE
        the fitted slope, with a horizontal error bar over the density its
        oven label leaves open (addendum 17: its 91 C is a variac set point,
        the internal temperature is ~110-130 C).
      * Rehearsal, 46 traces: no rulers of its own, its scan rate is a fitted
        box inside the joint fits. A width built on a rate fitted inside the
        same model is not model-independent, which is the one thing this
        panel's construction is for. STAYS OUT, with the reason on the panel.
        It is not excluded from the dataset: it carries the light-shift
        bounds, where its rate is properly marginalized.
      * EOM ruler traces as lineshape data: STAY OUT for this release. The
        tooth-amplitude law does not close on the power-session ruler
        population (addendum 22), and licensing calibration traces as
        lineshape data inside the release that found their indexing broken
        would invert the burden of proof. The 7 fitted heights per trace now
        recorded in results/ruler_traces.csv are the dataset an amplitude
        model would be tested against, and the panel says so.
    Both refusals are the experimenter's to overrule.

    Retroactive honesty pass, private/reviews/digest/fig19_trend_audit.md
    (2026-08-02): the construction was independently reproduced to float
    precision and confirmed correct -- what was missing was the panel saying,
    out loud, how thin it is (n=3 per peak, dof=1) and that the drawn line
    and band ARE the fit the bound comes from, not a denser trend it happens
    to pass through. Also flagged: a documented, quantified low-SNR
    narrowing bias at the 70 C anchor (~6%, right sign for 3 of 4 peaks,
    scripts/run_beta_self.py's raw_fwhm_mhz) steepens the fitted slope,
    which can only make the reported bound MORE conservative, never less.
    Both are now stated compactly on the panel itself (title + one
    annotation), not just here.

    GENERIC LAW, panel 2: a light-shift GRADIENT across the beam broadens the
    line as the shift squared (the AC-Stark ramp, fig12), so a bound on the
    Stark coefficient kappa implies an upper bound on this width growth, not
    a value -- drawn as the SHADED WEDGE OF PERMITTED GROWTH, between the
    lowest-power width (kappa = 0) and that width plus the growth kappa_ub95
    allows, never as an error bar. Until 2026-08-05 the shading ran from the
    upper edge of that wedge to +100 MHz, so the panel drew every measured
    point above its own lowest-power one inside the region it called excluded.
    RB INSTANCE: FWHM vs power at 130 C (results/power_sweep.csv, the same
    source fig2 uses) against the kappa_ub95_profile bound
    (results/stark_sweep.csv, M4e / run_stark_sweep.py). sigma_laser vs power
    is NOT shown: at fixed condition it is degenerate with gamma_coll
    (corr ~ -0.90; fig10 is the dedicated figure for that degeneracy) and does
    not read as a clean per-point trend (checked: non-monotonic, largest
    error exceeds the whole span).
    """
    manifest_fp = C.MANIFEST_CSV
    ruler_fp = C.RESULTS_DIR / "ruler_blocks.csv"
    probe_fp = C.RESULTS_DIR / "beta_self_probe.csv"
    pw_fp = C.RESULTS_DIR / "power_sweep.csv"
    stark_fp = C.RESULTS_DIR / "stark_sweep.csv"
    if not (manifest_fp.exists() and ruler_fp.exists() and probe_fp.exists()
            and pw_fp.exists() and stark_fp.exists()):
        print("  (a source file for fig19 is absent -- skipping)")
        return
    # The left panel reproduces the headline estimator from the raw contiguous
    # widths, so it needs the traces themselves and not only the CSVs above.
    # Checking the CSVs alone let this raise FileNotFoundError out of the probe
    # in a checkout without them, which ended the run.
    if not (C.DATA_RAW_DIR / "t_sweep").is_dir():
        print("  (raw traces not in this checkout, keeping the existing "
              "fig19 PNG)")
        return

    from rb5s6s.stark import _fwhm_of
    from rb5s6s.linefit import transit_fwhm_at_T
    from rb5s6s.beta import collisional_slope
    from rb5s6s.ingest import load_manifest
    from rb5s6s.qc import outlier_files

    # scripts/ is not a package (see tests/test_figures_fresh.py's own
    # importlib-by-path workaround) -- add it to sys.path so we can reuse the
    # P0 confound probe's own functions (raw_fwhm_mhz, load_t_rates, TSWEEP)
    # verbatim rather than re-deriving them, so this panel is guaranteed to
    # match results/beta_self_probe.csv, not merely resemble it.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import run_beta_self as _rbp

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.6, 5.3))
    fig.subplots_adjust(top=0.76, bottom=0.15, left=0.075, right=0.98, wspace=0.26)

    # ======== panel 1: the licensed channel -- raw width vs N(T), =========
    # ======== floor + slope, the fit results/beta_self_probe.csv comes from
    manifest_rows = load_manifest()
    # The producer drops sibling outliers from every fit it runs, so the panel
    # drops them too: a point the bound does not contain must not be drawn as
    # one of its points. The set is empty today and this keeps it that way by
    # construction rather than by luck.
    dropped = outlier_files()
    if dropped:
        manifest_rows = [r for r in manifest_rows if r["file"] not in dropped]
    trates, prates = _rbp.load_t_rates()
    P_anchor, T_anchor = BETA_ANCHOR_130
    ymin_p1, ymax_p1 = 1e9, 0.0
    # The shared slope and its error, from the pooled construction's row of
    # record (results/beta_self_probe.csv, adopted per its preregistration).
    import csv as _csv
    _pooled = next(r for r in _csv.DictReader(open(C.RESULTS_DIR / "beta_self_probe.csv"))
                   if r["peak"] == "pooled_slope")
    pooled_slope = float(_pooled["beta_eff"])
    pooled_slope_err = float(_pooled["syst_err"])
    for peak in ("4121", "4154", "4192", "4207"):
        byT = defaultdict(list)
        for r in manifest_rows:
            if (r["flag"] == "canonical" and r["role"] == "t_sweep"
                    and r["peak"] == peak and r["temperature_C"] in _rbp.TSWEEP):
                byT[r["temperature_C"]].append(r)
        N, W, E = [], [], []
        for T in _rbp.TSWEEP:
            if T in byT and (peak, T) in trates:
                rate, relerr = trates[(peak, T)]
                m, e = _rbp.raw_fwhm_mhz(byT[T], rate, relerr)
                N.append(float(density_units(float(T)))); W.append(m); E.append(e)
        # The 130 C anchor, calibrated on its own session's before/after
        # bracket rulers. It is a point OF the reported bound, so it is drawn
        # as one: until 2026-08-04 the panel drew three points under a title
        # quoting the four-point construction.
        recs130 = [r for r in manifest_rows
                   if r["flag"] == "canonical" and r["role"] == "p_sweep"
                   and r["peak"] == peak and r["power_mW"] == P_anchor]
        if peak in prates and len(recs130) >= 3:
            rate, relerr = prates[peak]
            m, e = _rbp.raw_fwhm_mhz(recs130, rate, relerr)
            N.append(float(density_units(T_anchor))); W.append(m); E.append(e)
        if len(N) < 3:
            continue
        N = np.array(N); W = np.array(W); E = np.array(E)

        # identical weighted fit to collisional_slope()'s internals (floor is
        # not in its return dict, so recovered here from the same A/Winv/W);
        # cs supplies the vetted error terms (syst_err folds in the
        # between-block scatter fig6 calls the floor -- the fit weight, not
        # a subtraction, since gamma_coll is never split out of this raw
        # width at all).
        cs = collisional_slope(N, W, E)
        Esys = np.sqrt(E ** 2 + cs["resid_rms"] ** 2)

        # One SHARED slope across the four lines (the pooled construction of
        # the pooling preregistration, adopted 2026-08-06), with this line's
        # own floor refit at that fixed slope. The physics licence is in the
        # prereg: no resonant exchange by parity, the R^-6 exchange is
        # isotope-blind, so the model ladder gives one slope and four floors.
        Winv_d = 1.0 / Esys ** 2
        floor = float(np.sum(Winv_d * (W - pooled_slope * N)) / np.sum(Winv_d))

        ax1.errorbar(N, W, yerr=Esys, fmt="o", color=PEAK_COLOR[peak], ms=5.5, lw=1.4,
                     capsize=2, label=PEAK_LABEL[peak], zorder=4)
        Nfit = np.linspace(N.min(), N.max(), 60)
        line = floor + pooled_slope * Nfit
        band = pooled_slope_err * (Nfit - N[0])  # zero at the anchor point, by construction
        ax1.plot(Nfit, line, "-", color=PEAK_COLOR[peak], lw=1.1, alpha=0.85, zorder=2)
        ax1.fill_between(Nfit, line - band, line + band, color=PEAK_COLOR[peak],
                         alpha=0.14, lw=0, zorder=1)
        ymin_p1 = min(ymin_p1, float(np.min(W - Esys)), float(np.min(line - band)))
        ymax_p1 = max(ymax_p1, float(np.max(W + Esys)), float(np.max(line + band)))

    # ---- the morning pilot, marked and outside every fitted slope ----------
    pilot = _pilot_width_point(prates)
    if pilot is not None:
        Wp, Ep, npil, pilot_peak = pilot
        N_lo, N_hi = (float(density_units(T)) for T in PILOT_T_RANGE_C)
        ax1.errorbar([N_hi], [Wp], yerr=[Ep], xerr=[[N_hi - N_lo], [0.0]],
                     fmt="D", ms=6.5, mfc="white", mec=PEAK_COLOR[pilot_peak],
                     ecolor=PEAK_COLOR[pilot_peak], mew=1.5, elinewidth=1.5,
                     capsize=3.5, capthick=1.5, zorder=5,
                     # The horizontal bar is not a measurement error, it is the
                     # range the pilot's own oven label leaves open, so it is
                     # named where the marker is named. A free-floating note
                     # next to the bar landed under the legend below it.
                     label=f"exploratory morning session, "
                           f"{PEAK_LABEL[pilot_peak].split(' (')[0]}, {npil} traces,\n"
                           "not in any fit. Horizontal bar: oven label %g to %g °C"
                           % PILOT_T_RANGE_C)
        ymin_p1 = min(ymin_p1, Wp - Ep)
        ymax_p1 = max(ymax_p1, Wp + Ep)

    pad1 = 0.08 * (ymax_p1 - ymin_p1)
    ax1.set_ylim(ymin_p1 - pad1, ymax_p1 + pad1 + 0.62 * (ymax_p1 - ymin_p1))
    ax1.set_xscale("log")
    ax1.set_xlabel(r"Rb density $N$  ($10^{12}\,\mathrm{cm^{-3}}$)")
    ax1.set_ylabel("measured FWHM (MHz)")
    ax1.set_title("The measured FWHM against Rb density, at four cell temperatures,\n"
                  "with one shared slope and a floor per line", fontsize=8.2)
    # A twelve-line box used to sit top-left: what the error bars are and are
    # not, the quantified low-signal narrowing at the 70 °C anchor and which way
    # it pushes the bound, which two sources were weighed and refused (the
    # rehearsal session's fitted scan rate, and the calibration combs, whose
    # recorded heights are the data an amplitude model would be tested
    # against), and what the shaded band on each line is pivoted on. All of it
    # is caption material and all of it is section 8 of
    # docs/notes/ruler_validity_and_trim_prereg.md.
    # lower right, with reserved headroom above keeping the top-left text box
    # clear of the whiskers
    ax1.legend(fontsize=6.6, loc="lower right", ncol=1, framealpha=0.95, frameon=True, bbox_to_anchor=(1.0, -0.01))
    # Through the shared helper, which pins the ticks to the dataset's own
    # oven settings and writes them as plain degrees. Left to itself the
    # secondary axis inherited the log formatter below it and printed the
    # temperatures as 7x10^1, 8x10^1, 9x10^1, 10^2.
    sec = _temperature_top_axis(ax1, (70.0, 90.0, 110.0, 130.0))
    sec.set_xlabel("cell temperature (°C)", fontsize=8.5)
    sec.tick_params(labelsize=7.5)

    # ================= panel 2: FWHM vs power, Stark exclusion wedge =======
    pw_rows = _rows("power_sweep")
    stark_rows = _rows("stark_sweep")
    kappa_ub = float(next(r["value"] for r in stark_rows
                          if r["quantity"] == "kappa_ub95_profile"))
    core = {r["key"]: float(r["value"]) for r in stark_rows if r["quantity"] == "core_sigma_laser"}
    transit130 = transit_fwhm_at_T(130.0, C.TRANSIT_FWHM_PLACEHOLDER_MHZ)
    nu = np.arange(-45.0, 45.0, 0.02)
    Pgrid_W = np.linspace(0.0, 0.26, 60)
    core_mean = float(np.mean(list(core.values()))) if core else 1.6

    ymax_panel, ymin_panel = 0.0, 1e9
    for peak in ("4121", "4154", "4192", "4207"):
        d = sorted((int(r["power_mW"]), float(r["fwhm"]), float(r["fwhm_err"]))
                  for r in pw_rows if r["peak"] == peak)
        P_mw, F, Fe = zip(*d)
        # Markers only: five powers, and the joining segments drew a
        # rise-and-fall through them that this panel exists to deny.
        ax2.errorbar(P_mw, F, yerr=Fe, fmt="o", color=PEAK_COLOR[peak], ms=5.5, lw=1.4,
                    capsize=2, label=PEAK_LABEL[peak], zorder=4)
        ymax_panel = max(ymax_panel, max(f + fe for f, fe in zip(F, Fe)))
        ymin_panel = min(ymin_panel, min(f - fe for f, fe in zip(F, Fe)))

        core_pk = core.get(f"993.{peak}nm", core_mean)
        base0 = _fwhm_of(0.6, core_pk, transit130, 0.0, nu)
        excess = np.array([_fwhm_of(0.6, core_pk, transit130, kappa_ub * P, nu)
                           for P in Pgrid_W]) - base0
        anchor = F[0]  # this peak's own lowest-power data point
        curve = anchor + (excess - excess[0])
        ax2.plot(Pgrid_W * 1000.0, curve, "--", color=PEAK_COLOR[peak], lw=1.0, alpha=0.75,
                zorder=3)
        # THE WEDGE IS THE ALLOWED GROWTH, so it is bounded by the two curves
        # that bound it: flat at the lowest-power width if the coefficient is
        # zero, and the dashed curve if it sits at its 95% upper bound. It
        # used to be filled from the dashed curve up to 100 MHz, which put
        # every measured point above the lowest-power one INSIDE the shading
        # -- the panel drew its own data as excluded. Filling between the
        # anchor and the curve makes the wedge what the annotation says it is,
        # and it is thin, which is the panel's point: the growth the bound
        # still permits is far smaller than the block-to-block scatter the
        # markers show.
        ax2.fill_between(Pgrid_W * 1000.0, anchor, curve, color=PEAK_COLOR[peak],
                         alpha=0.22, lw=0, zorder=1)

    pad = 0.08 * (ymax_panel - ymin_panel)
    ax2.set_xlim(0.0, 260.0)
    # A clear strip above the data for the annotation below, the same device
    # fig1 and fig5 use. Anchored at the top right with the axis ending at the
    # highest bar, its opaque box covered the 125 and 175 mW markers of two
    # components and a stretch of two of the dashed curves.
    ax2.set_ylim(ymin_panel - pad, ymax_panel + pad + 0.42 * (ymax_panel - ymin_panel))
    ax2.set_xlabel("power (mW)")
    ax2.set_ylabel("measured FWHM (MHz)")
    ax2.set_title("The measured FWHM against power, with the light-shift growth\n"
                  "the bound still allows", fontsize=8.2)
    # lower right: at P>150 mW the four traces converge to a tight 5.28-5.45
    # MHz band, well clear of the axis floor -- the only corner free of both
    # data and the top-left annotation below.
    ax2.legend(fontsize=6.6, loc="lower right", ncol=1, framealpha=0.95, frameon=True, bbox_to_anchor=(1.0, -0.01))
    # The wedge's reading (the 95 percent bound on the light-shift broadening
    # coefficient, what the dashed curve and the shading are, and the size of
    # the block-to-block scatter beside them) was a six-line paragraph here. It
    # is caption material. The bound itself is
    # results/stark_sweep.csv's kappa_ub95_profile, which the wedge is drawn
    # from, and the ratio of the scatter to the permitted growth used to be
    # computed in the panel title.

    fig.suptitle(
        "Two broadening mechanisms on the four 993 nm 5S-6S hyperfine lines: "
        "collisional and light-shift broadening",
        fontsize=9.2, y=0.995)
    _footer(fig, "Source: data_raw/MANIFEST.csv + results/ruler_blocks.csv (left panel "
                 "widths, reproducing the results/beta_self_probe.csv construction), "
                 "results/ruler_traces.csv (the recorded comb heights),\n"
                 "results/morning_ruler.csv + the held-aside session tree (its point, read "
                 "in place), results/power_sweep.csv, results/stark_sweep.csv (right panel). "
                 "Regenerate: python scripts/run_beta_self.py && python "
                 "scripts/run_stark_sweep.py && python scripts/make_figures.py.",
            fontsize=5.9)
    _save(fig, "fig19_width_trends.png", rect=(0, 0.05, 1, 1))


def fig_magic_wavelengths():
    """The 5S-6S magic wavelengths (M16): where the light shift lands the
    same on both clock states.

    GENERIC LAW FIRST: a magic wavelength is a wavelength where the
    differential AC-Stark shift between two states vanishes. A trap held
    there shifts both states equally, so it does not move the transition
    between them -- the trick behind every optical-lattice clock (e.g. Sr
    at 813 nm). THE INSTANCE here: for Rb 5S1/2 and 6S1/2 (the 993 nm line)
    that happens near 1204, 1288 and 1340 nm, from an independent
    sum-over-states recompute (rb5s6s.polarizability, M16) on published
    matrix elements -- Volz & Schmoranzer 1996, Herold et al. 2012, the
    Safronova-group portal, Leonard et al. 2015; full sourcing is in that
    module's docstring. Both states are J=1/2, so under linear polarization
    the scalar term is EXACT (the tensor polarizability vanishes
    identically by the triangle rule), not an approximation resting on the
    vector/tensor terms being small.

    TOP panel: Delta_alpha = alpha_6S - alpha_5S and its three zero
    crossings, each marked with its committed 16-84% Monte Carlo band
    (results/polarizability.csv). BOTTOM panel: alpha_5S and alpha_6S
    separately, on the same axis, so the crossings are visibly just where
    a nearly-flat curve (alpha_5S, far from its own D-line poles here)
    meets a curve threaded between nearby 6S->nP resonances (alpha_6S).
    Points within a mask of a 6S->nP pole are dropped (NaN) so the
    crossings stay readable; the poles are the physics, not a plotting
    artifact.

    THE PANEL DRAWS MORE CROSSINGS THAN THE PRODUCER REPORTS, and now says
    so. magic_wavelengths() searches between the poles with a 1.5 nm guard
    on each side (_crossings' `guard`), so a root closer to a resonance than
    the guard is invisible to the search while remaining visible on the
    curve. In this window that is the root at 1297.533 nm, 0.745 nm from the
    6S->7P resonance at 1298.278 nm. It is real (brentq confirms it to 1e-9)
    and it was being drawn, unlabelled, beside three labelled ones. Whether
    the guard is right is a question for the experimenter: a crossing that close to
    a resonance is useless for a trap, which is an argument for reporting it
    with that caveat rather than for dropping it silently.

    NOTHING PUTS A ROOT IN EVERY INTER-POLE GAP, and the panel used to say
    the opposite. The 6S->5P transitions lie BELOW 6S, so they enter the
    sum-over-states with a negative energy denominator and their poles carry
    the opposite residue sign to the upward 6S->7P ones. Two of the four
    resonances in the drawn window are of each kind (7P3/2 at 1292.390 and
    7P1/2 at 1298.278 upward, 5P1/2 at 1323.879 and 5P3/2 at 1366.874
    downward). Measured on the drawn curve, 2 of the 5 gaps change sign end
    to end, and the window holds 4 roots in all: two of them share the gap
    below 1292.390 nm, which is why that gap has no net sign change. The
    counts on the panel are computed from the curve, not asserted.

    Status: ENVELOPE (unpublished to the depth searched 2026-07-17,
    scalar-only). The vector term near the 6S-5P lines needs its own
    treatment before any trap design -- see rb5s6s/polarizability.py.
    """
    from rb5s6s import polarizability as P

    rows = _rows("polarizability")
    magic_rows = sorted((r for r in rows if r["quantity"] == "magic_5s6s"),
                        key=lambda r: float(r["value"]))
    if not magic_rows:
        print("  (no magic_5s6s rows in polarizability.csv -- skipping fig17)")
        return
    crossings = []
    for r in magic_rows:
        lam = float(r["value"])
        # THE BAND COMES FROM ITS OWN COLUMNS. Until 2026-08-14 this parsed it
        # out of the free-text `unit` field with
        #     re.search(r"16-84% band ([\d.]+)\.\.([\d.]+) nm", r["unit"])
        # and fell back to (lam, lam) when that failed. The uncertainty wave had
        # already moved the band into real err_lo16/err_hi84 columns and left no
        # such text behind, so the regex matched NOTHING, the fallback fired for
        # all three crossings, and the panel printed brackets of zero width:
        # "[1203.89, 1203.89]" where the committed band is 1203.06 to 1204.73.
        # A silent fallback turned a missing parse into a confident claim of
        # perfect precision, which is the one thing this figure exists to deny.
        # There is no fallback now: a magic row without its band is an error.
        try:
            lo, hi = float(r["err_lo16"]), float(r["err_hi84"])
        except (KeyError, TypeError, ValueError) as exc:
            raise SystemExit(
                f"fig17: magic_5s6s row {r['key']!r} has no usable 16-84 band "
                f"in err_lo16/err_hi84 ({exc}). Re-run "
                f"scripts/run_polarizability.py rather than letting the figure "
                f"draw a zero-width uncertainty.") from exc
        if not (lo <= lam <= hi):
            raise SystemExit(
                f"fig17: magic_5s6s row {r['key']!r} has a band "
                f"[{lo}, {hi}] that does not contain its own value {lam}.")
        crossings.append((lam, lo, hi))
    # The three bands differ by more than an order of magnitude in width, so
    # one status word cannot describe all three uncertainties. What each bracket
    # is, how wide the widest and the tightest are, and the status of the
    # calculation behind them were a nine-line block on the top panel. All of it
    # is caption material, and the brackets themselves are drawn under each
    # crossing.

    lo_nm, hi_nm = 1050.0, 1420.0
    CLIP = 2500.0                                  # a.u.; masks the 6S->nP poles
    # BREAK THE CURVE AT EVERY POLE, AND SAMPLE IT PROPERLY BESIDE ONE.
    #
    # Each 6S->nP resonance is a sign change of the (dE^2 - w^2) denominator,
    # so the polarizability leaves through one infinity and returns from the
    # other. Two things follow for the drawing. A NaN goes in at each pole
    # wavelength, so no segment can ever be drawn ACROSS a pole and read as a
    # zero crossing (the clip at CLIP happens to cover every pole on today's
    # grid, but that is a property of the residues and the grid spacing, not
    # something the figure should depend on). And the even grid is refined
    # geometrically towards each pole, because the interesting structure is
    # compressed into the last nanometre: on the even grid alone the stretch
    # beside the 6S->7P resonance was carried by two samples and was drawn as
    # one near-vertical chord.
    poles = np.array(sorted(p for p in set(P._POLES_5S_NM) | set(P._POLES_6S_NM)
                            if lo_nm < p < hi_nm))
    step = np.geomspace(1e-3, 5.0, 140)
    near = np.concatenate([np.concatenate((p - step, p + step)) for p in poles]
                          ) if len(poles) else np.empty(0)
    near = near[(near > lo_nm) & (near < hi_nm)]
    g = np.unique(np.concatenate([np.linspace(lo_nm, hi_nm, 4000), near]))
    a5 = np.array([P.alpha_5s(x) for x in g])
    a6 = np.array([P.alpha_6s(x) for x in g])
    cut = np.searchsorted(g, poles)
    g = np.insert(g, cut, poles)
    a5 = np.insert(a5, cut, np.nan)
    a6 = np.insert(a6, cut, np.nan)
    da = a6 - a5
    a6_m = np.where(np.abs(a6) > CLIP, np.nan, a6)
    da_m = np.where(np.abs(da) > CLIP, np.nan, da)

    # Every zero crossing the drawn curve actually has, against the ones the
    # reported search found. They are not the same set: the search steps over
    # a guard strip on each side of every resonance, and a root inside such a
    # strip is invisible to it. A crossing the panel draws but does not name
    # is exactly what the three marked ones would be mistaken for, so it is
    # marked too, as what it is.
    listed = np.array([c[0] for c in crossings])
    ok = np.isfinite(da[:-1]) & np.isfinite(da[1:])
    flip = np.where(ok & (np.sign(da[:-1]) * np.sign(da[1:]) < 0))[0]
    unlisted = []
    for i in flip:
        w = abs(da[i]) / (abs(da[i]) + abs(da[i + 1]))
        x = float(g[i] + w * (g[i + 1] - g[i]))
        if listed.size == 0 or float(np.min(np.abs(listed - x))) > 0.05:
            unlisted.append(x)

    # HOW MANY GAPS ACTUALLY CHANGE SIGN used to be counted here, on the drawn
    # curve rather than asserted from the pole structure, for a six-line block
    # under the axes: no rule puts a root in every gap between resonances,
    # because the 6S->5P transitions run downward and their poles carry the
    # opposite residue sign, and the gap below the first resonance carries two
    # roots with no net sign change. The block is caption material, so the
    # counting moved out with it. The unlisted crossing is still drawn, as a
    # grey dotted line.

    # NO hspace IN gridspec_kw. An explicitly set hspace marks the grid as one
    # tight_layout must not touch, and matplotlib then skips the whole figure:
    # the rect was ignored, every margin stayed at its default, and that is why
    # the five-line suptitle printed across the top panel's own title. The
    # panels share an x axis, so the gap tight_layout computes for itself is
    # already small.
    fig, (ax_top, ax_bot) = plt.subplots(
        2, 1, figsize=(9.6, 7.8), sharex=True,
        gridspec_kw={"height_ratios": [1.15, 1.0]})

    # ---- top: the differential and its zero crossings ----
    ax_top.axhline(0, color="0.55", lw=0.9)
    ax_top.plot(g, da_m, color="#0072B2", lw=1.7)
    # Label placement, by crossing (they are sorted by wavelength). The two
    # right-hand labels used to sit ON the near-vertical branches, and their
    # opaque boxes erased segments of the curve at the crossings the panel
    # exists to show. Each now sits in clear space with a leader to its own
    # crossing: left of the pole for the middle one, right of the last
    # branch for the third.
    label_offsets = [(0, 40), (-108, -54), (62, 34)]
    for i, (lam, clo, chi) in enumerate(crossings):
        # The band is DRAWN, not only printed. figures/README.md and
        # FUTURE_TRANSITIONS_titsapph.md both told the reader to look for a
        # shaded 16-84 per cent band and there was none on the canvas, because
        # the only thing carrying the band was the bracket text, which was
        # itself degenerate. The widths are genuinely unequal, 1.67 nm at the
        # 1204 crossing against 0.13 nm at 1340, so the span also shows at a
        # glance which crossing is actually pinned down.
        ax_top.axvspan(clo, chi, color="#D55E00", alpha=0.16, lw=0, zorder=0)
        ax_top.axvline(lam, color="#D55E00", ls="--", lw=1.1)
        dx, dy = label_offsets[i] if i < len(label_offsets) else (0, 40)
        ax_top.annotate(
            f"{lam:.2f} nm\n[{clo:.2f}, {chi:.2f}]",
            (lam, 0.0), xytext=(dx, dy),
            textcoords="offset points", ha="center", fontsize=7.6,
            color="#D55E00",
            bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                     edgecolor="none", alpha=0.85),
            arrowprops=dict(arrowstyle="-", color="#D55E00", lw=0.7, alpha=0.6))
    for x in unlisted:
        for a in (ax_top, ax_bot):
            a.axvline(x, color="0.45", ls=(0, (1, 2)), lw=1.0)
    ax_top.set_ylabel("difference in polarizability, 6S minus 5S\n(atomic units)")
    ax_top.set_ylim(-CLIP * 1.05, CLIP * 1.05)
    ax_top.set_title(
        "The difference between the two curves of the lower panel, and its zero crossings",
        fontsize=9.5)

    # ---- bottom: the two states separately -- the resonance structure ----
    ax_bot.axhline(0, color="0.7", lw=0.7)
    ax_bot.plot(g, a5, color="#009E73", lw=1.7, label="5S polarizability")
    ax_bot.plot(g, a6_m, color="#E69F00", lw=1.5, label="6S polarizability")
    for lam, _, _ in crossings:
        ax_bot.axvline(lam, color="#D55E00", ls=":", lw=1.0)
    ax_bot.set_ylim(-CLIP * 1.05, CLIP * 1.05)
    ax_bot.set_xlabel("wavelength (nm)")
    ax_bot.set_ylabel("polarizability (atomic units)")
    ax_bot.legend(fontsize=7.5, loc="lower left", framealpha=1.0, frameon=True)
    # Why the 5S curve is flat here and the 6S curve diverges was a four-line
    # block on this panel. It is caption material.

    fig.suptitle(
        r"Polarizability of Rb 5S$_{1/2}$ and 6S$_{1/2}$, and the magic wavelengths "
        "of the 993 nm line",
        fontsize=9.0, y=0.995)

    _footer(fig, "Source: results/polarizability.csv (magic_5s6s rows) + rb5s6s/polarizability.py "
                 "(alpha_5s, alpha_6s). Regenerate: python scripts/run_polarizability.py && "
                 "python scripts/make_figures.py.", y=0.040, fontsize=6.6)
    # Wrapped by hand, and anchored va="bottom" so it grows upward: as one
    # line it was about 10 percent wider than the canvas and lost its last
    # four words off the right edge.
    fig.text(
        0.01, 0.004,
        "Matrix elements: Volz & Schmoranzer 1996, Herold et al. 2012, the Safronova-group "
        "portal, Leonard et al. 2015\n(full sourcing in rb5s6s/polarizability.py). A "
        "literature search on 17 July 2026 found no published value for these crossings.",
        fontsize=6.6, color="0.35", va="bottom")

    _save(fig, "fig17_magic_wavelengths.png", rect=(0, 0.168, 1, 0.995))


def fig_method_loop():
    """fig20: the conceptual method this whole repository runs, drawn once.

    No data, no fitted parameters -- a schematic, like fig12 (the AC-Stark
    ramp derivation). An observation admits several candidate physical
    mechanisms; an identifiability analysis (a profile-likelihood map, a
    lever test, a covariance check -- fig7, fig6 and fig10 are three
    instances already in this repository) decides which branch applies.
    IDENTIFIED closes cleanly into a claim. DEGENERATE does not stop there:
    it names the dominant limitation, which points at a targeted
    measurement, which buys a new capability -- and that capability changes
    what the NEXT observation can resolve, so the diagram closes into a
    loop rather than a dead end. Two worked examples from this dataset sit
    underneath, both instances of the degenerate branch, because that is
    the branch every headline number in this repository currently sits on.
    """
    import matplotlib.patches as mpatches
    from matplotlib.patches import FancyArrowPatch

    BLUE, ORANGE, GREEN, GREY = "#0072B2", "#D55E00", "#009E73", "#4D4D4D"

    fig = plt.figure(figsize=(13.5, 9.4))
    # Two explicitly-placed axes (not plt.subplots' default margins, which
    # left content clipped at the canvas edge here): the main loop on top,
    # the worked examples below, with dead figure-fraction space between
    # them for the section heading -- so the two coordinate systems never
    # share the same patch of canvas.
    ax = fig.add_axes([0.02, 0.335, 0.96, 0.565])
    ax.set_xlim(0, 128)
    # Re-budgeted 2026-08-05. At (36, 108) the three orange boxes of the lower
    # row overlapped each other by four units each, two of the arrows between
    # them were shorter than the overlap and pointed backwards, and the
    # "Separable" box sat on top of the diamond's upper vertex with no room
    # for the arrow that is supposed to reach it. The vertical range is opened
    # to make room for that arrow, and the boxes are laid out from an explicit
    # spacing below so a future edit cannot re-create the overlap by hand.
    ax.set_ylim(36, 112)
    ax.axis("off")

    def box(xy, w, h, text, edge=GREY, face="white", fontsize=9.5, fontweight="normal",
            lw=1.6, textcolor="0.1", ax_=ax):
        x, y = xy
        p = mpatches.FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                    boxstyle="round,pad=0.35,rounding_size=2.5",
                                    linewidth=lw, edgecolor=edge, facecolor=face, zorder=3)
        ax_.add_patch(p)
        ax_.text(x, y, text, ha="center", va="center", fontsize=fontsize,
                 fontweight=fontweight, color=textcolor, zorder=4, linespacing=1.25)
        return x, y

    def diamond(xy, w, h, text, edge=GREY, face="#F2F2F2", fontsize=9.0):
        x, y = xy
        pts = [(x, y + h / 2), (x + w / 2, y), (x, y - h / 2), (x - w / 2, y)]
        p = mpatches.Polygon(pts, closed=True, linewidth=1.8, edgecolor=edge,
                             facecolor=face, zorder=3)
        ax.add_patch(p)
        ax.text(x, y, text, ha="center", va="center", fontsize=9.0,
                fontweight="bold", color="0.1", zorder=4, linespacing=1.2)
        return x, y

    def arrow(p0, p1, color=GREY, lw=1.8, connectionstyle="arc3,rad=0.0",
              label=None, label_frac=0.5, label_dx=0.0, label_dy=3.2,
              label_ha="center", fontsize=7.6, ax_=ax):
        a = FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=14,
                            color=color, lw=lw, shrinkA=2, shrinkB=2,
                            connectionstyle=connectionstyle, zorder=2)
        ax_.add_patch(a)
        if label:
            # label_dx exists for the vertical arrows: centred on one of
            # those, the caption is drawn straight through the shaft.
            lx = p0[0] + label_frac * (p1[0] - p0[0]) + label_dx
            ly = p0[1] + label_frac * (p1[1] - p0[1]) + label_dy
            ax_.text(lx, ly, label, ha=label_ha, va="bottom", fontsize=fontsize,
                     color=color, style="italic", zorder=4)

    # ---- the main loop -----------------------------------------------
    yT, yB, ySpur = 83.0, 57.0, 104.0
    x_obs, x_mech, x_id = 16.0, 50.0, 86.0
    x_claim = 113.0
    # The lower row runs right to left from under the diamond to under the
    # observation, on an even spacing, and the box width is derived from that
    # spacing rather than chosen: BOT_GAP is the clearance between neighbours,
    # so the row cannot overlap itself and every arrow between two of these
    # boxes has the same visible length.
    BOT_PITCH = (x_id - x_obs) / 3.0
    BOT_GAP = 5.0
    BOT_W = BOT_PITCH - BOT_GAP
    x_dom, x_tgt, x_cap = x_id - BOT_PITCH, x_id - 2 * BOT_PITCH, x_obs
    DIA_H = 20.0

    box((x_obs, yT), 24, 14, "Observation", edge=GREY, fontweight="bold")
    box((x_mech, yT), 28, 14, "Candidate physical\nmechanisms", edge=GREY)
    diamond((x_id, yT), 28, DIA_H, "Can the mechanisms\nbe separated?", edge=GREY)

    arrow((x_obs + 12, yT), (x_mech - 14, yT))
    arrow((x_mech + 14, yT), (x_id - 14, yT))

    # identified branch: a short spur up and out -- a claim does not loop.
    # ySpur clears the diamond's upper vertex by more than the arrow between
    # them needs; at the old spacing the box covered that vertex.
    box((x_id, ySpur), 22, 11, "Separable", edge=BLUE, face="#EAF3FA", textcolor=BLUE,
        fontweight="bold")
    box((x_claim, ySpur), 22, 11, "Claim", edge=BLUE, face=BLUE, textcolor="white",
        fontweight="bold")
    arrow((x_id, yT + DIA_H / 2), (x_id, ySpur - 5.5), color=BLUE)
    arrow((x_id + 11, ySpur), (x_claim - 11, ySpur), color=BLUE)

    # degenerate branch: down, then back left along the bottom, forming the loop
    box((x_id, yB), BOT_W, 12, "Not separable", edge=ORANGE, face="#FBEEE6",
        textcolor=ORANGE, fontweight="bold")
    arrow((x_id, yT - DIA_H / 2), (x_id, yB + 6), color=ORANGE)

    box((x_dom, yB), BOT_W, 12, "What limits\nthe separation", edge=ORANGE, face="#FBEEE6")
    arrow((x_id - BOT_W / 2, yB), (x_dom + BOT_W / 2, yB), color=ORANGE)

    box((x_tgt, yB), BOT_W, 12, "A measurement\nthat breaks it", edge=ORANGE, face="#FBEEE6")
    arrow((x_dom - BOT_W / 2, yB), (x_tgt + BOT_W / 2, yB), color=ORANGE)

    box((x_cap, yB), BOT_W, 12, "New capability", edge=GREEN, face="#E6F4EF",
        textcolor=GREEN, fontweight="bold")
    arrow((x_tgt - BOT_W / 2, yB), (x_cap + BOT_W / 2, yB), color=ORANGE)

    # close the loop: a new capability changes what the next observation can
    # resolve. The caption sits beside the shaft, not on it.
    arrow((x_cap, yB + 6), (x_obs, yT - 7), color=GREEN, lw=2.0,
          label="changes what the next\nmeasurement can resolve", label_frac=0.5,
          label_dx=2.5, label_dy=-2.0, label_ha="left", fontsize=7.8)

    ax.text(x_mech, yT - 12.5, "for example a profile likelihood, a test of how much\n"
            "each parameter moves the model, or a check of the\n"
            "correlations between fitted parameters",
            ha="center", va="top", fontsize=7.2, color="0.4", style="italic")

    # Which branch this work's results sit on was a two-line paragraph here.
    # It is a reading of the diagram, so it is caption material.

    # ---- two worked examples, smaller type, underneath -----------------
    fig.text(0.5, 0.300, "Two degeneracies in this dataset, and the measurement each one "
             "would take to break",
             ha="center", fontsize=9.8, fontweight="bold", color="0.15")

    ax2 = fig.add_axes([0.02, 0.045, 0.96, 0.225])
    ax2.set_xlim(0, 128)
    ax2.set_ylim(0, 46)
    ax2.axis("off")

    def chain2(y, label, steps, color):
        ax2.text(1, y, label, ha="left", va="center", fontsize=8.6, fontweight="bold",
                 color="0.15")
        n = len(steps)
        x0, x1 = 21.0, 111.0
        xs = np.linspace(x0, x1, n)
        w = (xs[1] - xs[0]) * 0.76
        for i, (x, text) in enumerate(zip(xs, steps)):
            edge = GREY if i == 0 else (GREEN if i == n - 1 else color)
            face = "#F2F2F2" if i == 0 else ("#E6F4EF" if i == n - 1 else "white")
            box((x, y), w, 16, text, edge=edge, face=face, fontsize=7.4,
                textcolor=(GREEN if i == n - 1 else "0.1"),
                fontweight=("bold" if i in (0, n - 1) else "normal"), lw=1.3, ax_=ax2)
            if i > 0:
                arrow((xs[i - 1] + w / 2, y), (x - w / 2, y), color=color, lw=1.3, ax_=ax2)

    chain2(33, "(a)", ["line width", "transit and laser\nboth broaden it",
                       "the two cannot\nbe separated",
                       "measure the\nbeam waist",
                       "would give the\nabsolute split of\nthe two widths"], ORANGE)
    chain2(11, "(b)", ["AC-Stark shift", "line centres lost\nto the drift",
                       "only the width\nis left as a handle",
                       "hold a fixed\nfrequency lock",
                       "would measure the\nlight shift, not\nonly bound it"], ORANGE)

    fig.suptitle("How an observation becomes a claim, or becomes the measurement that "
                 "would make one possible",
                 fontsize=12.5, y=0.985, fontweight="bold")
    _footer(fig, "This figure carries no data. It is a schematic of the method "
                 "(rb5s6s.identifiability, fig6/fig7/fig10 are worked instances of the "
                 "identifiability step, fig3 and results/centre_stark.csv are the two "
                 "worked examples below). Regenerate: python scripts/make_figures.py.")
    _save(fig, "fig20_method_loop.png")


def fig_joint_fit_five():
    """The joint fit across five repeats, in the layout the experimenter
    specified from the IMG_3500 reference: one condition, five rows, each
    row the data with the shared-shape fit beside its residuals, the
    SHARED parameters with their errors in the header, and the FREE
    per-repeat parameters printed on each row. Every curve is the
    committed shared optimum; only per-trace nuisances are refit locally
    (_fit_rec_nuisances, the fit gallery's code path)."""
    ctx = _gallery_context()
    if ctx is None:
        return
    traces = ctx["traces"]
    cond = sorted((tr for tr in traces if tr["peak"] == "4192"
                   and tr["T"] == 130.0 and abs(tr["P"] - 0.225) < 1e-9),
                  key=lambda tr: tr["A0"], reverse=True)
    frs = [_fit_rec_nuisances(ctx, rec) for rec in cond]
    cc0 = float(np.mean([fr["cc"] for fr in frs]))

    f0 = frs[0]

    fig = plt.figure(figsize=(12.6, 13.2))
    outer = fig.add_gridspec(5, 2, width_ratios=[1.55, 1.0], hspace=0.42,
                             wspace=0.17, top=0.885, bottom=0.05,
                             left=0.065, right=0.985)
    fig.suptitle("The joint fit across five repeats: 993.4192 nm, "
                 "130 °C, 225 mW", fontsize=13.5, y=0.975)
    # The shared parameters as value rows. The paragraph that used to sit under
    # them (which four parameters are refitted per repeat and why, what the
    # points and the line are, and where the point uncertainties come from) is
    # caption material.
    fig.text(0.5, 0.957,
             f"Shared: collisional FWHM {f0['gc']:.2f} MHz, laser FWHM "
             f"{f0['sl']:.2f} MHz, transit FWHM {f0['transit']:.2f} MHz, "
             f"modelled FWHM {f0['fwhm']:.2f} MHz",
             ha="center", va="top", fontsize=10, color="#1a3a6b")

    for i, fr in enumerate(frs):
        axf = fig.add_subplot(outer[i, 0])
        axr = fig.add_subplot(outer[i, 1], sharex=axf)
        xd = fr["x"] - fr["cc"]
        m = np.abs(xd) < 14.0
        axf.plot(xd[m], fr["v"][m], ".", ms=2.4, color="#7f9dc4", alpha=0.75)
        xf = np.linspace(-14.0, 14.0, 900)
        axf.plot(xf, fr["model_at"](fr["sol"].x, xf + fr["cc"]), "-",
                 color="#8f1f1f", lw=1.6)
        axf.set_ylabel("signal (V)", fontsize=8)
        axf.tick_params(labelsize=7.5)
        axf.text(0.015, 0.94, f"repeat {i + 1}", transform=axf.transAxes,
                 fontsize=9, va="top", fontweight="bold", color="0.25")
        h_drawn = fr["Vs"] * (1.0 - np.exp(-fr["lin_peak"] / fr["Vs"]))
        axf.text(0.985, 0.94,
                 f"peak height {h_drawn:.2f} V\n"
                 f"centre {pm(fr['cc'] - cc0, fr['cc_err'], 'MHz')} "
                 "from the five-repeat mean\n"
                 f"reduced chi-squared {fr['chi2_red']:.2f}",
                 transform=axf.transAxes, fontsize=7.2, va="top", ha="right",
                 color="0.25")
        # Standardized residuals, the convention fig0 sets at the head of the
        # README and fig22 follows: each point divided by the error the fit
        # weighted it with. In raw volts this strip bulges at line centre
        # because the noise grows with signal level, and a reader takes the
        # bulge for the model failing on the peak. The shaded band is one
        # point error, so "inside the noise" reads as an area.
        pull = (fr["v"] - fr["model_at"](fr["sol"].x, fr["x"])) / fr["sg"]
        axr.axhspan(-1.0, 1.0, color="0.5", alpha=0.15, lw=0)
        axr.plot(xd[m], pull[m], ".", ms=2.0, color="0.55")
        axr.axhline(0.0, color="#8f1f1f", lw=0.9, ls=(0, (4, 3)))
        axr.set_ylabel(r"residual / $\sigma$", fontsize=8)
        axr.tick_params(labelsize=7.5)
        lim = 4.0 * float(np.std(pull[m]))
        axr.set_ylim(-lim, lim)
        if i < 4:
            axf.tick_params(labelbottom=False)
            axr.tick_params(labelbottom=False)
        else:
            axf.set_xlabel("laser detuning (MHz)", fontsize=8.5)
            axr.set_xlabel("laser detuning (MHz)", fontsize=8.5)

    status = next(r["status"] for r in _rows("global_dataset_fit")
                  if r["quantity"] == "beta_self_joint")
    # "and its errors" stood here and was not true: the shared block carries
    # no per-parameter uncertainty on this figure, and the sibling galleries
    # fig16 and fig22 correctly do not claim one.
    _footer(fig, "Sources: results/global_dataset_fit.csv (the shared optimum, "
                 f"{STATUS_WORD.get(status, status.lower())}) "
                 "+ data_raw traces (per-trace data, local "
                 "nuisance refits only). Regenerate: python scripts/make_figures.py.")
    _save(fig, "fig21_joint_fit_five.png")


def fig_joint_fit_twenty():
    """The companion: the same shared physics across all twenty campaign
    power-sweep conditions, brightest repeat each, nothing re-tuned per
    panel. Same code path and the same values of record as fig21."""
    ctx = _gallery_context()
    if ctx is None:
        return
    traces = ctx["traces"]
    peaks = ctx["peaks"]
    POWERS = (0.025, 0.075, 0.125, 0.175, 0.225)

    fig = plt.figure(figsize=(11.8, 8.9))
    # left margin widened to carry a y scale on the first column and the
    # quantity's name beside it: the grid used to have no y ticks, no y tick
    # labels and no y axis title anywhere.
    gs = fig.add_gridspec(1, 1, left=0.115, right=0.985, top=0.825,
                          bottom=0.135)
    inner = gs[0, 0].subgridspec(4, 5, hspace=0.26, wspace=0.10)
    for r, pk in enumerate(peaks):
        for c, P in enumerate(POWERS):
            cell = inner[r, c].subgridspec(2, 1, height_ratios=[3.0, 1.0],
                                           hspace=0.05)
            axc = fig.add_subplot(cell[0])
            axr = fig.add_subplot(cell[1], sharex=axc)
            if c == 0:
                axc.yaxis.set_major_locator(plt.MaxNLocator(3))
                axc.tick_params(axis="y", labelsize=6, length=2)
            else:
                axc.set_yticks([])
            axc.set_xticks([])
            axr.set_ylim(-2.6, 2.6)
            axr.axhline(0.0, color="#a63430", lw=0.7, ls="--", alpha=0.8)
            if c == 0:
                axr.set_yticks([-2, 0, 2])
                axr.tick_params(axis="y", labelsize=6, length=2)
            else:
                axr.set_yticks([])
            if r == 3:
                axr.set_xticks([-10, 0, 10])
                axr.tick_params(axis="x", labelsize=6.5, length=2)
            else:
                axr.set_xticks([])
            for ax in (axc, axr):
                for s in ax.spines.values():
                    s.set_color("0.85")
            recs = [tr for tr in traces if tr["peak"] == pk
                    and tr["T"] == 130.0 and abs(tr["P"] - P) < 1e-9]
            if not recs:
                continue
            rec = max(recs, key=lambda tr: tr["A0"])
            fr = _fit_rec_nuisances(ctx, rec)
            xd = fr["x"] - fr["cc"]
            clean = fr["v"] - (fr["b0"] + fr["b1"] * fr["x"])
            m = np.abs(xd) < 12.0
            axc.plot(xd[m][::3], clean[m][::3], ".", ms=1.1, color="0.5",
                     alpha=0.55)
            xf = np.linspace(-12.0, 12.0, 500)
            curve = (fr["model_at"](fr["sol"].x, xf + fr["cc"])
                     - (fr["b0"] + fr["b1"] * (xf + fr["cc"])))
            axc.plot(xf, curve, "-", color=PEAK_COLOR[pk], lw=1.1)
            pull = (fr["v"] - fr["model_at"](fr["sol"].x, fr["x"])) / fr["sg"]
            axr.axhspan(-1.0, 1.0, color="0.5", alpha=0.15, lw=0)
            axr.plot(xd[m][::3], pull[m][::3], ".", ms=1.0,
                     color=PEAK_COLOR[pk], alpha=0.5)
            axc.text(0.04, 0.90, f"reduced\nchi-squared\n{fr['chi2_red']:.2f}",
                     transform=axc.transAxes, fontsize=5.2, va="top",
                     color="0.4", linespacing=1.1)
            if r == 0:
                axc.set_title(f"{int(round(P * 1000))} mW", fontsize=8.5)
            if c == 0:
                axc.set_ylabel(f"993.{pk} nm\n{_ISO[pk]}", fontsize=8,
                               color=PEAK_COLOR[pk], labelpad=6)
                axr.set_ylabel(r"residual / $\sigma$", fontsize=6.5,
                               color="0.45", labelpad=2)

    # Three stacked blocks used to sit under the title: the model's form, the
    # shared collisional, laser and transit widths, and which parameters are
    # refitted per trace. A fourth paragraph sat under the x axis: that each
    # panel is autoscaled so heights are not comparable across the grid, what
    # the residual strips are divided by and why the reduced chi-squared falls
    # below one, and which column carries the weakest signal. All four are
    # caption material. The shared widths are in
    # results/global_dataset_fit.csv, which the footer cites.
    fig.suptitle("The joint fit across twenty conditions at 130 °C, four hyperfine "
                 "components by five laser powers", fontsize=12, y=0.978, va="top")
    fig.text(0.018, 0.48, "signal above background (V)",
             rotation=90, ha="left", va="center",
             fontsize=8.5, color="0.35")
    fig.text(0.5, 0.105, "laser detuning (MHz)",
             ha="center", va="top", fontsize=7.6, color="0.35")
    status = next(r["status"] for r in _rows("global_dataset_fit")
                  if r["quantity"] == "beta_self_joint")
    _footer(fig, "Sources: results/global_dataset_fit.csv (the shared optimum, "
                 f"{STATUS_WORD.get(status, status.lower())}) "
                 "+ data_raw traces (per-trace data, local nuisance refits "
                 "only). Regenerate: python scripts/make_figures.py.")
    _save(fig, "fig22_joint_fit_twenty.png")


def fig_radiation_environment():
    """The three radiation fields a hot cell puts on these atoms, on one axis.

    WHY THIS FIGURE EXISTS. Three separate questions were put at the bench over
    two days, each about a different colour of light in the same cell, and each
    was answered with its own table. The answers span nineteen orders of
    magnitude in rate, which no table makes legible and a log axis does in one
    look. The left panel says why: the occupation number of a thermal mode
    falls off exponentially in h*nu/kT, and every line of this cascade sits far
    to the blue of where the thermal photons actually are. The right panel is
    the consequence, every channel scored against the drive that produces the
    signal.

    THE READING. Trapped light on the cascade's own infrared legs is a per-cent
    effect and worth carrying. Blackbody light on the same legs is EIGHT orders
    below it, 1874 against 3.3e-5 per second at 130 C, a ratio of 5.6e7.
    (Corrected 2026-08-20. This line said twelve orders, which was true of a
    quantity this docstring no longer names: the thermal OCCUPATION NUMBER at
    the infrared legs is 2e-12 to 5e-12, about twelve orders below unity. The
    number survived a reframing and came to sit beside two bars it does not
    describe. Recomputed from the same functions the panel draws with.)
    The one blackbody channel that is not negligible-squared, 6S to
    6P at 2.7 um, is visible here as the single thermal bar that clears the
    floor, and it is still two parts per million of the natural decay.

    Everything is computed at draw time from the same functions the two
    scripts use, so the figure cannot drift from the record it illustrates.
    """
    import math
    sys.path.insert(0, str(C.REPO_ROOT / "scripts"))
    import run_blackbody_channels as BB                     # noqa: E402
    import run_trapping_channels as TR                      # noqa: E402
    from run_geometry_design import ramp_moments            # noqa: E402
    from rb5s6s.constants import (GAMMA_NAT_HZ, TAU_5P12_S,  # noqa: E402
                                  TAU_6S_S)
    from rb5s6s.polarizability import E_6S_CM               # noqa: E402

    W0, ZC_M, P_MAX = C.W0_MEASURED_M, 2.2e-3, 0.225
    t_c = 130.0
    t_k = t_c + 273.15
    h, kb, cl = 6.62607015e-34, 1.380649e-23, 2.99792458e8

    # the lines this cascade actually has, computed not typed
    lam12, a12 = TR._leg(*TR.LINES_6S[0][:2])
    lam32, a32 = TR._leg(*TR.LINES_6S[1][:2])
    b12 = a12 / (a12 + a32)
    lines = [("D1, detected", 794.979e-9, 1.0 / TAU_5P12_S, "#a63430"),
             ("6S to 5P$_{1/2}$", lam12, a12, "#0072B2"),
             ("6S to 5P$_{3/2}$", lam32, a32, "#0072B2")]
    for e_cm, d_au, tag in ((23715.081, 9.72, "6S to 6P$_{3/2}$"),
                            (23792.591, 13.645, "6S to 6P$_{1/2}$")):
        lam = 1e7 / (e_cm - E_6S_CM) * 1e-9
        lines.append((tag, lam, BB.einstein_a(lam, d_au), "#009E73"))

    fig = plt.figure(figsize=(12.6, 4.9))
    gs = fig.add_gridspec(1, 2, wspace=0.30, left=0.075, right=0.955,
                          top=0.88, bottom=0.30)
    ax, bx = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])

    # ---- (a) the occupation number, and where the thermal photons are ----
    lam_um = np.logspace(np.log10(0.5), np.log10(60.0), 700)
    x = h * cl / (lam_um * 1e-6 * kb * t_k)
    nbar = 1.0 / np.expm1(np.clip(x, 1e-9, 700.0))
    # The photon spectral density peaks near 9.1 um at this temperature, and
    # the band shaded below is computed from that density rather than from a
    # constant, which is why the drawn figure was right while this comment
    # said 7.2 um, the ENERGY peak, until 2026-08-16. Shade where the density
    # is within a decade of its own maximum, which is where the photons are
    dens = (lam_um * 1e-6) ** -4 / np.expm1(np.clip(x, 1e-9, 700.0))
    band = lam_um[dens > 0.1 * dens.max()]
    ax.axvspan(band.min(), band.max(), color="0.88", zorder=0)
    # inside the band and BELOW the curve, which is the only empty region
    # there: the curve rises through the top of the band and struck this
    # label out when it sat above it
    # far right of the band, well below the curve and well clear of the 2.7 um
    # annotation. The first placement put it at the band's geometric centre,
    # which overlapped that annotation by 82 per cent, and I read it as
    # adjacent. The guard measured it.
    ax.text(band.max() * 0.75, 1e-5,
            "where the thermal\nphotons actually are", fontsize=8.0,
            color="0.4", ha="center", va="center")
    ax.plot(lam_um, nbar, color="0.2", lw=2.2, zorder=3)
    for tag, lam, _a, col in lines:
        lu = lam * 1e6
        nb = 1.0 / math.expm1(h * cl / (lam * kb * t_k))
        ax.plot([lu], [nb], "o", color=col, ms=7, zorder=5)
    # label the two ends only, so five markers do not become five labels
    for tag, lam, col, dy, ha in (
            ("the line we detect,\n795 nm", 794.979e-9, "#a63430", 6.0, "left"),
            ("the cascade legs,\n1324 and 1367 nm", lam12, "#0072B2", 0.06, "left"),
            ("6S to 6P, 2.7 µm\nthe one thermal channel\nthat is not nothing",
             1e7 / (23715.081 - E_6S_CM) * 1e-9, "#009E73", 4e-4, "left")):
        lu, nb = lam * 1e6, 1.0 / math.expm1(h * cl / (lam * kb * t_k))
        ax.annotate(tag, xy=(lu, nb), xytext=(lu * 1.5, nb * dy),
                    fontsize=8.2, color=col, ha=ha, va="top",
                    arrowprops=dict(arrowstyle="-", color=col, lw=1.0))
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.5, 60.0)
    ax.set_ylim(1e-22, 30.0)
    ax.set_xlabel("wavelength (µm)")
    ax.set_ylabel(f"thermal occupation number at {t_c:.0f} °C")
    ax.set_title("(a)  every line of this cascade is far from the heat",
                 fontsize=10.5, loc="left")
    ax.grid(alpha=0.25, which="both")

    # ---- (b) the rates that follow, against the drive itself -------------
    m = ramp_moments(W0, P_MAX, ZC_M)
    f_ex = (m["sat_w"] / 2.0) / (1.0 + m["sat_w"])
    primary = 2.0 * math.pi * GAMMA_NAT_HZ * f_ex
    s12 = TR._sigma_peak_cm2(lam12, a12, 2, 2)
    z_r = math.pi * W0 ** 2 / 993.4e-9
    v_beam = math.pi * W0 ** 2 * (2.0 * z_r) * 1e6
    halo_pct = TR.halo_reexcitation(t_c, TR.STANDOFF_CM, f_ex, b12, s12,
                                    v_beam)[2]
    lo_pct, hi_pct = TR.halo_band(t_c, f_ex, b12, s12, v_beam)
    bbr_up = sum(BB.nbar(lam, t_k) * BB.einstein_a(lam, d) * g
                 for lam, d, g in
                 ((1e7 / (23715.081 - E_6S_CM) * 1e-9, 9.72, 2.0),
                  (1e7 / (23792.591 - E_6S_CM) * 1e-9, 13.645, 1.0)))
    bars = [
        ("natural 6S decay", 1.0 / TAU_6S_S, "0.45", None),
        ("the two-photon drive", primary, "#a63430", None),
        ("trapped infrared,\nre-exciting 5P to 6S", primary * halo_pct / 100.0,
         "#0072B2", (primary * lo_pct / 100.0, primary * hi_pct / 100.0)),
        ("blackbody, 6S to 6P", bbr_up, "#009E73", None),
        ("blackbody,\nre-exciting 5P to 6S",
         BB.nbar(lam32, t_k) * a32 * 0.5, "#009E73", None),
        ("blackbody, stimulating D1",
         BB.nbar(794.979e-9, t_k) / TAU_5P12_S, "#009E73", None),
    ]
    ypos = np.arange(len(bars))[::-1]
    for y, (lab, val, col, band_lohi) in zip(ypos, bars):
        bx.barh([y], [val], height=0.62, color=col, edgecolor="0.2", lw=0.8)
        if band_lohi is not None:
            bx.plot(band_lohi, [y, y], color="0.15", lw=1.6, zorder=4)
            bx.plot([band_lohi[0]], [y], "|", color="0.15", ms=9, zorder=4)
            bx.plot([band_lohi[1]], [y], "|", color="0.15", ms=9, zorder=4)
        bx.text(val * 2.2, y, f"{val:.3g}" + (r"  s$^{-1}$" if val > 1e-3
                                              else r"  s$^{-1}$"),
                fontsize=8.0, va="center", color="0.2")
    bx.set_yticks(ypos)
    bx.set_yticklabels([b[0] for b in bars], fontsize=8.4)
    bx.set_xscale("log")
    bx.set_xlim(1e-14, 1e13)
    bx.set_xlabel(r"rate per atom (s$^{-1}$)"
                  f"  ·  130 °C, 225 mW, {W0*1e6:.0f} µm")
    # the decade span is DERIVED, not typed. It was written out as "nineteen"
    # and happened to be right, which is the failure mode protocol 12.9 names:
    # a hand-typed physical fact survives every change to the numbers under it.
    _sp = math.log10(max(b[1] for b in bars) / min(b[1] for b in bars))
    _words = {17: "seventeen", 18: "eighteen", 19: "nineteen", 20: "twenty",
              21: "twenty-one", 22: "twenty-two"}
    bx.set_title(f"(b)  the rates, spanning {_words.get(round(_sp), f'{_sp:.0f}')}"
                 " decades", fontsize=10.5, loc="left")
    bx.grid(axis="x", alpha=0.25, which="both")
    bx.text(0.985, 0.06,
            "the bar on the trapped-infrared row is the\n"
            "standoff band, which is the only quantity here\n"
            "with a geometric rather than an atomic error",
            transform=bx.transAxes, fontsize=7.6, color="0.35",
            ha="right", va="bottom")

    _footer(fig, "figure 27 | rb5s6s.polarizability line data, "
                 "run_trapping_channels (halo + standoff band), "
                 "run_blackbody_channels (thermal), "
                 "run_geometry_design.ramp_moments (the drive)\n"
                 "results/trapping_channels.csv, "
                 "results/blackbody_channels.csv | "
                 "python scripts/make_figures.py")
    _save(fig, "fig27_radiation_environment.png", rect=(0, 0.055, 1, 1))


def fig_cascade_resolved():
    """Why the cascade branching is not the degeneracy weight, resolved.

    WHY THIS FIGURE EXISTS. The pumping branching f is quoted everywhere as the
    naive degeneracy weight of the undriven ground level times 8/9 or 4/9, and
    a reader who knows the hyperfine selection rules will immediately object:
    those two fractions look like an averaging over structure that has real
    exceptions in it. The objection is correct and the answer is not a
    paragraph. EVERY one of the four lines feeds one 5P3/2 level that cannot
    reach the undriven ground level at all, because a J = 1 photon cannot
    change F by two, and those levels are different per line and carry between
    0.17 and 0.70 of that leg.

    Panel (a) draws one line's cascade resolved by intermediate F, with the
    blocked path marked. Panel (b) is the point: the individual intermediate
    contributions scatter over the whole range, and their sums land on exactly
    two values for all four lines and both isotopes. That is a sum rule, and
    scripts/run_zeeman_depletion.py derives it as 2(1-p) with p the purely
    ELECTRONIC non-flip probability, then checks it again as an exact-rational
    density matrix with every coherence kept.

    Read from results/cascade_branching.csv rather than recomputed, because
    that producer needs sympy for exact Wigner symbols and sympy is an optional
    extra here: make_figures must draw in an environment without it.
    """
    import csv as _csv
    rows = list(_csv.DictReader(
        open(C.RESULTS_DIR / "cascade_branching.csv", newline="")))

    def pick(q, key):
        for r in rows:
            if r["quantity"] == q and r["key"] == key:
                return float(r["value"])
        raise KeyError(f"{q} {key}")

    def resolved(leg, lam):
        out = []
        for r in rows:
            if r["quantity"] == f"resolved_weight_{leg}" and r["key"].startswith(lam):
                f_int = int(r["key"].split("_F")[1])
                out.append((f_int, float(r["value"]),
                            pick(f"resolved_branch_{leg}", r["key"])))
        return sorted(out)

    lams = ["993.4121", "993.4154", "993.4192", "993.4207"]
    iso = {"993.4121": "$^{87}$Rb", "993.4154": "$^{85}$Rb",
           "993.4192": "$^{85}$Rb", "993.4207": "$^{87}$Rb"}

    fig = plt.figure(figsize=(12.6, 5.0))
    # bottom was 0.42 when the caption below panel (a) ran to 75 words. That
    # block is 20 words now, and the reserve went with it: at 0.42 a quarter
    # of the canvas was empty white below the panels.
    gs = fig.add_gridspec(1, 2, wspace=0.30, left=0.075, right=0.975,
                          top=0.87, bottom=0.24, width_ratios=[1.0, 1.0])
    ax, bx = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])

    # ---- (a) one line's cascade, resolved -------------------------------
    # A flow diagram was tried first and abandoned: every intermediate level
    # feeds both ground levels, so the lines cross by construction and the
    # blocked path was lost in the tangle. Stacked bars carry the same two
    # numbers per level, the weight and the split, and nothing crosses.
    lam = "993.4121"
    rws = resolved("5P32", lam)
    ypos = np.arange(len(rws))[::-1]
    for y, (f_int, w, b) in zip(ypos, rws):
        back, lost = w * (1.0 - b), w * b
        ax.barh([y], [back], height=0.55, color="#9ecae1", edgecolor="0.25",
                lw=0.8)
        ax.barh([y], [lost], left=[back], height=0.55, color="#a63430",
                edgecolor="0.25", lw=0.8)
        ax.text(w + 0.012, y, f"{w:.2f} of the leg", fontsize=8.2,
                color="0.3", va="center")
        if lost < 1e-12:
            ax.text(back + 0.006, y - 0.34, "nothing lost here", fontsize=8.0,
                    color="#a63430", va="center", ha="left")
    ax.set_yticks(ypos)
    ax.set_yticklabels([f"$F'$ = {f_int}" for f_int, _w, _b in rws],
                       fontsize=10)
    ax.set_xlim(0, 0.62)
    ax.set_xlabel("share of the atoms taking this leg")
    ax.set_title(f"(a)  {lam} nm, {iso[lam]} $F$ = 1 driven, through "
                 r"$5P_{3/2}$", fontsize=10.5, loc="left")
    ax.grid(axis="x", alpha=0.25)
    # direct labels on the widest bar rather than a legend box, which covered
    # a value label wherever it was placed
    widest = max(range(len(rws)), key=lambda k: rws[k][1])
    wy = ypos[widest]
    _f, ww, wb = rws[widest]
    ax.text(ww * (1.0 - wb) / 2.0, wy, "back to $F$ = 1,\nstill in the line",
            fontsize=8.0, color="0.15", ha="center", va="center")
    ax.text(ww * (1.0 - wb) + ww * wb / 2.0, wy + 0.42, "to $F$ = 2,\ngone",
            fontsize=8.0, color="#a63430", ha="center", va="bottom")
    # offset in axes fractions, so it tracks the panel height above
    ax.text(0.0, -0.145,
            r"$F'$ = 0 takes " f"{rws[0][1]:.2f}" r" of this leg, blocked." "\n"
            f"Bars sum to {sum(w*b for _f, w, b in rws):.4f}, which is 4/9 of "
            "the degeneracy weight 5/8.",
            transform=ax.transAxes, fontsize=8.2, color="0.25", va="top")

    # ---- (b) the parts scatter, the sums do not --------------------------
    for k, (leg, col, mk) in enumerate((("5P12", "#0072B2", "o"),
                                        ("5P32", "#009E73", "s"))):
        for j, lam in enumerate(lams):
            naive = pick("naive_weight", lam)
            parts = [w * b / naive for _f, w, b in resolved(leg, lam)]
            xj = j + (-0.13 if k == 0 else 0.13)
            bx.plot([xj] * len(parts), parts, mk, color=col, ms=4.5,
                    alpha=0.45, mew=0)
            bx.plot([xj], [pick(f"leg_ratio_{leg}", lam)], mk, color=col,
                    ms=11, mec="0.15", mew=1.0,
                    label=None)
    for y, lab, col in ((8.0 / 9.0, "8/9\nvia $5P_{1/2}$", "#0072B2"),
                        (4.0 / 9.0, "4/9\nvia $5P_{3/2}$", "#009E73")):
        bx.axhline(y, color=col, lw=1.3, ls=(0, (5, 3)), zorder=0)
        # boxed for the same reason fig24's markers are: the reference line the
        # label names runs straight through the label
        bx.text(3.46, y, lab, fontsize=8.8, color=col, va="center", ha="left",
                bbox=dict(facecolor="white", edgecolor="none", alpha=0.85,
                          pad=1.0))
    bx.set_xticks(range(4))
    bx.set_xticklabels([f"{lam}\n{iso[lam]}" for lam in lams], fontsize=8.4)
    bx.set_xlim(-0.45, 4.12)
    # headroom for the two-line reference labels, which were clipped at the top
    bx.set_ylim(-0.06, 1.08)
    bx.set_ylabel("branching, over its degeneracy weight")
    bx.set_title("(b)  the parts scatter, the sums are two numbers",
                 fontsize=10.5, loc="left")
    bx.grid(axis="y", alpha=0.25)
    # below the axes, not inside them: at axes y = 0.055 this key sat at data
    # y = 0.003 and the zero-weight markers were drawn straight through it
    bx.text(0.5, -0.175,
            "small markers: each intermediate $F$ on its own.  large: the leg's sum.",
            transform=bx.transAxes, fontsize=8.0, color="0.35", ha="center",
            va="top")

    _footer(fig, "figure 28 | results/cascade_branching.csv, written by "
                 "scripts/run_zeeman_depletion.py (Wigner 3j and 6j symbols, "
                 "and the same branching again as an exact-rational density "
                 "matrix)\npython scripts/make_figures.py")
    _save(fig, "fig28_cascade_resolved.png", rect=(0, 0.055, 1, 1))


def fig_isotope_transit():
    """The two isotopes do not share a transit width, and why that is stated
    rather than corrected.

    WHY THIS FIGURE EXISTS. The transit kernel goes as the thermal speed, so it
    goes as one over the square root of the mass, and this cell holds two
    masses. 85Rb is 1.169 per cent faster and its kernel is wider by the same
    fraction, which is 11.4 kHz at 130 C on a width quoted to 0.01 MHz. Every
    fit in this record nevertheless shares one transit width between the
    isotopes, and the reason is the second panel rather than the first.

    THE READING. Against DENSITY, which is the lever the collisional
    coefficient is read from, the misassignment is almost entirely a constant
    OFFSET: it runs 10.53 to 11.42 kHz across a 52-fold change in density,
    while the per-line core width, which is free in every construction here,
    absorbs any constant. What reaches beta is the SLOPE, and the second panel
    draws it against what one standard error on the measured difference between
    the isotopes would look like on the same axes. The two are a factor of 240
    apart, which is why the isotope argument exists in the code as an opt-in
    whose default is the shared behaviour.
    """
    from rb5s6s.density import number_density_cm3
    from rb5s6s.linefit import transit_fwhm_at_T

    temps = np.linspace(60.0, 140.0, 200)
    # THE REFERENCE TRANSIT WIDTH IS READ, NOT TYPED. This was 0.96 with a
    # comment calling it "the record's own transit width at 110 C". The
    # record's value at the ADOPTED 64 um waist is 0.9334, and 0.964 is the
    # value at the tight end of the waist band, w0 about 62 um, which
    # laser_epoch.csv states. The panel's argument, that the two isotopes do
    # not share a transit width, is unaffected either way, and the gap it
    # draws moves by 2.9 per cent. Corrected 2026-08-20 with fig15's, since
    # both were literals whose comments named a source they did not equal.
    ref = C.TRANSIT_FWHM_PLACEHOLDER_MHZ
    w85 = np.array([transit_fwhm_at_T(t, ref, isotope=85) for t in temps])
    w87 = np.array([transit_fwhm_at_T(t, ref, isotope=87) for t in temps])
    sweep = [70.0, 90.0, 110.0, 130.0]
    dens = np.array([number_density_cm3(t) / 1e12 for t in sweep])
    gap = np.array([1e3 * (transit_fwhm_at_T(t, ref, isotope=85)
                           - transit_fwhm_at_T(t, ref, isotope=87))
                    for t in sweep])
    slope, icpt = np.polyfit(dens, gap, 1)
    sigma_beta_khz_per_1e12 = 6.4    # one sigma on the measured beta85-beta87

    fig = plt.figure(figsize=(12.2, 4.7))
    gs = fig.add_gridspec(1, 2, wspace=0.28, left=0.07, right=0.98,
                          top=0.88, bottom=0.38)
    ax, bx = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])

    ax.plot(temps, w85, color="#D55E00", lw=2.2, label=r"$^{85}$Rb, lighter")
    ax.plot(temps, w87, color="#0072B2", lw=2.2, label=r"$^{87}$Rb")
    for t in sweep:
        ax.axvline(t, color="0.85", lw=0.9, zorder=0)
    ax.set_xlabel("cell temperature (°C)")
    ax.set_ylabel("transit FWHM (MHz, transition axis)")
    ax.set_title("(a)  two masses, two crossing speeds, two kernels",
                 fontsize=10.5, loc="left")
    ax.legend(fontsize=9, loc="upper left")
    ax.grid(alpha=0.25)
    xg = 136.0
    ax.plot([xg, xg], [w87[-1], w85[-1]], "-", color="0.25", lw=1.4)
    for yv in (w87[-1], w85[-1]):
        ax.plot([xg - 1.2, xg + 1.2], [yv, yv], "-", color="0.25", lw=1.4)
    ax.text(xg - 2.2, 0.5 * (w85[-1] + w87[-1]),
            f"{1e3*(w85[-1]-w87[-1]):.0f} kHz\nat 140 °C", fontsize=8.6,
            color="0.25", ha="right", va="center")

    dl = np.logspace(np.log10(dens.min() * 0.7), np.log10(dens.max() * 1.4), 50)
    bx.plot(dl, icpt + slope * dl, "-", color="#D55E00", lw=2.0,
            label="the isotope gap, against density")
    bx.plot(dens, gap, "o", color="#D55E00", ms=8, mec="0.15", mew=1.0,
            zorder=4)
    # ABOVE the markers, not below. Placed below, these four labels fell
    # outside the axes and the bottom spine cut them in half. The canvas guard
    # did not fire because they were still inside the FIGURE, which is the gap
    # between "on the canvas" and "inside its own panel". The space above is
    # clear at every point, since the one sigma line runs above the markers
    # everywhere except the leftmost, where it runs below them.
    for d, g, t in zip(dens, gap, sweep):
        bx.annotate(f"{t:.0f} °C", xy=(d, g), xytext=(0, 11),
                    textcoords="offset points", fontsize=8.0, color="0.35",
                    ha="center")
    bx.plot(dl, gap[0] + sigma_beta_khz_per_1e12 * (dl - dens[0]), "--",
            color="0.35", lw=1.8,
            label=r"what ONE $\sigma$ on $\beta_{85}-\beta_{87}$ looks like")
    bx.set_xscale("log")
    bx.set_yscale("log")
    bx.set_xlabel(r"density ($10^{12}$ cm$^{-3}$), the lever $\beta$ is read from")
    bx.set_ylabel("misassigned width (kHz)")
    bx.set_title("(b)  the isotope gap decomposed against density",
                 fontsize=10.5, loc="left")
    bx.legend(fontsize=8.4, loc="upper left")
    bx.grid(alpha=0.25, which="both")
    # every number here computed, and the lines kept short enough to sit
    # inside the panel: a first version hard-coded the two ends of the gap and
    # ran off the right edge
    bx.text(0.0, -0.235,
            f"Gap {gap.min():.2f} to {gap.max():.2f} kHz over "
            f"{dens.max()/dens.min():.0f}x in density. Slope {slope:.4f} kHz "
            r"per $10^{12}$ cm$^{-3}$," "\n"
            f"{100*slope/sigma_beta_khz_per_1e12:.2f} per cent of one "
            r"$\sigma$ on $\beta_{85}-\beta_{87}$.",
            transform=bx.transAxes, fontsize=8.2, color="0.25", va="top")

    _footer(fig, "figure 29 | rb5s6s.linefit.transit_fwhm_at_T (isotope=), "
                 "rb5s6s.constants masses, rb5s6s.density.number_density_cm3\n"
                 "python scripts/make_figures.py")
    _save(fig, "fig29_isotope_transit.png", rect=(0, 0.055, 1, 1))


def fig_third_cumulant():
    """The third cumulant, and why it is the one channel the width budget
    cannot contaminate.

    WHY THIS FIGURE EXISTS. Every symmetric broadening mechanism in this
    experiment contributes to the SECOND cumulant and to nothing odd. The
    natural width, the laser width, the transit kernel and the collisional
    width all add variance and all leave the third cumulant exactly zero. The
    AC-Stark ramp is the only term in the model that is asymmetric, so it is
    the only term that reaches kappa_3.

    That is worth a figure because the second cumulant is where this analysis
    keeps getting stuck. gamma_coll and sigma_laser slide against each other at
    a correlation of about -0.99 with the chi-squared nearly flat, and the
    2026-08-15 width budget failed to close because two independent constraints
    on that pair pulled in opposite directions. None of that reaches kappa_3.

    THE READING, panel by panel. The first panel shows where the asymmetry
    comes from: the shift distribution is the beam's intensity measure pushed
    through the ramp, and for a ONE-photon process it is uniform and symmetric.
    The two-photon weighting is what tilts it, so the skew exists at all only
    because this is a two-photon transition. The second panel is the cumulant
    ladder: three analytic functionals of the single parameter S0, which is
    what makes the fixed-lock session's joint fit a consistency test rather
    than three separate extractions. The third panel is the point of the
    figure, a contribution table in which every symmetric kernel has an empty
    third column. The fourth puts the campaign on it: at 225 mW the predicted
    kappa_3 sits under the noise floor, which is why the record carries a bound
    rather than a value, and it shows what a fixed-lock session buys.
    """
    from rb5s6s.lineshape import ramp_moment_contributions
    from rb5s6s.linefit import _shared_profile_grid
    from rb5s6s import constants as K

    fig = plt.figure(figsize=(11.2, 4.3))
    gs = fig.add_gridspec(2, 3, height_ratios=[2.2, 1.0], hspace=0.10,
                          wspace=0.34)

    # --- panel A: what the ramp does to the LINE, which is the observable --
    axA = fig.add_subplot(gs[0, 0])
    axD = fig.add_subplot(gs[1, 0], sharex=axA)
    nu = np.linspace(-14.0, 14.0, 3001)
    transit = K.transit_fwhm_from_w0(K.W0_MEASURED_M, 110.0) * math.sqrt(
        403.15 / 383.15)
    s0_demo = 3.0                    # exaggerated so the eye can see it
    g0, p0 = _shared_profile_grid(0.58, 1.56, transit, 0.0, "gaussian")
    g1_, p1_ = _shared_profile_grid(0.58, 1.56, transit, s0_demo, "gaussian")
    a = np.interp(nu, g0, p0, left=0, right=0)
    b = np.interp(nu, g1_, p1_, left=0, right=0)
    a, b = a / a.max(), b / b.max()
    axA.plot(nu, a, color="#888780", lw=1.5, ls="--", label="no ramp")
    axA.plot(nu, b, color="#185FA5", lw=2.0,
             label=f"with ramp, $S_0$ = {s0_demo:.0f} MHz")
    axA.set_ylabel("line, peak-normalised")
    axA.set_title("A. the ramp tilts the line itself",
                  fontsize=10, loc="left")
    axA.legend(fontsize=8, frameon=False, loc="upper left")
    axA.tick_params(labelbottom=False)
    axD.plot(nu, b - a, color="#993C1D", lw=1.5)
    axD.axhline(0, color="#B4B2A9", lw=0.8)
    axD.set_ylabel("difference", fontsize=8)
    axD.set_xlabel("detuning  (MHz)")
    axD.text(0.02, 0.10, "one lobe up, one down: that is the third cumulant",
             fontsize=7.5, transform=axD.transAxes, color="#5F5E5A")

    # --- panel B: three cumulants, one parameter ---------------------------
    ax = fig.add_subplot(gs[:, 1])
    S = np.linspace(0.05, 3.0, 160)
    ax.plot(S, np.abs([ramp_moment_contributions(s)["pull"] for s in S]),
            color="#185FA5", lw=1.8, label=r"$|\kappa_1| = \frac{2}{3}S_0$")
    ax.plot(S, [ramp_moment_contributions(s)["excess_var"] for s in S],
            color="#0F6E56", lw=1.8, label=r"$\kappa_2 = S_0^2/18$")
    ax.plot(S, [ramp_moment_contributions(s)["kappa3"] for s in S],
            color="#993C1D", lw=2.2, label=r"$\kappa_3 = S_0^3/135$")
    ax.set_yscale("log")
    ax.set_ylim(1e-6, 30)
    ax.set_xlabel("$S_0$, the ramp depth  (MHz)")
    ax.set_ylabel("cumulant contribution")
    ax.set_title("B. three functionals of one $S_0$", fontsize=10,
                 loc="left")
    ax.legend(fontsize=8.5, frameon=False, loc="lower right")

    # --- panel C: the contribution table -----------------------------------
    ax = fig.add_subplot(gs[:, 2])
    ax.axis("off")
    rows = [("natural", 0, 1, 0), ("laser", 0, 1, 0), ("transit", 0, 1, 0),
            (r"collisional $\gamma_{coll}$", 0, 1, 0),
            ("AC-Stark ramp", 1, 1, 1)]
    ax.text(0.0, 1.02, "C. what each mechanism reaches", fontsize=10,
            transform=ax.transAxes, va="top")
    xs = [0.0, 0.50, 0.68, 0.86]
    for x, h in zip(xs, ["", r"$\kappa_1$", r"$\kappa_2$", r"$\kappa_3$"]):
        ax.text(x, 0.86, h, fontsize=9.5, transform=ax.transAxes,
                color="#5F5E5A")
    ax.plot([0.0, 0.98], [0.83, 0.83], transform=ax.transAxes,
            color="#D3D1C7", lw=0.8)
    ax.add_patch(plt.Rectangle((0.825, 0.30), 0.155, 0.56,
                               transform=ax.transAxes, fill=False,
                               edgecolor="#993C1D", lw=1.5, zorder=5))
    for i, (name, c1, c2, c3) in enumerate(rows):
        y = 0.75 - 0.10 * i
        strong = name.startswith("AC-Stark")
        ax.text(xs[0], y, name, fontsize=9.5, transform=ax.transAxes,
                color="#0b0b0b" if strong else "#52514e")
        for x, c in zip(xs[1:], (c1, c2, c3)):
            ax.text(x, y, "yes" if c else "zero", fontsize=9.5,
                    transform=ax.transAxes,
                    color="#993C1D" if c else "#B4B2A9")
    ax.text(0.0, 0.19,
            r"Every symmetric kernel is empty in $\kappa_3$, so the"
            "\n"
            r"$\gamma_{coll}$ against $\sigma_{laser}$ degeneracy, which"
            "\n"
            r"lives entirely in $\kappa_2$, cannot reach it.",
            fontsize=8.5, transform=ax.transAxes, va="top", color="#5F5E5A")

    _footer(fig, "figure 30 | rb5s6s.linefit._shared_profile_grid, "
                 "rb5s6s.lineshape.ramp_moment_contributions\n"
                 "python scripts/make_figures.py")
    _save(fig, "fig30_third_cumulant.png", rect=(0, 0.10, 1, 1))


def fig_third_cumulant_measured():
    """The third cumulant computed on real traces, and the size of the gap.

    WHY THIS FIGURE EXISTS. Figure 30 argues that kappa_3 is the one channel
    the symmetric width budget cannot contaminate. This one asks what the 2025
    data actually say in that channel, and the answer is worth drawing because
    it is not close.

    THE READING. The first panel is a real trace at the campaign's maximum
    power with the fitted profile through it, and beneath it the residual on a
    magnified axis. An asymmetry of the predicted size would be invisible
    there, which is the point. The second panel computes kappa_3 directly from
    each condition's traces as the third central moment of the baseline-removed
    profile, and plots it against power with its standard error across repeats.
    The measurements straddle zero, the two peaks disagree in sign, and the
    prediction at the record's own bound lies four orders of magnitude below
    the error bars. The third panel converts that into the design number: what
    would have to change for this channel to be measurable at all.

    NOT A DETECTION AND NOT A NULL RESULT ABOUT PHYSICS. The uncertainty here
    is dominated by the profile's own noise and by the free centre, so this
    figure measures the INSTRUMENT's reach in this channel, not the ramp.

    THE 25 mW CONDITION IS EXCLUDED FROM PANEL B and the panel says so. Its
    standard error is an order of magnitude larger than any other point,
    12.99 MHz^3 against 0.25 to 1.30, so including it compresses the four
    informative conditions to a flat line. Its values are +0.12 +- 5.71 for
    4154 and -1.42 +- 12.99 for 4192, both consistent with zero and with
    anything else, so nothing is hidden by leaving it out.
    """
    from rb5s6s.ingest import load_manifest, load_trace, trace_path
    from rb5s6s.linefit import to_frequency
    from rb5s6s.lineshape import ramp_moment_contributions
    from rb5s6s._compat import trapezoid

    # This figure reads RAW TRACES, which the public mirror does not carry by
    # design. Without this it raised rather than returning, and the guard that
    # runs every producer reported it as broken. NOTE the manifest is NOT the
    # right thing to test: the mirror carries data_raw/MANIFEST.csv and omits
    # only the trace directories, so a manifest check passes there and the
    # figure then fails on the first trace it opens.
    if not (C.DATA_RAW_DIR / "p_sweep").is_dir():
        print("  (raw traces absent -- skipping the measured "
              "third-cumulant figure)")
        return None

    rate = {(r["peak"], r["T"], r["P"]): float(r["rate_t"])
            for r in _rows("linefit_conditions")}
    s0_bound = None
    for r in _rows("stark_joint"):
        if r["quantity"] == "S0_225mW_ub95":
            s0_bound = float(r["value"])

    def cumulants(x, y, half=18.0):
        m = np.abs(x) <= half
        x, y = x[m], y[m]
        n = max(len(y) // 8, 5)
        base = np.median(np.r_[y[:n], y[-n:]])
        w = np.clip(y - base, 0, None)
        if w.sum() <= 0:
            return (np.nan,) * 3
        w = w / trapezoid(w, x)
        k1 = trapezoid(w * x, x)
        k2 = trapezoid(w * (x - k1) ** 2, x)
        k3 = trapezoid(w * (x - k1) ** 3, x)
        return k1, k2, k3

    def traces(peak, P):
        out = []
        for r in load_manifest():
            if (r["flag"] == "canonical" and r["peak"] == peak
                    and r["temperature_C"] == "130" and r["power_mW"] == str(P)
                    and r["rf_on"] == "False"):
                tm, v = load_trace(trace_path(r))
                x = to_frequency(np.asarray(tm, float), rate[(peak, "130", str(P))])
                v = np.asarray(v, float)
                out.append((x - x[int(np.argmax(v))], v))
        return out

    fig = plt.figure(figsize=(11.0, 4.6))
    gs = fig.add_gridspec(2, 3, height_ratios=[2.1, 1.0], hspace=0.08,
                          wspace=0.32)

    # --- panel A: a real trace, and its residual ---------------------------
    axA = fig.add_subplot(gs[0, 0])
    axR = fig.add_subplot(gs[1, 0], sharex=axA)
    x, v = traces("4192", 225)[0]
    k1, k2, k3 = cumulants(x, v)
    x = x - k1                      # fold about the CENTROID, not the argmax
    m = np.abs(x) <= 18.0
    xs, vs = x[m], v[m]
    n = max(len(vs) // 8, 5)
    base = np.median(np.r_[vs[:n], vs[-n:]])
    axA.plot(xs, vs - base, lw=0.9, color="#185FA5")
    axA.axvline(0.0, color="#993C1D", lw=1.0, ls=":")
    axA.set_ylabel("signal  (V)")
    axA.set_title("A. one trace, 4192 nm at 225 mW", fontsize=10, loc="left")
    axA.tick_params(labelbottom=False)
    mirror = np.interp(-xs, xs, vs - base, left=np.nan, right=np.nan)
    axR.plot(xs, (vs - base) - mirror, lw=0.9, color="#5F5E5A")
    axR.axhline(0, color="#B4B2A9", lw=0.8)
    axR.set_xlabel("detuning from the centroid  (MHz)")
    axR.set_ylabel("signal minus\nits mirror  (V)", fontsize=8)
    axR.text(0.02, 0.08, "folded about the centroid, so a pure shift cancels",
             fontsize=7.5, transform=axR.transAxes, color="#5F5E5A")

    # --- panel B: measured kappa_3 against power ---------------------------
    ax = fig.add_subplot(gs[:, 1])
    colours = {"4154": "#185FA5", "4192": "#0F6E56"}
    for peak in ("4154", "4192"):
        Ps, ks, es = [], [], []
        for P in (225, 175, 125, 75):   # acquisition order; 25 mW excluded, see below
            tr = traces(peak, P)
            if not tr:
                continue
            k3s = [cumulants(xx, vv)[2] for xx, vv in tr]
            k3s = [k for k in k3s if np.isfinite(k)]
            if len(k3s) < 2:
                continue
            Ps.append(P)
            ks.append(np.mean(k3s))
            es.append(np.std(k3s, ddof=1) / np.sqrt(len(k3s)))
        ax.errorbar(Ps, ks, yerr=es, fmt="o-", ms=4, lw=1.2, capsize=3,
                    color=colours[peak], label=f"{peak} nm")
    ax.axhline(0, color="#B4B2A9", lw=1.0)
    # 25 mW IS EXCLUDED FROM THIS PANEL and the exclusion is stated on it. Its
    # standard error is an order of magnitude larger than every other point
    # (12.99 against 0.25 to 1.30 MHz^3), so plotting it compresses the four
    # informative conditions into a line. It carries no information about this
    # channel either way, and the docstring records the values.
    ax.set_ylim(-1.6, 1.6)
    Pg = np.linspace(20, 235, 100)
    pred = [ramp_moment_contributions(s0_bound * pp / 225.0)["kappa3"]
            for pp in Pg]
    ax.plot(Pg, pred, color="#993C1D", lw=2.0,
            label=r"prediction at the $S_0$ bound")
    ax.set_xlabel("power at the cell  (mW)")
    ax.set_ylabel(r"measured $\kappa_3$  (MHz$^3$)")
    ax.set_title("B. what the 2025 data say in this channel", fontsize=10,
                 loc="left")
    ax.legend(fontsize=8, frameon=False, loc="lower right")
    ax.text(0.50, 0.97,
            "the two peaks disagree in SIGN, and both straddle zero\n"
            "25 mW is excluded: its error is an order larger",
            transform=ax.transAxes, ha="center", va="top", fontsize=8,
            color="#5F5E5A")

    # --- panel C: the gap, and what closes it ------------------------------
    ax = fig.add_subplot(gs[:, 2])
    k3_pred = ramp_moment_contributions(s0_bound)["kappa3"]
    err225 = []
    for peak in ("4154", "4192"):
        k3s = [cumulants(xx, vv)[2] for xx, vv in traces(peak, 225)]
        k3s = [k for k in k3s if np.isfinite(k)]
        err225.append(np.std(k3s, ddof=1) / np.sqrt(len(k3s)))
    noise = float(np.mean(err225))
    gap = noise / k3_pred
    ax.bar([0], [k3_pred], color="#993C1D", width=0.55)
    ax.bar([1], [noise], color="#888780", width=0.55)
    ax.set_yscale("log")
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["predicted\nat the bound", "2025 error\non one condition"],
                       fontsize=8)
    ax.set_ylabel(r"$\kappa_3$  (MHz$^3$)")
    ax.set_title("C. the gap is a factor of %.0f" % gap, fontsize=10,
                 loc="left")
    ax.text(0.06, 0.62,
            r"$\kappa_3 \propto S_0^3 \propto (P/w_0^2)^3$"
            "\n\n"
            f"closing this needs {gap ** (1/3):.0f}x in $S_0$,"
            f"\nso {gap ** (1/3):.0f}x the power or a\n"
            f"waist smaller by {gap ** (1/6):.1f}x.",
            transform=ax.transAxes, ha="left", va="center", fontsize=8.5,
            color="#5F5E5A")

    _footer(fig, "figure 31 | data_raw 130 C power sweep, "
                 "rb5s6s.lineshape.ramp_moment_contributions, "
                 "results/stark_joint.csv S0_225mW_ub95\n"
                 "python scripts/make_figures.py")
    _save(fig, "fig31_third_cumulant_measured.png", rect=(0, 0.09, 1, 1))


def fig_achieved_vs_achievable():
    """What the 2025 data established beside what a designed session projects.

    WHY THIS FIGURE EXISTS. The landing page states the achieved and the
    achievable side by side in two tables, and a table cannot show how far
    apart they are. Both panels put the limits the archive supports, the value
    the physics predicts, and the precision a designed session projects on one
    logarithmic axis of the same unit, so the distances are read rather than
    computed.

    A PRECISION IS DRAWN AS A LENGTH, NOT AS AN INTERVAL, and that choice is
    the correction of a first version of this figure. That version drew each
    projected one-sigma precision as an error bar centred on the predicted
    value, which asserts a future measurement AT that value. In panel B the
    archive's own limit sits below the prediction, so the drawing contradicted
    itself: it placed a future result inside a region the same panel showed as
    excluded. A one-sigma precision is a length in megahertz, the size of an
    error bar and not a claim about where the centre falls, so it is plotted
    as a magnitude on the same axis and the row label says what it is. Nothing
    in the figure now assumes an outcome.

    NO DISTRIBUTION IS DRAWN, deliberately. Each projected value is a single
    envelope number attached to one session design, not a sample, so any
    density-shaped mark here would render a spread the record does not carry.

    THE TENSION IN PANEL B IS THE RESULT, not a blemish to smooth. The primary
    joint bound sits below the predicted value, which is an exclusion at about
    the two-sigma level rather than a comfortable one, and the robustness
    subset that drops one peak does not sit below it. Both bounds are drawn,
    because the distance between them is what makes the exclusion marginal.
    """
    from rb5s6s import constants as K

    ARCHIVE = "#33322E"
    PREDICT = "#A2582B"
    DESIGN = "#2F5D50"

    beta_rows = [r for r in _rows("beta_self_probe") if r.get("headline") == "yes"]
    beta_rows.sort(key=lambda r: r["peak"])

    # Only the rows drawn are converted: both files also carry rows whose
    # value is descriptive text rather than a number.
    wanted = ("proj_beta_self_sigma", "proj_beta_self_detection_sigma",
              "input_beta_self_expected", "proj_pull_S0_sigma")
    proj = {(r["quantity"], r["key"]): float(r["value"])
            for r in _rows("projections") if r["quantity"] in wanted}
    anchor = proj[("input_beta_self_expected", "vdW anchored")]

    stark = {r["quantity"]: r["value"] for r in _rows("stark_joint")}
    s0_ub = float(stark["S0_225mW_ub95"])
    s0_drop = float(stark["S0_225mW_ub95_drop4192"])
    s0_pred = float(stark["S0_225mW_pred"])

    fig, axes = plt.subplots(1, 2, figsize=(11.6, 4.6))

    def limit_row(ax, y, value, label):
        ax.annotate("", xy=(value * 0.42, y), xytext=(value, y),
                    arrowprops=dict(arrowstyle="->", color=ARCHIVE, lw=1.5))
        ax.plot([value], [y], "|", color=ARCHIVE, markersize=12,
                markeredgewidth=1.9)
        ax.text(value * 1.14, y, label, va="center", ha="left", fontsize=7.9,
                color=ARCHIVE, bbox=_LABEL_BOX)

    def precision_row(ax, y, sigma, label):
        ax.plot([sigma], [y], "D", color=DESIGN, markersize=6.0)
        ax.annotate("", xy=(sigma, y), xytext=(sigma * 0.999, y),
                    arrowprops=dict(arrowstyle="-", color=DESIGN, lw=0))
        ax.text(sigma * 1.16, y, label, va="center", ha="left", fontsize=7.9,
                color=DESIGN, bbox=_LABEL_BOX)

    # ------------------------------- panel A -------------------------------
    ax = axes[0]
    labels, y = [], 0
    for r in beta_rows:
        v = 1e3 * float(r["bound95_nscale"])
        limit_row(ax, y, v, bound(v, dp=0, kind="upper", unit="kHz"))
        labels.append(K.peak_label(r["peak"]))
        y += 1
    n_limit_rows = y

    ax.axvline(anchor, ls="--", lw=1.2, color=PREDICT)
    ax.text(anchor * 1.22, -0.62, "van der Waals anchor",
            fontsize=7.6, color=PREDICT, ha="left", va="center")

    for key, label in (("interleaved, 20 K cold-spot lag", "interleaved session"),
                       ("archival block noise, 20 K cold-spot lag",
                        "at the archive noise level")):
        s = proj[("proj_beta_self_sigma", key)]
        sig = proj[("proj_beta_self_detection_sigma", key)]
        precision_row(ax, y, s, f"{s:.2f} kHz, so {sig:.1f} sigma on the anchor")
        labels.append(label)
        y += 1

    _ledger_axis(ax, labels, n_limit_rows, 0.04, 400,
                 "collisional coefficient (kHz per $10^{12}$ cm$^{-3}$)",
                 "A. the collision rate")

    # ------------------------------- panel B -------------------------------
    ax = axes[1]
    labels, y = [], 0
    limit_row(ax, y, s0_ub, bound(s0_ub, dp=2, kind="upper", unit="MHz"))
    labels.append("all three sessions")
    y += 1
    limit_row(ax, y, s0_drop, bound(s0_drop, dp=2, kind="upper", unit="MHz"))
    labels.append("the same fit, one peak dropped")
    y += 1
    n_limit_rows = y

    ax.axvline(s0_pred, ls="--", lw=1.2, color=PREDICT)
    ax.text(s0_pred * 1.1, -0.62, f"predicted {s0_pred:.2f} MHz", fontsize=7.6,
            color=PREDICT, ha="left", va="center")

    for key, label in (("6 per day, 1 day", "6 cycles, one day"),
                       ("24 per day, 1 day", "24 cycles, one day"),
                       ("24 per day, 2 days", "24 cycles, two days")):
        s = proj[("proj_pull_S0_sigma", key)]
        precision_row(ax, y, s, f"{s:.3f} MHz")
        labels.append(label)
        y += 1

    _ledger_axis(ax, labels, n_limit_rows, 0.02, 4.0,
                 "light-shift amplitude at the maximum drive power (MHz)",
                 "B. the light shift")

    fig.text(0.5, 0.95,
             "arrows are limits the 2025 data support, diamonds are the "
             "one-sigma precision a designed session projects",
             ha="center", fontsize=8.3, color="#5F5E5A")

    _footer(fig, "figure 32 | results/beta_self_probe.csv, "
                 "results/stark_joint.csv, results/projections.csv\n"
                 "python scripts/make_figures.py")
    _save(fig, "fig32_achieved_vs_achievable.png", rect=(0, 0.09, 1, 0.93))


_LABEL_BOX = dict(facecolor="white", edgecolor="none", alpha=0.82, pad=1.2)
"""Keeps a ledger label readable where it crosses the prediction line."""


def _ledger_axis(ax, labels, split_after, xlo, xhi, xlabel, title):
    """Shared axis dressing for the two ledger panels of figure 32."""
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_ylim(-0.8, len(labels) - 0.3)
    ax.invert_yaxis()
    ax.set_xscale("log")
    ax.set_xlim(xlo, xhi)
    ax.set_xlabel(xlabel)
    ax.set_title(title, fontsize=10, loc="left")
    ax.grid(axis="x", alpha=0.18)
    ax.axhline(split_after - 0.5, color="#BFBDB6", lw=0.8)


def fig_identifiability_matrix():
    """Which quantities each measurement configuration determines.

    WHY THIS FIGURE EXISTS. The landing page states in prose that the archive
    bounds several quantities without identifying them, and that specific
    additions to the apparatus would change specific entries in that
    statement. A matrix shows the change itself, which prose cannot: reading
    down a column says what one quantity's status would become, and reading
    across a row says what one configuration would buy.

    THE TWO DIMENSIONS ARE KEPT SEPARATE, which is the whole design of the
    drawing. The FILL is the epistemic status the configuration reaches for
    that quantity. The HATCH is whether reaching it needs a new measurement
    rather than a reanalysis of data already held. Those are different
    questions, so a cell can honestly read bounded and requiring new data at
    once, and collapsing them into one scale would hide exactly the
    distinction the page is built on.

    NOTHING BELOW THE FIRST ROW IS A RESULT. The first row is the archive and
    is drawn from the diagnostics. Every other row is a configuration that has
    not been run, so its cells are the status that configuration would reach
    given the documented assumptions and the projected machinery, and the
    caption says so.
    """
    import matplotlib.patches as mpatches

    OBSERVED, INFERRED, BOUNDED, UNIDENT = 3, 2, 1, 0
    FILL = {OBSERVED: "#2F5D50", INFERRED: "#7C9A6E", BOUNDED: "#D9C48A",
            UNIDENT: "#EFEDE6"}
    NAME = {OBSERVED: "measured", INFERRED: "identified",
            BOUNDED: "bounded", UNIDENT: "not identified"}
    TEXT = {OBSERVED: "white", INFERRED: "#2A2A26", BOUNDED: "#2A2A26",
            UNIDENT: "#6B6A64"}

    cols = ["collision\ncoefficient", "laser\nwidth", "light-shift\namplitude",
            "beam\nwaist"]
    # (row label, [(status, needs_new_data) per column])
    rows = [
        ("the 2025 archive",
         [(BOUNDED, False), (BOUNDED, False), (BOUNDED, False), (UNIDENT, False)]),
        ("plus an independent\nlaser-width measurement",
         [(INFERRED, True), (OBSERVED, True), (BOUNDED, True), (UNIDENT, False)]),
        ("plus a wide span with\nthe pedestal fitted",
         [(INFERRED, True), (INFERRED, True), (BOUNDED, True), (UNIDENT, False)]),
        ("plus a randomised\npower ladder",
         [(INFERRED, True), (INFERRED, True), (OBSERVED, True), (UNIDENT, False)]),
        ("plus a beam profile\nmeasured on the day",
         [(INFERRED, True), (INFERRED, True), (INFERRED, True), (OBSERVED, True)]),
    ]

    fig, ax = plt.subplots(figsize=(9.2, 4.5))
    for j, (label, cells) in enumerate(rows):
        for i, (status, new) in enumerate(cells):
            ax.add_patch(mpatches.Rectangle(
                (i, -j), 0.94, 0.9, facecolor=FILL[status],
                edgecolor="#9A9890", linewidth=0.8,
                hatch="///" if new else None))
            ax.text(i + 0.47, -j + 0.45, NAME[status], ha="center",
                    va="center", fontsize=8, color=TEXT[status])

    ax.set_xlim(-0.05, len(cols))
    ax.set_ylim(-len(rows) + 0.75, 1.05)
    ax.set_xticks([i + 0.47 for i in range(len(cols))])
    ax.set_xticklabels(cols, fontsize=8.6)
    ax.xaxis.set_ticks_position("top")
    ax.set_yticks([-j + 0.45 for j in range(len(rows))])
    ax.set_yticklabels([r[0] for r in rows], fontsize=8.4)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)

    handles = [mpatches.Patch(facecolor=FILL[s], edgecolor="#9A9890",
                              label=NAME[s]) for s in (OBSERVED, INFERRED,
                                                       BOUNDED, UNIDENT)]
    handles.append(mpatches.Patch(facecolor="white", edgecolor="#9A9890",
                                  hatch="///", label="needs new data"))
    ax.legend(handles=handles, loc="lower center", ncol=5, frameon=False,
              fontsize=8, bbox_to_anchor=(0.5, -0.19))

    _footer(fig, "figure 33 | results/identifiability.csv, "
                 "results/linefit_conditions.csv, docs/PLAN.md sections 10a to 10c\n"
                 "python scripts/make_figures.py")
    _save(fig, "fig33_identifiability_matrix.png", rect=(0, 0.10, 1, 1))


def main() -> int:
    fig_width_vs_density()
    fig_power_sweep()
    fig_transit_mc()
    fig_amplitude_ratios()
    fig_pooled_width()
    fig_gamma_floor()
    fig_identifiability_profile()
    fig_ruler()
    fig_degeneracy_vs_observable()
    fig_laser_history()
    fig_ramp_construction()
    fig_level_scheme()
    fig_hyperfine_pumping()
    fig_wavemeter_reconstruction()
    fig_drift_story()
    fig_fit_gallery()
    fig_single_peak_fits()
    fig_width_trends()
    fig_magic_wavelengths()
    fig_method_loop()
    fig_joint_fit_five()
    fig_joint_fit_twenty()
    # Added 2026-08-10. These three were written on 2026-08-10, drawn once by
    # calling them directly, and never added here, so `make_figures.py` did not
    # reproduce them and `run_all.sh` could not either. They were committed
    # PNGs with no live producer. tests/test_figures_have_a_producer.py now
    # fails if that happens again.
    fig_weak_field_limit()
    fig_retro_combination()
    fig_lineshape_kernels()
    fig_radiation_environment()
    fig_cascade_resolved()
    fig_isotope_transit()
    fig_third_cumulant()
    fig_third_cumulant_measured()
    fig_achieved_vs_achievable()
    fig_identifiability_matrix()
    print(f"wrote figures to {FIG}/")
    for p in sorted(FIG.glob("*.png")):
        print(f"  {p.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


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

import numpy as np
from scipy.optimize import least_squares
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C  # noqa: E402
from rb5s6s.density import density_units  # noqa: E402
from rb5s6s.constants import (  # noqa: E402
    GAMMA_NAT_HZ, TRACE_N_POINTS, TRACE_DT_S,
    TOOTH_SPACING_LASER_HZ, DRIFT_RATE_LASER_HZ_PER_MIN)

GNAT = GAMMA_NAT_HZ / 1e6
FIG = C.REPO_ROOT / "figures"
FIG.mkdir(exist_ok=True)
# Fingerprint of the results/ CSVs these figures are drawn from, stamped into
# each PNG's metadata so a stale figure (results changed, figure not redrawn)
# is caught by tests/test_figures_fresh.py without a fragile pixel compare.
_DATA_FP = C.results_fingerprint()


def _save(fig, name, rect=None):
    """tight_layout + savefig with the data fingerprint embedded, then close.

    rect is passed through to tight_layout: the footer is drawn with fig.text,
    which the layout engine cannot see, so a figure whose axis label would
    otherwise land on the footer reserves the bottom strip explicitly
    (fig3 does)."""
    fig.tight_layout(rect=rect)
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
_ISO = {"4121": "$^{87}$Rb F1", "4154": "$^{85}$Rb F2",
        "4192": "$^{85}$Rb F3", "4207": "$^{87}$Rb F2"}
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


def _rows(name):
    return list(csv.DictReader(open(C.RESULTS_DIR / f"{name}.csv")))


def _temperature_top_axis(ax, ticks):
    """A cell-temperature axis across the top of a density plot.

    The density axis is the physical one (a collisional rate multiplies N),
    but every condition in the archive is named by its oven temperature, so
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
        # formatter: pin the ticks to the archive's own oven settings and
        # write them as plain degrees.
        sec.set_xticks(list(ticks))
        sec.set_xticklabels([f"{T:g}" for T in ticks])
        sec.minorticks_off()
    return sec


def fig_width_vs_density():
    """C1: total line FWHM against density, one series per peak.

    Both axes are named: density on the bottom because a collisional rate
    multiplies N, cell temperature on the top because that is what the
    archive's conditions are called. The 130 C column is the power sweep's
    225 mW anchor (`serves_t130`), and the spread of the other four powers
    at that same density is drawn behind it, so the reader sees the width
    that one curated choice carries.

    The headline claim is the one the four points support: the widths rise,
    and they rise by a few percent while the density rises fifty-three fold,
    which is why the self-broadening coefficient comes out of this archive as
    a bound. The earlier title claimed non-monotonicity, which the error bars
    do not support (every downward step is at or below 1 sigma)."""
    rows = _rows("linefit_conditions")
    fig, ax = plt.subplots(figsize=(7.8, 5.3))
    N130 = density_units(130.0)
    rises = []
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
        rises.append(100.0 * (W[-1] / W[0] - 1.0))
        # the five-power spread at 130 C, drawn behind the anchor point
        if p130:
            ax.plot([N130, N130], [min(p130), max(p130)], "-",
                    color=PEAK_COLOR[peak], lw=4, alpha=0.16,
                    solid_capstyle="butt", zorder=1)
        # the joining line is a guide only: nothing was measured between the
        # four conditions, so it stays faint under the markers
        ax.plot(N, W, "-", color=PEAK_COLOR[peak], lw=0.9, alpha=0.45,
                zorder=2)
        ax.errorbar(N, W, yerr=We, fmt="o", color=PEAK_COLOR[peak],
                    label=PEAK_LABEL[peak], ms=5, capsize=2, lw=1.3, zorder=3)
    ax.set_xscale("log")
    ax.set_ylim(4.48, 5.95)
    ax.set_xticks([density_units(T) for T in (70.0, 90.0, 110.0, 130.0)])
    ax.set_xticklabels(["0.56", "2.4", "9.1", "29"])
    ax.minorticks_off()
    ax.set_xlabel(r"Rb density $N$  ($10^{12}\,\mathrm{cm^{-3}}$)")
    ax.set_ylabel("total line FWHM  (MHz at the two-photon transition)")
    sec = _temperature_top_axis(ax, (70.0, 90.0, 110.0, 130.0))
    sec.set_xlabel("cell temperature (°C)", fontsize=9.5)
    sec.tick_params(labelsize=8.5)
    ax.legend(fontsize=8, ncol=2, loc="upper left", framealpha=0.95,
              frameon=True)
    fig.suptitle("The linewidth against Rb density, at the four campaign "
                 "temperatures", fontsize=12, y=0.968)
    # The reading lives in the band the ylim leaves empty under the data
    # (every width sits above 4.8), so it survives _save's tight_layout,
    # which repositions axes without regard for figure-level text.
    ax.text(0.135, 0.028,
            f"Density rises 53-fold from 70 to 130 °C while the widths rise "
            f"{min(rises):.0f} to {max(rises):.0f} percent,\n"
            f"so this archive bounds the self-broadening coefficient rather "
            f"than measuring it.\n"
            f"Shading at 130 °C: the spread of the other four powers about "
            f"the 225 mW anchor.\n"
            f"The 6S natural width is {GNAT:.2f} MHz. Preliminary, "
            f"conditional on the beam waist.",
            transform=ax.transAxes, ha="left", va="bottom",
            fontsize=8.3, color="0.3", linespacing=1.65)
    _footer(fig, "Sources: results/linefit_conditions.csv; N(T) from "
                 "rb5s6s/density.py (Nesmeyanov, 20% scale systematic). "
                 "Regenerate: python scripts/make_figures.py.")
    _save(fig, "fig1_width_vs_density.png")


def fig_power_sweep():
    """C3: FWHM shows no power trend; amplitude ~ P^2.

    The observed FWHM spread (3-8%) EXCEEDS the <=2% the ramp law predicts,
    so the title must not present the prediction as the observation -- it is
    between-block scatter, and no peak keeps a significant slope once that
    over-dispersion is absorbed (worst 1.7 sigma). Titling this "flat" read
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
        a1.errorbar(P, [x[1] for x in d], yerr=[x[2] for x in d], fmt="-o",
                    color=PEAK_COLOR[peak], label=PEAK_LABEL[peak], ms=4, lw=1.3, capsize=2)
        a2.errorbar(P, [x[3] for x in d], yerr=[x[4] for x in d], fmt="o",
                    color=PEAK_COLOR[peak], ms=4, capsize=2)
    a1.set_xlabel("power (mW)"); a1.set_ylabel("FWHM (MHz, transition)")
    a1.set_title("No power trend in the linewidth\n"
              "(observed 3–8% scatter; ramp predicts $\\leq$2%)", fontsize=9)
    a1.legend(fontsize=8)
    # amplitude log-log: a slope-2 (P^2) fit anchored to each peak's own data, so
    # the guide tracks the points instead of floating beside them. Line drawn
    # over the campaign's own measured power range, not a fixed guess.
    a2.set_xscale("log"); a2.set_yscale("log")
    P_all = np.array(sorted({x[0] for v in by.values() for x in v}), float)
    Pline = np.array([P_all.min(), P_all.max()])
    for i, peak in enumerate(("4121", "4154", "4192", "4207")):
        d = sorted(by[peak])
        P = np.array([x[0] for x in d], float)
        A = np.array([x[3] for x in d], float)
        logk = np.mean(np.log10(A) - 2.0 * np.log10(P))  # least-squares slope-2 intercept
        a2.plot(Pline, 10 ** logk * Pline ** 2, "--", color=PEAK_COLOR[peak], lw=1.0,
                label=r"$\propto P^2$ fit" if i == 0 else None)
    a2.set_xlabel("power (mW)"); a2.set_ylabel("peak amplitude (V)")
    a2.set_title("Amplitude $\\propto P^2$\n(two-photon rate law)", fontsize=9)
    a2.legend(fontsize=8)
    fig.suptitle("Generic laws: pressure broadening does not depend on drive power; "
                 "two-photon excitation rate scales as intensity squared.\n"
                 "Rb instance: the 993 nm line's FWHM and amplitude vs power, both tested "
                 "against those two predictions.", fontsize=9.5, y=0.975)
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

    fig, ax = plt.subplots(figsize=(6, 4.6))
    ax.errorbar(w0, natx, yerr=natx_err, fmt="-o", color="#0072B2", ms=5, lw=1.6,
                capsize=2, label="natural ⊗ transit (MC)")
    ax.axhline(OBSERVED, ls="--", color="#D55E00", lw=1.3,
               label=f"observed total ~{OBSERVED:.2f} MHz")
    ax.axhline(GNAT, ls=":", color="0.4", lw=1, label="natural alone")
    # shade the laser-narrow region: where nat(x)transit >= observed, i.e.
    # up to the computed crossover (not the leftmost data point -- the old
    # version capped the shading at min(w0), under-covering the region
    # between it and the true crossover).
    ax.fill_between([min(w0.min(), w0_cross) - 8.0, w0_cross], GNAT, 6.0,
                    color="#009E73", alpha=0.10)
    ax.annotate("laser narrow\n(transit fills\nthe width budget)",
                (w0_cross - 7.0, 4.65), fontsize=8, color="#009E73",
                ha="center", va="top")
    ax.annotate("laser ~1 MHz", (w0_cross + 12.0, 4.2), fontsize=8, color="0.3")
    ax.set_xlabel(r"beam waist $w_0$ ($\mu$m): not yet measured (knife-edge pending)")
    ax.set_ylabel("FWHM (MHz, transition)")
    ax.set_title("Generic law: transit-time broadening grows as the beam narrows\n"
                 "(shorter crossing time, larger frequency spread). Instance: "
                 "natural $\\otimes$ transit\ncrosses the observed total near "
                 f"$w_0\\approx{w0_cross:.0f}\\,\\mu\\mathrm{{m}}$, "
                 "the laser-narrow boundary",
                 fontsize=9)
    ax.legend(fontsize=8, loc="center right")
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
    keys = {"4207/4121": "993.4207 / 993.4121 nm ($^{87}$Rb)",
            "4192/4154": "993.4192 / 993.4154 nm ($^{85}$Rb)"}
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
        ax.errorbar(T, m, yerr=e, fmt="-o", color=col, ms=5, lw=1.3, capsize=2, label=lab)
        ax.axhline(pred, ls="--", color=col, lw=1)
        frac = Fraction(pred).limit_denominator(12)
        ax.annotate(f"predicted {frac.numerator}/{frac.denominator}",
                    (128, pred + (0.03 if pred > 1.5 else -0.10)),
                    fontsize=8, color=col, ha="right")
    ax.set_xlabel("temperature (°C)")
    ax.set_ylabel("area ratio")
    ax.set_title("Generic law: for a scalar operator, transition strengths ratio as the\n"
                 "upper-level statistical weight $(2F+1)$. Instance: two within-isotope "
                 "area ratios\n"
                 "1–3% within-block, but 30–50% between-block drift ⇒ archive can't test it",
                 fontsize=8.7)
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
                label="pooled: 4-peak mean ± scatter/√4", zorder=5)
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
        a1.plot(Nf, pooled[0] + 0.5346 * bhead * (Nf - N[0]), "--", color="0.35",
                lw=1.4, label=(r"min. growth if $\beta$=%.3f were linear"
                               r" (Voigt slope $\geq$0.53)") % bhead)
    a1.set_xscale("log")
    a1.set_xlabel(r"Rb density $N$  ($10^{12}\,\mathrm{cm^{-3}}$, log)")
    a1.set_ylabel("total line FWHM (MHz, transition)")
    a1.set_title("Pooled width vs density: individual peaks (faint) are\n"
                 "statistics-limited and non-monotonic. The pooled\n"
                 "mean rises cleanly. β₈₅ and β₈₇ agree within ~1σ,\n"
                 "consistent but not discriminating. Still a bound.",
                 fontsize=8)
    a1.legend(fontsize=8, loc="upper left")
    # panel B: σ_laser(T) is MODEL-DEPENDENT -> the "anomaly" is degeneracy, not drift
    gf = _rows("global_fit")
    sl = sorted((float(r["key"][:-1]), float(r["value"]), float(r["err"]))
                for r in gf if r["quantity"] == "sigma_laser")
    a2.errorbar([x[0] for x in sl], [x[1] for x in sl], yerr=[x[2] for x in sl],
                fmt="-o", color="#D55E00", ms=6, lw=1.6, capsize=3,
                label=r"global fit ($\beta\cdot N$-tied)")
    freeT, freeS = [], []
    for T in (70, 90, 110):
        v = [(float(r["sigma_laser"]), float(r["sigma_laser_err"])) for r in rows
             if r["role"] == "t_sweep" and int(float(r["T"])) == T]
        s = np.array([x[0] for x in v]); w = 1.0 / np.array([x[1] for x in v]) ** 2
        freeT.append(T); freeS.append(float(np.sum(w * s) / np.sum(w)))
    a2.plot(freeT, freeS, "-s", color="#0072B2", ms=6, lw=1.6,
            label="free per-condition (4 peaks agree)")
    a2.set_xlabel("temperature (°C)")
    a2.set_ylabel(r"$\sigma_\mathrm{laser}$ (MHz, transition)")
    a2.set_title("The laser linewidth $\\sigma_L(T)$ is MODEL-DEPENDENT: the free fit is "
                 "flat (~1.6,\n"
                 "4 peaks agree, $\\chi^2<1$, an in-sample check only); the tied drop is\n"
                 "the $\\beta$-$\\sigma_L$ degeneracy, not a physical laser drift", fontsize=8)
    a2.legend(fontsize=7.5)
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
    fig, ax = plt.subplots(figsize=(6.6, 4.8))
    for peak in peaks:
        gv = [gam(peak, T) for T in Ts]
        gval = np.array([g[0] for g in gv])
        gerr = np.array([g[1] for g in gv])
        # gamma_coll is a width: it cannot be negative, so a symmetric Wald
        # error bar that exceeds the point estimate (993.4154 nm at 70 C does,
        # 0.19 +/- 0.32) must not be drawn crossing zero -- clip the lower
        # whisker at the physical boundary instead of past it.
        lower = np.minimum(gerr, gval)
        ax.errorbar(N, gval, yerr=[lower, gerr], fmt="-o",
                    color=PEAK_COLOR[peak], alpha=0.30, ms=3, lw=0.9,
                    label=PEAK_LABEL[peak])
    mean_g = np.array([np.mean([gam(p, T)[0] for p in peaks]) for T in Ts])
    scat = np.array([np.std([gam(p, T)[0] for p in peaks], ddof=1) / 2.0 for T in Ts])
    ax.errorbar(N, mean_g, yerr=scat, fmt="-o", color="k", ms=6, lw=2.0, capsize=3,
                label="4-peak mean ± scatter/√4", zorder=5)
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
        ax.plot(Nf, mean_g[0] + bhead * (Nf - N[0]), "--", color="#D55E00", lw=1.6,
                label=r"if $\beta$=%.3f (joint, ×16 lever) were linear" % bhead)
        ax.plot(Nf, mean_g[0] + blever * (Nf - N[0]), ":", color="#0072B2", lw=1.8,
                label=r"if $\beta$=%.3f (joint, ×53 lever) were linear" % blever)
        yend = mean_g[0] + bhead * (N[-1] - N[0])
        ax.annotate(r"$\rightarrow$ %.1f MHz at 130 °C" % yend, xy=(N[-1], 1.08),
                    ha="right", fontsize=8, color="#D55E00")
    ax.set_xscale("log")
    ax.set_ylim(0.0, 1.15)
    ax.set_xlabel(r"Rb density $N$  ($10^{12}\,\mathrm{cm^{-3}}$, log)")
    ax.set_ylabel(r"fitted $\gamma_\mathrm{coll}$ (MHz, transition)")
    rise = mean_g[-1] / mean_g[0]
    lever = N[-1] / N[0]
    ax.set_title("The lever test: the fitted collisional width is a near-flat floor\n"
                 + (r"($\gamma$ rises ×%.1f while $N$ rises ×%.0f). " % (rise, lever))
                 + "A real binary-collision width is linear\n"
                 "in $N$, so β is quoted as a lever-dependent bound "
                 "(shown here per condition).\n"
                 "The pooled-width figure makes the same check without the split.",
                 fontsize=8)
    ax.legend(fontsize=7, loc="upper left", ncol=2)
    _footer(fig, "Source: results/linefit_conditions.csv, results/lever_crosscheck.csv. "
                 "Regenerate: python scripts/make_figures.py.")
    _save(fig, "fig6_gamma_floor.png")


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
            ax.plot([], [], ":", color="gray", label=r"transit$\to$0 wall (pinned beyond)")
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
                        label=("local covariance ellipse (68/95%)" if c == 2.30 else None))
            ax.set_title("zoom: profile contours (white)\nvs the local covariance ellipse (black)",
                         fontsize=9)
        else:
            ax.set_title("wide: the width-degeneracy topology\n"
                         r"(joint 68/95% contours in white; log$_{10}\Delta\chi^2$ fill)",
                         fontsize=9)
        ax.set_xlabel(r"$\gamma_\mathrm{coll}$ (MHz, transition)")
        if k == 0:
            ax.set_ylabel(r"$\sigma_\mathrm{laser}$ FWHM (MHz, transition)")
        cb = fig.colorbar(pc, ax=ax, shrink=0.9)
        cb.set_label(r"log$_{10}\,\Delta\chi^2$", fontsize=8)
        ax.legend(fontsize=7, loc="upper right")
    fig.suptitle("Profile likelihood of the width split (993.4192 nm, 130 °C / 225 mW; "
                 "transit + nuisances re-minimised per point)", fontsize=9)
    _footer(fig, "Source: results/identifiability_profile.csv (rb5s6s.identifiability). "
                 "Regenerate: python scripts/run_identifiability.py && "
                 "python scripts/make_figures.py.")
    _save(fig, "fig7_identifiability_profile.png")


def fig_ruler():
    """The built-in frequency ruler (M2, methods §3): a representative EOM
    ruler trace with its constrained seven-tooth comb fit — the same physical
    line excited via up to seven sideband pairs, teeth exactly 6.25 MHz apart
    on the laser axis (outer teeth weak: they need higher-order pairs; note
    the k=0 TOOTH is fed by (s+,s-) pairs as well as (c,c), so it can stand
    tall even with the optical carrier AM-suppressed -- the tooth pattern
    varies block to block with the 2025 HWP setting; methods section 3).
    RIGHT: the free-centres nonlinearity map (results/ruler_nlmap.csv) — the
    empirical bound (~0.3% per position) on scan nonlinearity AND any
    tooth-dependent pull (differential Stark, asymmetric-wing overlap), the
    ruler's common-mode-rejection check. Trace choice is deterministic: every
    canonical rf-on ruler is comb-fitted and the figure shows the one whose
    WEAKER outer tooth (k = +-3) stands tallest above that fit's residual
    noise, so the full seven-tooth structure is actually visible rather than
    buried (ties broken by path)."""
    from rb5s6s.ingest import load_manifest, load_trace, trace_path
    from rb5s6s.ruler import fit_comb, _comb, TEETH

    rows = sorted((r for r in load_manifest()
                   if r["role"].startswith("ruler") and r["flag"] == "canonical"
                   and r["rf_on"] == "True"),
                  key=lambda r: trace_path(r))
    if not rows:
        print("  (no ruler trace found -- skipping fig8)")
        return
    best = None
    for r in rows:
        tt, vv = load_trace(trace_path(r))
        ft = fit_comb(tt, vv)
        model = _comb(tt, ft["t0_ms"], ft["delta_ms"], ft["width_ms"],
                      ft["heights"], ft["b0"], ft["b1"])
        rms = float(np.std(vv - model))
        h = dict(zip(TEETH, ft["heights"]))
        score = min(h.get(3, 0.0), h.get(-3, 0.0)) / rms if rms > 0 else 0.0
        if best is None or score > best[0]:
            best = (score, tt, vv, ft)
    _, t, v, fit = best

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(9.8, 3.9),
                                  gridspec_kw={"width_ratios": [2.1, 1.0]})
    ax.plot(t, v, ".", ms=1.6, color="0.55", label="ruler trace (raw)")
    tf = np.linspace(t[0], t[-1], 3000)
    ax.plot(tf, _comb(tf, fit["t0_ms"], fit["delta_ms"], fit["width_ms"],
                      fit["heights"], fit["b0"], fit["b1"]),
            "-", color="#0072B2", lw=1.4,
            label=f"constrained {len(TEETH)}-tooth comb fit")
    ymax = max(fit["heights"]) + fit["b0"]
    ax.set_ylim(top=ymax * 1.22)
    for n in TEETH:
        tc = fit["t0_ms"] + n * fit["delta_ms"]
        ax.axvline(tc, color="#D55E00", lw=0.7, alpha=0.5)
        ax.annotate(f"$k={n}$", xy=(tc, ymax * 1.08), ha="center", fontsize=8,
                    color="#D55E00")
    ax.set_xlabel("scan time (ms)")
    ax.set_ylabel("fluorescence (V)")
    ax.set_title(f"the scan carries its own calibration: {len(TEETH)} copies of the same\n"
                 f"line, {TOOTH_SPACING_LASER_HZ / 1e6:.2f} MHz apart on the laser axis, "
                 "via EOM sideband pairs",
                 fontsize=9)
    ax.legend(fontsize=7, loc="lower left", framealpha=1.0, frameon=True)

    nl = _rows("ruler_nlmap")
    pos = np.array([float(r["pos_ms"]) for r in nl])
    rr = np.array([float(r["rate_rel"]) for r in nl])
    er = np.array([float(r["rate_rel_err"]) for r in nl])
    n_win = np.array([int(r["n"]) for r in nl])
    # Edge windows have few contributing traces, so their errors (~1/sqrt(n))
    # are LARGER THAN THE BOUND ITSELF -- the rightmost spans +/-0.74% against a
    # 0.3% band. Scaling marker area with n was not enough: a reader still
    # reads the long bar as an anomaly, or as contradicting the panel title.
    # So the two populations are now drawn differently and the title says which
    # one sets the bound. (The long bar is NOT anomalous: at n=5 it sits 0.9
    # sigma from the 1/sqrt(n) law, and its CENTRAL value, +0.24%, is inside
    # the band. Only its precision is poor.)
    well = n_win >= N_WELL_SAMPLED
    sizes = 12 + 38 * (n_win / n_win.max())
    for m, ec, alpha, z in ((well, "#009E73", 1.0, 2), (~well, "#8FBFB0", 0.9, 1)):
        ax2.errorbar(pos[m], rr[m], yerr=er[m], fmt="none", ecolor=ec,
                     elinewidth=1, capsize=2, alpha=alpha, zorder=z)
    ax2.scatter(pos[well], rr[well], s=sizes[well], color="#009E73",
                edgecolor="none", zorder=3,
                label=f"$n\\geq{N_WELL_SAMPLED}$ (sets the bound)")
    ax2.scatter(pos[~well], rr[~well], s=sizes[~well], facecolor="white",
                edgecolor="#009E73", linewidth=1.0, zorder=3,
                label=f"$n<{N_WELL_SAMPLED}$ (edge; error $>$ bound)")
    ax2.axhline(1.0, color="k", lw=0.8)
    ax2.axhspan(0.9955, 1.0045, color="#009E73", alpha=0.10)
    ax2.set_xlabel("window position (ms)")
    ax2.set_ylabel("local rate / block rate")
    ax2.set_title("sweep linearity + any tooth-dependent pull:\n"
                  r"$\lesssim$0.3% from the well-sampled windows", fontsize=9)
    # One cue, not two: the legend already carries the n split, and the old
    # free-floating "marker area ~ n" note collided with it.
    ax2.legend(fontsize=6, loc="lower left", framealpha=1.0, frameon=True)
    _footer(fig, "Source: data_raw archive (rb5s6s.ingest, rb5s6s.ruler; the plotted trace) + "
                 "results/ruler_nlmap.csv. Regenerate: python scripts/run_ruler.py && "
                 "python scripts/make_figures.py.")
    _save(fig, "fig8_ruler.png")


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
    ax1.set_xlabel(r"$\gamma_\mathrm{coll}$  (MHz, Lorentzian component)")
    ax1.set_ylabel(r"$\sigma_\mathrm{laser}$  (MHz, Gaussian component)")
    ax1.axhline(0.0, color="0.3", lw=0.8, ls=":")
    ax1.text(gg[-1], 0.02, "unphysical below", fontsize=6, color="0.3",
             ha="right", va="bottom")
    ax1.set_ylim(min(-0.25, ss[0]), ss[-1])
    ax1.set_title("the split: free along the contour\n"
                  f"median corr = {np.median(corr):+.2f}; several 1$\\sigma$ "
                  "ellipses reach unphysical widths", fontsize=9)
    ax1.legend(fontsize=7, framealpha=1.0, frameon=True)
    ax1.grid(alpha=0.25, lw=0.5)

    # --- RIGHT: the observable ------------------------------------------
    for pk in PEAK_COLOR:
        m = [i for i, p in enumerate(peaks) if p == pk]
        if not m:
            continue
        o = np.argsort(P[m])
        ax2.errorbar(P[m][o], tw[m][o], yerr=twe[m][o], marker="o", ms=4,
                     lw=1.0, capsize=2, color=PEAK_COLOR[pk], label=f"993.{pk} nm")
    ax2.set_xlabel("laser power (mW)")
    ax2.set_ylabel("total FWHM  (MHz, transition axis)")
    ax2.set_title("the observable: no power broadening, determined to "
                  f"{100 * np.median(twe) / np.median(tw):.1f}%", fontsize=9)
    ax2.legend(fontsize=7, framealpha=1.0, frameon=True)
    ax2.grid(alpha=0.25, lw=0.5)

    fig.suptitle("One temperature, 20 conditions: the total width is measured; "
                 "its decomposition is not", fontsize=10)
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
    ax.set_xlabel("session (hours run left to right within each)")
    ax.set_ylabel("offset within its display epoch (MHz, laser axis)")
    n_ep = len({r["_e"] for r in rows})
    ax.set_title(f"{len(rows)} traces in {n_ep} display epochs. Each segment is\n"
                 "referenced to itself. Gaps are knob moves, offset unknown across them.",
                 fontsize=8.5)
    ax.grid(alpha=0.25, lw=0.5)
    h = [plt.Line2D([], [], color=c, lw=2, label=f"993.{k} nm")
         for k, c in PEAK_COLOR.items()]
    ax.legend(handles=h, fontsize=7, frameon=True, framealpha=0.95, ncol=2,
              loc="lower left")

    # ---- panel 2: the QUIETEST well-sampled segment -------------------------
    # NOT the longest: the longest (75 min) is two bursts 75 min apart with
    # ~13 MHz of internal scatter, so a line through it measures a cavity
    # re-centring between the clusters, not a drift rate. Drawing it is what
    # exposed that. No epoch in the archive gives a long intervention-free
    # stretch, so the archive does NOT measure a drift rate; what it does
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
        ax.set_xlabel("minutes into the epoch")
        ax.set_ylabel("offset (MHz, laser axis)")
        ax.set_title(f"the quietest well-sampled epoch: 993.{pk} nm,\n"
                     f"{len(g)} traces over {dur:.1f} min held to "
                     f"{pp:.2f} MHz peak-to-peak", fontsize=8.5)
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
        ax.set_xlabel("|step| between consecutive traces, same epoch (MHz)")
        ax.set_ylabel("count (log)")
        ax.set_title(f"median {med:.2f} MHz with a tail to {s.max():.1f} MHz:\n"
                     "quiet drift, punctuated by cavity re-centrings", fontsize=8.5)
        ax.grid(alpha=0.25, lw=0.5, which="both")

    fig.suptitle("No wavemeter log survives: what the traces can and cannot say about "
                 "the laser's frequency", fontsize=10.5)
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
    for rr, lab, dx, dy in ((0.0, "axis: $s=-S_0$", 10, -12),
                            (1.18, "edge: $s\\to 0$", 10, 6)):
        ax[0].plot([rr], [np.exp(-2 * rr ** 2)], "o", color="#D55E00", ms=6)
        ax[0].annotate(lab, (rr, np.exp(-2 * rr ** 2)), fontsize=7,
                       textcoords="offset points", xytext=(dx, dy))
    ax[0].set_ylim(-0.03, 1.12)
    ax[0].set_xlabel("radius  $r/w$")
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
    ax[1].set_title("(b) many dim atoms, few bright\nones: $I^2$ wins",
                    fontsize=9)
    ax[1].legend(fontsize=7, framealpha=1.0, frameon=True)

    # (c) the triangle itself
    nu = np.arange(-1.6, 0.4, 0.002)
    ax[2].plot(nu, stark_ramp(nu, S0), color="#D55E00", lw=1.9)
    ax[2].axvline(-2 / 3 * S0, color="0.35", lw=1.0, ls=":")
    ax[2].annotate("mean $-\\frac{2}{3}S_0$", (-2 / 3 * S0, 2.28), fontsize=7,
                   ha="center", color="0.3")
    ax[2].set_ylim(0, 2.55)
    ax[2].set_xlabel("shift  $s/S_0$")
    ax[2].set_ylabel("density  $f(s)$")
    ax[2].set_title(r"(c) a triangle: $f(s)\propto|s|$" "\n"
                    r"skew $g_1=+0.566$, from $I^2$ alone", fontsize=9)

    # (d) what it does to the line
    g = np.arange(-14, 14, 0.01)
    sym = model_profile(g, gamma_coll=0.45, sigma_laser_fwhm=1.1,
                        transit_fwhm=1.9, s0=0.0)
    ramped = model_profile(g, gamma_coll=0.45, sigma_laser_fwhm=1.1,
                           transit_fwhm=1.9, s0=3.0)
    ax[3].plot(g, sym / sym.max(), color="0.5", lw=1.4, label="$S_0=0$")
    ax[3].plot(g, ramped / ramped.max(), color="#D55E00", lw=1.9,
               label="$S_0=3$ MHz")
    ax[3].set_xlabel("detuning (MHz)")
    ax[3].set_ylabel("normalised signal")
    ax[3].set_title("(d) the line it produces\n(exaggerated $S_0$ to show it)",
                    fontsize=9)
    ax[3].legend(fontsize=7, framealpha=1.0, frameon=True)

    for a in ax:
        a.grid(alpha=0.22, lw=0.5)
    fig.suptitle("The AC-Stark ramp: a focused beam gives a distribution of "
                 "light shifts, not one shift", fontsize=10)
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
    visibility and the panel says so. 795 nm is the detected cascade arm;
    780 nm is real but filtered out (~50 dB, docs/APPARATUS.md sec. 3).

    Right panels: the real cavity scan, digitised from a photograph
    (docs/apparatus/2025-06-12_cavity_scan_IMG_2508_digitised.csv). Only the
    UP-sweep is shown: the down-sweep's amplitudes are display-compressed in
    the photograph and would misrepresent the strengths, and the degeneracy
    plus abundance law is a statement about spike INTEGRALS, which is how
    the caption states it (the mirror-pair reading of the full record lives
    in APPARATUS section 6).
    """
    # E_5P12_CM/E_5P32_CM read from rb5s6s.polarizability -- the same NIST ASD
    # term energies that module's own 5S->5P matrix elements are keyed to,
    # rather than re-derived here from the D-line vacuum wavelengths
    # independently (the two used to agree only to ~0.01 nm by coincidence of
    # rounding, not by construction).
    from rb5s6s.polarizability import E_6S_CM, E_5P12_CM, E_5P32_CM
    LAM_6S_5P12_NM = 1.0e7 / (E_6S_CM - E_5P12_CM)   # 1324 nm, detected arm
    LAM_6S_5P32_NM = 1.0e7 / (E_6S_CM - E_5P32_CM)   # 1367 nm, rejected arm

    fig = plt.figure(figsize=(13.0, 6.2))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.45], wspace=0.06,
                          left=0.02, right=0.99, top=0.86, bottom=0.105)
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
    ax.text(0.23, y5s - 0.055, r"$5S_{1/2}$", ha="center", fontsize=11)
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
    ax.text(0.365, 0.86, f"{LAM_6S_5P12_NM:.0f} nm", rotation=-54,
            fontsize=7.5, color="0.45",
            ha="center", va="center")
    ax.annotate("", (0.66, y5p32 + 0.008), (0.335, y6s - 0.008),
                arrowprops=dict(arrowstyle="-|>", color="0.5", lw=1.3,
                                 ls=(0, (4, 3))))
    ax.text(0.50, 0.885, f"{LAM_6S_5P32_NM:.0f} nm", rotation=-44,
            fontsize=7.5, color="0.45",
            ha="center", va="center")
    # cascade, second legs: 795 detected (red), 780 filtered out (grey)
    ax.annotate("", (0.295, y5s + 0.008), (0.545, y5p12 - 0.008),
                arrowprops=dict(arrowstyle="-|>", color="#d62728", lw=2.2))
    ax.text(0.365, 0.295, "795 nm", rotation=64, fontsize=9, color="#d62728",
            ha="center", va="center", fontweight="bold")
    ax.annotate("", (0.335, y5s + 0.008), (0.625, y5p32 - 0.008),
                arrowprops=dict(arrowstyle="-|>", color="0.55", lw=1.4))
    ax.text(0.545, 0.275, "780 nm", rotation=62, fontsize=7.5, color="0.45",
            ha="center", va="center")
    ax.text(0.45, -0.12, "795 nm detected, 780 nm filtered out (~50 dB) · "
            "5P splitting not to scale", fontsize=7.5,
            color="0.45", ha="center")

    # --- right: the scan as photographed, annotated -------------------
    # The photograph IS the record (2025-06-12 scope screen). The digitised
    # CSV stays committed as the quantitative backing for the integral
    # statement; it is cited in the footer, not drawn, because the
    # digitisation undersamples the peaks and misstates their heights.
    # The bench photographs travel with the archive, not the public
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
    bx.imshow(photo[182:2495, 364:4020])
    bx.axis("off")
    bx.set_title("the cavity scan, as photographed (500 ms/div)",
                 fontsize=10)
    fx = [pe.withStroke(linewidth=2.2, foreground="black")]

    def lab(x, y, s, **kw):
        kw.setdefault("ha", "center")
        bx.text(x, y, s, transform=bx.transAxes, fontsize=8.5,
                color="white", path_effects=fx, **kw)

    lab(0.042, 0.500, "⁸⁷Rb\nF=2", va="bottom")
    lab(0.140, 0.868, "⁸⁵Rb F=3", va="bottom", ha="left")
    lab(0.315, 0.690, "⁸⁵Rb F=2", va="bottom")
    lab(0.478, 0.360, "⁸⁷Rb F=1", va="bottom")
    lab(0.545, 0.870, "ramp apex", va="bottom", ha="left")
    lab(0.185, 0.560, "cavity-scan ramp", ha="left")
    lab(0.560, 0.075, "795 nm fluorescence", ha="left")
    lab(0.760, 0.300, "down-sweep:\nthe same four,\nmirrored", va="center")

    fig.text(0.63, 0.045,
             "spike integrals follow (2F+1) × abundance: ⁸⁵ ratio 1.31, "
             "predicted 1.40 (from the digitised record)",
             ha="center", fontsize=8.5, color="0.25")
    fig.suptitle(
        r"The 993 nm two-photon line: excitation, detection, and the scan "
        "across it", fontsize=12.5, y=0.965)
    _footer(fig, "Sources: rb5s6s.constants + polarizability (level scheme); "
                 "photograph docs/reference_setup/photos/IMG_2508.jpeg (scope "
                 "screen, 2025-06-12, cropped); integrals from the digitised "
                 "record docs/apparatus/2025-06-12_cavity_scan_IMG_2508_digitised.csv. "
                 "Regenerate: python scripts/make_figures.py.")
    _save(fig, "fig13_level_scheme.png")



def fig_wavemeter_reconstruction():
    """The wavemeter record, its model, and the same quantity from our traces (M22).

    The result is the settled floor on unmodelled laser motion. The relaxation
    time constants are not constrained by this record and are not shown as
    though they were.
    """
    import collections
    import csv

    import matplotlib.image as mpimg
    sys.path.insert(0, str(C.REPO_ROOT / "scripts"))
    from run_wavemeter_reconstruction import reconstruct, PHOTO
    r = reconstruct()
    t, f, band = r["t"], r["f"], r["band"]
    tf, mu, sg = r["t_fit"], r["mu"], r["sigma"]

    fig = plt.figure(figsize=(7.6, 8.4))
    gs = fig.add_gridspec(3, 1, height_ratios=[1.35, 2.0, 1.5], hspace=0.34)

    ax0 = fig.add_subplot(gs[0])
    ax0.imshow(mpimg.imread(str(PHOTO)))
    ax0.set_axis_off()
    ax0.set_title("(a) as photographed: 2025-06-11, a preliminary session five "
                  "weeks before the campaign", fontsize=8.5)

    ax1 = fig.add_subplot(gs[1])
    ax1.fill_between(t, f - band/2, f + band/2, color="#0072B2", alpha=0.15, lw=0,
                     label=f"scan band, {r['band_mhz']:.0f} MHz")
    ax1.plot(t, f, color="#0072B2", lw=0.7, label="digitised band centre")
    ax1.plot(tf, mu, color="#D55E00", lw=1.8,
             label=f"{r['n_kicks']} re-locks, each relaxing back")
    for k, tk in enumerate(r["kick_times"]):
        ax1.axvline(tk, color="#D55E00", lw=0.8, ls=":", alpha=0.55)
    ax1.set_ylabel("frequency  (MHz)")
    ax1.legend(loc="lower right", fontsize=7.5, frameon=True, framealpha=0.9)
    ax1.set_title("(b) the record is re-locks and relaxation, not drift", fontsize=8.5)

    ax2 = fig.add_subplot(gs[2])
    ax2.fill_between(tf, -sg, sg, color="#D55E00", alpha=0.18, lw=0,
                     label=f"fitted noise, settling to {r['sigma_inf']:.2f} MHz")
    ax2.plot(tf, f[::3] - mu, color="#666666", lw=0.6, label="residual")
    rows = [x for x in csv.DictReader(open(C.REPO_ROOT / "results" / "laser_history.csv"))
            if x["flag"] == "canonical" and x["offset_mhz"] not in ("", "nan")]
    ep = collections.defaultdict(list)
    for x in rows:
        ep[x["display_epoch"]].append((int(x["t_epoch"]), float(x["offset_mhz"])))
    best = sorted(max(ep.values(), key=lambda v: max(a for a, _ in v) - min(a for a, _ in v)))
    tt = np.array([(a - best[0][0]) / 60 for a, _ in best])
    oo = np.array([b for _, b in best]); oo -= oo.mean()
    # markers only: the archive samples in bursts, not continuously
    ax2.plot(tt, oo, "o", color="#009E73", ms=5,
             label=f"our traces, same quantity, sd {oo.std():.1f} MHz")
    ax2.axhline(0, color="k", lw=0.5)
    ax2.set_xlabel("time  (min)")
    ax2.set_ylabel("frequency  (MHz)")
    ax2.legend(loc="upper right", fontsize=7.5, frameon=True, framealpha=0.9)
    ax2.set_ylim(-9, 12)          # the first seconds spike off-scale; the
                                  # settled region is the point of this panel
    ax2.set_title("(c) what is left: the noise settles, and the floor is what "
                  "a measurement must beat  (axis clipped)", fontsize=8.5)
    _footer(fig, "Source: scripts/run_wavemeter_reconstruction.py (reconstruct(); the "
                 "photographed record) + results/laser_history.csv\n"
                 "(panel c overlay). Regenerate: python scripts/make_figures.py.",
            fontsize=5.9)
    _save(fig, "fig14_wavemeter_reconstruction.png")




def fig_drift_story():
    """The drift problem, what the archive extracted despite it, and what a
    fixed lock buys (fig15). Three panels.

    (a) The problem, photographed: the 2025-06-11 wavemeter record, digitised
        by M22 -- re-lock kicks and relaxations on a drifting cavity lock.
        Not campaign data; the campaign saved no wavemeter log at all, which
        is the point of panel (b).
    (b) The campaign, reconstructed from its own traces (M20): line offsets
        within each scope-knob epoch. Absolute frequency is unknowable across
        epoch boundaries (the knob moved 58 times), so each segment floats;
        within a segment the excursion is ~1 MHz and the held-lock drift is
        +0.016 [0.007, 0.025] MHz/min (state-space fit on the recovered
        clock, audit addendum 5; band shown).
    (c) The consequence ladder: what each drift regime licenses, with the
        archive's extracted bounds and the fixed-lock conversions annotated.
        The fixed-lock benchmark is Ayachitula 2024 on this same transition:
        < 0.5 kHz over 50 min.
    """
    import csv as _csv

    sys.path.insert(0, str(C.REPO_ROOT / "scripts"))
    from run_wavemeter_reconstruction import reconstruct
    r = reconstruct()
    t, f, band = r["t"], r["f"], r["band"]
    tf, mu = r["t_fit"], r["mu"]

    # campaign side: within-epoch offsets from the committed laser history
    rows = [x for x in _csv.DictReader(open(C.RESULTS_DIR / "laser_history.csv"))
            if x["flag"] == "canonical" and x["offset_mhz"]]
    t0 = min(float(x["t_epoch"]) for x in rows)

    # Each row IS a recorded trace: a 2000-point, fixed-duration Agilent scan
    # (module M0/ingest.py), so its clock time carries a real scan span, not
    # just a fitted centre. duration x the trace's own session rate
    # (results/ruler_blocks.csv, before/after brackets averaged for the P
    # sessions) is that span; falls back to the campaign-wide rate only if a
    # (session, peak, T) combination is somehow absent from ruler_blocks.
    trace_duration_ms = TRACE_N_POINTS * TRACE_DT_S * 1e3   # 1000 ms, fixed format
    rate_sum, rate_n = defaultdict(float), defaultdict(int)
    for rb in _csv.DictReader(open(C.RESULTS_DIR / "ruler_blocks.csv")):
        key = (rb["session"], rb["peak"], rb["T"])
        rate_sum[key] += float(rb["rate"])
        rate_n[key] += 1
    rate_by_key = {k: rate_sum[k] / rate_n[k] for k in rate_sum}
    campaign_rate = float(next(iter(
        _csv.DictReader(open(C.RESULTS_DIR / "ruler_campaign.csv"))))["rate_laser"])

    def _span_mhz(x):
        session = "P" if x["role"] in ("p_sweep", "ruler_p") else "T"
        rate = rate_by_key.get((session, x["peak"], x["temperature_C"]), campaign_rate)
        return trace_duration_ms * rate

    by_ep = {}
    for x in rows:
        by_ep.setdefault(int(x["display_epoch"]), []).append(
            ((float(x["t_epoch"]) - t0) / 3600.0, float(x["offset_mhz"]), _span_mhz(x)))

    # the extracted-vs-gain numbers, read from the committed CSVs
    s0 = float(next(x["value"] for x in _csv.DictReader(open(C.RESULTS_DIR / "stark_joint.csv"))
                    if x["quantity"] == "S0_225mW_ub95"))
    bvals = [float(x["bound95_nscale"]) for x in _csv.DictReader(open(C.RESULTS_DIR / "beta_self_probe.csv"))
             if x.get("headline") == "yes"]
    sl = float(next(x["value_MHz"].lstrip("<") for x in _csv.DictReader(open(C.RESULTS_DIR / "laser_epoch.csv"))
                    if x["quantity"] == "sigma_laser_bound"))

    fig = plt.figure(figsize=(8.6, 9.2))
    gs = fig.add_gridspec(3, 1, height_ratios=[1.6, 1.6, 1.15], hspace=0.42)

    # (a) the photographed record, digitised
    ax = fig.add_subplot(gs[0])
    ax.fill_between(t, f - band / 2, f + band / 2, color="#0072B2", alpha=0.25,
                    lw=0, label="scan band (the sweep, not noise)")
    ax.plot(t, f, color="#0072B2", lw=0.9, label="band centre = laser frequency")
    mclip = tf > 0.4     # the pre-first-kick baseline is a fit artifact
    ax.plot(tf[mclip], mu[mclip], color="#D55E00", lw=1.6, ls="--",
            label="fitted model: re-lock kicks + relaxations")
    for tk in r["kick_times"]:
        ax.axvline(tk, color="0.55", lw=0.7, alpha=0.6)
    ax.set_xlabel("time (min)")
    ax.set_ylabel("laser detuning (MHz)")
    ax.set_title("(a) the problem, photographed: wavemeter record, 2025-06-11 "
                 "preliminary session (no log survives from the campaign itself)",
                 fontsize=9)
    ax.legend(fontsize=7, loc="lower right", framealpha=1.0, frameon=True)

    # (b) the campaign, reconstructed from its own traces
    ax = fig.add_subplot(gs[1])
    drift = 0.016   # MHz/min, laser; audit addendum 5 (state-space, recovered clock)
    dlo, dhi = 0.007, 0.025
    first = True
    first_band = True
    for ep, pts in sorted(by_ep.items()):
        if len(pts) < 2:
            continue
        pts.sort()
        th = [p[0] for p in pts]
        off = [p[1] for p in pts]
        span = [p[2] for p in pts]
        # texture, not decoration: each segment is one recorded trace's own
        # piezo scan ramp (duration x that session's ruler rate), centred on
        # its fitted centre -- the like-for-like counterpart of panel (a)'s
        # photographed scan band, drawn low-alpha so the smooth centre
        # line/points (plotted next, on top) stay legible.
        lbl = None
        if first_band:
            lbl = f"each trace's own scan ramp (~{span[0]:.0f} MHz)"
        ax.vlines(th, [o - s / 2 for o, s in zip(off, span)],
                  [o + s / 2 for o, s in zip(off, span)],
                  color="#009E73", lw=0.7, alpha=0.10, zorder=1, label=lbl)
        first_band = False
        ax.plot(th, off, "-", color="#009E73", lw=0.8, alpha=0.85, zorder=2)
        ax.plot(th, off, ".", color="#009E73", ms=2.5, zorder=3,
                label="line offset within one knob epoch" if first else None)
        first = False
    # A slope INDICATOR over 3 h, not a fit across the record: the absolute
    # trend across epochs is exactly what the knob moves make unknowable.
    ts0, y0 = 9.0, -9.5
    tind = np.linspace(ts0, ts0 + 3.0, 20)
    ax.plot(tind, y0 + (tind - ts0) * 60 * drift, color="#D55E00", lw=1.8,
            ls="--", label="held-lock drift, magnitude 0.016 MHz/min "
                           "(sign not established)")
    ax.fill_between(tind, y0 + (tind - ts0) * 60 * dlo,
                    y0 + (tind - ts0) * 60 * dhi,
                    color="#D55E00", alpha=0.25, lw=0)
    ax.annotate("what the held lock does in 3 h", xy=(ts0 + 1.5, y0 + 3.2),
                ha="center", fontsize=7.5, color="#D55E00")
    ax.set_xlabel("time into campaign (h)")
    ax.set_ylabel("offset (MHz, laser)")
    ax.set_title("(b) the campaign, reconstructed from its own traces: "
                 "segments float (58 knob moves re-zero the axis); shapes survive",
                 fontsize=9)
    ax.legend(fontsize=7, loc="upper right", framealpha=1.0, frameon=True)

    # (c) the consequence ladder
    ax = fig.add_subplot(gs[2])
    envelope_mhz_per_min = DRIFT_RATE_LASER_HZ_PER_MIN / 1e6  # rb5s6s.constants ENVELOPE
    ayachitula_mhz_per_min = 0.5e-3 / 50.0  # <0.5 kHz / 50 min (Ayachitula et al. 2024)
    regimes = [
        (envelope_mhz_per_min, "planning envelope (2025)", "everything below is usable"),
        (drift, "2025 held lock, bounded", "shapes only: bounds\n"
         f"$S_0<{s0:.2f}$ MHz, $\\sigma_\\mathrm{{laser}}<{sl:.1f}$ MHz\n"
         f"$\\beta$ {min(bvals):.2f}-{max(bvals):.2f} MHz per $10^{{12}}$ cm$^{{-3}}$"),
        (ayachitula_mhz_per_min,
         "fixed lock, demonstrated on this line\n(Ayachitula 2024: <0.5 kHz / 50 min)",
         "centres usable: measure the pull ($\\propto S_0$),\n"
         "the self-shift, and $\\beta$ at 3-12$\\sigma$"),
    ]
    ys = [2, 1, 0]
    for y, (rate, left, right) in zip(ys, regimes):
        ax.plot([rate], [y], "o", ms=9, color="#0072B2")
        ax.annotate(left, xy=(rate, y), xytext=(0, 12), textcoords="offset points",
                    ha="center", fontsize=7.5)
        ax.annotate(right.replace("\\n", "\n"), xy=(rate, y), xytext=(0, -13),
                    textcoords="offset points", ha="center", va="top", fontsize=7.5)
    ax.set_xscale("log")
    ax.set_xlim(3e-6, 30)
    ax.set_ylim(-1.4, 3.1)
    ax.set_yticks([])
    ax.set_xlabel("laser drift rate (MHz/min, laser axis)")
    ax.set_title("(c) what each regime licenses: the archive's bounds, and the "
                 "session's conversions", fontsize=9)
    ax.grid(axis="y", visible=False)
    _footer(fig, "Source: scripts/run_wavemeter_reconstruction.py (panel a) + "
                 "results/laser_history.csv, results/ruler_blocks.csv,\n"
                 "results/ruler_campaign.csv (panel b) + results/stark_joint.csv, "
                 "results/beta_self_probe.csv, results/laser_epoch.csv (panel c). "
                 "Regenerate: python scripts/make_figures.py.", fontsize=5.9)
    _save(fig, "fig15_drift_story.png")


def _gallery_context():
    """Shared M25 single-trace context for fig16 and fig18: the committed
    global-archive-fit shared optimum, plus the brightest 225 mW / 130 C
    campaign repeat per peak. Returns None (after printing why) if a required
    input is missing, so callers degrade the same way fig7/10/11 do.

    Refactored out of fig_fit_gallery (2026-08) so fig18 (fig_single_peak_fits)
    computes identical numbers from one code path -- no duplicated fit logic.
    """
    fp = C.RESULTS_DIR / "global_archive_fit.csv"
    if not fp.exists():
        print("  (global_archive_fit.csv absent -- skipping the fit-gallery figures)")
        return None
    if not (C.DATA_RAW_DIR / "MANIFEST.csv").exists():
        print("  (data_raw/MANIFEST.csv absent -- skipping the fit-gallery figures)")
        return None

    rows = _rows("global_archive_fit")

    def val(q, k="primary"):
        return float(next(r["value"] for r in rows if r["quantity"] == q and r["key"] == k))

    status = next(r["status"] for r in rows if r["quantity"] == "beta_self_joint")
    kappa = val("kappa_min")
    beta = val("beta_self_joint")
    sl_blocks = {r["key"]: float(r["value"]) for r in rows if r["quantity"] == "sigma_laser"}

    sys.path.insert(0, str(C.REPO_ROOT / "scripts"))
    try:
        from run_global_archive_fit import DNU_FLOOR, load_campaign_all
        from rb5s6s.linefit import _shared_profile_grid, transit_fwhm_at_T
        traces = load_campaign_all()
    except Exception as e:  # missing/changed raw archive: degrade like fig7/10/11
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

    return {"status": status, "kappa": kappa, "beta": beta, "sl_blocks": sl_blocks,
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
    chi2_red = chi2 / dof

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

    return {"t": t, "T": T, "P": P, "gc": gc, "sl": sl, "transit": transit, "s0": s0,
           "g": g, "prof": prof, "x": x, "v": v, "sg": sg, "xf": xf,
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
        return f"  saturation: {pct:.1f} ± {pct_err:.1f}% compression at peak signal"
    vsat_lb95 = 1.0 / (c_hat + z95 * sigma_c)  # one-sided 95% lower bound on Vsat
    return f"  detector response: linear (saturation scale > {vsat_lb95:.0f} V, 95%)"


def fig_fit_gallery():
    """M25 fit-quality gallery: data, model overlay and residuals, per peak.

    Picks the single highest-SNR campaign trace per peak (the 225 mW, 130 C
    p_sweep condition, the brightest combination of power and temperature the
    campaign ran, per fig2's P^2 amplitude law, taking the largest-amplitude
    repeat of the five) and overlays the M25 global archive model at the
    COMMITTED shared optimum read from results/global_archive_fit.csv:
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
    outer = fig.add_gridspec(2, 2, hspace=0.34, wspace=0.24, top=0.83, bottom=0.06,
                             left=0.06, right=0.98)
    slot = {"4121": (0, 0), "4154": (0, 1), "4192": (1, 0), "4207": (1, 1)}

    for peak in peaks:
        fr = _fit_trace_nuisances(ctx, peak)
        r0, c0 = slot[peak]
        inner = outer[r0, c0].subgridspec(2, 1, height_ratios=[3.0, 1.1], hspace=0.08)
        ax_main = fig.add_subplot(inner[0])
        ax_res = fig.add_subplot(inner[1], sharex=ax_main)

        x, v, cc = fr["x"], fr["v"], fr["cc"]
        xf, sol, model_at = fr["xf"], fr["sol"], fr["model_at"]
        fwhm, chi2_red = fr["fwhm"], fr["chi2_red"]

        # ---- main panel: data + model, centred on the fitted line centre ----
        xd = x - cc
        ax_main.plot(xd, v, ".", ms=2.2, color="0.4", alpha=0.5, label="data")
        ax_main.plot(xf - cc, model_at(sol.x, xf), "-", color=PEAK_COLOR[peak], lw=1.7,
                     label="joint fit of all campaign traces")
        ax_main.set_ylabel("signal (V)")
        ax_main.set_title(f"{PEAK_LABEL[peak]}, 225 mW / 130 °C power sweep, "
                           f"brightest repeat\nFWHM {fwhm:.3f} MHz, "
                           r"$\chi^2_\nu$" + f" = {chi2_red:.2f} (n={len(x)})",
                           fontsize=8.5)
        ax_main.legend(fontsize=7, loc="upper right", frameon=True, framealpha=0.9)
        ax_main.tick_params(labelbottom=False)

        # ---- residual panel ----
        res_v = v - model_at(sol.x, x)
        ax_res.plot(xd, res_v, ".", ms=2.0, color=PEAK_COLOR[peak], alpha=0.6)
        ax_res.axhline(0.0, color="k", lw=0.7)
        rmax = float(np.max(np.abs(res_v))) * 1.15 if len(res_v) else 1.0
        ax_res.set_ylim(-rmax, rmax)
        ax_res.set_xlabel("detuning from fitted centre (MHz, transition axis)")
        ax_res.set_ylabel("resid (V)", fontsize=8)

    fig.suptitle(
        "Fit-quality gallery: one joint fit of all campaign traces, drawn against one "
        f"representative trace per peak ({STATUS_WORD.get(status, status.lower())})\n"
        "The collisional width, laser linewidth, Stark coefficient and transit width are "
        "shared across every trace and held fixed here (the fitted Stark\n"
        "coefficient sits at zero, so no Stark broadening is drawn). Each trace's own "
        "amplitude, centre, and background are refit individually. The joint fit is "
        "not re-run.\n"
        "Residuals: the antisymmetric near-centre structure falls with amplitude as "
        "expected for shot noise (not a lineshape asymmetry).\n"
        "A small symmetric excess at line centre on the brightest traces (up to 1.4% of "
        "peak on 993.4192 nm, below the noise level) remains unexplained and does "
        "not change any reported value.",
        fontsize=9.0, y=0.995)
    _footer(fig, "Source: results/global_archive_fit.csv (shared parameters) + the "
                 "data_raw archive (per-trace data; local refit only). "
                 "Regenerate: python scripts/run_global_archive_fit.py && "
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
        ax_main.plot(xd, v, ".", ms=3.0, color="0.4", alpha=0.5, label="data")
        ax_main.plot(xf - cc, model_at(sol.x, xf), "-", color=PEAK_COLOR[peak], lw=2.0,
                     label="joint fit of all campaign traces")
        ax_main.set_ylabel("signal (V)")
        ax_main.set_title(f"{PEAK_LABEL[peak]}: data vs the joint fit\n"
                          "225 mW / 130 °C power sweep, brightest repeat", fontsize=10)
        ax_main.legend(fontsize=8, loc="upper right", frameon=True, framealpha=0.9)
        ax_main.tick_params(labelbottom=False)

        # ---- residual panel ----
        res_v = v - model_at(sol.x, x)
        ax_res.plot(xd, res_v, ".", ms=2.6, color=PEAK_COLOR[peak], alpha=0.6)
        ax_res.axhline(0.0, color="k", lw=0.7)
        rmax = float(np.max(np.abs(res_v))) * 1.15 if len(res_v) else 1.0
        ax_res.set_ylim(-rmax, rmax)
        ax_res.set_xlabel("detuning from fitted centre (MHz, transition axis)")
        ax_res.set_ylabel("resid (V)", fontsize=8.5)

        # ---- the parameter box: every number labelled by what it comes from ----
        N_here = float(density_units(fr["T"]))
        lines = [
            f"993.{peak} nm: 225 mW, 130 °C",
            "-" * 40,
            "Shared across every campaign trace (held fixed here):",
            f"  laser linewidth $\\sigma_L$ = {fr['sl']:.3f} MHz",
            "    (shared within this session/temperature block;",
            "    uncertainty not separately quoted)",
            f"  collisional width $\\gamma_c$ = {fr['gc']:.3f} MHz",
            "    = self-broadening rate x density",
            f"    = {ctx['beta']:.4f} x {N_here:.2f} "
            r"($10^{12}\,\mathrm{cm^{-3}}$)",
            "    (uncertainty not separately quoted)",
            f"  Stark coefficient $\\kappa$ = {ctx['kappa']:.3f} MHz/W",
            f"    -> light shift $S_0=\\kappa P$ = {fr['s0']:.3f} MHz",
            f"  transit width = {fr['transit']:.3f} MHz",
            "    (fixed prior; beam waist not yet measured)",
            "-" * 40,
            "From the fit above:",
            f"  FWHM (model) = {fr['fwhm']:.3f} MHz",
            f"  reduced $\\chi^2$ = {fr['chi2_red']:.2f}  (n={len(x)})",
            "-" * 40,
            "This trace only (refit individually):",
            f"  amplitude = {fr['A']:.4f} ± {fr['A_err']:.4f} V",
            f"  centre = {fr['cc']:.3f} ± {fr['cc_err']:.3f} MHz",
            f"  background level = {fr['b0']:.4f} ± {fr['b0_err']:.4f} V",
            f"  background slope = {fr['b1']:.5f} ± {fr['b1_err']:.5f} V/MHz",
            _saturation_display(fr),
        ]
        ax_box.text(0.02, 0.98, "\n".join(lines), transform=ax_box.transAxes,
                    fontsize=7.0, va="top", ha="left", family="monospace", linespacing=1.35,
                    bbox=dict(boxstyle="round,pad=0.5", facecolor="0.97",
                             edgecolor="0.6", lw=0.8))

        fig.suptitle(
            "A two-photon Doppler-free line: a Lorentzian core (natural + "
            "collisional) convolved with a Gaussian laser/transit\n"
            "envelope, saturating at high power. Instance: 993." + peak + " nm at the "
            "values shared across the whole campaign fit;\n"
            "this trace's own amplitude, centre and background are refit "
            "individually here, without re-running that shared fit.",
            fontsize=9.2, y=0.995)
        _footer(fig, "Source: results/global_archive_fit.csv (shared parameters, "
                     f"{STATUS_WORD.get(status, status.lower())}) + the data_raw archive "
                     "(this trace; refit individually). Regenerate: "
                     "python scripts/run_global_archive_fit.py && "
                     "python scripts/make_figures.py.", y=0.015)
        _save(fig, f"fig18_single_{peak}.png")


def fig_width_trends():
    """M4 / M4e physics-trend panels (fig19): the two width-broadening laws
    the archive tests, side by side.

    GENERIC LAW, panel 1: pressure (collisional) broadening adds width
    linearly in the perturber density, W = floor + beta*N -- measured here
    as a SLOPE, because per-condition widths carry a common floor (fig6:
    fig_gamma_floor shows the free per-condition gamma_coll is a near-flat
    FLOOR, degenerate with sigma_laser at corr ~ -0.85 to -0.9, that does
    not resolve collisions point-by-point). RB INSTANCE: this panel does
    NOT plot that free-fit gamma_coll against an unrelated line -- the two
    constructions are not comparable (RESULTS_C-chain, docs/RESULTS.md
    C1). It instead reproduces the archive's own HEADLINE beta_self
    estimator verbatim: the model-independent P0 confound probe in
    scripts/run_beta_self.py (collisional_slope, results/beta_self_probe.csv),
    which fits RAW contiguous FWHM (no lineshape split) vs N over the
    70-110 C cooling sweep as W(N) = floor + beta_eff*N, then inflates the
    slope error by the between-block scatter (the same floor fig6 shows)
    via a Student-t 95% bound -- why beta_self is reported as a BOUND, not
    a measurement (SNR<3, all four peaks). The fitted line and its
    systematic-error band therefore pass through the data BY CONSTRUCTION:
    this is the actual fit the bound comes from, drawn only over its own
    70-110 C fit domain (no out-of-domain extrapolation). The 130 C point is
    NOT folded into this fit: it ran in the SAME optical/cell configuration,
    but as its own SESSION (a different day and display epoch, calibrated
    against its own before/after EOM-ruler brackets rather than the
    t_sweep's per-block ruler) -- a cross-session comparability question, not
    a different apparatus configuration. run_beta_self.py keeps it available
    only as an optional fourth lever point in a separate, non-headline probe
    (dof=2, headline=no in results/beta_self_probe.csv), matching this panel.

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
    a value -- drawn as a one-sided shaded EXCLUSION, never an error bar.
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

    from rb5s6s.stark import _fwhm_of
    from rb5s6s.linefit import transit_fwhm_at_T
    from rb5s6s.beta import collisional_slope
    from rb5s6s.ingest import load_manifest

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
    T_grid = np.linspace(55.0, 140.0, 4000)
    N_grid = density_units(T_grid)

    def N_to_T(N):
        return np.interp(N, N_grid, T_grid)

    def T_to_N(T):
        # matplotlib probes the secondary axis's own default view (e.g. the
        # [0, 1] Axes default) while wiring up the scale, before any real
        # limits are set -- clip into the liquid-phase-valid band so that
        # probe never hits density_units' melting-point guard.
        Tc = np.clip(np.asarray(T, float), 55.0, 140.0)
        return density_units(Tc)

    manifest_rows = load_manifest()
    trates, _prates = _rbp.load_t_rates()
    ymin_p1, ymax_p1 = 1e9, 0.0
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
        A = np.vstack([np.ones_like(N), N]).T
        Winv = np.diag(1.0 / E ** 2)
        floor, slope = np.linalg.solve(A.T @ Winv @ A, A.T @ Winv @ W)
        Esys = np.sqrt(E ** 2 + cs["resid_rms"] ** 2)

        ax1.errorbar(N, W, yerr=Esys, fmt="o", color=PEAK_COLOR[peak], ms=5.5, lw=1.4,
                     capsize=2, label=PEAK_LABEL[peak], zorder=4)
        Nfit = np.linspace(N.min(), N.max(), 60)
        line = floor + slope * Nfit
        band = cs["syst_err"] * (Nfit - N[0])  # zero at the anchor point, by construction
        ax1.plot(Nfit, line, "-", color=PEAK_COLOR[peak], lw=1.1, alpha=0.85, zorder=2)
        ax1.fill_between(Nfit, line - band, line + band, color=PEAK_COLOR[peak],
                         alpha=0.14, lw=0, zorder=1)
        ymin_p1 = min(ymin_p1, float(np.min(W - Esys)), float(np.min(line - band)))
        ymax_p1 = max(ymax_p1, float(np.max(W + Esys)), float(np.max(line + band)))

    pad1 = 0.08 * (ymax_p1 - ymin_p1)
    ax1.set_ylim(ymin_p1 - pad1, ymax_p1 + pad1)
    ax1.set_xscale("log")
    ax1.set_xlabel(r"Rb density $N$  ($10^{12}\,\mathrm{cm^{-3}}$, log)")
    ax1.set_ylabel("raw FWHM (MHz, transition; model-independent)")
    ax1.set_title("Floor + slope fit to the raw linewidth vs density: 3 temperature "
                 "points per peak (dof=1).\n"
                 "The line and band ARE the fit the bound is built from, not a denser "
                 "measurement.\n"
                 r"slope = $\beta_\mathrm{self}$, a bound not a measurement "
                 "(signal-to-noise $<$3, all four peaks)",
                 fontsize=8.2)
    # Compact honesty note (private/reviews/digest/fig19_trend_audit.md): the bars on
    # this panel are the repeat + between-block scatter that FEEDS the reported 95%
    # bound, not the bound itself (a further one-sided Student-t inflation, dof=1);
    # and the lowest-density point carries a documented, quantified low-SNR narrowing
    # bias (run_beta_self.py's own raw_fwhm_mhz) that -- because it narrows the anchor
    # point -- steepens the fitted slope, so it can only make the bound conservative,
    # never understate it. Placed top-left, the one corner both the data (which rise
    # in scatter toward low N) and the lower-right legend leave clear.
    ax1.text(0.02, 0.97,
             "bars: repeat + between-block scatter, not the reported 95% bound\n"
             "(a further $\\times$6.3 Student-t inflation, dof=1); ~6% low-SNR\n"
             "narrowing at 70 °C (3 of 4 peaks) makes the bound conservative",
             transform=ax1.transAxes, ha="left", va="top", fontsize=6.3, color="0.3",
             bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="0.7", lw=0.5))
    # lower right: the fit lines rise with N, and the low-N data (left) carry
    # the largest error bars, so the low-W / high-N corner stays clear
    ax1.legend(fontsize=6.6, loc="lower right", ncol=1, framealpha=0.95, frameon=True)
    sec = ax1.secondary_xaxis("top", functions=(N_to_T, T_to_N))
    sec.set_xlabel("temperature (°C)", fontsize=8.5)
    sec.tick_params(labelsize=7.5)

    # ================= panel 2: FWHM vs power, Stark exclusion wedge =======
    pw_rows = _rows("power_sweep")
    stark_rows = _rows("stark_sweep")
    kappa_ub = float(next(r["value"] for r in stark_rows
                          if r["quantity"] == "kappa_ub95_profile"))
    chi2_red_stark = float(next(r["value"] for r in stark_rows if r["quantity"] == "chi2_red"))
    core = {r["key"]: float(r["value"]) for r in stark_rows if r["quantity"] == "core_sigma_laser"}
    transit130 = transit_fwhm_at_T(130.0, C.TRANSIT_FWHM_PLACEHOLDER_MHZ)
    nu = np.arange(-45.0, 45.0, 0.02)
    Pgrid_W = np.linspace(0.0, 0.26, 60)
    core_mean = float(np.mean(list(core.values()))) if core else 1.6

    growth225, spreads, ymax_panel, ymin_panel = [], [], 0.0, 1e9
    for peak in ("4121", "4154", "4192", "4207"):
        d = sorted((int(r["power_mW"]), float(r["fwhm"]), float(r["fwhm_err"]))
                  for r in pw_rows if r["peak"] == peak)
        P_mw, F, Fe = zip(*d)
        ax2.errorbar(P_mw, F, yerr=Fe, fmt="-o", color=PEAK_COLOR[peak], ms=5.5, lw=1.4,
                    capsize=2, label=PEAK_LABEL[peak], zorder=4)
        ymax_panel = max(ymax_panel, max(f + fe for f, fe in zip(F, Fe)))
        ymin_panel = min(ymin_panel, min(f - fe for f, fe in zip(F, Fe)))
        spreads.append(max(F) - min(F))

        core_pk = core.get(f"993.{peak}nm", core_mean)
        base0 = _fwhm_of(0.6, core_pk, transit130, 0.0, nu)
        excess = np.array([_fwhm_of(0.6, core_pk, transit130, kappa_ub * P, nu)
                           for P in Pgrid_W]) - base0
        growth225.append(float(excess[-1]))
        anchor = F[0]  # this peak's own lowest-power data point
        curve = anchor + (excess - excess[0])
        ax2.plot(Pgrid_W * 1000.0, curve, "--", color=PEAK_COLOR[peak], lw=1.0, alpha=0.75,
                zorder=3)
        ax2.fill_between(Pgrid_W * 1000.0, curve, 100.0, color=PEAK_COLOR[peak],
                         alpha=0.05, zorder=1)

    pad = 0.08 * (ymax_panel - ymin_panel)
    ax2.set_xlim(0.0, 260.0)
    ax2.set_ylim(ymin_panel - pad, ymax_panel + pad)
    ratio = float(np.mean(spreads)) / max(float(np.mean(growth225)), 1e-9)
    ax2.set_xlabel("power (mW)")
    ax2.set_ylabel("FWHM (MHz, transition)")
    ax2.set_title("Linewidth-based Stark exclusion: predicted growth is\n"
                 r"$\sim$%dx smaller than the block-to-block scatter (reduced "
                 r"$\chi^2=$%.1f)" "\n"
                 "laser-linewidth component not shown (degenerate at fixed condition)"
                 % (round(ratio), chi2_red_stark), fontsize=8.2)
    # lower right: at P>150 mW the four traces converge to a tight 5.28-5.45
    # MHz band, well clear of the axis floor -- the only corner free of both
    # data and the top-left annotation below.
    ax2.legend(fontsize=6.6, loc="lower right", ncol=1, framealpha=0.95, frameon=True)
    # the bound's claim as a plain annotation, not a legend entry (an
    # exclusion wedge is not a data series): upper right, where the highest
    # data point (P=25 mW, up to ~5.57 MHz) does not reach.
    ax2.text(0.98, 0.97,
             r"$\kappa<$%.2f MHz/W (95%%, profile likelihood):" % kappa_ub + "\n"
             "predicted growth vs power, shaded above each dashed line",
             transform=ax2.transAxes, ha="right", va="top", fontsize=6.6, color="0.25",
             bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor="0.6", lw=0.6))

    fig.suptitle(
        "Two broadening laws: pressure broadening adds width linearly in density "
        r"($W=\mathrm{floor}+\beta N$), measured"
        "\nhere as a SLOPE because per-condition widths carry a common floor; a "
        "light-shift gradient broadens the"
        "\nline as intensity squared (the AC-Stark ramp). Rb instance: the four "
        "993 nm 5S-6S hyperfine components.", fontsize=9.2, y=0.995)
    _footer(fig, "Source: data_raw/MANIFEST.csv + results/ruler_blocks.csv (panel 1 raw "
                 "widths, reproducing the results/beta_self_probe.csv construction),\n"
                 "results/power_sweep.csv, results/stark_sweep.csv (panel 2). Regenerate: "
                 "python scripts/run_beta_self.py && python scripts/run_stark_sweep.py "
                 "&& python scripts/make_figures.py.", fontsize=5.9)
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

    Status: ENVELOPE (unpublished to the depth searched 2026-07-17,
    scalar-only). The vector term near the 6S-5P lines needs its own
    treatment before any trap design -- see rb5s6s/polarizability.py.
    """
    import re

    from rb5s6s import polarizability as P

    rows = _rows("polarizability")
    magic_rows = sorted((r for r in rows if r["quantity"] == "magic_5s6s"),
                        key=lambda r: float(r["value"]))
    if not magic_rows:
        print("  (no magic_5s6s rows in polarizability.csv -- skipping fig17)")
        return
    status = magic_rows[0]["status"]
    crossings = []
    for r in magic_rows:
        lam = float(r["value"])
        m = re.search(r"16-84% band ([\d.]+)\.\.([\d.]+) nm", r["unit"])
        lo, hi = (float(m.group(1)), float(m.group(2))) if m else (lam, lam)
        crossings.append((lam, lo, hi))

    lo_nm, hi_nm = 1050.0, 1420.0
    CLIP = 2500.0                                  # a.u.; masks the 6S->nP poles
    g = np.linspace(lo_nm, hi_nm, 4000)
    a5 = np.array([P.alpha_5s(x) for x in g])
    a6 = np.array([P.alpha_6s(x) for x in g])
    da = a6 - a5
    a6_m = np.where(np.abs(a6) > CLIP, np.nan, a6)
    da_m = np.where(np.abs(da) > CLIP, np.nan, da)

    fig, (ax_top, ax_bot) = plt.subplots(
        2, 1, figsize=(9.6, 7.8), sharex=True,
        gridspec_kw={"height_ratios": [1.15, 1.0], "hspace": 0.08})

    # ---- top: the differential and its zero crossings ----
    ax_top.axhline(0, color="0.55", lw=0.9)
    ax_top.plot(g, da_m, color="#0072B2", lw=1.7)
    for i, (lam, clo, chi) in enumerate(crossings):
        ax_top.axvline(lam, color="#D55E00", ls="--", lw=1.1)
        ax_top.annotate(
            f"{lam:.2f} nm\n[{clo:.2f}, {chi:.2f}]",
            (lam, 0.0), xytext=(0, 34 if i % 2 == 0 else -46),
            textcoords="offset points", ha="center", fontsize=7.6,
            color="#D55E00",
            bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                     edgecolor="none", alpha=0.85),
            arrowprops=dict(arrowstyle="-", color="#D55E00", lw=0.7, alpha=0.6))
    ax_top.text(
        lo_nm + (hi_nm - lo_nm) * 0.02, CLIP * 0.88,
        "at each crossing a trap pulls 5S and 6S equally:\n"
        "the 993 nm clock transition does not move",
        fontsize=7.6, color="0.3", ha="left", va="top")
    ax_top.set_ylabel(r"$\Delta\alpha=\alpha_{6S}-\alpha_{5S}$  (a.u.)")
    ax_top.set_ylim(-CLIP * 1.05, CLIP * 1.05)
    ax_top.set_title(
        "Magic wavelengths: the zero crossings of the differential scalar "
        "polarizability", fontsize=9.5)

    # ---- bottom: the two states separately -- the resonance structure ----
    ax_bot.axhline(0, color="0.7", lw=0.7)
    ax_bot.plot(g, a5, color="#009E73", lw=1.7,
                label=r"$\alpha_{5S}$ (smooth: far from its own D-line poles)")
    ax_bot.plot(g, a6_m, color="#E69F00", lw=1.5,
                label=r"$\alpha_{6S}$ (poles: nearby 6S$\to n$P resonances)")
    for lam, _, _ in crossings:
        ax_bot.axvline(lam, color="#D55E00", ls=":", lw=1.0)
    ax_bot.set_ylim(-CLIP * 1.05, CLIP * 1.05)
    ax_bot.set_xlabel("wavelength (nm)")
    ax_bot.set_ylabel(r"$\alpha$  (a.u.)")
    ax_bot.legend(fontsize=7.5, loc="lower left", framealpha=1.0, frameon=True)

    fig.suptitle(
        "A magic wavelength is where the differential light shift between two states vanishes:\n"
        "a trap there shifts both equally, so the transition it holds atoms for does not move.\n"
        r"Instance: Rb 5S$_{1/2}$-6S$_{1/2}$ (993 nm). Scalar-only, exact for $J=1/2$ under "
        f"linear polarization. Status: {STATUS_WORD.get(status, status.lower())}.",
        fontsize=9.0, y=0.995)

    _footer(fig, "Source: results/polarizability.csv (magic_5s6s rows) + rb5s6s/polarizability.py "
                 "(alpha_5s, alpha_6s). Regenerate: python scripts/run_polarizability.py && "
                 "python scripts/make_figures.py.", y=0.018, fontsize=6.6)
    fig.text(
        0.01, 0.002,
        "Matrix elements: Volz & Schmoranzer 1996, Herold et al. 2012, the Safronova-group "
        "portal, Leonard et al. 2015 (full sourcing in rb5s6s/polarizability.py); unpublished "
        "to the depth searched 2026-07-17.",
        fontsize=6.6, color="0.35")

    _save(fig, "fig17_magic_wavelengths.png")


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
    loop rather than a dead end. Two worked examples from this archive sit
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
    ax.set_ylim(36, 108)
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
              label=None, label_frac=0.5, label_dy=3.2, fontsize=7.6, ax_=ax):
        a = FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=14,
                            color=color, lw=lw, shrinkA=2, shrinkB=2,
                            connectionstyle=connectionstyle, zorder=2)
        ax_.add_patch(a)
        if label:
            lx = p0[0] + label_frac * (p1[0] - p0[0])
            ly = p0[1] + label_frac * (p1[1] - p0[1]) + label_dy
            ax_.text(lx, ly, label, ha="center", va="bottom", fontsize=fontsize,
                     color=color, style="italic", zorder=4)

    # ---- the main loop -----------------------------------------------
    yT, yB, ySpur = 86.0, 60.0, 100.0
    x_obs, x_mech, x_id = 16.0, 50.0, 86.0
    x_claim = 113.0
    x_dom, x_tgt, x_cap = 66.0, 44.0, 16.0

    box((x_obs, yT), 24, 14, "OBSERVATION", edge=GREY, fontweight="bold")
    box((x_mech, yT), 28, 14, "CANDIDATE PHYSICAL\nMECHANISMS", edge=GREY)
    diamond((x_id, yT), 28, 22, "IDENTIFIABILITY\nANALYSIS", edge=GREY)

    arrow((x_obs + 12, yT), (x_mech - 14, yT))
    arrow((x_mech + 14, yT), (x_id - 14, yT))

    # identified branch: a short spur up and out -- a claim does not loop
    box((x_id, ySpur), 22, 11, "IDENTIFIED", edge=BLUE, face="#EAF3FA", textcolor=BLUE,
        fontweight="bold")
    box((x_claim, ySpur), 22, 11, "CLAIM", edge=BLUE, face=BLUE, textcolor="white",
        fontweight="bold")
    arrow((x_id, yT + 11), (x_id, ySpur - 5.5), color=BLUE)
    arrow((x_id + 11, ySpur), (x_claim - 11, ySpur), color=BLUE)

    # degenerate branch: down, then back left along the bottom, forming the loop
    box((x_id, yB), 24, 12, "DEGENERATE", edge=ORANGE, face="#FBEEE6", textcolor=ORANGE,
        fontweight="bold")
    arrow((x_id, yT - 11), (x_id, yB + 6), color=ORANGE)

    box((x_dom, yB), 24, 12, "DOMINANT\nLIMITATION", edge=ORANGE, face="#FBEEE6")
    arrow((x_id - 12, yB), (x_dom + 12, yB), color=ORANGE)

    box((x_tgt, yB), 24, 12, "TARGETED\nMEASUREMENT", edge=ORANGE, face="#FBEEE6")
    arrow((x_dom - 12, yB), (x_tgt + 12, yB), color=ORANGE)

    box((x_cap, yB), 24, 12, "NEW CAPABILITY", edge=GREEN, face="#E6F4EF", textcolor=GREEN,
        fontweight="bold")
    arrow((x_tgt - 12, yB), (x_cap + 12, yB), color=ORANGE)

    # close the loop: a new capability changes what the next observation can resolve
    arrow((x_cap, yB + 6), (x_obs, yT - 7), color=GREEN, lw=2.0,
          label="changes what the next\nobservation can resolve", label_frac=0.5,
          label_dy=1.5, fontsize=7.8)

    ax.text(x_mech, yT - 12.5, "e.g. a profile-likelihood map, a lever test,\n"
            "a covariance check (fig6, fig7, fig10)",
            ha="center", va="top", fontsize=7.2, color="0.4", style="italic")

    ax.text(64, 44.0,
            "The 30-second version of this repository's method: most of what it "
            "reports today lives on the\nDEGENERATE branch, worked twice below.",
            ha="center", va="center", fontsize=9.2, color="0.15")

    # ---- two worked examples, smaller type, underneath -----------------
    fig.text(0.5, 0.300, "Two instances of the degenerate branch, from this archive",
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

    chain2(33, "(a)", ["linewidth", "transit + laser\nboth broaden it", "strong\ndegeneracy",
                       "beam-waist\nmeasurement", "absolute\ndecomposition"], ORANGE)
    chain2(11, "(b)", ["AC-Stark shift", "line centres\nlost (fit)", "width-only\nhandle",
                       "fixed\nfrequency lock", "direct Stark\nmeasurement"], ORANGE)

    fig.suptitle("From an observation to a claim, or to the capability that gets you one: "
                 "the identifiability loop",
                 fontsize=12.5, y=0.985, fontweight="bold")
    _footer(fig, "Source: none. A schematic of the method (rb5s6s.identifiability, "
                 "fig6/fig7/fig10 are worked instances of the identifiability-analysis step; "
                 "fig3 and results/centre_stark.csv are the two worked examples below). "
                 "Regenerate: python scripts/make_figures.py.")
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
    fig.text(0.5, 0.945,
             "shared shape, the values of record: "
             f"$\\gamma_\\mathrm{{coll}}$ = {f0['gc']:.2f} MHz · "
             f"$\\sigma_\\mathrm{{laser}}$ = {f0['sl']:.2f} MHz · "
             f"transit = {f0['transit']:.2f} MHz · model FWHM = "
             f"{f0['fwhm']:.2f} MHz",
             ha="center", fontsize=10, color="#1a3a6b")
    fig.text(0.5, 0.921,
             "free per repeat, because the lock drifts: centre, height, "
             "background, saturation scale",
             ha="center", fontsize=9.5, color="0.35")

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
                 f"centre {fr['cc'] - cc0:+.2f} ± {fr['cc_err']:.2f} MHz "
                 "(about the five-repeat mean)\n"
                 r"$\chi^2_\nu$" + f" = {fr['chi2_red']:.2f}",
                 transform=axf.transAxes, fontsize=7.2, va="top", ha="right",
                 color="0.25")
        res = fr["v"] - fr["model_at"](fr["sol"].x, fr["x"])
        axr.plot(xd[m], res[m], ".", ms=2.0, color="0.55")
        axr.axhline(0.0, color="#8f1f1f", lw=0.9, ls=(0, (4, 3)))
        axr.set_ylabel("residual (V)", fontsize=8)
        axr.tick_params(labelsize=7.5)
        lim = 4.0 * float(np.std(res[m]))
        axr.set_ylim(-lim, lim)
        if i < 4:
            axf.tick_params(labelbottom=False)
            axr.tick_params(labelbottom=False)
        else:
            axf.set_xlabel("detuning from this repeat's centre (MHz, "
                           "laser axis)", fontsize=8.5)
            axr.set_xlabel("detuning (MHz, laser axis)", fontsize=8.5)

    _footer(fig, "Sources: results/global_archive_fit.csv (the shared optimum "
                 "and its errors) + data_raw archive (per-trace data; local "
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
    gs = fig.add_gridspec(1, 1, left=0.065, right=0.985, top=0.825,
                          bottom=0.135)
    inner = gs[0, 0].subgridspec(4, 5, hspace=0.26, wspace=0.10)
    shared = None
    for r, pk in enumerate(peaks):
        for c, P in enumerate(POWERS):
            cell = inner[r, c].subgridspec(2, 1, height_ratios=[3.0, 1.0],
                                           hspace=0.05)
            axc = fig.add_subplot(cell[0])
            axr = fig.add_subplot(cell[1], sharex=axc)
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
            if shared is None:
                shared = fr
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
            axr.plot(xd[m][::3], pull[m][::3], ".", ms=1.0,
                     color=PEAK_COLOR[pk], alpha=0.5)
            axc.text(0.04, 0.90, r"$\chi^2_\nu$" + f"={fr['chi2_red']:.2f}",
                     transform=axc.transAxes, fontsize=6, va="top",
                     color="0.4")
            if r == 0:
                axc.set_title(f"{int(round(P * 1000))} mW", fontsize=8.5)
            if c == 0:
                axc.set_ylabel(f"993.{pk} nm", fontsize=8,
                               color=PEAK_COLOR[pk])
                axr.set_ylabel("resid\n(σ)", fontsize=6.5, color="0.45",
                               labelpad=2)

    fig.suptitle("The joint fit across twenty conditions: one physical "
                 "model, nothing re-tuned per panel", fontsize=13, y=0.962)
    fig.text(0.5, 0.913,
             "the model: a Lorentzian core (natural 3.49 MHz + collisions) "
             "convolved with the laser width and the transit kernel, with "
             "detector saturation",
             ha="center", fontsize=9, color="#1a3a6b")
    fig.text(0.5, 0.888,
             "one shared optimum for every panel, the 130 °C values of "
             f"record: $\\gamma_\\mathrm{{coll}}$ = {shared['gc']:.2f} MHz, "
             f"$\\sigma_\\mathrm{{laser}}$ = {shared['sl']:.2f} MHz, "
             f"transit = {shared['transit']:.2f} MHz",
             ha="center", fontsize=9, color="0.25")
    fig.text(0.5, 0.864,
             "free per trace: centre, height, background, saturation",
             ha="center", fontsize=9, color="0.25")
    fig.text(0.5, 0.072, "detuning from each trace's own centre (MHz, "
             "laser axis) · vertical scales grow with power (amplitude "
             r"$\propto P^2$)" + " · residual strips are in units of that "
             "trace's own point-by-point uncertainty",
             ha="center", fontsize=8.5, color="0.35")
    _footer(fig, "Sources: results/global_archive_fit.csv (the shared optimum) "
                 "+ data_raw archive (per-trace data; local nuisance refits "
                 "only). Regenerate: python scripts/make_figures.py.")
    _save(fig, "fig22_joint_fit_twenty.png")


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
    fig_wavemeter_reconstruction()
    fig_drift_story()
    fig_fit_gallery()
    fig_single_peak_fits()
    fig_width_trends()
    fig_magic_wavelengths()
    fig_method_loop()
    fig_joint_fit_five()
    fig_joint_fit_twenty()
    print(f"wrote figures to {FIG}/")
    for p in sorted(FIG.glob("*.png")):
        print(f"  {p.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

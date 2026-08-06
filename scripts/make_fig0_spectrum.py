#!/usr/bin/env python3
"""
fig0 -- a representative fitted spectrum (the "here is our data" figure).

Not part of the results pipeline: it re-loads ONE canonical condition's repeats
end-to-end (M0->M1->M2->M3, exactly as scripts/run_linefit.py does), re-runs the
joint fit_condition, and plots the brightest single trace with the composite
model (natural (x) transit (x) laser) overlaid, plus a residual panel. Style
matches scripts/make_figures.py (Okabe-Ito, recessive grid).

Writes figures/fig0_spectrum.png. Default line: 993.4192 nm (85Rb F3) at
130 C / 225 mW -- the highest-SNR canonical condition (chi2_red ~ 1.1).
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C  # noqa: E402
from rb5s6s.constants import GAMMA_NAT_HZ  # noqa: E402
from rb5s6s.ingest import load_manifest, load_trace, trace_path  # noqa: E402
from rb5s6s.noise import condition_noise_model, signal_level, sigma_of_v  # noqa: E402
from rb5s6s.qc import trace_metrics, hard_flags, ingest_flags  # noqa: E402
from rb5s6s.linefit import (fit_condition, to_frequency, transit_fwhm_at_T,  # noqa: E402
                            _shared_profile_grid)

GNAT = GAMMA_NAT_HZ / 1e6
FIG = C.REPO_ROOT / "figures"
FIG.mkdir(exist_ok=True)
PEAK_COLOR = {"4121": "#0072B2", "4154": "#D55E00", "4192": "#009E73", "4207": "#E69F00"}
# "F1" read as a label code rather than a quantum number, so the hyperfine
# level is written out. Kept identical to the _ISO registry in
# scripts/make_figures.py: the two move together.
_ISO = {"4121": "$^{87}$Rb F = 1", "4154": "$^{85}$Rb F = 2",
        "4192": "$^{85}$Rb F = 3", "4207": "$^{87}$Rb F = 2"}
PLOT_HALFWIDTH_MHZ = 15.0  # detuning window shown (excludes the ~40 MHz mirror)

plt.rcParams.update({"figure.dpi": 130, "font.size": 10, "axes.grid": True,
                     "grid.alpha": 0.25, "axes.axisbelow": True, "legend.frameon": False})


def _footer(fig, text, y=0.008, fontsize=6.3):
    """The provenance line every figure carries: the sources it is drawn from
    and the command that regenerates it. Same position, size and colour as
    scripts/make_figures.py's own _footer, so the set reads as one document."""
    fig.text(0.01, y, text, fontsize=fontsize, color="0.35", va="bottom")


def fitted_total_width(role, peak, T, P):
    """The condition's fitted total FWHM and its uncertainty, read from
    results/linefit_conditions.csv.

    Measuring the width off the plotted curve on a 0.025 MHz grid (what this
    script used to do) can only run low, and it printed 5.33 against the
    5.3683 +/- 0.0202 the committed CSV carries for the same fit. The figure
    now quotes the value of record, with its uncertainty."""
    for r in csv.DictReader(open(C.RESULTS_DIR / "linefit_conditions.csv")):
        if (r["role"], r["peak"], r["T"], r["P"]) == (role, peak, T, P):
            return float(r["total_fwhm"]), float(r["total_fwhm_err"])
    raise SystemExit(f"no linefit_conditions row for {(role, peak, T, P)}")


def _block_rates():
    """M2 transition-axis rate per block (mirrors run_linefit.load_block_rates)."""
    trate, pbr = {}, defaultdict(dict)
    for r in csv.DictReader(open(C.RESULTS_DIR / "ruler_blocks.csv")):
        rate = 2.0 * float(r["rate"])  # laser -> transition axis
        # rate_err omitted deliberately: display-only figure; the ~1% axis-scale
        # error is invisible at plot resolution (review finding 4, 2026-07-16)
        if r["session"] == "T":
            trate[(r["peak"], r["T"])] = rate
        else:
            pbr[r["peak"]][r["bracket"]] = rate
    prate = {p: float(np.mean(list(br.values()))) for p, br in pbr.items()}
    return trate, prate


def load_condition(role, peak, T, P):
    """Return (freqs, volts, law) for one canonical RF-off condition, using the
    same QC and rate assignment as scripts/run_linefit.py."""
    trate, prate = _block_rates()
    rate = trate.get((peak, T)) if role == "t_sweep" else prate.get(peak)
    if rate is None:
        raise SystemExit(f"no M2 rate for {(role, peak, T, P)}")
    freqs, volts = [], []
    for r in load_manifest():
        if (r["flag"], r["rf_on"], r["role"], r["peak"], r["temperature_C"],
                r["power_mW"]) != ("canonical", "False", role, peak, T, P):
            continue
        t, v, info = load_trace(trace_path(r), with_info=True)
        m = trace_metrics(t, v)
        if any("truncated" in f or "dropout" in f
               for f in hard_flags(m, rf_on=False) + ingest_flags(info)):
            continue
        freqs.append(to_frequency(t, rate)); volts.append(v)
    if len(volts) < 3:
        raise SystemExit(f"only {len(volts)} usable traces for {(role, peak, T, P)}")
    return freqs, volts, condition_noise_model(volts)


def make(role="p_sweep", peak="4192", T="130", P="225"):
    freqs, volts, law = load_condition(role, peak, T, P)
    transit = transit_fwhm_at_T(float(T), C.TRANSIT_FWHM_PLACEHOLDER_MHZ)
    fit = fit_condition(freqs, volts, T_C=float(T), law=law, transit_fwhm=transit)
    gc, sl = fit["gamma_coll"], fit["sigma_laser"]

    # brightest single trace of the repeats -> the representative spectrum
    i = int(np.argmax(fit["amps"]))
    nu, v = freqs[i], volts[i]
    c = fit["centers"][i]

    # rebuild the fitted shared (area-normalized) shape; recover this trace's
    # linear params [A, b0, b1] by least squares at the fixed shape+center
    # (they are linear, so this reproduces the fit's own values for this trace)
    g, prof = _shared_profile_grid(gc, sl, transit, 0.0, "gaussian")
    shape = np.interp(nu - c, g, prof, left=0.0, right=0.0)
    win = np.abs(nu - c) <= PLOT_HALFWIDTH_MHZ
    D = np.vstack([shape[win], np.ones(win.sum()), nu[win]]).T
    (A, b0, b1), *_ = np.linalg.lstsq(D, v[win], rcond=None)

    x = nu[win] - c
    base = b0 + b1 * nu[win]
    peakV = float((A * shape[win]).max())
    y = (v[win] - base) / peakV
    ymod = (A * shape[win]) / peakV
    resid = y - ymod
    # standardized residuals: per-point M1 noise on the normalized axis. A flat
    # +-1 band is valid here, whereas the raw noise grows with signal near the peak, so
    # a single median-sigma band would understate it exactly where resid is
    # largest -- hence resid/sigma, which also visualizes chi2_red ~ 1 directly.
    lev, _ = signal_level(v)
    sig = sigma_of_v(np.maximum(lev, 0.0), law)[win] / peakV
    rstd = resid / np.maximum(sig, 1e-9)

    # smooth model on a fine axis for the overlay curve
    xf = np.linspace(-PLOT_HALFWIDTH_MHZ, PLOT_HALFWIDTH_MHZ, 1200)
    yf = A * np.interp(xf, g, prof, left=0.0, right=0.0) / peakV

    total_fwhm, total_fwhm_err = fitted_total_width(role, peak, T, P)
    col = PEAK_COLOR[peak]

    fig, (ax, axr) = plt.subplots(2, 1, figsize=(6.4, 5.3), sharex=True,
                                  gridspec_kw={"height_ratios": [3.2, 1]},
                                  constrained_layout=True)
    ax.plot(x, y, "o", ms=3.2, color=col, alpha=0.7, label="data (one of 5 repeats)")
    ax.plot(xf, yf, "-", color="k", lw=1.6,
            label="fit: natural and collisional widths,\n"
                  "convolved with transit and laser")
    ax.axhline(0.0, color="0.6", lw=0.8, ls=":")
    ax.set_ylabel("normalized fluorescence")
    ax.set_title(f"993.{peak} nm ({_ISO[peak]}) two-photon line: {T} $^{{\\circ}}$C, {P} mW\n"
                 f"total width at half maximum {total_fwhm:.2f} $\\pm$ "
                 f"{total_fwhm_err:.2f} MHz, from the joint fit to the repeats",
                 fontsize=9.5)
    # Upper left: the line rises at centre and the right shoulder carries the
    # legend into the data. The left corner is baseline at this window.
    ax.legend(fontsize=8, loc="upper left")
    ax.set_ylim(-0.10, 1.12)

    # The four components the fit convolves. All four are full widths at half
    # maximum (rb5s6s.lineshape takes an FWHM for every kernel, the Gaussian
    # laser term included), and the box now says so, because a reader who reads
    # sigma_laser as a standard deviation cannot reproduce the total above.
    # The natural width is fixed by the 6S lifetime; the transit width rides on
    # the assumed waist, whose value is read from the constant of record rather
    # than typed.
    ax.annotate(f"natural width {GNAT:.2f} MHz\n"
                f"collisional width {gc:.2f} MHz\n"
                f"transit-time width {transit:.2f} MHz,\n"
                f"  from a beam waist of {C.W0_PRIOR_M * 1e6:.0f} $\\mu$m\n"
                "  that has not been measured\n"
                f"laser width {sl:.2f} MHz\n"
                "all four are widths at half maximum\n"
                f"reduced chi-squared {fit['chi2_red']:.2f}",
                xy=(0.98, 0.97), xycoords="axes fraction", va="top", ha="right",
                fontsize=7.5, color="0.25",
                bbox=dict(boxstyle="round", fc="white", ec="0.8", alpha=0.85))

    axr.axhspan(-1.0, 1.0, color="0.5", alpha=0.15, label="band of one point error")
    axr.plot(x, rstd, "o", ms=2.6, color=col, alpha=0.7)
    axr.axhline(0.0, color="k", lw=0.9)
    axr.set_ylabel("residual, in units\nof the point error", fontsize=8.5)
    axr.set_xlabel("detuning from line centre (MHz at the two-photon transition frequency)")
    axr.legend(fontsize=7, loc="upper right")
    rmax = min(max(float(np.max(np.abs(rstd))) * 1.2, 3.0), 8.0)
    axr.set_ylim(-rmax, rmax)
    _footer(fig, "Sources: the data_raw archive (this trace, re-fit end to end) + "
                 "results/ruler_blocks.csv (frequency axis)\n"
                 "+ results/linefit_conditions.csv (the total width and its error). "
                 "Regenerate: python scripts/make_fig0_spectrum.py.")
    # constrained_layout cannot see fig.text, so the footer's strip is
    # reserved on the layout engine itself (its rect is left, bottom, width,
    # height, not the corner pair tight_layout takes)
    fig.get_layout_engine().set(rect=(0.0, 0.048, 1.0, 0.945))
    out = FIG / "fig0_spectrum.png"
    fig.savefig(out); plt.close(fig)
    print(f"wrote {out}")
    print(f"  {peak} {role} T{T} P{P}: A={A:.2f} V, total_fwhm={total_fwhm:.4f} +/- "
          f"{total_fwhm_err:.4f} MHz (results/linefit_conditions.csv), "
          f"gamma_coll={gc:.2f}, sigma_laser={sl:.2f}, chi2_red={fit['chi2_red']:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(make())

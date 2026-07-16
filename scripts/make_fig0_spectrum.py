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
_ISO = {"4121": "$^{87}$Rb F1", "4154": "$^{85}$Rb F2",
        "4192": "$^{85}$Rb F3", "4207": "$^{87}$Rb F2"}
PLOT_HALFWIDTH_MHZ = 15.0  # detuning window shown (excludes the ~40 MHz mirror)

plt.rcParams.update({"figure.dpi": 130, "font.size": 10, "axes.grid": True,
                     "grid.alpha": 0.25, "axes.axisbelow": True, "legend.frameon": False})


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
    # standardized residuals: per-point M1 noise on the normalized axis. (A flat
    # +-1 band is honest here; the raw noise grows with signal near the peak, so
    # a single median-sigma band would understate it exactly where resid is
    # largest -- hence resid/sigma, which also visualizes chi2_red ~ 1 directly.)
    lev, _ = signal_level(v)
    sig = sigma_of_v(np.maximum(lev, 0.0), law)[win] / peakV
    rstd = resid / np.maximum(sig, 1e-9)

    # smooth model on a fine axis for the overlay curve
    xf = np.linspace(-PLOT_HALFWIDTH_MHZ, PLOT_HALFWIDTH_MHZ, 1200)
    yf = A * np.interp(xf, g, prof, left=0.0, right=0.0) / peakV

    total_fwhm = 2.0 * xf[yf >= 0.5 * yf.max()][-1] if (yf >= 0.5 * yf.max()).any() else np.nan
    col = PEAK_COLOR[peak]

    fig, (ax, axr) = plt.subplots(2, 1, figsize=(6.4, 5.3), sharex=True,
                                  gridspec_kw={"height_ratios": [3.2, 1]},
                                  constrained_layout=True)
    ax.plot(x, y, "o", ms=3.2, color=col, alpha=0.7, label="data (one of 5 repeats)")
    ax.plot(xf, yf, "-", color="k", lw=1.6,
            label=r"fit: natural $\otimes$ transit $\otimes$ laser")
    ax.axhline(0.0, color="0.6", lw=0.8, ls=":")
    ax.set_ylabel("normalized fluorescence")
    ax.set_title(f"993.{peak} nm ({_ISO[peak]}) two-photon line — {T} $^{{\\circ}}$C, {P} mW\n"
                 f"total FWHM {total_fwhm:.2f} MHz (transition axis)", fontsize=9.5)
    ax.legend(fontsize=8, loc="upper right")
    ax.set_ylim(-0.10, 1.12)

    # width-budget box: the four components the fit convolves (natural is fixed
    # by the 6S lifetime; transit rides on the OPEN w0 prior)
    ax.annotate(f"$\\Gamma_\\mathrm{{nat}}$ = {GNAT:.2f} MHz\n"
                f"$\\gamma_\\mathrm{{coll}}$ = {gc:.2f} MHz\n"
                f"transit = {transit:.2f} MHz ($w_0$ prior)\n"
                f"$\\sigma_\\mathrm{{laser}}$ = {sl:.2f} MHz\n"
                f"$\\chi^2_\\nu$ = {fit['chi2_red']:.2f}",
                xy=(0.02, 0.97), xycoords="axes fraction", va="top", ha="left",
                fontsize=7.5, color="0.25",
                bbox=dict(boxstyle="round", fc="white", ec="0.8", alpha=0.85))

    axr.axhspan(-1.0, 1.0, color="0.5", alpha=0.15, label=r"$\pm1\sigma$")
    axr.plot(x, rstd, "o", ms=2.6, color=col, alpha=0.7)
    axr.axhline(0.0, color="k", lw=0.9)
    axr.set_ylabel(r"resid. / $\sigma$")
    axr.set_xlabel("detuning from line centre  (MHz, transition axis)")
    axr.legend(fontsize=7, loc="upper right")
    rmax = min(max(float(np.max(np.abs(rstd))) * 1.2, 3.0), 8.0)
    axr.set_ylim(-rmax, rmax)
    out = FIG / "fig0_spectrum.png"
    fig.savefig(out); plt.close(fig)
    print(f"wrote {out}")
    print(f"  {peak} {role} T{T} P{P}: A={A:.2f} V, total_fwhm={total_fwhm:.2f} MHz, "
          f"gamma_coll={gc:.2f}, sigma_laser={sl:.2f}, chi2_red={fit['chi2_red']:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(make())

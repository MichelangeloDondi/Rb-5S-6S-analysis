#!/usr/bin/env python3
"""Teaching panels for the documentation in docs/.

These are NOT result figures. Every one is drawn from a closed-form
expression or from synthetic numbers generated here with a fixed seed, none
of them reads results/ or data_raw/, and none of them carries a data
fingerprint, because there is no data behind them to go stale. They live in
docs/wiki/figures/ rather than figures/ for exactly that reason: the
figures/ tree is the result gallery and is guarded as one.

Since 2026-08-26 every wiki page carries at least two figures, by
decision. Pages draw from the result gallery in
figures/ and the apparatus record where those fit, and from the teaching
panels here where the page needs a closed-form illustration of its own
concept. The 44 panels below are those illustrations.

Register: the same plain-physics rules as the result figures, so no pipeline
dialect in anything drawn, and every drawing function carries a footer
naming what the panel is and how to rebuild it.

Run: python scripts/make_wiki_figures.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.special import jv

from rb5s6s._compat import trapezoid

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

OUT = Path(__file__).resolve().parents[1] / "docs" / "wiki" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

INK = "0.25"
ACCENT = "#0072B2"      # Okabe-Ito blue, the same family the gallery uses
ACCENT2 = "#D55E00"     # Okabe-Ito vermillion
ACCENT3 = "#009E73"     # Okabe-Ito green


def _footer(fig, text):
    """One provenance line per figure, in the same place on every panel."""
    fig.text(0.01, 0.012, text, fontsize=6.3, color="0.35", va="bottom")


def _save(fig, name):
    fig.tight_layout(rect=(0, 0.045, 1, 1))
    fig.savefig(OUT / name, dpi=200)
    plt.close(fig)
    print(f"  wrote {name}")


def fig_allan_deviation():
    """Two noise processes that a plain standard deviation cannot tell apart."""
    rng = np.random.default_rng(20260816)
    n = 1 << 14
    white = rng.standard_normal(n)
    walk = np.cumsum(rng.standard_normal(n)) * 0.02

    def adev(y, taus):
        out = []
        for m in taus:
            k = len(y) // m
            if k < 3:
                out.append(np.nan)
                continue
            a = y[:k * m].reshape(k, m).mean(axis=1)
            out.append(np.sqrt(0.5 * np.mean(np.diff(a) ** 2)))
        return np.array(out)

    taus = np.unique(np.logspace(0, 3.2, 24).astype(int))
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0))

    ax[0].plot(white[:1200], lw=0.4, color=ACCENT)
    ax[0].plot(walk[:1200], lw=0.9, color=ACCENT2)
    ax[0].set_xlabel("sample number")
    ax[0].set_ylabel("frequency (arbitrary units)")
    ax[0].set_title("(a) two records", fontsize=9)

    for y, c, lab in ((white, ACCENT, "white noise"),
                      (walk, ACCENT2, "random walk")):
        ax[1].loglog(taus, adev(y, taus), "o-", ms=3, lw=1.2, color=c,
                     label=lab)
    ref = taus.astype(float)
    ax[1].loglog(ref, 0.9 * ref ** -0.5, ":", color=INK, lw=1.0)
    ax[1].loglog(ref, 0.012 * ref ** 0.5, "--", color=INK, lw=1.0)
    # Each slope label sits beside ITS OWN curve. Placed together on the same
    # side they read as labelling the wrong line, which is what the first
    # render did.
    ax[1].text(1.05, 0.33, r"slope $-1/2$", fontsize=7.5, color=INK)
    ax[1].text(260, 0.62, r"slope $+1/2$", fontsize=7.5, color=INK)
    ax[1].set_xlabel("averaging time (samples)")
    ax[1].set_ylabel("Allan deviation (arbitrary units)")
    ax[1].set_title("(b) the same records, resolved", fontsize=9)
    ax[1].legend(fontsize=7.5, frameon=False)
    ax[1].grid(alpha=0.25, which="both")

    _footer(fig, "synthetic noise, fixed seed. "
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_allan_deviation.png")


def fig_bessel():
    """The amplitudes a phase modulator writes onto the light."""
    beta = np.linspace(0, 6, 800)
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0))

    for n, c in ((0, ACCENT), (1, ACCENT2), (2, ACCENT3)):
        ax[0].plot(beta, jv(n, beta), lw=1.4, color=c, label=f"$J_{n}$")
    ax[0].axhline(0, color=INK, lw=0.6)
    ax[0].axvline(2.405, color=INK, ls=":", lw=1.0)
    ax[0].text(2.46, 0.72, r"$J_0$ first zero" "\n" r"$\beta = 2.405$",
               fontsize=7.5, color=INK)
    ax[0].set_xlabel(r"modulation depth $\beta$ (radians)")
    ax[0].set_ylabel("amplitude (dimensionless)")
    ax[0].set_title("(a) the first three orders", fontsize=9)
    ax[0].legend(fontsize=8, frameon=False)
    ax[0].grid(alpha=0.25)

    for n, c in ((0, ACCENT), (1, ACCENT2), (2, ACCENT3)):
        ax[1].plot(beta, jv(n, beta) ** 2, lw=1.4, color=c,
                   label=f"order {n}")
    ax[1].axvline(2.405, color=INK, ls=":", lw=1.0)
    ax[1].set_xlabel(r"modulation depth $\beta$ (radians)")
    ax[1].set_ylabel("power fraction (dimensionless)")
    ax[1].set_title("(b) power in each sideband", fontsize=9)
    ax[1].legend(fontsize=8, frameon=False)
    ax[1].grid(alpha=0.25)

    _footer(fig, "closed form, no data. "
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_bessel.png")


def fig_eom_comb():
    """What the modulation depth does to a two-photon comb."""
    orders = np.arange(-6, 7)
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0), sharey=True)

    for a, b, title in ((ax[0], 0.30, r"(a) shallow, $\beta = 0.30$"),
                        (ax[1], 1.202, r"(b) carrier nulled, $\beta = 1.202$")):
        amp = jv(orders, 2 * b) ** 2
        a.bar(orders, amp, width=0.35, color=ACCENT, edgecolor="none")
        a.set_xlabel("tooth number")
        a.set_title(title, fontsize=9)
        a.grid(alpha=0.25, axis="y")
        a.set_xticks(orders[::2])
    ax[0].set_ylabel("relative height (dimensionless)")
    ax[0].annotate("outer teeth too small to fit",
                   xy=(3, jv(3, 0.6) ** 2), xytext=(1.6, 0.55),
                   fontsize=7.5, color=INK,
                   arrowprops=dict(arrowstyle="->", color=INK, lw=0.8))

    _footer(fig, "closed form, no data. "
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_eom_comb.png")


def fig_joint_fit_toy():
    """Sharing a parameter across repeats that genuinely share it.

    Both estimates are REAL least-squares fits, not a summary statistic. The
    shared one is a single fit over all four traces at once with one width
    and a free amplitude and centre per trace, which is what a joint fit
    does. Averaging four independent widths is a different operation and
    would teach the wrong thing on a page about joint fitting.
    """
    from scipy.optimize import least_squares

    rng = np.random.default_rng(5852)
    x = np.linspace(-6, 6, 220)
    width_true, offsets = 2.0, [-1.4, -0.5, 0.4, 1.3]
    noise = 0.16

    traces = []
    for off in offsets:
        y = 1.0 / (1 + ((x - off) / width_true) ** 2)
        traces.append(y + noise * rng.standard_normal(x.size))

    def lor(amp, c, w):
        return amp / (1 + ((x - c) / w) ** 2)

    indep = []
    for y in traces:
        sol = least_squares(lambda p, y=y: lor(p[0], p[1], abs(p[2])) - y,
                            [1.0, 0.0, 1.5])
        indep.append(abs(sol.x[2]))

    def joint_resid(p):
        w = abs(p[0])
        return np.concatenate([lor(p[1 + 2 * i], p[2 + 2 * i], w) - y
                               for i, y in enumerate(traces)])

    shared = abs(least_squares(
        joint_resid, [1.5] + [1.0, 0.0] * len(traces)).x[0])

    fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0))
    for y in traces:
        ax[0].plot(x, y, lw=0.8, alpha=0.85)
    ax[0].set_xlabel("detuning (arbitrary units)")
    ax[0].set_ylabel("signal (arbitrary units)")
    ax[0].set_title("(a) four repeats, each drifted", fontsize=9)
    ax[0].grid(alpha=0.25)

    # Direct labels, placed against the fitted coordinates printed below, so
    # nothing lands on a marker or on another label.
    ax[1].axhline(width_true, color=INK, ls="--", lw=1.0)
    ax[1].axhline(shared, color=ACCENT, lw=1.6)
    ax[1].plot(range(1, 5), indep, "o", ms=6, color=ACCENT2)
    ax[1].text(4.5, width_true + 0.004, "true width", fontsize=7.5,
               color=INK, ha="right", va="bottom")
    ax[1].text(0.55, shared - 0.030, "one width fitted across all four",
               fontsize=7.5, color=ACCENT, va="top")
    ax[1].text(0.55, max(indep) + 0.008, "each trace fitted alone",
               fontsize=7.5, color=ACCENT2, va="bottom")
    ax[1].set_xlabel("repeat number")
    ax[1].set_ylabel("width (arbitrary units)")
    ax[1].set_title("(b) one width, or four", fontsize=9)
    ax[1].set_xlim(0.4, 4.6)
    ax[1].set_ylim(min(indep) - 0.03, max(indep) + 0.045)
    ax[1].grid(alpha=0.25)
    print(f"    joint-fit panel: independent widths "
          f"{[round(v, 3) for v in indep]}, shared {shared:.3f}, "
          f"true {width_true}")

    _footer(fig, "synthetic traces, fixed seed. "
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_joint_fit_toy.png")


def fig_shift_distribution():
    """The inhomogeneous light shift as a distribution, not a number.

    Closed form throughout: for the two-photon triangle ramp the shift
    density on [-S0, 0] is f(s) = 2|s|/S0^2 under I^2 weighting, against
    the uniform f(s) = 1/S0 a one-photon (I-weighted) line would carry.
    The panel shows both, with each distribution's mean marked, which is
    the single number a naive treatment would quote in place of either
    shape. Rebuild: python scripts/make_wiki_figures.py
    """
    import numpy as np
    s0 = 1.0
    s = np.linspace(-s0, 0.0, 400)
    two = 2.0 * np.abs(s) / s0**2
    one = np.ones_like(s) / s0
    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    ax.plot(s, two, lw=2.2, label="two-photon, $I^2$ weighting: $f(s)=2|s|/S_0^2$")
    ax.plot(s, one, lw=2.2, ls="--", label="one-photon, $I$ weighting: uniform")
    ax.axvline(-2.0 * s0 / 3.0, color="C0", lw=1.0, alpha=0.7)
    ax.axvline(-s0 / 2.0, color="C1", lw=1.0, alpha=0.7, ls="--")
    ax.annotate("mean $-\\frac{2}{3}S_0$", (-2.0 * s0 / 3.0, 0.30),
                color="C0", ha="center", fontsize=9,
                textcoords="offset points", xytext=(-2, 0))
    ax.annotate("mean $-\\frac{1}{2}S_0$", (-s0 / 2.0, 0.12),
                color="C1", ha="center", fontsize=9,
                textcoords="offset points", xytext=(2, 0))
    ax.set_xlabel("shift $s$ ($S_0$)")
    ax.set_ylabel("probability density")
    ax.set_xlim(-1.02 * s0, 0.02)
    ax.set_ylim(0, 2.3)
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    _footer(fig, "Closed form, no data. The line carries the whole shape, "
                 "and the two weightings disagree about its mean.\n"
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_shift_distribution.png")


def fig_ic_penalty():
    """What each criterion charges for one extra parameter."""
    n = np.logspace(0.5, 6, 400)
    fig, ax = plt.subplots(figsize=(5.0, 3.5))
    ax.semilogx(n, np.full_like(n, 2.0), lw=1.6, color=ACCENT,
                label="Akaike, 2 per parameter")
    ax.semilogx(n, np.log(n), lw=1.6, color=ACCENT2,
                label="Bayesian, $\\ln N$ per parameter")
    ax.axvline(np.e ** 2, color=INK, ls=":", lw=1.0)
    ax.set_ylim(0, 15)
    ax.text(25, 0.55, "the two agree at $N = e^2 \\approx 7.4$",
            fontsize=7.5, color=INK)
    ax.set_xlabel("number of points $N$ (dimensionless)")
    ax.set_ylabel("penalty per parameter (dimensionless)")
    ax.legend(fontsize=8, frameon=False, loc="upper left")
    ax.grid(alpha=0.25, which="both")

    _footer(fig, "closed form, no data. "
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_ic_penalty.png")


def fig_sampling_the_line():
    """Why a wider span needs a longer record, drawn at the real numbers.

    A NOISELESS version of this panel is misleading and was drawn first: two
    dozen points trace a smooth curve perfectly well, so the short record
    looks adequate. The shortfall is not smoothness, it is how many NOISY
    samples the width is fitted from, so the noise has to be in the picture.
    It is drawn at the measured law, a = 0.00297 and b = 0.001004 from
    results/noise_model.csv, on a trace of unit peak.
    """
    from scipy.optimize import least_squares

    span, fwhm = 2400.0, 5.41
    a_v, b_v = 0.00297, 0.001004
    nu = np.linspace(-12, 12, 2000)
    curve = 1.0 / (1 + (2 * nu / fwhm) ** 2)

    fig, ax = plt.subplots(1, 2, figsize=(7.4, 3.2), sharey=True)
    for a, npts in zip(ax, (10000, 40000)):
        step = span / npts
        s = np.arange(-12, 12 + step, step)
        clean = 1.0 / (1 + (2 * s / fwhm) ** 2)
        rng = np.random.default_rng(4)
        y = clean + np.sqrt(a_v ** 2 + b_v * clean) * rng.standard_normal(s.size)
        on_line = int(np.sum(np.abs(s) <= fwhm / 2))

        widths = []
        for k in range(40):
            r = np.random.default_rng(100 + k)
            yy = clean + np.sqrt(a_v ** 2 + b_v * clean) * r.standard_normal(s.size)
            sol = least_squares(
                lambda q: q[0] / (1 + (2 * (s - q[1]) / abs(q[2])) ** 2) - yy,
                [1.0, 0.0, fwhm])
            widths.append(abs(sol.x[2]))
        spread = float(np.std(widths))

        a.plot(s, y, ".", ms=2.2, color=ACCENT, zorder=2)
        a.plot(nu, curve, color=INK, lw=1.1, zorder=3)
        a.axvspan(-fwhm / 2, fwhm / 2, color="0.90", zorder=0)
        a.set_xlabel("detuning (MHz)")
        a.set_title(f"{npts} points over {span:.0f} MHz\n"
                    f"{on_line} on the line, width scatter {spread:.3f} MHz",
                    fontsize=8.5)
        a.set_xlim(-12, 12)
        a.grid(alpha=0.25)
        print(f"    {npts}: {on_line} on the line, width scatter {spread:.4f} MHz")
    ax[0].set_ylabel("signal (normalised)")

    _footer(fig, "a 5.41 MHz line at the measured noise law, sampled two ways, "
                 "width scatter over 40 fits. "
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_sampling_the_line.png")


def fig_resampling_2():
    """Jackknife leave-one-out estimates: smooth for the mean, a step for the median."""
    rng = np.random.default_rng(20260826)
    n = 15
    x = np.sort(rng.normal(0.0, 1.0, n))
    full_mean, full_median = x.mean(), np.median(x)
    loo_mean = np.array([np.delete(x, i).mean() for i in range(n)])
    loo_median = np.array([np.median(np.delete(x, i)) for i in range(n)])

    fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0))
    idx = np.arange(1, n + 1)
    ax[0].plot(idx, loo_mean, "o-", ms=5, color=ACCENT)
    ax[0].axhline(full_mean, color=INK, ls="--", lw=1.0)
    ax[0].text(1, full_mean + 0.02, "full-sample mean", fontsize=7.5, color=INK)
    ax[0].set_xlabel("observation left out (sorted rank)")
    ax[0].set_ylabel("leave-one-out mean")
    ax[0].set_title("(a) mean: a smooth trend", fontsize=9)
    ax[0].grid(alpha=0.25)

    ax[1].plot(idx, loo_median, "o-", ms=5, color=ACCENT2)
    ax[1].axhline(full_median, color=INK, ls="--", lw=1.0)
    ax[1].text(1, full_median + 0.03, "full-sample median", fontsize=7.5, color=INK)
    ax[1].set_xlabel("observation left out (sorted rank)")
    ax[1].set_ylabel("leave-one-out median")
    ax[1].set_title("(b) median: flat, then a step", fontsize=9)
    ax[1].grid(alpha=0.25)

    se_mean = np.sqrt(n - 1) * np.std(loo_mean, ddof=0)
    se_median = np.sqrt(n - 1) * np.std(loo_median, ddof=0)
    _footer(fig, f"synthetic n={n} sample, fixed seed. jackknife SE: mean "
                 f"{se_mean:.3f}, median {se_median:.3f}. "
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_resampling_2.png")

def fig_correlated_samples_and_effective_sample_size():
    """A naive significance falls toward the measured autocorrelation time's true value."""
    taus_pts = np.array([1.0, 2.0, 3.79, 8.0])
    tau = np.linspace(1.0, 8.0, 400)
    sigma = 4.0 / np.sqrt(tau)
    sigma_pts = 4.0 / np.sqrt(taus_pts)

    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    ax.plot(tau, sigma, color=ACCENT, lw=1.6)
    ax.plot(taus_pts, sigma_pts, "o", ms=6, color=ACCENT2, zorder=3)
    labels = ["naive, tau=1", "tau=2", "tau=3.79\n(campaign median)", "tau=8"]
    offsets = [(6, 4), (6, 4), (6, -22), (6, 4)]
    for t, s, lab, off in zip(taus_pts, sigma_pts, labels, offsets):
        ax.annotate(f"{lab}\n{s:.2f} sigma", (t, s), textcoords="offset points",
                    xytext=off, fontsize=7.5, color=INK)
    ax.set_xlabel("autocorrelation time tau (samples)")
    ax.set_ylabel("apparent significance (sigma)")
    ax.set_title("A naive 4-sigma claim, corrected for tau", fontsize=9)
    ax.set_ylim(1.0, 4.6)
    ax.grid(alpha=0.25)

    _footer(fig, "closed form sigma = 4.0/sqrt(tau), this page's own Try it tau "
                 "values (1, 2, 3.79, 8). "
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_correlated_samples_and_effective_sample_size.png")

def fig_pooling_across_groups():
    """The Try it bound on a shared slope: an agreeing long lever tightens it, a disagreeing one widens it again."""
    rng = np.random.default_rng(20260826)

    def bound_on_shared_slope(groups):
        grid = np.linspace(0.0, 4.0, 2001)
        chi2 = np.zeros_like(grid)
        for i, s in enumerate(grid):
            total = 0.0
            for x, y, sd in groups:
                r = y - s * x
                total += (((r - r.mean()) / sd) ** 2).sum()
            chi2[i] = total
        d = chi2 - chi2.min()
        keep = grid >= grid[d.argmin()]
        return float(np.interp(2.706, d[keep], grid[keep]))

    def make(slope, xmax, n=40, sd=1.0):
        x = np.linspace(0.0, xmax, n)
        return x, slope * x + rng.normal(0, sd, n), sd

    short = make(1.0, 1.0)
    long_agree = make(1.0, 3.0)
    long_differ = make(2.0, 3.0)
    bounds = [bound_on_shared_slope([short]),
              bound_on_shared_slope([short, long_agree]),
              bound_on_shared_slope([short, long_differ])]

    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    labels = ["short alone", "+ agreeing\nlong lever", "+ disagreeing\nlong lever"]
    colors = [ACCENT, ACCENT3, ACCENT2]
    bars = ax.bar(labels, bounds, color=colors, width=0.55)
    for b, v in zip(bars, bounds):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.04, f"{v:.2f}",
                ha="center", fontsize=7.5, color=INK)
    ax.set_ylabel("95% bound on shared slope")
    ax.set_title("Adding data can loosen a shared-parameter bound", fontsize=9)
    ax.grid(alpha=0.25, axis="y")

    _footer(fig, "synthetic groups, fixed seed, reproducing this page's Try it "
                 "calculation. Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_pooling_across_groups.png")

def fig_optimiser_convergence():
    """Two BFGS runs on the same function, both converged, in different minima."""
    from scipy.optimize import minimize

    def f(x):
        x = x[0]
        return (x ** 2 - 1.0) ** 2 + 0.3 * x

    warm = minimize(f, [1.0], method="BFGS")
    cold = minimize(f, [-4.0], method="BFGS")

    x = np.linspace(-2.5, 2.5, 600)
    y = (x ** 2 - 1.0) ** 2 + 0.3 * x

    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    ax.plot(x, y, color=INK, lw=1.4)
    ax.plot(warm.x[0], warm.fun, "o", ms=7, color=ACCENT, zorder=3)
    ax.plot(cold.x[0], cold.fun, "o", ms=7, color=ACCENT2, zorder=3)
    ax.annotate(f"warm start, x0=1.0\nconverged={warm.success}, lands at x={warm.x[0]:.2f}",
                (warm.x[0], warm.fun), xytext=(0.3, 8.0), fontsize=7.5, color=ACCENT,
                arrowprops=dict(arrowstyle="->", color=ACCENT, lw=0.8))
    ax.annotate(f"cold start, x0=-4.0\nconverged={cold.success}, lands at x={cold.x[0]:.2f}",
                (cold.x[0], cold.fun), xytext=(-2.35, 9.5), fontsize=7.5, color=ACCENT2,
                arrowprops=dict(arrowstyle="->", color=ACCENT2, lw=0.8))
    ax.set_xlabel("x (dimensionless)")
    ax.set_ylabel("f(x) (dimensionless)")
    ax.set_title("Both runs report convergence, to different minima", fontsize=9)
    ax.grid(alpha=0.25)

    _footer(fig, f"f(x)=(x^2-1)^2+0.3x, this page's own Try it snippet. warm-cold "
                 f"gap {warm.fun - cold.fun:.3f}. "
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_optimiser_convergence.png")

def fig_grids_and_discretisation():
    """A half-maximum-read Lorentzian width departs from truth as the grid coarsens, this page's own snippet."""
    grid_steps_per_kernel = 12  # rb5s6s/lineshape.py's GRID_STEPS_PER_KERNEL

    def lorentzian(nu, fwhm):
        return 1.0 / (1 + (2 * nu / fwhm) ** 2)

    def measured_fwhm(points_per_width, true_fwhm=1.0, phase=0.31):
        step = true_fwhm / points_per_width
        n = int(np.ceil(8 * true_fwhm / step)) + 2
        nu = step * (np.arange(-n, n + 1) + phase)
        y = lorentzian(nu, true_fwhm)
        i_peak = np.argmax(y)
        half = 0.5 * y[i_peak]
        i = i_peak
        while y[i] >= half:
            i -= 1
        x_lo = nu[i] + (half - y[i]) * (nu[i + 1] - nu[i]) / (y[i + 1] - y[i])
        i = i_peak
        while y[i] >= half:
            i += 1
        x_hi = nu[i - 1] + (half - y[i - 1]) * (nu[i] - nu[i - 1]) / (y[i] - y[i - 1])
        return x_hi - x_lo

    pts = np.array([1.5, 2, 3, 4, 6, 8, 12, 20, 40, 200])
    dep = np.array([100.0 * (measured_fwhm(p) - 1.0) for p in pts])

    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    ax.semilogx(pts, dep, "o-", ms=5, color=ACCENT)
    i12 = int(np.argmin(np.abs(pts - grid_steps_per_kernel)))
    ax.plot(pts[i12], dep[i12], "o", ms=8, color=ACCENT2, zorder=3)
    ax.annotate("this repository's own\nconvolution grid, 12 pts/width",
                (pts[i12], dep[i12]), xytext=(15, dep[i12] + 8),
                textcoords="offset points", fontsize=7.5, color=ACCENT2,
                arrowprops=dict(arrowstyle="->", color=ACCENT2, lw=0.8))
    ax.set_xlabel("points sampled across the FWHM")
    ax.set_ylabel("departure from true FWHM (%)")
    ax.set_title("A half-maximum width read straight off the samples", fontsize=9)
    ax.grid(alpha=0.25, which="both")

    _footer(fig, "closed-form Lorentzian, this page's own measured_fwhm() snippet. "
                 "GRID_STEPS_PER_KERNEL=12 quoted by name from rb5s6s/lineshape.py. "
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_grids_and_discretisation.png")

def fig_compute_budgets_and_failure_modes_1():
    """Per-worker memory times worker count crosses the machine ceiling well before parallelism helps."""
    def jacobian_gb(n_points, n_params, overhead=3.0, dtype_bytes=8):
        bare_bytes = n_points * n_params * dtype_bytes
        return bare_bytes * overhead / 1e9

    n_points, n_params = 500_000, 200
    machine_ram_gb = 16.0
    per_worker_gb = jacobian_gb(n_points, n_params)
    workers = np.arange(1, 33)
    total_gb = per_worker_gb * workers
    max_workers = int(machine_ram_gb // per_worker_gb)

    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    ax.plot(workers, total_gb, color=ACCENT, lw=1.6)
    marks = np.array([1, 2, 4, 8, 10, 16, 32])
    ax.plot(marks, per_worker_gb * marks, "o", ms=5, color=ACCENT)
    ax.axhline(machine_ram_gb, color=ACCENT2, ls="--", lw=1.2)
    ax.text(1, machine_ram_gb + 2.0, "16 GB machine ceiling", fontsize=7.5, color=ACCENT2)
    ax.axvline(max_workers, color=INK, ls=":", lw=1.0)
    ax.text(max_workers + 0.5, 4, f"{max_workers} workers max\n({per_worker_gb:.1f} GB each)",
            fontsize=7.5, color=INK)
    ax.set_xlabel("worker count")
    ax.set_ylabel("total resident memory (GB)")
    ax.set_title("500,000 points, 200 parameters per fit", fontsize=9)
    ax.grid(alpha=0.25)

    _footer(fig, "closed form, jacobian_gb() from this page's own Try it snippet. "
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_compute_budgets_and_failure_modes_1.png")

def fig_compute_budgets_and_failure_modes_2():
    """A seconds-long preflight check against the multi-hour run it protects from failing late."""
    preflight_s = 2.0          # a path-existence check, illustrative round number
    failed_run_s = 3.0 * 3600  # this page's own Lesson 44 three-hour permission error

    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    bars = ax.bar(["preflight check", "run without it\n(fails at hour 3)"],
                  [preflight_s, failed_run_s], color=[ACCENT, ACCENT2], width=0.55)
    ax.set_yscale("log")
    ax.set_ylabel("wall-clock cost (seconds, log scale)")
    ax.set_title("Lesson 44: fail in seconds, not after most of the wall time", fontsize=9)
    for b, v, txt in zip(bars, [preflight_s, failed_run_s],
                          [f"{preflight_s:.0f} s", "3 h = 10800 s"]):
        ax.text(b.get_x() + b.get_width() / 2, v * 1.3, txt, ha="center",
                fontsize=7.5, color=INK)
    ax.grid(alpha=0.25, axis="y", which="both")

    _footer(fig, "illustrative preflight cost, the 3-hour figure is this page's "
                 "own Lesson 44 permission-error example. "
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_compute_budgets_and_failure_modes_2.png")

def fig_resolution_enhancement_and_what_it_costs():
    """Word length and noise resolution grow at different rates as samples are averaged."""
    n = np.logspace(0, 3.2, 400)
    word_bits = np.log2(n)
    noise_bits = 0.5 * np.log2(n)

    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    ax.semilogx(n, word_bits, color=ACCENT, lw=1.6, label="word length: log2(N)")
    ax.semilogx(n, noise_bits, color=ACCENT2, lw=1.6, label="noise: 0.5 log2(N)")
    ax.plot([256, 256], [np.log2(256), 0.5 * np.log2(256)], color=INK, lw=0.8, ls=":")
    ax.plot(256, np.log2(256), "o", ms=6, color=ACCENT, zorder=3)
    ax.plot(256, 0.5 * np.log2(256), "o", ms=6, color=ACCENT2, zorder=3)
    ax.text(280, np.log2(256) + 0.15, "N=256: 8 bits", fontsize=7.5, color=ACCENT)
    ax.text(280, 0.5 * np.log2(256) - 0.5, "N=256: 4 bits", fontsize=7.5, color=ACCENT2)
    ax.set_xlabel("averaged samples N (dimensionless)")
    ax.set_ylabel("bits gained (dimensionless)")
    ax.set_title("Reading word length for noise doubles the claimed gain", fontsize=9)
    ax.legend(fontsize=7.5, frameon=False, loc="upper left")
    ax.grid(alpha=0.25, which="both")

    _footer(fig, "closed form, log2(N) and 0.5*log2(N). "
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_resolution_enhancement_and_what_it_costs.png")

def fig_vapour_density_and_temperature():
    """How steeply the Rb vapour density rises with temperature, and the pilot's factor-3.2 uncertainty band."""
    from rb5s6s.density import number_density_cm3
    t_c = np.linspace(70.0, 140.0, 400)
    n = number_density_cm3(t_c)
    n_lo, n_hi = number_density_cm3(110.0), number_density_cm3(130.0)
    ratio = n_hi / n_lo

    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    ax.semilogy(t_c, n, lw=1.6, color=ACCENT)
    ax.axvspan(110, 130, color="0.88", zorder=0)
    ax.text(111, n.min() * 1.3, "pilot range\n110-130 C", fontsize=7.5,
            color=INK, va="bottom")
    ax.plot([110, 130], [n_lo, n_hi], "o", ms=5, color=ACCENT2, zorder=3)
    ax.annotate(f"factor {ratio:.1f} in density\nacross the pilot range",
                xy=(122, number_density_cm3(122.0)), xytext=(78, n_hi * 0.85),
                fontsize=7.5, color=INK,
                arrowprops=dict(arrowstyle="->", color=INK, lw=0.8))
    ax.set_xlabel("cell temperature (deg C)")
    ax.set_ylabel("Rb number density (cm^-3)")
    ax.set_title("Vapour density against cell temperature", fontsize=9)
    ax.grid(alpha=0.25, which="both")
    _footer(fig, "rb5s6s.density.number_density_cm3, closed form, Nesmeyanov/Steck correlation.\n"
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_vapour_density_and_temperature.png")

def fig_sweep_rate_and_detection_lag():
    """A fixed detector time constant inflates width and forges skew, and skew grows faster with sweep rate."""
    def gaussian(x, s):
        y = np.exp(-0.5 * (x / s) ** 2); return y / trapezoid(y, x)

    def causal_exp(x, s):
        y = np.where(x >= 0, np.exp(-x / s), 0.0); return y / trapezoid(y, x)

    def fwhm(x, y):
        a = x[y >= y.max() / 2.0]; return a[-1] - a[0]

    def skew(x, y):
        p = y / trapezoid(y, x); m = trapezoid(x * p, x)
        v = trapezoid((x - m) ** 2 * p, x)
        return trapezoid((x - m) ** 3 * p, x) / v ** 1.5

    dx = 0.01
    x = np.arange(-60.0, 60.0, dx)
    true_line = gaussian(x, 1.0)
    tau_ms = 0.25
    rates = np.array([1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 7.0, 10.0])
    traces = [np.convolve(true_line, causal_exp(x, tau_ms * r), mode="same") * dx
              for r in rates]
    widths = np.array([fwhm(x, t) for t in traces])
    skews = np.array([skew(x, t) for t in traces])

    fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0))
    ax[0].plot(x, true_line, color=INK, lw=1.0, label="true line, symmetric")
    ax[0].plot(x, traces[0], color=ACCENT, lw=1.4, label="1 MHz/ms sweep")
    ax[0].plot(x, traces[5], color=ACCENT2, lw=1.4, label="5 MHz/ms sweep")
    ax[0].set_xlim(-6, 10)
    ax[0].set_xlabel("detuning (MHz)")
    ax[0].set_ylabel("signal (normalised)")
    ax[0].set_title("(a) symmetric line, convolved", fontsize=9)
    ax[0].legend(fontsize=7.5, frameon=False)
    ax[0].grid(alpha=0.25)

    # One axis, both series as growth relative to the slowest sweep, so the
    # claim in the title is the thing the curves show.
    rel_w = (widths - widths[0]) / widths[0]
    rel_s = (skews - skews[0]) / max(skews[0], 1e-9)
    ax[1].plot(rates, rel_w / rel_w[-1], "o-", color=ACCENT, ms=4,
               label="excess width, normalised")
    ax[1].plot(rates, rel_s / rel_s[-1], "s-", color=ACCENT2, ms=4,
               label="skew, normalised")
    ax[1].set_xlabel("sweep rate (MHz per ms)")
    ax[1].set_ylabel("growth relative to the fastest sweep")
    ax[1].set_title("(b) skew outruns the width", fontsize=9)
    ax[1].legend(fontsize=7.5, frameon=False)
    ax[1].grid(alpha=0.25)

    _footer(fig, "synthetic Gaussian line convolved with a causal exponential kernel, tau=0.25 ms "
                 "(this page's Try-it snippet).\nRebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_sweep_rate_and_detection_lag.png")

def fig_digitisation_and_dynamic_range():
    """Codes spanned at the dim and bright ends of a nine-fold power ladder, at three digitiser bit depths."""
    bits = np.array([8, 12, 14])
    span = 81.0
    top = 0.8 * 2.0 ** bits
    dim = top / span

    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    x = np.arange(len(bits))
    w = 0.35
    ax.bar(x - w / 2, dim, width=w, color=ACCENT2, label="dimmest rung")
    ax.bar(x + w / 2, top, width=w, color=ACCENT, label="brightest rung")
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{b}-bit" for b in bits])
    ax.set_ylabel("digitiser codes spanned")
    ax.set_title("Codes at each end of a 9x power ladder", fontsize=9)
    for xi, d, t in zip(x, dim, top):
        ax.text(xi - w / 2, d * 1.2, f"{d:.1f}", ha="center", fontsize=7.5, color=INK)
        ax.text(xi + w / 2, t * 1.2, f"{t:.0f}", ha="center", fontsize=7.5, color=INK)
    ax.axhline(30, color=INK, ls=":", lw=1.0)
    ax.text(0.05, 34, "rule-of-thumb floor, 30 codes", fontsize=7.5, color=INK,
            transform=ax.get_yaxis_transform())
    ax.legend(fontsize=7.5, frameon=False)
    ax.grid(alpha=0.25, axis="y", which="both")
    _footer(fig, "arithmetic from this page's Try-it snippet: 9x power ladder, span=81, "
                 "80% headroom.\nRebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_digitisation_and_dynamic_range.png")

def fig_photon_counting():
    """Where the electronic noise floor stops dominating over shot noise, from the median committed noise law."""
    # median a_V and b_V across the 32 committed DIAGNOSTIC rows of results/noise_model.csv
    A_V_MEDIAN_V = 2.975e-3
    B_V_MEDIAN = 1.004e-3
    v_star = A_V_MEDIAN_V ** 2 / B_V_MEDIAN

    v = np.linspace(1e-4, 5 * v_star, 500)
    sigma_analog = np.sqrt(A_V_MEDIAN_V ** 2 + B_V_MEDIAN * v)
    sigma_shot = np.sqrt(B_V_MEDIAN * v)

    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    ax.plot(v * 1e3, sigma_analog * 1e3, color=ACCENT, lw=1.6,
            label="analogue chain, sqrt(a^2 + bV)")
    ax.plot(v * 1e3, sigma_shot * 1e3, color=ACCENT2, lw=1.6, ls="--",
            label="shot noise alone, sqrt(bV)")
    ax.axvline(v_star * 1e3, color=INK, ls=":", lw=1.0)
    ax.annotate(f"V* = {v_star * 1e3:.2f} mV", xy=(v_star * 1e3, sigma_shot[-1] * 1e3 * 0.3),
                xytext=(v_star * 1e3 * 1.5, sigma_shot[-1] * 1e3 * 0.15),
                fontsize=7.5, color=INK,
                arrowprops=dict(arrowstyle="->", color=INK, lw=0.8))
    ax.set_xlabel("signal level V (mV)")
    ax.set_ylabel("noise sigma (mV)")
    ax.set_title("Analogue noise against a shot-noise floor", fontsize=9)
    ax.legend(fontsize=7.5, frameon=False, loc="upper left")
    ax.grid(alpha=0.25)
    _footer(fig, "median a_V=2.975e-3 V, b_V=1.004e-3 V, quoted from results/noise_model.csv "
                 "(32 rows).\nRebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_photon_counting.png")

def fig_guided_atoms_and_nanofibres_1():
    """Where the atom sits relative to the guided intensity in each fibre geometry."""
    r = np.linspace(0, 4, 400)
    hollow = np.exp(-(r / 0.55) ** 2)
    glass_r, decay, edge_val = 1.0, 0.9, 0.7
    tail = np.where(r <= glass_r, 1.0 - (1.0 - edge_val) * (r / glass_r) ** 2,
                    edge_val * np.exp(-(r - glass_r) / decay))

    fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0))
    ax[0].plot(r, hollow, color=ACCENT, lw=1.6)
    ax[0].axvline(1.0, color=INK, lw=0.8, ls="--")
    ax[0].fill_between(r, 0, hollow, where=(r <= 1.0), color=ACCENT, alpha=0.12)
    ax[0].plot(0.15, np.exp(-(0.15 / 0.55) ** 2), "o", ms=7, color=ACCENT2, zorder=5)
    ax[0].text(0.35, 0.80, "atom, inside\nthe guided core", fontsize=7.5, color=INK)
    ax[0].text(1.05, 0.05, "hollow wall", fontsize=7, color=INK, rotation=90, va="bottom")
    ax[0].set_xlabel("distance from axis (core radii)")
    ax[0].set_ylabel("mode intensity (normalised)")
    ax[0].set_title("(a) hollow core: atom in the light", fontsize=9)
    ax[0].grid(alpha=0.25)

    ax[1].plot(r, tail, color=ACCENT3, lw=1.6)
    ax[1].axvline(glass_r, color=INK, lw=0.8, ls="--")
    ax[1].fill_between(r, 0, tail, where=(r >= glass_r), color=ACCENT3, alpha=0.12)
    atom_r = glass_r + 0.7
    atom_y = edge_val * np.exp(-(atom_r - glass_r) / decay)
    ax[1].plot(atom_r, atom_y, "o", ms=7, color=ACCENT2, zorder=5)
    ax[1].text(atom_r + 0.1, atom_y + 0.08,
               "atom, in the\nevanescent tail", fontsize=7.5, color=INK)
    ax[1].text(0.55, 0.05, "glass", fontsize=7, color=INK)
    ax[1].set_xlabel("distance from axis (glass radii)")
    ax[1].set_title("(b) nanofibre: atom outside the glass", fontsize=9)
    ax[1].grid(alpha=0.25)

    _footer(fig, "closed-form illustrative mode profiles, no fitted data. "
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_guided_atoms_and_nanofibres_1.png")

def fig_guided_atoms_and_nanofibres_2():
    """Drive power for the same effective intensity: milliwatts in the cell against microwatts in the fibre mode."""
    # READ from results/onf_candidate.csv, not retyped. These were hardcoded as
    # 6.784e7 and 0.50 um^2 with a comment saying they were quoted from that
    # file. The area moved to a solved value in the 2026-08-28 wave and this
    # figure kept drawing the assumption, which is the drawn-number-is-a-new-copy
    # class on a wiki surface.
    #
    # It takes the STARK area, because the quantity being drawn is the power
    # that reaches a given light-shift-equivalent intensity.
    _oc = {x["quantity"]: x["value"] for x in
            csv.DictReader(open(Path(__file__).resolve().parents[1]
                                / "results" / "onf_candidate.csv"))}
    INTENSITY_CELL_EFF_WM2 = float(_oc["intensity_cell_eff"])
    CELL_POWER_MW = 225.0
    MODE_AREA_EFF_UM2 = float(_oc["mode_area_stark"])
    onf_power_uw = INTENSITY_CELL_EFF_WM2 * (MODE_AREA_EFF_UM2 * 1e-12) * 1e6

    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    labels = ["vapour cell", f"nanofibre mode\n({MODE_AREA_EFF_UM2:.2f} um^2)"]
    powers_mw = [CELL_POWER_MW, onf_power_uw / 1000.0]
    bars = ax.bar(labels, powers_mw, color=[ACCENT, ACCENT2], width=0.5)
    ax.set_yscale("log")
    ax.set_ylabel("drive power (mW)")
    ax.set_title("Same effective intensity, very different power", fontsize=9)
    tags = [f"{CELL_POWER_MW:.0f} mW", f"{onf_power_uw:.1f} uW"]
    for b, tag in zip(bars, tags):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() * 1.3, tag,
                ha="center", fontsize=7.5, color=INK)
    ax.grid(alpha=0.25, axis="y", which="both")
    _footer(fig, f"intensity_cell_eff={INTENSITY_CELL_EFF_WM2:.3e} W/m^2 at 225 mW, "
                 f"mode_area_stark={MODE_AREA_EFF_UM2:.2f} um^2 "
                 "(results/onf_candidate.csv).\nRebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_guided_atoms_and_nanofibres_2.png")

def fig_selection_rules():
    """How a retroreflector angle mismatch reopens the otherwise-forbidden rank-1 leakage channel."""
    from rb5s6s.polarisation import rank_one_leak_rate
    theta = np.linspace(0.0, 10.0, 300)
    rate = np.array([rank_one_leak_rate(t) for t in theta])
    marked = rank_one_leak_rate(5.0)

    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    ax.plot(theta, rate, color=ACCENT, lw=1.6)
    ax.plot(5.0, marked, "o", ms=6, color=ACCENT2, zorder=5)
    ax.annotate(f"{marked:.1e} at 5 deg", xy=(5.0, marked),
                xytext=(5.8, marked * 1.35),
                fontsize=7.5, color=INK,
                arrowprops=dict(arrowstyle="->", color=INK, lw=0.8))
    ax.set_xlabel("retroreflector angle mismatch (degrees)")
    ax.set_ylabel("rank-1 leakage rate (fraction of the line)")
    ax.set_title("Rank-1 leakage against retro angle mismatch", fontsize=9)
    ax.grid(alpha=0.25)
    _footer(fig, "rb5s6s.polarisation.rank_one_leak_rate, closed form, T=130 C, 87Rb.\n"
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_selection_rules.png")

def fig_heavy_tailed_models_1():
    """Student-t densities departing from the Gaussian, and the downweight that produces it."""
    from scipy.stats import t as student_t
    r = np.linspace(-6, 6, 800)
    gauss = np.exp(-r**2 / 2) / np.sqrt(2 * np.pi)
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0))

    ax[0].plot(r, gauss, color=INK, lw=1.4, ls="--", label="Gaussian")
    for nu, c in ((10, ACCENT3), (3, ACCENT), (1, ACCENT2)):
        ax[0].plot(r, student_t.pdf(r, nu), lw=1.4, color=c,
                   label=f"Student-t, $\\nu={nu}$")
    ax[0].set_yscale("log")
    ax[0].set_ylim(1e-5, 1.0)
    ax[0].set_xlabel("standardized residual $r$")
    ax[0].set_ylabel("probability density (log scale)")
    ax[0].set_title("(a) heavier tails as $\\nu$ shrinks", fontsize=9)
    ax[0].legend(fontsize=7.5, frameon=False)
    ax[0].grid(alpha=0.25, which="both")

    rr = np.linspace(0, 6, 400)
    for nu, c in ((10, ACCENT3), (3, ACCENT), (1, ACCENT2)):
        w = nu / (nu + rr**2)
        ax[1].plot(rr, w, lw=1.4, color=c, label=f"$\\nu={nu}$")
    ax[1].set_xlabel("standardized residual $r$")
    ax[1].set_ylabel("downweight, normalised to 1 at $r=0$")
    ax[1].set_title("(b) the implied per-point downweight", fontsize=9)
    ax[1].legend(fontsize=7.5, frameon=False)
    ax[1].grid(alpha=0.25)

    _footer(fig, "closed form, no data. "
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_heavy_tailed_models_1.png")

def fig_heavy_tailed_models_2():
    """The clean and contaminated samples from the worked example, with fitted Student-t densities."""
    from scipy.optimize import minimize
    from scipy.stats import t as student_t

    def fit_student_t(sample, dof_bounds=(0.5, 100.0)):
        def neg_log_lik(p):
            scale, dof = p
            return (-student_t.logpdf(sample / scale, dof).sum()
                     + sample.size * np.log(scale))
        fit = minimize(neg_log_lik, x0=[sample.std(), 20.0], method="L-BFGS-B",
                        bounds=[(1e-3, None), dof_bounds])
        return fit.x

    rng = np.random.default_rng(20260826)
    n, frac, blowup = 400, 0.06, 12.0
    clean = rng.standard_normal(n)
    contaminated = clean.copy()
    n_out = int(round(frac * n))
    idx = rng.choice(n, size=n_out, replace=False)
    contaminated[idx] = rng.standard_normal(n_out) * blowup

    fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0))
    for a, sample, c, title in ((ax[0], clean, ACCENT, "(a) clean Gaussian sample"),
                                (ax[1], contaminated, ACCENT2,
                                 "(b) 6% of points blown up by 12x")):
        scale, dof = fit_student_t(sample)
        lim = max(4.5, np.abs(sample).max() * 1.05)
        x = np.linspace(-lim, lim, 1000)
        a.hist(sample, bins=40, density=True, color=c, alpha=0.55, edgecolor="none")
        a.plot(x, student_t.pdf(x / scale, dof) / scale, color=INK, lw=1.4)
        a.set_yscale("log")
        a.set_ylim(1e-4, 1.0)
        a.set_xlim(-lim, lim)
        a.set_xlabel("sample value")
        a.set_title(title, fontsize=9)
        a.text(0.97, 0.92, f"fitted $\\nu = {dof:.1f}$", ha="right", va="top",
               transform=a.transAxes, fontsize=7.5, color=INK)
        a.grid(alpha=0.25, which="both")
    ax[0].set_ylabel("probability density (log scale)")

    _footer(fig, "synthetic samples, fixed seed. "
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_heavy_tailed_models_2.png")

def fig_weighted_least_squares():
    """Where an electronic noise floor and shot noise trade off in a detector's variance law."""
    a, b = 1.2, 0.6                      # illustrative detector: floor a, shot coeff b
    v = np.linspace(0, 10, 400)
    floor = np.full_like(v, a**2)
    shot = b * v
    total = a**2 + b * v
    v_star = a**2 / b

    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    ax.plot(v, total, color=INK, lw=1.6, label=r"$\sigma^2(V) = a^2 + bV$")
    ax.plot(v, floor, color=ACCENT, lw=1.2, ls="--", label=r"floor $a^2$")
    ax.plot(v, shot, color=ACCENT2, lw=1.2, ls="--", label=r"shot term $bV$")
    ax.axvline(v_star, color=INK, lw=1.0, ls=":")
    ax.text(v_star + 0.2, 1.0, f"crossover\n$V^* = a^2/b = {v_star:.1f}$",
            fontsize=7.5, color=INK)
    ax.set_xlabel("signal level $V$ (arbitrary units)")
    ax.set_ylabel(r"variance $\sigma^2(V)$ (arbitrary units)")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, total.max() * 1.05)
    ax.legend(fontsize=7.5, frameon=False, loc="upper left")
    ax.grid(alpha=0.25)

    _footer(fig, "illustrative detector, closed form, no data. "
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_weighted_least_squares.png")

def fig_robust_fitting():
    """Three M-estimator shapes: an unbounded loss, a linear-tailed one, and a weight redescending to zero."""
    k, c = 1.345, 4.685
    r = np.linspace(0, 5, 400)
    ols = 0.5 * r**2
    huber = np.where(r <= k, 0.5 * r**2, k * r - 0.5 * k**2)
    tukey_w = np.where(r <= c, (1 - (r / c)**2)**2, 0.0)

    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    l1, = ax.plot(r, ols, color=ACCENT, lw=1.6,
                  label="ordinary squares, loss (quadratic)")
    l2, = ax.plot(r, huber, color=ACCENT2, lw=1.6,
                  label=f"Huber, loss (linear tail beyond k={k})")
    ax.axvline(k, color=ACCENT2, lw=0.8, ls=":")
    ax.text(k + 0.05, 10.5, f"$k={k}$", fontsize=7.5, color=ACCENT2)
    ax.set_xlabel("standardized residual $|r|$")
    ax.set_ylabel(r"loss $\rho(r)$ (dimensionless)")
    ax.set_xlim(0, 5)
    ax.set_ylim(0, 13)
    ax.grid(alpha=0.25)

    ax2 = ax.twinx()
    l3, = ax2.plot(r, tukey_w, color=ACCENT3, lw=1.6,
                   label=f"Tukey biweight, weight (redescends to 0 beyond c={c})")
    ax2.axvline(c, color=ACCENT3, lw=0.8, ls=":")
    ax2.text(c - 0.85, 0.90, f"$c={c}$", fontsize=7.5, color=ACCENT3)
    ax2.set_ylabel("Tukey weight $w(r)$ (dimensionless)")
    ax2.set_ylim(0, 1.05)

    ax.legend(handles=[l1, l2, l3], fontsize=7.5, frameon=False, loc="upper left")
    _footer(fig, "closed form and no data, tuning constants from Huber (1981) "
                 "and Beaton and Tukey (1974).\n"
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_robust_fitting.png")

def fig_profile_likelihood():
    """A chi-squared profile pinned at a physical boundary stays one-sided; a quadratic approximation from the same curvature does not."""
    obs0 = -0.3                       # a downward fluctuation below the boundary
    chi2_min = obs0**2
    curvature = 1.2                   # second derivative of (theta^2-obs0)^2 at theta=0

    th_pos = np.linspace(0.0, 1.3, 400)
    profile = (th_pos**2 - obs0)**2 - chi2_min
    th_all = np.linspace(-1.35, 1.35, 400)
    quad = 0.5 * curvature * th_all**2

    coeffs = [1.0, 0.0, -2.0 * obs0, 0.0, -1.0]
    roots = np.roots(coeffs)
    bound_true = float(np.min(roots[(np.abs(roots.imag) < 1e-9) & (roots.real > 0)].real))
    bound_quad = np.sqrt(2.0 / curvature)

    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    ax.axvspan(-1.4, 0.0, color="0.92", zorder=0)
    ax.plot(th_pos, profile, color=ACCENT, lw=1.8,
            label=r"profile (physical, $\theta \geq 0$)")
    ax.plot(th_all, quad, color=ACCENT2, lw=1.4, ls="--",
            label="quadratic approximation")
    ax.axhline(1.0, color=INK, lw=0.8, ls=":")
    ax.axvline(bound_true, color=ACCENT, lw=0.8, ls=":")
    ax.axvline(-bound_quad, color=ACCENT2, lw=0.8, ls=":")
    ax.axvline(bound_quad, color=ACCENT2, lw=0.8, ls=":")
    ax.text(0.03, 1.10, r"$\Delta\chi^2 = 1$", fontsize=7.5, color=INK)
    ax.text(bound_true + 0.04, 0.15, f"one-sided\nbound {bound_true:.2f}",
            fontsize=7.5, color=ACCENT)
    ax.text(-1.38, 3.5, "unphysical\n($\\theta<0$)", fontsize=7.5, color="0.45")
    ax.text(bound_quad + 0.04, 2.6, f"symmetric\ninterval $\\pm${bound_quad:.2f}",
            fontsize=7.5, color=ACCENT2)
    ax.set_xlabel(r"parameter $\theta$ (arbitrary units)")
    ax.set_ylabel(r"$\Delta\chi^2$")
    ax.set_xlim(-1.4, 1.4)
    ax.set_ylim(0, 4.2)
    ax.legend(fontsize=7.5, frameon=False, loc="upper center")
    ax.grid(alpha=0.25)

    _footer(fig, "synthetic chi-squared profile, closed form, no data. "
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_profile_likelihood.png")

def fig_monte_carlo_methods():
    """The 1/sqrt(N) convergence of a Monte Carlo integral, at the sample sizes the worked example uses."""
    rng = np.random.default_rng(20260826)
    true_value = 2.0
    sizes = np.array([100, 1_000, 10_000, 100_000, 1_000_000])
    budget = 20_000_000
    rms = []
    for n in sizes:
        reps = max(30, min(4000, budget // n))
        x = rng.uniform(0.0, np.pi, size=(reps, n))
        estimate = np.pi * np.mean(np.sin(x), axis=1)
        rms.append(float(np.sqrt(np.mean((estimate - true_value)**2))))
    rms = np.array(rms)
    ref = rms[0] * np.sqrt(sizes[0] / sizes)

    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    ax.loglog(sizes, rms, "o-", ms=5, lw=1.4, color=ACCENT,
              label="Monte Carlo estimate of $\\int_0^\\pi \\sin(x)\\,dx$")
    ax.loglog(sizes, ref, "--", lw=1.2, color=INK, label=r"$1/\sqrt{N}$ reference")
    ax.text(3e3, ref[1] * 1.15, r"slope $-1/2$", fontsize=7.5, color=INK)
    ax.set_xlabel("sample size $N$ (dimensionless)")
    ax.set_ylabel("RMS error (dimensionless)")
    ax.legend(fontsize=7.5, frameon=False)
    ax.grid(alpha=0.25, which="both")

    _footer(fig, "synthetic run, fixed seed, same worked example as the page's Try it "
                 "snippet.\nRebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_monte_carlo_methods.png")

def fig_resampling_1():
    """The parametric-bootstrap null for the largest Cook's distance, against the textbook rule of thumb it replaces."""
    rng = np.random.default_rng(20260826)
    x = np.array([1.0, 1.6, 2.2, 4.0])
    sigma = np.full_like(x, 0.05)
    n, p = len(x), 2
    X = np.column_stack([np.ones(n), x])
    w = 1.0 / sigma**2
    M = np.linalg.inv((X.T * w) @ X) @ (X.T * w)
    h = np.diag(X @ M)
    dof = n - p
    true_line = 0.30 + 0.05 * x

    B = 20000
    Y = true_line[None, :] + rng.normal(0.0, sigma[None, :], size=(B, n))
    resid = Y - (X @ (M @ Y.T)).T
    s2 = (w * resid**2).sum(axis=1) / dof
    e2 = (w * resid**2) / (s2[:, None] * (1 - h)[None, :])
    max_d = (e2 * h[None, :] / (p * (1 - h)[None, :])).max(axis=1)
    p95 = np.percentile(max_d, 95)
    rule = 4.0 / n

    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    ax.hist(max_d, bins=60, color=ACCENT, alpha=0.6, edgecolor="none",
            label=f"{B} parametric-bootstrap datasets")
    ax.axvline(p95, color=INK, lw=1.4, label=f"simulated 95th pct = {p95:.2f}")
    ax.axvline(rule, color=ACCENT2, lw=1.4, ls="--", label=f"textbook 4/n = {rule:.2f}")
    ax.set_xlabel("largest Cook's distance across the 4 points")
    ax.set_ylabel("count")
    ax.legend(fontsize=7.5, frameon=False)
    ax.grid(alpha=0.25)

    _footer(fig, "synthetic run, fixed seed, same design as the page's Try it snippet.\n"
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_resampling_1.png")

def fig_preregistration():
    """A null test's false-positive rate landing on its own stated threshold."""
    from scipy.stats import norm

    rng = np.random.default_rng(7)
    n_points, n_trials, alpha = 200, 20000, 0.05
    z_crit = norm.ppf(1 - alpha / 2)

    noise = rng.standard_normal((n_trials, n_points))
    z = noise.mean(axis=1) / (noise.std(axis=1, ddof=1) / np.sqrt(n_points))
    rate = float(np.mean(np.abs(z) > z_crit))

    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    ax.hist(z, bins=80, color=ACCENT, alpha=0.85, density=True,
            edgecolor="none", label=f"{n_trials} null trials")
    ax.axvline(z_crit, color=ACCENT2, lw=1.4, ls="--")
    ax.axvline(-z_crit, color=ACCENT2, lw=1.4, ls="--")
    ax.text(z_crit + 0.15, 0.05, f"z_crit = {z_crit:.3f}\n(nominal {alpha:.0%})",
            fontsize=7.5, color=ACCENT2)
    ax.text(0.02, 0.95, f"claimed detection in {rate:.4f} of trials",
            transform=ax.transAxes, fontsize=7.5, color=INK, va="top")
    ax.set_xlabel("z-statistic (dimensionless)")
    ax.set_ylabel("probability density")
    ax.set_title(f"{n_points} points per trial, pure noise, no injected effect",
                 fontsize=9)
    ax.legend(fontsize=7.5, frameon=False, loc="upper right")
    ax.grid(alpha=0.25)

    _footer(fig, "reproduces the page's own Try It null-test snippet, "
                 "seed=7, 20000 trials.\n"
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_preregistration.png")

def fig_reversal_tests():
    """The half-sum and half-difference of a swept line isolate two systematics for free."""
    nu = np.linspace(-30, 30, 1201)
    line = lambda c: 1.0 / (1.0 + ((nu - c) / 2.7) ** 2)
    lag_shift, real_shift = 0.8, 0.5
    up, down = line(real_shift + lag_shift), line(real_shift - lag_shift)

    def centre(v):
        half = v.max() / 2
        i = np.nonzero(v > half)[0]
        lo = np.interp(half, [v[i[0] - 1], v[i[0]]], [nu[i[0] - 1], nu[i[0]]])
        hi = np.interp(half, [v[i[-1] + 1], v[i[-1]]], [nu[i[-1] + 1], nu[i[-1]]])
        return 0.5 * (lo + hi)

    c_up, c_down = centre(up), centre(down)
    mean = 0.5 * (c_up + c_down)
    diff = 0.5 * (c_up - c_down)

    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    ax.plot(nu, up, color=ACCENT, lw=1.4, label="sweep up")
    ax.plot(nu, down, color=ACCENT2, lw=1.4, label="sweep down")
    ax.axvline(c_up, color=ACCENT, ls=":", lw=1.0)
    ax.axvline(c_down, color=ACCENT2, ls=":", lw=1.0)
    ax.text(c_up + 0.3, 0.08, f"centre {c_up:+.3f}", fontsize=7.5, color=ACCENT)
    ax.text(c_down + 0.3, 0.18, f"centre {c_down:+.3f}", fontsize=7.5, color=ACCENT2)
    ax.text(0.02, 0.97,
            f"injected shift {real_shift:+.3f}, recovered mean {mean:+.3f}\n"
            f"injected lag {lag_shift:+.3f}, recovered diff {diff:+.3f}",
            transform=ax.transAxes, fontsize=7.5, color=INK, va="top")
    ax.set_xlabel("detuning (MHz)")
    ax.set_ylabel("signal (normalised)")
    ax.set_xlim(-6, 6)
    ax.set_ylim(0, 1.32)
    ax.legend(fontsize=7.5, frameon=False, loc="upper right")
    ax.grid(alpha=0.25)

    _footer(fig, "reproduces the page's own Try It code block, no fitted data.\n"
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_reversal_tests.png")

def fig_sensitivity_analysis_1():
    """Sobol indices recover a purely-interactive input's variance share a one-at-a-time sweep would miss."""
    def model(x1, x2, c):
        return x1 + c * x1 * x2

    def sobol_indices(c, n, seed=0):
        rng = np.random.default_rng(seed)
        a = rng.uniform(-1.0, 1.0, size=(n, 2))
        b = rng.uniform(-1.0, 1.0, size=(n, 2))
        ya = model(a[:, 0], a[:, 1], c)
        yb = model(b[:, 0], b[:, 1], c)
        var_y = np.concatenate([ya, yb]).var()
        s1, st = {}, {}
        for i, name in enumerate(("x1", "x2")):
            ab = a.copy()
            ab[:, i] = b[:, i]
            yab = model(ab[:, 0], ab[:, 1], c)
            s1[name] = 1.0 - np.mean((yb - yab) ** 2) / (2.0 * var_y)
            st[name] = np.mean((ya - yab) ** 2) / (2.0 * var_y)
        return s1, st

    c, n = 5.0, 200_000
    s1, st = sobol_indices(c, n)
    var_x = 1.0 / 3.0
    var_interaction = c ** 2 / 9.0
    var_total = var_x + var_interaction
    exact = {"S1 X1": var_x / var_total, "S1 X2": 0.0,
             "ST X1": 1.0, "ST X2": var_interaction / var_total}
    mc = {"S1 X1": s1["x1"], "S1 X2": s1["x2"],
          "ST X1": st["x1"], "ST X2": st["x2"]}

    labels = list(mc)
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    ax.bar(x - 0.18, [mc[k] for k in labels], width=0.36, color=ACCENT,
           label=f"Monte Carlo, N={n:,}")
    ax.bar(x + 0.18, [exact[k] for k in labels], width=0.36, color=ACCENT2,
           label="closed-form exact")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Sobol index (fraction of variance)")
    ax.set_title("Y = X1 + 5 X1 X2, X1, X2 iid Uniform(-1,1)", fontsize=9)
    ax.legend(fontsize=7.5, frameon=False)
    ax.grid(alpha=0.25, axis="y")

    _footer(fig, "reproduces the page's own Try It Saltelli/Jansen estimator, seed=0.\n"
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_sensitivity_analysis_1.png")

def fig_sensitivity_analysis_2():
    """Where the next campaign's projected precision actually gets its uncertainty from."""
    # Quoted from docs/plan/05_width-collision-amplitude.md's variance-based
    # sensitivity study of the projected next-campaign precision.
    SHARE_TOP_TEMPERATURE = 0.58
    SHARE_COLD_SPOT_LAG = 0.33
    SHARE_N_TEMPERATURE_BLOCKS = 0.002

    labels = ["top temperature\nreached", "cold-spot lag\n(unmeasured)",
              "number of\ntemperature blocks"]
    shares = [SHARE_TOP_TEMPERATURE, SHARE_COLD_SPOT_LAG,
              SHARE_N_TEMPERATURE_BLOCKS]
    colors = [ACCENT, ACCENT2, ACCENT3]

    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    y = np.arange(len(labels))
    ax.barh(y, shares, color=colors, height=0.55)
    for yi, s in zip(y, shares):
        ax.text(s + 0.015, yi, f"{s:.3f}", fontsize=7.5, color=INK, va="center")
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("share of variance (dimensionless)")
    ax.set_xlim(0, 0.7)
    ax.grid(alpha=0.25, axis="x")

    _footer(fig, "values quoted from docs/plan/05_width-collision-amplitude.md, "
                 "not recomputed here.\n"
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_sensitivity_analysis_2.png")

def fig_influence_diagnostics():
    """Leverage concentrates on a single far-out point in an uneven design."""
    x = np.array([1.0, 1.3, 1.7, 12.0])
    X = np.column_stack([np.ones_like(x), x])
    H = X @ np.linalg.inv(X.T @ X) @ X.T
    leverage = np.diag(H)
    n, p = X.shape

    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    colors = [ACCENT if h <= 0.9 else ACCENT2 for h in leverage]
    ax.bar([f"{xi:.1f}" for xi in x], leverage, color=colors, width=0.55)
    ax.axhline(p / n, color=INK, ls="--", lw=1.0)
    ax.text(0.02, p / n + 0.02, f"mean leverage p/n = {p / n:.3f}",
            fontsize=7.5, color=INK, transform=ax.get_yaxis_transform())
    ax.text(3, leverage[-1] - 0.08, "fit passes\nthrough it",
            fontsize=7.5, color="white", ha="center", va="top")
    ax.set_xlabel("design point x (arbitrary units)")
    ax.set_ylabel("leverage h_ii (dimensionless)")
    ax.set_xlim(-0.7, 3.7)
    ax.set_ylim(0, 1.05)
    ax.set_title(f"{n} points, {p} free parameters, "
                 f"sum h_ii = {leverage.sum():.3f}", fontsize=9)
    ax.grid(alpha=0.25, axis="y")

    _footer(fig, "reproduces the page's own Try It hat-matrix snippet. "
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_influence_diagnostics.png")

def fig_injection_recovery_1():
    """Measured interval coverage against its nominal level, with the trial count that bounds how much either could differ by chance."""
    # Quoted from results/kernel_worlds.csv: the width-injecting world, 500
    # preregistered trials.
    N_TRIALS = 500
    NOMINAL = 0.68
    MEASURED = 0.746
    se = np.sqrt(MEASURED * (1 - MEASURED) / N_TRIALS)
    se_nominal_band = np.sqrt(NOMINAL * (1 - NOMINAL) / N_TRIALS)

    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    ax.axhspan(NOMINAL - se_nominal_band, NOMINAL + se_nominal_band,
               color="0.90", zorder=0)
    ax.axhline(NOMINAL, color=INK, ls="--", lw=1.2, zorder=1)
    ax.errorbar([0], [MEASURED], yerr=[se], fmt="o", ms=8, color=ACCENT,
                capsize=4, lw=1.6, zorder=2)
    ax.text(0.08, NOMINAL - 0.012, f"nominal level {NOMINAL:.2f}",
            fontsize=7.5, color=INK, va="top")
    ax.text(0.08, MEASURED + 0.01, f"measured coverage {MEASURED:.3f}\n"
            f"({N_TRIALS} trials)", fontsize=7.5, color=ACCENT, va="bottom")
    ax.set_xlim(-0.5, 1.0)
    ax.set_xticks([])
    ax.set_ylabel("interval coverage (fraction of trials)")
    ax.set_title("width-injecting world", fontsize=9)
    ax.grid(alpha=0.25, axis="y")

    _footer(fig, "coverage and trial count quoted from "
                 "results/kernel_worlds.csv by name, not recomputed here.\n"
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_injection_recovery_1.png")

def fig_injection_recovery_2():
    """Recovered width minus the injected truth, across twelve independent synthetic realisations."""
    from scipy.optimize import least_squares
    from rb5s6s import composite_profile, transit_fwhm_from_w0

    t = transit_fwhm_from_w0(64e-6, 130.0)
    grid, p = composite_profile(0.60, 1.40, t)
    nu = np.linspace(-15, 15, 1200)
    shape = np.interp(nu, grid, p / p.max(), left=0, right=0)

    truth = 0.60
    errors = []
    for seed in range(12):
        data = shape + 0.01 * np.random.default_rng(seed).standard_normal(nu.size)

        def r(q):
            g, pp = composite_profile(abs(q[1]), abs(q[2]), t)
            return q[0] * np.interp(nu, g, pp / pp.max(), left=0, right=0) - data

        errors.append(abs(least_squares(r, [1.0, 0.60, 1.40]).x[1]) - truth)
    errors = np.array(errors)

    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    ax.axhline(0, color=INK, lw=0.8)
    ax.plot(np.arange(1, 13), errors, "o", ms=6, color=ACCENT, zorder=2)
    ax.axhline(errors.mean(), color=ACCENT2, ls="--", lw=1.2)
    ax.text(12.3, errors.mean() + 0.004, f"mean {errors.mean():+.4f} MHz",
            fontsize=7.5, color=ACCENT2, va="bottom")
    ax.text(0.02, 0.05, f"scatter {errors.std():.4f} MHz (12 injections)",
            transform=ax.transAxes, fontsize=7.5, color=INK)
    ax.set_xlabel("injection number")
    ax.set_ylabel("recovered minus truth (MHz)")
    ax.set_xlim(0.3, 15.0)
    ax.set_title("truth = 0.600 MHz, the builder the fits use", fontsize=9)
    ax.grid(alpha=0.25)

    _footer(fig, "reproduces the page's own Try It snippet exactly "
                 "(rb5s6s.composite_profile, seeds 0-11).\n"
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_injection_recovery_2.png")

def fig_magnetic_sublevels():
    """Zeeman fan of the Rb-87 ground hyperfine sublevels, degenerate at B=0."""
    g_j = 2.002_319_304_4  # free-electron g_J for an L=0 state
    mu_b, h = 9.274_010_078_3e-24, 6.626_070_15e-34  # CODATA, this page's own constants
    nuclear_i = 1.5  # Rb-87 nuclear spin
    def g_f(f):
        return g_j * (f * (f + 1) + 0.5 * 1.5 - nuclear_i * (nuclear_i + 1)) / (2 * f * (f + 1))
    b = np.linspace(0, 5, 60)
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0), sharex=True, sharey=True)
    for a, f, c in ((ax[0], 1, ACCENT2), (ax[1], 2, ACCENT)):
        g = g_f(f)
        slope = g * mu_b / h * 1e-4 / 1e6  # MHz per gauss per unit m_F
        for m in range(-f, f + 1):
            a.plot(b, m * slope * b, color=c, lw=1.3)
            if m != 0:
                a.text(5.08, m * slope * 5, f"$m_F$={m:+d}", fontsize=7.5, color=c, va="center")
        a.set_xlim(0, 6.6)
        a.set_xlabel("magnetic field (gauss)")
        a.set_title(f"F={f}: $g_F$={g:+.3f}, {slope:+.3f} MHz/G per $m_F$", fontsize=9)
        a.grid(alpha=0.25)
    ax[0].set_ylabel("Zeeman shift (MHz)")
    _footer(fig, "closed form: Lande g_F for L=0, this page's own Try It script (CODATA mu_B, h). "
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_magnetic_sublevels.png")

def fig_blackbody_radiation():
    """Committed blackbody AC-Stark shift against a naive T^4 law and the campaign's light-shift bound."""
    t_c_pts = np.array([70, 90, 110, 130])
    shift_pts = np.array([79.9349, 101.983, 128.738, 160.963])  # results/blackbody_channels.csv
    exponent = 4.35  # rb5s6s/blackbody.py _SHIFT_EXPONENT, fitted to these 4 points
    s0_ub95_hz = 258_000.0  # results/stark_joint.csv S0_225mW_ub95 (0.258 MHz)
    t_c = np.linspace(70, 130, 200)
    t_k = t_c + 273.15
    model_435 = shift_pts[-1] * (t_k / (t_c_pts[-1] + 273.15)) ** exponent
    model_4 = shift_pts[0] * (t_k / (t_c_pts[0] + 273.15)) ** 4.0
    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    ax.semilogy(t_c, model_435, color=ACCENT, lw=1.6, label=r"fitted, $T^{4.35}$")
    ax.semilogy(t_c, model_4, color=ACCENT2, lw=1.4, ls="--", label=r"naive $T^4$ (same at 70 C)")
    ax.plot(t_c_pts, shift_pts, "o", ms=5, color=INK, zorder=3, label="fitted points")
    ax.axhline(s0_ub95_hz, color=ACCENT3, lw=1.3, ls=":")
    ax.text(71, s0_ub95_hz * 1.15, "campaign light-shift bound\nS0_225mW_ub95 = 258 kHz",
            fontsize=7.5, color=ACCENT3)
    undershoot = 100 * (1 - model_4[-1] / model_435[-1])
    ax.text(95, 58, f"$T^4$ undershoots by {undershoot:.0f}% at 130 C", fontsize=7.5, color=INK)
    ax.set_xlabel("cell temperature (C)")
    ax.set_ylabel("blackbody Stark shift magnitude (Hz)")
    ax.set_title("Blackbody shift across the cell's range", fontsize=9)
    ax.set_ylim(50, 5e5)
    ax.legend(fontsize=7.5, frameon=False, loc="center left")
    ax.grid(alpha=0.25, which="both")
    _footer(fig, "values: results/blackbody_channels.csv & stark_joint.csv.\n"
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_blackbody_radiation.png")

def fig_the_beam_waist():
    """Beam radius about the waist, with the Rayleigh range and divergence angle marked."""
    w0_um, lam_nm = 64.0, 993.4  # W0_MEASURED_M, LAMBDA_LASER_M, rb5s6s/constants.py
    w0, lam = w0_um * 1e-6, lam_nm * 1e-9
    zr = np.pi * w0 ** 2 / lam
    theta = lam / (np.pi * w0)
    z = np.linspace(-3 * zr, 3 * zr, 400)
    w = w0 * np.sqrt(1 + (z / zr) ** 2) * 1e6
    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    ax.fill_between(z * 1e3, -w, w, color=ACCENT, alpha=0.25, lw=0)
    ax.plot(z * 1e3, w, color=ACCENT, lw=1.4)
    ax.plot(z * 1e3, -w, color=ACCENT, lw=1.4)
    ax.plot(z * 1e3, theta * np.abs(z) * 1e6, color=INK, lw=0.8, ls=":")
    ax.plot(z * 1e3, -theta * np.abs(z) * 1e6, color=INK, lw=0.8, ls=":")
    ax.annotate("", xy=(0, w0_um), xytext=(0, -w0_um),
                arrowprops=dict(arrowstyle="<->", color=ACCENT2, lw=1.1))
    ax.text(1.4, 0, f"$w_0$={w0_um:.0f} um", fontsize=7.5, color=ACCENT2, va="center")
    ax.axvline(zr * 1e3, color=INK, lw=0.8, ls="--")
    ax.text(zr * 1e3 * 1.05, w.max() * 0.4, f"$z_R$={zr * 1e3:.1f} mm", fontsize=7.5,
            color=INK, rotation=90, va="center")
    ax.text(2.5 * zr * 1e3, theta * 2.5 * zr * 1e6 * 1.08, rf"$\theta$={theta * 1e3:.2f} mrad",
            fontsize=7.5, color=INK)
    ax.set_xlabel("distance from focus z (mm)")
    ax.set_ylabel("beam radius (um)")
    ax.set_title(r"$w_0\theta = \lambda/\pi$, the fixed diffraction trade", fontsize=9)
    ax.grid(alpha=0.25)
    _footer(fig, "w0, lambda from rb5s6s.constants (W0_MEASURED_M, LAMBDA_LASER_M).\n"
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_the_beam_waist.png")

def fig_standing_waves():
    """Doppler-free line to same-beam pedestal area ratio against the retro ratio."""
    rho_retro, rho_err = 0.94, 0.04  # rb5s6s.constants RHO_RETRO, RHO_RETRO_ERR
    rho = np.linspace(0.001, 1, 300)
    ratio = 4 * rho / (1 + rho ** 2)
    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    ax.plot(rho, ratio, color=ACCENT, lw=1.6)
    r_acc = 4 * rho_retro / (1 + rho_retro ** 2)
    slope = 4 * (1 - rho_retro ** 2) / (1 + rho_retro ** 2) ** 2
    ax.errorbar([rho_retro], [r_acc], xerr=[rho_err], yerr=[slope * rho_err], fmt="o",
                ms=5, color=ACCENT2, capsize=3, zorder=3)
    ax.annotate(f"accepted RHO_RETRO\n{rho_retro} +/- {rho_err}, ratio = {r_acc:.3f}",
                xy=(rho_retro, r_acc), xytext=(0.16, 1.02), fontsize=7.5, color=ACCENT2,
                arrowprops=dict(arrowstyle="->", color=ACCENT2, lw=0.8))
    ax.plot([1], [2], "s", ms=5, color=INK, zorder=3)
    ax.annotate("rho=1: ratio=2\n(slope=0 here)", xy=(1, 2), xytext=(0.42, 1.55),
                fontsize=7.5, color=INK, arrowprops=dict(arrowstyle="->", color=INK, lw=0.8))
    ax.set_xlim(0, 1.08)
    ax.set_ylim(0, 2.2)
    ax.set_xlabel(r"retro ratio $\rho$ (returning / forward intensity)")
    ax.set_ylabel(r"area ratio $4\rho/(1+\rho^2)$")
    ax.set_title("Narrow-line to pedestal area ratio", fontsize=9)
    ax.grid(alpha=0.25)
    _footer(fig, "closed form, RHO_RETRO from rb5s6s.constants.\n"
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_standing_waves.png")

def fig_doppler_free_geometries_1():
    """The three wavevector closures this page derives: flat, triangular, flat again."""
    fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.8))

    def arrow(a, tail, head, color, label, lx, ly):
        a.annotate("", xy=head, xytext=tail,
                   arrowprops=dict(arrowstyle="-|>", color=color, lw=1.6))
        a.text(lx, ly, label, fontsize=7.5, color=color, ha="center")

    arrow(ax[0], (0, 0.15), (1, 0.15), ACCENT, "$k_1$", 0.5, 0.32)
    arrow(ax[0], (1, -0.15), (0, -0.15), ACCENT2, "$k_2=-k_1$", 0.5, -0.32)
    ax[0].plot(0, 0, "o", color=INK, ms=4)
    ax[0].text(0.5, -0.8, "sum = 0", fontsize=7.5, color=INK, ha="center")
    ax[0].set_title("(a) two-photon", fontsize=9)
    ax[0].set_xlim(-0.3, 1.3)
    ax[0].set_ylim(-1.1, 0.6)
    pts = [(0, 0)]
    colors3 = (ACCENT, ACCENT2, ACCENT3)
    for i, th in enumerate((90, 210, 330)):
        tail = pts[-1]
        head = (tail[0] + np.cos(np.radians(th)), tail[1] + np.sin(np.radians(th)))
        pts.append(head)
        arrow(ax[1], tail, head, colors3[i], f"$k_{i + 1}$",
              (tail[0] + head[0]) / 2 + 0.22, (tail[1] + head[1]) / 2)
    ax[1].plot(0, 0, "o", color=INK, ms=4)
    ax[1].text(0, -1.5, "sum = 0 (equilateral, 120 deg apart)", fontsize=7.5, color=INK, ha="center")
    ax[1].set_title("(b) three equal colours", fontsize=9)
    ax[1].set_xlim(-1.3, 1.3)
    ax[1].set_ylim(-1.8, 1.3)
    arrow(ax[2], (0, 0.15), (1, 0.15), ACCENT, "$k$", 0.5, 0.4)
    arrow(ax[2], (1, 0.15), (2, 0.15), ACCENT, "$k$", 1.5, 0.4)
    arrow(ax[2], (2, -0.15), (0, -0.15), ACCENT2, "$2k$", 1.0, -0.4)
    ax[2].plot(0, 0, "o", color=INK, ms=4)
    ax[2].text(1.0, -0.95, "sum = 0 ($k+k-2k$)", fontsize=7.5, color=INK, ha="center")
    ax[2].set_title("(c) fundamental + harmonic", fontsize=9)
    ax[2].set_xlim(-0.4, 2.4)
    ax[2].set_ylim(-1.2, 0.7)
    for a in ax:
        a.set_aspect("equal")
        a.axis("off")
    _footer(fig, "closed form, no data: wavevector-sum diagrams from doppler-free-geometries.md. "
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_doppler_free_geometries_1.png")

def fig_doppler_free_geometries_2():
    """Residual first-order Doppler FWHM for the five signed-wavevector closures."""
    k_b, m_rb87, lam = 1.380649e-23, 1.443_160_895e-25, 993.4e-9  # rb5s6s.constants
    t_k = 403.15  # reference cell temperature, this page's own Try It (130 C)
    v_sigma = np.sqrt(k_b * t_k / m_rb87)
    k_fund = 2 * np.pi / lam

    def fwhm_hz(signed_k):
        return abs(sum(signed_k)) * k_fund * np.sqrt(8 * np.log(2)) * v_sigma / (2 * np.pi)

    cases = [
        ("single\nphoton", [1]),
        ("two counter-\npropagating", [1, -1]),
        ("three, all\none way", [1, 1, 1]),
        ("three, two\nand one", [1, 1, -1]),
        ("harmonic\n$k+k-2k$", [1, 1, -2]),
    ]
    vals = [fwhm_hz(ks) / 1e6 for _, ks in cases]
    colors = [ACCENT3 if v < 1e-6 else ACCENT2 for v in vals]
    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    ax.bar(range(len(cases)), vals, color=colors, width=0.6)
    for i, v in enumerate(vals):
        label = "Doppler-free" if v < 1e-6 else f"{v:.0f} MHz"
        ax.text(i, v + 30, label, ha="center", fontsize=7.5, color=INK)
    ax.set_xticks(range(len(cases)))
    ax.set_xticklabels([c for c, _ in cases], fontsize=7.5)
    ax.set_ylabel("residual first-order Doppler FWHM (MHz)")
    ax.set_title("Only the sum-to-zero closures cancel", fontsize=9)
    ax.set_ylim(0, 1550)
    ax.grid(alpha=0.25, axis="y")
    _footer(fig, "closed form at T=403.15 K, this page's own doppler_fwhm_hz.\n"
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_doppler_free_geometries_2.png")

def fig_shot_noise_and_technical_noise():
    """The three noise scalings and only the multiplicative one flat as a fraction of signal."""
    v = np.logspace(-2, 2, 200)
    terms = [("additive technical, $V^0$", 0.0, ACCENT3),
             ("shot, $V^{0.5}$", 0.5, ACCENT),
             ("multiplicative technical, $V^1$", 1.0, ACCENT2)]
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0))
    for name, p, c in terms:
        ax[0].loglog(v, v ** p, color=c, lw=1.5, label=name)
        ax[1].loglog(v, v ** (p - 1), color=c, lw=1.5, label=name)
    ax[0].set_xlabel("signal level V (arbitrary units)")
    ax[0].set_ylabel(r"noise $\sigma$ (arbitrary units)")
    ax[0].set_title("(a) sigma against signal", fontsize=9)
    ax[0].legend(fontsize=7.5, frameon=False, loc="upper left")
    ax[0].grid(alpha=0.25, which="both")
    ax[1].set_xlabel("signal level V (arbitrary units)")
    ax[1].set_ylabel(r"fractional noise $\sigma/V$")
    ax[1].set_title("(b) only the multiplicative term is flat", fontsize=9)
    ax[1].grid(alpha=0.25, which="both")
    _footer(fig, "closed form, this page's own Try It scalings (V^0, V^0.5, V^1). "
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_shot_noise_and_technical_noise.png")

def fig_the_noise_law():
    """One committed noise-law condition, with the floor, shot and excess bands stacked in sigma."""
    a_v, b_v, c = 5.479247e-3, 9.995141e-4, 0.0  # results/noise_model.csv, 4121nm/130C/225mW
    v = np.linspace(1e-4, 0.3, 400)
    sig_floor = np.full_like(v, a_v)
    sig_floor_shot = np.sqrt(a_v ** 2 + b_v * v)
    sig_total = np.sqrt(a_v ** 2 + b_v * v + c * v ** 2)
    v_star = a_v ** 2 / b_v
    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    ax.fill_between(v, 0, sig_floor, color=ACCENT3, alpha=0.35, label="floor $a$")
    ax.fill_between(v, sig_floor, sig_floor_shot, color=ACCENT, alpha=0.35, label="shot $bV$")
    ax.fill_between(v, sig_floor_shot, sig_total, color=ACCENT2, alpha=0.6, label="excess $cV^2$")
    ax.plot(v, sig_total, color=INK, lw=1.3)
    ax.axvline(v_star, color=INK, lw=0.8, ls="--")
    ax.text(v_star * 1.08, sig_total.max() * 0.5, f"floor=shot\nat V*={v_star * 1e3:.1f} mV",
            fontsize=7.5, color=INK)
    ax.text(0.14, 0.0155, "excess fits to 0 here,\nas in 31 of 32 conditions",
            fontsize=7.5, color=ACCENT2)
    ax.set_xlabel("signal level V (volts above baseline)")
    ax.set_ylabel(r"noise $\sigma$ (volts)")
    ax.set_title("Where each noise term dominates", fontsize=9)
    ax.legend(fontsize=7.5, frameon=False, loc="upper left")
    ax.grid(alpha=0.25)
    _footer(fig, "a_V, b_V, c: results/noise_model.csv (4121nm, 130C, 225mW).\n"
                 "Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_the_noise_law.png")


def fig_reduced_chi_squared_1():
    """The sampling spread of chi2_red collapses with the degrees of freedom.

    The panel exists because a bare chi2_red is uninterpretable: 1.3 is
    unremarkable on ten degrees of freedom and a crisis on ten thousand.
    """
    from scipy import stats
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    for dof, colour, style in ((10, ACCENT3, ":"), (100, ACCENT, "--"),
                               (1000, ACCENT2, "-")):
        x = np.linspace(0.2, 4.2, 1600)
        y = dof * stats.chi2.pdf(x * dof, dof)
        ax.plot(x, y / y.max(), style, color=colour, lw=1.6,
                label=f"ν = {dof}, sd = {np.sqrt(2 / dof):.2f}")
    ax.axvline(1.0, color=INK, lw=0.9)
    ax.annotate("expected value 1", xy=(1.0, 1.16), xytext=(1.45, 1.16),
                fontsize=8, color=INK, va="center",
                arrowprops=dict(arrowstyle="-", color=INK, lw=0.7))
    ax.axvline(3.7, color="0.45", lw=0.9, ls="-.")
    ax.annotate("3.7, the summary width regression",
                xy=(3.7, 0.30), xytext=(3.52, 0.30),
                fontsize=8, color="0.35", va="center", ha="right",
                arrowprops=dict(arrowstyle="->", color="0.45", lw=0.7))
    ax.set_xlabel("reduced chi-squared")
    ax.set_ylabel("density (each scaled to its own peak)")
    ax.set_xlim(0.2, 4.2)
    ax.set_ylim(0, 1.32)
    ax.legend(frameon=False, fontsize=8, loc="upper right")
    ax.spines[["top", "right"]].set_visible(False)
    _footer(fig, "Teaching panel. Chi-squared sampling density, closed form, "
                 "no data. Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_reduced_chi_squared_1.png")

def fig_reduced_chi_squared_2():
    """One misfit, two readings that chi2_red alone cannot separate.

    Left: a model missing a component. Right: the identical residuals with
    the errors inflated by the square root of chi2_red, which sets the
    number to one and leaves the structure untouched. The injected amplitude
    is solved for at draw time so the left panel lands on 3.7, the value
    this record's own width-against-power fit returns.
    """
    from scipy.optimize import brentq
    rng = np.random.default_rng(20260827)
    n = 40
    x = np.linspace(-3.0, 3.0, n)
    sigma = np.full(n, 0.05)
    truth = np.exp(-x ** 2 / 2)
    shape = np.cos(2.1 * x)
    noise = rng.normal(0, sigma, n)

    def cr_of(amp):
        r = (truth + amp * shape + noise - truth) / sigma
        return float(np.sum(r ** 2) / (n - 2))
    amp = brentq(lambda a: cr_of(a) - 3.7, 0.0, 0.5, xtol=1e-9)
    y = truth + amp * shape + noise
    cr = cr_of(amp)
    infl = np.sqrt(cr)

    fig, axes = plt.subplots(2, 2, figsize=(7.8, 4.6), sharex=True,
                             sharey="row",
                             gridspec_kw={"height_ratios": [2, 1]})
    for col, (s, lab) in enumerate(
            ((sigma, f"errors as quoted, reduced chi-squared {cr:.1f}"),
             (sigma * infl,
              f"errors inflated {infl:.1f} times, reduced chi-squared 1.0"))):
        top, bot = axes[0, col], axes[1, col]
        top.errorbar(x, y, yerr=s, fmt="o", ms=3, lw=0.9, color=ACCENT,
                     ecolor="0.6", capsize=0)
        top.plot(x, truth, "-", color=ACCENT2, lw=1.6)
        top.set_title(lab, fontsize=9, color=INK)
        bot.axhline(0, color=INK, lw=0.8)
        bot.errorbar(x, y - truth, yerr=s, fmt="o", ms=2.6, lw=0.8,
                     color=ACCENT, ecolor="0.6", capsize=0)
        bot.set_xlabel("detuning (arbitrary)")
        for a in (top, bot):
            a.spines[["top", "right"]].set_visible(False)
    axes[0, 0].set_ylabel("signal")
    axes[1, 0].set_ylabel("residual")
    _footer(fig, "Teaching panel. Synthetic, seed 20260827, drawn here. The "
                 "points and the residual structure are identical in both "
                 "columns. Rebuild: python scripts/make_wiki_figures.py")
    _save(fig, "wiki_reduced_chi_squared_2.png")

def main():
    print(f"drawing wiki panels into {OUT}")
    fig_allan_deviation()
    fig_bessel()
    fig_eom_comb()
    fig_joint_fit_toy()
    fig_ic_penalty()
    fig_sampling_the_line()
    fig_shift_distribution()
    fig_resampling_2()
    fig_correlated_samples_and_effective_sample_size()
    fig_pooling_across_groups()
    fig_optimiser_convergence()
    fig_grids_and_discretisation()
    fig_compute_budgets_and_failure_modes_1()
    fig_compute_budgets_and_failure_modes_2()
    fig_resolution_enhancement_and_what_it_costs()
    fig_vapour_density_and_temperature()
    fig_sweep_rate_and_detection_lag()
    fig_digitisation_and_dynamic_range()
    fig_photon_counting()
    fig_guided_atoms_and_nanofibres_1()
    fig_guided_atoms_and_nanofibres_2()
    fig_selection_rules()
    fig_heavy_tailed_models_1()
    fig_heavy_tailed_models_2()
    fig_weighted_least_squares()
    fig_robust_fitting()
    fig_profile_likelihood()
    fig_monte_carlo_methods()
    fig_resampling_1()
    fig_preregistration()
    fig_reversal_tests()
    fig_sensitivity_analysis_1()
    fig_sensitivity_analysis_2()
    fig_influence_diagnostics()
    fig_injection_recovery_1()
    fig_injection_recovery_2()
    fig_magnetic_sublevels()
    fig_blackbody_radiation()
    fig_the_beam_waist()
    fig_standing_waves()
    fig_doppler_free_geometries_1()
    fig_doppler_free_geometries_2()
    fig_shot_noise_and_technical_noise()
    fig_the_noise_law()
    fig_reduced_chi_squared_1()
    fig_reduced_chi_squared_2()
    print("done")


if __name__ == "__main__":
    main()

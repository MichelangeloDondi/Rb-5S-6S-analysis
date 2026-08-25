#!/usr/bin/env python3
"""Teaching panels for the documentation in docs/.

These are NOT result figures. Every one is drawn from a closed-form
expression or from synthetic numbers generated here with a fixed seed, none
of them reads results/ or data_raw/, and none of them carries a data
fingerprint, because there is no data behind them to go stale. They live in
docs/wiki/figures/ rather than figures/ for exactly that reason: the
figures/ tree is the result gallery and is guarded as one.

A panel exists here only where a figure materially improves the page it sits
on. Seven earn it (a count once left at five while six existed, the
carried-count class again). The pages with no panel carry none, which is a choice
rather than an omission.

Register: the same plain-physics rules as the result figures, so no pipeline
dialect in anything drawn, and every drawing function carries a footer
naming what the panel is and how to rebuild it.

Run: python scripts/make_wiki_figures.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.special import jv

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


def main():
    print(f"drawing wiki panels into {OUT}")
    fig_allan_deviation()
    fig_bessel()
    fig_eom_comb()
    fig_joint_fit_toy()
    fig_ic_penalty()
    fig_sampling_the_line()
    fig_shift_distribution()
    print("done")


if __name__ == "__main__":
    main()

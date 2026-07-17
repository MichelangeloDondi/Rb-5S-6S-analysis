#!/usr/bin/env python3
"""
The Ti:Sapph polarizability ladder: 5S->6S (993), 5S->7S (760), 5S->5D5/2 (778).

For each transition prints Delta_alpha(lambda) at the drive, the magic wavelengths
(= the light-shift sign-flip locations, where alpha_upper = alpha_lower), and an
uncertainty band, and draws Delta_alpha(lambda) to figures/fig9_polarizability_ladder.png.

7S is an INDEPENDENT sum-over-states (rb5s6s.polarizability, Safronova 2004
all-order elements). 5D5/2 is ADOPTED from Hamilton et al. 2023 (measured magic
776.179(5) nm) -- a from-scratch 5D recompute needs the nF elements + tensor
treatment, flagged there as future work. Nothing is written to results/.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from rb5s6s import polarizability as P  # noqa: E402

_SEED = 20260717


def _mc_7s(fn, n: int = 1500, seed: int = _SEED):
    """16/50/84 percentiles of fn over draws of the 5S and 7S inputs."""
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(n):
        s5 = [max(d + rng.normal(0, sd), 0.0) for _, d, sd in P.LINES_5S]
        s7 = [max(d + rng.normal(0, sd), 0.0) for _, d, sd in P.LINES_7S]
        kw5 = dict(scale=s5, tail=P.TAIL_5S + rng.normal(0, P.TAIL_5S_SIG),
                   core=P.CORE_5S + rng.normal(0, P.CORE_5S_SIG))
        kw7 = dict(scale=s7, tail=P.TAIL_7S + rng.normal(0, P.TAIL_7S_SIG),
                   core=P.CORE_7S + rng.normal(0, P.CORE_7S_SIG))
        try:
            vals.append(fn(kw5, kw7))
        except Exception:
            pass
    v = np.sort(np.asarray(vals, float))
    return np.median(v), np.percentile(v, 16), np.percentile(v, 84)


def _nearest_magic(kw5, kw7, target, lo, hi):
    from scipy.optimize import brentq
    f = lambda x: P.alpha_7s(x, **kw7) - P.alpha_5s(x, **kw5)
    g = np.linspace(lo, hi, 400)
    val = [f(x) for x in g]
    best = None
    for i in range(len(g) - 1):
        if val[i] * val[i + 1] < 0:
            x = brentq(f, g[i], g[i + 1], xtol=1e-6)
            if best is None or abs(x - target) < abs(best - target):
                best = x
    if best is None:
        raise ValueError("no crossing")
    return best


def main() -> None:
    print("=" * 70)
    print("Ti:Sapph polarizability ladder  (Delta_alpha = alpha_upper - alpha_5S)")
    print("=" * 70)

    # --- 5S->6S (anchor, already validated) ---
    m6 = [x for x, _ in P.magic_wavelengths()]
    print("\n5S->6S  (993 nm, clean):")
    print(f"  Delta_alpha(993) = {P.delta_alpha(993):.0f} a.u.  (BLUE shift; |val| "
          f"~5% of Orson 2021's 1093, opposite sign -- THEORY_NOTE section 5)")
    print(f"  magic / sign-flips: {', '.join(f'{x:.1f}' for x in m6)} nm  "
          f"(all far to the red, clean)")

    # --- 5S->7S (independent recompute) ---
    print("\n5S->7S  (760 nm, intermediate detuning):")
    stat = _mc_7s(lambda k5, k7: P.alpha_7s(0, **k7))
    print(f"  alpha_7S(static) = {stat[0]:.0f} a.u. [{stat[1]:.0f}, {stat[2]:.0f}]"
          f"  (large: 7S-7P gap only 1524 cm^-1; follows the 5S 319 -> 6S 5167 -> 7S trend)")
    d760 = _mc_7s(lambda k5, k7: P.alpha_7s(760, **k7) - P.alpha_5s(760, **k5))
    print(f"  Delta_alpha(760) = {d760[0]:+.0f} a.u. [{d760[1]:+.0f}, {d760[2]:+.0f}]"
          f"  (RED shift; large -- 760 sits near the 5S D lines at 780/795)")
    magic7 = P.magic_5s7s()
    print(f"  magic / sign-flips (700-1000 nm):")
    for x, a in magic7:
        near = "  <- just red of the 7S-5P3/2 pole (741 nm)" if abs(x - 742) < 3 else \
               "  <- beside the 5S tune-out (790.03)" if abs(x - 790) < 2 else ""
        print(f"    {x:.2f} nm  (alpha = {a:.0f} a.u.){near}")
    try:
        mb = _mc_7s(lambda k5, k7: _nearest_magic(k5, k7, 742.6, 742.0, 760.0))
        print(f"    band on the 742.6 nm crossing: [{mb[1]:.2f}, {mb[2]:.2f}] nm")
    except Exception:
        print("    (MC band on the 742 crossing unstable near the pole -- omitted)")

    # --- 5S->5D5/2 (adopted from Hamilton 2023) ---
    lam_res = 1e7 / (P.E_5D52_CM - 12816.545)
    print("\n5S->5D5/2  (778 nm, NEAR-RESONANT):  ADOPTED from Hamilton et al. 2023")
    print(f"  5P3/2-5D5/2 resonance at {lam_res:.1f} nm (RME {P.RME_5P32_5D52} a.u.)")
    print(f"  magic / sign-flip = {P.MAGIC_5S5D52_EXP_NM} nm (experimental, +-0.005)"
          f" / {P.MAGIC_5S5D52_THEORY_NM} nm (theory)")
    print(f"  -> at the 778 nm drive Delta_alpha != 0 (the magic sits ~2 nm blue),"
          f" so the light shift there has a definite, non-zero sign.")
    print("  NOTE: a from-scratch 5D recompute needs the 5D-nF elements (absent from")
    print("  the Safronova 2004 tables) and the tensor treatment -- future work.")

    # --- figure: Delta_alpha(lambda) for the two clean/independent transitions ---
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for ax, (lo, hi, drive, fn, title, magics) in zip(axes, [
        (1150, 1400, 993, P.delta_alpha, "5S->6S", m6),
        (720, 800, 760, P.delta_alpha_7s, "5S->7S", [x for x, _ in magic7]),
    ]):
        g = np.linspace(lo, hi, 2000)
        y = np.array([fn(x) for x in g])
        # clip near poles for a readable axis
        y[np.abs(y) > 8000] = np.nan
        ax.axhline(0, color="0.6", lw=0.8)
        ax.plot(g, y, color="C0", lw=1.6)
        ax.axvline(drive, color="C3", ls="--", lw=1.2, label=f"drive {drive} nm")
        for m in magics:
            if lo < m < hi:
                ax.axvline(m, color="C2", ls=":", lw=1.1)
                ax.annotate(f"{m:.1f}", (m, 0), textcoords="offset points",
                            xytext=(2, 6), fontsize=8, color="C2")
        ax.set_title(f"{title}: $\\Delta\\alpha(\\lambda)$")
        ax.set_xlabel("wavelength (nm)")
        ax.set_ylabel("$\\Delta\\alpha$ (a.u.)")
        ax.legend(fontsize=8, loc="best")
    axes[1].annotate("5D magic 776.18 nm\n(Hamilton 2023, adopted)", (776, 0),
                     xytext=(730, 3500), fontsize=8, color="0.3",
                     arrowprops=dict(arrowstyle="->", color="0.5"))
    fig.tight_layout()
    out = Path(__file__).resolve().parents[1] / "figures" / "fig9_polarizability_ladder.png"
    fig.savefig(out, dpi=140)
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()

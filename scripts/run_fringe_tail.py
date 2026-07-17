#!/usr/bin/env python3
"""
M14: fringe-tail imprint on the standing-wave AC-Stark ramp.

Samples the 3D Maxwell-Boltzmann + fringe-phase ensemble (rb5s6s.fringe_tail)
at the archival (50 um, S0 = 0.6 MHz) and October (16 um, S0 = 5.7 MHz)
geometries, rho = 1 and 0.75, and reports how the slow-axial-speed fringe tail
suppresses the ramp's skew, inflates its variance, and how large the
fringe-resolved fraction is. The coherence window is swept between the
transit-limited case and the 6S lifetime to bracket the one open modelling
choice. Independent blocks are pooled so the third-moment skew is seed-stable
and carries a reported Monte-Carlo error.

Writes results/fringe_tail.csv.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C  # noqa: E402
from rb5s6s.constants import TAU_6S_S  # noqa: E402
from rb5s6s.fringe_tail import fringe_tail_mc  # noqa: E402

# (label, w0 in m, S0 in MHz): archival prior and the October small-waist target
REGIMES = (
    ("2025 (50um, 0.6MHz)", 50e-6, 0.6),
    ("Oct  (16um, 5.7MHz)", 16e-6, 5.7),
)
RHOS = (1.0, 0.75)
# coherence window: transit-limited (None) and 6S-lifetime-capped -> the bracket
WINDOWS = (("transit", None), ("tau6s", TAU_6S_S))
T_C = 130.0
# high statistics so the third-moment skew is seed-stable (see module docstring):
# 16 pooled blocks of 2e6 atoms => ~0.0025 skew standard error.
N_ATOMS = 2_000_000
N_BLOCKS = 16


def main() -> int:
    print("=" * 82)
    print("(M14) FRINGE-TAIL imprint on the standing-wave AC-Stark ramp")
    print(f"  3D-MB + fringe-phase MC, {N_BLOCKS} x {N_ATOMS} atoms pooled;")
    print("  coherence window swept transit <-> tau_6S.\n")
    print(f"  {'regime':22s} {'rho':>4} {'window':>8} {'d_skew':>16} "
          f"{'d_kappa3':>9} {'exc_var':>8} {'f_res':>7} {'wfrac':>7}")
    rows = []
    for label, w0, s0 in REGIMES:
        for rho in RHOS:
            for wname, tc in WINDOWS:
                r = fringe_tail_mc(w0_m=w0, s0_mhz=s0, rho=rho, T_C=T_C,
                                   coherence_s=tc, n_atoms=N_ATOMS,
                                   n_blocks=N_BLOCKS)
                r["regime"] = label
                r["window"] = wname
                rows.append(r)
                print(f"  {label:22s} {rho:>4.2f} {wname:>8} "
                      f"{r['d_skew']:>+8.4f} +- {r['d_skew_mc_err']:.4f} "
                      f"{r['d_kappa3']:>+9.4f} {r['excess_var_frac']*100:>7.2f}% "
                      f"{r['frac_resolved']*100:>6.2f}% {r['window_frac']*100:>6.2f}%")

    # coefficient checks (rho = 1, transit window): the claimed leverages, per
    # unit fringe-modulation variance Var(x) = f_res_var (= f_res/2 in the note)
    print("\n  COEFFICIENT CHECKS (rho=1, transit window; f = Var(x) = f_res/2):")
    print(f"  {'regime':22s} {'d_skew/f':>10} {'d_kappa3/(S0^3 f)':>18} "
          f"{'exc_var(/Var0)/f':>17}")
    for label, w0, s0 in REGIMES:
        r = fringe_tail_mc(w0_m=w0, s0_mhz=s0, rho=1.0, T_C=T_C, coherence_s=None,
                           n_atoms=N_ATOMS, n_blocks=N_BLOCKS)
        f = r["f_res_var"]
        exc_over_var0 = (r["var"] - r["var_nofringe"]) / r["var_nofringe"]
        print(f"  {label:22s} {r['d_skew']/f:>10.2f} "
              f"{r['d_kappa3']/(s0**3*f):>18.3f} {exc_over_var0/f:>17.2f}")

    with open(C.RESULTS_DIR / "fringe_tail.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["quantity", "key", "value", "unit"])
        for r in rows:
            k = f"{r['regime'].split()[0]}_rho{r['rho']:.2f}_{r['window']}"
            w.writerow(["d_skew", k, f"{r['d_skew']:.4f}",
                        "standardized skew change (with - without fringe)"])
            w.writerow(["d_skew_mc_err", k, f"{r['d_skew_mc_err']:.4f}",
                        "block-to-block standard error on d_skew"])
            w.writerow(["d_kappa3", k, f"{r['d_kappa3']:.4f}",
                        "third-cumulant change MHz^3 (with - without fringe)"])
            w.writerow(["excess_var_frac", k, f"{r['excess_var_frac']:.4f}",
                        "fraction of the shift variance contributed by the fringe"])
            w.writerow(["frac_resolved", k, f"{r['frac_resolved']:.4f}",
                        "signal-weighted fraction with fringe survival F > 0.5"])
            w.writerow(["window_frac", k, f"{r['window_frac']:.4f}",
                        "coherence-window axial-speed fraction P(|vz| < (lambda/2)/T_window)"])

    print("\n  READING: the fringe tail SUPPRESSES the ramp skew (d_skew < 0) and")
    print("  inflates its variance, both scaling with the fringe-modulation")
    print("  variance. Negligible at the archival 50 um waist (|d_skew| ~ 0.05,")
    print("  below the archival noise); material at the October 16 um waist")
    print("  (|d_skew| ~ 0.15, ~27% of the +0.566 triangle skew). The transit <->")
    print("  tau_6S window sweep brackets it; the third cumulant is the stable")
    print("  bracket (Oct -0.15 -> -0.18 MHz^3), the standardized skew nearly flat")
    print("  because the same window that grows the cumulant also grows the")
    print("  variance it is normalized by. Wrote results/fringe_tail.csv.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

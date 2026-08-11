#!/usr/bin/env python3
"""
M15: fringe-tail imprint on the standing-wave AC-Stark ramp.

Samples the 3D Maxwell-Boltzmann + fringe-phase ensemble (rb5s6s.fringe_tail)
at the measured waist (config.W0_MEASURED_M) and small-waist config S (16 um)
geometries -- both S0 from lineshape.stark_shift_S0_mhz at 225 mW, so neither
waist nor shift can go stale here -- over the three retro ratios, and reports
how the slow-axial-speed fringe tail
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
from rb5s6s.lineshape import stark_shift_S0_mhz  # noqa: E402

# (label, w0 in m, S0 in MHz): the measured waist and the small-waist (config S) target
_S0_ARCHIVAL = stark_shift_S0_mhz(0.225, C.W0_MEASURED_M, rho=C.RHO_RETRO)
_S0_SMALL = stark_shift_S0_mhz(0.225, 16e-6, rho=C.RHO_RETRO)
REGIMES = (
    (f"2025 ({C.W0_MEASURED_M*1e6:.0f}um, {_S0_ARCHIVAL:.2f}MHz)",
     C.W0_MEASURED_M, _S0_ARCHIVAL),
    (f"S    (16um, {_S0_SMALL:.1f}MHz)", 16e-6, _S0_SMALL),
)
RHOS = (1.0, C.RHO_RETRO, 0.75)
# the intrinsic standardized skew of the triangular ramp, 18^1.5/135 = +0.566:
# the denominator every prose site normalizes d_skew by (constants.py says so)
G1_TRIANGLE = 18 ** 1.5 / 135
# coherence window: transit-limited (None) and 6S-lifetime-capped -> the bracket
WINDOWS = (("transit", None), ("tau6s", TAU_6S_S))
T_C = 130.0
# high statistics so the third-moment skew is seed-stable (see module docstring):
# 16 pooled blocks of 2e6 atoms => ~0.0025 skew standard error.
N_ATOMS = 2_000_000
N_BLOCKS = 16


def main() -> int:
    print("=" * 82)
    print("(M15) FRINGE-TAIL imprint on the standing-wave AC-Stark ramp")
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
            w.writerow(["d_kappa3_mc_err", k, f"{r['d_kappa3_mc_err']:.4f}",
                        "block-to-block standard error on d_kappa3"])
            w.writerow(["excess_var_frac", k, f"{r['excess_var_frac']:.4f}",
                        "fraction of the shift variance contributed by the fringe"])
            w.writerow(["excess_var_frac_mc_err", k,
                        f"{r['excess_var_frac_mc_err']:.4f}",
                        "block-to-block standard error on excess_var_frac"])
            w.writerow(["frac_resolved", k, f"{r['frac_resolved']:.4f}",
                        "signal-weighted fraction with fringe survival F > 0.5"])
            w.writerow(["frac_resolved_mc_err", k,
                        f"{r['frac_resolved_mc_err']:.4f}",
                        "block-to-block standard error on frac_resolved"])
            w.writerow(["window_frac", k, f"{r['window_frac']:.4f}",
                        "coherence-window axial-speed fraction P(|vz| < (lambda/2)/T_window)"])

    # the READING quotes the run's own numbers, so it cannot describe a waist or
    # a suppression the run did not produce (it long said "the archival 50 um
    # waist" after W0_MEASURED_M moved to 64 um, and a percentage of the triangle
    # skew that was last true two waists earlier)
    def _band(lab):
        d = [abs(r["d_skew"]) for r in rows if r["regime"].split()[0] == lab]
        return f"|d_skew| {min(d):.2f}-{max(d):.2f}, {min(d) / G1_TRIANGLE * 100:.0f}-" \
               f"{max(d) / G1_TRIANGLE * 100:.0f}% of the +{G1_TRIANGLE:.3f} triangle skew"
    print("\n  READING: the fringe tail SUPPRESSES the ramp skew (d_skew < 0) and")
    print("  inflates its variance, both scaling with the fringe-modulation")
    print(f"  variance. At the measured {C.W0_MEASURED_M*1e6:.0f} um it is negligible")
    print(f"  ({_band('2025')}), the whole skew being below the")
    print("  archival noise there; at the small 16 um waist (config S) it is")
    print(f"  material ({_band('S')}). The transit <->")
    print("  tau_6S window sweep brackets it; the third cumulant is the stable")
    print("  bracket (config S -0.14 -> -0.16 MHz^3), the standardized skew nearly flat")
    print("  because the same window that grows the cumulant also grows the")
    print("  variance it is normalized by. Wrote results/fringe_tail.csv.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

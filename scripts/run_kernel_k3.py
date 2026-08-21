#!/usr/bin/env python
"""K2.5 and K3: the mixed G+L kernel against the real archive.

Preregistered in private/reviews/K3_PREREG_2026-08-21.md BEFORE this ran.

WHY THIS IS A MULTI-CONDITION PRODUCER AND NOT A PER-CONDITION ONE. At a fixed
condition Gamma_L,equiv is EXACTLY degenerate with gamma_coll: both are
Lorentzian widths, Lorentzians add, and the fit recovers their sum while the
split is arbitrary. The separating lever is DENSITY, since gamma_coll is
beta_self * N(T) and a laser width is not. This producer therefore fits each
peak across the 70/90/110/130 C ladder, whose density lever is a factor 52.5,
and the identifiable object is one Gamma_L,equiv per ladder.

K2.5 FIRST: IS THE KERNEL LEGITIMATELY ONE SCALAR? Each peak's ladder is fitted
independently, and the four fitted Gamma_L,equiv values are compared against
their errors. A kernel parameter that varies across peaks is a DIFFERENT
FINDING from a global one, and assuming globality straight after discovering
that the kernel's shape matters would repeat the shape mistake one level up.

K3: THE NESTED COMPARISON. G (gamma_l pinned at zero) is nested inside G+L
(gamma_l free) by construction, one parameter at its boundary. The statistic is
the chi2 DIFFERENCE between the two fits of the same data, which is why
fit_beta_self reports absolute chi2 rather than only a reduced one. The null
sits ON the boundary, so the asymptotic reference is the 50:50 mixture of a
point mass at zero and a chi2 with one degree of freedom, and the p-value is
half the naive one.

WHAT THIS PRODUCER MAY NOT SAY. G+L winning supports A NON-GAUSSIAN HOMOGENEOUS
COMPONENT, full stop. Attribution TO THE LASER is licensed by the K5 transfer
triangle and by nothing here, and no column in this CSV is named for the laser.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from rb5s6s import config as C                          # noqa: E402
from rb5s6s.beta import fit_beta_self                   # noqa: E402
from rb5s6s.ingest import load_manifest                 # noqa: E402
from run_beta_self import load_conditions, load_t_rates       # noqa: E402
from rb5s6s.qc import outlier_files                           # noqa: E402

OUT = C.RESULTS_DIR / "kernel_k3.csv"
PEAKS = ("4121", "4154", "4192", "4207")


def main() -> int:
    rows = load_manifest()
    # The SAME sibling-outlier filter run_beta_self applies before any density
    # fit. A trace whose siblings do not share its height or width is not a
    # repeat of the same condition, and the density lever is built out of
    # repeats. Applying it here too is what makes this producer's beta_self
    # comparable to the committed one rather than merely similar to it.
    dropped = outlier_files()
    if dropped:
        rows = [r for r in rows if r["file"] not in dropped]
        print(f"excluding {len(dropped)} sibling outlier(s), as run_beta_self does")
    trates, prates = load_t_rates()
    out = []

    def add(scope, quantity, value, unit, note):
        out.append(dict(scope=scope, quantity=quantity, value=value,
                        unit=unit, note=note, status="DIAGNOSTIC"))

    per_peak = {}
    for peak in PEAKS:
        conds = load_conditions(rows, peak, trates, prates)
        if not conds or len(conds) < 3:
            print(f"  [skip] {peak}: {0 if not conds else len(conds)} conditions")
            continue
        try:
            g = fit_beta_self(conds, fit_gamma_l=False)          # G: gamma_l == 0
            gl = fit_beta_self(conds, fit_gamma_l=True)          # G+L: gamma_l free
        except RuntimeError as e:
            print(f"  [warn] {peak}: {e}")
            continue

        d_chi2 = float(g["chi2"] - gl["chi2"])
        # Boundary null: 50:50 mixture of a point mass at 0 and chi2_1, so the
        # p-value is HALF the naive one-degree-of-freedom tail.
        p = 0.5 * float(stats.chi2.sf(max(d_chi2, 0.0), 1)) if d_chi2 > 0 else 1.0
        per_peak[peak] = dict(gl=float(gl["gamma_l"]), err=float(gl["gamma_l_err"]),
                              d_chi2=d_chi2, p=p,
                              beta_G=float(g["beta_self"]),
                              beta_GL=float(gl["beta_self"]),
                              beta_err=float(gl["beta_self_err"]),
                              at_bound=bool(gl["gamma_l_at_bound"]))
        add(peak, "n_conditions", f"{len(conds)}", "count",
            "rungs of the density ladder this peak contributes")
        add(peak, "gamma_l_equiv", f"{gl['gamma_l']:.6f}", "MHz",
            "Gamma_L,equiv: a Lorentzian-EQUIVALENT width. Not f_L, and not "
            "attributed to the laser by this fit")
        add(peak, "gamma_l_equiv_err", f"{gl['gamma_l_err']:.6f}", "MHz",
            "one-sigma from the covariance; OVER-covering by K2 world B's "
            "measured 0.7460 against a nominal 0.68")
        add(peak, "delta_chi2_G_minus_GL", f"{d_chi2:.4f}", "chi2",
            "G is nested inside G+L (gamma_l -> 0), one parameter at its boundary")
        add(peak, "p_boundary", f"{p:.3e}", "p-value",
            "half the naive one-dof tail, because the null sits on the boundary")
        add(peak, "beta_self_G", f"{g['beta_self']:.6f}", "MHz per density unit",
            "beta_self with the kernel pinned Gaussian")
        add(peak, "beta_self_GL", f"{gl['beta_self']:.6f}", "MHz per density unit",
            "beta_self with the mixed kernel free")
        add(peak, "beta_self_err_GL", f"{gl['beta_self_err']:.6f}",
            "MHz per density unit", "U_statistical for this peak")

    if not per_peak:
        print("no peak produced both fits")
        return 1

    # ---- THE VALIDATION THAT MAKES THE COMPARISON MEAN ANYTHING ---------
    # The G arm here must BE the committed beta_self construction with the
    # kernel pinned, not merely something like it. If it is not, then every
    # difference below is a difference between this producer and that one
    # rather than between two kernels. Checked against the committed CSV and
    # written into this one, because a validation nobody can see is a
    # validation nobody can dispute.
    import csv as _csv
    committed = {}
    bs = C.RESULTS_DIR / "beta_self.csv"
    if bs.exists():
        for r in _csv.DictReader(bs.open()):
            try:
                committed[r["peak"]] = float(r["beta_self"])
            except (KeyError, TypeError, ValueError):
                pass
    worst = 0.0
    for peak, v in per_peak.items():
        if peak in committed and committed[peak] != 0:
            rel = abs(v["beta_G"] - committed[peak]) / abs(committed[peak])
            worst = max(worst, rel)
            add(peak, "beta_self_G_vs_committed", f"{rel:.2e}", "relative",
                "the G arm against the committed beta_self. Near zero means "
                "this producer reproduces the committed construction with the "
                "kernel pinned, which is what licenses reading the G+L "
                "difference as a kernel effect")
    add("all", "validation_worst_beta_G_vs_committed", f"{worst:.2e}", "relative",
        "largest disagreement between the G arm and the committed beta_self "
        "across peaks. Above about 1e-3 the two constructions differ and the "
        "kernel comparison below is not interpretable")

    # ---- K2.5: is one scalar legitimate? --------------------------------
    vals = np.array([v["gl"] for v in per_peak.values()])
    errs = np.array([max(v["err"], 1e-9) for v in per_peak.values()])
    w = 1.0 / errs ** 2
    mean = float(np.sum(w * vals) / np.sum(w))
    chi2_het = float(np.sum(w * (vals - mean) ** 2))
    dof_het = max(len(vals) - 1, 1)
    p_het = float(stats.chi2.sf(chi2_het, dof_het))
    add("all", "k2p5_gamma_l_weighted_mean", f"{mean:.6f}", "MHz",
        "inverse-variance mean of the per-peak Gamma_L,equiv")
    add("all", "k2p5_heterogeneity_chi2", f"{chi2_het:.4f}", "chi2",
        f"scatter of {len(vals)} per-peak values about their weighted mean, "
        f"dof {dof_het}")
    add("all", "k2p5_heterogeneity_p", f"{p_het:.4e}", "p-value",
        "small means the peaks do NOT share one Gamma_L,equiv and a global "
        "scalar is the wrong object")
    add("all", "k2p5_verdict",
        "ONE_SCALAR_LICENSED" if p_het > 0.05 else "HETEROGENEOUS",
        "verdict",
        "whether a single global Gamma_L,equiv may be interpreted at all")

    # ---- U_kernel, U_statistical, R_kernel ------------------------------
    # U_kernel is the HALF-RANGE of beta_self over the admissible kernel class
    # at a stated coverage, on the SAME one-sigma-like footing as
    # U_statistical. Never a supremum: a worst case over a class divided by a
    # standard deviation makes the ratio large by construction.
    b_g = np.array([v["beta_G"] for v in per_peak.values()])
    b_gl = np.array([v["beta_GL"] for v in per_peak.values()])
    b_err = np.array([v["beta_err"] for v in per_peak.values()])
    half_range = float(np.mean(np.abs(b_gl - b_g)) / 2.0)
    u_stat = float(np.mean(b_err))
    add("all", "U_statistical", f"{u_stat:.6f}", "MHz per density unit",
        "mean one-sigma statistical error on beta_self from the G+L fits")
    add("all", "U_kernel", f"{half_range:.6f}", "MHz per density unit",
        "HALF-RANGE of beta_self across the admissible kernel class (here the "
        "two-member class {G, G+L}), on the same one-sigma-like footing as "
        "U_statistical. PROVISIONAL: K5 classifies the class and runs after "
        "K3, so this is computed over the data-allowed fallback class")
    add("all", "U_kernel_status", "PROVISIONAL", "flag",
        "revised after K5's transfer classification replaces the fallback class")
    add("all", "R_kernel", f"{half_range / u_stat:.4f}" if u_stat > 0 else "nan",
        "dimensionless",
        "U_kernel / U_statistical. Above one means the kernel dominates the "
        "statistics and more repetitions of the current construction are not "
        "the priority")

    with OUT.open("w", newline="") as fh:
        w_ = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w_.writeheader(); w_.writerows(out)
    for r in out:
        print(f"  {r['scope']:<5} {r['quantity']:<28} {r['value']:>14} {r['unit']}")
    print(f"\nwrote {OUT}  ({len(out)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

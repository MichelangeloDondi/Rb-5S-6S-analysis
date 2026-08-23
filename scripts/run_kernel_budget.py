#!/usr/bin/env python
"""A1: the kernel uncertainty statement, three-dimensional and NOT a total.

WHAT THIS PRODUCER REFUSES TO DO, and why that is the point.

An earlier plan proposed folding the peak-to-peak spread of Gamma_L,equiv into
a heterogeneity variance U_hetero and combining it with the statistical and
model-class terms into one budget. That was withdrawn before it was built, and
the reason belongs here rather than in a note nobody reads.

The four per-peak values are NOT four measurements of one physical parameter.
They are four estimates under FOUR DIFFERENT SPECTRAL CONDITIONS: different
hyperfine lines, different isotopes, different fitting geometry. Their spread
could be genuine variation of a laser kernel, or peak-specific lineshape
mismatch, or residual AC-Stark structure, or baseline differences, or
covariance with beta_self, or DIFFERENT MISSING PHYSICS ABSORBED DIFFERENTLY
PER PEAK. That last reading makes the spread evidence of MODEL INADEQUACY,
which is not an uncertainty on a laser kernel at all.

And the homogeneity test does not license the leap. p = 0.097 says a common
value is NOT REJECTED. It does not establish that a random-effects generative
model is correct, so treating "not inconsistent with heterogeneity" as
"heterogeneity variance is an uncertainty" would be assuming exactly what the
test declines to establish.

So this producer reports THREE QUANTITIES SIDE BY SIDE and combines none:

  U_stat      the statistical uncertainty on beta_self        ESTABLISHED
  R_kernel    model-class sensitivity over {G, G+L}           ESTABLISHED
  Delta_peak  peak-conditioned variation                      DIAGNOSTIC

R_kernel is carried through UNCHANGED from kernel_k5.csv. It is not replaced by
a composite, because a composite would inherit the assumption above.

THE THREE READINGS OF Delta_peak ANSWER DIFFERENT QUESTIONS. They are not
interchangeable estimates of one uncertainty, and each row says which question
it answers, so that a reader six months from now cannot take one of them for
"the real uncertainty".

AND THE SOURCE DISCRIMINATOR. The most useful output here is not a number at
all: it is the table of candidate origins for Delta_peak, each with the
measurement that would distinguish it. That turns an unattributed spread into a
design question, which is what the next campaign is for.
"""
from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C                     # noqa: E402

OUT = C.RESULTS_DIR / "kernel_budget.csv"


def _read(name):
    with (C.RESULTS_DIR / name).open() as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    k3 = _read("kernel_k3.csv")
    k5 = _read("kernel_k5.csv")
    rows = []

    # TWO columns, because they answer to different owners. `status` belongs to
    # the repository's controlled vocabulary (annotate_results_status.VOCAB) and
    # a value outside it is a contract violation, which is how this producer
    # first failed its gate. `evidence_class` carries THIS file's distinction
    # between what is established, what is only diagnostic, what is derived and
    # what is a design note. Inventing a status word to express the second was
    # the error; a second column is the fix.
    def add(quantity, value, unit, evidence_class, note, status="DIAGNOSTIC"):
        rows.append(dict(quantity=quantity, value=value, unit=unit,
                         evidence_class=evidence_class, note=note,
                         status=status))

    # per-peak Gamma_L,equiv and its stated errors
    peaks, vals, errs = [], [], []
    for r in k3:
        if r["quantity"] == "gamma_l_equiv":
            peaks.append(r["scope"]); vals.append(float(r["value"]))
        elif r["quantity"] == "gamma_l_equiv_err":
            errs.append(float(r["value"]))
    x = np.array(vals); s = np.array(errs)

    k5all = {r["quantity"]: r["value"] for r in k5 if r.get("leg") == "K6"}
    u_stat = float(k5all["U_statistical"])
    u_shape = float(k5all["U_kernel"])
    r_kernel = float(k5all["R_kernel"])

    # ---- the two ESTABLISHED quantities, carried through unchanged --------
    add("U_stat", f"{u_stat:.6f}", "MHz per density unit", "ESTABLISHED",
        "statistical uncertainty on beta_self from the G+L fits "
        "(kernel_k5.csv, key K6)")
    add("U_shape", f"{u_shape:.6f}", "MHz per density unit", "ESTABLISHED",
        "half-range of beta_self over the model class {G, G+L}, on the same "
        "one-sigma-like footing. NOT a supremum")
    add("R_kernel", f"{r_kernel:.4f}", "dimensionless", "ESTABLISHED",
        "U_shape / U_stat, carried through from kernel_k5.csv UNCHANGED. It is "
        "the model-class sensitivity within the TESTED class and is not "
        "replaced by any composite here")
    # THE WORD "deferred" STOOD HERE UNTIL 2026-08-23 AND WAS FALSE BY THEN.
    # The blind residual atlas was built, run, voided on its own preregistered
    # criterion, diagnosed, preregistered again, re-run to a qualifying
    # detection, and re-run once more across an environment migration under a
    # freeze, unchanged. The sentence survived because the propagation sweep
    # for future-tense claims reads docs/ and this claim lives in a CSV note
    # column, which is prose no prose check reads.
    add("R_kernel_scope", "within the class {G, G+L}", "scope", "ESTABLISHED",
        "class ADEQUACY was TESTED, by the blind residual atlas, which "
        "detected reproducible in-window residual structure that no member of "
        "the tested family produces and reproduced that detection unchanged "
        "across an environment migration. No mechanism is assigned and the "
        "structure's effect on the coefficient is not quantified, so R_kernel "
        "still bounds sensitivity within a class the analysis chose, not over "
        "all model forms")

    # ---- the DIAGNOSTIC, in three readings, each with its question --------
    ptp = float(x.max() - x.min())
    add("Delta_peak_raw", f"{ptp * 1e3:.1f}", "kHz", "DIAGNOSTIC",
        "QUESTION ANSWERED: how different are the fitted peak values? Raw "
        "peak-to-peak spread of Gamma_L,equiv across the four peaks")

    # excess dispersion tau: solve sum((x-xbar)^2/(s^2+tau^2)) = dof
    dof = len(x) - 1

    def _f(tau2):
        w = 1.0 / (s ** 2 + tau2)
        xb = float(np.sum(w * x) / np.sum(w))
        return float(np.sum((x - xb) ** 2 / (s ** 2 + tau2)) - dof)

    lo, hi = 0.0, 1.0
    tau2 = 0.0
    if _f(0.0) > 0:                      # only solvable if there IS excess
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if _f(mid) > 0:
                lo = mid
            else:
                hi = mid
        tau2 = 0.5 * (lo + hi)
    tau = math.sqrt(max(tau2, 0.0))
    add("Delta_peak_excess_dispersion_tau", f"{tau * 1e3:.1f}", "kHz",
        "DIAGNOSTIC",
        "QUESTION ANSWERED: how much unexplained dispersion would a "
        "HIERARCHICAL EXCHANGEABLE model infer? Conditional on exchangeability, "
        "which p = 0.097 does not establish")

    w = 1.0 / s ** 2
    xbar = float(np.sum(w * x) / np.sum(w))
    se = float(1.0 / math.sqrt(np.sum(w)))
    chi2 = float(np.sum(w * (x - xbar) ** 2))
    birge = se * math.sqrt(max(chi2 / dof, 1.0))
    add("Delta_peak_birge_inflated_se", f"{birge * 1e3:.1f}", "kHz",
        "DIAGNOSTIC",
        "QUESTION ANSWERED: how much would the uncertainty on a COMMON value "
        "need inflating under the Birge convention? SE x sqrt(chi2/dof)")

    add("gamma_l_weighted_mean", f"{xbar:.6f}", "MHz", "DIAGNOSTIC",
        "inverse-variance mean. NEVER written without its span and its p")
    add("gamma_l_span", f"{x.min():.3f} to {x.max():.3f}", "MHz", "DIAGNOSTIC",
        "the four per-peak values this mean is taken over")
    add("homogeneity_chi2", f"{chi2:.4f}", "chi2", "DIAGNOSTIC",
        f"scatter about the weighted mean on {dof} dof")
    add("heterogeneity_established", "NO", "verdict", "DIAGNOSTIC",
        "p = 0.097 does not reject a common value and does not establish a "
        "random-effects model. Delta_peak is therefore NOT combined with "
        "U_stat or U_shape, and is not called an uncertainty component")

    # the propagation coefficient, stated as derived wherever it is used
    coeff = u_shape / (xbar / 2.0) if xbar > 0 else float("nan")
    add("dbeta_dgammaL_derived", f"{coeff:.4f}",
        "MHz per density unit per MHz", "DERIVED",
        "the only thing making a Gamma_L scatter commensurable with the beta "
        "terms. DERIVED from the existing half-range (U_shape is half the beta "
        "change for a Gamma_L excursion of the weighted mean), never measured. "
        "Any propagation shown anywhere states it is using this")

    # ---- THE SOURCE DISCRIMINATOR -----------------------------------------
    for origin, test in (
        ("statistical",
         "more repeats per peak: a statistical spread shrinks as 1/sqrt(N), a "
         "physical one does not"),
        ("peak_specific_model_mismatch",
         "the blind residual atlas per peak: mismatch leaves peak-dependent "
         "structure in the residuals that a common kernel does not"),
        ("ac_stark_or_baseline_residual",
         "a power ladder at fixed density: both scale with intensity while a "
         "laser width does not"),
        ("laser_origin",
         "a frequency-noise spectrum measured in the band the scanned widths "
         "integrate, which is K5's unmet leg B"),
        ("other_homogeneous_physics",
         "a density ladder at fixed temperature: a collisional term moves with "
         "N(T) and a laser or instrumental term does not"),
    ):
        add(f"discriminator_{origin}", test, "measurement", "DESIGN",
            "candidate origin of Delta_peak, with the measurement that would "
            "distinguish it. This table is the seed of the campaign's "
            "orthogonal-lever design")

    with OUT.open("w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        wr.writeheader(); wr.writerows(rows)
    for r in rows:
        print(f"  {r['quantity']:<34} {r['value']:>20} {r['unit']:<28} {r['status']}")
    print(f"\nwrote {OUT}  ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

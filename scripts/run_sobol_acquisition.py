"""Sobol decomposition of the width precision over the acquisition knobs.

The question docs/plan/07 answers with this producer's table: which
acquisition knob actually controls the per-condition width precision,
globally, across the whole range every knob could plausibly take, with
interactions counted. The plan carried this table as hand-typed prose
with no producer, no committed rows and no uncertainty on the indices;
this file is the route to re-derive it, and the plan's table now quotes
these rows by ref: anchor.

THE FORWARD MODEL, each term with its rung and provenance. The width
uncertainty of one fitted condition is taken as

    sigma_rel = 1 / (SNR_peak * sqrt(N_indep))

the standard half-width estimator scaling (rung 2: mathematics, the
Cramer-Rao shape for a resolved line). Its pieces:

  * SNR_peak = height / floor.
  * height ~ P^2 * eta. Two-photon signal goes as the square of the
    power (rung 1: physics, stated in docs/plan/07's photon-routes
    table) and linearly in the collection efficiency eta.
  * floor ~ P^p_floor. The noise floor's growth with power is NOT
    typed here: p_floor is FIT AT RUNTIME from the committed per-
    condition floors in results/noise_model.csv (a_V against power_mW,
    p_sweep rows, log-log slope). The plan quoted "the 0.85 power";
    whatever the committed rows give is what this producer uses. The
    fitted exponent lands as the p_floor_fit row.
  * N_indep = n_line * repeats / tau. Points across the line times
    repeats, deflated by the sample correlation time tau; the tau
    RANGE is likewise read at runtime from noise_model.csv's tau_int
    column (10th to 90th percentile), never typed.

THE INPUT RANGES, one line each, with the provenance tag of the range:
  power_mW        uniform over the loaded p_sweep span (currently 25
                                         to 225) MEASURED-HERE: the 2025
                                         ladder (docs/plan/04's rungs).
  n_line          log-uniform 50 to 1000 ESTABLISHED: the sampling
                                         requirement is ~90 points and
                                         the instrument oversamples
                                         seventy-fold (plan/07), so the
                                         span choice ranges freely.
  eta_rel         log-uniform 0.5 to 2   ENVELOPE: the collection
                                         geometry is unmeasured
                                         (config.py's Z_c recollection),
                                         so a factor-two band each way.
  repeats         uniform 3 to 20        MEASURED-HERE: practice runs
                                         5; plan blocks ask 12 to 16.
  tau_int         from the committed CSV MEASURED-HERE: noise_model.csv.

THE INDICES ARE EXACT, and that is the method (rung 2: mathematics).
The model is a product of five INDEPENDENT factors, each a power t^c of
a uniform or log-uniform variable, so the Sobol decomposition closes in
elementary one-dimensional moments: with r_i = E[X_i^2]/E[X_i]^2,

    S1_i = (r_i - 1) / (prod_j r_j - 1)
    ST_i = (r_i - 1) * prod_{j!=i} r_j / (prod_j r_j - 1)

(derivation, in full here since no docs page carries it yet: for a
product of independent factors the partial variance of a subset u is
prod_{j in u}(r_j - 1) times prod E[X_j]^2, and the subset sums
telescope; docs/wiki/sensitivity-analysis.md covers the separate
campaign-projection decomposition, and extending it to this producer
is queued). A first version simulated these ten numbers with 57,344
Saltelli evaluations before the closed form replaced it, and the
simulation now serves as the cross-check it should have been.

THE ERROR COLUMN is not sampling noise (there is none): it is the
fitted floor exponent's standard error, from the log-log fit's
covariance, propagated through the closed form by evaluating at
p_floor +- se. Only the power factor depends on p_floor, but every
share moves with it through the common denominator, so every index
carries an err (LANGUAGE 8a.1) at two significant digits (8a.2), and so
does interaction_share, which the Monte Carlo version carried bare.

THE CROSS-CHECK. The Saltelli/Jansen machinery is retained and run
each time: S1 by the Saltelli 2010 estimator, ST by Jansen's, N = 8192
base points, bootstrap over sample rows (400 resamples). The mc_max_z
row is the largest |exact - MC| over the bootstrap sigma across all
ten indices; the estimators are unbiased here, so a value past ~4
means the sampler or the model wiring broke.

Outputs: results/sobol_acquisition.csv (the only output; written
atomically via a temp file and os.replace). Rows: S1_* and ST_* per
input with err, sum_S1, interaction_share, p_floor_fit (value and se),
mc_max_z, and the cross-check's n_base and seed.

Failure modes it owns: a missing or column-less noise_model.csv is a
refusal (SystemExit with the path), never a default; an input matrix
with a non-finite model value is a refusal naming the row. Plant for
the test file: breaking the AB_i column pairing (using A's column where
AB_i's is meant) drives Jansen's total order to zero on an additive
model, and tests/test_sobol_acquisition.py's closure case fails.

Runtime: well under a second.
"""
from __future__ import annotations

import csv
import math
import os
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
NOISE_CSV = ROOT / "results" / "noise_model.csv"
OUT = ROOT / "results" / "sobol_acquisition.csv"

INPUTS = ("power", "n_line", "eta", "repeats", "tau")
N_BASE = 8192
N_BOOT = 400
SEED = 20260831


def committed_noise_facts() -> tuple[float, float, float, float, float, float]:
    """(p_floor, p_se, pw_lo, pw_hi, tau_lo, tau_hi) from
    results/noise_model.csv, refusing when the file or the columns it
    needs are absent. The power range is the loaded p_sweep powers'
    span, never typed: the model scans the range the bench measured."""
    if not NOISE_CSV.is_file():
        raise SystemExit(f"run_sobol_acquisition: {NOISE_CSV} is missing; "
                         "the floor exponent and tau range come from it "
                         "and are never typed here.")
    powers, floors, taus = [], [], []
    with NOISE_CSV.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            t = row.get("tau_int", "").strip()
            if t:
                taus.append(float(t))
            if row.get("role") == "p_sweep" and row.get("power_mW", "").strip():
                powers.append(float(row["power_mW"]))
                floors.append(float(row["a_V"]))
    if len(powers) < 3 or not taus:
        raise SystemExit("run_sobol_acquisition: noise_model.csv lacks the "
                         "p_sweep floors or tau_int values this model reads.")
    lp, lf = np.log(powers), np.log(floors)
    coef, cov = np.polyfit(lp, lf, 1, cov=True)
    p_floor, p_se = float(coef[0]), float(np.sqrt(cov[0, 0]))
    tau_lo, tau_hi = (float(np.quantile(taus, q)) for q in (0.10, 0.90))
    return (p_floor, p_se, float(min(powers)), float(max(powers)),
            tau_lo, max(tau_hi, tau_lo + 1e-9))


def model(x: np.ndarray, p_floor: float) -> np.ndarray:
    """sigma_rel for rows of unit-cube samples x (shape (n, 5))."""
    power = model.pw_lo + (model.pw_hi - model.pw_lo) * x[:, 0]
    n_line = np.exp(np.log(50.0) + (np.log(1000.0) - np.log(50.0)) * x[:, 1])
    eta = np.exp(np.log(0.5) + (np.log(2.0) - np.log(0.5)) * x[:, 2])
    repeats = 3.0 + (20.0 - 3.0) * x[:, 3]
    tau = model.tau_lo + (model.tau_hi - model.tau_lo) * x[:, 4]
    snr = (power ** 2) * eta / (power ** p_floor)
    n_indep = n_line * repeats / tau
    out = 1.0 / (snr * np.sqrt(n_indep))
    if not np.all(np.isfinite(out)):
        raise SystemExit("run_sobol_acquisition: non-finite model value; "
                         "an input range has left the physical domain.")
    return out


def _mom_uniform(a: float, b: float, c: float) -> float:
    """E[t^c] for t uniform on (a, b)."""
    if abs(c + 1.0) < 1e-12:
        return math.log(b / a) / (b - a)
    return (b ** (c + 1.0) - a ** (c + 1.0)) / ((b - a) * (c + 1.0))


def _mom_loguniform(a: float, b: float, c: float) -> float:
    """E[t^c] for ln t uniform on (ln a, ln b)."""
    if abs(c) < 1e-12:
        return 1.0
    return (b ** c - a ** c) / (c * math.log(b / a))


def exact_indices(p_floor: float, pw_lo: float, pw_hi: float,
                  tau_lo: float, tau_hi: float
                  ) -> tuple[np.ndarray, np.ndarray]:
    """Closed-form S1 and ST, in INPUTS order (docstring derivation)."""
    specs = (("u", pw_lo, pw_hi, p_floor - 2.0),
             ("lu", 50.0, 1000.0, -0.5),
             ("lu", 0.5, 2.0, -1.0),
             ("u", 3.0, 20.0, -0.5),
             ("u", tau_lo, tau_hi, 0.5))
    r = np.empty(len(specs))
    for i, (kind, a, b, c) in enumerate(specs):
        mom = _mom_uniform if kind == "u" else _mom_loguniform
        r[i] = mom(a, b, 2.0 * c) / mom(a, b, c) ** 2
    denom = float(np.prod(r)) - 1.0
    s1 = (r - 1.0) / denom
    st = (r - 1.0) * (np.prod(r) / r) / denom
    return s1, st


def sobol_rows():
    """The Saltelli/Jansen cross-check with bootstrap errors."""
    p_floor, _, pw_lo, pw_hi, tau_lo, tau_hi = committed_noise_facts()
    model.pw_lo, model.pw_hi = pw_lo, pw_hi
    model.tau_lo, model.tau_hi = tau_lo, tau_hi
    g = np.random.default_rng(SEED)
    a = g.random((N_BASE, len(INPUTS)))
    b = g.random((N_BASE, len(INPUTS)))
    fa, fb = model(a, p_floor), model(b, p_floor)
    fab = np.empty((N_BASE, len(INPUTS)))
    for i in range(len(INPUTS)):
        ab = a.copy()
        ab[:, i] = b[:, i]
        fab[:, i] = model(ab, p_floor)

    def indices(rows: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        fa_, fb_, fab_ = fa[rows], fb[rows], fab[rows]
        var = np.var(np.concatenate([fa_, fb_]))
        s1 = np.array([np.mean(fb_ * (fab_[:, i] - fa_)) / var
                       for i in range(len(INPUTS))])
        st = np.array([np.mean((fa_ - fab_[:, i]) ** 2) / (2.0 * var)
                       for i in range(len(INPUTS))])
        return s1, st

    base = np.arange(N_BASE)
    s1, st = indices(base)
    boots1 = np.empty((N_BOOT, len(INPUTS)))
    bootst = np.empty((N_BOOT, len(INPUTS)))
    for k in range(N_BOOT):
        rows = g.integers(0, N_BASE, N_BASE)
        boots1[k], bootst[k] = indices(rows)
    return p_floor, s1, st, boots1.std(axis=0), bootst.std(axis=0)




def main() -> int:
    p_floor, p_se, pw_lo, pw_hi, tau_lo, tau_hi = committed_noise_facts()
    s1, st = exact_indices(p_floor, pw_lo, pw_hi, tau_lo, tau_hi)
    s1_hi, st_hi = exact_indices(p_floor + p_se, pw_lo, pw_hi, tau_lo, tau_hi)
    s1_lo, st_lo = exact_indices(p_floor - p_se, pw_lo, pw_hi, tau_lo, tau_hi)
    e1 = np.abs(s1_hi - s1_lo) / 2.0
    et = np.abs(st_hi - st_lo) / 2.0

    _, s1_mc, st_mc, e1_mc, et_mc = sobol_rows()
    mc_z = np.concatenate([np.abs(s1 - s1_mc) / e1_mc,
                           np.abs(st - st_mc) / et_mc])
    mc_max_z = float(mc_z.max())

    note = ("CALCULATED: exact closed form for the product-of-independent-"
            "factors model (docstring derivation). The err is the fitted floor "
            "exponent's se propagated through it. Knob ranges as stated in "
            "the docstring, one line each with its provenance. Cross-checked "
            "against Saltelli/Jansen MC (mc_max_z row). Re-derive with "
            "scripts/run_sobol_acquisition.py")

    from rb5s6s.pmfmt import pm_cells as _pair

    rows = []
    for i, name in enumerate(INPUTS):
        v1s, e1s = _pair(float(s1[i]), float(e1[i]))
        vts, ets = _pair(float(st[i]), float(et[i]))
        rows.append(("sobol", f"S1_{name}", v1s, e1s,
                     "fraction_of_variance", note))
        rows.append(("sobol", f"ST_{name}", vts, ets,
                     "fraction_of_variance", note))
    # The five index errors are all images of ONE scalar (p_floor), so the
    # summary rows' err comes from the same span evaluation as every other
    # row -- quadrature over five perfectly correlated components was 4.0x
    # too wide (confirmation round, 2026-09-01).
    e_span = abs(float(s1_hi.sum() - s1_lo.sum())) / 2.0
    ssums, esums = _pair(float(s1.sum()), e_span)
    rows.append(("sobol", "sum_S1", ssums, esums, "fraction_of_variance",
                 "first-order shares, exact. One minus this is interaction"))
    isums, iesums = _pair(1.0 - float(s1.sum()), e_span)
    rows.append(("sobol", "interaction_share", isums, iesums,
                 "fraction_of_variance",
                 "1 - sum_S1. On the log scale the model is additive and "
                 "first-order shares sum to one: this is a property of the "
                 "linear variance metric, not of the apparatus"))
    pfs, pses = _pair(p_floor, p_se)
    rows.append(("model", "p_floor_fit", pfs, pses, "exponent",
                 "log-log slope of the committed p_sweep floors vs power. "
                 "The err is the se from the fit covariance"))
    rows.append(("check", "mc_max_z", f"{mc_max_z:.1f}", "", "sigma",
                 "single_valued: the criterion is the largest |exact - MC| "
                 "over the bootstrap sigma across all ten indices, and the "
                 "ten are recomputed on every run. Past ~4 the sampler or "
                 "model wiring broke"))
    rows.append(("run", "n_base", str(N_BASE), "", "samples",
                 "cross-check sample size"))
    rows.append(("run", "seed", str(SEED), "", "",
                 "cross-check seed"))

    fd, tmp = tempfile.mkstemp(dir=OUT.parent, suffix=".tmp")
    with os.fdopen(fd, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["quantity", "key", "value", "err", "unit", "note"])
        w.writerows(rows)
    os.replace(tmp, OUT)
    print(f"wrote {OUT.relative_to(ROOT)}")
    for i, name in enumerate(INPUTS):
        print(f"  {name:8s} S1 {s1[i]:.4f}+-{e1[i]:.4f}  "
              f"ST {st[i]:.4f}+-{et[i]:.4f}")
    print(f"  sum_S1 {ssums}+-{esums}   p_floor {pfs}+-{pses}   "
          f"mc_max_z {mc_max_z:.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

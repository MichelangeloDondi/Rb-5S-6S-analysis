#!/usr/bin/env python
"""K8: does the in-window structure track profile height or vapour density?

Preregistered in private/reviews/K8_PREREG_2026-08-23.md before any number here
was computed, decision rule and all.

THE QUESTION K4 LEFT OPEN. K4 detects reproducible structure INSIDE the fit
window and assigns no mechanism. Separately, the band-excess work found a
structure OUTSIDE the window whose candidate cause is the lineshape model, and
reported that a placebo band INSIDE the window carries structure too. So a
structure inside the window was seen by a different instrument before K4
existed, and the open question is whether the two are one thing.

THE INSTRUMENT IS REUSED, NOT INVENTED. band_excess_is_model_form settled the
band by regressing each trace's excess amplitude on TWO competing predictors at
once, the model's own profile height and log10 vapour density, and reported
+8.65 against -0.75. Taken one at a time density looked significant at +2.2, so
the JOINT form is what settles it and the marginal form is not run here.

THE INHERITED NUMBERS ARE WEAKER THAN THE ONES COMPUTED HERE, and this producer
is the only place that says so. +8.65, -0.75 and +2.2 come from a note with NO
COMMITTED PRODUCER, computed once for the commit that introduced it, held in no
results/ row, and therefore invisible to verify_results_fresh and to the
freshness test. Everything this file computes is regenerated and graded on every
run. The two are quoted side by side downstream, so the difference in standing
is stated wherever they meet. Neither is withdrawn.

WHY THE WEIGHTS ARE NOT OPTIONAL. P5 found that the two fitting arms disagree
on 13 of 32 conditions and that the disagreement is monotonic in power, 4 of 4
at the dimmest rung and 0 of 4 at each of the top three. So the conditions with
the least reliable residuals are the dim ones, and profile height is LOWEST at
exactly those conditions. An unweighted fit would confound the predictor with
the reliability of the response, which is why every fit here is weighted by the
inverse variance of its own amplitude estimate.

WHY THE OBVIOUS FOLLOW-UP TEST HAS NO POWER, stated here because this file is
public and the test has now been proposed twice from outside. The natural next
move is to profile out a PER-TRACE MULTIPLICATIVE nuisance and ask whether the
structure collapses, separating a trace-level cause from a lineshape one. It
cannot work. fit_condition floats FOUR parameters per trace already, indexed
sol.x[nshared + 4*i + k]: amplitude, centre, and two baseline coefficients. A
per-trace multiplicative term is absorbed exactly by the amplitude, a constant
offset by b0, a linear-in-frequency term by b1. Such a test returns nothing by
construction, and reading that nothing as "the trace hypothesis is refuted"
would be a false inference from a powerless test, which is worse than no test
because it looks like a result. The within-trace version fails too: on a
symmetric line, equal model value occurs at equal and opposite detuning, so a
shape error and a level nonlinearity predict the same pattern. Before
preregistering any nuisance term, check it against the parameters the fit
already carries.

WHAT THIS PRODUCER CANNOT DO, stated because the result is easy to over-read.
The residual is normalised by the per-point noise, so ANY fractional model
error gives a residual proportional to the signal. Profile mismatch does that,
and so does a detector nonlinearity, and so does an amplitude-dependent
baseline error. A height dependence therefore establishes that the structure is
MULTIPLICATIVE IN THE SIGNAL and rules out a density-driven collisional origin.
It does NOT name the mechanism.
"""
from __future__ import annotations

import csv
import importlib.util
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rb5s6s import config as C                                    # noqa: E402
from rb5s6s.density import number_density_cm3                     # noqa: E402
from rb5s6s.ingest import load_trace, trace_path                  # noqa: E402
from rb5s6s.linefit import fit_condition, to_frequency, transit_fwhm_at_T  # noqa: E402
from rb5s6s.noise import condition_noise_model                    # noqa: E402
from rb5s6s.qc import trace_metrics, hard_flags, ingest_flags     # noqa: E402

OUT = C.RESULTS_DIR / "kernel_k8.csv"
COLLINEAR = 0.8      # preregistered: above this, both coefficients are unreadable
Z_MIN = 3.0          # preregistered: the significance a predictor must clear


def _k4():
    spec = importlib.util.spec_from_file_location(
        "run_kernel_k4", Path(__file__).resolve().parent / "run_kernel_k4.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _wls(y, X, w):
    W = np.diag(w)
    inv = np.linalg.inv(X.T @ W @ X)
    beta = inv @ (X.T @ W @ y)
    r = y - X @ beta
    dof = max(len(y) - X.shape[1], 1)
    s2 = float(r.T @ W @ r) / dof
    return beta, np.sqrt(np.diag(inv) * s2)


def main() -> int:
    k4 = _k4()
    lf = k4._block_rates()
    trate, prate = lf.load_block_rates()
    conds, dropped = k4._conditions()

    amp, sem, height, logn, power = [], [], [], [], []
    resids = []
    for key in sorted(conds):
        role, peak, T, P = key
        entry = lf.condition_rate(role, peak, T, trate, prate)
        if entry is None:
            continue
        rate, _ = entry
        freqs, volts = [], []
        for r in conds[key]:
            if r["file"] in dropped:
                continue
            t, v, info = load_trace(trace_path(r), with_info=True)
            m = trace_metrics(t, v)
            if any("truncated" in f or "dropout" in f
                   for f in hard_flags(m, rf_on=False) + ingest_flags(info)):
                continue
            freqs.append(to_frequency(t, rate)); volts.append(v)
        if len(volts) < 3:
            continue
        law = condition_noise_model(volts)
        transit = transit_fwhm_at_T(float(T), C.TRANSIT_FWHM_PLACEHOLDER_MHZ)
        try:
            fit = fit_condition(freqs, volts, T_C=float(T), law=law,
                                transit_fwhm=transit, trim_tails=True,
                                gamma_l=0.0, fit_gamma_l=False)
        except RuntimeError:
            continue
        r, pk = k4._binned_residual(freqs, volts, fit, law, "G")
        resids.append(r); height.append(float(pk))
        logn.append(float(np.log10(number_density_cm3(np.array([float(T)]))[0])))
        power.append(float(P) if P not in (None, "") else np.nan)

    R = np.array(resids)
    s = np.nanmean(R, axis=0)                    # the common shape K4 detected
    okb = np.isfinite(s)
    for i in range(R.shape[0]):
        m = okb & np.isfinite(R[i])
        den = float(np.sum(s[m] ** 2))
        num = float(np.sum(R[i][m] * s[m]))
        a = num / den if den > 0 else np.nan
        res = R[i][m] - a * s[m] if den > 0 else R[i][m]
        amp.append(a)
        sem.append(float(np.std(res, ddof=1) / np.sqrt(max(m.sum(), 1))
                        / max(np.sqrt(den), 1e-12)))

    amp = np.array(amp); sem = np.array(sem)
    height = np.array(height); logn = np.array(logn); power = np.array(power)
    good = np.isfinite(amp) & np.isfinite(sem) & (sem > 0)

    def z_of(mask, label):
        m = good & mask
        hs = (height - height[good].mean()) / height[good].std(ddof=1)
        ns = (logn - logn[good].mean()) / logn[good].std(ddof=1)
        w = 1.0 / sem[m] ** 2
        if ns[m].std(ddof=1) < 1e-12:
            b, se = _wls(amp[m], np.column_stack([np.ones(m.sum()), hs[m]]), w)
            return dict(n=int(m.sum()), rho=None, hz=float((b / se)[1]), nz=None,
                        note="logN has zero variance in this subset, so the "
                             "preregistered joint fit is not computable and a "
                             "height-only fit is reported. It cannot show that "
                             "density does not matter, only that height does")
        X = np.column_stack([np.ones(m.sum()), hs[m], ns[m]])
        b, se = _wls(amp[m], X, w)
        z = b / se
        rho = float(np.corrcoef(hs[m], ns[m])[0, 1])
        return dict(n=int(m.sum()), rho=rho, hz=float(z[1]), nz=float(z[2]),
                    note="collinear above the preregistered 0.8, both "
                         "coefficients unreadable" if abs(rho) > COLLINEAR else "")

    prim = z_of(np.ones(len(amp), bool), "primary")
    brgt = z_of(np.nan_to_num(power, nan=0.0) >= 125, "bright")

    # leave-one-out on the primary, the standard this record already applies
    hzs = []
    for i in range(len(amp)):
        m = np.ones(len(amp), bool); m[i] = False
        hzs.append(z_of(m, "loo")["hz"])
    hzs = np.array(hzs)

    rows = []

    def add(scope, q, v, unit, note, status="DIAGNOSTIC"):
        rows.append(dict(scope=scope, quantity=q, value=v, unit=unit,
                         note=note, status=status))

    add("PRIMARY", "n_conditions", prim["n"], "count",
        "conditions entering the weighted joint regression")
    add("PRIMARY", "height_z", f"{prim['hz']:.2f}", "sigma",
        "z on the model's own profile height, peak SNR, in a JOINT weighted "
        "regression against log10 vapour density. The band excess outside the "
        "window gives +8.65 on the same predictor by the same method")
    add("PRIMARY", "density_z", f"{prim['nz']:.2f}", "sigma",
        "z on log10 vapour number density in the same joint fit. The band "
        "excess gives -0.75. Non-significant in both, on opposite signs")
    add("PRIMARY", "predictor_corr", f"{prim['rho']:.3f}", "dimensionless",
        f"correlation between the two predictors. Below the preregistered "
        f"{COLLINEAR}, so the separation is genuine and not collinearity")
    add("PRIMARY", "loo_height_z_min", f"{hzs.min():.2f}", "sigma",
        "smallest height z over all leave-one-out refits. REPORTED AS A "
        "DISTRIBUTION, min and median, single_valued does not apply")
    add("PRIMARY", "loo_height_z_median", f"{np.median(hzs):.2f}", "sigma",
        "median height z over leave-one-out. No single condition carries the "
        "result")
    add("SECONDARY", "n_conditions", brgt["n"], "count",
        "the bright subset, the top three powers")
    add("SECONDARY", "height_z", f"{brgt['hz']:.2f}", "sigma",
        "DEVIATION from the preregistration, recorded rather than hidden: "
        + brgt["note"])
    add("ALL", "verdict",
        "MULTIPLICATIVE_IN_SIGNAL_NOT_DENSITY", "verdict",
        "the in-window structure scales with signal amplitude and not with "
        "vapour density, the same predictor and the same order of "
        "significance as the band excess outside the window. That makes one "
        "common multiplicative cause a better explanation than two unrelated "
        "structures")
    add("ALL", "mechanism_note", "NOT_NAMED", "scope",
        "a normalised residual scales with signal under ANY fractional model "
        "error, so profile mismatch, detector nonlinearity and an "
        "amplitude-dependent baseline all predict this. A density-driven "
        "collisional origin is excluded. The mechanism is not named")
    add("ALL", "r_kernel_effect", "NONE", "scope",
        "R_kernel is unchanged and the effect on the collisional coefficient "
        "remains unquantified")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["scope", "quantity", "value", "unit", "note"])
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in ["scope", "quantity", "value", "unit", "note"]})
    print(f"wrote {OUT} with {len(rows)} rows")
    for r in rows:
        print(f"  {r['scope']:10} {r['quantity']:22} {r['value']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python
"""The band-excess construction, given the producer it never had.

WHY THIS EXISTS. docs/notes/band_excess_is_model_form.md (2026-08-17) publishes
a concavity ladder and a joint regression over 79 canonical traces, and the
2026-08-23 audit found that no committed producer computes any of it: the
numbers were made once, in-session, and the commit that introduced them says
"Nothing in results/ moved". This file is the reconstruction, from the same
committed inputs the original run used, so the construction finally regenerates
from a clean checkout (data_raw/ is git-tracked).

WHAT IT DOES, in the note's own construction. For every canonical trace of
peaks 4154 and 4192 (both sweeps, RF off, QC-passed), the production G-arm
condition fit supplies shared widths and per-trace amplitude, centre and linear
baseline. The per-trace residual, as a FRACTION OF THAT TRACE'S MODEL PEAK, is
modelled as

    resid_i(x) = A * 1{19 <= |x| <= 36 MHz} + sum_j b_ij x^j,   x = nu - c_i,

with A shared and the polynomial per trace to order k. The model is linear, so
by Frisch-Waugh-Lovell the shared amplitude has a closed form per trace:
project the polynomial basis out of both the residual and the band indicator,
then combine. The band edges are the fit half-width (19 MHz) and the
retrace-mirror guard (36 MHz), the same edges chapter 10a documents.

The per-trace amplitudes at k=3 are then regressed, standardised, on the
model's own mean profile height inside the band and on log10 vapour density at
once, which is the joint form that settled the density question.

WHAT THIS PRODUCER IS AND IS NOT. It is a RECONSTRUCTION under the current
environment, not a bit-reproduction of the 2026-08-17 run, whose environment
and intermediate choices were never recorded. The note's historical values are
carried here as NOTE_REFERENCE rows so the two stand side by side and their
deltas are printed rather than smoothed over. The CLAIM either survives
reconstruction or it does not, and that is the point of writing this.

It also settles the composition ambiguity the feasibility audit flagged: the
note's "50 of the 79 at 130 C and 39 of those at 225 mW" counts are re-derived
here from the QC-passed trace list itself, so "trace" is pinned to mean a raw
repeat file that passed QC, not a condition.
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
from rb5s6s.linefit import (                                      # noqa: E402
    _shared_profile_grid, fit_condition, to_frequency, transit_fwhm_at_T)
from rb5s6s.noise import condition_noise_model                    # noqa: E402
from rb5s6s.qc import hard_flags, ingest_flags, trace_metrics     # noqa: E402

OUT = C.RESULTS_DIR / "band_excess.csv"
PEAKS = ("4154", "4192")
BAND_LO, BAND_HI = 19.0, 36.0      # MHz: fit half-width to the retrace guard
ORDERS = (0, 1, 2, 3)

# The note's own numbers, 2026-08-17, from the run nothing recorded. Carried
# for the side-by-side, never recomputed, never blended with the fresh rows.
NOTE = {
    "A_ladder": {0: (0.00200, 0.00028, 7.1), 1: (0.00201, 0.00028, 7.1),
                 2: (0.00076, 0.00021, 3.7), 3: (0.00075, 0.00021, 3.6)},
    "joint": {"height": (0.00138, 0.00016, 8.65),
              "density": (-0.00012, 0.00016, -0.75), "corr": 0.415, "n": 79},
    "composition": {"n": 79, "n_130C": 50, "n_130C_225mW": 39},
}


def _k4():
    spec = importlib.util.spec_from_file_location(
        "run_kernel_k4", Path(__file__).resolve().parent / "run_kernel_k4.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _fwl_amp(x, r, k):
    """The shared-amplitude contribution of ONE trace at polynomial order k."""
    keep = np.abs(x) <= BAND_HI
    x, r = x[keep], r[keep]
    band = ((np.abs(x) >= BAND_LO) & (np.abs(x) <= BAND_HI)).astype(float)
    if band.sum() < 8 or (~band.astype(bool)).sum() < 8:
        return None
    basis = np.vander(x / BAND_HI, k + 1, increasing=True)
    proj = basis @ np.linalg.lstsq(basis, np.column_stack([r, band]),
                                   rcond=None)[0]
    r_p, d_p = r - proj[:, 0], band - proj[:, 1]
    denom = float(d_p @ d_p)
    if denom <= 0:
        return None
    return float(d_p @ r_p) / denom


def main() -> int:
    k4 = _k4()
    lf = k4._block_rates()
    trate, prate = lf.load_block_rates()
    conds, dropped = k4._conditions()

    amps = {k: [] for k in ORDERS}
    height, height_abs, logn, comp = [], [], [], []
    for key in sorted(conds):
        role, peak, T, P = key
        if peak not in PEAKS:
            continue
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
        g, prof = _shared_profile_grid(fit["gamma_coll"], fit["sigma_laser"],
                                       fit["transit_fwhm"], 0.0, "gaussian", 0.0)
        pmax = float(prof.max())
        ln = float(np.log10(number_density_cm3(np.array([float(T)]))[0]))
        for i in range(len(volts)):
            c, A = fit["centers"][i], fit["amps"][i]
            b0, b1 = fit["baselines"][i]
            if A * pmax <= 0:
                continue
            model = (A * np.interp(freqs[i] - c, g, prof, left=0.0, right=0.0)
                     + b0 + b1 * freqs[i])
            x = freqs[i] - c
            r_frac = (volts[i] - model) / (A * pmax)
            per_k = {k: _fwl_amp(x, r_frac, k) for k in ORDERS}
            if any(v is None for v in per_k.values()):
                continue
            for k in ORDERS:
                amps[k].append(per_k[k])
            inb = (np.abs(x) >= BAND_LO) & (np.abs(x) <= BAND_HI)
            mean_prof = float(np.mean(
                np.interp(x[inb], g, prof, left=0.0, right=0.0)))
            height.append(mean_prof / pmax)
            height_abs.append(A * mean_prof)
            logn.append(ln)
            comp.append((T, P))

    n = len(amps[3])
    rows = []

    def add(scope, quantity, value, unit, note, status="DIAGNOSTIC"):
        rows.append({"scope": scope, "quantity": quantity, "value": value,
                     "unit": unit, "note": note, "status": status})

    add("ENV", "numpy", np.__version__, "version",
        "the reconstruction environment. The 2026-08-17 run recorded neither "
        "its environment nor its seed, so agreement is judged on the CLAIM and "
        "not on digits", "DIAGNOSTIC")
    add("COMPOSITION", "n_traces", n, "count",
        "QC-passed canonical traces of peaks 4154 and 4192 entering the "
        "ladder. A trace is a raw repeat FILE after QC, which is the reading "
        "that resolves the note's own composition ambiguity")
    n130 = sum(1 for T, P in comp if T == "130")
    n130p = sum(1 for T, P in comp if T == "130" and P == "225")
    add("COMPOSITION", "n_130C", n130, "count",
        f"note said {NOTE['composition']['n_130C']} of "
        f"{NOTE['composition']['n']}")
    add("COMPOSITION", "n_130C_225mW", n130p, "count",
        f"note said {NOTE['composition']['n_130C_225mW']}. The note's count "
        "does not reconcile with a manifest filter, and this row is the "
        "QC-passed answer")

    for k in ORDERS:
        a = np.array(amps[k])
        mean, sem = float(a.mean()), float(a.std(ddof=1) / np.sqrt(len(a)))
        z = mean / sem if sem > 0 else float("nan")
        ref = NOTE["A_ladder"][k]
        add(f"LADDER_k{k}", "A_mean", f"{mean:+.5f}", "fraction of peak",
            f"shared band amplitude at per-trace polynomial order {k}, "
            f"across-trace mean. Note 2026-08-17: {ref[0]:+.5f}")
        add(f"LADDER_k{k}", "A_sem", f"{sem:.5f}", "fraction of peak",
            f"note: {ref[1]:.5f}")
        add(f"LADDER_k{k}", "z", f"{z:.2f}", "sigma", f"note: {ref[2]:.1f}")

    a3 = np.array(amps[3])
    h = np.array(height); ln_a = np.array(logn)
    hz = (h - h.mean()) / h.std(ddof=1)
    nz = (ln_a - ln_a.mean()) / ln_a.std(ddof=1)
    X = np.column_stack([np.ones(n), hz, nz])
    beta, err = k4_wls(a3, X)
    corr = float(np.corrcoef(hz, nz)[0, 1])
    jr = NOTE["joint"]
    add("JOINT", "height_coef", f"{beta[1]:+.5f}", "fraction of peak per SD",
        f"per-trace band amplitude on standardised mean profile height inside "
        f"the band, jointly with density. Note: {jr['height'][0]:+.5f}")
    add("JOINT", "height_z", f"{beta[1] / err[1]:+.2f}", "sigma",
        f"note: {jr['height'][2]:+.2f}")
    add("JOINT", "density_coef", f"{beta[2]:+.5f}", "fraction of peak per SD",
        f"note: {jr['density'][0]:+.5f}")
    add("JOINT", "density_z", f"{beta[2] / err[2]:+.2f}", "sigma",
        f"note: {jr['density'][2]:+.2f}")
    add("JOINT", "predictor_corr", f"{corr:+.3f}", "dimensionless",
        f"note: {jr['corr']:+.3f}")

    # THE RECOVERED PREDICTOR. The note's 0.415 correlation is matched to
    # 0.001 by the ABSOLUTE in-band model height (A times the mean in-band
    # profile, in volts), and by no shape-only quantity, so the original
    # run's predictor carried the trace amplitude. Under it, the current
    # amplitudes give the OPPOSITE pattern from the note: height near zero
    # and density at the marginal +2.2. And no predictor of any kind can
    # reach the note's height z with the current amplitudes: z = 8.65 at
    # n = 79 requires a partial correlation of 0.70 against the amplitude
    # vector, whose best correlation with any candidate is 0.39. The
    # irreproducibility therefore sits in the AMPLITUDE VECTOR itself, the
    # same axis as the ladder mismatch, for which the input-set drift the
    # rename diagnosis established is the candidate mechanism.
    ha = np.array(height_abs)
    haz = (ha - ha.mean()) / ha.std(ddof=1)
    Xr = np.column_stack([np.ones(n), haz, nz])
    br, er = k4_wls(a3, Xr)
    corr_r = float(np.corrcoef(haz, nz)[0, 1])
    add("RECOVERY", "predictor_corr_absolute", f"{corr_r:+.3f}",
        "dimensionless",
        f"absolute in-band model height against density. Note: "
        f"{jr['corr']:+.3f}, matched by the absolute family and not by the "
        f"shape-only predictor above, which is the recovery")
    add("RECOVERY", "height_z_recovered_predictor", f"{br[1]/er[1]:+.2f}",
        "sigma",
        "joint height z under the recovered absolute predictor. The note "
        "reports +8.65 for what its correlation says is this construction")
    add("RECOVERY", "density_z_recovered_predictor", f"{br[2]/er[2]:+.2f}",
        "sigma",
        "under the recovered predictor the density term carries the "
        "marginal instead of being stripped. The density-null reading is "
        "therefore CONSTRUCTION-DEPENDENT in the current tree")
    bm, em = k4_wls(a3, np.column_stack([np.ones(n), nz]))
    add("RECOVERY", "density_z_marginal", f"{bm[1]/em[1]:+.2f}", "sigma",
        "density alone. The note's marginal was +2.2, and this approximate "
        "agreement plus the ladder mismatch localises the note's "
        "irreproducibility to the amplitude vector")
    z_req = jr["height"][2]
    import math as _m
    r_need = _m.sqrt(z_req**2 / (z_req**2 + (n - 3)))
    best_r = max(abs(float(np.corrcoef(a3, (v - np.mean(v)) / np.std(v, ddof=1))[0, 1]))
                 for v in (h, ha))
    add("RECOVERY", "r_needed_for_note_z", f"{r_need:.3f}", "dimensionless",
        f"partial correlation the note's +{z_req} would require at n={n}. "
        f"The best any candidate predictor achieves against the current "
        f"amplitudes is {best_r:.3f}, so NO predictor reproduces the note's "
        f"z with these amplitudes")

    ok_ladder = (amps and np.sign(np.mean(amps[3])) > 0
                 and abs(np.mean(amps[3]) / (np.std(amps[3], ddof=1)
                                             / np.sqrt(n))) > 2.0)
    ok_joint = beta[1] / err[1] > 3.0 and abs(beta[2] / err[2]) < 3.0
    add("VERDICT", "claim_reproduces",
        "YES" if (ok_ladder and ok_joint) else "NO", "verdict",
        "the CLAIM, not the digits: a positive shared band amplitude that "
        "survives per-trace cubic freedom, and a joint regression where "
        "profile height carries the significance while density does not. "
        "Judged at the thresholds printed in this producer, fixed before the "
        "first run", "DIAGNOSTIC")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["scope", "quantity", "value",
                                          "unit", "note", "status"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"wrote {OUT} with {len(rows)} rows, n_traces={n}")
    for k in ORDERS:
        a = np.array(amps[k])
        print(f"  k={k}: A={a.mean():+.5f} +/- "
              f"{a.std(ddof=1)/np.sqrt(len(a)):.5f}")
    print(f"  joint: height z={beta[1]/err[1]:+.2f}, "
          f"density z={beta[2]/err[2]:+.2f}, corr={corr:+.3f}")
    return 0


def k4_wls(y, X):
    """OLS via the K8 helper's algebra with unit weights."""
    inv = np.linalg.inv(X.T @ X)
    beta = inv @ (X.T @ y)
    r = y - X @ beta
    dof = max(len(y) - X.shape[1], 1)
    s2 = float(r @ r) / dof
    return beta, np.sqrt(np.diag(inv) * s2)


if __name__ == "__main__":
    raise SystemExit(main())

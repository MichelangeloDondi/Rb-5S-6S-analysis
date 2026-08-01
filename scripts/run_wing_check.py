#!/usr/bin/env python3
"""
M24: the near-core asymmetry is not a collisional wing -- C3f's open item closed.

M23 left one piece of residual structure standing: a small same-side
asymmetry near the line core, present in both sessions, too weakly
power-dependent to be the Stark wedge. The candidate that mattered was a
collisional (quasistatic self-broadening) red satellite, because that would
be new line physics and would connect to the beta_self programme. It makes
one unforgiving prediction: as a pair effect its fractional weight must
scale with density, and the temperature sweep holds a x52 density lever at
fixed 225 mW while the Stark wedge and any instrumental asymmetry stay put.

THE MEASUREMENT. Per (peak, T) condition on the canonical RF-off
temperature sweep, the M23 standoff wing (2 MHz standoff, 6 MHz scale,
fitted on BOTH sides so the side is measured rather than assumed) is added
to the symmetric line model and its fractional amplitude f_w fitted jointly
with the condition's widths, every trace keeping its own free centre. The
same estimator then runs across the 130 C power sweep, where a physical
wing must be a CONSTANT fraction (density fixed) while an SNR artifact
tracks amplitude.

THE RESULT, twice over:

  * Density lever: f_w(red, 130 C) = 0.0002 +/- 0.0009 of peak -- a
    per-mille null exactly where a collisional wing would be 52x enhanced.
    Every 110 C and 130 C condition is consistent with zero on both sides.
    The largest central value in the sweep sits at 70 C (+0.010 +/- 0.008,
    1.3 sigma), the LOWEST-density, lowest-amplitude corner -- the SNR
    direction, and the opposite of collisional.
  * Power lever: at fixed density the fitted wing fraction falls with
    power instead of holding constant, tracking amplitude exactly as
    C3c's shot-noise identification of the residual skew already said.

Both levers contradict a physical wing. The asymmetry M23 flagged is
amplitude-linked statistics, not line physics; nothing about it enters the
Stark budget, and the self-broadening satellite thread is closed on this
archive. (What a real satellite search needs is the fixed-lock session's
SNR at 150-170 C, where the same estimator would see a 0.001-fraction wing
at many sigma.)

Writes results/wing_check.csv. Reads data_raw and the M2 bracket rates.
Runtime ~6 min.
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

from rb5s6s import config as C  # noqa: E402
from rb5s6s.density import number_density_cm3  # noqa: E402
from rb5s6s.ingest import load_manifest, load_trace, trace_path  # noqa: E402
from rb5s6s.linefit import (_shared_profile_grid, adaptive_halfwidth,  # noqa: E402
                            to_frequency, transit_fwhm_at_T)
from rb5s6s.noise import condition_noise_model, sigma_of_v, signal_level  # noqa: E402
from run_beta_self import load_t_rates  # noqa: E402

NU0_MHZ = 2.0             # wing standoff, as in M23
W_WING_MHZ = 6.0          # wing scale, fixed: not identifiable at 70 C SNR
PEAKS = ("4121", "4154", "4192", "4207")


def fit_wing(recs, rate, T_C, side):
    """Joint per-condition fit; side=-1 red wing, +1 blue. Returns
    (f_w, err, chi2_red) with the error sqrt(chi2_red)-inflated."""
    volts = [load_trace(trace_path(r))[1] for r in recs]
    law = condition_noise_model(volts)
    tau = max(law.get("tau_int", 1.0), 1.0)
    tr = []
    for r in recs:
        t, v = load_trace(trace_path(r))
        nu = to_frequency(t, rate)
        lev, base = signal_level(v)
        c0 = float(nu[int(np.argmax(lev))])
        sg = np.maximum(sigma_of_v(np.maximum(lev, 0.0), law), 1e-6) * np.sqrt(tau)
        m = np.abs(nu - c0) <= adaptive_halfwidth(nu, v)
        tr.append((nu[m], v[m], sg[m], c0, float(lev.max()), float(base)))
    transit = transit_fwhm_at_T(T_C, C.TRANSIT_FWHM_PLACEHOLDER_MHZ)
    p0 = np.concatenate([[0.5, 1.0, 0.0],
                         np.concatenate([[t[4], t[3], t[5], 0.0] for t in tr])])
    lo = np.concatenate([[0.0, 0.05, 0.0],
                         np.concatenate([[0.0, t[3] - 10, -np.inf, -np.inf] for t in tr])])
    hi = np.concatenate([[50.0, 50.0, 0.5],
                         np.concatenate([[np.inf, t[3] + 10, np.inf, np.inf] for t in tr])])

    def resid(p):
        gc, sl, fw = p[0], p[1], p[2]
        g, prof = _shared_profile_grid(gc, sl, transit, 0.0, "gaussian",
                                       dnu_floor=2e-2)
        if fw > 0:
            m = (side * g) > NU0_MHZ
            prof = prof.copy()
            prof[m] += fw * prof.max() * np.exp(-(np.abs(g[m]) - NU0_MHZ) / W_WING_MHZ)
        out = []
        for i, (nu, v, sg, *_) in enumerate(tr):
            A, cc, b0, b1 = p[3 + 4 * i: 7 + 4 * i]
            mdl = A * np.interp(nu - cc, g, prof, left=0., right=0.) + b0 + b1 * nu
            out.append((v - mdl) / sg)
        return np.concatenate(out)

    s = least_squares(resid, p0, bounds=(lo, hi), max_nfev=4000,
                      x_scale="jac", ftol=1e-12, xtol=1e-12)
    r = resid(s.x)
    dof = max(len(r) - len(p0), 1)
    chi2_red = float(np.sum(r * r)) / dof  # np.sum, not r@r: Accelerate matmul raises spurious FP warnings on Apple Silicon
    try:
        cov = np.linalg.inv(s.jac.T @ s.jac)
        fe = float(np.sqrt(max(cov[2, 2], 0)) * np.sqrt(max(chi2_red, 1)))
    except np.linalg.LinAlgError:
        fe = float("nan")
    return float(s.x[2]), fe, chi2_red


def wmean(pairs):
    w = np.array([1 / max(e, 1e-4) ** 2 for _, e in pairs])
    return (float(np.sum([v * wi for (v, _), wi in zip(pairs, w)]) / w.sum()),
            float(1 / np.sqrt(w.sum())))


def main() -> int:
    rows = load_manifest()
    _, prates = load_t_rates()
    out_rows = []

    # density lever: t_sweep + the 130 C block, fixed 225 mW
    byT = defaultdict(list)
    for r in rows:
        if r["flag"] != "canonical" or r["rf_on"] == "True":
            continue
        if r["role"] == "t_sweep" or r.get("serves_t130") == "True":
            byT[(r["peak"], int(r["temperature_C"]))].append(r)
    n70 = float(number_density_cm3(np.array([70.0]))[0])
    perT = defaultdict(lambda: {"red": [], "blue": []})
    print("(M24) WING CHECK -- density lever (fixed 225 mW):")
    for (pk, T), recs in sorted(byT.items()):
        rate, _ = prates[pk]
        for lab, side in (("red", -1), ("blue", +1)):
            f, e, c2 = fit_wing(recs, rate, float(T), side)
            perT[T][lab].append((f, e))
            out_rows.append([f"f_wing_{lab}", f"{pk}_T{T}", f"{f:.4f}", f"{e:.4f}",
                             "fraction of peak; standoff wing, per condition"])
        print(f"  {pk} T={T}", flush=True)
    for T in sorted(perT):
        nn = float(number_density_cm3(np.array([float(T)]))[0]) / n70
        for lab in ("red", "blue"):
            m, e = wmean(perT[T][lab])
            out_rows.append([f"f_wing_{lab}_mean", f"T{T}", f"{m:.4f}", f"{e:.4f}",
                             f"weighted over peaks; N/N(70C) = {nn:.1f}"])
            print(f"  T={T} {lab}: {m:+.4f} +/- {e:.4f}  (N/N70 {nn:.0f})")

    # power lever: p_sweep at fixed 130 C
    byP = defaultdict(list)
    for r in rows:
        if r["flag"] == "canonical" and r["role"] == "p_sweep":
            byP[(r["peak"], int(r["power_mW"]))].append(r)
    perP = defaultdict(list)
    print("  power lever (fixed 130 C), red side:")
    for (pk, P), recs in sorted(byP.items()):
        if len(recs) < 3:
            continue
        rate, _ = prates[pk]
        f, e, c2 = fit_wing(recs, rate, 130.0, -1)
        perP[P].append((f, e))
        out_rows.append(["f_wing_red", f"{pk}_P{P}", f"{f:.4f}", f"{e:.4f}",
                         "fraction of peak; power lever, 130 C"])
        print(f"  {pk} P={P}", flush=True)
    for P in sorted(perP):
        m, e = wmean(perP[P])
        out_rows.append(["f_wing_red_mean", f"P{P}", f"{m:.4f}", f"{e:.4f}",
                         "weighted over peaks; a physical wing is a constant "
                         "fraction across this row, an SNR artifact falls"])
        print(f"  P={P}: {m:+.4f} +/- {e:.4f}")

    # the verdict rows the ledger reads
    m130, e130 = wmean(perT[130]["red"])
    out_rows.append(["f_wing_red_130C", "verdict", f"{m130:.4f}", f"{e130:.4f}",
                     "THE closure: per-mille null exactly where a collisional "
                     "satellite would be 52x enhanced; the asymmetry M23 "
                     "flagged is amplitude-linked statistics, not line physics"])
    out_rows.append(["density_lever", "verdict", "52.5", "",
                     "N(130C)/N(70C); the scaling a pair effect cannot dodge"])

    with open(C.RESULTS_DIR / "wing_check.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["quantity", "key", "value", "err", "unit"])
        w.writerows(out_rows)
    print("  Wrote results/wing_check.csv.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

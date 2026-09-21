#!/usr/bin/env python3
"""Ratios and differences of the windowed second cumulant ACROSS the design's
axes, from the canonical traces and the committed fits, with the model's own
prediction at three waists beside each.

WHY THIS EXISTS. At one condition every same-parity ratio of the windowed
cumulants carries the width once: the transit, the laser width and the
Lorentzian floor move the whole even ladder in one direction. What carries new
information is a ratio across a design axis, because the axis is what the
terms differ on. Four such statistics are read here, none of them a fit:

  power ratio      k2(225 mW) / k2(25 mW) at 130 C, per peak and pooled. Every
                   power-independent width cancels (the laser, the Lorentzian
                   floor, the collisions, the transit) and what remains is the
                   P^2 family: the saturation companion and the AC-Stark ramp,
                   both going as w0^-4.
  temperature      k2(T) - k2(70 C) at 225 mW, per peak. The session's laser
  difference       width and the Lorentzian floor cancel. beta Delta N(T) and
                   the transit's sqrt(T) remain.
  window ratio     k2(3.25) / k2(12) per condition, dimensionless. The axis
                   scale and the amplitude cancel. the wing's weight against
                   the core remains, which is the Lorentzian fraction of the
                   line, a kernel-form probe.
  isotope and F    at one condition, k2(85Rb) - k2(87Rb) and, within each
  contrasts        isotope, k2 of the higher F line minus the lower. Every
                   shared term cancels. the isotope contrast reads the
                   transit's mass ratio alone (the lighter 85Rb is faster and
                   wider), the F contrast reads the pumping companion's
                   branching and whatever F-dependent term the model lacks.

THE ESTIMATOR is `rb5s6s.cumulants.windowed_cumulants` at half-widths 3.25, 6
and 12 MHz, self-centred, with a linear baseline through two strips 30 to
40 MHz from the centre on each side so that a pedestal and a tilt are removed
the same way from every trace and from the model. Every windowed statistic is
computed twice, on the estimator's own 4001-point window and on a halved
2001-point window, and a trace whose two readings disagree beyond
`GRID_TOL` (relative) is refused for that window. The cell's bar is the block
scatter over the repeats (the standard deviation over the traces divided by
the root of their number), which is the bar the power ladder's own record
names. the ratios and differences propagate it in quadrature.

THE PREDICTIONS come from `rb5s6s.fullmodel.full_profile` sampled on a grid
like the traces' own (0.0425 MHz steps over 42 MHz each side) and read with
the same estimator, at 42, 64 and 85 um: the transit from the waist and the
temperature (`constants.transit_fwhm_from_w0`, per isotope), the ramp depth
from `lineshape.stark_shift_S0_mhz` at the retro ratio of record, the
two-photon Rabi frequency from `hyperpolarizability.two_photon_rabi_hz`, the
companion with the peak's branching, and the committed gamma_coll and
sigma_laser of `results/linefit_conditions.csv`. Which committed widths, per
statistic, is stated in each row's note: the power ratio holds the per-peak
inverse-variance mean over the five rungs (the committed per-rung widths
already absorb the P^2 terms, so using them would count the companion twice),
the temperature difference and the window ratio take each condition's own,
and the contrasts take the mean over the peaks they compare.

WHAT THE COMMITTED FITS COULD NOT SUPPLY. The per-trace centre: the
committed file carries the shared widths, so the window is seeded on the
committed QC peak position and self-centres from there, which is what the
estimator does by construction. The RF-on sideband rung of the night plan is
not here: it needs the rulers, which are outside this file's population.

FAILURE MODES. A window seeded a line away from the peak converges on the
wrong line: the seed is the trace's own committed peak position, and the
estimator's own convergence flag is honoured, an unconverged window refused.
A strip that falls outside the trace has no baseline: that trace is refused
rather than clamped. A cell with a single trace has no scatter and its bar is
written empty.

POOLING. The per-condition trace work runs under `RB5S6S_WORKERS` workers
(rb5s6s.workers.n_workers), submitted and collected in a fixed order. there
is no random number here, so seeding is moot and the CSV is byte-identical at
every worker count. The predictions run in the parent after the pool. The
CSV is written once, at the end, only after every task returned.

STATUS. Every row is DIAGNOSTIC: the archive's own statistics against the
model at the committed parameters, no term measured.
"""
import csv
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))
from _producer_lock import take_producer_lock                      # noqa: E402
from rb5s6s import windows
from rb5s6s import config as _CFG                                  # noqa: E402
from rb5s6s import constants as K                                  # noqa: E402
# MOMENTS, NOT CUMULANTS (O33). This producer asks only for orders 2 and/or 3, where the two
# bases are the SAME NUMBER (k2 = mu2 and k3 = mu3 identically), so the switch cannot move a
# committed cell -- it removes the retired name, which is the point of doing it everywhere.
from rb5s6s.cumulants import windowed_moments                    # noqa: E402
from rb5s6s.fullmodel import full_profile                          # noqa: E402
from rb5s6s.hyperpolarizability import two_photon_rabi_hz          # noqa: E402
from rb5s6s.ingest import load_manifest, load_trace, trace_path    # noqa: E402
from rb5s6s.linefit import to_frequency                            # noqa: E402
from rb5s6s.lineshape import stark_shift_S0_mhz                    # noqa: E402
from rb5s6s.pmfmt import pm_cells                                  # noqa: E402
from rb5s6s.workers import n_workers                               # noqa: E402

WINDOWS = windows.LEGACY      # the pre-2026-09-19 set, named once (rb5s6s/windows.py); this producer is historical
MAIN_WINDOW = 6.0
STRIP = (30.0, 40.0)          # the baseline strips, MHz from the centre, each side
N_FULL, N_HALF = 4001, 2001
# Measured before it was set (2026-09-14, four conditions, both grids): the
# median disagreement is 3e-6 and the tail reaches 1e-3 on dim 70 C traces at
# the 12 MHz window, where the self-centring contracts slowly and the two
# grids settle a hair apart. A tenth of that tail, 1e-4, is where the grid
# error is still a hundredth of the cell's own block scatter.
GRID_TOL = 1e-4               # relative disagreement between the two grids that refuses a reading
WAISTS_UM = (42.0, 64.0, 85.0)
PEAKS = ("4121", "4154", "4192", "4207")
ISO = {p: K.PEAKS[p]["isotope"] for p in PEAKS}
PAIRS_F = {"87Rb": ("4207", "4121"), "85Rb": ("4192", "4154")}     # higher F minus lower F
P_BLANK_MW = 225.0
GRID_STEP_MHZ = 0.0425
GRID_HALF_MHZ = 42.0
MODEL_NU = np.arange(-round(GRID_HALF_MHZ / GRID_STEP_MHZ), round(GRID_HALF_MHZ / GRID_STEP_MHZ) + 1) * GRID_STEP_MHZ


def _read(name):
    with (_CFG.RESULTS_DIR / name).open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def conditions():
    out = {}
    for r in _read("linefit_conditions.csv"):
        if not r.get("T"):
            continue
        P = float(r["P"]) if r.get("P") else P_BLANK_MW
        out[(r["role"], r["peak"], float(r["T"]), P)] = {
            "rate": float(r["rate_t"]), "gamma_coll": float(r["gamma_coll"]),
            "gamma_coll_err": float(r["gamma_coll_err"]),
            "sigma_laser": float(r["sigma_laser"]), "sigma_laser_err": float(r["sigma_laser_err"])}
    return out


def canonical_traces():
    out = {}
    for r in load_manifest():
        if r["flag"] != "canonical" or r["rf_on"] != "False" or r["role"] not in ("p_sweep", "t_sweep"):
            continue
        P = float(r["power_mW"]) if r["power_mW"] else P_BLANK_MW
        out.setdefault((r["role"], r["peak"], float(r["temperature_C"]), P), []).append(r)
    for v in out.values():
        v.sort(key=lambda r: int(r["repeat_idx"]))
    return out


def qc_peak_positions():
    return {r["file"]: float(r["peak_pos_ms"]) for r in _read("qc_metrics.csv")}


def k2_checked(nu, y, half_width, centre0):
    """k2 on the full and the halved window grid. Returns (k2, relative
    disagreement) or (nan, disagreement) when the two disagree, the window
    did not converge, or a baseline strip is outside the trace."""
    baseline = ("linear", (centre0 - STRIP[1], centre0 - STRIP[0]), (centre0 + STRIP[0], centre0 + STRIP[1]))
    try:
        full, info = windowed_moments(nu, y, half_width, (2,), baseline=baseline, n_points=N_FULL, centre0=centre0)
        half, info_h = windowed_moments(nu, y, half_width, (2,), baseline=baseline, n_points=N_HALF, centre0=centre0)
    except ValueError:
        return float("nan"), float("nan")
    a, b = full[2], half[2]
    if not (np.isfinite(a) and np.isfinite(b)) or info["converged"] < 1 or info_h["converged"] < 1:
        return float("nan"), float("nan")
    dis = abs(a - b) / abs(a) if a != 0 else float("inf")
    if dis > GRID_TOL:
        return float("nan"), dis
    return float(a), dis


def condition_task(key, fit, recs, seeds):
    """Per trace and window: k2 on both grids. Returns per-window arrays."""
    vals = {w: [] for w in WINDOWS}
    dis = {w: [] for w in WINDOWS}
    refused = {w: 0 for w in WINDOWS}
    for r in recs:
        t, v = load_trace(trace_path(r))
        nu = to_frequency(t, fit["rate"])
        c0 = seeds[r["file"]] * fit["rate"]
        for w in WINDOWS:
            k, d = k2_checked(nu, v, w, c0)
            if np.isfinite(k):
                vals[w].append(k)
                dis[w].append(d)
            else:
                refused[w] += 1
    return {"key": key, "vals": vals, "dis": dis, "refused": refused}


def _run_task(args):
    return condition_task(*args)


def cell(values):
    """(mean, block-scatter bar, n) over the repeats. the bar is nan for one trace."""
    x = np.asarray(values, float)
    if x.size == 0:
        return float("nan"), float("nan"), 0
    if x.size == 1:
        # one trace has no scatter and so no bar: the cell is refused rather
        # than written bare
        return float("nan"), float("nan"), 1
    return float(x.mean()), float(x.std(ddof=1) / np.sqrt(x.size)), int(x.size)


def model_k2(w0_um, T_C, P_mW, gamma_coll, sigma_laser, isotope, peak, windows=WINDOWS):
    """The model's k2 per window, on the traces' own grid, read with the same
    estimator on both grids. a disagreement raises rather than publishing."""
    w0 = w0_um * 1e-6
    P_W = P_mW / 1e3
    s0 = float(stark_shift_S0_mhz(P_W, w0, K.RHO_RETRO))
    omega = float(two_photon_rabi_hz(P_W, w0, K.RHO_RETRO)) / 1e6
    y = full_profile(MODEL_NU, gamma_coll=gamma_coll, sigma_laser_fwhm=sigma_laser,
                     transit_fwhm=float(K.transit_fwhm_from_w0(w0, T_C, isotope=isotope)),
                     s0=s0, peak=peak, omega_mhz=omega, T_C=T_C, isotope=isotope)
    out = {}
    for w in windows:
        k, d = k2_checked(MODEL_NU, y, w, 0.0)
        if not np.isfinite(k):
            raise SystemExit(f"run_cross_arm_ratios: the model's k2 at {w} MHz, {w0_um} um, "
                             f"{T_C} C, {P_mW} mW disagrees between the two grids by {d:.2e}. refused")
        out[w] = k
    return out


def ivw(pairs):
    """Inverse-variance mean over (value, err) pairs: (mean, err, chi2, n)."""
    v = np.array([p[0] for p in pairs])
    e = np.array([p[1] for p in pairs])
    m = np.isfinite(v) & np.isfinite(e) & (e > 0)
    v, e = v[m], e[m]
    if v.size == 0:
        return float("nan"), float("nan"), float("nan"), 0
    w = 1.0 / e ** 2
    mean = float(np.sum(w * v) / np.sum(w))
    return mean, float(1.0 / np.sqrt(np.sum(w))), float(np.sum(w * (v - mean) ** 2)), int(v.size)


def pooled_width(fits, keys):
    """Inverse-variance mean of the committed gamma_coll and sigma_laser over keys."""
    gc = ivw([(fits[k]["gamma_coll"], fits[k]["gamma_coll_err"]) for k in keys])[0]
    sl = ivw([(fits[k]["sigma_laser"], fits[k]["sigma_laser_err"]) for k in keys])[0]
    return gc, sl


def label(key):
    role, peak, T, P = key
    return f"{peak}_T{T:g}_P{P:g}"


def pred_cells(preds):
    return ", ".join(f"{w:g} um {v:+.4f}" for w, v in preds.items())


def main() -> int:
    take_producer_lock("cross_arm_ratios")
    fits = conditions()
    traces = canonical_traces()
    seeds = qc_peak_positions()
    keys = sorted(k for k in fits if k in traces)
    tasks = [(k, fits[k], traces[k], {r["file"]: seeds[r["file"]] for r in traces[k]}) for k in keys]
    nw = n_workers()
    if nw > 0:
        with ProcessPoolExecutor(max_workers=nw) as pool:
            futures = [pool.submit(_run_task, t) for t in tasks]
            results = [f.result() for f in futures]
    else:
        results = [_run_task(t) for t in tasks]
    stats = {r["key"]: r for r in results}
    cells = {k: {w: cell(stats[k]["vals"][w]) for w in WINDOWS} for k in keys}
    max_dis = max((d for r in results for w in WINDOWS for d in r["dis"][w] if np.isfinite(d)), default=0.0)
    n_refused = sum(r["refused"][w] for r in results for w in WINDOWS)

    out = [["quantity", "key", "value", "err", "unit", "note", "status"]]
    out.append(["estimator", "definition", f"{MAIN_WINDOW:g}", "", "MHz half-width",
                f"self-centred windowed k2 (rb5s6s.cumulants.windowed_cumulants) at half-widths {', '.join(f'{w:g}' for w in WINDOWS)} MHz, a linear baseline through strips {STRIP[0]:g} to {STRIP[1]:g} MHz from the centre on each side, seeded on the committed QC peak position. every reading computed on {N_FULL} and {N_HALF} window points and refused beyond a relative disagreement of {GRID_TOL:g}: the largest disagreement admitted was {max_dis:.2e} and {n_refused} trace-windows were refused. the bar of a cell is the block scatter over its repeats", "DIAGNOSTIC"])
    for k in keys:
        for w in WINDOWS:
            m, e, n = cells[k][w]
            if n < 2:
                out.append([f"k2_w{w:g}", label(k), "", "", "MHz^2",
                            f"fewer than two traces admitted ({n}), so no scatter and no cell. {stats[k]['refused'][w]} refused", "DIAGNOSTIC"])
                continue
            v, es = pm_cells(m, e)
            out.append([f"k2_w{w:g}", label(k), v, es, "MHz^2",
                        f"mean over {n} traces, the bar the block scatter. {stats[k]['refused'][w]} refused", "DIAGNOSTIC"])

    # ---- the power ratio at 130 C ---------------------------------------
    pooled_ratio, pooled_pred = [], {w0: [] for w0 in WAISTS_UM}
    for peak in PEAKS:
        hi, lo = ("p_sweep", peak, 130.0, 225.0), ("p_sweep", peak, 130.0, 25.0)
        if hi not in cells or lo not in cells:
            continue
        (mh, eh, nh), (ml, el, nl) = cells[hi][MAIN_WINDOW], cells[lo][MAIN_WINDOW]
        ratio = mh / ml
        err = ratio * np.hypot(eh / mh, el / ml)
        rungs = [kk for kk in keys if kk[0] == "p_sweep" and kk[1] == peak]
        gc, sl = pooled_width(fits, rungs)
        preds = {}
        for w0 in WAISTS_UM:
            a = model_k2(w0, 130.0, 225.0, gc, sl, ISO[peak], peak, (MAIN_WINDOW,))[MAIN_WINDOW]
            b = model_k2(w0, 130.0, 25.0, gc, sl, ISO[peak], peak, (MAIN_WINDOW,))[MAIN_WINDOW]
            preds[w0] = a / b
            pooled_pred[w0].append(a / b)
        pooled_ratio.append((ratio, err))
        v, es = pm_cells(ratio, err)
        out.append(["power_ratio_k2", peak, v, es, "",
                    f"k2({MAIN_WINDOW:g} MHz) at 225 mW over 25 mW, 130 C, {nh} and {nl} traces. the P^2 terms alone move it. model at the per-peak pooled committed widths (gamma_coll {gc:.4f}, sigma_laser {sl:.4f} MHz), the ramp and the companion at the record's retro ratio: {pred_cells(preds)}. pulls " + ", ".join(f"{w0:g} um {(ratio - p) / err:+.1f}" for w0, p in preds.items()), "DIAGNOSTIC"])
    m, e, chi2, n = ivw(pooled_ratio)
    v, es = pm_cells(m, e)
    pp = {w0: float(np.mean(pooled_pred[w0])) for w0 in WAISTS_UM}
    out.append(["power_ratio_k2", "pooled", v, es, "",
                f"inverse-variance pool over {n} peaks, chi2 {chi2:.1f} for {n - 1} dof. model, the mean over the peaks: {pred_cells(pp)}. pulls " + ", ".join(f"{w0:g} um {(m - p) / e:+.1f}" for w0, p in pp.items()), "DIAGNOSTIC"])
    for w0 in WAISTS_UM:
        out.append(["power_ratio_k2_model", f"w{w0:g}", f"{pp[w0]:.5f}", "", "",
                    f"the model's pooled ratio at {w0:g} um: the companion (Omega^2, w0^-4) and the ramp (S0^2, w0^-4) at 225 against 25 mW", "DIAGNOSTIC"])

    # ---- the temperature difference at 225 mW ----------------------------
    pooled_td = {90.0: [], 110.0: [], 130.0: []}
    pooled_td_pred = {T: {w0: [] for w0 in WAISTS_UM} for T in pooled_td}
    for peak in PEAKS:
        base = ("t_sweep", peak, 70.0, P_BLANK_MW)
        if base not in cells:
            continue
        mb, eb, nb = cells[base][MAIN_WINDOW]
        for key in (("t_sweep", peak, 90.0, P_BLANK_MW), ("t_sweep", peak, 110.0, P_BLANK_MW),
                    ("p_sweep", peak, 130.0, 225.0)):
            if key not in cells:
                continue
            mt, et, nt = cells[key][MAIN_WINDOW]
            diff, err = mt - mb, float(np.hypot(et, eb))
            preds = {}
            for w0 in WAISTS_UM:
                a = model_k2(w0, key[2], 225.0, fits[key]["gamma_coll"], fits[key]["sigma_laser"], ISO[peak], peak, (MAIN_WINDOW,))[MAIN_WINDOW]
                b = model_k2(w0, 70.0, 225.0, fits[base]["gamma_coll"], fits[base]["sigma_laser"], ISO[peak], peak, (MAIN_WINDOW,))[MAIN_WINDOW]
                preds[w0] = a - b
            pooled_td[key[2]].append((diff, err))
            for w0 in WAISTS_UM:
                pooled_td_pred[key[2]][w0].append(preds[w0])
            v, es = pm_cells(diff, err)
            out.append(["temperature_difference_k2", f"{peak}_T{key[2]:g}_minus_T70", v, es, "MHz^2",
                        f"k2({MAIN_WINDOW:g} MHz) at 225 mW, {key[2]:g} C minus 70 C, {nt} and {nb} traces. the session's laser width and the floor cancel, beta Delta N and the transit's sqrt(T) remain. model at each condition's own committed widths, the transit from the waist and the temperature: {pred_cells(preds)}. pulls " + ", ".join(f"{w0:g} um {(diff - p) / err:+.1f}" for w0, p in preds.items()), "DIAGNOSTIC"])

    for T, pairs in pooled_td.items():
        m, e, chi2, n = ivw(pairs)
        pp = {w0: float(np.mean(pooled_td_pred[T][w0])) for w0 in WAISTS_UM}
        v, es = pm_cells(m, e)
        out.append(["temperature_difference_k2", f"pooled_T{T:g}_minus_T70", v, es, "MHz^2",
                    f"inverse-variance pool over {n} peaks at {T:g} C minus 70 C, chi2 {chi2:.1f} for {n - 1} dof. model, the mean over the peaks: {pred_cells(pp)}. pulls " + ", ".join(f"{w0:g} um {(m - p) / e:+.1f}" for w0, p in pp.items()), "DIAGNOSTIC"])

    # ---- the window ratio per condition ----------------------------------
    pooled_wr = {"power_arm": [], "temperature_arm": []}
    for k in keys:
        role, peak, T, P = k
        a = stats[k]["vals"][3.25]
        b = stats[k]["vals"][12.0]
        n = min(len(a), len(b))
        if n == 0:
            continue
        r = np.array(a[:n]) / np.array(b[:n])
        m, e, n = cell(r)
        if n < 2:
            out.append(["window_ratio_k2", label(k), "", "", "",
                        f"fewer than two traces admitted at both windows ({n}), so no scatter and no cell", "DIAGNOSTIC"])
            continue
        preds = {w0: (lambda mk: mk[3.25] / mk[12.0])(model_k2(w0, T, P, fits[k]["gamma_coll"], fits[k]["sigma_laser"], ISO[peak], peak)) for w0 in WAISTS_UM}
        v, es = pm_cells(m, e)
        out.append(["window_ratio_k2", label(k), v, es, "",
                    f"k2(3.25) over k2(12) per trace, the mean over {n} traces with the block scatter. the wing's weight against the core, a kernel-form probe. model at this condition's committed widths: {pred_cells(preds)}. pulls " + ", ".join(f"{w0:g} um {(m - p) / e:+.1f}" if np.isfinite(e) and e > 0 else f"{w0:g} um n/a" for w0, p in preds.items()), "DIAGNOSTIC"])
        arm = "power_arm" if role == "p_sweep" else "temperature_arm"
        pooled_wr[arm].append((m, e))
        if role == "p_sweep" and P == 225.0:
            pooled_wr["temperature_arm"].append((m, e))
    for arm, pairs in pooled_wr.items():
        m, e, chi2, n = ivw(pairs)
        v, es = pm_cells(m, e)
        out.append(["window_ratio_k2", f"pooled_{arm}", v, es, "",
                    f"inverse-variance pool over the {arm.replace('_', ' ')} ({n} conditions, the 130 C corner at 225 mW in both arms), chi2 {chi2:.1f} for {n - 1} dof", "DIAGNOSTIC"])

    # ---- the isotope and F contrasts per (T, P) --------------------------
    groups = {}
    for k in keys:
        groups.setdefault((k[0], k[2], k[3]), {})[k[1]] = k
    pooled_iso = {"power_arm": [], "temperature_arm": []}
    pooled_f = {iso: [] for iso in PAIRS_F}
    for (role, T, P), peaks in sorted(groups.items()):
        if set(peaks) != set(PEAKS):
            continue
        c = {p: cells[peaks[p]][MAIN_WINDOW] for p in PEAKS}
        if any(not np.isfinite(c[p][1]) for p in PEAKS):
            continue
        contrast = (c["4154"][0] + c["4192"][0]) / 2 - (c["4121"][0] + c["4207"][0]) / 2
        err = 0.5 * float(np.sqrt(sum(c[p][1] ** 2 for p in PEAKS)))
        gc, sl = pooled_width(fits, [peaks[p] for p in PEAKS])
        preds = {}
        for w0 in WAISTS_UM:
            a = model_k2(w0, T, P, gc, sl, 85, None, (MAIN_WINDOW,))[MAIN_WINDOW]
            b = model_k2(w0, T, P, gc, sl, 87, None, (MAIN_WINDOW,))[MAIN_WINDOW]
            preds[w0] = a - b
        lab = f"T{T:g}_P{P:g}"
        v, es = pm_cells(contrast, err)
        out.append(["isotope_contrast_k2", lab, v, es, "MHz^2",
                    f"mean k2({MAIN_WINDOW:g} MHz) of 85Rb (4154, 4192) minus 87Rb (4121, 4207) at {T:g} C, {P:g} mW. every shared term cancels and the transit's mass ratio remains: the lighter 85Rb is faster, so a transit predicts a POSITIVE contrast. model at the four-peak pooled committed widths (gamma_coll {gc:.4f}, sigma_laser {sl:.4f} MHz) with only the transit's isotope changed: {pred_cells(preds)}. pulls " + ", ".join(f"{w0:g} um {(contrast - p) / err:+.1f}" for w0, p in preds.items()), "DIAGNOSTIC"])
        arm = "power_arm" if role == "p_sweep" else "temperature_arm"
        pooled_iso[arm].append((contrast, err))
        if role == "p_sweep" and P == 225.0:
            pooled_iso["temperature_arm"].append((contrast, err))
        for iso, (hi, lo) in PAIRS_F.items():
            fc = c[hi][0] - c[lo][0]
            fe = float(np.hypot(c[hi][1], c[lo][1]))
            gc2, sl2 = pooled_width(fits, [peaks[hi], peaks[lo]])
            fp = {}
            for w0 in WAISTS_UM:
                a = model_k2(w0, T, P, gc2, sl2, ISO[hi], hi, (MAIN_WINDOW,))[MAIN_WINDOW]
                b = model_k2(w0, T, P, gc2, sl2, ISO[lo], lo, (MAIN_WINDOW,))[MAIN_WINDOW]
                fp[w0] = a - b
            v, es = pm_cells(fc, fe)
            out.append([f"F_contrast_k2_{iso}", lab, v, es, "MHz^2",
                        f"k2({MAIN_WINDOW:g} MHz) of {hi} minus {lo} at {T:g} C, {P:g} mW: the higher F minus the lower within {iso}. the pumping companion differs by the branching, the higher-branching lower-F line the wider, so the model's contrast is negative and grows as P^2. model at the pair's pooled committed widths: {pred_cells(fp)}. pulls " + ", ".join(f"{w0:g} um {(fc - p) / fe:+.1f}" for w0, p in fp.items()), "DIAGNOSTIC"])
            pooled_f[iso].append((fc, fe))
    for arm, pairs in pooled_iso.items():
        m, e, chi2, n = ivw(pairs)
        v, es = pm_cells(m, e)
        out.append(["isotope_contrast_k2", f"pooled_{arm}", v, es, "MHz^2",
                    f"inverse-variance pool over the {arm.replace('_', ' ')} ({n} conditions), chi2 {chi2:.1f} for {n - 1} dof. a transit predicts a positive value", "DIAGNOSTIC"])
    for iso, pairs in pooled_f.items():
        m, e, chi2, n = ivw(pairs)
        v, es = pm_cells(m, e)
        out.append([f"F_contrast_k2_{iso}", "pooled", v, es, "MHz^2",
                    f"inverse-variance pool over {n} conditions, chi2 {chi2:.1f} for {n - 1} dof. the model's pumping contrast is negative", "DIAGNOSTIC"])
    out.append(["isotope_law", "transit", f"{np.sqrt(K.M_RB87_KG / K.M_RB85_KG) - 1:.5f}", "", "",
                "the 85Rb transit over the 87Rb transit minus one, the root of the mass ratio", "DIAGNOSTIC"])

    out_path = _CFG.RESULTS_DIR / "cross_arm_ratios.csv"
    tmp = out_path.with_name(out_path.name + ".writing")
    with tmp.open("w", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerows(out)
    tmp.replace(out_path)
    print(f"wrote {out_path} ({len(out) - 1} rows, largest grid disagreement {max_dis:.2e}, "
          f"{n_refused} trace-windows refused, workers {nw})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
M3 real-data shakedown: joint lineshape fit of every canonical RF-off
condition, end-to-end through M0->M1->M2->M3.

PRELIMINARY by construction — read before using any number:
  * the transit width rides on w0 (OPEN until the knife-edge measurement); it is
    FIXED here at a placeholder (config.TRANSIT_FWHM_PLACEHOLDER_MHZ at 110 C
    with sqrt(T) scaling). Absolute sigma_laser and gamma_coll inherit that
    assumption AND the -0.9 laser<->coll degeneracy (see linefit.py).
  * The DEGENERACY-ROBUST observable is the TOTAL Voigt FWHM per condition
    and its temperature trend — reported first. gamma_coll(T) is shown but
    is preliminary; beta_self proper (with the confound program, N(T), and
    the measured w0) is module M4.

Rate assignment (per condition -> its M2 block rate, transition axis):
  * T-sweep line (peak, T)  -> ruler_t block (peak, T)
  * P-sweep line (peak,130) -> mean of that peak's before/after brackets
Missing a rate -> the condition is skipped with a printed note (never a
silent fallback).

Outputs: results/linefit_conditions.csv + stdout trend tables.
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _producer_lock import take_producer_lock     # noqa: E402
from rb5s6s import config as C  # noqa: E402
from rb5s6s.constants import GAMMA_NAT_HZ, TOOTH_SPACING_LASER_HZ  # noqa: E402
from rb5s6s.ingest import load_manifest, load_trace, trace_path  # noqa: E402
from rb5s6s.noise import condition_noise_model, condition_key as noise_key  # noqa: E402
from rb5s6s.qc import (trace_metrics, hard_flags, ingest_flags,  # noqa: E402
                       outlier_files)
from rb5s6s.ruler import campaign_rate_relsyst  # noqa: E402
from rb5s6s.linefit import fit_condition, to_frequency, transit_fwhm_at_T  # noqa: E402

GNAT = GAMMA_NAT_HZ / 1e6
MHZ_TOOTH = TOOTH_SPACING_LASER_HZ / 1e6


def load_block_rates():
    """Read M2 results/ruler_blocks.csv -> transition-axis rate per block,
    WITH each block's relative rate error (2026-07-16 -- finding: the
    ruler calibration error was folded in run_beta_self/run_power_sweep but
    dropped here, where the per-condition widths are made). A rate error
    scales the whole frequency axis of its block, so every width-type
    quantity from that block (gamma_coll, sigma_laser, total FWHM) carries a
    block-coherent fractional error equal to it; it is folded into the
    written errors below. P-sweep brackets: rate = mean(before, after), the
    half-difference added in quadrature (matching run_beta_self).

    Since 2026-08-04 the campaign-level FRACTIONAL systematics of
    results/ruler_campaign.csv are folded on top (ruler.campaign_rate_relsyst:
    how much of the rate is a choice among eight legitimate estimators of the
    same blocks, and the rulers and the lines sitting at different places in
    the acquisition window). Both are block-coherent in exactly the sense the
    per-block error already carried here is, and neither was in any width's
    budget before. The campaign STATISTICAL error is not folded, because the
    per-block statistical error below already is it.

    Returns dicts of (rate, relerr) keyed for T-sweep and P-sweep lookups."""
    path = C.RESULTS_DIR / "ruler_blocks.csv"
    if not path.exists():
        raise SystemExit("run scripts/run_ruler.py first (need results/ruler_blocks.csv)")
    trate, pbrackets = {}, defaultdict(dict)
    for r in csv.DictReader(open(path)):
        rr = 2.0 * float(r["rate"])   # laser -> transition axis
        ee = 2.0 * float(r["rate_err"])
        if r["session"] == "T":
            trate[(r["peak"], r["T"])] = (rr, ee / rr)
        else:
            pbrackets[r["peak"]][r["bracket"]] = (rr, ee)
    prate = {}
    for peak, br in pbrackets.items():
        if "before" in br and "after" in br:
            (rb, eb), (ra, ea) = br["before"], br["after"]
            mean = 0.5 * (rb + ra)
            err = np.sqrt(0.5 * (eb ** 2 + ea ** 2) + (0.5 * (rb - ra)) ** 2)
            prate[peak] = (mean, err / mean)
        elif br:
            (rr, ee) = next(iter(br.values()))
            prate[peak] = (rr, ee / rr)
    syst = campaign_rate_relsyst()
    if syst > 0:
        for d in (trate, prate):
            for k, (rr, rel) in list(d.items()):
                d[k] = (rr, float(np.hypot(rel, syst)))
    return trate, prate


def condition_rate(role, peak, T, trate, prate):
    if role == "t_sweep":
        return trate.get((peak, T))
    return prate.get(peak)  # p_sweep all at 130 C, bracketed


def _tau_of(fit, core) -> float:
    from rb5s6s.noise import integrated_time_sokal
    rs, ms = fit.get("whitened_residuals"), fit.get("core_masks")
    if not rs:
        return float("nan")
    parts = [np.asarray(r) if core is None else np.asarray(r)[np.asarray(m)] for r, m in zip(rs, ms)]
    taus = [integrated_time_sokal(p, kmax=min(200, max(10, p.size // 4)))["tau"] for p in parts if p.size >= 40]
    return float(np.median(taus)) if taus else float("nan")


def _common_fraction(fit, core: bool) -> float:
    rs, ms = fit.get("whitened_residuals"), fit.get("core_masks")
    if not rs or not ms or len(rs) < 3:
        return float("nan")
    n_min = min(len(r) for r in rs)
    R = np.array([np.asarray(r)[:n_min] for r in rs]); M = np.array([np.asarray(m)[:n_min] for m in ms])
    sel = M.all(axis=0) if core else (~M).all(axis=0)
    if sel.sum() < 20:
        return float("nan")
    X = R[:, sel]; n = X.shape[0]
    V = float(np.mean(np.var(X, axis=1, ddof=1)))
    var_mean = float(np.var(X.mean(axis=0), ddof=1))
    C = (n * var_mean - V) / (n - 1)
    return float(C / V) if V > 0 else float("nan")


def _core_var(fit) -> float:
    rs, ms = fit.get("whitened_residuals"), fit.get("core_masks")
    if not rs or not ms:
        return float("nan")
    x = np.concatenate([np.asarray(r)[np.asarray(m)] for r, m in zip(rs, ms)])
    return float(np.var(x)) if x.size > 10 else float("nan")


def _wing_var(fit) -> float:
    rs, ms = fit.get("whitened_residuals"), fit.get("core_masks")
    if not rs or not ms:
        return float("nan")
    x = np.concatenate([np.asarray(r)[~np.asarray(m)] for r, m in zip(rs, ms)])
    return float(np.var(x)) if x.size > 10 else float("nan")


def main() -> int:
    take_producer_lock("run_linefit")
    rows = load_manifest()
    trate, prate = load_block_rates()
    # Sibling outliers are removed from the condition fits: a trace whose own
    # siblings do not share its height or width is not a repeat of the same
    # measurement, and averaging it into one is what the pre-registered rule
    # exists to stop. It keeps its row in results/qc_metrics.csv, marked.
    dropped = outlier_files()

    conds = defaultdict(list)
    for r in rows:
        if r["flag"] == "canonical" and r["rf_on"] == "False":
            conds[(r["role"], r["peak"], r["temperature_C"], r["power_mW"])].append(r)

    print(f"M3 shakedown: {len(conds)} canonical RF-off conditions "
          f"(transit FIXED at placeholder {C.TRANSIT_FWHM_PLACEHOLDER_MHZ} MHz@110C, w0 OPEN)")
    if dropped:
        print(f"  excluding {len(dropped)} sibling outlier(s): "
              + ", ".join(sorted(dropped)))
    out, n_trimmed = [], 0
    _kept, _pooled_sigma, _pooled_gamma = {}, {}, {}                     # per condition: the kept (nu, v) pairs and the pooled laser width, for the per-trace pass
    for key in sorted(conds):
        role, peak, T, P = key
        entry = condition_rate(role, peak, T, trate, prate)
        if entry is None:
            print(f"  [skip] {key}: no M2 rate"); continue
        rate, rate_relerr = entry
        freqs, volts = [], []
        for r in conds[key]:
            if r["file"] in dropped:
                continue
            t, v, info = load_trace(trace_path(r), with_info=True)
            m = trace_metrics(t, v)
            if any("truncated" in f or "dropout" in f for f in
                   hard_flags(m, rf_on=False) + ingest_flags(info)):
                continue
            freqs.append(to_frequency(t, rate)); volts.append(v)
            _kept.setdefault(key, []).append((freqs[-1], v))
        if len(volts) < 3:
            print(f"  [skip] {key}: {len(volts)} usable traces"); continue
        law = condition_noise_model(volts, key=noise_key(key[1], key[2], key[3] or 225.0))   # F36; the temperature arm's rows carry no power in the manifest and sit at 225 mW
        transit = transit_fwhm_at_T(float(T), C.TRANSIT_FWHM_PLACEHOLDER_MHZ)
        try:
            fit = fit_condition(freqs, volts, T_C=float(T), law=law, transit_fwhm=transit,
                                trim_tails=True)
        except RuntimeError as e:
            print(f"  [warn] fit failed {key}: {e}"); continue
        for tr in fit["trim_records"]:
            if tr["trimmed"]:
                n_trimmed += 1
                print(f"  [trim] {key}: a trace keeps {tr['trim_start_ms']:.1f} to "
                      f"{tr['trim_end_ms']:.1f} MHz ({tr['trim_reason']})")
        # total width = numerical FWHM of the full composite model at the
        # fitted params (the degeneracy-robust observable: insensitive to how
        # the width splits between laser and collisional cores)
        from rb5s6s.lineshape import model_profile
        nu = np.arange(-60, 60, 0.005)

        def _total_fwhm(gc, sl):
            prof = model_profile(nu, gamma_coll=max(gc, 0.0),
                                 sigma_laser_fwhm=max(sl, 1e-6), transit_fwhm=transit)
            # sub-grid FWHM by linear interpolation of the two half-max crossings
            # (reading nu[prof>=half] quantizes FWHM to the grid step)
            h = 0.5 * prof.max()
            above = np.where(prof >= h)[0]
            lo, hi = above[0], above[-1]
            left = nu[lo] - (prof[lo] - h) / (prof[lo] - prof[lo - 1]) * (nu[lo] - nu[lo - 1]) \
                if lo > 0 else nu[lo]
            right = nu[hi] + (prof[hi] - h) / (prof[hi] - prof[hi + 1]) * (nu[hi + 1] - nu[hi]) \
                if hi < len(nu) - 1 else nu[hi]
            return float(right - left)

        gc, sl = fit["gamma_coll"], fit["sigma_laser"]
        s_gc, s_sl = fit["gamma_coll_err"], fit["sigma_laser_err"]
        total_fwhm = _total_fwhm(gc, sl)
        _pooled_sigma[key] = float(sl); _pooled_gamma[key] = float(gc)
        # Error on the TOTAL width: propagate the fit covariance through the
        # (numerical) total-FWHM map via a central-difference Jacobian. The
        # strong sigma_laser<->gamma_coll anticorrelation (corr ~ -0.85) makes
        # this MUCH smaller than the naive quadrature sum -- which is exactly
        # why the total width is the trustworthy, degeneracy-robust observable
        # (README 2.4) while the split is not. Transit is FIXED (w0 prior, an
        # OPEN systematic handled separately), so it adds no statistical term.
        h_gc = max(0.25 * s_gc, 0.01)
        h_sl = max(0.25 * s_sl, 0.01)
        d_gc = (_total_fwhm(gc + h_gc, sl) - _total_fwhm(gc - h_gc, sl)) / (2 * h_gc)
        d_sl = (_total_fwhm(gc, sl + h_sl) - _total_fwhm(gc, sl - h_sl)) / (2 * h_sl)
        rho = fit["corr_laser_coll"]
        rho = rho if np.isfinite(rho) else 0.0
        var = (d_gc * s_gc) ** 2 + (d_sl * s_sl) ** 2 + 2 * d_gc * d_sl * rho * s_gc * s_sl
        total_fwhm_err = float(np.sqrt(max(var, 0.0)))
        out.append({
            "role": role, "peak": peak, "T": T, "P": P, "rate_t": rate,
            "rate_relerr": rate_relerr,
            # the block-coherent ruler-rate error scales every width in the
            # block together; folded here so no consumer of this CSV can drop
            # it (finding 4, 2026-07-16)
            "n": len(volts), "gamma_coll": fit["gamma_coll"],
            "gamma_coll_err": float(np.hypot(fit["gamma_coll_err"],
                                             fit["gamma_coll"] * rate_relerr)),
            "sigma_laser": fit["sigma_laser"],
            "sigma_laser_err": float(np.hypot(fit["sigma_laser_err"],
                                              fit["sigma_laser"] * rate_relerr)),
            "total_fwhm": total_fwhm,
            "total_fwhm_err": float(np.hypot(total_fwhm_err,
                                             total_fwhm * rate_relerr)),
            "corr": fit["corr_laser_coll"], "chi2_red": fit["chi2_red"],
            # THE CORE CHECK (F42): the whitened residual variance inside one full width of each
            # trace's centre against the wings', both against one; a law fitted on the wings and
            # extrapolated to the core through bV + cV^2 that over-predicts the core reads under one
            "core_whitened_variance": _core_var(fit), "wing_whitened_variance": _wing_var(fit),
            # THE COMMON COMPONENT OF A CONDITION'S REPEATS (F44): a residual shared by
            # the five traces (fixed-pattern baseline, sweep-locked pickup, misfit) enters the law and
            # the bar as noise but does not scatter between repeats; C = (n Var(mean) - V)/(n - 1)
            # sample by sample, as a fraction of the per-trace variance V, core and wings apart
            "common_fraction_core": _common_fraction(fit, core=True), "common_fraction_wing": _common_fraction(fit, core=False),
            # THE FULL FIT'S OWN CORRELATION TIME (F44): Sokal's time on the joint fit's
            # whitened residual, core and wings together and the core alone, against the wing-pool time
            # the seam carried; the core's time is the one a width's bar needs
            "tau_fullfit": _tau_of(fit, core=None), "tau_fullfit_core": _tau_of(fit, core=True), "tau_carried": float(law.get("tau_eff", law.get("tau_int", float("nan")))),
            "noise_floor_limited": fit["noise_floor_limited"],
            "gamma_coll_at_bound": fit["gamma_coll_at_bound"],
            "sigma_laser_at_bound": fit["sigma_laser_at_bound"],
        })

    with open(C.RESULTS_DIR / "linefit_conditions.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

    # ---- THE PER-TRACE PASS AND THE PER-PARAMETER PULLS (F36, 2026-09-17) ----
    # Each trace fitted alone with the condition's pooled laser width pinned; the scatter of each
    # fitted parameter over the condition's repeats against the fit's own bar, as a Student-t pull
    # on (n - 1) degrees of freedom, pooled over the conditions, is the effective correlation time
    # that parameter's bar needs, with no lag window: read beside tau_resid, never assumed.
    traces_out, pulls = [], {"gamma_coll": [], "amplitude": [], "centre": [], "sigma_laser": []}
    _sl_rows = {}
    _corr_rows = []
    for key in sorted(conds):
        role, peak, T, P = key
        if key not in _pooled_sigma or not _kept.get(key):
            continue
        law = condition_noise_model([v for _, v in _kept[key]], key=noise_key(peak, T, P or 225.0))
        transit = transit_fwhm_at_T(float(T), C.TRANSIT_FWHM_PLACEHOLDER_MHZ)
        vals = {"gamma_coll": [], "amplitude": [], "centre": []}; errs = {"gamma_coll": [], "amplitude": [], "centre": []}
        for nu, v in _kept[key]:
            try:
                f1 = fit_condition([nu], [v], T_C=float(T), law=law, transit_fwhm=transit, fix_sigma_laser=float(_pooled_sigma[key]))
            except Exception as e:                                           # a single trace that will not fit is a row, not a crash
                traces_out.append({"role": role, "peak": peak, "temperature_C": T, "power_mW": P, "gamma_coll": float("nan"), "gamma_coll_err": float("nan"), "chi2_red": float("nan"), "note": f"fit failed: {type(e).__name__}"}); continue
            pt = {"A": (f1.get("amps") or [float("nan")])[0], "c": (f1.get("centers") or [float("nan")])[0],
                  "A_err": (f1.get("amps_err") or [float("nan")])[0], "c_err": (f1.get("centers_err") or [float("nan")])[0]}
            traces_out.append({"role": role, "peak": peak, "temperature_C": T, "power_mW": P,
                               "gamma_coll": f1["gamma_coll"], "gamma_coll_err": f1["gamma_coll_err"], "chi2_red": f1["chi2_red"],
                               "gamma_coll_err_marginal": f1.get("gamma_coll_err_marginal", float("nan")), "corr_marginal": f1.get("corr_marginal", float("nan")),
                               "amplitude": pt.get("A", float("nan")), "amplitude_err": pt.get("A_err", float("nan")),
                               "centre_mhz": pt.get("c", float("nan")), "centre_err": pt.get("c_err", float("nan")),
                               "note": "one trace alone, the condition's pooled laser width pinned for the F36 per-parameter calibration"})
            vals["gamma_coll"].append(f1["gamma_coll"]); errs["gamma_coll"].append(f1["gamma_coll_err"])
            for nm, kv, ke in (("amplitude", "A", "A_err"), ("centre", "c", "c_err")):
                if kv in pt and ke in pt:
                    vals[nm].append(pt[kv]); errs[nm].append(pt[ke])
        # the complementary pass: gamma_coll pinned at the pooled value, the laser width read per trace
        vals["sigma_laser"], errs["sigma_laser"] = [], []
        for nu, v in _kept[key]:
            try:
                f2 = fit_condition([nu], [v], T_C=float(T), law=law, transit_fwhm=transit, fix_gamma_coll=float(_pooled_gamma[key]))
                vals["sigma_laser"].append(f2["sigma_laser"]); errs["sigma_laser"].append(f2["sigma_laser_err"])
                _sl_rows.setdefault(key, []).append((f2["sigma_laser"], f2["sigma_laser_err"], f2.get("sigma_laser_err_marginal", float("nan"))))
            except Exception:
                pass
        # the third pass: both widths free per trace, their correlation across the condition's repeats
        # against the within-trace noise correlation (F44's discriminant): noise alone reads the
        # fit's own -0.9, a laser-linewidth jitter pulls it toward zero, an axis-scale jitter toward
        # positive, because a scale moves every width together
        _both = []
        for nu, v in _kept[key]:
            try:
                f3 = fit_condition([nu], [v], T_C=float(T), law=law, transit_fwhm=transit)
                _both.append((f3["gamma_coll"], f3["sigma_laser"], f3.get("corr_laser_coll", float("nan"))))
            except Exception:
                pass
        if len(_both) >= 4:
            _gc = np.array([b[0] for b in _both]); _sl = np.array([b[1] for b in _both]); _rho_fit = float(np.nanmedian([b[2] for b in _both]))
            if np.std(_gc) > 0 and np.std(_sl) > 0:
                _corr_rows.append((key, float(np.corrcoef(_gc, _sl)[0, 1]), _rho_fit, len(_both)))
        for nm in vals:
            v_ = np.array(vals[nm], float); e_ = np.array(errs[nm], float)
            ok = np.isfinite(v_) & np.isfinite(e_) & (e_ > 0)
            if ok.sum() >= 3:
                # the pull of the repeats' scatter against the bar: var over mean bar^2, n - 1 dof
                pulls[nm].append((float(np.var(v_[ok], ddof=1) / np.mean(e_[ok] ** 2)), int(ok.sum()) - 1))
    for key, lst in _sl_rows.items():
        role, peak, T, P = key
        for sl_, e_, em_ in lst:
            traces_out.append({"role": role, "peak": peak, "temperature_C": T, "power_mW": P, "sigma_laser": sl_, "sigma_laser_err": e_, "sigma_laser_err_marginal": em_,
                               "note": "the complementary pass, the collisional width pinned at the pooled value and the laser width read per trace"})
    with open(C.RESULTS_DIR / "linefit_traces.csv", "w", newline="") as f:
        if traces_out:
            fields = sorted({k for row in traces_out for k in row}, key=lambda k: (k != "role", k != "peak", k))
            w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(traces_out)
    pull_rows = []
    if _corr_rows:
        _z = np.array([np.arctanh(np.clip(c, -0.999, 0.999)) for _, c, _, _ in _corr_rows]); _w = np.array([n - 3 for _, _, _, n in _corr_rows], float)
        _zbar = float(np.sum(_w * _z) / np.sum(_w)); _se = float(1.0 / np.sqrt(np.sum(_w)))
        _rfit = float(np.nanmedian([rf for _, _, rf, _ in _corr_rows]))
        pull_rows.append({"parameter": "widths_correlation_across_repeats", "pooled_mean_square_pull": float(np.tanh(_zbar)), "n_conditions": len(_corr_rows), "dof": int(np.sum(_w)),
                          "note": f"the correlation of gamma_coll and sigma_laser, both free per trace, across each condition's repeats, pooled by Fisher z (one-sigma {np.tanh(_zbar - _se):+.3f} to {np.tanh(_zbar + _se):+.3f}). The within-trace noise correlation the fit reports is {_rfit:+.3f}. Noise alone reproduces that number, a laser-linewidth jitter pulls the across-repeat value toward zero, an axis-scale jitter toward positive (F44's discriminant)"})
    for nm, pl in pulls.items():
        if pl:
            msp = float(np.average([q for q, _ in pl], weights=[d for _, d in pl]))
            pull_rows.append({"parameter": nm, "pooled_mean_square_pull": msp, "n_conditions": len(pl),
                              "dof": int(sum(d for _, d in pl)),
                              "note": "the repeats' scatter over the fit's own bar, pooled over the conditions with their degrees of freedom. It is the effective correlation time this parameter's bar needs (F36), read beside tau_resid. The width is fitted with the laser width pinned per condition"})
    # THE (k, J) FIT (F44, 2026-09-17): the repeats' variance as a calibration factor on
    # the bar against an added width variation, sd^2 = k^2 bar^2 + J^2 over the conditions, each
    # weighted by its degrees of freedom on a sample variance; the form the width bars carry
    _S2, _B2, _D = [], [], []
    for key in sorted(conds):
        if key not in _pooled_sigma or not _kept.get(key):
            continue
        _v = np.array([float(row["gamma_coll"]) for row in traces_out if row.get("role") == key[0] and row.get("peak") == key[1] and row.get("temperature_C") == key[2] and row.get("power_mW") == key[3] and "gamma_coll" in row and np.isfinite(float(row.get("gamma_coll", "nan")))])
        _e = np.array([float(row["gamma_coll_err"]) for row in traces_out if row.get("role") == key[0] and row.get("peak") == key[1] and row.get("temperature_C") == key[2] and row.get("power_mW") == key[3] and "gamma_coll_err" in row and np.isfinite(float(row.get("gamma_coll_err", "nan")))])
        if _v.size >= 3 and _e.size == _v.size and np.all(_e > 0):
            _S2.append(np.var(_v, ddof=1)); _B2.append(np.mean(_e ** 2)); _D.append(_v.size - 1)
    if len(_S2) >= 4:
        _S2, _B2, _D = np.array(_S2), np.array(_B2), np.array(_D, float)
        def _nll(k2, J2):
            _m = k2 * _B2 + J2
            return float(np.sum(_D / 2.0 * (_S2 / _m + np.log(_m))))
        _Js = np.linspace(0.0, 0.1, 1001); _pJ = np.array([_nll(1.0, J * J) for J in _Js]); _J = float(_Js[_pJ.argmin()]); _inJ = _Js[2 * (_pJ - _pJ.min()) <= 1.0]
        _ks = np.linspace(0.5, 2.5, 801); _pk = np.array([_nll(k * k, 0.0) for k in _ks]); _k = float(_ks[_pk.argmin()]); _ink = _ks[2 * (_pk - _pk.min()) <= 1.0]
        _free = min(((k, J, _nll(k * k, J * J)) for k in np.linspace(0.5, 2.0, 61) for J in np.linspace(0.0, 0.08, 81)), key=lambda q: q[2])
        pull_rows.append({"parameter": "width_variation_J_at_k1", "pooled_mean_square_pull": _J, "n_conditions": len(_S2), "dof": int(_D.sum()),
                          "note": f"MHz. The added between-repeat width variation with the bar's calibration factor fixed at one, one-sigma {_inJ.min():.4f} to {_inJ.max():.4f}. The free fit reads k {_free[0]:.3f} and J {_free[1]:.4f}. A pure factor (J = 0) sits at delta(-2 ln L) {2 * (_pk.min() - _free[2]):.1f} and k = 1 at {2 * (_pJ.min() - _free[2]):.2f}, so the added form is the one the width bars carry (F44)"})
        # per arm (F44): the arms disagree and one pooled J hides it; the 130 C arm's J is
        # the one the width results carry, the temperature arm's (k, J) stands beside it
        _keys = [key for key in sorted(conds) if key in _pooled_sigma and _kept.get(key)]
        _arm = np.array([("130C" if str(key[2]) == "130" else "T-arm") for key in _keys][:len(_S2)])
        for _name in ("130C", "T-arm"):
            _sel = _arm == _name
            if _sel.sum() < 4:
                continue
            _s2, _b2, _d = _S2[_sel], _B2[_sel], _D[_sel]
            def _nll_a(k2, J2, _s2=_s2, _b2=_b2, _d=_d):
                _m = k2 * _b2 + J2
                return float(np.sum(_d / 2.0 * (_s2 / _m + np.log(_m))))
            _pJa = np.array([_nll_a(1.0, J * J) for J in _Js]); _Ja = float(_Js[_pJa.argmin()]); _inJa = _Js[2 * (_pJa - _pJa.min()) <= 1.0]
            _fa = min(((k, J, _nll_a(k * k, J * J)) for k in np.linspace(0.4, 2.0, 81) for J in np.linspace(0.0, 0.08, 81)), key=lambda q: q[2])
            _pka = np.array([_nll_a(k * k, 0.0) for k in _ks])
            pull_rows.append({"parameter": f"width_variation_J_at_k1_{_name}", "pooled_mean_square_pull": _Ja, "n_conditions": int(_sel.sum()), "dof": int(_d.sum()),
                              "note": f"MHz, this arm alone, one-sigma {_inJa.min():.4f} to {_inJa.max():.4f}. The free fit reads k {_fa[0]:.3f} and J {_fa[1]:.4f}. k = 1 sits at delta(-2 ln L) {2 * (_pJa.min() - _fa[2]):.2f} and J = 0 at {2 * (_pka.min() - _fa[2]):.1f}. The width results carry the 130C arm's J and the temperature arm's pair stands beside it (F44)"})
        pull_rows.append({"parameter": "bar_factor_k_at_J0", "pooled_mean_square_pull": _k, "n_conditions": len(_S2), "dof": int(_D.sum()),
                          "note": f"the bar's calibration factor with no added variation, one-sigma {_ink.min():.3f} to {_ink.max():.3f}. It is rejected against the added form by delta(-2 ln L) {2 * (_pk.min() - _free[2]):.1f} (F44)"})
    with open(C.RESULTS_DIR / "linefit_pulls.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["parameter", "pooled_mean_square_pull", "n_conditions", "dof", "note"]); w.writeheader(); w.writerows(pull_rows)
    print("  per-trace pass:", len(traces_out), "traces;", {r["parameter"]: round(r["pooled_mean_square_pull"], 3) for r in pull_rows})

    # ---- total width vs T (degeneracy-robust) ----
    print(f"\n{'='*72}\nTOTAL line FWHM (transition axis, MHz) vs T  [degeneracy-robust]")
    print(f"{'peak':>6s} {'70C':>12s} {'90C':>12s} {'110C':>12s} {'130C(P225)':>12s}")
    def cell(peak, T):
        if T == "130":
            r = next((o for o in out if o["role"] == "p_sweep" and o["peak"] == peak
                      and o["P"] == "225"), None)
        else:
            r = next((o for o in out if o["role"] == "t_sweep" and o["peak"] == peak
                      and o["T"] == T), None)
        return f"{r['total_fwhm']:.2f}" if r else "-"
    for peak in ("4121", "4154", "4192", "4207"):
        print(f"{peak:>6s} " + " ".join(f"{cell(peak,T):>12s}" for T in ("70","90","110","130")))

    # ---- preliminary gamma_coll vs T ----
    print(f"\n{'-'*72}\nPRELIMINARY gamma_coll (MHz) vs T  [degeneracy corr ~ -0.9; NOT beta_self]")
    print(f"{'peak':>6s} {'70C':>14s} {'90C':>14s} {'110C':>14s}")
    for peak in ("4121", "4154", "4192", "4207"):
        cells = []
        for T in ("70", "90", "110"):
            r = next((o for o in out if o["role"] == "t_sweep" and o["peak"] == peak
                      and o["T"] == T), None)
            cells.append(f"{r['gamma_coll']:.2f}+/-{r['gamma_coll_err']:.2f}" if r else "-")
        print(f"{peak:>6s} " + " ".join(f"{c:>14s}" for c in cells))
    print(f"\nmedian laser<->coll corr = "
          f"{np.median([o['corr'] for o in out]):.2f}; "
          f"median chi2_red = {np.median([o['chi2_red'] for o in out]):.2f}")
    print("ALL PRELIMINARY: transit fixed on the OPEN w0 prior; beta_self + "
          "confound program + N(T) are module M4.")
    print(f"\nresidual-tail trims taken by the condition fits: {n_trimmed}. "
          "This producer does not persist a per-trace trim record, so "
          "results/trim_report.csv leaves its `linefit` rows unrecorded. "
          "A nonzero count here is the signal that it has to start.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

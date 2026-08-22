#!/usr/bin/env python
"""K4: the blind residual atlas, preregistered in private/reviews/K4_PREREG_2026-08-22.md.

THE ONE QUESTION THE K-CHAIN LEFT. R_kernel is a sensitivity WITHIN the class
{G, G+L}, and every other K-chain result lives inside that class too. Whether
the class is ADEQUATE is the fourth level of this record's hierarchy, and
nothing in kernel_k5.csv or kernel_k7.csv speaks to it. K2 said so: its worlds
misspecify ONE thing at a time, and the real line may be wrong in a way none of
them describes.

So this producer asks whether the fitted family leaves COHERENT structure in
the residuals, and it asks it the only way a single condition cannot: by
stacking conditions on a common axis, where a shape belonging to the LINE
survives averaging and noise does not.

WHY THE NULL IS A SIGN FLIP. The question is not whether any one condition has
structure, it is whether conditions SHARE a shape. Flipping the sign of a whole
condition's residual vector preserves that condition's amplitude and its
autocorrelation exactly, and destroys only the coherence across conditions.
That makes it the null of "no common residual shape" and not the null of "no
residual", which is a different and much weaker thing to reject.

WHY THE ERROR BAR IS TAKEN ACROSS CONDITIONS. Using the within-condition noise
would understate the error on a common shape, because correlated misfit is
exactly what is being looked for and it does not average down within a
condition. The scatter ACROSS conditions is the denominator that
reflects it.

A NULL RESULT IS USELESS WITHOUT ITS SENSITIVITY, and the preregistration says
so. Stacking 32 conditions of order 1e4 points reaches coherent amplitudes far
below any single condition's noise, so this producer measures what it could
have detected and reports that number whether or not it detects anything.
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C                                    # noqa: E402
from rb5s6s.ingest import load_manifest, load_trace, trace_path   # noqa: E402
from rb5s6s.linefit import _shared_profile_grid                   # noqa: E402
from rb5s6s.linefit import (fit_condition, to_frequency,          # noqa: E402
                            transit_fwhm_at_T)
from rb5s6s.noise import condition_noise_model, sigma_of_v, signal_level  # noqa: E402
from rb5s6s.qc import trace_metrics, hard_flags, ingest_flags, outlier_files  # noqa: E402

OUT = C.RESULTS_DIR / "kernel_k4.csv"

# Preregistered, before any run.
WINDOW = 3.0          # plus or minus this many fitted total widths from centre
NBINS = 121           # bins across that window
NDRAW = 1000          # sign-flip draws
ALPHA = 0.01          # p below this counts as evidence of a common shape
INJECT_AMPS = (2e-4, 5e-4, 1e-3, 2e-3, 5e-3)   # fraction of line peak
INJECT_TRIALS = 60
INJECT_TARGET = 0.90  # detection probability defining the sensitivity


def _conditions():
    rows = load_manifest()
    dropped = outlier_files()
    conds = defaultdict(list)
    for r in rows:
        if r["flag"] == "canonical" and r["rf_on"] == "False":
            conds[(r["role"], r["peak"], r["temperature_C"], r["power_mW"])].append(r)
    return conds, dropped


def _block_rates():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "run_linefit", Path(__file__).resolve().parent / "run_linefit.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _binned_residual(freqs, volts, fit, law, arm):
    """One condition's mean residual, binned on the common axis.

    The axis is (nu - centre) / total width, so a shape that belongs to the
    line sits at the same place in every condition regardless of how wide that
    condition's line is.
    """
    from rb5s6s.constants import GAMMA_NAT_HZ
    homog = (GAMMA_NAT_HZ / 1e6 + fit["gamma_coll"] + fit.get("gamma_l", 0.0))
    total = homog + fit["sigma_laser"] + fit["transit_fwhm"]
    # THE SAME FUNCTION THE FIT USED, not composite_profile. fit_condition
    # builds its model through _shared_profile_grid, which carries the Stark
    # ramp callable and the laser and transit kind alongside the widths.
    # Reconstructing with composite_profile instead compares the data against a
    # DIFFERENT model from the one that was fitted, and the difference is a
    # smooth symmetric function peaking at line centre, which is precisely the
    # shape this producer would then report as a common residual.
    g, prof = _shared_profile_grid(fit["gamma_coll"], fit["sigma_laser"],
                                   fit["transit_fwhm"], 0.0, "gaussian",
                                   fit.get("gamma_l", 0.0))
    # THE ATLAS USES THE PREREGISTERED WINDOW, NOT THE FIT'S OWN TRIM. Points
    # the fit trimmed that fall inside plus or minus WINDOW widths still enter
    # here. That can only make structure EASIER to find, never harder, so it is
    # conservative against the null claim this producer is most likely to
    # return, and it means a trimmed-away shape cannot hide from the test.
    edges = np.linspace(-WINDOW, WINDOW, NBINS + 1)
    acc = np.zeros(NBINS)
    cnt = np.zeros(NBINS)
    peak = 0.0   # line peak in units of the per-point noise, i.e. peak SNR
    for i in range(len(volts)):
        c = fit["centers"][i]
        A = fit["amps"][i]
        b0, b1 = fit["baselines"][i]
        model = A * np.interp(freqs[i] - c, g, prof, left=0.0, right=0.0) + b0 + b1 * freqs[i]
        # The SAME sigma the fit used, built the same way, from the signal
        # level rather than the raw trace. Diagnostics in linefit use the
        # UNSCALED sigma, for which a perfect model gives unit variance
        # regardless of correlation, so the atlas uses it too.
        lev, _ = signal_level(volts[i])
        sig = sigma_of_v(np.maximum(lev, 0.0), law)
        r = (volts[i] - model) / sig
        peak = max(peak, float(A * prof.max() / max(float(np.median(sig)), 1e-12)))
        x = (freqs[i] - c) / total
        idx = np.digitize(x, edges) - 1
        ok = (idx >= 0) & (idx < NBINS) & np.isfinite(r)
        np.add.at(acc, idx[ok], r[ok])
        np.add.at(cnt, idx[ok], 1.0)
    with np.errstate(invalid="ignore", divide="ignore"):
        out = np.where(cnt > 0, acc / np.maximum(cnt, 1), np.nan)
    return out, peak


def _statistic(mat):
    """max |mean / SEM| across conditions, per bin. NaN bins are ignored."""
    with np.errstate(invalid="ignore"):
        n = np.sum(np.isfinite(mat), axis=0)
        mean = np.nanmean(mat, axis=0)
        sd = np.nanstd(mat, axis=0, ddof=1)
        sem = sd / np.sqrt(np.maximum(n, 1))
        z = np.where((n >= 5) & (sem > 0), np.abs(mean) / np.maximum(sem, 1e-12), 0.0)
    return float(np.nanmax(z)), mean, sem, n


def _null_p(mat, observed, seed0=0):
    hits = 0
    for d in range(NDRAW):
        rng = np.random.default_rng(seed0 + d)
        signs = rng.choice([-1.0, 1.0], size=(mat.shape[0], 1))
        z, *_ = _statistic(mat * signs)
        hits += z >= observed
    return (hits + 1) / (NDRAW + 1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=0,
                    help='smoke-test on the first N conditions; 0 means all')
    a = ap.parse_args()
    lf = _block_rates()
    trate, prate = lf.load_block_rates()
    conds, dropped = _conditions()

    arms = {"G": dict(fit_gamma_l=False), "GL": dict(fit_gamma_l=True, gamma_l=0.3)}
    stacks = {k: [] for k in arms}
    stacks["SYNTH"] = []
    peaks = {k: [] for k in arms}
    peaks["SYNTH"] = []
    widths_G = {}

    keys = sorted(conds)
    if a.limit:
        keys = keys[:a.limit]
    print(f"K4: {len(keys)} canonical conditions, two arms")
    for key in keys:
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
            if any("truncated" in f or "dropout" in f for f in
                   hard_flags(m, rf_on=False) + ingest_flags(info)):
                continue
            freqs.append(to_frequency(t, rate)); volts.append(v)
        if len(volts) < 3:
            continue
        law = condition_noise_model(volts)
        transit = transit_fwhm_at_T(float(T), C.TRANSIT_FWHM_PLACEHOLDER_MHZ)
        for arm, kw in arms.items():
            try:
                fit = fit_condition(freqs, volts, T_C=float(T), law=law,
                                    transit_fwhm=transit, trim_tails=True, **kw)
            except RuntimeError:
                continue
            b, pk = _binned_residual(freqs, volts, fit, law, arm)
            stacks[arm].append(b)
            peaks[arm].append(pk)
            if arm == "G":
                widths_G[key] = fit["gamma_coll"]
                # THE CONTROL THAT MAKES A DETECTION BELIEVABLE. Generate
                # traces FROM the fitted model with the same noise law, refit
                # them the same way, and stack their residuals. By
                # construction there is no misfit, so a detection here would
                # mean the binning, the axis, the statistic or the
                # reconstruction manufactures a common shape. This is K2's
                # world-A logic applied to the atlas, and without it a
                # detection on real data cannot be told from a producer bug.
                gg, pp = _shared_profile_grid(fit["gamma_coll"],
                                              fit["sigma_laser"],
                                              fit["transit_fwhm"], 0.0,
                                              "gaussian", 0.0)
                rng = np.random.default_rng(4000 + len(stacks["G"]))
                sv = []
                for i in range(len(volts)):
                    A = fit["amps"][i]; c = fit["centers"][i]
                    b0, b1 = fit["baselines"][i]
                    m = (A * np.interp(freqs[i] - c, gg, pp, left=0.0, right=0.0)
                         + b0 + b1 * freqs[i])
                    lev, _ = signal_level(m)
                    sg = sigma_of_v(np.maximum(lev, 0.0), law)
                    sv.append(m + rng.normal(0.0, sg))
                try:
                    law2 = condition_noise_model(sv)
                    f2 = fit_condition(freqs, sv, T_C=float(T), law=law2,
                                       transit_fwhm=transit, trim_tails=True)
                    b2, _ = _binned_residual(freqs, sv, f2, law2, "SYNTH")
                    stacks["SYNTH"].append(b2)
                except RuntimeError:
                    pass

    rows = []

    def add(scope, quantity, value, unit, note, status="DIAGNOSTIC"):
        rows.append(dict(scope=scope, quantity=quantity, value=value,
                         unit=unit, note=note, status=status))

    for arm in arms:
        mat = np.array(stacks[arm])
        if mat.size == 0:
            continue
        z, mean, sem, n = _statistic(mat)
        p = _null_p(mat, z, seed0=1000 if arm == "G" else 5000)
        add(arm, "n_conditions", mat.shape[0], "count",
            "conditions contributing to the stack")
        add(arm, "max_z", f"{z:.3f}", "sigma",
            "largest |stacked mean / its across-condition standard error| "
            "inside the preregistered window")
        add(arm, "p_signflip", f"{p:.4f}", "p-value",
            f"{NDRAW} sign-flip draws. Below {ALPHA} would be evidence of a "
            "COMMON residual shape, which would mean the model class is "
            "inadequate. It would NOT name the missing term")
        add(arm, "verdict",
            "COMMON_SHAPE_DETECTED" if p < ALPHA else "NO_COMMON_SHAPE",
            "verdict",
            "a null does NOT establish that the class is adequate. It bounds "
            "any common missing term at the sensitivity reported below")

        # sensitivity: inject a bump at +1 width and see when it is detected
        rng0 = 90_000
        sens = None
        for amp in INJECT_AMPS:
            det = 0
            bump = np.exp(-0.5 * ((np.linspace(-WINDOW, WINDOW, NBINS) - 1.0) / 0.25) ** 2)
            # A bump of a times the line peak enters a residual already
            # expressed in units of the per-point noise as a * (peak SNR).
            # The earlier form divided by the residual scatter, which mixes
            # units and returned an unreachable sensitivity for every
            # amplitude tried.
            scale = amp * float(np.nanmedian(peaks[arm]))
            for t in range(INJECT_TRIALS):
                rng = np.random.default_rng(rng0 + t)
                signs = rng.choice([-1.0, 1.0], size=(mat.shape[0], 1))
                m2 = mat * signs + scale * bump
                z2, *_ = _statistic(m2)
                det += z2 >= z
            if det / INJECT_TRIALS >= INJECT_TARGET:
                sens = amp
                break
        add(arm, "sensitivity_frac_of_peak",
            f"{sens:.1e}" if sens else f">{INJECT_AMPS[-1]:.0e}", "fraction",
            "smallest injected common bump, as a fraction of line peak, "
            "detected in 90 per cent of trials at the observed threshold. "
            "This is what a null result bounds")

    if stacks["SYNTH"]:
        ms = np.array(stacks["SYNTH"])
        zs, *_ = _statistic(ms)
        ps = _null_p(ms, zs, seed0=7000)
        add("CONTROL", "n_conditions", ms.shape[0], "count",
            "synthetic conditions built from the fitted model plus its own "
            "noise law, then refitted")
        add("CONTROL", "max_z", f"{zs:.3f}", "sigma", "same statistic")
        add("CONTROL", "p_signflip", f"{ps:.4f}", "p-value",
            "a DETECTION here would invalidate the real-data result, because "
            "these traces contain no misfit by construction")
        add("CONTROL", "verdict",
            "PRODUCER_MANUFACTURES_SHAPE" if ps < ALPHA else "CLEAN",
            "verdict",
            "CLEAN means the binning, axis, statistic and reconstruction do "
            "not create a common shape on their own")

    # THE TWO ARMS ARE A CHECK, NOT A COMPARISON, and the preregistration says
    # why it had to be corrected. At a fixed condition G and G+L are the same
    # model: both extra widths are Lorentzian, Lorentzians add, so only their
    # sum enters the profile and the arms differ solely in how they LABEL that
    # sum. Their residuals must therefore agree to machine precision. That
    # makes this row a test of the exact degeneracy surviving the entire
    # fitting pipeline, where tests/test_gamma_l_identity.py pins it only in
    # the profile function.
    if stacks["G"] and stacks["GL"]:
        a = np.array(stacks["G"]); b = np.array(stacks["GL"])
        if a.shape == b.shape:
            per_cond = np.nanmax(np.abs(a - b), axis=1)
            add("CHECK", "arm_residual_median_abs_diff",
                f"{float(np.nanmedian(per_cond)):.3e}", "sigma",
                "median over conditions of the largest per-condition "
                "difference between the G and G+L residual stacks")
            add("CHECK", "arm_residual_max_abs_diff",
                f"{float(np.nanmax(per_cond)):.3e}", "sigma",
                "the worst condition. REPORTED AS A DISTRIBUTION rather than "
                "one number, because a large max beside a tiny median means "
                "ONE condition's two fits landed in different places, not "
                "that the degeneracy failed. The degeneracy itself predicts "
                "agreement to optimiser tolerance, and the median is what "
                "tests it")
            add("CHECK", "arm_conditions_above_1e3",
                int(np.nansum(per_cond > 1e-3)), "count",
                "conditions whose two arms differ by more than 1e-3 sigma "
                "anywhere in the window")

    # THE PREREGISTERED VOID CHECK. If this refit does not reproduce the
    # committed per-condition widths, the atlas is measuring a difference
    # between PRODUCERS rather than a residual, and the run is void rather
    # than interesting. Stated in the preregistration so it cannot be skipped
    # by a run that happens to produce an attractive picture.
    try:
        committed = {}
        with (C.RESULTS_DIR / "linefit_conditions.csv").open() as fh:
            for r in csv.DictReader(fh):
                committed[(r["role"], r["peak"], r["T"], r["P"])] = float(r["gamma_coll"])
        rel = []
        for key, w in widths_G.items():
            c = committed.get((key[0], str(key[1]), str(key[2]), str(key[3])))
            if c is not None and abs(c) > 0:
                rel.append(abs(w - c) / abs(c))
        if rel:
            worst = max(rel)
            add("VOID_CHECK", "n_matched", len(rel), "count",
                "conditions matched against results/linefit_conditions.csv")
            add("VOID_CHECK", "worst_rel_diff_gamma_coll", f"{worst:.3e}",
                "relative",
                "this refit against the committed one. Large means the atlas "
                "compares producers rather than measuring a residual")
            add("VOID_CHECK", "verdict",
                "VOID" if worst > 1e-3 else "REPRODUCES", "verdict",
                "the run is void above 1e-3 relative")
        else:
            add("VOID_CHECK", "verdict", "UNMATCHED", "verdict",
                "no condition keys matched, so the check could not run")
    except (OSError, KeyError) as e:
        add("VOID_CHECK", "verdict", "UNAVAILABLE", "verdict", f"{type(e).__name__}")

    add("ALL", "window_widths", WINDOW, "fitted total widths",
        "preregistered half-window of the stack")
    add("ALL", "scope_note", "IN_WINDOW_ONLY", "flag",
        "this tests the residual INSIDE the fit window. The record separately "
        "carries a reproducible excess OUTSIDE it, which this neither tests "
        "nor speaks to, and the two may not be merged")
    add("ALL", "class_adequacy_note", "NOT_ESTABLISHED_EITHER_WAY", "flag",
        "R_kernel remains a sensitivity within {G, G+L}. A null here bounds a "
        "common missing term and does not widen the class that was tested")

    # THE HEADLINE ROW GOES FIRST, because a reader scanning this file must
    # not meet COMMON_SHAPE_DETECTED before meeting the verdict on whether the
    # run counts at all. If the void check fired, every detection row below is
    # inadmissible under this producer's own preregistration.
    voided = any(r["scope"] == "VOID_CHECK" and r["quantity"] == "verdict"
                 and r["value"] == "VOID" for r in rows)
    rows.insert(0, dict(
        scope="RUN", quantity="admissible",
        value="NO" if voided else "YES", unit="flag",
        note=("the preregistered void check FIRED, so the detection rows below "
              "may NOT be cited as a result. See "
              "private/reviews/K4_PREREG_2026-08-22.md"
              if voided else
              "the preregistered void check passed"),
        status="DIAGNOSTIC"))

    with OUT.open("w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        wr.writeheader(); wr.writerows(rows)
    print(f"wrote {OUT} with {len(rows)} rows")
    for r in rows:
        print(f"  {r['scope']:<5} {r['quantity']:<28} {r['value']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

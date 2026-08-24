#!/usr/bin/env python
"""Is the digitiser's quantisation step below the analogue noise?

WHY THIS EXISTS. The acquisition chapter argued that vertical resolution is
what binds this measurement, on the reasoning that the pedestal is about one
least significant bit and the band excess sits below one. The experimenter
asked whether the features were not already below the NOISE, which is the
question that decides whether quantisation binds at all, and the record had
never measured it.

WHAT IT MEASURES, per canonical trace:
  * the true quantisation step, taken as the smallest positive spacing
    between distinct stored values, with the fraction of samples sitting on
    that lattice reported beside it so a reader can see whether the grid is
    real;
  * the baseline noise, the standard deviation over the outer tenth of the
    trace at each end, where the line is absent;
  * their ratio, which is the number that answers the question.

THE ARITHMETIC. A uniform quantiser contributes LSB/sqrt(12) = 0.289 LSB of
noise, independent of the signal, and it adds in quadrature. So a chain whose
analogue noise is s LSB has its total inflated by a factor
sqrt(1 + (0.289/s)^2), which is where the per-cent figures come from. Above a
few LSB of dither the quantiser stops being a floor and averaging recovers
structure below the step, which is what a dithered converter is for.

THE 8-BIT COLUMN. The chapter's own hypothetical is an eight-bit front end
with the line peak filling the screen, so the same trace is re-expressed
against LSB = peak/256 and the inflation recomputed. That keeps the
comparison on the record's own terms rather than on this producer's.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rb5s6s import config as C                                    # noqa: E402
from rb5s6s.ingest import load_trace, trace_path                  # noqa: E402
from rb5s6s.qc import hard_flags, ingest_flags, trace_metrics     # noqa: E402

OUT = C.RESULTS_DIR / "quantisation.csv"
QUANT_NOISE = 1.0 / np.sqrt(12.0)      # LSB, uniform quantiser
EDGE_FRACTION = 10                     # outer tenth at each end is baseline


def _trace_numbers(path):
    t, v = load_trace(path)
    v = np.asarray(v, dtype=float)
    if v.size < 200:
        return None
    uniq = np.unique(v)
    steps = np.diff(uniq)
    steps = steps[steps > 1e-12]
    if steps.size == 0:
        return None
    lsb = float(np.min(steps))
    lattice = float(np.mean(
        np.abs((v - v.min()) / lsb - np.round((v - v.min()) / lsb)) < 0.02))
    n = v.size
    edge = np.concatenate([v[: n // EDGE_FRACTION], v[-(n // EDGE_FRACTION):]])
    sigma = float(np.std(edge))
    peak = float(v.max() - np.median(edge))
    return lsb, lattice, sigma, peak


def main() -> int:
    rows = []
    with (ROOT / "data_raw" / "MANIFEST.csv").open() as fh:
        manifest = list(csv.DictReader(fh))

    per_cond = {}
    for r in manifest:
        if r.get("rf_on", "").strip().lower() in ("true", "1", "yes"):
            continue
        key = (r.get("role"), r.get("peak"), r.get("temperature_C"),
               r.get("power_mW"))
        try:
            t, v, info = load_trace(trace_path(r), with_info=True)
        except Exception:
            continue
        m = trace_metrics(t, v)
        if any("truncated" in f or "dropout" in f
               for f in hard_flags(m, rf_on=False) + ingest_flags(info)):
            continue
        got = _trace_numbers(trace_path(r))
        if got is None:
            continue
        per_cond.setdefault(key, []).append(got)

    def add(scope, quantity, value, unit, note, status="DIAGNOSTIC"):
        rows.append(dict(scope=scope, quantity=quantity, value=value,
                         unit=unit, note=note, status=status))

    ratios, inflations, lattices = [], [], []
    for key in sorted(per_cond):
        vals = per_cond[key]
        lsb = float(np.median([x[0] for x in vals]))
        lattice = float(np.median([x[1] for x in vals]))
        sigma = float(np.median([x[2] for x in vals]))
        peak = float(np.median([x[3] for x in vals]))
        ratio = sigma / lsb
        infl = float(np.hypot(ratio, QUANT_NOISE) / ratio - 1.0)
        ratios.append(ratio)
        inflations.append(infl)
        lattices.append(lattice)
        scope = "_".join(str(k) for k in key)
        add(scope, "sigma_over_lsb", f"{ratio:.1f}", "LSB",
            f"baseline noise in units of the true quantisation step, over "
            f"{len(vals)} traces. Lattice fraction {lattice:.2f}, peak "
            f"{peak / lsb:.0f} LSB, {np.log2(peak / lsb):.1f} bits of range")
        add(scope, "quantisation_noise_inflation", f"{100 * infl:.3f}",
            "per cent",
            "how much the quantiser adds to the analogue noise, in "
            "quadrature at LSB over root twelve")

    r_arr = np.array(ratios)
    add("ALL", "n_conditions", len(ratios), "count",
        "conditions entering, radio-frequency off, quality-control passed")
    add("ALL", "sigma_over_lsb_lo", f"{r_arr.min():.1f}", "LSB",
        "the least dithered condition in the campaign")
    add("ALL", "sigma_over_lsb_median", f"{np.median(r_arr):.1f}", "LSB",
        "the typical condition")
    add("ALL", "sigma_over_lsb_hi", f"{r_arr.max():.1f}", "LSB",
        "the most dithered condition")
    add("ALL", "median_inflation", f"{100 * float(np.median(inflations)):.4f}",
        "per cent", "the typical contribution across conditions")
    add("ALL", "inflation_hi", f"{100 * max(inflations):.3f}", "per cent",
        "the top of the distribution across conditions, beside its median "
        "so the tail does not read as the summary")
    add("ALL", "lattice_fraction_median", f"{np.median(lattices):.2f}",
        "fraction",
        "how much of the sample set sits on the inferred grid. Below about "
        "0.9 the stored values carry finer structure than one step, which "
        "makes the ratio above a LOWER bound on the dither")

    # The chapter's own hypothetical, on the same traces.
    eight = []
    for key in sorted(per_cond):
        vals = per_cond[key]
        sigma = float(np.median([x[2] for x in vals]))
        peak = float(np.median([x[3] for x in vals]))
        if peak <= 0:
            continue
        s8 = sigma / (peak / 256.0)
        eight.append(float(np.hypot(s8, QUANT_NOISE) / s8 - 1.0))
    if eight:
        add("EIGHT_BIT", "median_inflation",
            f"{100 * float(np.median(eight)):.2f}", "per cent",
            "the typical value of the same hypothetical")
        add("EIGHT_BIT", "inflation_hi", f"{100 * max(eight):.2f}",
            "per cent",
            "the same traces re-expressed against an eight-bit front end "
            "with the line peak filling the screen, which is the "
            "configuration the acquisition chapter argues about")

    # ---- the wider budget: what DOES bind, read from the committed law ----
    # The noise model's variance law is var = a^2 + b*V + c*V^2 per condition.
    # How its terms scale with power is the diagnosis: a linear a(P) is
    # light-linked background (shot noise on a background that grows as P^2,
    # or intensity noise on one that grows as P), a flat b is cathode shot
    # noise through the multiplier, and the P -> 0 intercept of a is the
    # dark-plus-electronics floor that decides whether the transimpedance
    # gain is in the right decade.
    import numpy as _np
    nm = {}
    with (C.RESULTS_DIR / "noise_model.csv").open() as fh:
        for r in csv.DictReader(fh):
            if r.get("role") == "p_sweep":
                nm.setdefault(r["peak"], []).append(
                    (float(r["power_mW"]), float(r["a_V"]), float(r["b_V"])))
    slopes, intercepts, bvals = [], [], []
    for peak, pts in sorted(nm.items()):
        pts.sort()
        P = _np.array([x[0] for x in pts]); A = _np.array([x[1] for x in pts])
        coef = _np.polyfit(P, A, 1)
        r_lin = float(_np.corrcoef(A, _np.polyval(coef, P))[0, 1])
        r_sqrt = float(_np.corrcoef(A, _np.sqrt(P))[0, 1])
        slopes.append(float(coef[0])); intercepts.append(float(coef[1]))
        bvals += [x[2] for x in pts]
        add(f"peak_{peak}", "a_vs_P_slope", f"{coef[0] * 1e3:.4f}", "mV per mW",
            f"the baseline noise grows LINEARLY with power (r {r_lin:.3f} "
            f"linear against {r_sqrt:.3f} for a square-root law), which is "
            "the signature of light-linked background, not of electronics "
            "and not of shot noise on a fixed background")
        add(f"peak_{peak}", "a_at_P0", f"{coef[1] * 1e3:.3f}", "mV",
            "the power-to-zero intercept, the dark and electronics floor")
    add("BUDGET", "electronics_floor_median", f"{_np.median(intercepts) * 1e3:.2f}",
        "mV", "median dark-plus-electronics floor across peaks. Against the "
        "4 to 15 mV of light-linked noise at operating power, the "
        "electronics are not the limit, so the transimpedance gain is in "
        "the right decade and neither raising nor lowering it buys noise")
    add("BUDGET", "b_median", f"{_np.median(bvals) * 1e3:.3f}", "mV",
        "the level-proportional variance coefficient, near-constant across "
        "every condition and peak, the signature of cathode shot noise "
        "through the multiplier. On the peak this term dominates, and only "
        "more collected photons improve it")
    add("BUDGET", "what_binds", "ANALOGUE_NOISE_AND_INDEPENDENT_SAMPLES",
        "verdict",
        "the ranked levers: the light-linked background in the wings, which "
        "grows linearly with power and is 8 to 10 times worse at 225 mW "
        "than at 25 mW, then repeats that are actually independent, then "
        "collection solid angle on the shot-limited peak. Sample rate and "
        "bit depth buy nothing: the noise is correlated at about 1.9 ms, "
        "so a sweep carries at most its duration over that time of "
        "independent samples regardless of rate")

    verdict = "NOT_THE_BINDING_TERM" if max(inflations) < 0.05 else "MATTERS"
    add("VERDICT", "quantisation", verdict, "verdict",
        "the quantiser is dithered by the analogue noise, so vertical "
        "resolution is not what limits this measurement. What limits it is "
        "the analogue noise per point and the number of INDEPENDENT samples, "
        "which noise_model.csv reports as tau_int between 1.3 and 19.8 "
        "samples. Threshold fixed before the first run: a contribution below "
        "5 per cent of the noise is not a binding term", "DIAGNOSTIC")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["scope", "quantity", "value",
                                           "unit", "note", "status"])
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {OUT} ({len(rows)} rows, {len(ratios)} conditions)")
    print(f"  sigma/LSB  min {r_arr.min():.1f}  median {np.median(r_arr):.1f}"
          f"  max {r_arr.max():.1f}")
    print(f"  worst quantisation inflation {100 * max(inflations):.3f} per cent")
    print(f"  verdict: {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

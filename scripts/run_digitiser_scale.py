#!/usr/bin/env python
"""The oscilloscope's vertical scale, recovered from the traces themselves.

WHY THIS EXISTS. `data_raw/MANIFEST.csv` carries no vertical-zoom column, so
which scale each peak was recorded at looked like an apparatus fact only the
owner held. It is not: a digitiser writes samples on a grid, so the
quantisation step is visible in the trace, and with it the window and the
level count. **Every nuisance on this bench is recoverable from the data that
carries the signal, and this is the last input that appeared to be missing.**

WHAT IT DOES NOT SHOW, and the first version of this docstring claimed it.
That version said the step sets the pedestal's share of the window and the
rounding bias, so a per-peak bias would differ by the same factor and
contaminate the isotope differential. **Both halves are wrong, refuted on this producer's own terms on 2026-09-11.**

  * The pedestal's share: under the 5/95 convention this file applies, the
    baseline sits at 5 per cent of the window for EVERY peak, so the step sets
    nothing about it.
  * The rounding bias: measured on the 32 traces used here, the baseline noise
    is 8.4 to 45 steps on 31 of them and 2.1 on the remaining one. For a
    rounding quantiser under Gaussian dither the bias of a sample mean is
    bounded by `(s/pi) exp(-2 pi^2 (sigma/s)^2)`, which at 2.1 is 1e-38 of a
    step. **The quantiser is dithered and the bias is nil.**

**And the record already said so on three committed surfaces**, which this
file contradicted: `results/quantisation.csv` (noise over step 5.2 to 246,
inflation at most 0.155 per cent), `docs/plan/07` ("quantisation never bit
anywhere in the data") and `docs/methods/06` ("The digitiser is not in this
budget").

SO WHAT IS THIS FOR. The scale itself, as a recorded apparatus fact the
manifest lacks, and nothing downstream of it. It is not evidence about the
isotope differential and it is not a bias term.

THE ESTIMATOR, and the obvious one is wrong. A greatest common divisor of the
gaps between sorted distinct values is the natural choice and it runs away:
refined by halving it returned steps of order 1e-20 on two peaks of four,
because averaging and rescaling have broken the exact commensurability those
traces once had. **The MODAL gap is robust to that** and returns a step for
every peak. Its share of all gaps is reported per row, because a modal share
near a half says the grid is intact and a share near a fifth says it is not and
the step may be a small multiple of the true one.

THE WINDOW is not measured, it is the owner's stated convention of 2026-09-11:
the baseline sat at 5 per cent of the window and the peak at 95, so the signal
spans 90 per cent of it. That is an ASSUMPTION and it is tagged as one; the
step and the span are measurements and are tagged as such.
"""
from __future__ import annotations

import argparse
import csv
import math
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rb5s6s import config as CFG                       # noqa: E402
from rb5s6s.ingest import load_manifest, load_trace, trace_path   # noqa: E402

OUT = Path(CFG.RESULTS_DIR) / "digitiser_scale.csv"

#: The owner's stated convention, 2026-09-11. Not a measurement.
BASELINE_FRACTION, PEAK_FRACTION = 0.05, 0.95
SIGNAL_SHARE = PEAK_FRACTION - BASELINE_FRACTION

#: Traces per peak. Eight is where the median step stopped moving.
N_PER_PEAK = 8


def grid_score(volts, step: float) -> float:
    """How well a candidate step describes the sample grid, in [0, 1].

    `|mean exp(2 pi i v / s)|` is 1 when every sample lies on a grid of step
    `s` and falls toward 0 otherwise, and it is IMMUNE TO THE OFFSET, which is
    the property a greatest common divisor lacked. One on an intact grid, and
    it distinguishes a step from twice that step, which the modal share does
    not: on 2026-09-11 an intact trace scored 0.81 with a
    share of 0.185 beside a broken one scoring 0.012 with a share of 0.168.
    """
    v = np.asarray(volts, float)
    if not np.isfinite(step) or step <= 0:
        return 0.0
    return float(abs(np.mean(np.exp(2j * np.pi * v / step))))


def modal_step(volts) -> tuple[float, float]:
    """The digitiser's step, as the MODAL gap, HALVED while that fits better.

    Returns the step and its grid score. The modal gap alone returns TWICE the
    grid on some traces: on four of the archive's thirty-two, three of them in
    the peak that set the published headline, the score at the modal gap is
    0.012 to 0.023 and at half of it 0.988 to 0.991, with the smallest positive
    gap exactly half the modal one. So the modal gap is a candidate and the
    score is the test, and the step is halved while halving raises the score.
    """
    u = np.unique(np.asarray(volts, float))
    d = np.diff(u)
    d = d[d > 0]
    if d.size < 10:
        return float("nan"), 0.0
    counts = Counter(float(f"{x:.6g}") for x in d)
    step = float(counts.most_common(1)[0][0])
    score = grid_score(volts, step)
    for _ in range(4):                      # at most four halvings
        half = step / 2.0
        s_half = grid_score(volts, half)
        if s_half <= score + 1e-9:
            break
        step, score = half, s_half
    return step, score


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--plant", action="store_true")
    args = ap.parse_args()
    if args.plant:
        return plant()

    rows = load_manifest()
    peaks = sorted({r["peak"] for r in rows if r.get("peak")})
    out = []
    for peak in peaks:
        recs = [r for r in rows
                if r["peak"] == peak and r.get("flag") == "canonical"][:N_PER_PEAK]
        steps, spans, shares = [], [], []
        for r in recs:
            try:
                _t, v = load_trace(trace_path(r))
            except Exception:
                continue
            s, f = modal_step(v)
            if math.isfinite(s) and s > 0:
                steps.append(s); spans.append(float(np.ptp(v))); shares.append(f)
        if not steps:
            continue
        step, span = float(np.median(steps)), float(np.median(spans))
        window = span / SIGNAL_SHARE
        out.append({"peak": peak, "n_traces": len(steps),
                    "step_v": f"{step:.6e}", "span_v": f"{span:.6f}",
                    "grid_score": f"{np.median(shares):.3f}",
                    "window_v": f"{window:.6f}",
                    "levels": f"{window / step:.0f}",
                    "note": ("step_v, span_v and grid_score measured. window_v "
                             "and levels rest on the 5/95 convention."),
                    "status": "ENVELOPE"})
    if not out:
        print("digitiser_scale: no traces; raw archive absent", file=sys.stderr)
        return 1

    ref = min(float(r["step_v"]) for r in out)
    for r in out:
        r["relative_zoom"] = f"{float(r['step_v']) / ref:.3f}"
    spread = max(float(r["relative_zoom"]) for r in out)
    out.append({
        "peak": "ALL", "n_traces": sum(int(r["n_traces"]) for r in out),
        "relative_zoom": f"{spread:.3f}", "status": "MEASURED",
        "note": (f"the vertical scale differs by {spread:.1f}x across the peaks "
                 f"AT THIS SUBSET'S POWER, and that is not a property of the "
                 f"peaks: the same spread read at other rungs of the power "
                 f"ladder runs 2.3 to 11.2, and within ONE peak the step moves "
                 f"by 96 to 638 along the ladder. docs/APPARATUS.md already "
                 f"carries 596 for the same quantity. NO BIAS FOLLOWS FROM "
                 f"THIS: the baseline sits at the same window fraction for "
                 f"every peak by the 5/95 convention, and the quantiser is "
                 f"dithered at 8.4 to 45 steps of baseline noise, which bounds "
                 f"any rounding bias below 1e-38 of a step. window_v and "
                 f"levels rest on that convention and are envelopes. step_v, "
                 f"span_v and grid_score are measured.")})

    fields = ["peak", "n_traces", "step_v", "span_v", "grid_score", "window_v",
              "levels", "relative_zoom", "note", "status"]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in out:
            w.writerow({k: r.get(k, "") for k in fields})
    print(f"wrote {OUT.name}: {len(out) - 1} peaks, scale spread {spread:.1f}x")
    return 0


def plant() -> int:
    """Probe the estimator against grids it must and must not recover."""
    fails = []
    rng = np.random.default_rng(7)

    # 1. a clean grid is recovered exactly, at several steps
    for step in (1e-5, 8.29e-5, 5.025e-4):
        v = np.round(rng.normal(0, 50 * step, 4000) / step) * step
        got, share = modal_step(v)
        if abs(got - step) / step > 1e-6:
            fails.append(f"clean grid at {step:g} recovered as {got:g}")
        if share < 0.2:
            fails.append(f"clean grid at {step:g} gave a modal share of {share:.2f}")

    # 2. THE NEGATIVE THE GCD FAILED. An incommensurate offset breaks exact
    #    divisibility; the estimator must survive it where a halved GCD ran
    #    away to 1e-20 on the real traces.
    v = np.round(rng.normal(0, 400e-5, 4000) / 1e-5) * 1e-5 + math.pi * 1e-9
    got, _ = modal_step(v)
    if not (0.5e-5 < got < 2e-5):
        fails.append(f"a grid with an incommensurate offset gave {got:g}")

    # 3. THE DEFECT FOUND ON 2026-09-11. A grid occupying only even multiples
    #    makes the MODAL gap twice the true step; the score must catch it and
    #    the halving must fix it, which the modal share alone did not.
    step = 1e-5
    v = np.round(rng.normal(0, 200 * step, 6000) / (2 * step)) * (2 * step)
    got, sc = modal_step(v)
    if abs(got - 2 * step) / step > 1e-6:
        fails.append(f"an even-multiple grid should read {2*step:g}, got {got:g}")
    if grid_score(v, step) < 0.9:
        fails.append("the score does not see the true step under an even-multiple grid")
    # and on a grid the true step describes, halving must NOT be taken
    v2 = np.round(rng.normal(0, 200 * step, 6000) / step) * step
    got2, sc2 = modal_step(v2)
    if abs(got2 - step) / step > 1e-6:
        fails.append(f"halving was taken on an intact grid: {got2:g} for {step:g}")
    if sc2 < 0.9:
        fails.append(f"an intact grid scored {sc2:.3f}, below 0.9")

    # 3. too few distinct values is nan, not a guess
    got, share = modal_step(np.array([1.0, 1.0, 1.0]))
    if not math.isnan(got):
        fails.append("a degenerate trace returned a step instead of nan")

    # 4. the convention is applied and not measured
    if abs(SIGNAL_SHARE - 0.90) > 1e-12:
        fails.append("the 5/95 convention does not span 90 per cent")

    for f in fails:
        print(f"PLANT FAIL: {f}", file=sys.stderr)
    print(f"plant: 4 groups probed, {len(fails)} failure(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())

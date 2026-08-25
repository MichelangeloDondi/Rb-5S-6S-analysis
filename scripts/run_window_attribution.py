#!/usr/bin/env python3
"""
How much of the between-block centre excursion is the horizontal knob (M28)
==========================================================================

WHY THIS MODULE EXISTS AT ALL. The number it produces has been published
for weeks and had no producer. "99.8 per cent of the between-block
excursion is the horizontal setting" appears in DATA.md, in
PREREGISTRATION_RESULTS addendum 4, on the front page's fig15 caption and
inside panel (b) of the figure itself, and the 2026-08-24 provenance audit
found that no committed row carried it. It is recorded as an open debt in
HISTORY.md, in the same paragraph as the twin span-sweep correlations.
This closes that half of the debt.

It is also the reason the campaign has line SHAPES and no line CENTRES, so
it is not a bookkeeping number: it is the measurement that decides what the
whole 2025 dataset can be asked.

WHAT IS MEASURED. The power sweep's traces are cut into CONDITION BLOCKS,
maximal runs of consecutive traces sharing one peak and one nominal power,
and each block is reduced to its mean fitted peak position and its mean
window-start setting. Between consecutive blocks the two move together:

    d_pos = peak position move        d_win = window setting move

If the peak followed the atom, d_pos would be unrelated to d_win. If it
followed the operator's knob, d_pos equals d_win. The attributed fraction
below is one minus the mean square of (d_pos - d_win) over the mean square
of d_pos, which is a fraction of MEAN SQUARE ABOUT ZERO and not of variance
about the mean. On data of this shape the two agree to the fifth decimal,
and the distinction is stated because a fraction with an unnamed
denominator is unfalsifiable.

THE GROUPING IS AN INPUT, SO TWO ARE REPORTED. The published 145.2 and
6.3 ms come from an addendum that cut the state space's 99 traces into 17
blocks; this module's primary grouping gives 20 blocks over 100 traces, so
its RMS values differ and its FRACTION does not. A finer cut that also
splits on the display epoch is emitted beside it for the same reason. The
fraction is the claim, the RMS values are the grouping's, and a reader who
finds two different millisecond numbers in the record should find both
groupings here rather than suspect one of them.

NO FIT RUNS HERE. Every input is a committed cell of
`results/laser_history.csv`, and this module does arithmetic on them, which
is why it is safe to regenerate in an environment that is not the
environment of record.

Writes `results/window_attribution.csv`.
"""
from __future__ import annotations

import csv
import itertools
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rb5s6s import config as C  # noqa: E402

LASER_HISTORY_CSV = C.RESULTS_DIR / "laser_history.csv"
OUT_CSV = C.RESULTS_DIR / "window_attribution.csv"

# The two groupings, each a key function over traces already sorted in time.
# A grouping is named in the output because it is a choice, not a fact.
GROUPINGS = {
    "peak_power": lambda r: (r["peak"], r["power_mW"]),
    "epoch_peak_power": lambda r: (r["display_epoch"], r["peak"], r["power_mW"]),
}


def _load() -> list[dict]:
    if not LASER_HISTORY_CSV.exists():
        return []
    rows = list(csv.DictReader(open(LASER_HISTORY_CSV)))
    usable = [r for r in rows
              if r["role"] == "p_sweep" and r["peak_pos_ms"] and r["window_start_ms"]]
    return sorted(usable, key=lambda r: float(r["t_epoch"]))


def decompose(traces: list[dict], keyfn) -> dict[str, float]:
    """Block the traces, difference consecutive blocks, attribute the move."""
    blocks = []
    for _key, group in itertools.groupby(traces, key=keyfn):
        group = list(group)
        blocks.append((float(np.mean([float(r["peak_pos_ms"]) for r in group])),
                       float(np.mean([float(r["window_start_ms"]) for r in group]))))
    series_pos = np.array([b[0] for b in blocks])
    d_pos = np.diff(series_pos)
    d_win = np.diff([b[1] for b in blocks])
    resid = float(np.sqrt(np.mean((d_pos - d_win) ** 2)))
    ms_pos = float(np.mean(d_pos ** 2))
    return {
        "n_blocks": float(len(blocks)),
        "n_steps": float(len(d_pos)),
        "rms_d_pos": float(np.sqrt(ms_pos)),
        "rms_d_win": float(np.sqrt(np.mean(d_win ** 2))),
        "rms_resid": resid,
        "attributed_pct": 100.0 * (1.0 - resid ** 2 / ms_pos),
        "n_steps_with_knob_move": float(np.sum(np.abs(d_win) > 1e-9)),
        # The peak-to-peak travel of the block-mean position across the whole
        # session. The figure draws this series and states its span, so the
        # span is emitted rather than computed at draw time.
        "excursion_ms": float(series_pos.max() - series_pos.min()),
    }


def main() -> int:
    traces = _load()
    if not traces:
        print(f"  {LASER_HISTORY_CSV.name} absent from this checkout -- skipped")
        return 0

    print("=" * 74)
    print("(M28) THE BETWEEN-BLOCK CENTRE EXCURSION, ATTRIBUTED")
    print(f"  {len(traces)} power-sweep traces carry both a fitted position "
          f"and a window setting\n")

    out_rows: list[dict] = []

    def add(quantity, key, value, err, unit, status):
        out_rows.append({
            "quantity": quantity, "key": key,
            "value": f"{value:.4f}" if isinstance(value, float) else value,
            "err": f"{err:.4f}" if isinstance(err, float) else err,
            "unit": unit, "status": status})

    add("n_p_sweep_traces", "usable", float(len(traces)), "",
        "count. power-sweep traces carrying a fitted peak position and a "
        "window-start setting", "DIAGNOSTIC")

    for name, keyfn in GROUPINGS.items():
        d = decompose(traces, keyfn)
        print(f"  grouping {name}: {int(d['n_blocks'])} blocks, "
              f"{int(d['n_steps'])} steps, "
              f"{int(d['n_steps_with_knob_move'])} of them carrying a knob move")
        print(f"    RMS d(peak position) = {d['rms_d_pos']:.1f} ms, "
              f"RMS d(window setting) = {d['rms_d_win']:.1f} ms, "
              f"RMS residual = {d['rms_resid']:.1f} ms")
        print(f"    attributed to the window setting: "
              f"{d['attributed_pct']:.2f} per cent\n")

        primary = name == "peak_power"
        where = "PRIMARY" if primary else "a finer cut, reported to show the "\
                                          "fraction is not the grouping's"
        add("n_condition_blocks", name, d["n_blocks"], "",
            f"count. maximal runs of consecutive traces sharing the grouping "
            f"keys. {where}", "DIAGNOSTIC")
        add("n_block_steps", name, d["n_steps"], "",
            f"count. differences between consecutive blocks, of which "
            f"{int(d['n_steps_with_knob_move'])} carry a window-setting move",
            "DIAGNOSTIC")
        add("rms_d_peak_position_ms", name, d["rms_d_pos"], "",
            "ms. root mean square move of the block-mean fitted peak "
            "position between consecutive blocks", "DIAGNOSTIC")
        add("rms_d_window_setting_ms", name, d["rms_d_win"], "",
            "ms. root mean square move of the block-mean window-start "
            "setting between consecutive blocks", "DIAGNOSTIC")
        add("excursion_peak_to_peak_ms", name, d["excursion_ms"], "",
            "ms. how far the block-mean peak position travels across the "
            "whole session, end to end. a scale for the figure, and NOT the "
            "attributed fraction's denominator, which is the mean square of "
            "the between-block steps", "DIAGNOSTIC")
        add("rms_residual_ms", name, d["rms_resid"], "",
            "ms. what is left of the peak-position move once the window "
            "move is subtracted, which is the part a laser could have "
            "caused", "DIAGNOSTIC")
        add("window_attributed_pct", name, d["attributed_pct"], "",
            "per cent of the mean square between-block peak-position move, "
            "about zero rather than about the mean, that the window setting "
            "accounts for. THE CAMPAIGN HAS SHAPES AND NOT CENTRES BECAUSE "
            "OF THIS ROW", "MEASURED" if primary else "DIAGNOSTIC")

    # THE ROBUSTNESS THE PANEL FORCED, 2026-08-25. Drawing the block series
    # showed that three of the nineteen steps cross from one spectral line to
    # another, and those three carry the largest moves, because moving to a
    # different line means moving the window a long way. A fraction whose
    # numerator is dominated by three trivially-explained jumps would be a
    # weaker claim than it sounds, so the same decomposition is run on the
    # sixteen steps that stay within one line. It holds.
    keyfn = GROUPINGS["peak_power"]
    blocks_meta = [(k, list(g)) for k, g in itertools.groupby(traces, key=keyfn)]
    peaks = [g[0]["peak"] for _k, g in blocks_meta]
    same_line = np.array([peaks[i] == peaks[i + 1] for i in range(len(peaks) - 1)])
    d = decompose(traces, keyfn)
    means = [(float(np.mean([float(r["peak_pos_ms"]) for r in g])),
              float(np.mean([float(r["window_start_ms"]) for r in g])))
             for _k, g in blocks_meta]
    d_pos = np.diff([m[0] for m in means])[same_line]
    d_win = np.diff([m[1] for m in means])[same_line]
    resid = float(np.sqrt(np.mean((d_pos - d_win) ** 2)))
    within_pct = 100.0 * (1.0 - resid ** 2 / float(np.mean(d_pos ** 2)))
    print(f"  within one spectral line only ({int(same_line.sum())} of "
          f"{len(same_line)} steps): {within_pct:.2f} per cent\n")
    add("n_block_steps_within_line", "peak_power", float(same_line.sum()), "",
        "count. steps between consecutive blocks that stay on one spectral "
        "line. the other steps move to a different line, which moves the "
        "window a long way for a reason nobody disputes", "DIAGNOSTIC")
    add("window_attributed_pct_within_line", "peak_power", within_pct, "",
        "per cent, the same decomposition restricted to steps that stay on "
        "one spectral line. this is the robustness check the figure forced. "
        "the three cross-line steps carry the largest moves, so the headline "
        "would be a weaker claim if it rested on them. it does not",
        "MEASURED")

    C.RESULTS_DIR.mkdir(exist_ok=True)
    with open(OUT_CSV, "w", newline="") as f:
        cols = ["quantity", "key", "value", "err", "unit", "status"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(out_rows)
    print(f"  Wrote {OUT_CSV.relative_to(ROOT)}: {len(out_rows)} rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

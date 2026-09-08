"""How the noise floor scales with density, from two committed CSVs.

The plan hub argues that radiation trapping does not set the floor: across
70, 90 and 110 C at fixed power the floor rises with density about as its
square root (shot noise on a background proportional to the atom number),
and the floor divided by the square root of the line height is flat. Those
two exponents were fitted by hand on 2026-09-07 and stated without a
producer. A replay reproduced them from `results/noise_model.csv` (the
`t_sweep` rows' signal-independent term a_V) and `results/qc_metrics.csv`
(the rf-off traces' height_v) against `rb5s6s.density.number_density_cm3`,
and found the pooled exponent hiding a per-peak spread from 0.17 to 0.66
ordered by line height. This file makes that replay the record's own:
pooled and per-peak log-log slopes with their standard errors, into
`results/noise_floor_scaling.csv`. Rung 2, mathematics on committed cells;
no simulation.
"""
import csv
import os
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rb5s6s import config as C  # noqa: E402
from rb5s6s.density import number_density_cm3  # noqa: E402
from rb5s6s.pmfmt import pm_cells  # noqa: E402

OUT = C.RESULTS_DIR / "noise_floor_scaling.csv"


def _refuse_unless_isolated() -> None:
    import rb5s6s
    pkg = os.path.realpath(os.path.dirname(rb5s6s.__file__))
    here = os.path.realpath(str(ROOT))
    if not pkg.startswith(here):
        raise SystemExit(f"run_noise_floor_scaling: the package resolves to {pkg}, outside {here}")


def _slope(x, y):
    """Least-squares slope of y on x with its standard error; needs three points."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    coef, cov = np.polyfit(x, y, 1, cov=True) if x.size > 2 else (np.polyfit(x, y, 1), np.full((2, 2), np.nan))
    return float(coef[0]), float(np.sqrt(cov[0, 0]))


def main() -> int:
    _refuse_unless_isolated()
    floor = defaultdict(dict)                      # peak -> T -> a_V
    with open(C.RESULTS_DIR / "noise_model.csv", newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["role"] == "t_sweep" and r["a_V"]:
                floor[r["peak"]][float(r["temperature_C"])] = float(r["a_V"])
    height = defaultdict(lambda: defaultdict(list))   # peak -> T -> heights
    with open(C.RESULTS_DIR / "qc_metrics.csv", newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r.get("rf_on") in ("False", "0", "") and r.get("height_v") and r.get("peak") in floor:
                T = float(r["temperature_C"])
                if T in floor[r["peak"]]:
                    height[r["peak"]][T].append(float(r["height_v"]))
    rows, per_floor, per_ratio = [], [], []
    px, py_floor, py_ratio = [], [], []
    for peak in sorted(floor):
        Ts = sorted(T for T in floor[peak] if height[peak][T])
        if len(Ts) < 3:
            continue
        ln = [np.log(number_density_cm3(T)) for T in Ts]
        lf = [np.log(floor[peak][T]) for T in Ts]
        lh = [np.log(np.mean(height[peak][T])) for T in Ts]
        s_f, e_f = _slope(ln, lf); s_r, e_r = _slope(ln, np.asarray(lf) - 0.5 * np.asarray(lh))
        per_floor.append(s_f); per_ratio.append(s_r)
        px += ln; py_floor += lf; py_ratio += list(np.asarray(lf) - 0.5 * np.asarray(lh))
        rows.append((f"peak_{peak}", "floor_exponent", s_f, e_f, ",".join(f"{T:g}" for T in Ts), "log-log slope of the signal-independent noise term against density"))
        rows.append((f"peak_{peak}", "floor_over_sqrt_height_exponent", s_r, e_r, ",".join(f"{T:g}" for T in Ts), "the same for the floor divided by the square root of the line height"))
    # the pooled fit shares one exponent with a per-peak offset: centre each peak on its own mean
    def pooled(ys):
        xs, yc = [], []
        k = 0
        for peak in sorted(floor):
            Ts = sorted(T for T in floor[peak] if height[peak][T])
            if len(Ts) < 3:
                continue
            n = len(Ts); seg_x = np.asarray(px[k:k + n]); seg_y = np.asarray(ys[k:k + n]); k += n
            xs += list(seg_x - seg_x.mean()); yc += list(seg_y - seg_y.mean())
        return _slope(xs, yc)
    s_f, e_f = pooled(py_floor); s_r, e_r = pooled(py_ratio)
    rows.append(("pooled", "floor_exponent", s_f, e_f, "all", f"one exponent shared across the peaks, each centred on its own mean. The per-peak values run {min(per_floor):.2f} to {max(per_floor):.2f}"))
    rows.append(("pooled", "floor_over_sqrt_height_exponent", s_r, e_r, "all", f"one exponent shared across the peaks. The per-peak values run {min(per_ratio):.2f} to {max(per_ratio):.2f}. Flat means trapping does not set the floor"))
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["scope", "quantity", "value", "err", "temperatures_C", "note", "status"])
        for scope, q, v, e, Ts, note in rows:
            w.writerow([scope, q, *pm_cells(v, e), Ts, note, "DIAGNOSTIC"])
    print(f"wrote {OUT} with {len(rows)} rows; pooled floor exponent {s_f:.3f} +- {e_f:.3f}, ratio {s_r:.3f} +- {e_r:.3f}, per-peak floor {[round(v, 3) for v in per_floor]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

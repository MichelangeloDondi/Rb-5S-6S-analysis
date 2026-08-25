#!/usr/bin/env python3
"""
What the drifting lock's freedom costs the centre channel (module M29)
=====================================================================

THE QUESTION, and it is the experimenter's. Asked on 2026-08-25 to invert
the centre channel from an estimate into a test -- assume the light shift
is known, and ask what the data says about it -- the answer came back
uninformative, and the DIAGNOSIS was the finding: the limit is not the
noise, it is that one power change inside a freely fitted drift is nearly
degenerate with that drift's slope. This module measures that cost instead
of asserting it.

WHY IT EXISTS. The diagnosis was recorded in a preregistration and its
headline, a factor of 48, was published in `docs/plan/07` as the evidence
for a campaign design change. Rebuilding it as a producer on 2026-08-25
did not reproduce that factor, for two reasons that are worth more than
the number:

1. THE BASELINE IT DIVIDED BY IS NOT EVALUABLE ON THIS ARCHIVE. A centre
   here is `offset_mhz`, which is defined as a departure from the mean over
   its own (display epoch, peak) group. The per-epoch constant is therefore
   ALREADY REMOVED BY THE DATA'S CONSTRUCTION, and a row computed with no
   per-epoch freedom is a forecast for a lock that does not drift, not a
   measurement on these traces. It is reported below and labelled as one.
2. THE STEP IT QUOTED SPANS A POWER CHANGE NO EPOCH CONTAINS. The three
   multi-power epochs run 75 to 125 mW and 175 to 225 mW, so the largest
   change available inside one epoch is 50 mW, not the 100 mW whose
   predicted pull was quoted.

Neither disturbs the CONCLUSION, which is why the correction is a
correction and not a retraction: the drift's freedom still dominates the
noise by a large factor, and the campaign fix is still to cycle the power
several times inside one display epoch, because a line cannot follow a
zig-zag. What changes is that the factor is now measured, on a stated
trace set, against a stated baseline.

THE CONSTRUCTION, fixed here so the rows are comparable to each other.
Every row uses the SAME traces and the SAME noise model, and only the
drift's freedom changes between them, because a comparison in which two
things move measures neither. The observation model is

    offset_i = A * pull(P_i) + (drift basis for trace i's epoch)

with `pull(P) = (2/3) * S0(1 W) * P / 2`, the centroid pull on the laser
axis: two thirds because the centroid of the ramp-averaged profile moves
by that fraction of the peak shift, and a half because the laser axis is
half the transition axis. A is the amplitude on the PREDICTED shift, so
A = 1 is the prediction holding and A = 0 is no shift at all. The noise is
one MAD-sigma per epoch, taken from the residuals after a line is removed,
which is the most permissive drift class and therefore cannot inflate the
scatter with unmodelled drift. sigma_A is read off the Fisher information,
which for a linear model with known noise is exact rather than asymptotic.

NO FIT RUNS HERE beyond the per-epoch de-trending that sets the noise
scale: the design is linear, so the information is arithmetic on committed
cells of `results/laser_history.csv`. Nothing this module writes moves a
committed bound; the centre channel remains closed on this archive, and
what these rows govern is a CAMPAIGN DESIGN decision.

Writes `results/centre_fisher.csv`.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rb5s6s import config as C  # noqa: E402
from rb5s6s.constants import RHO_RETRO, W0_MEASURED_M  # noqa: E402
from rb5s6s.lineshape import stark_shift_S0_mhz  # noqa: E402

LASER_HISTORY_CSV = C.RESULTS_DIR / "laser_history.csv"
OUT_CSV = C.RESULTS_DIR / "centre_fisher.csv"

# Two thirds of the peak shift is the ramp-averaged centroid pull, and the
# laser axis is half the transition axis. Both factors are the record's, not
# this module's, and they are the same two the fig15 panel applies.
CENTROID_FRACTION = 2.0 / 3.0
LASER_AXIS_FACTOR = 0.5

# The drift classes, in order of increasing freedom. `None` is the
# counterfactual: no per-epoch freedom at all, which THIS ARCHIVE CANNOT
# REALISE because its centres are already epoch-referenced.
DRIFT_CLASSES = [
    (None, "drift_known", "ENVELOPE"),
    (0, "constant_per_epoch", "MEASURED"),
    (1, "linear_per_epoch", "MEASURED"),
    (2, "quadratic_per_epoch", "MEASURED"),
]


def pull_mhz_per_w() -> float:
    """The predicted centre pull per watt, laser axis."""
    return (CENTROID_FRACTION * LASER_AXIS_FACTOR
            * stark_shift_S0_mhz(1.0, W0_MEASURED_M, rho=RHO_RETRO))


def _mad_sigma(x: np.ndarray) -> float:
    return float(1.4826 * np.median(np.abs(x - np.median(x))))


def _load_epochs() -> dict[str, list[dict]]:
    """The display epochs that contrast more than one power, in time order."""
    if not LASER_HISTORY_CSV.exists():
        return {}
    rows = [r for r in csv.DictReader(open(LASER_HISTORY_CSV))
            if r["role"] == "p_sweep" and r["offset_mhz"] and r["power_mW"]]
    by: dict[str, list[dict]] = {}
    for r in rows:
        by.setdefault(r["display_epoch"], []).append(r)
    return {k: sorted(v, key=lambda r: float(r["t_epoch"]))
            for k, v in sorted(by.items(), key=lambda kv: int(kv[0]))
            if len({r["power_mW"] for r in v}) > 1 and len(v) >= 3}


def _epoch_arrays(traces: list[dict]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    y = np.array([float(r["offset_mhz"]) for r in traces])
    t = np.array([float(r["t_epoch"]) for r in traces])
    t = (t - t.mean()) / 60.0                      # minutes about the epoch mean
    p = np.array([float(r["power_mW"]) for r in traces]) / 1000.0   # watts
    return y, t, p


def noise_per_epoch(epochs: dict[str, list[dict]]) -> dict[str, float]:
    """One sigma per epoch, from residuals after removing a line in time.

    Taken under the most permissive drift class ON PURPOSE: a noise scale
    estimated under a stiffer class would absorb real drift and inflate,
    which would make the drift look cheap by making the noise look dear.
    """
    sigma = {}
    for key, traces in epochs.items():
        y, t, _ = _epoch_arrays(traces)
        basis = np.vstack([np.ones_like(t), t]).T
        resid = y - basis @ np.linalg.lstsq(basis, y, rcond=None)[0]
        sigma[key] = _mad_sigma(resid)
    return sigma


def sigma_amplitude(epochs: dict[str, list[dict]], sigma: dict[str, float],
                    order: int | None) -> float:
    """Fisher error on the amplitude A, at a given per-epoch drift freedom."""
    keys = list(epochs)
    per = 1 if order is None else order + 1
    ncol = 1 + (1 if order is None else per * len(keys))
    design, weight = [], []
    for i, key in enumerate(keys):
        _, t, p = _epoch_arrays(epochs[key])
        for j in range(len(t)):
            row = np.zeros(ncol)
            row[0] = pull_mhz_per_w() * p[j]
            if order is None:
                row[1] = 1.0                       # one shared level, no epoch freedom
            else:
                for d in range(per):
                    row[1 + i * per + d] = t[j] ** d
            design.append(row)
            weight.append(1.0 / sigma[key] ** 2)
    fisher = np.array(design).T @ np.diag(weight) @ np.array(design)
    return float(np.sqrt(np.linalg.pinv(fisher)[0, 0]))


def main() -> int:
    epochs = _load_epochs()
    if not epochs:
        print(f"  {LASER_HISTORY_CSV.name} absent or holds no multi-power "
              f"epoch -- skipped")
        return 0

    sigma = noise_per_epoch(epochs)
    n_traces = sum(len(v) for v in epochs.values())
    pull = pull_mhz_per_w()

    print("=" * 74)
    print("(M29) WHAT THE DRIFT'S FREEDOM COSTS THE CENTRE CHANNEL")
    print(f"  {len(epochs)} display epochs contrast more than one power, "
          f"{n_traces} traces\n")

    out_rows: list[dict] = []

    def add(quantity, key, value, err, unit, status):
        out_rows.append({
            "quantity": quantity, "key": key,
            "value": f"{value:.4f}" if isinstance(value, float) else value,
            "err": f"{err:.4f}" if isinstance(err, float) else err,
            "unit": unit, "status": status})

    add("n_multi_power_epochs", "p_sweep", float(len(epochs)), "",
        "count. display epochs holding at least two nominal powers and at "
        "least three traces", "DIAGNOSTIC")
    add("n_traces", "p_sweep", float(n_traces), "",
        "count. traces inside those epochs, all of which enter every row "
        "below", "DIAGNOSTIC")
    add("pull_per_watt_mhz", "predicted", pull, "",
        "MHz per W on the laser axis. the predicted centre pull, two thirds "
        "of the peak shift for the ramp-averaged centroid and one half for "
        "the axis convention", "DIAGNOSTIC")

    # The largest power change available INSIDE one epoch, which is the
    # lever this channel actually has. Quoting a change that spans two
    # epochs would put a number on a measurement nobody can make.
    steps = []
    for key, traces in epochs.items():
        _, _, p = _epoch_arrays(traces)
        steps.append((float(p.max() - p.min()), key))
    d_p, where = max(steps)
    print(f"  largest power change inside one epoch: {1000 * d_p:.0f} mW "
          f"(epoch {where}), predicted pull {1000 * pull * d_p:.0f} kHz")
    add("delta_power_max_in_epoch_w", where, d_p, "",
        "W. the largest power change available INSIDE a single display "
        "epoch. a change spanning two epochs is not a lever, because the "
        "centres either side of an epoch boundary are not comparable. "
        "single_valued: this is the lever the design happens to offer, "
        "not a summary over a population. three epochs contrast two "
        "powers each and every one of them steps by 50 mW, so the "
        "spread a sibling median would report is zero",
        "DIAGNOSTIC")
    add("predicted_step_mhz", where, pull * d_p, "",
        "MHz on the laser axis. what the prediction says the centre moves "
        "across that power change", "DIAGNOSTIC")

    for key in epochs:
        add("sigma_per_trace_mhz", f"epoch_{key}", sigma[key], "",
            "MHz. MAD-sigma of the within-epoch centres after a line in "
            "time is removed", "DIAGNOSTIC")
        print(f"  epoch {key}: sigma per trace = {sigma[key]:.4f} MHz "
              f"over {len(epochs[key])} traces")

    print()
    values = {}
    for order, name, status in DRIFT_CLASSES:
        values[name] = sigma_amplitude(epochs, sigma, order)
        print(f"  {name:22s} sigma_A = {values[name]:.3f}   ({status})")
        add("sigma_amplitude", name, values[name], "",
            "dimensionless. one-sigma error on the amplitude multiplying "
            "the PREDICTED shift, so 1 is the prediction holding and 0 is "
            "no shift. the drift-known row is a FORECAST for a fixed lock "
            "and not a measurement on this archive, whose centres already "
            "have their per-epoch mean removed by construction",
            status)

    # THE TWO RATIOS, both named, because the published one divided by the
    # forecast without saying so. The measured cost is the second.
    infl_forecast = values["linear_per_epoch"] / values["drift_known"]
    infl_measured = values["linear_per_epoch"] / values["constant_per_epoch"]
    print(f"\n  inflation, linear over the fixed-lock forecast: "
          f"{infl_forecast:.1f}x")
    print(f"  inflation, linear over constant per epoch:       "
          f"{infl_measured:.1f}x  <- the cost this archive can measure")
    add("inflation_linear_over_drift_known", "forecast", infl_forecast, "",
        "dimensionless. how much a freely fitted linear drift costs "
        "relative to a lock whose drift is known. the denominator is a "
        "FORECAST, so this ratio speaks to a future campaign and not this one",
        "ENVELOPE")
    add("inflation_linear_over_constant", "measured", infl_measured, "",
        "dimensionless. how much a freely fitted linear drift costs "
        "relative to a per-epoch level alone, which is the comparison BOTH "
        "of whose terms this archive can evaluate. THIS IS THE COST THE "
        "CAMPAIGN DESIGN TURNS ON", "MEASURED")

    # THE LADDER-ORDER FORECAST, which is the row the design chapter rests
    # on. Everything above measures the archive as taken. This asks what the
    # SAME traces, at the SAME times and the SAME noise, would have given
    # under a different power ORDER, which is the one thing the 2025 session
    # could have changed for free.
    #
    # WHY THE ARCHIVE'S ORDER IS THE WORST CASE, and it is sharper than
    # "power and time were collinear". Each epoch took all repeats of one
    # power back to back, so its traces sit in TWO TIGHT TIME CLUSTERS with
    # one power in each. A straight line through two clusters is fixed by
    # the difference of their means, and so is a one-time power step: the
    # two are then the same vector to within the scatter inside a cluster.
    # Spreading the powers through the epoch separates them, and the
    # separation costs nothing but the order the operator writes down.
    orders = {
        "as_taken": None,
        "cycled": None,
    }
    for name in orders:
        design_epochs = {}
        for key, traces in epochs.items():
            _, t, p = _epoch_arrays(traces)
            if name == "cycled":
                # the same multiset of powers, alternated in time
                lo, hi = float(p.min()), float(p.max())
                p = np.array([hi if j % 2 == 0 else lo for j in range(len(p))])
            design_epochs[key] = [
                {"offset_mhz": "0.0", "t_epoch": str(60.0 * t[j]),
                 "power_mW": str(1000.0 * p[j]), "display_epoch": key}
                for j in range(len(t))]
        orders[name] = sigma_amplitude(design_epochs, sigma, 1)
        add("sigma_amplitude_forecast", f"linear_drift_{name}", orders[name], "",
            "dimensionless. what a free per-epoch linear drift would leave "
            "on the amplitude if the campaign's own traces and times carried "
            "this power ORDER. a FORECAST over an ordering, not a "
            "measurement of one", "ENVELOPE")
    gain = orders["as_taken"] / orders["cycled"]
    print(f"\n  ladder order, same traces and times: as taken "
          f"{orders['as_taken']:.2f}, cycled {orders['cycled']:.2f} "
          f"-> {gain:.1f}x better")
    add("ladder_order_gain", "cycled_over_as_taken", gain, "",
        "dimensionless. how much the light-shift error improves from "
        "CYCLING THE POWER through the epoch instead of taking every repeat "
        "of one power before changing. same traces, same times, same noise, "
        "only the order. THIS IS WHAT THE CAMPAIGN DESIGN CHANGE BUYS, AND "
        "IT COSTS NOTHING", "ENVELOPE")

    # WHAT THE ARCHIVE ACTUALLY TESTS, stated as a significance because that
    # is the form the design chapter quotes and the form a reader checks.
    # A = 1 is the prediction, so testing it at 1/sigma_A sigma is the whole
    # claim. The chapter said "three sigma per epoch"; the number below is
    # the aggregate over all three epochs and is smaller, which is why the
    # sentence there now cites this row.
    for name in ("constant_per_epoch", "drift_known"):
        sig_n = 1.0 / values[name]
        add("prediction_significance_sigma", name, sig_n, "",
            "sigma. how many sigma separate the predicted shift from no "
            "shift at all, aggregated over every multi-power epoch, at the "
            "stated drift freedom. the drift-known row is the fixed-lock "
            "FORECAST", "MEASURED" if name == "constant_per_epoch"
            else "ENVELOPE")
        print(f"  prediction tested at {sig_n:.1f} sigma under {name}")

    C.RESULTS_DIR.mkdir(exist_ok=True)
    with open(OUT_CSV, "w", newline="") as f:
        cols = ["quantity", "key", "value", "err", "unit", "status"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(out_rows)
    print(f"\n  Wrote {OUT_CSV.relative_to(ROOT)}: {len(out_rows)} rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

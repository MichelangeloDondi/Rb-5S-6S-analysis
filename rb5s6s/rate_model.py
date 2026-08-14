"""Time-resolved sweep-rate model — replacing bracket averages with rate(t).

WHY THIS MODULE EXISTS (2026-08-01). The ms-to-MHz transfer function was a
per-block constant: each science block took the mean of its before/after EOM
ruler brackets, and a genuine in-session rate shift was carried as inflated
uncertainty rather than modelled (`run_beta_self.load_t_rates`, audit fix of
2026-07-11). Three findings retired that scheme:

1. THE DRIFT IS REAL AND RESOLVED. All ruler traces have recovered
   timestamps (`data_recovered/CLOCK.csv`; earliest copy per basename, since
   later backup copies only inflate mtime). Per peak, the P-session rate
   drifts linearly at up to 1.9%/h with 2.8-5.6 sigma significance on three
   of the four peaks. The before/after brackets were undersampling a drift,
   not measuring a constant: 4207's brackets disagree by 1.43% (5.5 sigma).

2. WHAT REMAINS AFTER MODELLING IS NOISE. Decomposing the per-trace rate
   variance: raw scatter 0.852%; per-peak (the sweep nonlinearity - each
   hyperfine line sits at a different point of the triangle) leaves 0.782%;
   adding per-session leaves 0.677%; adding linear-in-time leaves 0.596% -
   BELOW the median per-trace statistical error of 0.636%. A model that
   drives the residual under the statistical floor has captured all the
   structure there is.

3. THE ERRORS FALL WHERE THEY WERE CO-DOMINANT. Interpolating rate(t) to
   each science trace's timestamp, against the committed bracket scheme:
   P-session per-peak errors 0.37/0.09/0.22/0.62% -> 0.20/0.07/0.12/0.21%.
   In the T session the sweep rate cannot know the cell temperature, so one
   pooled per-peak rate(t) lets the bright 90/110 C blocks calibrate the dim
   70 C ones, and that is where the gain is largest: the four 70 C blocks go
   1.49/1.48/0.32/1.19% -> 0.29/0.24/0.20/0.19%, a five- to sixfold cut
   exactly where `load_t_rates`' own budget note called the ruler error
   co-dominant with the laser-width drift. One block moves the other way
   (4154 110 C, 0.20 -> 0.32%): the pooled scatter there exceeds that
   block's own formal error, so the wider number is the one that stands.

THE MODEL. Per (session, peak): rate(t) = a + b (t - t0)/3600, ordinary
least squares over that peak's ruler traces, with SCATTER-BASED covariance
(the residual variance, not the per-trace formal errors - the scatter is the
honest dispersion and it already carries any per-block over-dispersion, e.g.
4121's per-T means straddle its fit by up to 0.9%). Rates are LASER-axis
MHz/ms, like `ruler_blocks.csv`; consumers double for the transition axis.

FALLBACK. Nine T-session rulers (the dim 70 C blocks of 4154/4192 among
them) and four 4154 70 C science traces have no recovered clock. A block
whose science-side time is unknown falls back to the committed per-block
scheme unchanged; a model is only fitted where at least four clocked rulers
span more than MIN_SPAN_H. The fallback path is exercised by the 4154 T-block
in production, not only in tests.

WHAT THIS DOES NOT DO. It does not touch the centre channel. The centres
stay dead for the reasons in `run_stark_centres.py` (the knob frame is not
licensed and the power schedule is collinear with drift); this module
improves the WIDTH channel, where the rate enters every width
multiplicatively and block-coherently.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import numpy as np

from . import config as C

MODEL_CSV = "ruler_rate_model.csv"
MIN_TRACES = 4          # fewer clocked rulers than this: no model, fallback
MIN_SPAN_H = 0.4        # less time leverage than this: no slope worth fitting
# 0.4 h, not more: each P-session ladder spans only 0.49-0.76 h between its
# rulers, and the 4207 slope is 5.6 sigma inside 0.65 h. The gate exists to
# reject slope fits with no time leverage, not to reject the P session.


def load_clock(root: Path | None = None) -> dict[str, float]:
    """Basename -> acquisition-epoch map from the recovered backup.

    The backup holds several copies of many files; a copy can only be LATER
    than the acquisition, so the earliest mtime per basename is the best
    available acquisition time (worst observed multi-copy spread: 725 h).

    Names are ALSO matched through the manifest md5 (2026-08-01). The backup
    saved some traces under variant names: the 4154 and 4192 70 C blocks
    appear as `4154_070c1.csv` where the manifest calls them
    `4154nm_070c1.csv`. Matching on filename alone lost sixteen clocks and
    sent the dim 70 C blocks - exactly the ones the model helps most - down
    the fallback path. All sixteen are md5-identical to canonical traces, so
    the content check is decisive rather than a guess at a naming rule."""
    # An explicit root is the caller's business. The DEFAULT root is this
    # file's own two-directories-up guess, which is right in a checkout and
    # points inside site-packages from a wheel, so that case is the one that
    # needs the cause named rather than a bare FileNotFoundError.
    if root is None:
        C.require_repo_data("data_raw")
    root = root or C.REPO_ROOT
    clock: dict[str, float] = {}
    by_md5: dict[str, float] = {}
    with open(root / "data_recovered" / "CLOCK.csv") as fh:
        for r in csv.DictReader(fh):
            n = Path(r["path"]).name.lower()
            t = float(r["mtime_epoch"])
            clock[n] = min(clock.get(n, t), t)
            md5 = r.get("md5")
            if md5:
                by_md5[md5] = min(by_md5.get(md5, t), t)
    manifest = root / "data_raw" / "MANIFEST.csv"
    if manifest.exists():
        with open(manifest) as fh:
            for r in csv.DictReader(fh):
                n = Path(r["file"]).name.lower()
                t = by_md5.get(r.get("md5", ""))
                if t is not None:
                    clock[n] = min(clock.get(n, t), t)
    return clock


def fit_rate_models(trace_rows: list[dict], clock: dict[str, float]) -> list[dict]:
    """Per-(session, peak) linear rate(t) fits over the ruler traces.

    Returns one row per fitted model: a (laser MHz/ms at t0), b (per hour),
    t0 (epoch), the three scatter-based covariance terms, the residual
    scatter, and the trace count. Groups failing MIN_TRACES/MIN_SPAN_H are
    simply absent - consumers fall back to the per-block scheme."""
    groups: dict[tuple[str, str], list[tuple[float, float]]] = defaultdict(list)
    for r in trace_rows:
        n = Path(r["file"]).name.lower()
        if n in clock:
            groups[(r["session"], r["peak"])].append(
                (clock[n], float(r["rate_MHzms"])))
    out = []
    for (session, peak), d in sorted(groups.items()):
        if len(d) < MIN_TRACES:
            continue
        t = np.array([x[0] for x in d])
        rate = np.array([x[1] for x in d])
        if (t.max() - t.min()) / 3600.0 < MIN_SPAN_H:
            continue
        t0 = float(t.mean())
        th = (t - t0) / 3600.0
        A = np.vstack([np.ones_like(th), th]).T
        ab, *_ = np.linalg.lstsq(A, rate, rcond=None)
        resid = rate - A @ ab
        s2 = float(np.sum(resid * resid)) / max(len(d) - 2, 1)
        cov = s2 * np.linalg.inv(A.T @ A)
        out.append({
            "session": session, "peak": peak,
            "a_rate_laser": float(ab[0]), "b_per_hour": float(ab[1]),
            "t0_epoch": t0,
            "var_a": float(cov[0, 0]), "cov_ab": float(cov[0, 1]),
            "var_b": float(cov[1, 1]),
            "scatter_pct": 100.0 * float(np.sqrt(s2)) / float(ab[0]),
            "n_traces": len(d),
            "t_min_epoch": float(t.min()), "t_max_epoch": float(t.max()),
        })
    return out


def write_models(rows: list[dict], root: Path | None = None) -> Path:
    root = root or C.REPO_ROOT
    path = root / "results" / MODEL_CSV
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return path


def read_models(root: Path | None = None) -> dict[tuple[str, str], dict]:
    root = root or C.REPO_ROOT
    path = root / "results" / MODEL_CSV
    if not path.exists():
        return {}
    models = {}
    with open(path) as fh:
        for r in csv.DictReader(fh):
            # tolerate annotation columns (annotate_results_status adds a
            # string `status`): convert what parses, keep the rest verbatim
            row = {}
            for k, v in r.items():
                try:
                    row[k] = float(v)
                except (TypeError, ValueError):
                    row[k] = v
            models[(r["session"], r["peak"])] = row
    return models


def rate_at(model: dict, epoch: float) -> tuple[float, float]:
    """(laser-axis rate, relative error) of one model at one time.

    Evaluation outside the ruler span is extrapolation and the linear form
    is only vouched for inside it; the variance grows quadratically outside,
    which is the model saying so, but callers should prefer the fallback if
    they are far out."""
    th = (epoch - model["t0_epoch"]) / 3600.0
    r = model["a_rate_laser"] + model["b_per_hour"] * th
    var = model["var_a"] + 2.0 * th * model["cov_ab"] + th * th * model["var_b"]
    return float(r), float(np.sqrt(var) / r)


def science_times(role_dir: str, root: Path | None = None) -> dict[str, float]:
    """Basename -> epoch for the canonical science traces of one role."""
    root = root or C.REPO_ROOT
    clock = load_clock(root)
    out = {}
    for f in sorted((root / "data_raw" / role_dir).glob("*.csv")):
        n = f.name.lower()
        if n in clock:
            out[f.name] = clock[n]
    return out

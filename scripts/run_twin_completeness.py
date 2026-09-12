#!/usr/bin/env python3
"""Does the twin reproduce the archive's residual structure? The one test of it.

WHY AN INFORMATION CRITERION CANNOT ANSWER THIS, and this file exists because
it cannot. AIC and BIC compare two models over one dataset with different
parameter counts. The twin generates seven terms `fullmodel.UNFITTABLE` names
that no fit can free, so for those there is no "model with" and "model without"
to compare and the difference in AIC is not small, it is UNDEFINED. A census
over the fittable terms grades the FITTER's term list and is structurally
silent about the world the twin builds. Worse, the layer-isolation study found
every twin layer moving the fitted waist by under 0.05 per cent on its own, and
a term that does not move the likelihood scores no preference either way: an
information criterion would wave all seven through whether the twin had them
right or wrong.

WHAT DOES ANSWER IT is the comparison the repository's own charter names, and
which nothing implemented until now: fit the same model to real traces and to
twin traces at matched conditions, and compare what the fits LEAVE BEHIND. A
term the twin is missing cannot hide in a residual, whether or not a fit can
free it.

THE STATISTICS ARE CHOSEN TO NEED NO FREQUENCY AXIS, so a ruler calibration
cannot enter and no fit has to converge for the comparison to mean something.
They are read off the flat wings, where the line is absent by construction:

  sigma          the noise scale, which the amplitude law sets;
  rho1           the first lag, which a digitiser's filter would set;
  tau_int        the INTEGRATED correlation time, which is what the variance
                 of every statistic the twin reports actually depends on;
  excess kurtosis  whether the noise is Gaussian, which shot noise at these
                 levels should be and a drifting baseline would not be.

READ THE GAP, NOT THE COLUMN. A twin that matches the archive on all four has
no residual evidence against it; one that misses on any is missing a term, and
the statistic that misses says which kind. This is evidence of ABSENCE at the
resolution of these four numbers, never a proof of completeness, and the row
`n_real_traces` is what sets that resolution.

READS RAW TRACES, so a clone without `data_raw/` cannot run it and the
committed file is what such a clone reads.

STATUS. The archive columns are MEASURED, from real traces. The twin columns
and the gaps are DIAGNOSTIC: they are readings of a simulation against them.
"""
import csv
import math
import os
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from rb5s6s import config as _CFG                                  # noqa: E402
from rb5s6s.forecast import build_world_trace                      # noqa: E402
from rb5s6s.ingest import load_trace                               # noqa: E402
from rb5s6s.noise import load_noise_model                          # noqa: E402
from rb5s6s.pmfmt import in_plain_band, pm_cells                   # noqa: E402

_CFG_RESULTS = _CFG.RESULTS_DIR
ROLE = "p_sweep"
N_TRACES = 40                 # canonical traces sampled, deterministic order
WING = 400                    # leading samples
LAGS = 20
#: The twin's span must put its wing OFF the line or the statistic reads the
#: line's shoulder. At +-25 MHz the first 400 of 2501 points sit at -25 to -17
#: MHz, three linewidths out, and a linear detrend does not flatten a curved
#: shoulder: the correlation time there reads 10.4 whatever the noise is set
#: to, identically with quantisation on and off. At +-200 MHz it reads 1.34
#: white and 3.14 at the law's time, which is the noise and not the line.
TWIN_SPAN = (-200.0, 200.0)
#: The per-trace baseline tilt is MEASURED on the real wings and never solved
#: for. An earlier cut fitted its amplitude so the twin's correlation time
#: matched the archive's, then reported that they matched: an interpolation
#: residual presented as a test. Worse, the amplitude that fit was about seven
#: times the directly measured one, which is the evidence that a tilt alone does
#: not account for the archive's correlation. Measuring the term and reporting
#: what is still missing is what this reports, and it leaves every statistic
#: here held out.


def _cells(m: float, e: float) -> tuple[str, str, str]:
    """Value and error cells, with the uncertainty moved into the note when the
    pair falls outside the plain-decimal band.

    A noise scale of 4e-4 with an error of 2e-6 cannot be written as two plain
    cells at two significant digits: the factored form is owed and two separate
    columns cannot carry it. The uncertainty then goes to the note rather than
    being dropped, which is what the other producers in this tree do.
    """
    if in_plain_band(m, e):
        v, er = pm_cells(m, e)
        return v, er, ""
    return f"{m:.4g}", "", f" Its standard error is {e:.2g}, outside the plain-decimal band."


def _wing_stats(v: np.ndarray, detrend: bool = True) -> dict:
    """The four numbers, off a wing.

    `detrend` removes a LINEAR baseline, and the difference between the two
    settings is what this measures. A slow tilt across the wing inflates a
    correlation time and a straight line removes it, while a broadband
    correlation survives both. The archive reads 1.88 tilted and 0.96
    detrended, so what it carries is mostly a tilt.

    THIS ESTIMATOR IS NOT THE COMMITTED LAW'S AND THE TWO NUMBERS DO NOT
    COMPARE. Over `WING` samples at `LAGS` lags it recovers 1.33 from a
    synthetic AR(1) whose true integrated time is 2.515, so it is biased low by
    construction on a short window. Every figure here is therefore read
    ARCHIVE-AGAINST-TWIN under one estimator, and never against
    `noise_model.csv`'s own `tau_int`, which a different instrument measured.
    """
    w = np.asarray(v[:WING], dtype=float)
    # a linear baseline, not a mean: a slow drift across the wing is not noise
    x = np.arange(w.size, dtype=float)
    d = (w - np.polyval(np.polyfit(x, w, 1), x)) if detrend else (w - w.mean())
    sd = float(d.std(ddof=1))
    if sd <= 0:
        return {}
    ac = [float(np.corrcoef(d[:-k], d[k:])[0, 1]) for k in range(1, LAGS + 1)]
    m2 = float(np.mean(d ** 2))
    return {"sigma": sd, "rho1": ac[0],
            "tau_int": 1.0 + 2.0 * float(np.sum(ac)),
            "excess_kurtosis": float(np.mean(d ** 4) / m2 ** 2 - 3.0)}


def _real_wings() -> tuple[list[dict], list[dict]]:
    rows = [r for r in csv.DictReader((_CFG.DATA_RAW_DIR / "MANIFEST.csv")
                                      .open(encoding="utf-8"))
            if r["role"] == ROLE and r["flag"] == "canonical"]
    rows.sort(key=lambda r: r["file"])            # deterministic, not sampled
    out, used = [], []
    for r in rows[:N_TRACES]:
        try:
            _t, v = load_trace(_CFG.DATA_RAW_DIR / r["file"])
        except Exception:
            continue
        s = _wing_stats(v)
        if s:
            out.append(s); used.append(r)
    return out, used


def _measured_tilt(used: list[dict]) -> float:
    """The real wings' own tilt, as a rise across the full grid in noise sigma.

    Each wing gives a least-squares slope and a residual sigma; the rise across
    the wing over that sigma is the dimensionless tilt there, and the wing is
    `WING` of the archive's own sample count, so scaling to the full grid is
    one ratio. Nothing here is fitted to a correlation time.
    """
    vals = []
    for v in _reload(used):
        w = np.asarray(v[:WING], dtype=float)
        x = np.arange(w.size, dtype=float)
        c = np.polyfit(x, w, 1)
        d = w - np.polyval(c, x)
        sd = float(d.std(ddof=1))
        if sd > 0:
            rise = float(c[0]) * w.size
            vals.append(abs(rise) / sd * (v.size / w.size))
    return float(np.mean(vals)) if vals else 0.0


def _floor_for(r: dict) -> float:
    """The dark floor at THIS trace's own condition, never the pooled median.

    The law is fitted per (peak, temperature, power) and its `a` runs 0.00134 V
    at 25 mW to 0.00434 at 125, a factor of three across the arm. Using the
    pooled 0.00364 everywhere overshot the dim rungs by the same factor, which
    is the record's own rule about a statistic evaluated over a population it
    does not describe.
    """
    try:
        return float(load_noise_model(
            str(_CFG_RESULTS / "noise_model.csv"), role=ROLE, peak=r["peak"],
            temperature_C=float(r["temperature_C"]),
            power_mW=float(r["power_mW"]))["a"])
    except Exception:
        return 0.0


def _twin(used: list[dict], tau_int: float, tilt: float = 0.0,
          floor: bool = True) -> list[dict]:
    """One twin trace per real trace, at that trace's own power, peak and law."""
    law_s0 = 0.364
    out = []
    for i, r in enumerate(used):
        p_w = float(r["power_mW"] or 225.0) / 1000.0
        rng = np.random.default_rng(8_100_000 + i)
        _nu, v, _ = build_world_trace(
            power_w=p_w, kappa=law_s0 / 0.225, t_c=float(r["temperature_C"]),
            order_idx=i % 5, n_rungs=5, rng=rng,
            layers=dict(cascade=True, saturation=True, stark=True, bbr=True,
                        drift=True, quantise=True),
            positions={r["peak"]: 0.0}, shares={r["peak"]: 1.0},
            gamma_coll=0.55, sigma_laser_fwhm=1.6, transit_fwhm=0.9575,
            power_max_w=0.225, cycles_at_max=1.0, drift_mhz_total=0.05,
            noise_frac_bright=0.004, adc_levels=65536, gamma_l=0.40,
            resolve_shift=True, grid_span=TWIN_SPAN, tau_int=tau_int,
            baseline_tilt_sigma=tilt,
            noise_floor_v=(_floor_for(r) if floor else 0.0))
        s = _wing_stats(v, detrend=(tilt == 0.0))
        if s:
            out.append(s)
    return out


def _reload(used: list[dict]):
    for r in used:
        try:
            _t, v = load_trace(_CFG.DATA_RAW_DIR / r["file"])
        except Exception:
            continue
        yield v


def _agg(rows: list[dict], key: str) -> tuple[float, float]:
    a = np.array([r[key] for r in rows], float)
    return float(a.mean()), float(a.std(ddof=1) / math.sqrt(a.size))


def main() -> int:
    law = load_noise_model(str(_CFG_RESULTS / "noise_model.csv"),
                           role=ROLE, pool="median")
    arc, used = _real_wings()
    if len(arc) < 10:
        raise SystemExit("run_twin_completeness: fewer than ten archive traces "
                         "loaded, so no comparison is licensed")
    white = _twin(used, 1.0)
    corr = _twin(used, law["tau_int"])
    # THE TILT IS MEASURED FROM THE REAL WINGS, not fitted to a statistic.
    # Each wing's own least-squares slope, as a rise across the full grid in
    # units of that wing's residual sigma.
    tilt_hat = _measured_tilt(used)
    tilted = _twin(used, 1.0, tilt=tilt_hat)
    # the SAME wings without the linear removal: the gap between the two is
    # the tilt, and the tilt is the term this comparison actually finds
    tilt_rows = [s for s in (_wing_stats(v, detrend=False)
                            for v in _reload(used)) if s]

    out = [["quantity", "arm", "value", "err", "note", "status"]]
    out.append(["n_real_traces", "", str(len(arc)), "",
                f"canonical {ROLE} traces, first {N_TRACES} by filename, wings "
                f"of {WING} samples. This sets the resolution of every verdict "
                "below and is why none of them proves completeness",
                "MEASURED"])
    for key in ("sigma", "rho1", "tau_int", "excess_kurtosis"):
        a_m, a_e = _agg(arc, key)
        w_m, w_e = _agg(white, key)
        c_m, c_e = _agg(corr, key)
        av, ae, a_txt = _cells(a_m, a_e)
        out.append([f"measured_{key}", "", av, ae,
                    "measured on the real traces' wings." + a_txt, "MEASURED"])
        for label, (m, e) in (("twin_white", (w_m, w_e)),
                              ("twin_at_measured_tau", (c_m, c_e))):
            v, er, _txt = _cells(m, e)
            pull = (m - a_m) / math.hypot(e, a_e) if (e or a_e) else float("nan")
            out.append([f"{label}_{key}", "", v, er,
                        f"twin at tau_int={'1.0' if label.endswith('white') else law['tau_int']:.4}. "
                        f"Pull against the measured value {pull:+.1f} sigma.{_txt}",
                        "DIAGNOSTIC"])
    # THE TERM THIS COMPARISON ACTUALLY FINDS, and it is not the one the day
    # started by looking for. The archive's wing carries a slow TILT: under one
    # estimator it reads 1.88 with only the mean removed and 0.96 once a
    # straight line is taken out, while a broadband correlation survives both
    # removals. The twin has no per-trace baseline tilt, so this is a missing
    # term, and it is a different term from the AR(1) the noise law's own
    # `tau_int` would suggest.
    at_m, at_e = _agg(tilt_rows, "tau_int")
    tw_m, tw_e = _agg(tilted, "tau_int")
    av, ae = pm_cells(at_m, at_e)
    tv, te, _tt = _cells(tw_m, tw_e)
    out.append(["twin_with_baseline_tilt_tau_int", "", tv, te,
                f"the twin carrying a per-trace baseline tilt of "
                f"{tilt_hat:.2f} sigma across the grid, solved for over the "
                f"measured from the real wings and not fitted, read the same way "
                "as the row below. This is the term the comparison found "
                "missing, now generated", "DIAGNOSTIC"])
    out.append(["twin_baseline_tilt_sigma_measured", "", f"{tilt_hat:.2f}", "",
                "the rise across the full grid in units of the wing residual "
                "sigma, averaged over the real wings' own least-squares "
                "slopes. MEASURED, never fitted to a correlation time: an "
                "earlier cut solved for it and needed about seven times this, "
                "which is the evidence that a tilt alone does not account for "
                "the archive's correlation", "DIAGNOSTIC"])
    out.append(["measured_tau_int_not_detrended", "", av, ae,
                "the same wings with only the mean removed. Against the "
                "detrended value, the gap is a slow baseline tilt within each "
                "trace, which the twin does not generate", "MEASURED"])

    # the headline the charter asks for
    a_t, a_te = _agg(arc, "tau_int")
    w_t, w_te = _agg(white, "tau_int")
    c_t, c_te = _agg(corr, "tau_int")
    out.append(["verdict_white_reproduces_measured_correlation", "",
                "no" if abs(w_t - a_t) / math.hypot(w_te, a_te) > 3 else "yes",
                "",
                f"archive {a_t:.2f}, twin white {w_t:.2f}, "
                f"{abs(w_t - a_t) / math.hypot(w_te, a_te):.1f} sigma apart. "
                "This is the term the charter binds the twin to and it is the "
                "one an information criterion cannot grade", "DIAGNOSTIC"])
    out.append(["residual_gap_tilt_correlation_sigma", "",
                f"{abs(tw_m - at_m) / math.hypot(tw_e, at_e):.1f}", "",
                "sigma between the twin's correlation time at the MEASURED tilt and "
                "the real one. Nothing here was fitted, so this is a real gap: "
                "the measured tilt does not close the correlation time, and "
                "what else contributes is open", "DIAGNOSTIC"])

    # THE HELD-OUT STATISTICS, which are what the calibration did not touch.
    # One parameter was fitted to one number; three others were written by this
    # same producer and went unread until someone opened the CSV. They are
    # verdicts now, so a future reader cannot repeat that.
    for key, name in (("sigma", "noise_level"),
                      ("rho1", "first_lag"),
                      ("excess_kurtosis", "tail_shape")):
        a_m2, a_e2 = _agg(arc, key)
        t_m2, t_e2 = _agg(tilted, key)
        pull = abs(t_m2 - a_m2) / math.hypot(a_e2, t_e2) if (a_e2 or t_e2) else float("nan")
        out.append([f"heldout_{name}_pull_sigma", "", f"{pull:.1f}", "",
                    f"HELD OUT: the tilt was calibrated on the correlation "
                    f"time and not on this. Real {a_m2:.5g}, twin {t_m2:.5g}. "
                    f"{'The twin reproduces it' if pull <= 3 else 'THE TWIN DOES NOT REPRODUCE IT, so a term is still missing'}",
                    "DIAGNOSTIC"])
    out.append(["verdict_law_tau_reproduces_measured_correlation", "",
                "yes" if abs(c_t - a_t) / math.hypot(c_te, a_te) <= 3 else "no",
                "",
                f"archive {a_t:.2f}, twin at the law's tau_int {c_t:.2f}, "
                f"{abs(c_t - a_t) / math.hypot(c_te, a_te):.1f} sigma apart",
                "DIAGNOSTIC"])

    dst = _CFG_RESULTS / "twin_completeness.csv"
    with open(dst, "w", newline="") as fh:
        csv.writer(fh, lineterminator="\n").writerows(out)
    print(f"{len(arc)} archive traces; tau_int archive {a_t:.2f}, "
          f"twin white {w_t:.2f}, twin at the law {c_t:.2f}")
    print(f"wrote {os.path.relpath(dst, REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

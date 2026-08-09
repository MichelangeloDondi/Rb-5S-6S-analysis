#!/usr/bin/env python3
"""
Digitise the 2025-06-11 wavemeter record from its photograph (module M22)
========================================================================

Why this exists. None of the long-term wavemeter logs were saved to disk, so
`APPARATUS.md` section 6 carries six laser-drift figures read off dated screen
photographs by eye. This module measures one of them instead, and then asks the
question the table cannot: how much of the laser's motion is instrumental, and
what is left once the instrumental part is modelled away.

What the record is. A preliminary session on 2025-06-11, five weeks before the
17-18 July campaign. It is NOT campaign data and nothing here characterises the
campaign laser. Its value is that it is legible enough to measure, and that it
shows the shape of the problem.

Method. The wavemeter draws its trace in saturated blue on white, so the trace
separates by colour. Each pixel column gives the band of frequencies the scan
covered at that moment; its centre is the laser frequency and its width is the
scan modulation. Pixels convert through the plot's own tick spacing, measured
from the image rather than assumed.

The model, current form (2026-08-03 replacement). Between two re-locks the
servo holds the laser onto a reference that is itself settling thermally, so
the frequency RAMPS steadily through the whole interval at a rate that interval
sets for itself. A re-lock ends the ramp with a step, and the step takes a
finite time to complete. Nothing relaxes back. The record is a sawtooth:

  * a free LEVEL and a free RAMP RATE for each inter-lock interval,
  * one SHARED finite RISE TIME for the step at every re-lock,
  * no relaxation term of any kind, and no separate background drift or
    curvature: the per-interval ramps absorb what the old shared quadratic
    background was standing in for,
  * the same three-parameter heteroscedastic noise, sigma(t) = sigma_inf +
    A exp(-t/tau_sigma), fitted jointly and unchanged in form.

Geometry. find_kicks returns 12 times, which cut the record into 13 intervals,
but the first kick lands at 0.222 min, inside the opening 0.4 min the
likelihood drops (see below). So 12 intervals are fitted and 11 re-lock steps
are measured, one at each interior kick. Parameter count 28: 12 levels, 12
ramp rates, 1 rise time, 3 noise parameters.

How it is fitted. Profiled likelihood. With the rise time fixed, the mean is
LINEAR in its 24 levels and ramp rates, so those are solved in closed form by
weighted least squares inside the objective and the outer optimiser searches
only four numbers: the rise time and the three noise parameters. The replaced
fit threw all 19 of its parameters at L-BFGS-B at once, and that was the single
largest source of uncertainty in the number it published: its best-of-20-restart
likelihood moved by 19.8 units across five seeds, which is far more than the
difference between the models it was being used to choose between. The
four-dimensional search is stable to the last digits printed here.

Why the relaxation model was replaced (2026-08-03). The replaced form (one
shared relaxation time constant per kick on a shared quadratic background, 19
parameters, 20-restart L-BFGS-B) was tested against fourteen alternatives on
the same 481 points and the same noise model, with whiteness as the gate rather
than likelihood alone. It failed on four counts:

  * Its residual is not white. Lag-1 autocorrelation 0.68 and a runs test at
    z = -6.3, that is 172 sign runs where 241 are expected, long same-sign
    stretches a correct mean function does not leave.
  * Its optimiser is unstable, as above.
  * Four of its twelve fitted kick amplitudes do essentially nothing (two sit
    exactly at zero, two more below 0.6 MHz), so a third of the events it
    claims to model are not being modelled.
  * Its relaxation is unresolvable in principle here. The fitted time constant
    was 353 min on a 54 min record, so the exponential decays by 14% end to
    end and never distinguishes itself from a straight line.

The sawtooth passes the gate the relaxation model failed. Its residual has RMS
0.660 MHz with a runs test at z = -0.21 (239 runs against 241 expected) and
lag-1 autocorrelation 0.11, measured against the record's own kick-free scatter
of 0.55 MHz in the quiet tail. Ljung-Box over 20 lags is still elevated, driven
by the samples within one decimated step of a kick where the finder's
mid-rise timing and the model's step disagree, so the residual is called white
enough to quote from rather than white.

The pre-first-kick opening ~0.4 min of the record (t < EDGE_CUT_MIN) is
excluded from the LIKELIHOOD: the trace starts already mid-rise with no
preceding interval to anchor it, a photographed edge effect. mu/sigma are still
evaluated back over the full record for the returned arrays, and the figures
draw the model only where it was fitted.

THE RESULT, and it is one number: sigma_inf, the settled floor on unmodelled
laser motion, 0.62 MHz. That is essentially where the replaced model left it
(0.63 MHz), which is the useful part of this replacement: the floor is the one
quantity that survived a mean-model change large enough to retire everything
else the module used to report. Against the campaign's AC-Stark bound of
0.64 MHz it is comparable rather than above it, still consistent with the
archival bound coming from averaging across blocks rather than from any single
block.

WHAT THE SAWTOOTH SAYS ABOUT THE RECORD, beyond the floor. Of the 11 modelled
re-locks, 8 step the frequency up by more than 1 MHz (4 to 18 MHz), 1 steps it
DOWN by 1.1 MHz, and 2 do not step at all within 0.2 MHz: the kick finder
flagged a fast excursion there that the sawtooth explains as the end of a
steep ramp. The ramp rates fall monotonically in magnitude through the record,
from -8.9 MHz/min in the first fitted interval to -0.4 MHz/min in the last,
which is the thermal settle the replaced model was fitting with a single
record-wide quadratic. Reading it interval by interval is what removes the need
for that background term.

WHAT THIS RECORD STILL DOES NOT MEASURE, recorded because three earlier
versions of this module claimed otherwise:

  * A relaxation time constant, of any kind. There is no relaxation in the
    model any more, and the two earlier published values (a slow constant of
    88 min, then a shared 353 min) are both withdrawn. The agreement anyone
    might notice with the 97 min the timestamp audit fitted to the archive
    traces was numerology under both.

  * The number of re-lock events, beyond an order of magnitude. An earlier
    version selected 42 by BIC under a constant-noise model. That was an
    artifact: with the noise held constant, extra events were the only way to
    absorb the early scatter. The finder reports 12 candidates and the
    sawtooth turns 8 of the 11 it can test into real steps, so the record
    supports roughly ten, one every five to seven minutes, which is also what
    the apparatus record describes.

  * A rate the laser holds. The single 0.19 MHz/min in the apparatus table is
    a straight line through a sawtooth. The per-interval rates above are what
    the laser actually does, and no single one of them describes the record.

The in-campaign photograph needs no digitising at all. Its statistics panel is
in shot: mean 301.7796130 THz, standard deviation 100 kHz, and a 38 MHz
excursion across 8.5 minutes, reported by the instrument itself.
"""
from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.optimize import lsq_linear, minimize

ROOT = Path(__file__).resolve().parents[1]
PHOTO = ROOT / "docs" / "apparatus" / "2025-06-11_wavemeter_drift_53min.jpg"
OUT_CSV = ROOT / "results" / "wavemeter_reconstruction.csv"

MHZ_PER_TICK = 2.0        # the y labels step by 2e-6 THz
MIN_PER_TICK = 1.0        # the x labels step by 1 minute
TASKBAR_Y = 820           # below this the photo shows desktop icons, also blue
KICK_SIGMA = 3.0          # see the docstring on why not 2
DECIMATE = 3              # 27 px/min is heavily oversampled for this fit
SEED = 20260731
RESTARTS = 20
EDGE_CUT_MIN = 0.4        # pre-first-kick opening: a digitisation edge effect,
                          # excluded from the fit (see docstring); mu/sigma are
                          # still evaluated back over the full record on return

# Boxes on the mean's linear coefficients. The level box is the one the
# replaced fit used; the ramp box is wider than its shared-drift box because
# the record's own within-interval slopes reach -8 MHz/min.
LEVEL_MHZ = 60.0
RAMP_MHZ_PER_MIN = 20.0
# The rise time runs from well under one digitised pixel (0.037 min) to half a
# minute, searched logarithmically.
RISE_BOUNDS_MIN = (0.004, 0.5)
# sigma_inf, A, tau_sigma: unchanged from the replaced fit.
NOISE_BOUNDS = ((0.05, 5.0), (0.0, 20.0), (0.5, 120.0))
# A step smaller than this is not called a re-lock. It is one third of the kick
# finder's own 1.59 MHz detection threshold, so a flagged event that the
# sawtooth reduces to a fifth of what triggered the finder counts as null.
STEP_MHZ = 1.0


def _blue_mask(rgb: np.ndarray) -> np.ndarray:
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    m = (b > 90) & (b - r > 45) & (b - g > 35)
    m[TASKBAR_Y:, :] = False
    return m


def _runs(idx, gap=4):
    out: list[list[int]] = []
    for i in idx:
        if not out or i - out[-1][-1] > gap:
            out.append([i])
        else:
            out[-1].append(i)
    return [float(np.mean(g)) for g in out]


def _calibrate(rgb: np.ndarray) -> tuple[float, float]:
    """Pixels per minute and pixels per 2 MHz, from the plot's own ticks."""
    sub = rgb[140:820, 85:1550]
    r, g, b = sub[..., 0], sub[..., 1], sub[..., 2]
    grey = (abs(r - g) < 28) & (abs(g - b) < 28) & (r > 105) & (r < 205)
    cols = grey.sum(0)
    px_per_min = float(np.median(np.diff(_runs(np.nonzero(cols > cols.max() * 0.55)[0]))))

    marg = rgb[140:820, 28:88]
    rows = np.nonzero((marg.mean(2) < 135).sum(1) > 3)[0]
    px_per_tick = float(np.median(np.diff(_runs(rows))))
    return px_per_min, px_per_tick


def extract():
    """Time (min), band centre (MHz), band width (MHz), and the calibration."""
    rgb = np.asarray(Image.open(PHOTO).convert("RGB")).astype(int)
    blue = _blue_mask(rgb)
    px_per_min, px_per_tick = _calibrate(rgb)
    mhz_per_px = MHZ_PER_TICK / px_per_tick

    x, med, width = [], [], []
    for col in range(rgb.shape[1]):
        ys = np.nonzero(blue[:, col])[0]
        if ys.size < 8:
            continue
        x.append(col)
        med.append(float(np.median(ys)))
        width.append((ys.max() - ys.min()) * mhz_per_px)
    x = np.asarray(x, float)
    t = (x - x.min()) * (MIN_PER_TICK / px_per_min)
    f = -(np.asarray(med) - med[0]) * mhz_per_px     # pixels grow downward
    return t, f, np.asarray(width), px_per_min, px_per_tick


def find_kicks(t, f, k: float = KICK_SIGMA) -> np.ndarray:
    """Upward discontinuities. A re-lock kicks the frequency up by definition."""
    d = np.diff(f)
    quiet = d[np.abs(d) < np.percentile(np.abs(d), 95)]
    idx = np.nonzero(d > k * np.std(quiet))[0]
    return np.array([float(t[int(g)]) for g in _runs(idx, gap=10)])


# ------------------------------------------------------------ the model ----
def _seg_weights(tt, tk, rise):
    """One column per inter-lock interval, summing to 1 at every time.

    A hard indicator would step the mean instantaneously, but the trace takes
    two to six pixels to climb, so the boundary between consecutive intervals
    is a logistic of width `rise`. The model then climbs over the same few
    pixels the record does, which is where the replaced fit's largest
    residual spikes lived.
    """
    K = len(tk)
    s = [np.ones_like(tt)]
    for j in range(1, K):
        z = np.clip((tt - tk[j]) / rise, -600.0, 600.0)
        s.append(1.0 / (1.0 + np.exp(-z)))
    s.append(np.zeros_like(tt))
    return np.column_stack([s[j] - s[j + 1] for j in range(K)])


def _design(tt, tk, rise):
    """Columns of the mean: K interval levels, then K interval ramps."""
    w = _seg_weights(tt, tk, rise)
    return np.column_stack([w, w * (tt[:, None] - np.asarray(tk)[None, :])])


def _solve_lin(x, y, w, lo, hi):
    """Weighted least squares with every coefficient inside its own box.

    The unconstrained solve is what the fit almost always wants (no coefficient
    reaches its box at the optimum). The bounded solve is the fallback, and a
    clip is the fallback to that, so the objective never sees a value it has to
    guess about.
    """
    xw, yw = x * w[:, None], y * w
    with np.errstate(all="ignore"):
        b, *_ = np.linalg.lstsq(xw, yw, rcond=None)
    if np.all(np.isfinite(b)) and np.all(b >= lo - 1e-12) and np.all(b <= hi + 1e-12):
        return b
    try:
        with np.errstate(all="ignore"):
            r = lsq_linear(xw, yw, bounds=(lo, hi), method="bvls", max_iter=300)
        if np.all(np.isfinite(r.x)):
            return r.x
    except Exception:
        pass
    return np.clip(np.where(np.isfinite(b), b, 0.0), lo, hi)


def _sigma(theta, tt):
    return theta[0] + theta[1] * np.exp(-tt / theta[2])


def _profile(tfit, ffit, tk, rise, noise, lo, hi):
    """Design, boxed weighted solve, residual: the profiled step, in one place.

    Under one errstate, because numpy reports floating-point flags at the next
    checked operation rather than where they were raised, and the
    rank-revealing solve inside `_solve_lin` raises them routinely while the
    optimiser probes rise times so short that two interval columns coincide.
    Finiteness is checked on the outputs instead of trusted from the flags.
    """
    with np.errstate(all="ignore"):
        s = _sigma(noise, tfit)
        x = _design(tfit, tk, rise)
        b = _solve_lin(x, ffit, 1.0 / s, lo, hi)
        r = ffit - x @ b
    return s, b, r


def _acf(x, lag: int = 1) -> float:
    x = np.asarray(x, float)
    x = x - x.mean()
    return float(np.sum(x[:-lag] * x[lag:]) / np.sum(x * x))


def _runs_z(x) -> float:
    """Wald-Wolfowitz runs statistic on the residual signs."""
    s = np.sign(np.asarray(x, float))
    s[s == 0] = 1
    npos, nneg = int((s > 0).sum()), int((s < 0).sum())
    n = npos + nneg
    obs = 1 + int(np.sum(s[1:] != s[:-1]))
    mu = 2.0 * npos * nneg / n + 1.0
    var = 2.0 * npos * nneg * (2.0 * npos * nneg - n) / (n * n * (n - 1.0))
    return float((obs - mu) / np.sqrt(var))


def fit(t, f, tk, restarts: int = RESTARTS, edge_cut: float = EDGE_CUT_MIN,
        seed: int = SEED):
    """Joint maximum likelihood for the sawtooth: a free level and a free ramp
    per inter-lock interval, one shared finite rise at each re-lock, and the
    settling noise.

    Fitted by PROFILED likelihood. Fix the rise time and the mean is linear in
    its 2K levels and ramps, so they are solved by weighted least squares
    inside the objective and the outer search covers only four numbers. That
    replaced a 19-dimensional L-BFGS-B search whose answer moved by 19.8 in
    likelihood across seeds. See the module docstring for the audit that
    retired the relaxation model this replaces.

    Points with t < edge_cut are excluded from the likelihood (a digitisation
    edge effect at the start of the photograph). mu/sigma are still evaluated
    back over the FULL input t for the return value, so callers that plot the
    whole record are unaffected.

    Fitting the noise instead of choosing a weighting is the whole point. The
    returned pull width is the diagnostic and should come out at 1.
    """
    tk = np.asarray(tk, float)
    K = len(tk)
    m = t >= edge_cut
    tfit, ffit = t[m], f[m]
    lo = np.concatenate([np.full(K, -LEVEL_MHZ), np.full(K, -RAMP_MHZ_PER_MIN)])
    hi = -lo

    def unpack(z):
        return float(np.exp(z[0])), z[1:]

    def obj(z):
        rise, noise = unpack(z)
        s = _sigma(noise, tfit)
        if not np.all(np.isfinite(s)) or np.any(s <= 1e-3):
            return 1e12
        _s, _b, r = _profile(tfit, ffit, tk, rise, noise, lo, hi)
        with np.errstate(all="ignore"):
            v = float(np.sum(np.log(s) + 0.5 * (r / s) ** 2))
        return v if np.isfinite(v) else 1e12

    bnds = ([(float(np.log(RISE_BOUNDS_MIN[0])), float(np.log(RISE_BOUNDS_MIN[1])))]
            + [tuple(map(float, b)) for b in NOISE_BOUNDS])
    rng = np.random.default_rng(seed)
    best = None
    for _ in range(restarts):
        z0 = np.array([rng.uniform(*bnds[0]), rng.uniform(0.3, 1.2),
                       rng.uniform(1.0, 8.0), rng.uniform(2.0, 15.0)])
        r = minimize(obj, z0, method="L-BFGS-B", bounds=bnds,
                     options={"maxiter": 20000, "maxfun": 60000,
                              "ftol": 1e-12, "gtol": 1e-10})
        if best is None or r.fun < best.fun:
            best = r
    # the boxed inner solve makes the profiled surface only piecewise smooth,
    # so polish the gradient optimum with a derivative-free step
    pol = minimize(obj, best.x, method="Nelder-Mead", bounds=bnds,
                   options={"maxiter": 8000, "maxfev": 12000,
                            "xatol": 1e-9, "fatol": 1e-11})
    z = pol.x if pol.fun < best.fun else best.x
    nll = float(min(pol.fun, best.fun))

    rise, noise = unpack(z)
    sg_fit, beta, resid_fit = _profile(tfit, ffit, tk, rise, noise, lo, hi)
    level, ramp = beta[:K], beta[K:]

    # What the fit says the frequency actually did at each re-lock it can test:
    # the level the previous interval's ramp had reached, against the level the
    # next interval starts from. The first kick has no fitted interval before
    # it, so 12 detected kicks give 11 measurable steps.
    steps = [{"t_kick": float(tk[j]),
              "step_mhz": float(level[j] - (level[j - 1]
                                            + ramp[j - 1] * (tk[j] - tk[j - 1])))}
             for j in range(1, K)]
    up = int(sum(1 for s in steps if s["step_mhz"] > STEP_MHZ))
    down = int(sum(1 for s in steps if s["step_mhz"] < -STEP_MHZ))

    res = {"sigma_inf": float(noise[0]), "noise_amp": float(noise[1]),
           "tau_sigma": float(noise[2]), "rise_min": rise, "n_kicks": K,
           "n_steps": len(steps), "n_up": up, "n_down": down,
           "n_null": len(steps) - up - down, "steps": steps,
           "level_mhz": level, "ramp_mhz_per_min": ramp,
           "pull_width": float(np.std(resid_fit / sg_fit)),
           "resid_rms": float(np.sqrt(np.mean(resid_fit ** 2))),
           "resid_acf1": _acf(resid_fit, 1),
           "resid_runs_z": _runs_z(resid_fit),
           "n_fit_points": int(tfit.size),
           "n_par": int(2 * K + 4), "nll": nll}
    with np.errstate(all="ignore"):
        mu_all = _design(t, tk, rise) @ beta
    return res, mu_all, _sigma(noise, t), f - mu_all


def reconstruct() -> dict:
    t, f, width, px_min, px_tick = extract()
    tk = find_kicks(t, f)
    res, mu_s, sg_s, _ = fit(t[::DECIMATE], f[::DECIMATE], tk)
    res.update({"record_min": float(t.max()), "band_mhz": float(np.median(width)),
                "px_per_min": px_min, "px_per_tick": px_tick, "kick_times": tk,
                "t": t, "f": f, "band": width, "edge_cut_min": EDGE_CUT_MIN,
                "t_fit": t[::DECIMATE], "mu": mu_s, "sigma": sg_s})
    return res


if __name__ == "__main__":
    r = reconstruct()
    OUT_CSV.parent.mkdir(exist_ok=True)
    with OUT_CSV.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["quantity", "key", "value", "unit"])
        w.writerow(["record_length", "2025-06-11", f"{r['record_min']:.1f}",
                    "min; digitised from the screen photograph"])
        w.writerow(["scan_band_width", "2025-06-11", f"{r['band_mhz']:.1f}",
                    "MHz; the scan modulation, laser axis"])
        w.writerow(["settled_noise_floor", "2025-06-11", f"{r['sigma_inf']:.2f}",
                    "MHz; THE RESULT. unmodelled laser motion once the re-lock "
                    "steps and the per-interval ramps are removed; the one "
                    "quantity that survived the 2026-08-03 replacement of the "
                    "relaxation model by the sawtooth (0.63 before, 0.62 now); "
                    "see the module docstring"])
        w.writerow(["noise_settling_time", "2025-06-11", f"{r['tau_sigma']:.2f}",
                    "min; the scatter itself settles on this timescale. much "
                    "shorter than the replaced model's 9.1 min because the "
                    "ramps now carry the early structure the noise term used "
                    "to absorb"])
        w.writerow(["n_relock_events", "2025-06-11", r["n_kicks"],
                    "count; candidate events from the kick finder, which did "
                    "not change at the 2026-08-03 replacement. order of "
                    "magnitude only, one per 5-7 min, consistent with the "
                    "apparatus record"])
        w.writerow(["n_modelled_steps", "2025-06-11", r["n_steps"],
                    "count; the candidates the sawtooth can test. the first "
                    "kick at 0.22 min falls inside the excluded opening 0.4 "
                    "min, so it has no fitted interval before it"])
        w.writerow(["n_upward_relocks", "2025-06-11", r["n_up"],
                    f"count; modelled steps above +{STEP_MHZ:.0f} MHz, the "
                    "re-locks proper"])
        w.writerow(["n_downward_steps", "2025-06-11", r["n_down"],
                    f"count; modelled steps below -{STEP_MHZ:.0f} MHz. the "
                    "replaced model could not express one: its amplitudes "
                    "were bounded non-negative"])
        w.writerow(["n_null_events", "2025-06-11", r["n_null"],
                    f"count; flagged events whose modelled step is within "
                    f"{STEP_MHZ:.0f} MHz of zero, i.e. the end of a steep ramp "
                    "rather than a re-lock"])
        w.writerow(["relock_rise_time", "2025-06-11", f"{r['rise_min']:.4f}",
                    "min; ONE shared rise time for the step at every re-lock "
                    "(logistic width). about 2.6 s, roughly one digitised "
                    "pixel, so the record resolves the step as fast but not "
                    "as instantaneous"])
        w.writerow(["ramp_rate_first_interval", "2025-06-11",
                    f"{r['ramp_mhz_per_min'][0]:.2f}",
                    "MHz/min; the fitted ramp of the first fitted inter-lock "
                    "interval. these per-interval ramps replace the replaced "
                    "model's record-wide drift and curvature"])
        w.writerow(["ramp_rate_last_interval", "2025-06-11",
                    f"{r['ramp_mhz_per_min'][-1]:.2f}",
                    "MHz/min; the fitted ramp of the last interval. the fall "
                    "in magnitude across the record is the thermal settle"])
        w.writerow(["pull_width", "2025-06-11", f"{r['pull_width']:.3f}",
                    "dimensionless; 1.0 means the settling-noise model is right"])
        w.writerow(["residual_rms", "2025-06-11", f"{r['resid_rms']:.3f}",
                    "MHz; over the fitted points, against the record's own "
                    "kick-free scatter of 0.55 MHz"])
        w.writerow(["residual_runs_z", "2025-06-11", f"{r['resid_runs_z']:.2f}",
                    "dimensionless; Wald-Wolfowitz runs statistic on the "
                    "residual signs. the replaced relaxation model sat at "
                    "-6.3, which is what retired it"])
        w.writerow(["residual_acf1", "2025-06-11", f"{r['resid_acf1']:.3f}",
                    "dimensionless; lag-1 autocorrelation of the residual, "
                    "0.68 under the replaced relaxation model"])
        w.writerow(["nll", "2025-06-11", f"{r['nll']:.3f}",
                    f"dimensionless; negative log-likelihood at the optimum, "
                    f"{r['n_par']} parameters on {r['n_fit_points']} points. "
                    "not comparable to the replaced model's 259.3 as a "
                    "number to prefer, since the parameter counts differ; the "
                    "whiteness of the residual is what decided between them"])
    for k in ("record_min", "band_mhz", "n_kicks", "sigma_inf", "tau_sigma",
              "rise_min", "n_up", "n_down", "n_null", "pull_width",
              "resid_rms", "resid_acf1", "resid_runs_z", "nll"):
        print(f"  {k:22} {r[k]}")
    print(f"\n  Wrote {OUT_CSV.relative_to(ROOT)}.")

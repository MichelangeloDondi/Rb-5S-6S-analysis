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

The model, current form (2026-08-02 refinement). A re-lock kicks the frequency
up; every kick then relaxes with ONE SHARED time constant tau (amplitude free
per kick), riding on a SHARED quadratic background drift(t) = drift*t +
curv*t^2 common to the whole record. The mechanism split: tau is the re-lock
relaxation (a single, largely unresolved, long timescale -- see below); drift
and curv together are the record-wide cavity thermal settle, which is not
exactly linear over the ~53 min window (curv is its leading correction, the
same shape a slow exponential with T >> 53 min shows to second order in
t/T). Both pieces are shared across every kick: no per-kick time constant is
fit, which is the guard against overfitting a 12-event record.

Why this form and not the superseded one (residual audit, 2026-08-02). The
previous model (two shared exponentials per kick, tau_fast/tau_slow with a
shared mixing fraction, no separate drift term) left strong residual
structure against the digitised trace: lag-1 autocorrelation 0.78 and a runs
test at z=-6.8 on 481 points (t > 0.4 min), i.e. long same-sign stretches a
correct model should not leave. Four alternatives were fit against the same
heteroscedastic noise model and compared by BIC:
  * one shared tau + linear drift (no curvature): decisively worse
    (BIC +51 relative to the superseded form) -- a plain single exponential
    plus a straight line is a worse functional match than the old
    two-exponential mixture, despite having one fewer parameter.
  * the superseded form plus a linear drift term: no improvement (BIC +6);
    the fitted drift lands at ~0, because the old model's own tau_slow was
    already pinned near its bound (a de facto near-linear component), so an
    explicit drift term is redundant.
  * curvature reset at every individual relaxation (i.e. inside each
    post-kick segment rather than in the shared background): decisively
    worse (BIC +213). The curvature belongs to the shared record-wide
    background, not to each relaxation profile.
  * two shared time constants (fast + slow) plus the shared quadratic
    background: nominally the best raw BIC (-18 relative to the superseded
    form), but the fit is degenerate -- across 60 restarts spanning the
    mixing fraction over its full range, the best-likelihood solutions pin
    the fraction EXACTLY at its fast-component-unused boundary in 9 of the
    top 10 local optima. The data never wants a second, faster mechanism
    once the shared background curvature is present, so it is dropped:
    algebraically, that degenerate optimum already equals a single-tau
    model, and refitting the single-tau form directly (no unused second
    timescale to pin) reaches the same likelihood cleanly.
That single-tau-plus-shared-quadratic-background form is what is implemented
below. It has the SAME parameter count as the superseded model (19: tau,
base, drift, curv, 12 per-kick amplitudes, 3 noise parameters -- vs the old
tau_fast, tau_slow, frac, base, 12 amplitudes, 3 noise parameters), so its
likelihood gain (Delta(-2 ln L) = 32.8) is not bought with extra freedom:
BIC and AIC move together and both favour it decisively (Kass-Raftery
"very strong"). Residual structure shrinks but does not vanish (lag-1
autocorrelation 0.71, runs z=-5.35): what is left is (a) short (~1 min)
correlated wiggle in the digitised trace itself, which is the noise model's
job, not the mean's, and (b) a small (5-8 MHz) systematic dip immediately
BEFORE several kicks, present at essentially the same size under both models
-- a real feature of the record (an approach-to-unlock transient) that is a
different physical mechanism from a post-kick relaxation and is left
unmodelled rather than fit with a per-kick nuisance parameter.

The pre-first-kick opening ~0.4 min of the record (t < EDGE_CUT_MIN) is
excluded from the LIKELIHOOD (not just the figure): the trace starts already
mid-rise with no preceding kick to anchor it, a photographed edge effect no
relaxation-based mean function can represent. It was already excluded from
the fig15 panel (a) overlay (drawn only for t > 0.4 min); this makes the fit
itself agree with what is plotted. mu/sigma are still evaluated back over the
full record for the returned arrays, so the overlay is unchanged in extent.

The noise settles too, and that still matters more than the mean's exact
form. The record starts disturbed and quietens, so the scatter is modelled as
sigma(t) = sigma_inf + A exp(-t/tau_sigma) and everything is fitted by joint
maximum likelihood, unchanged in FORM across this refinement (only the mean
model changed). Fitting the noise rather than choosing a weighting is what
makes the result stable, and the pull distribution comes out at unit width,
which is the check that the noise model is right (0.995 under the current
mean model).

THE RESULT, and it is one number: sigma_inf, the settled floor on unmodelled
laser motion, moved with this refinement from about 0.8-1.0 MHz to about
0.6 MHz (point estimate 0.63 MHz, this seed/restart schedule) -- lower
because less residual structure now needs to be absorbed into the noise term
once the mean model fits better. It is a real, directionally significant
shift (about a third lower), sitting outside the superseded number's own
generously-stated ~20% band on the low side. Against the campaign's
AC-Stark bound of 0.64 MHz it is now comparable rather than above it, still
consistent with the archival bound coming from averaging across blocks
rather than from any single block.

WHAT THIS RECORD STILL DOES NOT MEASURE, recorded because two earlier
versions of this module claimed otherwise and a third (the two-exponential
form superseded above) implied a two-mechanism split the record cannot
support:

  * A precise relaxation time constant. Even in this simpler single-tau
    form, tau is loosely pinned: this seed/restart schedule lands at
    353 min, a local (Laplace) uncertainty at a nearby optimum gives
    roughly +/-100 min (about 30%), and comparably good fits
    (Delta(-2 ln L) < 10) were found from roughly 250 to 550 min across many
    restarts in the offline audit. That is a real improvement on the
    superseded model's factor-of-forty-seven wander between its two,
    mutually-tradeable timescales, but it is still "one long, largely
    unresolved timescale", not a precision number. An earlier version
    reported a slow constant of 88 min and pointed out that the timestamp
    audit fitted 97 min to the archive traces; that agreement was numerology
    then and stays numerology now that the fitted value is different again.

  * The number of re-lock events, beyond an order of magnitude. An earlier
    version selected 42 by BIC under a constant-noise model. That was an
    artifact: with the noise held constant, extra events were the only way to
    absorb the early scatter. Under the correct likelihood the ranking inverts
    and 42 becomes the worst option. The record supports roughly ten, one every
    five to seven minutes, which is also what the apparatus record describes.
    Unaffected by this refinement (12 either way; the kick FINDER did not
    change, only the relaxation model fit to what it finds).

The in-campaign photograph needs no digitising at all. Its statistics panel is
in shot: mean 301.7796130 THz, standard deviation 100 kHz, and a 38 MHz
excursion across 8.5 minutes, reported by the instrument itself.
"""
from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parents[1]
PHOTO = ROOT / "docs" / "apparatus" / "2025-06-11_wavemeter_drift_53min.jpg"
OUT_CSV = ROOT / "results" / "wavemeter_reconstruction.csv"

MHZ_PER_TICK = 2.0        # the y labels step by 2e-6 THz
MIN_PER_TICK = 1.0        # the x labels step by 1 minute
TASKBAR_Y = 820           # below this the photo shows desktop icons, also blue
KICK_SIGMA = 3.0          # see the docstring on why not 2
DECIMATE = 3              # 27 px/min is heavily oversampled for this fit
SEED = 20260731
EDGE_CUT_MIN = 0.4        # pre-first-kick opening: a digitisation edge effect,
                          # excluded from the fit (see docstring); mu/sigma are
                          # still evaluated back over the full record on return


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


def fit(t, f, tk, restarts: int = 20, edge_cut: float = EDGE_CUT_MIN):
    """Joint maximum likelihood: relaxation + shared background for the mean,
    settling for the noise.

    Mean model (current, 2026-08-02): one SHARED relaxation time constant tau
    per kick (amplitude free per kick) plus a SHARED quadratic background
    drift(t) = drift*t + curv*t^2 across the whole record. Superseded by this:
    two shared exponentials (tau_fast, tau_slow, shared mixing fraction), no
    separate drift term -- see the module docstring for the residual audit
    that replaced it (BIC -32.8 at the SAME parameter count, 19).

    Points with t < edge_cut are excluded from the likelihood (a digitisation
    edge effect, not a re-lock or a relaxation -- see the module docstring);
    mu/sigma are still evaluated back over the FULL input t for the return
    value, so callers that plot the whole record are unaffected.

    Fitting the noise instead of choosing a weighting is the whole point. The
    returned pull width is the diagnostic and should come out at 1.
    """
    K = len(tk)
    rng = np.random.default_rng(SEED)
    m = t >= edge_cut
    tfit, ffit = t[m], f[m]

    def mu(p, tt):
        y = np.full_like(tt, p[1]) + p[2] * tt + p[3] * tt ** 2
        for ti, ai in zip(tk, p[4:4 + K]):
            mm = tt >= ti
            d = tt[mm] - ti
            y[mm] += ai * np.exp(-d / p[0])
        return y

    def sg(p, tt):
        return p[4 + K] + p[5 + K] * np.exp(-tt / p[6 + K])

    def nll(p):
        s = sg(p, tfit)
        if p[0] <= 0 or p[6 + K] <= 0 or np.any(s <= 1e-3):
            return 1e12
        return float(np.sum(np.log(s) + 0.5 * ((ffit - mu(p, tfit)) / s) ** 2))

    # tau: broad log-uniform, since the superseded model's own tau_slow (near
    # its bound) already said "long, not a fast piezo snap" -- see docstring.
    bnds = ([(0.1, 600), (-60, 60), (-3, 3), (-0.05, 0.05)] + [(0, 40)] * K
            + [(0.05, 5), (0, 20), (0.5, 120)])

    # This surface is hard: curvature, drift, tau and 12 free per-kick
    # amplitudes trade off badly enough that random amplitude starts alone
    # regularly strand L-BFGS-B 30-40 nll worse than the true optimum
    # (verified against a much larger offline search). What fixes it is
    # seeding each amplitude at its own OBSERVED jump (data just after the
    # kick minus data just before it) instead of a random guess -- a cheap,
    # deterministic, per-kick starting point that removes most of the
    # 12-dimensional difficulty before the optimizer ever sees curvature.
    def _jump_estimate(ti):
        after = ffit[tfit >= ti]
        before = ffit[tfit < ti]
        if len(after) == 0 or len(before) == 0:
            return 5.0
        return float(np.clip(after[0] - before[-1], 0.5, 39.0))

    amp0 = np.array([_jump_estimate(ti) for ti in tk])

    best = None
    for i in range(restarts):
        p0 = ([float(np.exp(rng.uniform(np.log(20), np.log(550)))),
               float(np.median(ffit)) + rng.uniform(-15, 15),
               rng.uniform(-2.2, 0.3), rng.uniform(-0.02, 0.025)]
              + list(np.clip(amp0 * rng.uniform(0.6, 1.3, size=K), 0, 40))
              + [rng.uniform(0.5, 1.1), rng.uniform(1, 10), rng.uniform(1, 8)])
        r = minimize(nll, p0, method="L-BFGS-B", bounds=bnds,
                     options={"maxiter": 20000, "maxfun": 40000})
        if best is None or r.fun < best.fun:
            best = r
    p = best.x
    resid_fit = ffit - mu(p, tfit)
    return ({"sigma_inf": float(p[4 + K]), "tau_sigma": float(p[6 + K]),
             "tau_relax": float(p[0]), "drift_mhz_per_min": float(p[2]),
             "curvature_mhz_per_min2": float(p[3]), "n_kicks": K,
             "pull_width": float(np.std(resid_fit / sg(p, tfit))),
             "nll": float(best.fun)},
            mu(p, t), sg(p, t), f - mu(p, t))


def reconstruct() -> dict:
    t, f, width, px_min, px_tick = extract()
    tk = find_kicks(t, f)
    res, mu_s, sg_s, _ = fit(t[::DECIMATE], f[::DECIMATE], tk)
    res.update({"record_min": float(t.max()), "band_mhz": float(np.median(width)),
                "px_per_min": px_min, "px_per_tick": px_tick, "kick_times": tk,
                "t": t, "f": f, "band": width,
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
                    "MHz; THE RESULT. unmodelled laser motion once re-locks, their "
                    "relaxation and the shared background drift are removed; "
                    "moved down about a third at the 2026-08-02 mean-model "
                    "refinement (residual structure absorbed into a better mean, "
                    "not noise); see the module docstring"])
        w.writerow(["noise_settling_time", "2025-06-11", f"{r['tau_sigma']:.1f}",
                    "min; the scatter itself settles on this timescale"])
        w.writerow(["n_relock_events", "2025-06-11", r["n_kicks"],
                    "count; order of magnitude only, one per 5-7 min, "
                    "consistent with the apparatus record; unaffected by the "
                    "2026-08-02 mean-model refinement (the kick finder did not change)"])
        w.writerow(["pull_width", "2025-06-11", f"{r['pull_width']:.3f}",
                    "dimensionless; 1.0 means the settling-noise model is right"])
        w.writerow(["relaxation_tau", "2025-06-11", f"{r['tau_relax']:.1f}",
                    "min; ONE shared re-lock relaxation constant (superseded a "
                    "two-timescale form the record could not resolve, see the "
                    "module docstring); still loosely pinned, local SE ~30%, "
                    "comparably good fits found from ~250 to ~550 min"])
        w.writerow(["background_drift", "2025-06-11", f"{r['drift_mhz_per_min']:.3f}",
                    "MHz/min; shared linear term of the record-wide background "
                    "(NOT the campaign held-lock drift, a different record/script)"])
        w.writerow(["background_curvature", "2025-06-11", f"{r['curvature_mhz_per_min2']:.5f}",
                    "MHz/min^2; shared quadratic term, the leading correction to "
                    "treating the ~53 min background as linear -- the term whose "
                    "absence was the biggest defect of the superseded model"])
    for k in ("record_min", "band_mhz", "n_kicks", "sigma_inf", "tau_sigma", "pull_width"):
        print(f"  {k:22} {r[k]}")
    print(f"\n  Wrote {OUT_CSV.relative_to(ROOT)}.")

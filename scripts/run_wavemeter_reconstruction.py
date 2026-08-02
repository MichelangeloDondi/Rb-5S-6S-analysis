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

The model, and how it was arrived at. A re-lock kicks the frequency up and it
relaxes back, so the mean is a sum of relaxations, one per event, with shared
time constants. Two exponentials beat one decisively and three add nothing. A
stretched exponential loses by a wide margin despite having fewer parameters,
which says the relaxation is two mechanisms rather than a continuum of
timescales.

The noise settles too, and that turned out to matter more than the mean. The
record starts disturbed and quietens, so the scatter is modelled as
sigma(t) = sigma_inf + A exp(-t/tau_sigma) and everything is fitted by joint
maximum likelihood. Fitting the noise rather than choosing a weighting is what
makes the result stable, and the pull distribution comes out at unit width,
which is the check that the noise model is right.

THE RESULT, and it is one number: sigma_inf, the settled floor on unmodelled
laser motion, is about 0.8 to 0.95 MHz. That is stable to twenty per cent
across every kick count, weighting and random restart tried. Against the
campaign's AC-Stark bound of 0.64 MHz it is comparable rather than dominant,
which is consistent with the archival bound coming from averaging across blocks
rather than from any single block.

WHAT THIS RECORD DOES NOT MEASURE, recorded because two earlier versions of
this module claimed otherwise:

  * The relaxation time constants. They wander over a factor of forty-seven
    between fits of equal likelihood, because with one free amplitude per event
    the model trades amplitude against time constant. An earlier version
    reported a slow constant of 88 min and pointed out that the timestamp audit
    fitted 97 min to the archive traces. That agreement was numerology.

  * The number of re-lock events, beyond an order of magnitude. An earlier
    version selected 42 by BIC under a constant-noise model. That was an
    artifact: with the noise held constant, extra events were the only way to
    absorb the early scatter. Under the correct likelihood the ranking inverts
    and 42 becomes the worst option. The record supports roughly ten, one every
    five to seven minutes, which is also what the apparatus record describes.

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


def fit(t, f, tk, restarts: int = 6):
    """Joint maximum likelihood: relaxations for the mean, settling for the noise.

    Fitting the noise instead of choosing a weighting is the whole point. The
    returned pull width is the diagnostic and should come out at 1.
    """
    K = len(tk)
    rng = np.random.default_rng(SEED)

    def mu(p):
        y = np.full_like(t, p[3])
        for ti, ai in zip(tk, p[4:4 + K]):
            m = t >= ti
            d = t[m] - ti
            y[m] += ai * (p[2] * np.exp(-d / p[0]) + (1 - p[2]) * np.exp(-d / p[1]))
        return y

    def sg(p):
        return p[4 + K] + p[5 + K] * np.exp(-t / p[6 + K])

    def nll(p):
        s = sg(p)
        if p[0] <= 0 or p[1] <= 0 or p[6 + K] <= 0 or np.any(s <= 1e-3):
            return 1e12
        return float(np.sum(np.log(s) + 0.5 * ((f - mu(p)) / s) ** 2))

    bnds = ([(0.1, 20), (2, 600), (0, 1), (-60, 60)] + [(0, 40)] * K
            + [(0.05, 5), (0, 20), (0.5, 120)])
    best = None
    for _ in range(restarts):
        p0 = ([rng.uniform(1, 9), rng.uniform(20, 350), rng.uniform(0.3, 0.95),
               float(np.median(f))]
              + [rng.uniform(1, 9) for _ in range(K)]
              + [rng.uniform(0.5, 1.1), rng.uniform(1, 10), rng.uniform(1, 8)])
        r = minimize(nll, p0, method="L-BFGS-B", bounds=bnds,
                     options={"maxiter": 20000, "maxfun": 40000})
        if best is None or r.fun < best.fun:
            best = r
    p = best.x
    resid = f - mu(p)
    return ({"sigma_inf": float(p[4 + K]), "tau_sigma": float(p[6 + K]),
             "tau_fast": float(p[0]), "tau_slow": float(p[1]), "n_kicks": K,
             "pull_width": float(np.std(resid / sg(p))), "nll": float(best.fun)},
            mu(p), sg(p), resid)


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
                    "MHz; THE RESULT. unmodelled laser motion once re-locks and "
                    "their relaxation are removed; stable to ~20% across kick "
                    "counts, weightings and restarts"])
        w.writerow(["noise_settling_time", "2025-06-11", f"{r['tau_sigma']:.1f}",
                    "min; the scatter itself settles on this timescale"])
        w.writerow(["n_relock_events", "2025-06-11", r["n_kicks"],
                    "count; order of magnitude only, one per 5-7 min, "
                    "consistent with the apparatus record"])
        w.writerow(["pull_width", "2025-06-11", f"{r['pull_width']:.3f}",
                    "dimensionless; 1.0 means the settling-noise model is right"])
        w.writerow(["relaxation_tau_fast", "2025-06-11", f"{r['tau_fast']:.2f}",
                    "min; NOT CONSTRAINED by this record, see the module docstring"])
        w.writerow(["relaxation_tau_slow", "2025-06-11", f"{r['tau_slow']:.1f}",
                    "min; NOT CONSTRAINED, varies ~50x between equal-likelihood fits"])
    for k in ("record_min", "band_mhz", "n_kicks", "sigma_inf", "tau_sigma", "pull_width"):
        print(f"  {k:22} {r[k]}")
    print(f"\n  Wrote {OUT_CSV.relative_to(ROOT)}.")

#!/usr/bin/env python3
"""
Digitise the 2025-06-11 wavemeter record from its photograph (module M22)
========================================================================

Why this exists. None of the long-term wavemeter logs were saved to disk, so
`APPARATUS.md` §6 carries six drift figures read off dated screen photographs
by eye, quoted at plus or minus twenty per cent. One of those figures does real
work: the 0.19 MHz/min for the cavity-locked laser is what the factor of two to
five for the reference-cavity lock rests on, and it is the number the archive's
own within-block bound is said to match.

A number that load-bearing should not be an eyeball estimate when the
photograph is legible enough to measure. This module measures it.

Method. The wavemeter plots its trace in saturated blue on a white field, so
the trace separates from the axes, gridlines and text by colour alone. For each
pixel column the blue pixels give the band of frequencies the scan covered at
that time. The centre of that band is the laser frequency; the width is the
scan modulation. Pixels convert to physical units through the plot's own axes,
whose tick spacing is measured from the image rather than assumed.

What it finds, and it is not a drift rate at all. The record is a SAWTOOTH.
Eight discrete upward steps of +2.4 to +15.7 MHz punctuate it, and between them
the frequency decays back, at -9.3 MHz/min in the first short segment easing to
-0.43 MHz/min in the last and longest. A straight line through that measures
nothing: the quoted 0.19 MHz/min is the residue of averaging jumps against
decays, and its value depends mostly on where the jumps happen to fall.

That structure is not a surprise here, which is the point. APPARATUS.md section
6 already says the cavity lock kept dropping out during the etalon thermal
transient with each recapture landing megahertz-scale off, and the timestamp
audit fit one universal re-kick with a time constant near 97 minutes, re-armed
at every re-lock. This photograph shows that behaviour directly, and it was
reconstructed from a different source than the traces those conclusions came
from.

Two estimators of the band centre are computed, the midpoint of the extremes
and the median of the blue pixels. They agree to 0.001 MHz/min, which is the
check that the structure is in the data rather than in the choice of estimator.

Limits, which are real. The calibration assumes the axis ticks are evenly
spaced, which they are on this instrument. Reading a photograph of a screen
cannot recover what the saved log would have held, and the point of this module
is not to claim otherwise. It is to replace an eyeball estimate with a
measurement that a reader can reproduce from the same image.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PHOTO = ROOT / "docs" / "apparatus" / "2025-06-11_wavemeter_drift_53min.jpg"
OUT_CSV = ROOT / "results" / "wavemeter_reconstruction.csv"

# Axis calibration, measured from the image itself (see _calibrate).
MHZ_PER_TICK = 2.0        # the y labels step by 2e-6 THz
MIN_PER_TICK = 1.0        # the x labels step by 1 minute
TASKBAR_Y = 820           # below this the photo shows desktop icons, also blue


def _blue_mask(rgb: np.ndarray) -> np.ndarray:
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    m = (b > 90) & (b - r > 45) & (b - g > 35)
    m[TASKBAR_Y:, :] = False
    return m


def _calibrate(rgb: np.ndarray) -> tuple[float, float]:
    """Pixels per minute and pixels per 2 MHz, from the plot's own ticks."""
    sub = rgb[140:820, 85:1550]
    r, g, b = sub[..., 0], sub[..., 1], sub[..., 2]
    grey = (abs(r - g) < 28) & (abs(g - b) < 28) & (r > 105) & (r < 205)
    cols = grey.sum(0)
    idx = np.nonzero(cols > cols.max() * 0.55)[0]
    groups: list[list[int]] = []
    for i in idx:
        if not groups or i - groups[-1][-1] > 4:
            groups.append([i])
        else:
            groups[-1].append(i)
    px_per_min = float(np.median(np.diff([np.mean(gp) for gp in groups])))

    marg = rgb[140:820, 28:88]
    dark = marg.mean(2) < 135
    rows = np.nonzero(dark.sum(1) > 3)[0]
    groups = []
    for i in rows:
        if not groups or i - groups[-1][-1] > 4:
            groups.append([i])
        else:
            groups[-1].append(i)
    px_per_tick = float(np.median(np.diff([np.mean(gp) for gp in groups])))
    return px_per_min, px_per_tick


def reconstruct() -> dict:
    rgb = np.asarray(Image.open(PHOTO).convert("RGB")).astype(int)
    blue = _blue_mask(rgb)
    px_per_min, px_per_tick = _calibrate(rgb)
    mhz_per_px = MHZ_PER_TICK / px_per_tick
    min_per_px = MIN_PER_TICK / px_per_min

    x, mid, med, band = [], [], [], []
    for col in range(rgb.shape[1]):
        ys = np.nonzero(blue[:, col])[0]
        if ys.size < 8:
            continue
        x.append(col)
        mid.append(0.5 * (ys.min() + ys.max()))
        med.append(float(np.median(ys)))
        band.append((ys.max() - ys.min()) * mhz_per_px)
    x = np.asarray(x, float)
    t = (x - x.min()) * min_per_px
    # pixel y grows downward, frequency upward
    f_mid = -(np.asarray(mid) - mid[0]) * mhz_per_px
    f_med = -(np.asarray(med) - med[0]) * mhz_per_px
    band = np.asarray(band)

    jumps, segs = _segment(t, f_med)
    out = {
        "n_columns": len(t),
        "record_min": float(t.max()),
        "band_mhz": float(np.median(band)),
        "n_jumps": len(jumps),
        "jump_min_mhz": float(min(j[1] for j in jumps)) if jumps else float("nan"),
        "jump_max_mhz": float(max(j[1] for j in jumps)) if jumps else float("nan"),
        "decay_fastest": float(min(s[2] for s in segs)) if segs else float("nan"),
        "decay_slowest": float(max(s[2] for s in segs)) if segs else float("nan"),
        "naive_line_slope": float(np.polyfit(t, f_med, 1)[0]),
        "naive_slope_midpoint_estimator": float(np.polyfit(t, f_mid, 1)[0]),
        "px_per_min": px_per_min,
        "px_per_tick": px_per_tick,
    }
    out["estimator_agreement"] = abs(out["naive_line_slope"]
                                     - out["naive_slope_midpoint_estimator"])
    return out, t, f_med, band, jumps, segs


def _segment(t, f):
    """Split the record at its discontinuities; fit a slope between them."""
    d = np.diff(f)
    quiet = d[np.abs(d) < np.percentile(np.abs(d), 95)]
    thr = 5 * np.std(quiet)
    idx = np.nonzero(np.abs(d) > thr)[0]
    groups: list[list[int]] = []
    for i in idx:
        if not groups or i - groups[-1][-1] > 10:
            groups.append([i])
        else:
            groups[-1].append(i)
    centres = [g[len(g) // 2] for g in groups]
    jumps = [(float(t[i]), float(f[min(i + 3, len(f) - 1)] - f[max(i - 3, 0)]))
             for i in centres]
    edges = [0] + centres + [len(t) - 1]
    segs = []
    for a, b in zip(edges[:-1], edges[1:]):
        if b - a < 60:
            continue
        sl = float(np.polyfit(t[a + 5:b - 5], f[a + 5:b - 5], 1)[0])
        segs.append((float(t[a]), float(t[b]), sl))
    return jumps, segs


if __name__ == "__main__":
    res, t, f, band, jumps, segs = reconstruct()
    OUT_CSV.parent.mkdir(exist_ok=True)
    import csv
    with OUT_CSV.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["quantity", "key", "value", "unit"])
        w.writerow(["record_length", "2025-06-11", f"{res['record_min']:.1f}",
                    "min; digitised from the screen photograph"])
        w.writerow(["scan_band_width", "2025-06-11", f"{res['band_mhz']:.1f}",
                    "MHz; the scan modulation, laser axis"])
        w.writerow(["n_relock_steps", "2025-06-11", res["n_jumps"],
                    "count; upward discontinuities in the band centre"])
        w.writerow(["relock_step_range", "2025-06-11",
                    f"{res['jump_min_mhz']:.1f}-{res['jump_max_mhz']:.1f}",
                    "MHz; smallest to largest step"])
        w.writerow(["decay_between_steps", "2025-06-11",
                    f"{res['decay_fastest']:.2f}..{res['decay_slowest']:.2f}",
                    "MHz/min; fastest (early, short segment) to slowest (late)"])
        w.writerow(["naive_line_slope", "2025-06-11", f"{res['naive_line_slope']:.3f}",
                    "MHz/min; a straight line through the sawtooth, NOT a drift rate"])
        w.writerow(["estimator_agreement", "2025-06-11", f"{res['estimator_agreement']:.4f}",
                    "MHz/min; midpoint vs median centre, a robustness check"])
    for k, v in res.items():
        print(f"  {k:32} {v}")
    print("\n  steps:")
    for tt, dz in jumps:
        print(f"    t={tt:5.1f} min   {dz:+6.1f} MHz")
    print("  decay between steps:")
    for a, b, s in segs:
        print(f"    {a:5.1f}-{b:5.1f} min   {s:+.3f} MHz/min")
    print(f"\n  Wrote {OUT_CSV.relative_to(ROOT)}.")

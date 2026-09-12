#!/usr/bin/env python3
"""What an EOM depth ladder buys on the fitted waist, and what it costs to skip.

THE TERM THIS ATTACKS. The saturation companion is the one model term measured
to move the fitted transit width materially when it is not carried, and the
archive's waist is systematics-limited rather than statistics-limited, so the
term matters more than any amount of extra data.

WHY THE COMB IS THE RIGHT AXIS AND THE ONLY ONE. A phase modulation
redistributes the two-photon excitation among the teeth while leaving the total
intensity untouched, so every tooth sits at the SAME light shift, the same
collisional width, the same laser width and the same transit, and differs only
in Rabi frequency, which follows `J_k(2 beta)`. A power ladder cannot do this:
it moves the shift and the drive together. `build_world_trace` already carries
the law, keying the companion on `s0 * sqrt(rate)`.

THE LADDER IS THE ONE THE ARCHIVE'S OWN RULERS ADMIT, not the one the whole
comb suggests. `run_ruler_tooth_shares.py` measures a flat pedestal under the
comb that puts the third-order teeth below their own floor, so the usable
orders are 0, 1 and 2 and the span is about five in rate rather than about
seventy. This producer reads that CSV for the orders and the depth rather than
assuming either.

THE ARM THAT MATTERS IS THE ONE WITH gamma_l FROZEN, and the first cut of this
study got that wrong. A free Lorentzian width absorbs the saturation companion
one for one, so an arm that leaves it free returns a waist bias consistent with
zero whatever the truth is, and reads as showing the ladder unnecessary. The
dangerous condition, and the one the record's waist-only fits actually run, is
the waist alone free.

READS A COMMITTED CSV: `results/ruler_tooth_shares.csv`. Register A75 applies.

STATUS. Twin measurements of a design, so DIAGNOSTIC.
"""
import csv
import math
import os
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares
from scipy.special import jv

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from rb5s6s import config as _CFG                                  # noqa: E402
from rb5s6s.fullmodel import full_profile, saturation_companion_mhz  # noqa: E402
from rb5s6s.pmfmt import pm_cells                                  # noqa: E402

_CFG_RESULTS = _CFG.RESULTS_DIR

TRUTH = dict(gamma_coll=0.55, sigma_laser_fwhm=1.6, transit_fwhm=0.9575,
             gamma_l=0.40, s0=0.364)
OMEGA0 = 0.45
T_C, PEAK = 110.0, "4192"
NOISE = 0.004
NU = np.linspace(-25.0, 25.0, 1501)
N_TRIALS = int(os.environ.get("RF_LADDER_TRIALS", "300"))


def _usable_ladder():
    """Orders and depth from the committed ruler measurement, never assumed."""
    src = _CFG_RESULTS / "ruler_tooth_shares.csv"
    rows = list(csv.DictReader(src.open(encoding="utf-8")))
    cell = {r["quantity"]: r["value"] for r in rows}
    orders = tuple(int(k) for k in cell["usable_ladder_orders"].split(","))
    two_beta = float(cell["two_beta_with_pedestal"])
    # NORMALISE OVER THE PHYSICAL COMB, NOT OVER THE USABLE SUBSET. The first
    # cut divided by the sum over the three usable orders alone, which is
    # 0.6183 of the comb, so every share came out 1.617 times its physical
    # value and every tooth was driven at 1.272 times its real Rabi frequency:
    # a configuration no bench has. The teeth the pedestal excludes still carry
    # their share of the drive, so they belong in the denominator and not in
    # the ladder.
    all_orders = tuple(range(-3, 4))
    whole = float(sum(float(jv(k, two_beta)) ** 2 for k in all_orders))
    raw = np.array([float(jv(k, two_beta)) ** 2 for k in orders])
    return orders, two_beta, raw / whole


def _world(rates, rng):
    out = []
    for r in rates:
        y = full_profile(NU, peak=PEAK, T_C=T_C,
                         omega_mhz=OMEGA0 * math.sqrt(r), **TRUTH)
        y = r * y / y.max()
        out.append(y + rng.normal(0.0, NOISE * float(np.max(rates)), y.size))
    return out


def _resid(p, ys, rates, omega_fixed, gl_fixed):
    i = 0
    transit = float(p[i]); i += 1
    gl = float(gl_fixed) if gl_fixed is not None else float(p[i])
    if gl_fixed is None:
        i += 1
    om = float(omega_fixed) if omega_fixed is not None else float(p[i])
    if transit <= 0.01 or gl < 0.0 or om < 0.0:
        return np.full(sum(y.size for y in ys), 1e6)
    res = []
    kw = dict(TRUTH); kw["transit_fwhm"] = transit; kw["gamma_l"] = gl
    for y, r in zip(ys, rates):
        m = full_profile(NU, peak=PEAK, T_C=T_C,
                         omega_mhz=om * math.sqrt(r), **kw)
        A = np.column_stack([m, np.ones_like(m)])
        c, *_ = np.linalg.lstsq(A, y, rcond=None)      # amplitude and offset
        res.append(y - A @ c)
    return np.concatenate(res)


def _arm(rates, single, omega_fixed, gl_fixed):
    use = rates[:1] if single else rates
    got = []
    for t in range(N_TRIALS):
        rng = np.random.default_rng(5_300_000 + t)
        ys = _world(rates, rng)
        ys = ys[:1] if single else ys
        p0 = [TRUTH["transit_fwhm"] * 1.1]
        if gl_fixed is None:
            p0.append(TRUTH["gamma_l"] * 0.9)
        if omega_fixed is None:
            p0.append(OMEGA0 * 1.3)
        r = least_squares(_resid, p0, args=(ys, use, omega_fixed, gl_fixed),
                          method="lm", max_nfev=4000)
        got.append(float(r.x[0]))
    a = np.array(got)
    bias = float(a.mean()) - TRUTH["transit_fwhm"]
    sd = float(a.std(ddof=1))
    return (100.0 * bias / TRUTH["transit_fwhm"],
            100.0 * sd / math.sqrt(len(a)) / TRUTH["transit_fwhm"],
            100.0 * sd / TRUTH["transit_fwhm"])


def main() -> int:
    orders, two_beta, rates = _usable_ladder()
    comp = [saturation_companion_mhz(OMEGA0 * math.sqrt(r), PEAK) for r in rates]
    out = [["quantity", "arm", "value", "err", "note", "status"]]
    out.append(["ladder_rate_span", "", f"{rates.max() / rates.min():.2f}", "",
                f"over the orders {','.join(map(str, orders))} the archive's "
                f"rulers admit, at a depth of {two_beta}. At ONE light shift, "
                "which is what no power ladder can do", "DIAGNOSTIC"])
    out.append(["ladder_companion_span", "",
                f"{max(comp) / min(comp):.2f}", "",
                "the span in the saturation companion's own width across those "
                "teeth", "DIAGNOSTIC"])

    arms = (("one_tooth_waist_only", True, 0.0, TRUTH["gamma_l"]),
            ("ladder_waist_only_omega_free", False, None, TRUTH["gamma_l"]),
            ("ladder_waist_only_omega_pinned", False, OMEGA0, TRUTH["gamma_l"]),
            ("one_tooth_gamma_l_free", True, 0.0, None))
    for name, single, om, gl in arms:
        bias, se, sd = _arm(rates, single, om, gl)
        v, e = pm_cells(bias, se)
        note = {
            "one_tooth_waist_only":
                "the dangerous condition: one tooth, the waist alone free, the "
                "companion not modelled. This is the bias the ladder exists to "
                "remove",
            "ladder_waist_only_omega_free":
                "every usable tooth jointly with one shared Rabi frequency "
                "free. The bias is gone",
            "ladder_waist_only_omega_pinned":
                "the floor, with the Rabi frequency held at the truth. Matching "
                "the free arm says the ladder is not limited by its own "
                "precision on that term",
            "one_tooth_gamma_l_free":
                "why an arm with the Lorentzian width free measures nothing "
                "here: it absorbs the companion one for one and returns a bias "
                "consistent with zero whatever the truth is",
        }[name]
        out.append(["transit_bias_pct", name, v, e,
                    f"{note}. Per-trace scatter {sd:.4f} per cent over "
                    f"{N_TRIALS} trials", "DIAGNOSTIC"])

    dst = _CFG_RESULTS / "rf_saturation_ladder.csv"
    with open(dst, "w", newline="") as fh:
        csv.writer(fh, lineterminator="\n").writerows(out)
    print(f"ladder {orders} at 2 beta = {two_beta}, "
          f"rate span {rates.max() / rates.min():.2f}x")
    print(f"wrote {os.path.relpath(dst, REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

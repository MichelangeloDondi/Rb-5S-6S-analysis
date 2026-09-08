"""How linear the frequency axis must be, for the observable that reads a line's asymmetry.

THE QUESTION. The EOM ruler fixes the SCALE of the frequency axis. Its
linearity between anchors is a separate requirement, and nothing in this
repository said how tight it is. A sweep whose rate is not constant stretches
one side of a line against the other, which forges exactly the asymmetry the
third cumulant reads, so that channel sets a bar far above what a centre fit
needs.

THE PARAMETRISATION. Write the true frequency against the assumed axis as
nu = nuhat + alpha * nuhat^2, keeping the leading departure. The rate
d(nu)/d(nuhat) = 1 + 2 alpha nuhat then varies across a window of half-width W
by a fraction eps = 2 alpha W, and the distortion enters the profile at first
order in alpha, so the induced cumulant is linear in eps. The rows carry that
linearity as a measured check.

THE NONLINEARITY IS THE ACTUATOR'S AND NOT THE SCAN'S, and the first version
of this producer had it the other way. It defined the departure as a fraction
of the SPAN SCANNED, so a 200 MHz zoom of the same piezo read thirty times
worse than a 6 GHz sweep and the record refused the zoom on that ground. A
piezo's bow is a fraction of its TRAVEL: the same actuator scanned over a
sub-span at the same position has the same curvature and the same rate
variation across the same window. Here eta is the maximum departure from the
best-fit straight line as a fraction of the full travel T, and the scanned
span does not enter the rate variation at all. What a wide sweep buys is
anchors to MEASURE the bow, which is a different argument.

THE DILUTION LAW, ON RUNG 2. With the best-fit line removed and the departure
normalised to eta at the travel's ends, a quadratic bow is g = 6 x^2 - 1/2 on
x in [-1/2, 1/2], so nu = T x + eta T g, the rate is T (1 + 12 eta x), and
across a window of half-width W about the travel's centre it varies by
eps = 12 eta W / T exactly. The coefficient is twelve; an algebraic first pass
gave one and the producer's numerical value is reported beside the derived one.
A ripple of N cycles across the travel replaces the twelve by (2 pi N)^2 for
small eta, which is why a short-scale departure does not dilute.

A SWEEP THAT REVERSES HAS NO RATE VARIATION, and the first version reported
one. Its ripple row sampled three phases at which fifty cycles happened to sit
at the same point of the period, read 8.2 per cent, and called it position
independent; over a period the same ripple reverses the sweep in seventeen of
forty-one phases. The rate is now asserted positive across the whole window
and a reversing sweep returns NaN with the reversing fraction recorded.

THE TIGHT WAIST IS OUTSIDE THE MODEL'S LICENCE AND IS FLAGGED. `model_profile`
composes the line as a convolution, which the record holds at 40 microns and
wider and not below, and it carries neither the axial collection window nor
the saturation companion that move the 16 micron third cumulant at the factor
of three level. The 16 micron case is kept because the campaign proposes it,
with its status and note saying what it is, and a 40 micron case is the
campaign's licensed configuration.

Rung 2 for the forms and the coefficient; rung 3 for the tolerances, which
are read on the production estimator because the window truncation has no
closed form against this kernel.
Run: `python scripts/run_sweep_linearity.py` (about ten seconds)
"""
from __future__ import annotations

import csv

import numpy as np

from rb5s6s import config as C
from rb5s6s import constants as K
from rb5s6s.cumulants import windowed_cumulants
from rb5s6s.lineshape import model_profile

NU = np.linspace(-120.0, 120.0, 480001)
GAMMA_COLL = 0.55
SIGMA_LASER = 1.6
GAMMA_NAT = 3.49
GAMMA_COLL_BAND = (0.40, 0.70)
SIGMA_LASER_BAND = (1.2, 2.0)
# the actuator's full travel: the four-peak span the campaign sweeps
TRAVEL_MHZ = 6000.0
# (name, waist, on-axis shift at 225 mW, window half-width, inside the licence)
CASES = (("archive", 64e-6, 0.364, 6.0, True),
         ("campaign_40um", 40e-6, 0.932, 6.0, True),
         ("campaign_16um", 16e-6, 5.826, 12.0, False))


def _refuse_unless_isolated() -> None:
    """Refuse to run when the package does not resolve inside this script's own
    tree. A bare `python scripts/foo.py` from a clone puts scripts/ first on
    sys.path and the editable install then supplies the CANONICAL package, so
    the producer writes into the canonical checkout while believing itself
    isolated. Three readers did exactly that on 2026-09-07 and were saved by
    byte-identical output. Printing the path was the first form and it did
    not stop them. `realpath` on both sides, since /tmp is a symlink here."""
    import os as _os
    import rb5s6s as _pkg
    here = _os.path.realpath(_os.path.join(_os.path.dirname(__file__), _os.pardir))
    pkg = _os.path.realpath(_pkg.__file__)
    if not pkg.startswith(here + _os.sep):
        raise SystemExit(f"REFUSING: rb5s6s resolves to {pkg}, outside this tree {here}; "
                         f"set PYTHONPATH to this tree's root before running")


def induced_k3(eps, W, s0, transit, gamma_coll=GAMMA_COLL, sigma_laser=SIGMA_LASER):
    """The windowed third cumulant of a line read on a stretched axis."""
    alpha = eps / (2.0 * W)
    y = model_profile(NU + alpha * NU ** 2, gamma_coll=gamma_coll,
                      sigma_laser_fwhm=sigma_laser, transit_fwhm=transit,
                      s0=s0, gamma_nat_mhz=GAMMA_NAT, resolve_shift=True)
    v, info = windowed_cumulants(NU, y, W, (3,), centre0=0.0, baseline="wings")
    if not info["converged"] or not info.get("in_span", True):
        return float("nan")
    return float(v[3])


def _departure(shape, x, phase):
    if shape == "quadratic":
        g = x ** 2
    elif shape == "cubic":
        g = x ** 3
    elif shape.startswith("ripple"):
        g = np.sin(2 * np.pi * int(shape[6:]) * x + phase)
    else:
        raise ValueError(shape)
    A = np.vstack([np.ones_like(x), x]).T
    g = g - A @ np.linalg.lstsq(A, g, rcond=None)[0]
    return g / np.abs(g).max()


def rate_variation(shape, eta, W, x0_frac=0.0, phase=0.0, n=400001):
    """The fractional rate variation across a window, for a named departure of
    the ACTUATOR over its full travel; NaN where the sweep reverses inside the
    window, since a rate variation is then undefined."""
    x = np.linspace(-0.5, 0.5, n)
    nu = TRAVEL_MHZ * x + eta * TRAVEL_MHZ * _departure(shape, x, phase)
    r = np.gradient(nu, x)
    m = np.abs(x - x0_frac) <= W / TRAVEL_MHZ
    if r[m].min() <= 0:
        return float("nan")
    rc = float(np.interp(x0_frac, x, r))
    return float((r[m].max() - r[m].min()) / (2.0 * rc))


def ripple_over_phases(n_cycles, eta, W, n_phase=41):
    """Max and median rate variation over a period of phase, among the phases
    that keep the sweep monotone, and the reversing fraction. A maximum is a
    worst case and the median beside it is the spread the ratchet asks for."""
    vals, reversing = [], 0
    for ph in np.linspace(0, 2 * np.pi, n_phase, endpoint=False):
        v = rate_variation(f"ripple{n_cycles}", eta, W, 0.0, ph)
        if np.isfinite(v):
            vals.append(v)
        else:
            reversing += 1
    if not vals:
        return float("nan"), float("nan"), reversing / n_phase
    # a percentile and a median, never a bare maximum: the ratchet on worst
    # cases is right that a maximum over forty-one samples is the least stable
    # number a distribution has
    return float(np.percentile(vals, 95)), float(np.median(vals)), reversing / n_phase


def tolerance(W, s0, transit, real, gamma_coll=GAMMA_COLL, sigma_laser=SIGMA_LASER, n_iter=50):
    """The rate variation whose forged cumulant equals the light shift's own,
    bisected on a logarithmic bracket; a refused reading or a bracket edge is
    an error and not a number."""
    lo, hi = 1e-6, 1.0
    for _ in range(n_iter):
        mid = float(np.sqrt(lo * hi))
        f = induced_k3(mid, W, 0.0, transit, gamma_coll, sigma_laser)
        if not np.isfinite(f):
            raise RuntimeError(f"windowed cumulant refused at eps={mid:.3g}, W={W}")
        if abs(f) < abs(real):
            lo = mid
        else:
            hi = mid
    out = float(np.sqrt(lo * hi))
    if out < 3e-6 or out > 0.3:
        raise RuntimeError(f"tolerance {out:.3g} sits at the bracket's edge")
    return out


def _two_sig(err):
    """An uncertainty to two significant digits and the decimals it fixes."""
    d = int(np.floor(np.log10(err)))
    dec = max(0, 1 - d)
    return f"{err:.{dec}f}", dec


def main() -> int:
    _refuse_unless_isolated()
    rows = []

    def add(case, quantity, value, unit, basis, note, status):
        rows.append(dict(case=case, quantity=quantity, value=value, unit=unit,
                         basis=basis, note=note, status=status))

    for name, w0, s0, W, licensed in CASES:
        transit = K.transit_fwhm_from_w0(w0, 130.0)
        real = induced_k3(0.0, W, s0, transit)
        lic = ("inside the convolution licence" if licensed else
               "OUTSIDE the convolution licence: the model carries neither the "
               "axial collection window nor the saturation companion, which the "
               "record puts at the factor-of-three level on this cumulant here")
        add(name, "window_half_width", f"{W:.2f}", "MHz",
            "the analysis window this configuration is read at", lic, "DIAGNOSTIC")
        add(name, "k3_light_shift", f"{real:.6g}", "MHz^3",
            f"windowed third cumulant of the ramp at a {s0:.3f} MHz on-axis shift",
            "the signal any forged asymmetry is measured against. " + lic, "ENVELOPE")
        tol = tolerance(W, s0, transit, real)
        corners = []
        for gc in GAMMA_COLL_BAND:
            for sl in SIGMA_LASER_BAND:
                r_c = induced_k3(0.0, W, s0, transit, gc, sl)
                corners.append(tolerance(W, s0, transit, r_c, gc, sl, n_iter=34))
        tol_err = 0.5 * (max(corners) - min(corners))
        err_txt, dec = _two_sig(100.0 * tol_err)
        k3c = [induced_k3(0.0, W, s0, transit, gc, sl) for gc in GAMMA_COLL_BAND for sl in SIGMA_LASER_BAND]
        add(name, "rate_variation_tolerance_err", err_txt, "per cent",
            "half-span over both extremes of the collisional and laser width bands",
            "the tolerance FALLS as the line widens, since a wider line leaves less "
            "of its asymmetry inside a fixed window. The band is the line's own "
            "width uncertainty" + ("" if licensed else ", and not the factor of three above"),
            "ENVELOPE")
        add(name, "k3_light_shift_err", f"{0.5 * (max(k3c) - min(k3c)):.6g}", "MHz^3",
            "half-span over the same width corners", "moves the same way", "ENVELOPE")
        add(name, "rate_variation_tolerance", f"{100.0 * tol:.{dec}f}", "per cent",
            "the rate variation across the window whose forged third cumulant "
            "equals the light shift's own",
            {"archive": "a smooth bow of two parts in a thousand over the full travel "
                        "already reaches this, and two per cent exceeds it tenfold",
             "campaign_40um": "the campaign's tightest licensed waist",
             "campaign_16um": lic}[name], "ENVELOPE")
        a, b = induced_k3(1e-3, W, 0.0, transit), induced_k3(1e-2, W, 0.0, transit)
        add(name, "artefact_linearity_ratio", f"{b / a:.4f}", "dimensionless",
            "induced k3 at a 1 per cent rate variation over that at 0.1 per cent",
            "ten is the first-order form, derivable from the parametrisation", "DIAGNOSTIC")
        # the bow, at the travel's centre and at two positions
        for eta in (0.002, 0.02, 0.10):
            e0 = rate_variation("quadratic", eta, W, 0.0)
            add(name, f"eps_bow_eta{eta * 100:g}", f"{100.0 * e0:.4f}", "per cent",
                f"quadratic bow of {100 * eta:g} per cent of the full travel, window at the centre",
                f"derived 12 eta W / T = {100 * 12 * eta * W / TRAVEL_MHZ:.4f}. "
                f"margin against this case's tolerance {tol / e0:.2f}", "DIAGNOSTIC")
        e_edge = rate_variation("quadratic", 0.02, W, 0.4)
        add(name, "eps_bow_eta2_at_0.4_of_travel", f"{100.0 * e_edge:.4f}", "per cent",
            "the same bow read with the window at 0.4 of the travel",
            "the rate at that point is larger, so the fraction is smaller", "DIAGNOSTIC")
        # the sub-span invariance: the plant of the definition
        add(name, "eps_bow_eta2_subscan_200MHz_same_actuator",
            f"{100.0 * rate_variation('quadratic', 0.02, W, 0.0):.4f}", "per cent",
            "the same actuator scanned over 200 MHz at the same position and window",
            "identical to the full-travel value by construction: the scanned span "
            "does not enter a local rate variation", "DIAGNOSTIC")
        # ripples, over a period of phase, monotone only
        for ncyc, eta in ((8, 0.01), (50, 0.001), (50, 0.005)):
            mx, med, rev = ripple_over_phases(ncyc, eta, W)
            key = f"eps_ripple{ncyc}_eta{eta * 100:g}"
            add(name, key + "_p95_over_phase",
                f"{100.0 * mx:.4f}" if np.isfinite(mx) else "nan", "per cent",
                f"ripple of {ncyc} cycles across the travel at {100 * eta:g} per cent, "
                f"95th percentile over 41 phases of those that keep the sweep monotone",
                f"derived (2 pi N)^2 eta W / T = {100 * (2 * np.pi * ncyc) ** 2 * eta * W / TRAVEL_MHZ:.3f} "
                f"for small eta. Reversing fraction {rev:.2f}. Monotone needs eta below "
                f"{100 / (2 * np.pi * ncyc):.2f} per cent", "DIAGNOSTIC")
            add(name, key + "_median_over_phase",
                f"{100.0 * med:.4f}" if np.isfinite(med) else "nan", "per cent",
                "the same, at the median of the monotone phases",
                "the centre of the distribution the percentile above is drawn from", "DIAGNOSTIC")
        add(name, "dilution_coefficient_numerical",
            f"{rate_variation('quadratic', 0.10, W, 0.0) / (0.10 * W / TRAVEL_MHZ):.2f}",
            "dimensionless", "eps over eta W / T for a bow, on the grid",
            "twelve on rung 2, and the grid residue is the difference", "DIAGNOSTIC")

    dest = C.RESULTS_DIR / "sweep_linearity.csv"
    with open(dest, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["case", "quantity", "value", "unit", "basis", "note", "status"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"wrote {dest} with {len(rows)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

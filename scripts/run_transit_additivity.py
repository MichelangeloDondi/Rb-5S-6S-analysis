#!/usr/bin/env python3
"""How much of the guided transit width actually reaches the observed line.

WHY THIS FILE EXISTS, AND IT IS THE FIRST APPLICATION OF LOGIC 0d.2.

This quantity was wrong three times in one day, 2026-08-28, because it was a
hand-fitted literal with no producer:

  1. It was stated as "adds exactly", the retracted claim, for the life of the
     fibre model.
  2. It was corrected to "adds almost exactly", which is also false: the
     kernel's time function has no linear term at the origin, so it enters at
     SECOND order.
  3. It was then given a coefficient, `_SECOND_ORDER_C = 3.26`, fitted by
     convolving a SINGLE squared Lorentzian at the ensemble's FWHM. The
     ensemble is a MIXTURE of squared Lorentzians, and a mixture and a single
     component of the same FWHM have entirely different curvature at the
     origin, which is what the added width depends on.

LOGIC 0d.2 says a rule broken three times should have been a guard, and that
on the third breach the repair must be a mechanism. This is that mechanism.

THE PHYSICS, stated so the numbers below can be checked rather than trusted.

An atom crossing an evanescent field sees a two-sided exponential envelope in
TIME. The lineshape is the squared magnitude of its transform, a squared
Lorentzian, and the Maxwell average over speeds is a MIXTURE of those. The
mixture's time-domain function is

    g(t) = SUM_v w(v) (1 + |t|/tau_v) exp(-|t|/tau_v),   tau_v = Lambda/v

whose expansion is 1 - t^2/2tau^2 + |t|^3/3tau^3: NO LINEAR TERM. Linear at the
origin is exactly the property that makes Lorentzian widths add, so this kernel
enters the width quadratically, the way a Gaussian does, and contributes far
less than its own FWHM.

TWO CONSTRUCTIONS, AND THE SECOND IS A BOUND RATHER THAN A DUPLICATE. The
defect above survived because two computations disagreed and nothing compared
them, so this producer computes the added width twice. Route A convolves the
real profiles. Route B asks what a GAUSSIAN of the same curvature would add,
which is what the second-order description predicts if the kernel were
Gaussian-like near the origin.

They are NOT expected to be equal, and two earlier versions of this docstring
were wrong about how. The first said they should be equal. The second said
route B is a LOWER BOUND and quoted a gap of 7.5, 26 and 45 per cent across
the branches, "which orders exactly as the spread of tau does".

**That ordering was the ordering of a bug.** `_second_order_prediction`
averaged v^2 under s^k where the mixture's time-domain weight is s^(k+1), so
the two ensemble curvatures were understated by exactly 3/2 and 2, and the
spread being admired was those two factors. The weight was re-derived
on 2026-08-28 and the fingerprint was plain: the flux branch's wrong answer
equalled the speed branch's right one.

**Corrected, the routes agree to about a tenth on every branch and route B is
an UPPER bound, not a lower one.** The reason is not that curvature is a local
property, which would read the same way if the sign were positive. At fixed
second moment the two routes agree at LEADING order by construction: for a
narrow kernel the added width is linear in the kernel's second moment m2 with a
coefficient set by the BASE profile alone, and route B's Gaussian matches m2
identically. So the kernel's shape drops out at leading order and the gap IS
the first-order term, which is negative. That also predicts its size and its
ordering across branches.

**The coefficient is a property of the base and is not universal**, which an
earlier version of this docstring got wrong by quoting 3*m2/gamma as though it
were. In this file gamma is the Lorentzian FWHM, and the coefficient is about 6
for a Lorentzian base and 4*ln2 for a Gaussian one; the composite used here
gives about 5.5. The kernel-independence is the load-bearing part and it holds;
the number was mine and was out by roughly two.

**And the gap was not always negative, which the first account of this repair
got wrong.** Under the old weight it was -0.075 on single_velocity and +0.265
and +0.454 on the two ensemble branches. Exposing the sign alone would have
caught the first and passed the other two. Two independent errors held the
retired claim up, each concealing the other's signature, which is why the
ordering test passed as well.

The tests assert the agreement and the sign. Equality is not claimed, an
ordering across branches is no longer claimed, and a future error that inverts
the sign or breaks the second-order scaling cannot hide.

WHAT IT DOES NOT DO. It does not model the fitter. What a temperature ladder
recovers is the response of a FITTED Lorentzian parameter, and the transit
term is preferentially absorbed by the Gaussian channel at a correlation near
-0.94. This producer reports the added TOTAL width, which is an upper bound on
what the ladder sees, and says so in every note.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import math
import numpy as np
from scipy.integrate import quad
from scipy.special import gamma
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from _producer_lock import take_producer_lock          # noqa: E402
from rb5s6s import config as C                         # noqa: E402
from rb5s6s.constants import GAMMA_NAT_HZ              # noqa: E402
from rb5s6s.fibre import TRANSIT_KERNEL_FACTOR, transit_fwhm   # noqa: E402

OUT = C.RESULTS_DIR / "transit_additivity.csv"

KB = 1.380649e-23
M_RB87 = 86.909180527 * 1.66053906660e-27
# The 370 nm fibre's solved intensity decay length, from
# rb5s6s.fibre.solve_he11(370, 993.4181).intensity_decay_nm after the silica
# index was corrected to Malitson at the working wavelength (it read 397 under
# the wrong index). THE EXPONENTIAL ITSELF IS AN ENVELOPE CHOICE: methods
# chapter 9 section 9.1 shows the K1 field is not asymptotic at these radii,
# and matched on the second moment the effective length is about 274 nm, so
# every added width below UNDERSTATES by about (401/274)^2, about 2.1. The
# direction is conservative for the temperature-ladder lever, and carrying
# the solved profile through the kernel is the named open derivation.
LAMBDA_M = 400.8e-9
TEMPS_UK = (10.0, 20.0, 50.0, 100.0, 170.0)
GAMMA_L_EXTRA_MHZ = 0.398      # the twin's common Lorentzian component
SIGMA_G_MHZ = 0.30             # the twin's Gaussian laser contribution
BRANCHES = ("single_velocity", "ensemble_flux", "ensemble_speed")

def _fwhm(x: np.ndarray, y: np.ndarray) -> float:
    """Full width at half maximum, or a stated reason it has none.

    A first version handed `brentq` a bracket assuming the peak sat at the
    array centre and the profile fell below half inside the window. When that
    failed it raised scipy's "f(a) and f(b) must have different signs", which
    tells a reader nothing about which profile was malformed. This finds the
    crossings by scan and says what it saw.
    """
    y = np.asarray(y, dtype=float)
    y = y / y.max()
    c = int(np.argmax(y))
    right = np.nonzero(y[c:] < 0.5)[0]
    # A ONE-SIDED SPECTRUM HAS NO LEFT HALF. `rfftfreq` starts at zero, so a
    # symmetric profile peaks at index 0 and the width is twice the right-hand
    # crossing. The first version assumed a two-sided grid and reported the
    # absence of a left crossing as a malformed profile.
    if c == 0 and right.size:
        j = int(right[0])
        return 2.0 * brentq(lambda s: np.interp(s, x, y) - 0.5,
                            x[max(j - 1, 0)], x[j])
    left = np.nonzero(y[:c + 1] < 0.5)[0]
    if left.size == 0 or right.size == 0:
        raise ValueError(
            f"profile does not fall below half inside the window "
            f"[{x[0]:.4g}, {x[-1]:.4g}]: peak at {x[c]:.4g}, "
            f"edges {y[0]:.3g} and {y[-1]:.3g}. Widen the grid or check the "
            f"kernel, but do not widen the bracket and call it a width.")
    i, j = left[-1], c + right[0]
    lo = brentq(lambda t: np.interp(t, x, y) - 0.5, x[i], x[i + 1])
    hi = brentq(lambda t: np.interp(t, x, y) - 0.5, x[j - 1], x[j])
    return hi - lo


def _kernel_spectrum(nu_mhz, t_k, branch):
    """The kernel profile on a frequency grid, from the RECORD'S OWN integral.

    A first version built the mixture as a 1500-by-600001 array, which is 900
    million elements and does not finish. Worse, it reverse-engineered the
    Maxwell weight exponent instead of using the definition the package
    already states, which is how the speed branch came out wrong: its weight
    does not vanish at v -> 0, so a naive grid is dominated by arbitrarily slow
    atoms.

    So this uses `rb5s6s.fibre`'s own dimensionless form,

        I_k(b) = int_0^inf s^(4+k) exp(-s^2) / (s^2 + b^2)^2 ds

    with k = 1 for the flux weight and k = 0 for the speed weight, evaluated on
    a coarse b-grid and interpolated. Correct by construction against the
    committed factors rather than by a fitted exponent, and it finishes.
    """
    vp = np.sqrt(2 * KB * t_k / M_RB87)
    b = 2 * np.pi * np.abs(nu_mhz) * 1e6 * LAMBDA_M / vp
    if branch == "single_velocity":
        vbar = np.sqrt(8 * KB * t_k / (np.pi * M_RB87))
        x = (2 * np.pi * nu_mhz * 1e6 * (LAMBDA_M / vbar)) ** 2
        return 1.0 / (1.0 + x) ** 2
    k = {"ensemble_flux": 1, "ensemble_speed": 0}[branch]

    def integral(bb):
        return quad(lambda s: s ** (4 + k) * np.exp(-s * s)
                    / (s * s + bb * bb) ** 2, 0.0, np.inf, limit=400)[0]

    grid = np.concatenate([[0.0], np.geomspace(1e-4, max(b.max(), 1.0), 900)])
    vals = np.array([integral(g) for g in grid])
    return np.interp(b, grid, vals / vals[0])


def _second_order_prediction(t_k, branch, g_l_mhz, sigma_g_mhz):
    """THE SECOND ROUTE, and it is analytic rather than a second convolution.

    A first version built a time-domain mixture and compared two numerical
    convolutions. It disagreed with route A by a third on the ensemble
    branches, and the cause was not arithmetic: the slowest components have
    tau up to 9076 us at 10 uK against a 3000 us grid, so the function was
    truncated, and extending the grid far enough conflicts with resolving a
    4 MHz line. Two numerical routes sharing that tension check nothing.

    So this route tests the PHYSICS CLAIM instead. If the kernel enters at
    second order, its characteristic function near the origin is
    1 - t^2/(2 tau_eff^2) with 1/tau_eff^2 = <1/tau^2> = <v^2>/Lambda^2, which
    is a GAUSSIAN of that curvature. The added width is then the Voigt excess
    over the Lorentzian, from Olivero-Longbothum. Agreement with route A is
    evidence that the second-order description holds; disagreement says the
    kernel is not behaving quadratically and the whole claim is wrong.

    THE WEIGHT IS s^(k+1), NOT s^k, and getting that wrong is what this
    docstring said until 2026-08-28.

    The mixture is built in `_kernel_spectrum` as s^k exp(-s^2) times a
    PEAK-normalised squared Lorentzian, s^4/(s^2+b^2)^2. The transform of a
    peak-normalised component carries an extra factor s, because
    FT[1/(s^2+b^2)^2] goes as (1/s^3)(1+s|u|)exp(-s|u|) and the peak
    normalisation multiplies by s^4. So the weight that sets the curvature at
    the origin is s^(k+1) exp(-s^2), and

        <v^2> = vp^2 * G((k+4)/2)/G((k+2)/2), exact, no floor and no grid.

    The old form understated it by G((k+3)/2)G((k+2)/2)/(G((k+1)/2)G((k+4)/2)),
    which is 2/3 on the flux branch and 1/2 on the speed branch. The
    fingerprint was unmistakable once looked for: the flux branch's wrong
    answer equalled the speed branch's right one, an index shift of exactly
    one.
    """
    vp = np.sqrt(2 * KB * t_k / M_RB87)
    if branch == "single_velocity":
        vbar = np.sqrt(8 * KB * t_k / (np.pi * M_RB87))
        v2 = vbar ** 2
    else:
        k = {"ensemble_flux": 1, "ensemble_speed": 0}[branch]
        v2 = vp ** 2 * gamma((k + 4) / 2) / gamma((k + 2) / 2)
    tau_eff = LAMBDA_M / np.sqrt(v2)                    # s
    sigma_nu = 1.0 / (2 * np.pi * tau_eff) / 1e6        # MHz
    f_g = 2.0 * np.sqrt(2 * np.log(2)) * sigma_nu
    # the composite already carries a Gaussian; the kernel adds in quadrature
    f_g0 = 2.0 * np.sqrt(2 * np.log(2)) * sigma_g_mhz
    def voigt(fg):
        return 0.5346 * g_l_mhz + np.sqrt(0.2166 * g_l_mhz ** 2 + fg ** 2)
    return voigt(np.hypot(f_g0, f_g)) - voigt(f_g0)


def added_width_mhz(t_k: float, branch: str) -> tuple[float, float, float]:
    """(kernel FWHM, added width, added width by the second route), in MHz."""
    g_l = GAMMA_NAT_HZ / 1e6 + GAMMA_L_EXTRA_MHZ
    # --- route A: convolve profiles on a frequency grid
    nu = np.linspace(-30.0, 30.0, 600_001)
    lor = 1.0 / (1.0 + (2 * nu / g_l) ** 2)
    gau = np.exp(-nu ** 2 / (2 * SIGMA_G_MHZ ** 2))
    comp = np.convolve(lor, gau, "same")
    kern = _kernel_spectrum(nu, t_k, branch)
    base_a = _fwhm(nu, comp)
    tot_a = _fwhm(nu, np.convolve(comp, kern, "same"))
    # --- route B: the analytic second-order prediction, see above
    return (_fwhm(nu, kern), tot_a - base_a,
            _second_order_prediction(t_k, branch, g_l, SIGMA_G_MHZ))


def main() -> int:
    take_producer_lock("run_transit_additivity")
    rows = []

    def add(branch, quantity, value, unit, basis, note, status="ENVELOPE"):
        rows.append(dict(branch=branch, quantity=quantity, value=value,
                         unit=unit, basis=basis, note=note, status=status))

    # COMPUTED ONCE PER (branch, temperature) AND REUSED. A first version
    # recomputed each convolution up to three times -- once in the loop,
    # twice more in the spanned rows -- which took the producer past two
    # minutes. Recomputing a deterministic result is the plainest form of
    # the waste LOGIC 0d.4 names, and it was committed while implementing it.
    cache: dict[tuple[str, float], tuple[float, float, float]] = {}
    for branch in BRANCHES:
        for t_uk in TEMPS_UK:
            cache[(branch, t_uk)] = added_width_mhz(t_uk * 1e-6, branch)
            g_k, add_a, add_b = cache[(branch, t_uk)]
            # SIGNED, and it was read through abs() until 2026-08-28.
            # Positive means the convolution exceeds the curvature-matched
            # Gaussian; negative means the Gaussian overshoots.
            #
            # TWO INDEPENDENT ERRORS HELD THE FALSE CLAIM UP, and the first
            # account of this repair said only one did. Reconstructed from the
            # old committed rows: under the old velocity weight the SIGNED gap
            # was -0.075 on single_velocity but +0.265 and +0.454 on the two
            # ensemble branches. So abs() hid a negative on ONE branch, and the
            # wrong weight MANUFACTURED genuine positives on the other two.
            #
            # That matters for what this is filed under. Exposing the sign
            # alone would have failed on single_velocity and PASSED on the two
            # branches carrying the weight bug, and the retired ordering test
            # would still have passed, because 0.075 < 0.265 < 0.454. So this
            # is not simply another instance of a value read through abs(): it
            # is a coincidence of two errors, each of which concealed the
            # other's signature. A record filed under "expose the sign" would
            # not catch the next one.
            disagree = (add_a - add_b) / max(abs(add_a), 1e-12)
            add(branch, f"added_width_{t_uk:.0f}uK", round(add_a * 1e3, 4), "kHz",
                f"convolved with a {GAMMA_NAT_HZ/1e6 + GAMMA_L_EXTRA_MHZ:.4f} MHz "
                f"Lorentzian FWHM and a Gaussian of {SIGMA_G_MHZ} MHz "
                f"STANDARD DEVIATION, "
                f"{2*math.sqrt(2*math.log(2))*SIGMA_G_MHZ:.4f} MHz FWHM",
                "per-branch diagnostic. An UPPER BOUND on what a "
                "temperature ladder reads. The spanned row is the claim",
                "DIAGNOSTIC")
            add(branch, f"added_fraction_{t_uk:.0f}uK", round(add_a / g_k, 4),
                "fraction", f"added width over the kernel's own FWHM {g_k*1e3:.2f} kHz",
                "per-branch diagnostic. 1.0 would mean the kernel adds "
                "exactly, as a Lorentzian does, and it does not. The spanned "
                "row is the claim",
                "DIAGNOSTIC")
            add(branch, f"gaussian_curvature_gap_{t_uk:.0f}uK",
                round(disagree, 5),
                "fraction, signed", "the convolved width minus a Gaussian of "
                "the same curvature, over the convolved width",
                "per-branch diagnostic. Its SIGN is part of the answer and "
                "is negative on every branch: at fixed second moment the two "
                "routes agree at leading order by construction, so the gap IS "
                "the first-order term, which is negative. This module's "
                "docstring derives that and its size. The correction history "
                "is in docs/history/09_the-guided-geometry.md",
                "DIAGNOSTIC")
    # THE CLAIM IS THE SPAN, AND ITS WIDTH IS THE UNCERTAINTY. Protocol 8a.1
    # asks for an uncertainty or a stated reason there is none. There is one
    # here and it is not numerical: `docs/methods/09` says plainly that the
    # weighting is a model choice this record does not settle, so the fraction
    # is not one number but a band across the branches, and the band is what a
    # reader may quote.
    for t_uk in TEMPS_UK:
        fr = [cache[(b, t_uk)][1] / cache[(b, t_uk)][0] for b in BRANCHES]
        add("spanned", f"added_fraction_{t_uk:.0f}uK_band",
            f"{min(fr):.3f} to {max(fr):.3f}", "fraction",
            f"across {', '.join(BRANCHES)}, convolved with a "
            f"{GAMMA_NAT_HZ/1e6 + GAMMA_L_EXTRA_MHZ:.4f} MHz Lorentzian FWHM "
            f"and a Gaussian of {SIGMA_G_MHZ} MHz STANDARD DEVIATION, "
            f"{2*math.sqrt(2*math.log(2))*SIGMA_G_MHZ:.4f} MHz FWHM",
            "the fraction of its own FWHM the kernel contributes. The SPREAD "
            "is the uncertainty, because the velocity weighting is a model "
            "choice this record spans rather than settles")

    for t_uk in TEMPS_UK:
        w = [cache[(b, t_uk)][1] * 1e3 for b in BRANCHES]
        add("spanned", f"added_width_{t_uk:.0f}uK_band",
            f"{min(w):.2f} to {max(w):.2f}", "kHz",
            f"across {', '.join(BRANCHES)}, convolved with a "
            f"{GAMMA_NAT_HZ/1e6 + GAMMA_L_EXTRA_MHZ:.4f} MHz Lorentzian FWHM "
            f"and a Gaussian of {SIGMA_G_MHZ} MHz STANDARD DEVIATION, "
            f"{2*math.sqrt(2*math.log(2))*SIGMA_G_MHZ:.4f} MHz FWHM",
            "the width the kernel adds to the observed line. The SPREAD is the "
            "uncertainty, for the same reason as the fraction band: the "
            "weighting is spanned and not settled")

    # THE PRODUCER VALIDATES ITS OWN KERNEL AGAINST THE PACKAGE'S COMMITTED
    # FACTOR. Without this the file computes a self-consistent answer to a
    # question the record is not asking, which is how the defect it exists for
    # arose: a mixture was replaced by a single component and nothing compared
    # the result with `transit_fwhm`.
    for branch in BRANCHES:
        nu = np.linspace(-30.0, 30.0, 600_001)
        mine = _fwhm(nu, _kernel_spectrum(nu, 150e-6, branch))
        theirs = transit_fwhm(150e-6, LAMBDA_M, kernel=branch).fwhm_hz / 1e6
        add(branch, "kernel_fwhm_vs_package",
            round(abs(mine - theirs) / theirs, 5), "fraction",
            f"this file {mine*1e3:.2f} kHz against transit_fwhm "
            f"{theirs*1e3:.2f} kHz at 150 uK",
            f"TRANSIT_KERNEL_FACTOR[{branch!r}] = "
            f"{TRANSIT_KERNEL_FACTOR[branch]}. A disagreement here means this "
            "producer is not computing the record's own kernel, which is the "
            "defect it was built after",
            "DIAGNOSTIC")

    # the temperature exponent, per branch
    for branch in BRANCHES:
        a = np.array([cache[(branch, t)][1] for t in TEMPS_UK])
        p = np.polyfit(np.log(np.array(TEMPS_UK)), np.log(a), 1)[0]
        add(branch, "temperature_exponent", round(float(p), 4), "power of T",
            f"log-log slope of the added width over {min(TEMPS_UK):.0f} to "
            f"{max(TEMPS_UK):.0f} uK",
            "linear additivity would give 0.5, since Gamma_transit goes as "
            "sqrt(T). Second order gives 1. A design fitting a sqrt(T) column "
            "recovers an amplitude that is not the transit width")

    exps = []
    for branch in BRANCHES:
        a = np.array([cache[(branch, t)][1] for t in TEMPS_UK])
        exps.append(float(np.polyfit(np.log(np.array(TEMPS_UK)), np.log(a), 1)[0]))
    add("spanned", "temperature_exponent_band",
        f"{min(exps):.3f} to {max(exps):.3f}", "power of T",
        f"across {', '.join(BRANCHES)}, convolved with a "
            f"{GAMMA_NAT_HZ/1e6 + GAMMA_L_EXTRA_MHZ:.4f} MHz Lorentzian FWHM "
            f"and a Gaussian of {SIGMA_G_MHZ} MHz STANDARD DEVIATION, "
            f"{2*math.sqrt(2*math.log(2))*SIGMA_G_MHZ:.4f} MHz FWHM",
        "LINEAR ADDITIVITY WOULD GIVE 0.5 and second order gives 1. This band "
        "excludes 0.5 by a wide margin on every branch, which is the single "
        "number separating the retracted claim from the live one")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {OUT}  ({len(rows)} rows)")
    for r in rows:
        if r["quantity"].startswith("added_fraction_170"):
            print(f"  {r['branch']:16} fraction at 170 uK = {r['value']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

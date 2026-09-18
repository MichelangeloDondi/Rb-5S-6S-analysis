"""
Lineshape model kernels and convolution (module M3, physics core)
=================================================================

The two-photon line is a convolution of independent broadening mechanisms,
built on the TRANSITION (two-photon sum) frequency axis in MHz:

    I(nu) = A * [ Lorentzian(Gamma_nat + gamma_coll)      # homogeneous
                  (X) transit_kernel(w_transit; sqrt(T))  # Doppler-transit
                  (X) laser_kernel(sigma_laser)           # laser jitter x2
                  (X) stark_ramp(S0) ]                     # AC-Stark, per power
                + background

Design rules
------------
* Everything axis-independent lives here (kernels + convolution). The
  time->frequency conversion (per-block rate from M2) and the data fit live
  in the M3 fit module, so no calibration can leak into the physics.
* Homogeneous terms COMBINE analytically: the natural width and the
  collisional width are both Lorentzian, so they add in FWHM before any
  convolution (one Lorentzian of width Gamma_nat + gamma_coll), which is
  faster and exact.
* Fixed by physics, not fit: Gamma_nat (constants.GAMMA_NAT_HZ); the transit
  kernel SHAPE and its sqrt(T) scaling; the Stark ramp SHAPE (density
  f(s) ∝ s on [0, S0] (BLUE, the adopted Delta alpha being negative; O27),
  from the I^2-excitation / I-shift derivation).
  Free per condition: amplitude, center, background, gamma_coll, and (per
  block) sigma_laser; S0 is FIXED per power from the prediction in the
  archival fits (it is a MEASUREMENT only in the fixed-lock data).

Provenance of the transit kernel (ESTABLISHED, not phenomenological):
Biraben, Bassini & Cagnac, J. Phys. (Paris) 40, 445 (1979) derived the
finite-transit Doppler-free two-photon line as exactly a Lorentzian
convolved with a two-sided exponential exp(-|nu|/b) -- the central-cusp,
exponential-wing "double exponential". Borde, C. R. Acad. Sci. B 282, 341
(1976) is the earlier general treatment; K. K. Lehmann, J. Chem. Phys. 154,
104105 (2021) gives the modern closed form in the transit-time limit (hence
"Lehmann lineshape"), with 1/e half-width ~ sqrt(T)/w0. We use that two-sided
exponential here (transit_fwhm_at_T enforces the sqrt(T) law); transit_mc.py
refines it for our exact 3D-MB + w(z) + I^2 + collection conditions. The cusp
is the falsifiable signature the cold-dim corner tests (Voigt vs
Lorentzian(X)exp BIC) target -- so the kernel shape is deliberately NOT a
Gaussian. Full provenance: docs/LITERATURE.md section 3.
"""

from __future__ import annotations

from typing import Callable

import numpy as np

from ._compat import trapezoid
from .constants import (GAMMA_NAT_HZ, DELTA_ALPHA_AU, ATOMIC_POLARIZABILITY_SI,
                        EPS0_F_PER_M, C_M_PER_S, H_PLANCK_JS, LAMBDA_LASER_M)


#: THE SIDE OF THE LINE THE AC-STARK RAMP SITS ON, stated once (owner order O27, 2026-09-17): +1 for
#: the blue side, the density on [0, s0], because this record's differential polarizability is
#: negative. Every construction of the ramp outside `stark_ramp` reads it -- the benchmark moments
#: below, `ramp_transit`, `fringe_tail`'s mirror, the producers that build a textbook ramp -- so the
#: convention is one token and `tests/test_ramp_sign_convention.py` refuses a restatement of it and
#: a kernel that disagrees with it. It was restated in 46 lines of 29 files when the kernel flipped,
#: and four of the code sites kept the old side for hours (F90, F92).
RAMP_SIDE = +1.0


def ramp_mean_over_s0() -> float:
    """The triangle's mean in units of s0: +2/3 on the blue side, -2/3 on the red."""
    return RAMP_SIDE * 2.0 / 3.0


def ramp_kappa3(s0: float) -> float:
    """The triangle's third cumulant: -s0^3/135 on the blue side and its opposite on the red. Every odd
    cumulant flips with the side and every even one does not (kappa_4 = -s0^4/540 on both)."""
    return -RAMP_SIDE * float(s0) ** 3 / 135.0


# ---------------------------------------------------------------------------
# elementary profiles (all AREA-NORMALIzed to 1, argument nu in MHz)
# ---------------------------------------------------------------------------

GRID_STEPS_PER_KERNEL = 12.0
"""Convolution grid steps per narrowest kernel FWHM.

Named rather than inlined so a test can vary it: with the divisor written as a
literal in two places, nothing could build the same profile on a finer grid,
and there was no convergence test at all. Coarsening it to 4 shifted the
composite FWHM -- the quantity the beta_self and kappa regressions fit -- by
~0.1% with the whole suite green (mutation test, 2026-07-29). The synthetic
closure tests cannot catch that: they build their data with this same routine,
so a grid bias cancels exactly."""

GRID_STEP_FLOOR_MHZ = 1e-3
"""Absolute floor on the grid step, so a vanishing kernel width cannot explode
the grid. Where this floor binds, the divisor above has no effect."""


def lorentzian(nu: np.ndarray, fwhm: float) -> np.ndarray:
    """Area-normalized Lorentzian of full width at half maximum `fwhm`."""
    hwhm = 0.5 * fwhm
    return (hwhm / np.pi) / (nu ** 2 + hwhm ** 2)


def gaussian(nu: np.ndarray, fwhm: float) -> np.ndarray:
    """Area-normalized Gaussian of FWHM `fwhm`."""
    sigma = fwhm / (2.0 * np.sqrt(2.0 * np.log(2.0)))
    return np.exp(-0.5 * (nu / sigma) ** 2) / (sigma * np.sqrt(2.0 * np.pi))


def two_sided_exponential(nu: np.ndarray, fwhm: float) -> np.ndarray:
    """Area-normalized symmetric two-sided exponential exp(-|nu|/b), whose
    FWHM is 2*b*ln2. Central cusp = the transit-broadening signature."""
    b = fwhm / (2.0 * np.log(2.0))
    return np.exp(-np.abs(nu) / b) / (2.0 * b)


def stark_ramp(nu: np.ndarray, s0: float) -> np.ndarray:
    """Signal-weighted AC-Stark shift distribution: a triangular ramp with
    density f(s) ∝ s on s in [0, s0] (BLUE shifts), area-normalized on the
    grid. Derivation (cell and evanescent geometry alike): two-photon signal
    ∝ I^2, shift ∝ I, volume measure gives du/u, so dS/du ∝ u -> linear ramp.
    s0 > 0 is the on-axis (maximum) shift in MHz, and THE SIDE FOLLOWS THE
    ADOPTED POLARIZABILITY, which is the owner's ruling of 2026-09-17 (O27,
    in his words: "use the SSOT of 1131.8 +- 5.9"). A level shifts by
    dE = -alpha E^2 / 4, so a NEGATIVE differential polarizability moves the
    transition BLUE and the signal-weighted ramp carries its mass at positive
    detuning. This kernel was coded red-sided until that ruling, which is the
    side the cited +1093 a.u. implies and which this record does not adopt;
    tests/test_ramp_side_matches_the_polarizability.py asserts the agreement
    and was a strict xfail while the two disagreed. Every bound this record
    quotes is unaffected because it reads the magnitude. Returns a delta-like
    unit spike at nu=0 when s0 <= 0 (no shift).

    THE I^2 IS A WEAK-FIELD STATEMENT (2026-08-10). The signal weight above is
    the leading term of the excited fraction, not the fraction, and the real
    weight (s/2)/(1+s) reduces to I^2 only while the saturation parameter s is
    small. That is safe here and not safe everywhere: s carries the two-photon
    Rabi frequency squared, so it scales as the FOURTH power of the inverse
    waist while s0 scales only as the second. At the archive's 64 um convention
    and 225 mW s is 0.033. At the 16 um a future session proposes it is 8.5,
    and re-integrating the moments with the saturated weight moves the
    predicted axial skew from -0.36 to -1.07. The sign flip survives, the
    magnitude does not. scripts/run_geometry_design.ramp_moments computes both
    branches and its weak-field branch reproduces stark_ramp_axial_moments;
    docs/THEORY_NOTE.md sec 2.0a and figures/fig24_weak_field_limit.png.

    IMPLEMENTATION (fix, 2026-07-11): the original code dropped a
    grid-point spike for any s0 <= dnu, so the shape switched DISCONTINUOUSLY
    from ramp to spike — a false-minimum trap for any fit that floats s0
    (fixed-lock data will). Now: exact per-cell integrals of the ramp density
    (area exactly 1, continuous in s0 at every scale), plus a one-node
    first-moment transfer so the discrete mean equals the exact +2/3 s0 even
    when s0 is far below the grid step — d(profile)/d(s0) never dies."""
    dnu = nu[1] - nu[0]
    out = np.zeros_like(nu)
    if s0 <= 0:
        out[np.argmin(np.abs(nu))] = 1.0 / dnu
        return out
    # exact integral of f(s) = 2 s / s0^2 over each grid cell intersected
    # with the support [0, s0]:  F([a,b]) = (b^2 - a^2)/s0^2
    lo = np.clip(nu - 0.5 * dnu, 0.0, s0)
    hi = np.clip(nu + 0.5 * dnu, 0.0, s0)
    w = (hi ** 2 - lo ** 2) / s0 ** 2          # >= 0, sums to exactly 1
    # first-moment correction: move a little mass between adjacent nodes so
    # the discrete mean is exactly +(2/3) s0 (sub-grid shift information)
    mean = float(np.sum(nu * w))
    target = +(2.0 / 3.0) * s0
    j = int(np.argmax(w))
    eps = (mean - target) / dnu   # >0: move eps redward; <0: move |eps| blueward
    if 0.0 <= eps <= w[j] and j >= 1:
        w[j] -= eps
        w[j - 1] += eps
    elif eps < 0.0 and (-eps) <= w[j] and j + 1 < len(w):
        w[j] += eps
        w[j + 1] -= eps
    return w / dnu


def aperture_onaxis_factor(w0_m: float, a_m: float = None, f_m: float = None,
                           lam_m: float = LAMBDA_LASER_M) -> float:
    """The on-axis focal intensity per RECORDED watt of a Gaussian clipped by a circular bore of
    radius `a_m` ahead of a lens of focal length `f_m`, relative to the unclipped beam.

    The input radius at the lens is w = lam f / (pi w0) for a focus w0; the clipped field's
    on-axis amplitude at the focus integrates the truncated Gaussian, (1 - e^{-a^2/w^2}), and the
    power meter reads BEHIND the cell, so the recorded power is the transmitted one,
    (1 - e^{-2 a^2/w^2}). Hence factor = (1 - e^{-a^2/w^2})^2 / (1 - e^{-2 a^2/w^2}), rung 2 (a
    closed form, F39, 2026-09-17, the thesis session's aperture harness): 0.716 at 42.4 um, 0.876 at
    52.1, 0.967 at 64 and 0.994 at 76. WHAT IT IS: the leading, on-axis part of the DIFFRACTION of
    the clipped focus, not a bookkeeping of the recorded watt (the transmission alone is 0.03 per
    cent at 64 um); the profile part of the same term (the side lobes, the effective M2, the change
    in the transit kernel and in the ramp's f(s)) is the deferred `eom_aperture` term, and the
    width channel's bound reads the SPREAD of the shift distribution under the rate weighting,
    which a clipped focus moves by a factor that differs from this one, appreciably below about
    50 um. It scales the light shift's S0 per recorded watt and the S0-to-delta-alpha conversion
    at every waist as a first correction; it is NOT yet inside `stark_shift_S0_mhz`, which the
    re-run wave wires with the whitening's correlation time (F36), so no committed cell moves
    before that wave lands.
    """
    from .constants import EOM_APERTURE_RADIUS_M, DRIVE_LENS_F_M
    a = EOM_APERTURE_RADIUS_M if a_m is None else float(a_m)
    f = DRIVE_LENS_F_M if f_m is None else float(f_m)
    w0 = np.asarray(w0_m, dtype=float)
    w = float(lam_m) * f / (np.pi * w0)
    x = a * a / (w * w)
    out = (1.0 - np.exp(-x)) ** 2 / (1.0 - np.exp(-2.0 * x))
    return float(out) if out.ndim == 0 else out


#: A draw of this size or smaller is evaluated exactly; above it the nodes-and-interpolate
#: path runs, with its bound asserted on every call (2026-09-17).
_SPREAD_EXACT_MAX = 64
_SPREAD_NODES = 257
_SPREAD_INTERP_TOL = 1e-6


def aperture_spread_factor(w0_m: float, a_m: float = None, f_m: float = None,
                           lam_m: float = LAMBDA_LASER_M,
                           n_r: int = 1200, n_rho: int = 600) -> float:
    """The factor by which the clipped focus changes the SPREAD of the light-shift distribution
    under the two-photon rate weighting, relative to the unclipped Gaussian at the same recorded
    power: what the width channel's bound reads, against `aperture_onaxis_factor`, which is what the
    on-axis shift reads (F39, reproduced here to 0.3 per cent against an independent quadrature).

    The Fraunhofer focal field of the Gaussian truncated at the bore, E(rho) = int_0^a
    e^{-r^2/w^2} J0(k r rho / f) r dr, its intensity normalised to the transmitted power; the shift
    goes as I and the rate as I^2, so the rms shift is sqrt(<I^4>/<I^2> - (<I^3>/<I^2>)^2) over the
    focal plane. Unclipped, that rms over the peak is 1/sqrt(18) = 0.2357, the test's anchor. Rung
    3 by quadrature, the focal plane only: the axial collection window and the kernel changes are
    the deferred profile part. 0.70 at 42.4 um, 0.86 at 52.1, 0.96 at 64, 0.99 at 76; F over the
    on-axis factor is 0.974, 0.982, 0.992 and 0.998, so the on-axis shortcut overstates the width
    channel's factor by 0.8 per cent at 64 um and 2.6 at 42.4.
    """
    from scipy.special import j0
    # A GRID OF WAISTS IS A GRID OF QUADRATURES, not a broadcast: the focal field is built on its
    # own radial grid per waist, so this maps rather than vectorises. Wired without it on
    # 2026-09-17, the producer of the polarizability posterior passes its whole waist grid here and
    # died on `float()` of an array, leaving `delta_alpha_posterior.csv` holding its header alone
    # (F57, and the fourteen dangling references that is how it surfaced).
    if np.ndim(w0_m) > 0:
        w = np.asarray(w0_m, dtype=float)
        if w.size <= _SPREAD_EXACT_MAX:
            return np.array([aperture_spread_factor(float(x), a_m, f_m, lam_m, n_r, n_rho)
                             for x in w])
        # A MONTE CARLO DRAW IS NOT A GRID. `run_delta_alpha_posterior.py` passes 200 000 prior
        # draws of the waist, and one quadrature is 29 ms, so mapping over them is 1.6 hours for a
        # function that is smooth and monotone in w0. Evaluated on nodes and interpolated it is
        # eight seconds. The interpolation is ASSERTED and not assumed: three interior probes are
        # compared against the exact quadrature and the call raises rather than returning a
        # silently interpolated number if the bound is missed.
        lo, hi = float(w.min()), float(w.max())
        if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
            return np.full(w.shape, aperture_spread_factor(lo, a_m, f_m, lam_m, n_r, n_rho))
        nodes = np.linspace(lo, hi, _SPREAD_NODES)
        vals = np.array([aperture_spread_factor(float(x), a_m, f_m, lam_m, n_r, n_rho)
                         for x in nodes])
        for frac in (0.25, 0.5, 0.75):
            x = lo + frac * (hi - lo)
            exact = aperture_spread_factor(x, a_m, f_m, lam_m, n_r, n_rho)
            got = float(np.interp(x, nodes, vals))
            if abs(got - exact) > _SPREAD_INTERP_TOL:
                raise ValueError(
                    f"aperture_spread_factor: interpolation over [{lo:.3e}, {hi:.3e}] missed its "
                    f"bound at w0={x:.3e} ({got:.6f} against {exact:.6f}); widen _SPREAD_NODES "
                    f"or call scalar-wise")
        return np.interp(w, nodes, vals)
    from .constants import EOM_APERTURE_RADIUS_M, DRIVE_LENS_F_M
    a = EOM_APERTURE_RADIUS_M if a_m is None else float(a_m)
    f = DRIVE_LENS_F_M if f_m is None else float(f_m)
    w_in = float(lam_m) * f / (np.pi * float(w0_m))
    k = 2.0 * np.pi / float(lam_m)
    rho = np.linspace(0.0, 4.0 * float(w0_m), n_rho)

    def _spread(rmax):
        r = np.linspace(0.0, rmax, n_r)
        E = np.array([trapezoid(np.exp(-r * r / w_in ** 2) * j0(k * r * p / f) * r, r) for p in rho])
        I = E * E
        I = I / trapezoid(I * 2.0 * np.pi * rho, rho)
        m2 = trapezoid(I ** 2 * 2.0 * np.pi * rho, rho)
        m3 = trapezoid(I ** 3 * 2.0 * np.pi * rho, rho)
        m4 = trapezoid(I ** 4 * 2.0 * np.pi * rho, rho)
        return float(np.sqrt(m4 / m2 - (m3 / m2) ** 2)), float(I[0])

    s_clip, _ = _spread(a)
    s_open, _ = _spread(6.0 * w_in)
    return s_clip / s_open


def stark_shift_S0_mhz(power_w: float, w0_m: float, rho: float = 1.0,
                       delta_alpha_au: float = DELTA_ALPHA_AU) -> float:
    """On-axis maximum AC-Stark shift S0 of the two-photon line (TRANSITION
    axis, MHz), under the pinned standard convention (constants.DELTA_ALPHA_AU):

        dE_i = -(1/4) alpha_i E0^2 = -alpha_i I / (2 eps0 c)     [<E^2>=E0^2/2]
        S0   = Delta_alpha * I_eff / (2 eps0 c h),
        I_eff = (1+rho) * 2 P / (pi w0^2)   (time-averaged fwd+retro, no x2).

    rho = retro power ratio (1.0 = perfect retro). Returns S0 >= 0 always,
    the DEPTH of the shift; its direction is the sign of Delta_alpha, which
    this record computes negative, a blue shift. Laser-axis value is S0/2. This is the coefficient
    the fixed-lock mean-pull-vs-power fit measures (inverted to give
    Delta_alpha); the archival ramp SHAPE does not depend on it."""
    i_eff = (1.0 + rho) * 2.0 * power_w / (np.pi * w0_m ** 2)
    # S0 is the ramp's DEPTH, a magnitude, which is how every consumer
    # uses it: the ramp runs on [0, S0], every bound here is one-sided
    # positive, and every fit bounds S0 >= 0. The docstring above has
    # always defined it with |dE_6S - dE_5S|; the implementation dropped
    # the modulus and agreed only while Delta_alpha happened to be
    # positive. The DIRECTION of the shift lives in Delta_alpha's sign
    # (negative here, so a blue shift), not in this magnitude.
    d_alpha = abs(delta_alpha_au) * ATOMIC_POLARIZABILITY_SI
    s0_hz = d_alpha * i_eff / (2.0 * EPS0_F_PER_M * C_M_PER_S * H_PLANCK_JS)
    return s0_hz / 1e6


def composite_profile(gamma_coll: float, sigma_laser: float,
                      transit_fwhm: float, laser_kind: str = "gaussian",
                      transit_kind: str = "exp", *, gamma_l: float = 0.0):
    """Fast no-Stark composite on a self-sized grid: Lorentzian(Gamma_nat +
    gamma_coll) (X) laser kernel (X) transit kernel, area-normalized.
    Returns (grid, profile). This is the shared kernel of the beta_self and
    global fits (S0 is fixed/negligible in the archival width fits; centre fits on
    fixed-lock data use model_profile with the ramp instead). Moved here from
    beta.py (2026-07-11): composite lineshapes belong in the
    lineshape module, not in one consumer.

    transit_kind selects the MODEL FORM for the transit contribution and is the
    knob for the Voigt-vs-Lehmann model-form systematic on beta_self (M4c/M8):
    'exp' = the Biraben-Cagnac two-sided exponential (the cusp, the Lehmann
    form, default); 'gaussian' = a Gaussian of the same FWHM, which makes the
    whole line a pure Voigt (no cusp). Running the global fit under both and
    differencing beta gives the model-form error bar the paper must quote."""
    # A LORENTZIAN LASER KERNEL IS ADDED, NOT CONVOLVED (2026-08-20).
    # Two Lorentzians of FWHM a and b convolve to one of FWHM a+b exactly, so
    # a Lorentzian laser width belongs in `homog` rather than in a second
    # convolution. This is not an optimisation. Done by convolution on a
    # finite grid the Lorentzian tails are truncated, and the truncation
    # depends on the SPAN, which depends on how a given total width is SPLIT
    # between the two widths. That made the profile depend on the split at up
    # to 3.7e-3 of peak where the continuum identity says it cannot depend on
    # it at all: a numerically manufactured separability pointing along
    # exactly the direction any laser-width inference has to measure. Against
    # the archive's own noise over ~1e4 points per condition that artefact
    # carries up to 70-sigma matched-filter leverage, so it could not be
    # assumed small. Addition removes it identically -- the profile is
    # invariant under sum-preserving changes of the split to machine zero --
    # and costs one convolution less. results/kernel_identifiability.csv measures it.
    # THE MIXED G+L KERNEL (2026-08-21). gamma_l is a SECOND, LORENTZIAN laser
    # component carried alongside the Gaussian one, so the laser kernel can be
    # G, L, or both at once, which is what the identifiability question needs.
    # It is ADDED into homog for the same exact reason the lorentzian arm is:
    # Lorentzians of FWHM a and b convolve to one of FWHM a+b identically, so
    # the sum is the only quantity a fit can see and imposing it removes the
    # discretisation artefact rather than measuring it. gamma_l = 0.0 is the
    # default and is BIT-IDENTICAL to the pre-change module: adding an exact
    # zero is a no-op in IEEE arithmetic, and tests/test_gamma_l_identity.py
    # asserts that against a snapshot rather than trusting the argument.
    if laser_kind not in ("gaussian", "lorentzian"):
        raise ValueError(
            f"laser_kind={laser_kind!r} is neither 'gaussian' nor "
            f"'lorentzian'. This selector used to treat any other "
            f"string as Lorentzian, so a typo chose a MODEL FORM "
            f"silently, which is the systematic this record spends its "
            f"kernel chain measuring.")
    # DELIBERATELY NOT _kernel_widths: this path clamps negative collisional and
    # laser widths, which the model's own path does not (both clamp gamma_l), so
    # unifying them would change behaviour on
    # clamped inputs (absent kernels are excluded from the grid step in both:
    # here when `widths` is built, and in the model's path one level down in
    # model_grid_step_mhz, not in _kernel_widths itself) (2026-09-04).
    _lorentz_laser = laser_kind != "gaussian"
    homog = (GAMMA_NAT_HZ / 1e6 + max(gamma_coll, 0.0) + max(gamma_l, 0.0)
             + (max(sigma_laser, 0.0) if _lorentz_laser else 0.0))
    # ONLY KERNELS THAT ARE PRESENT MAY SET THE GRID STEP (2026-08-21). The
    # step is min(widths)/N, and an ABSENT kernel floored to 1e-6 becomes that
    # minimum, driving the step to its floor and the grid to ~2e5 points for a
    # line that needs ~2e3. Harmless while every kernel was always present,
    # live the moment the sigma_G -> 0 submodel above became reachable. The
    # scratch reimplementation in run_kernel_identifiability.py had already
    # identified this and worked around it privately; the fix belongs here.
    # Bit-identical wherever both widths are positive, which is every
    # committed call: max(x, 1e-6) == x for the MHz-scale widths this record
    # uses, so only the previously pathological cases move.
    widths = ([homog]
              + ([] if (_lorentz_laser or sigma_laser <= 0.0)
                 else [max(sigma_laser, 1e-6)])
              + ([max(transit_fwhm, 1e-6)] if transit_fwhm > 0.0 else []))
    span = 6.0 * (sum(widths) + max(widths)) + 5.0
    dnu = max(min(widths) / GRID_STEPS_PER_KERNEL, GRID_STEP_FLOOR_MHZ)
    n = int(np.ceil(span / dnu))
    g = np.arange(-n, n + 1) * dnu
    prof = lorentzian(g, homog)
    # THE sigma_G -> 0 LIMIT MUST BE REACHABLE (2026-08-21). gaussian() divides
    # by sigma, so convolving with sigma_laser = 0 returned an all-nan profile.
    # That corner is not exotic: it IS the pure-Lorentzian model, which is the
    # nested submodel of the mixed G+L kernel, so the model could not evaluate
    # its own submodel and any nested likelihood-ratio comparison against it
    # would have propagated nan rather than failing loudly. A zero-width
    # Gaussian is a delta function and convolution with it is the identity, so
    # skipping the convolution IS the correct limit, not a guard against it.
    # Nothing committed changes: the only values affected were nan.
    if not _lorentz_laser and sigma_laser > 0.0:
        prof = np.convolve(prof, gaussian(g, sigma_laser), "same") * dnu
    # THE transit -> 0 LIMIT MUST BE REACHABLE (2026-08-22), for the same
    # reason and by the same argument as the sigma_G -> 0 limit above.
    # two_sided_exponential() and gaussian() both divide by their width, so
    # convolving with a zero-width transit returned an all-nan profile. The
    # GRID construction above already excludes an absent transit, so the two
    # halves of this function disagreed about whether the kernel could be
    # absent, and only the half that could produce nan was unguarded. A
    # zero-width kernel is a delta function and convolution with it is the
    # identity, so skipping it IS the correct limit rather than a guard
    # against it. Reached first by the fibre twin, whose near-Lorentzian
    # transit is carried inside the additive Lorentzian channel to the
    # accuracy that approximation holds, needing no separate transit kernel. Nothing committed changes: fit_transit=False pins
    # the width at TRANSIT_FWHM_PLACEHOLDER_MHZ, so no committed call reaches
    # zero, and the only values affected were nan.
    if transit_fwhm > 0.0:
        tk = (two_sided_exponential(g, transit_fwhm) if transit_kind == "exp"
              else gaussian(g, transit_fwhm))
        prof = np.convolve(prof, tk, "same") * dnu
    area = trapezoid(prof, g)
    return g, (prof / area if area > 0 else prof)


def stark_ramp_axial(nu: np.ndarray, s0: float, z_ratio: float,
                     n_photon: int = 2) -> np.ndarray:
    """Diverging-beam generalization of stark_ramp (PLAN §6;
    revision 2026-07-12 #3): the observed shift distribution when the
    collection volume spans an axial window |z| <= Z around the focus of a
    Gaussian beam with Rayleigh range z_R.  z_ratio = Z / z_R.

    Quasi-static derivation. At axial position zeta = z/z_R the transverse
    law is the |s|^(n-1) ramp with edge S(zeta) = s0/(1+zeta^2), and the
    per-z signal weight is w^2(z) I0(z)^n ∝ (1+zeta^2)^(1-n). The weight
    exactly cancels the local ramp normalization S(zeta)^n up to
    (1+zeta^2)^1, leaving the closed form (any n):

        f(s) ∝ |s|^(n-1) * [ zeta_m + zeta_m^3 / 3 ],
        zeta_m(s) = min( z_ratio, sqrt(s0/|s| - 1) )

    on s in [0, s0] (BLUE; O27). z_ratio -> 0 recovers the pure transverse law
    (triangle for n=2); the hard edge at +s0 softens to zero (only the
    focal plane reaches the full shift). Uniform collection weight is
    assumed on the window — replace with the measured collection profile
    in a fixed-lock session before quoting coefficients (OPEN)."""
    dnu = nu[1] - nu[0]
    if s0 <= 0:
        out = np.zeros_like(nu)
        out[np.argmin(np.abs(nu))] = 1.0 / dnu
        return out
    # integrate the closed-form density over each grid cell (8-point
    # midpoint sub-sampling; the density is bounded and piecewise smooth)
    lo = np.clip(nu - 0.5 * dnu, 0.0, s0)
    hi = np.clip(nu + 0.5 * dnu, 0.0, s0)
    sub = (np.arange(8) + 0.5) / 8.0
    s_sub = lo[:, None] + (hi - lo)[:, None] * sub[None, :]   # (ncell, 8)
    a = np.abs(s_sub)
    with np.errstate(divide="ignore", invalid="ignore"):
        zm = np.sqrt(np.maximum(s0 / np.where(a > 0, a, np.inf) - 1.0, 0.0))
    zm = np.minimum(zm, z_ratio)
    dens = a ** (n_photon - 1) * (zm + zm ** 3 / 3.0)
    w = dens.mean(axis=1) * (hi - lo)
    total = w.sum()
    if total <= 0:   # s0 far below the grid: degenerate to the spike
        out = np.zeros_like(nu)
        out[np.argmin(np.abs(nu))] = 1.0 / dnu
        return out
    return w / total / dnu


def local_ramp_density(x: np.ndarray, n_photon: int = 2) -> np.ndarray:
    """The transverse law on the dimensionless shift x = s/S: n x^(n-1) on
    [0, 1], area one; the local density every axial mixture starts from.

    BLUE-SIDED since O27: the adopted Delta alpha is negative, so the shift
    carries its mass at positive detuning. |x| is kept in the power so the
    law reads the same for either support."""
    x = np.asarray(x, float)
    inside = (x >= 0.0) & (x <= 1.0)
    return np.where(inside, n_photon * np.abs(x) ** (n_photon - 1), 0.0)


def trapped_ramp_density(x: np.ndarray, eta: float, n_photon: int = 2) -> np.ndarray:
    """The same law for atoms TRAPPED by the light that shifts them.

    A free atom crosses the beam and samples the intensity geometrically, which
    is `local_ramp_density`. A trapped atom sits in the potential the same light
    makes, so it samples the intensity with a Boltzmann weight and the density
    gains `exp(eta |x|)` with ``eta = U0 / kT`` the trap depth over the sample
    temperature -- `platforms.trap_eta` returns it. Normalised to area one on
    [0, 1] (BLUE; O27), so it drops into `build_world_trace(fringe_density=...)` and into
    `ramp_mixture` wherever the free law goes.

    ``eta = 0`` returns `local_ramp_density` exactly: an untrapped sample is the
    limit and not a separate model. At large ``eta`` the atoms sit at the bottom
    of the well where the intensity is highest, the mean of |x| tends to
    1 - 1/eta, its spread to 1/eta and its skewness to -2, so a deep trap turns
    the ramp's broad asymmetric weight into a narrow one near full shift.

    FAILURE MODE: called with a KINETIC temperature that is not the trapped
    sample's, `eta` is wrong and the whole weight with it; and a check of the
    eta -> 0 limit that only tests eta = 0 cannot fail, since exp(0) = 1 for any
    exponent, so the guard probes small non-zero eta as well.
    """
    x = np.asarray(x, float)
    eta = float(eta)
    inside = (x >= 0.0) & (x <= 1.0)          # BLUE; O27, as local_ramp_density
    u = np.abs(x)
    w = np.where(inside, u ** (n_photon - 1) * np.exp(eta * u), 0.0)
    area = trapezoid(w, x)
    return w / area if area > 0.0 else w


def saturated_ramp_density(x: np.ndarray, power_w: float, w0_m: float, T_C: float,
                           rho: float = 0.94, n_table: int = 240) -> np.ndarray:
    """The transverse shift law WITH SATURATION: p_sat(x) proportional to G(P x) / x on [0, 1].

    DERIVATION (F133, 2026-09-17, the physics rung). The shift at a point is s = S0 x with x the local
    intensity in units of the peak, and the excitation weight is the rate at the local power, G(P x).
    In the weak field G goes as the square of the power, so the weight is x^2, and with the Gaussian
    beam's own area element r dr = -(w^2/4) dx/x the density is 2x on [0, 1]: `local_ramp_density`,
    the triangle with mean 2/3 S0 and third cumulant -S0^3/135 (`ramp_kappa3`). Saturation changes
    ONLY the weight, so the same algebra gives G(P x)/x, one quadrature over the package's own rate
    `platforms.excitation_rate_per_atom` (tabulated log-log on `n_table` points as the kernel Monte
    Carlo tabulates it, then interpolated), area-normalised. G(P x) -> 0 as x^2, so the density is
    exactly 0 at x = 0 and the grid may start there. S0 cancels out of every dimensionless ratio.

    WHAT IT WAS MEASURED TO DO. Against 813 kernel Monte Carlo nodes the ratio k3_sat / k3_weak of this
    density agrees with the Monte Carlo's own to a median of 0.0000 and a worst of 0.0382 (40 um,
    225 mW); it takes the gate's `ramp_k3_rel` reading at that node from 0.1534 to 0.0478 and brings
    39 of 39 nodes of the 40 to 46 um band under the 0.05 tolerance (F133). In the weak field
    (P -> 0) it returns the triangle: `tests/test_saturated_ramp.py` asks for 1e-6.

    ITS STATED ERROR, MEASURED AGAINST THE EXACT FORM AND NOT AGAINST THE MONTE CARLO (the physics
    chair, 2026-09-18). The derivation is TRANSVERSE: one rate table at the on-axis power. The gate's
    reference is the AXIAL mixture (`ramp_mixture` at the node's z_ratio), where the local peak power
    falls as 1/(1 + zeta^2) along the column and the saturation with it. Because the rate depends on the
    absolute local intensity alone, that mixture HAS a one-line closed form,

        f(s) proportional to G(P s / S0) / s * [zeta_m + zeta_m^3 / 3],  zeta_m = min(Z, sqrt(S0/s - 1)),

    and the path here instead applies the weak-field zeta weight to a density saturated at the on-axis
    power, which coincides with it only where G goes as the square of the power. Against that exact form
    the shipped factorisation reads 1.9 per cent low in the third cumulant at z_ratio 0.667 and 1.3 per
    cent at 0.5. **The 4 per cent and the "under 0.3 per cent at 0.5" this docstring carried until
    2026-09-18 were F133a's TRANSVERSE residual against the Monte Carlo, measured with no mixture at all,
    and the second was wrong by four times in the unsafe direction.** The exact form is the named
    refinement and it is queued as `saturated-mixture-exact-form`; the agreement the gate records at the
    node (0.44 per cent) is partly a cancellation, the factorisation sitting 1.9 per cent below the exact
    form and the Monte Carlo 1.4 per cent below it, with the same sign. The side is `RAMP_SIDE`'s and is
    never restated here: x is the magnitude of the shift over S0.

    ITS REGIME, WHICH IS NOT STATED BY THE RATE IT CALLS. `platforms.excitation_rate_per_atom` carries the
    steady-state two-level saturation parameter s = 2 (Omega/Gamma_nat)^2, whose coherence decays at the
    NATURAL width alone. This bench's coherence decays faster: at 40 um and 130 C the transit rate 1/tau is
    0.56 of Gamma/2 before the laser's own width (0.1 to 2.8 MHz, a scanned nuisance of the MLE) is added,
    so the true saturation intensity is at least 1.6 times the one this weight uses. Measured on this density
    at the deepest node, rescaling s by 1/1.56 and 1/2.1 moves the mixture's saturated-over-weak third
    cumulant from 0.843 to 0.896 and 0.922, six to nine per cent, ABOVE the kernel gate's own 0.05
    tolerance. **The gate cannot see it**, because `scripts/run_kernel_mc.py` tabulates the same function:
    model and Monte Carlo agree whatever the true depth, which is one approximation integrated two ways.
    Carrying the coherence rate into the rate and recording `gamma_coh * tau` per node is queued as
    `saturation-regime-term`; until it lands, every k3 this density carries is conditional on the
    natural-width saturation and says so here.

    FAILURE MODE: a `power_w` in milliwatts or a `w0_m` in microns puts the table five decades away
    from saturation and returns the triangle with no error; the kernel Monte Carlo's node key carries
    both in the units the gate reads, and the test at 40 um and 225 mW is the plant."""
    import dataclasses
    from .platforms import PLATFORMS, excitation_rate_per_atom
    x = np.asarray(x, float)
    inside = (x > 0.0) & (x <= 1.0)
    plat = dataclasses.replace(PLATFORMS["cell_130C"], w0_m=float(w0_m), temperature_k=float(T_C) + 273.15)
    p_tab = np.exp(np.linspace(np.log(1e-4), 0.0, int(n_table))) * float(power_w)
    g_tab = np.array([excitation_rate_per_atom(float(p), plat, rho=float(rho)) for p in p_tab])
    logp, logg = np.log(p_tab), np.log(np.maximum(g_tab, 1e-300))
    px = float(power_w) * np.where(inside, x, 1.0)
    lp = np.log(px)
    lg = np.interp(lp, logp, logg)
    lg = np.where(lp < logp[0], logg[0] + 2.0 * (lp - logp[0]), lg)      # below the table: the weak field, G ~ P^2
    g = np.exp(lg)
    w = np.where(inside, g / np.where(inside, x, 1.0), 0.0)
    area = trapezoid(w, x)
    return w / area if area > 0.0 else w


def ramp_mixture_moments(s0: float, z_ratio: float, x_grid: np.ndarray, g_x: np.ndarray,
                         n_photon: int = 2, n_grid: int = 4001) -> dict:
    """Mean, variance and third cumulant of `ramp_mixture` on a fine internal grid, for the kernel
    gate's model side: the same object `stark_ramp_axial_moments` returns for the weak-field law,
    for ANY local density (the saturated one above, the fringe's, the trapped one). At z_ratio 0 with
    `local_ramp_density` it reproduces the triangle's 2/3 and 1/135 to the grid's rounding; at a
    finite z_ratio with that law it reproduces `stark_ramp_axial_moments` (the test).

    THE GRID IS MEMORY (2026-09-18): `ramp_mixture` holds an (n_grid, 8, n_zeta) array, 1.3 GB at
    20 001 cells and the default 1000 zeta nodes, which is what took a ten-worker kernel re-run to
    the fan-out runner's emergency floor in three seconds. 4001 cells is 256 MB and the moments
    agree with the closed form to 1e-6."""
    if s0 <= 0:
        return {"mean": 0.0, "var": 0.0, "k3": 0.0}
    x_hi = float(x_grid[-1])
    s = np.linspace(0.0, x_hi * s0, int(n_grid))
    f = ramp_mixture(s, float(s0), float(z_ratio), x_grid, g_x, n_photon=n_photon)
    a = trapezoid(f, s)
    m = trapezoid(s * f, s) / a
    var = trapezoid((s - m) ** 2 * f, s) / a
    k3 = trapezoid((s - m) ** 3 * f, s) / a
    return {"mean": float(m), "var": float(var), "k3": float(k3)}


def _require_density_grid(x_grid: np.ndarray, g_x: np.ndarray) -> None:
    """Refuse a local-density grid this routine would silently misread.

    `ramp_mixture` takes the support's lower edge as `x_grid[0]` and
    interpolates with zero outside, so a DESCENDING grid returns a delta at
    the origin rather than a line, with no error: mean 0.00 against the
    correct -0.65 (found 2026-09-08 on the exported surface the
    same wave added to ADAPTING.md). A grid that stops short of the support
    renormalises to one and reads as a narrower ramp. Both are the class the
    record names, a plausible-looking table where an error belonged.

    ITS BLIND REGION, stated: a grid from -0.5 to 0 carrying a density whose
    true support reaches -1 is indistinguishable here from a genuine density
    of support 0.5, since the support is what the caller declares. What is
    checkable is the upper edge, which the physics fixes at zero shift, and
    that is checked.
    """
    x = np.asarray(x_grid, dtype=float)
    g = np.asarray(g_x, dtype=float)
    if x.ndim != 1 or g.shape != x.shape or x.size < 2:
        raise ValueError("ramp_mixture: x_grid and g_x must be one-dimensional and the same length")
    if not (np.all(np.isfinite(x)) and np.all(np.isfinite(g))):
        raise ValueError("ramp_mixture: x_grid and g_x must be finite")
    if not np.all(np.diff(x) > 0):
        raise ValueError(
            "ramp_mixture: x_grid must ascend; the support's lower edge is read "
            "as x_grid[0], so a descending grid returns a delta at the origin")
    # BLUE SINCE O27: the LOWER edge is zero shift, to within one grid step, and the
    # support's edge is positive. The tolerance is the grid's own step and not an absolute
    # epsilon, because the fringe density is a histogram whose first BIN CENTRE sits half a
    # step above zero (a step of 0.0031), which the red-sided version of this check refused
    # on its first run for the mirrored reason.
    step = float(np.max(np.diff(x)))
    if x[0] < -1e-9 or x[0] > 1.5 * step or x[-1] <= 0.0:
        raise ValueError(
            f"ramp_mixture: x_grid must run from 0 up to the support's positive edge "
            f"(within one grid step), got [{x[0]:.4g}, {x[-1]:.4g}] with step {step:.4g}")
    if np.any(g < 0):
        raise ValueError("ramp_mixture: a density may not be negative")


def ramp_mixture(nu: np.ndarray, s0: float, z_ratio: float,
                 x_grid: np.ndarray, g_x: np.ndarray,
                 n_photon: int = 2, n_zeta: int = 1000) -> np.ndarray:
    """The axial mixture of a LOCAL shift density (docs/methods/03, the ramp's
    third generalisation, 2026-09-08). The collection window spans |z| <= Z
    about the focus, the local edge is S(zeta) = s0 / (1 + zeta^2) at
    zeta = z / z_R, and the per-z signal weight (1 + zeta^2)^(1-n) cancels
    the local normalisation S(zeta)^(-1) up to (1 + zeta^2)^(2-n), so for any
    local density g(x) on x = s/S,

        f(s) = (1/s0) * int_0^{Z/z_R} (1 + zeta^2)^(2-n) g( s (1 + zeta^2) / s0 ) dzeta,

    area-normalised. With g the transverse law this IS stark_ramp_axial, whose
    closed form zeta_m + zeta_m^3 / 3 is this integral done by hand (the
    test); with g the fringe-resolved density of
    rb5s6s.fringe_tail.fringe_shift_density it carries both terms the world
    builder lacked; z_ratio = 0 is the local density itself, so the fringe
    alone goes through here too. Cell-integrated with 8 sub-samples as the
    axial form is, evaluated only on the cells the support reaches (about
    2 s0 / dnu of them), and a delta at zero for s0 <= 0. The integrand in
    zeta is bounded and smooth except at the local edge, where it jumps, so
    the midpoint rule converges as 1/n_zeta: 4.6e-3 of the peak at 200,
    6.5e-4 at 1000 (the default; about 20 ms a call, and build_world_trace
    memoises per rung) at the widest window in the record, 4.17. At
    z_ratio = 0 it reproduces stark_ramp_axial's cell integration to
    rounding and differs from stark_ramp in the edge cell alone, by that
    function's one-node first-moment transfer (4 per cent of the peak in
    that cell, 2e-5 of the peak on a convolved trace)."""
    _require_density_grid(x_grid, g_x)
    dnu = nu[1] - nu[0]
    out = np.zeros_like(nu, dtype=float)
    if s0 <= 0:
        out[np.argmin(np.abs(nu))] = 1.0 / dnu
        return out
    x_hi = float(x_grid[-1])                         # the support's upper edge in x (BLUE; O27)
    lo_s, hi_s = 0.0, x_hi * s0
    cells = np.nonzero((nu + 0.5 * dnu > lo_s) & (nu - 0.5 * dnu < hi_s))[0]
    if cells.size == 0:
        out[np.argmin(np.abs(nu))] = 1.0 / dnu
        return out
    lo = np.clip(nu[cells] - 0.5 * dnu, lo_s, hi_s)
    hi = np.clip(nu[cells] + 0.5 * dnu, lo_s, hi_s)
    sub = (np.arange(8) + 0.5) / 8.0
    s_sub = lo[:, None] + (hi - lo)[:, None] * sub[None, :]            # (ncell, 8)
    if z_ratio > 0:
        zeta = (np.arange(n_zeta) + 0.5) / n_zeta * z_ratio             # midpoints
    else:
        zeta = np.zeros(1)
    fac = 1.0 + zeta ** 2
    x = s_sub[:, :, None] * fac[None, None, :] / s0                       # (ncell, 8, nz)
    g = np.interp(x.ravel(), x_grid, g_x, left=0.0, right=0.0).reshape(x.shape)
    dens = (g * fac[None, None, :] ** (2 - n_photon)).mean(axis=2)        # the zeta integral / Z
    w = dens.mean(axis=1) * (hi - lo)
    total = w.sum()
    if total <= 0:
        out[np.argmin(np.abs(nu))] = 1.0 / dnu
        return out
    out[cells] = w / total / dnu
    return out


def stark_ramp_axial_moments(s0: float, z_ratio: float, n_photon: int = 2,
                             n_grid: int = 200_001) -> dict:
    """Moments of stark_ramp_axial on a fine internal grid: mean, variance,
    and the dimensionless standardized skewness g1 = mu3 / var^(3/2).
    Pure-transverse (z_ratio -> 0) benchmarks: n=2 triangle gives
    mean = +(2/3) s0, var/mean^2 = 1/8, g1 = -18^1.5/135 ~ -0.5657;
    n=1 uniform gives mean = +s0/2, g1 = 0. THAT NULL IS THE z_ratio -> 0
    LIMIT AND NOT A PROPERTY OF ONE-PHOTON EXCITATION (2026-09-09): the
    transverse law is uniform at each slice, and the axial mixture of uniforms
    with a common lower endpoint and falling upper endpoints is not uniform and
    not symmetric. Call this function with n_photon=1 at a finite z_ratio and
    g1 runs to -1.92 at the 16 micron configuration. results/waist_ladder.csv
    carries the one-photon cumulant against the two-photon one per rung."""
    if s0 <= 0:
        # No ramp, so the shift distribution is a delta at zero: its mean and
        # variance are exactly zero and its standardized skew is 0/0. The two
        # sibling functions guard this case and return the spike; this one
        # divided by a zero norm and returned NaN for all three, which says
        # "undefined" about two moments that are exactly defined.
        return {"mean": 0.0, "var": 0.0,
                "skew_standardized": float("nan")}
    s = np.linspace(0.0, s0, n_grid)
    a = np.abs(s)
    with np.errstate(divide="ignore", invalid="ignore"):
        zm = np.sqrt(np.maximum(s0 / np.where(a > 0, a, np.inf) - 1.0, 0.0))
    zm = np.minimum(zm, z_ratio)
    f = a ** (n_photon - 1) * (zm + zm ** 3 / 3.0)
    norm = trapezoid(f, s)
    mean = trapezoid(f * s, s) / norm
    var = trapezoid(f * (s - mean) ** 2, s) / norm
    mu3 = trapezoid(f * (s - mean) ** 3, s) / norm
    return {"mean": float(mean), "var": float(var),
            "skew_standardized": float(mu3 / var ** 1.5)}


def ramp_moment_contributions(s0: float, z_ratio: float = 0.0,
                              n_photon: int = 2) -> dict:
    """The ramp's ADDITIVE contributions to the three lowest line cumulants —
    the forward model for the fixed-lock session "principled hybrid" (docs/PLAN.md §8.3,
    THEORY_NOTE §3). The convolved symmetric CORE kernels (natural, laser,
    transit) contribute nothing to SELF-CENTRED odd cumulants -- the
    Lorentzian only up to the truncation fraction
    results/cumulant_window_check.csv measures, its even
    moments divergent (docs/wiki/third-cumulant.md) -- so the ramp alone sets
    the odd part of a centred readout -- but the standing-wave fringe
    tail is a separate MULTIPLICATIVE effect that DOES suppress this third
    cumulant at the small waist (constants.py / fringe_tail), not modelled here.
    The ramp contributes:

        pull       = kappa_1  (centroid shift, MHz)
        excess_var = kappa_2  (variance the ramp adds, MHz^2)
        kappa3     = kappa_3  (third cumulant, MHz^3)

    These are THREE analytic functionals of the ONE parameter S0 (at a given
    collection geometry z_ratio = Z_c/z_R): the fixed-lock joint fit constrains a
    single S0(P) per condition and checks that the pull, excess-variance and
    third-cumulant measured from the data are mutually consistent with it
    (a chi^2). One S0, three moments -- a spurious asymmetry that is not a
    real ramp will not also reproduce the correct lower-order pull and
    variance. Pure triangle (z_ratio->0): pull +2/3 S0, excess_var S0^2/18,
    kappa3 -S0^3/135. NOT three extraction methods -- one fitted S0, three
    consistency projections."""
    m = stark_ramp_axial_moments(s0, max(z_ratio, 1e-6), n_photon)
    return {"pull": m["mean"], "excess_var": m["var"],
            "kappa3": m["skew_standardized"] * m["var"] ** 1.5}


def stark_from_intensity_profile(nu: np.ndarray, s0: float,
                                 intensity: np.ndarray,
                                 measure: np.ndarray,
                                 n_photon: int = 2) -> np.ndarray:
    """The general seam behind stark_ramp: the light-shift distribution for
    ANY sampled intensity profile, area-normalized on the grid.

    Every environment gives light a different intensity distribution — a
    focused beam, a nanofibre evanescent field, a hollow-core mode, a
    lattice site — and each turns the AC-Stark shift into its own lineshape
    through the same three ingredients: the shift is proportional to I, the
    detected signal to I^n_photon, and positions are weighted by the
    geometry's volume measure. Pass intensity samples I(x_i)/I_max on any
    parameterization x of the geometry, with measure_i the volume weight of
    each sample (r dr for a cylindrical evanescent field, uniform for a 1D
    scan, ...), and the returned density on nu is

        f(s) with s_i = -s0 * I_i / I_max, weight_i = measure_i * I_i^n.

    For the focused-beam geometric measure this reproduces stark_ramp's
    triangle exactly (test_lineshape has the equivalence test), and the n=1
    uniform case reproduces its flat distribution. Atoms outside the light
    (I=0) contribute at nu=0 with their signal weight, which is zero for
    any n >= 1, so truncating the sampling domain where the signal has died
    is safe. Returns a unit spike at nu=0 when s0 <= 0."""
    dnu = nu[1] - nu[0]
    out = np.zeros_like(nu, dtype=float)
    if s0 <= 0:
        out[np.argmin(np.abs(nu))] = 1.0 / dnu
        return out
    ii = np.asarray(intensity, float)
    w = np.asarray(measure, float) * np.maximum(ii, 0.0) ** n_photon
    s = +s0 * ii / ii.max()          # BLUE: the adopted Delta alpha is negative (O27)
    idx = np.clip(np.round((s - nu[0]) / dnu).astype(int), 0, len(nu) - 1)
    np.add.at(out, idx, w)
    area = out.sum() * dnu
    return out / area if area > 0 else out


# ---------------------------------------------------------------------------
# the composite model
# ---------------------------------------------------------------------------

def _grid(span: float, dnu: float) -> np.ndarray:
    n = int(np.ceil(span / dnu))
    return (np.arange(-n, n + 1)) * dnu


# --------------------------------------------------------------------------
# The permeated gases: a constant Lorentzian the cell cannot exclude
# --------------------------------------------------------------------------
ATMOSPHERE_TORR = 760.0
"""Total pressure the cell equilibrates towards, Torr."""

PERMEATED_GASES = {
    # species: mole fraction of air (the atmosphere's own partial pressure is where permeation ends)
    "he": 5.24e-6,
    "ne": 18.2e-6,
    "ar": 9340e-6,
}
"""Atmospheric abundance by species, and NO broadening coefficient (F138, 2026-09-18).

THE ABUNDANCES ARE THE LOAD-BEARING HALF and they owe nothing to any paper here: permeation carries
a sealed cell to the atmosphere's own PARTIAL PRESSURE of every species small enough to cross the
glass, so ABUNDANCE fixes where it ends and permeability fixes only how long it takes. Neon is 3.5
times helium in air, so the species this record named first is the smaller of the two that matter.

THE COEFFICIENTS ARE NOT IN THIS TABLE, BY RETRACTION. The version of 2026-09-18 morning carried
Zameroski's 5S-5D foreign-gas rates here and printed widths from them (0.2035 and 0.5452 MHz), which
F136 and F137 then quoted as fractions of the fitted collisional width. `docs/lit/zameroski2014.md`
refuses those rates as transferable ("the upper states differ, so the coefficients are not
transferable, and nothing here can be adopted as a value"), so a width computed from them is not a
width on this line, and F138 retracts every such number. The mechanism stands: a permeated gas is a
constant Lorentzian, exactly `gamma_l`. `permeated_gas_width_mhz` therefore takes its coefficients
as an ARGUMENT and refuses to run without them, so no width can be printed from a number the record
does not hold; a caller passing a 5S-5D coefficient is computing a SCALE and says so.
"""


def permeated_gas_width_mhz(coefficients, equilibrated=("he",), fractions=None):
    """The permeated family's constant Lorentzian width and net shift, MHz, at the CALLER'S
    coefficients: `coefficients[species] = (broadening MHz/Torr, shift MHz/Torr)`, required.

    Returns ``(width, shift, detail)``: the FWHM the family adds to the homogeneous width, the net
    centre shift, and a per-species breakdown. `equilibrated` names the species taken to have
    reached equilibrium; `fractions` overrides with an explicit 0-to-1 fraction per species, which
    is how the span is walked.

    **THIS IS A PRIOR ON `gamma_l`, NOT A SECOND TERM.** `_kernel_widths` builds
    ``homog = gamma_nat + gamma_coll + max(gamma_l, 0) + ...``, and Lorentzians of FWHM a and b
    convolve to one of FWHM a+b identically, so a permeated-gas width is EXACTLY DEGENERATE with
    `gamma_l` at one temperature. They separate only through a dependence the gas has and the laser
    does not -- at fixed pressure broadening goes as T^-1/2, a few per cent across this record's 70
    to 130 C arm, against `beta_self`'s steep rise -- so THIS DATA CANNOT SPLIT THEM. Adding the
    family to `homog` beside a free `gamma_l` would double-count it. The family's width is the
    centre of `gamma_l`'s prior and its span the prior's width.

    **THE TWO-TEMPERATURE CONVERSION IS NOT APPLIED, and the reason is that it cannot be.** A rate
    per pressure carries to another cell temperature as T^-1/2, and our Zameroski note records NO
    cell temperature. That is an OPEN item needing a read of the held PDF, not a small correction:
    a rate per pressure carries two temperatures, the source's and this record's, and the record
    has already paid for carrying one.

    **ARGON IS EXCLUDED BY OUR OWN LINE, which is the only part measured rather than borrowed.**
    Equilibrium would put 7.10 Torr in the cell, and a width from the borrowed 5S-5D coefficient is a
    SCALE and not a width on this line (F138), so the number that belongs here is the BOUND and not the
    width. Re-derived here from a
    COMMITTED cell rather than a remembered one: `results/linefit_conditions.csv`'s widest
    `total_fwhm` over its 32 rows is 5.741 MHz, so the line bounds argon below 1.8e-2 of equilibrium,
    and nitrogen and oxygen follow a fortiori by kinetic diameter. **The figure carried into this
    record from the thesis side was "under three parts in a thousand"; our own committed width gives
    1.8e-2, six times looser, and the tighter number is not reproducible from anything here.** The
    conclusion is unchanged. Argon is therefore never in the default
    `equilibrated` set; naming it asks for the excluded case deliberately.

    DEFAULT: helium alone, the conservative end this record can defend -- its time constant is about
    eight days against a cell's age, where neon's is two to twenty years and depends on the glass
    type and the fill date, both OPEN in `docs/plan/12_open-apparatus-items.md`.
    """
    if fractions is None:
        fractions = {k: (1.0 if k in equilibrated else 0.0) for k in PERMEATED_GASES}
    if not coefficients:
        raise ValueError("permeated_gas_width_mhz needs coefficients {species: (MHz/Torr broadening, MHz/Torr shift)}: "
                         "this record holds none for 5S-6S (F138), and a width from a borrowed one is a scale")
    width = shift = 0.0
    detail = {}
    for name, x_air in PERMEATED_GASES.items():
        f = float(fractions.get(name, 0.0))
        if f == 0.0:
            detail[name] = {"fraction": 0.0, "p_torr": 0.0, "width_mhz": 0.0, "shift_mhz": 0.0}
            continue
        if name not in coefficients:
            raise ValueError(f"no coefficient for {name!r}; every equilibrated species needs one")
        beta, delta = (float(x) for x in coefficients[name])
        p_torr = x_air * ATMOSPHERE_TORR * f
        w, d = p_torr * beta, p_torr * delta
        width += w
        shift += d
        detail[name] = {"fraction": f, "p_torr": p_torr, "width_mhz": w, "shift_mhz": d}
    return width, shift, detail


def permeated_gas_span_mhz(coefficients):
    """The width's span, helium-only against helium-and-neon equilibrated, at the caller's
    coefficients (a scale unless the coefficient is this line's own).

    The record spans a fact nobody has rather than picking the midpoint of an unknown: neon's
    equilibration fraction is not measured and its time constant straddles a cell's age.
    """
    lo, _, _ = permeated_gas_width_mhz(coefficients, equilibrated=("he",))
    hi, _, _ = permeated_gas_width_mhz(coefficients, equilibrated=("he", "ne"))
    return lo, hi


def _kernel_widths(gamma_coll, sigma_laser_fwhm, transit_fwhm, gamma_nat_mhz, laser_kind, gamma_l):
    """The one computation of the smooth kernels' widths, for model_profile and
    for model_grid_step_mhz (a reader found the two carrying textually identical
    copies, 2026-09-04): returns (lorentzian laser?, the homogeneous FWHM, the
    kernel widths that set the grid)."""
    lorentz_laser = laser_kind != "gaussian"
    homog = (gamma_nat_mhz + gamma_coll + max(gamma_l, 0.0)
             + (sigma_laser_fwhm if lorentz_laser else 0.0))
    kernel_widths = ([homog] + ([] if lorentz_laser else [sigma_laser_fwhm])
                     + [transit_fwhm])
    return lorentz_laser, homog, kernel_widths


def model_grid_step_mhz(*, gamma_coll: float, sigma_laser_fwhm: float,
                        transit_fwhm: float, s0: float = 0.0,
                        gamma_nat_mhz: float = GAMMA_NAT_HZ / 1e6,
                        laser_kind: str = "gaussian", gamma_l: float = 0.0,
                        resolve_shift: bool = False,
                        grid_steps_per_kernel: float | None = None) -> float:
    """The internal grid step model_profile convolves on, in MHz.

    Public so a producer that must know how many cells its ramp spans asks
    the model instead of re-deriving the rule beside it: the first such
    mirror (2026-09-04) named a constant the producer did not have, and a
    mirror that drifts from the model is exactly the blind spot A33 found.
    The rule: the narrowest smooth kernel over ``grid_steps_per_kernel``
    (the module constant when None), the shift joining the candidates only
    under ``resolve_shift``, floored at GRID_STEP_FLOOR_MHZ.
    """
    _lorentz_laser, homog, kernel_widths = _kernel_widths(gamma_coll, sigma_laser_fwhm, transit_fwhm,
                                                          gamma_nat_mhz, laser_kind, gamma_l)
    steps = GRID_STEPS_PER_KERNEL if grid_steps_per_kernel is None else float(grid_steps_per_kernel)
    grid_widths = kernel_widths + ([s0] if (resolve_shift and s0 > 0) else [])
    positive = [w for w in grid_widths if w > 0]
    # every width zero is a degenerate call rather than an error: the floor is
    # the answer, and the docstring promised it unconditionally while min() on
    # an empty candidate list raised (2026-09-04)
    dnu = (min(positive) / steps) if positive else GRID_STEP_FLOOR_MHZ
    return max(dnu, GRID_STEP_FLOOR_MHZ)


def model_profile(nu: np.ndarray, *, gamma_coll: float, sigma_laser_fwhm: float,
                  transit_fwhm: float, s0: float = 0.0,
                  gamma_nat_mhz: float = GAMMA_NAT_HZ / 1e6,
                  laser_kind: str = "gaussian", gamma_l: float = 0.0,
                  profile: Callable[[np.ndarray, float], np.ndarray] = stark_ramp,
                  resolve_shift: bool = False,
                  grid_steps_per_kernel: float | None = None,
                  ) -> np.ndarray:
    """Area-normalized composite line on the transition axis (MHz).

    TWO BROADENERS ARE DELIBERATELY ABSENT, and both share the ramp's own P^2
    signature, so a fit that omits them lets s0 absorb what they would have
    taken and the light-shift bound comes out LOOSE. They are atomic
    saturation, which widens the homogeneous core by sqrt(1+s) and is the
    larger, and hyperfine pumping through the real 5P cascade, whose decay does
    not preserve F, so a transiting atom can leave the driven ground state
    mid-flight. Their ratio is exactly the branching fraction f, which is not
    resolved here beyond 1/3 to 2/3. Both are left out because injecting them
    means committing to the two-level homogeneous saturation law with a
    two-photon Rabi frequency, standard practice rather than a derivation for
    this level structure. The consequence is measured rather than argued, a
    factor 2.8 on the width-only bound and 2.21 on the joint, and all three
    terms are degenerate in both of the width channel's CONTINUOUS knobs (P
    and w0), so no sweep separates them. Two things do. The centroid pull,
    because the companions broaden without moving the line. And the LINE INDEX
    (2026-08-10): the ramp and the saturation are F-independent here while the
    pumping branching runs 0.223 to 0.372 across the four archive lines, a
    two-step cascade product rather than a degeneracy weight, so the pumping
    term alone differs between the lines by 1.67. That is 4 kHz of width
    against an 88 kHz single-block scatter, so it is real and unspendable here.
    Reproduce with scripts/run_saturation_probe.py, write-up in
    docs/notes/two_photon_saturation_companion.md, drawn in
    figures/fig23_hyperfine_pumping.png.

    Parameters (all MHz, all on the transition axis):
      gamma_coll        collisional Lorentzian FWHM (adds to Gamma_nat)
      sigma_laser_fwhm  laser kernel FWHM (already x2 for the two photons)
      transit_fwhm      two-sided-exponential transit FWHM
      s0                on-axis AC-Stark red shift (0 => no Stark term)
      gamma_nat_mhz     natural FWHM (default the fixed physical value)
      laser_kind        'gaussian' (default) or 'lorentzian' laser wings
      profile           light-geometry seam: profile(grid, s0) -> the
                        area-normalized shift density convolved in when
                        s0 > 0. Default stark_ramp, the focused-beam
                        triangle. An adapted geometry passes a closure over
                        stark_from_intensity_profile with its own sampled
                        intensities and volume measure, e.g.
                        lambda g, s: stark_from_intensity_profile(g, s, I, m)

    Built by convolving the kernels on a fine internal grid, then sampled at
    `nu`. Homogeneous Lorentzians (natural + collisional) are combined
    analytically before convolution.
    """
    # A Lorentzian laser kernel is ADDED, not convolved: two Lorentzians
    # convolve to their summed width exactly, and doing it on a finite grid
    # instead made the profile depend on how the total was SPLIT, at up to
    # 3.7e-3 of peak, purely through tail truncation. See the long note in
    # lineshape.composite_profile and results/kernel_identifiability.csv.
    # gamma_l: the mixed G+L kernel's Lorentzian component, ADDED for the
    # exactness reason in composite_profile's note. Default 0.0 is bit-identical.
    if laser_kind not in ("gaussian", "lorentzian"):
        raise ValueError(
            f"laser_kind={laser_kind!r} is neither 'gaussian' nor "
            f"'lorentzian'. This selector used to treat any other "
            f"string as Lorentzian, so a typo chose a MODEL FORM "
            f"silently, which is the systematic this record spends its "
            f"kernel chain measuring.")
    _lorentz_laser, homog, kernel_widths = _kernel_widths(gamma_coll, sigma_laser_fwhm, transit_fwhm,
                                                          gamma_nat_mhz, laser_kind, gamma_l)
    span_widths = kernel_widths + ([s0] if s0 > 0 else [])
    span = 6.0 * (sum(span_widths) + max(span_widths)) + 5.0
    # grid step from the smooth kernels only: stark_ramp handles s0 below the
    # grid step exactly (cell integrals + moment correction), so a tiny s0
    # must not explode the grid (fix, 2026-07-11)
    # The grid is set by the smooth kernels; the ramp handles a shift below one
    # cell exactly in its mean, but a derivative of the profile (a windowed
    # moment, a width difference) converges only when the ramp itself is
    # resolved: the error collapses on the ramp's cell count (found 2026-09-04:
    # 0.478 to 0.498 on the survival ratio and 7.48 to a value about three per
    # cent lower on the cusp-branch broadening; with the shift on the grid the
    # steps per kernel and the shift together set that count). resolve_shift
    # adds the shift to the widths that set the grid; grid_steps_per_kernel
    # overrides the module constant.
    dnu = model_grid_step_mhz(gamma_coll=gamma_coll, sigma_laser_fwhm=sigma_laser_fwhm,
                              transit_fwhm=transit_fwhm, s0=s0, gamma_nat_mhz=gamma_nat_mhz,
                              laser_kind=laser_kind, gamma_l=gamma_l,
                              resolve_shift=resolve_shift,
                              grid_steps_per_kernel=grid_steps_per_kernel)
    g = _grid(span, dnu)

    prof = lorentzian(g, homog)
    if not _lorentz_laser:
        prof = _conv(prof, gaussian(g, sigma_laser_fwhm), dnu)
    if transit_fwhm > 0:                 # 0 => no transit kernel (nested-model ladder)
        prof = _conv(prof, two_sided_exponential(g, transit_fwhm), dnu)
    if s0 > 0:
        prof = _conv(prof, profile(g, s0), dnu)

    prof = np.interp(nu, g, prof, left=0.0, right=0.0)
    area = trapezoid(prof, nu)
    return prof / area if area > 0 else prof


def _conv(a: np.ndarray, b: np.ndarray, dnu: float) -> np.ndarray:
    """Same-length convolution preserving area (b is area-normalized)."""
    return np.convolve(a, b, mode="same") * dnu


def total_fwhm_mhz(nu: np.ndarray, *, gamma_coll: float, sigma_laser_fwhm: float,
                   transit_fwhm: float, s0: float = 0.0, **profile_kw) -> float:
    """The composite line's FULL WIDTH AT HALF MAXIMUM, transition axis, MHz.

    THE HEADLINE QUANTITY OF THIS WHOLE RECORD, and until v4.4 the only
    implementation of it was `stark._fwhm_of`, a private function. A package
    that exports eleven forward-model primitives and hides the one number the
    work is about is surfacing what its author found interesting rather than
    what a reader needs, and `stark._fwhm_of` now delegates here so there is
    exactly one definition. Two definitions of a headline quantity is how a
    factor of 48 survived five citations.

    The width is read off the model profile rather than composed from a
    formula, because the composite is a convolution of a Lorentzian, a
    Gaussian and a transit kernel with an optional Stark ramp, and no closed
    form is exact for it. `voigt_fwhm` below is the quick approximation for
    seeds and comparisons and is NOT this.

    `nu` sets the grid the half-maximum crossings are interpolated on, so it
    must span the line generously and be fine enough to resolve it; a grid
    that clips the wings returns the grid's width, not the line's.
    """
    y = model_profile(nu, gamma_coll=max(gamma_coll, 0.0),
                      sigma_laser_fwhm=sigma_laser_fwhm,
                      transit_fwhm=transit_fwhm, s0=max(s0, 0.0), **profile_kw)
    ypk = y.max()
    above = np.where(y >= 0.5 * ypk)[0]
    if above.size == 0:
        return float("nan")
    lo, hi = above[0], above[-1]

    def cross(i, j):
        y1, y2 = y[i], y[j]
        return (nu[i] + (0.5 * ypk - y1) * (nu[j] - nu[i]) / (y2 - y1)
                if y2 != y1 else nu[i])

    left = cross(lo - 1, lo) if lo > 0 else nu[lo]
    right = cross(hi, hi + 1) if hi + 1 < len(nu) else nu[hi]
    return float(right - left)


def voigt_fwhm(sigma_g_fwhm: float, gamma_l_fwhm: float) -> float:
    """Olivero-Longbothum Voigt FWHM approximation (for quick comparisons /
    seeds; the fits use the exact convolution above)."""
    return 0.5346 * gamma_l_fwhm + np.sqrt(0.2166 * gamma_l_fwhm ** 2 + sigma_g_fwhm ** 2)

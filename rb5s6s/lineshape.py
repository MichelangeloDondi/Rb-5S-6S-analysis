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
  f(s) ∝ |s| on [-S0, 0], from the I^2-excitation / I-shift derivation).
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
                        EPS0_F_PER_M, C_M_PER_S, H_PLANCK_JS)


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
    density f(s) ∝ |s| on s in [-s0, 0] (red shifts), area-normalized on the
    grid. Derivation (cell and evanescent geometry alike): two-photon signal
    ∝ I^2, shift ∝ I, volume measure gives du/u, so dS/du ∝ u -> linear ramp.
    s0 > 0 is the on-axis (maximum) red shift in MHz. Returns a delta-like
    unit spike at nu=0 when s0 <= 0 (no shift).

    THE I^2 IS A WEAK-FIELD STATEMENT (2026-08-10). The signal weight above is
    the leading term of the excited fraction, not the fraction, and the real
    weight (s/2)/(1+s) reduces to I^2 only while the saturation parameter s is
    small. That is safe here and not safe everywhere: s carries the two-photon
    Rabi frequency squared, so it scales as the FOURTH power of the inverse
    waist while s0 scales only as the second. At the archive's measured 64 um
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
    first-moment transfer so the discrete mean equals the exact -2/3 s0 even
    when s0 is far below the grid step — d(profile)/d(s0) never dies."""
    dnu = nu[1] - nu[0]
    out = np.zeros_like(nu)
    if s0 <= 0:
        out[np.argmin(np.abs(nu))] = 1.0 / dnu
        return out
    # exact integral of f(s) = 2|s|/s0^2 over each grid cell intersected
    # with the support [-s0, 0]:  F([a,b]) = (a^2 - b^2)/s0^2
    lo = np.clip(nu - 0.5 * dnu, -s0, 0.0)
    hi = np.clip(nu + 0.5 * dnu, -s0, 0.0)
    w = (lo ** 2 - hi ** 2) / s0 ** 2          # >= 0, sums to exactly 1
    # first-moment correction: move a little mass between adjacent nodes so
    # the discrete mean is exactly -(2/3) s0 (sub-grid shift information)
    mean = float(np.sum(nu * w))
    target = -(2.0 / 3.0) * s0
    j = int(np.argmax(w))
    eps = (mean - target) / dnu   # >0: move eps redward; <0: move |eps| blueward
    if 0.0 <= eps <= w[j] and j >= 1:
        w[j] -= eps
        w[j - 1] += eps
    elif eps < 0.0 and (-eps) <= w[j] and j + 1 < len(w):
        w[j] += eps
        w[j + 1] -= eps
    return w / dnu


def stark_shift_S0_mhz(power_w: float, w0_m: float, rho: float = 1.0,
                       delta_alpha_au: float = DELTA_ALPHA_AU) -> float:
    """On-axis maximum AC-Stark shift S0 of the two-photon line (TRANSITION
    axis, MHz), under the pinned standard convention (constants.DELTA_ALPHA_AU):

        dE_i = -(1/4) alpha_i E0^2 = -alpha_i I / (2 eps0 c)     [<E^2>=E0^2/2]
        S0   = Delta_alpha * I_eff / (2 eps0 c h),
        I_eff = (1+rho) * 2 P / (pi w0^2)   (time-averaged fwd+retro, no x2).

    rho = retro power ratio (1.0 = perfect retro). Returns S0 > 0 for a red
    shift (Delta_alpha > 0). Laser-axis value is S0/2. This is the coefficient
    the fixed-lock mean-pull-vs-power fit measures (inverted to give
    Delta_alpha); the archival ramp SHAPE does not depend on it."""
    i_eff = (1.0 + rho) * 2.0 * power_w / (np.pi * w0_m ** 2)
    d_alpha = delta_alpha_au * ATOMIC_POLARIZABILITY_SI
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
    # against it. Reached first by the fibre twin, whose Lorentzian transit is
    # carried inside the additive Lorentzian channel and needs no separate
    # transit kernel at all. Nothing committed changes: fit_transit=False pins
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

    on s in [-s0, 0]. z_ratio -> 0 recovers the pure transverse law
    (triangle for n=2); the hard edge at -s0 softens to zero (only the
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
    lo = np.clip(nu - 0.5 * dnu, -s0, 0.0)
    hi = np.clip(nu + 0.5 * dnu, -s0, 0.0)
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


def stark_ramp_axial_moments(s0: float, z_ratio: float, n_photon: int = 2,
                             n_grid: int = 200_001) -> dict:
    """Moments of stark_ramp_axial on a fine internal grid: mean, variance,
    and the dimensionless standardized skewness g1 = mu3 / var^(3/2).
    Pure-transverse (z_ratio -> 0) benchmarks: n=2 triangle gives
    mean = -(2/3) s0, var/mean^2 = 1/8, g1 = 18^1.5/135 ~ +0.5657;
    n=1 uniform gives mean = -s0/2, g1 = 0 — the skew exists at all only
    because the two-photon signal goes as I^2."""
    s = np.linspace(-s0, 0.0, n_grid)
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
    transit) contribute nothing to the odd cumulants and only add to the (even)
    variance, so the ramp alone sets the odd part -- but the standing-wave fringe
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
    variance. Pure triangle (z_ratio->0): pull -2/3 S0, excess_var S0^2/18,
    kappa3 +S0^3/135. NOT three extraction methods -- one fitted S0, three
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
    s = -s0 * ii / ii.max()
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


def model_profile(nu: np.ndarray, *, gamma_coll: float, sigma_laser_fwhm: float,
                  transit_fwhm: float, s0: float = 0.0,
                  gamma_nat_mhz: float = GAMMA_NAT_HZ / 1e6,
                  laser_kind: str = "gaussian", gamma_l: float = 0.0,
                  profile: Callable[[np.ndarray, float], np.ndarray] = stark_ramp
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
    _lorentz_laser = laser_kind != "gaussian"
    homog = (gamma_nat_mhz + gamma_coll + max(gamma_l, 0.0)
             + (sigma_laser_fwhm if _lorentz_laser else 0.0))
    kernel_widths = ([homog] + ([] if _lorentz_laser else [sigma_laser_fwhm])
                     + [transit_fwhm])
    span_widths = kernel_widths + ([s0] if s0 > 0 else [])
    span = 6.0 * (sum(span_widths) + max(span_widths)) + 5.0
    # grid step from the smooth kernels only: stark_ramp handles s0 below the
    # grid step exactly (cell integrals + moment correction), so a tiny s0
    # must not explode the grid (fix, 2026-07-11)
    dnu = min(w for w in kernel_widths if w > 0) / GRID_STEPS_PER_KERNEL
    dnu = max(dnu, GRID_STEP_FLOOR_MHZ)
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


def voigt_fwhm(sigma_g_fwhm: float, gamma_l_fwhm: float) -> float:
    """Olivero-Longbothum Voigt FWHM approximation (for quick comparisons /
    seeds; the fits use the exact convolution above)."""
    return 0.5346 * gamma_l_fwhm + np.sqrt(0.2166 * gamma_l_fwhm ** 2 + sigma_g_fwhm ** 2)

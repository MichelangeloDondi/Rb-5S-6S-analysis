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

import numpy as np

from ._compat import trapezoid
from .constants import (GAMMA_NAT_HZ, DELTA_ALPHA_AU, ATOMIC_POLARIZABILITY_SI,
                        EPS0_F_PER_M, C_M_PER_S, H_PLANCK_JS)


# ---------------------------------------------------------------------------
# elementary profiles (all AREA-NORMALIzed to 1, argument nu in MHz)
# ---------------------------------------------------------------------------

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
                      transit_kind: str = "exp"):
    """Fast no-Stark composite on a self-sized grid: Lorentzian(Gamma_nat +
    gamma_coll) (X) laser kernel (X) transit kernel, area-normalized.
    Returns (grid, profile). This is the shared kernel of the beta_self and
    global fits (S0 is fixed/negligible in the archival width fits; a fixed-lock session
    center fits use model_profile with the ramp instead). Moved here from
    beta.py (revision #9, 2026-07-11): composite lineshapes belong in the
    lineshape module, not in one consumer.

    transit_kind selects the MODEL FORM for the transit contribution and is the
    knob for the Voigt-vs-Lehmann model-form systematic on beta_self (M4c/M8):
    'exp' = the Biraben-Cagnac two-sided exponential (the cusp, the Lehmann
    form, default); 'gaussian' = a Gaussian of the same FWHM, which makes the
    whole line a pure Voigt (no cusp). Running the global fit under both and
    differencing beta gives the model-form error bar the paper must quote."""
    homog = GAMMA_NAT_HZ / 1e6 + max(gamma_coll, 0.0)
    widths = [homog, max(sigma_laser, 1e-6), max(transit_fwhm, 1e-6)]
    span = 6.0 * (sum(widths) + max(widths)) + 5.0
    dnu = max(min(widths) / 12.0, 1e-3)
    n = int(np.ceil(span / dnu))
    g = np.arange(-n, n + 1) * dnu
    prof = lorentzian(g, homog)
    lk = gaussian(g, sigma_laser) if laser_kind == "gaussian" else lorentzian(g, sigma_laser)
    prof = np.convolve(prof, lk, "same") * dnu
    tk = (two_sided_exponential(g, transit_fwhm) if transit_kind == "exp"
          else gaussian(g, transit_fwhm))
    prof = np.convolve(prof, tk, "same") * dnu
    area = trapezoid(prof, g)
    return g, (prof / area if area > 0 else prof)


def stark_ramp_axial(nu: np.ndarray, s0: float, z_ratio: float,
                     n_photon: int = 2) -> np.ndarray:
    """Diverging-beam generalization of stark_ramp (PLAN §8.3;
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
    THEORY_NOTE §3). Because the symmetric kernels contribute nothing to the
    odd cumulants and only add to the (even) variance, the ramp contributes:

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


# ---------------------------------------------------------------------------
# the composite model
# ---------------------------------------------------------------------------

def _grid(span: float, dnu: float) -> np.ndarray:
    n = int(np.ceil(span / dnu))
    return (np.arange(-n, n + 1)) * dnu


def model_profile(nu: np.ndarray, *, gamma_coll: float, sigma_laser_fwhm: float,
                  transit_fwhm: float, s0: float = 0.0,
                  gamma_nat_mhz: float = GAMMA_NAT_HZ / 1e6,
                  laser_kind: str = "gaussian") -> np.ndarray:
    """Area-normalized composite line on the transition axis (MHz).

    Parameters (all MHz, all on the transition axis):
      gamma_coll        collisional Lorentzian FWHM (adds to Gamma_nat)
      sigma_laser_fwhm  laser kernel FWHM (already x2 for the two photons)
      transit_fwhm      two-sided-exponential transit FWHM
      s0                on-axis AC-Stark red shift (0 => no Stark term)
      gamma_nat_mhz     natural FWHM (default the fixed physical value)
      laser_kind        'gaussian' (default) or 'lorentzian' laser wings

    Built by convolving the kernels on a fine internal grid, then sampled at
    `nu`. Homogeneous Lorentzians (natural + collisional) are combined
    analytically before convolution.
    """
    homog = gamma_nat_mhz + gamma_coll
    kernel_widths = [homog, sigma_laser_fwhm, transit_fwhm]
    span_widths = kernel_widths + ([s0] if s0 > 0 else [])
    span = 6.0 * (sum(span_widths) + max(span_widths)) + 5.0
    # grid step from the smooth kernels only: stark_ramp handles s0 below the
    # grid step exactly (cell integrals + moment correction), so a tiny s0
    # must not explode the grid (fix, 2026-07-11)
    dnu = min(w for w in kernel_widths if w > 0) / 12.0
    dnu = max(dnu, 1e-3)
    g = _grid(span, dnu)

    prof = lorentzian(g, homog)
    lk = gaussian(g, sigma_laser_fwhm) if laser_kind == "gaussian" \
        else lorentzian(g, sigma_laser_fwhm)
    prof = _conv(prof, lk, dnu)
    prof = _conv(prof, two_sided_exponential(g, transit_fwhm), dnu)
    if s0 > 0:
        prof = _conv(prof, stark_ramp(g, s0), dnu)

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

"""
Transit-broadening lineshape by Monte-Carlo (module M9)
======================================================

The phenomenological two-sided exponential (rb5s6s.lineshape) is a *stand-in*
for the real transit-time lineshape. This module computes the real thing from
first principles, addressing the three objections a careful reader raises
(2026-07-11):

  (1) the beam is not one radius -- w(z) = w0*sqrt(1+(z/zR)^2) grows along the
      axis and the collection optics integrate over many mm of it;
  (2) the atomic velocity is 3D Maxwell-Boltzmann, so transit is an average
      over transverse speeds (and impact parameters), not one on-axis time;
  (3) [experimental, not modelled here] stray/scattered 795 nm adds a pedestal.

PHYSICS. In the weak-excitation (low-saturation) limit the two-photon excited
amplitude for one atom is the Fourier transform of its two-photon coupling
along its trajectory, and the two-photon Rabi frequency is proportional to the
INTENSITY, Omega_2ph(t) ∝ I(r(t)). For a straight-line crossing of a Gaussian
beam (w ~ constant during the ~0.2 us transit, since an atom moves only
~30 um in z << zR ~ 3 mm), the intensity envelope is Gaussian in time, so the
per-atom lineshape is analytic:

    P_atom(nu) = I_pk^2 * (pi w^2 / (2 v_perp^2)) * exp(-(2 pi nu)^2 w^2 / (4 v_perp^2)),
    I_pk = (w0/w)^2 * exp(-2 b^2 / w^2),

with v_perp the transverse speed and b the impact parameter. The observed
lineshape sums P_atom over the atom ensemble, each atom weighted by its crossing
FLUX (proportional to v_perp; Lehmann 2021 eq. 6): uniform density in space (so
the two-photon 1/w^4 focus-weighting emerges automatically via I_pk^2), 2D
Maxwell-Boltzmann transverse speeds, and an optional collection-efficiency
weight eps(z). The flux weight is essential -- the signal is a steady-state RATE
(flux * excitation-probability), and it is what makes the Biraben-Cagnac cusp a
FINITE peak rather than a divergence. No free parameters beyond the geometry and
temperature; this is what a knife-edge-measured w(z) feeds in October.

The closed-form counterpart is constants.transit_fwhm_from_w0 (a two-sided
exponential of FWHM ln2 v_th / (pi w0), v_th = sqrt(2kT/m)), validated against
Lehmann's NNO worked example to 0.2%; this MC reproduces it and adds the real
w(z), impact-parameter and collection-column averaging.

WHY IT MATTERS. The magnitude the MC returns tests the archival budget. At the
nominal w0 = 32 um it gives a bare transit of ~1.87 MHz (110 C, transition axis)
-- convolved with the 3.49 MHz natural Lorentzian that ALREADY exceeds the
observed ~5.25 MHz line, so 32 um is EXCLUDED and w0 must be larger (~50 um
central, 45-70 um). i.e. the observed line is natural-plus-transit dominated and
the 2025 laser was NARROW; the MC settles this without a fit.

HISTORY (2026-07-12). An earlier version omitted the crossing-flux factor and so
weighted the ensemble by ~1/v, producing a spurious log-divergent cusp that ran
~2x too narrow. A separate note briefly claimed a SECOND (angular, factor-of-2)
bug and inferred w0 ~ 90 um; that was a laser-vs-transition axis bookkeeping
error -- the (2 pi nu) transition-axis convention here is correct. One real bug
(flux), now fixed.
"""

from __future__ import annotations

import numpy as np

from . import config as C
from .constants import (K_B_J_PER_K, M_RB87_KG, M_RB85_KG, LAMBDA_LASER_M,
                        W0_PRIOR_M)


def _sigma_v(T_C: float, isotope: int, mass_kg: float | None = None) -> float:
    """1D Maxwell-Boltzmann speed scale sqrt(kT/m) (m/s). ``mass_kg`` overrides
    the Rb isotope mass (used to reproduce non-Rb literature examples)."""
    m = mass_kg if mass_kg is not None else (M_RB87_KG if isotope == 87 else M_RB85_KG)
    return float(np.sqrt(K_B_J_PER_K * (T_C + 273.15) / m))


def transit_lineshape_mc(nu_mhz: np.ndarray, *, w0_m: float = W0_PRIOR_M,
                         T_C: float = 110.0, isotope: int = 87,
                         mass_kg: float | None = None,
                         z_half_range_m: float = 6e-3,
                         collection_sigma_z_m: float | None = None,
                         b_cut: float = 3.0, n_atoms: int = 200_000,
                         seed: int = None) -> np.ndarray:
    """Area-normalized transit lineshape on the TRANSITION axis (nu in MHz).

    z_half_range_m: half-length of the collected interaction column.
    collection_sigma_z_m: Gaussian collection acceptance in z (None = uniform).
    b_cut: impact parameters sampled uniformly in area out to b_cut*w(z).
    mass_kg: override the atomic mass (default = the Rb isotope mass); lets a
        test reproduce Lehmann 2021's NNO worked example (m = 44 u).
    """
    rng = np.random.default_rng(C.RNG_SEED if seed is None else seed)
    sv = _sigma_v(T_C, isotope, mass_kg)
    zR = np.pi * w0_m ** 2 / LAMBDA_LASER_M

    z0 = rng.uniform(-z_half_range_m, z_half_range_m, n_atoms)
    w = w0_m * np.sqrt(1.0 + (z0 / zR) ** 2)
    # impact parameter uniform in AREA within b_cut*w (uniform gas density)
    b = b_cut * w * np.sqrt(rng.uniform(0.0, 1.0, n_atoms))
    # transverse speed: 2D Maxwell-Boltzmann -> Rayleigh(sigma_v)
    v_perp = sv * np.sqrt(-2.0 * np.log(rng.uniform(1e-12, 1.0, n_atoms)))

    I_pk = (w0_m / w) ** 2 * np.exp(-2.0 * b ** 2 / w ** 2)
    # Per-atom excitation probability per crossing, |c_e|^2 ∝ I_pk^2 * w^2/v^2
    # (the pi/2 and one w^2 are the peak of the per-atom Gaussian; the extra w^2
    # is the uniform-in-area impact-parameter weight), TIMES the crossing FLUX
    # v_perp. The flux is the fix (2026-07-12): the signal is a steady-state RATE
    # = flux * prob, and flux ∝ v (Lehmann 2021 eq. 6). With Rayleigh(sv) speed
    # sampling (∝ v) this makes the net v-power 0 -> a FINITE two-sided-exponential
    # peak. WITHOUT it (the old bug) the net weight was ∝ 1/v -> a spurious
    # log-divergent, n_atoms-dependent cusp that ran ~2x too narrow.
    amp = I_pk ** 2 * (np.pi * w ** 2 / (2.0 * v_perp ** 2)) * v_perp * (w ** 2)
    if collection_sigma_z_m is not None:
        amp = amp * np.exp(-0.5 * (z0 / collection_sigma_z_m) ** 2)
    kcoef = (w ** 2) / (4.0 * v_perp ** 2)      # exponent = (2 pi nu_Hz)^2 * kcoef

    nu_hz = np.asarray(nu_mhz, float) * 1e6
    L = np.empty_like(nu_hz)
    two_pi2 = (2.0 * np.pi) ** 2
    for i, f in enumerate(nu_hz):
        L[i] = np.sum(amp * np.exp(-two_pi2 * f * f * kcoef))
    from ._compat import trapezoid
    area = trapezoid(L, nu_mhz)
    return L / area if area > 0 else L


def transit_added_fwhm_mc(gamma_nat_mhz: float = None, **kw) -> float:
    """The PHYSICAL transit metric: how much the transit kernel broadens the
    observable line, i.e. FWHM(natural (X) transit) - FWHM(natural).

    Why the convolved increment rather than the bare transit FWHM: the transit
    kernel is a cusped (two-sided-exponential) shape, and cusped kernels do NOT
    add in quadrature with the natural Lorentzian. The increment that a given
    transit actually contributes to the observed line therefore depends on the
    line it is convolved into, so the budget-relevant number is this convolved
    delta, not the bare kernel FWHM. (The bare FWHM is itself well-defined and
    n_atoms-independent once the crossing-flux weight is included -- see
    constants.transit_fwhm_from_w0 for its closed form; before the 2026-07-12
    flux fix the kernel had a spurious log-divergent, n_atoms-dependent cusp.)
    This convolved increment is the number that enters the budget and the
    transit<->w0 degeneracy."""
    from .lineshape import lorentzian
    from .constants import GAMMA_NAT_HZ
    gnat = GAMMA_NAT_HZ / 1e6 if gamma_nat_mhz is None else gamma_nat_mhz
    nu = np.arange(-30.0, 30.0, 0.01)
    dnu = nu[1] - nu[0]
    Lt = transit_lineshape_mc(nu, **kw)
    tot = np.convolve(Lt, lorentzian(nu, gnat), "same") * dnu
    half = nu[tot >= 0.5 * tot.max()]
    return float(half[-1] - half[0]) - gnat

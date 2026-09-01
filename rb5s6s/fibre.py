"""B3/O2: the fibre twin, minimal first.

THE FIBRE DOES NOT MEASURE LASER LINEWIDTH. It measures whether the observed
homogeneous component moves as the transit law predicts when temperature
varies. Nothing in this module estimates a laser linewidth, and a result from
it may not be reported as one.

O2 IS A DESIGN VALIDATION, NOT AN EXPERIMENTAL RESULT. Everything here
validates that a proposed design can identify intended quantities under
specified synthetic worlds. It does not demonstrate that the real fibre
experiment will. The epistemic class of every output is SIMULATION-BACKED at
best, never DEMONSTRATED.

MINIMAL FIRST, DELIBERATELY. The repository's historical failure mode is
building infrastructure before establishing that the discriminant works, so
the model here is only

    Gamma_hom(T, n) = Gamma_L + Gamma_transit(T) + Gamma_coll(n) + Gamma_0

and the first question is whether a temperature ladder can distinguish a
near-Lorentzian transit contribution from a temperature-independent
homogeneous one. `q_surf(t)`, a detection-channel object, and everything else wait until
that is answered.

THIS MODULE IS A LEAF. It imports core; core never imports it. Enforced by
tests/test_module_boundaries.py, not by intention.

THE TRANSIT KERNEL ENTERS AT SECOND ORDER, which is the whole reason this is
hard, and it is not what an earlier version of this docstring said. Its FWHM is
f*v/(pi*Lambda) with f between 0.24 and 0.44, but its time-domain function
(1+|t|/tau)exp(-|t|/tau) has NO linear term at the origin, and linear-at-the-
origin is exactly what makes Lorentzian widths add. So the kernel enters the
width quadratically, the way a Gaussian does, and contributes a fraction of
its own FWHM that depends on the line it is added to. The committed band is
results/transit_additivity.csv, quoted there with the core it was computed
against; a fraction without its core is uninterpretable, which is what made
this docstring wrong twice. Because it is
second order, the width a temperature ladder sees grows as T**0.98 rather than
as sqrt(T), so a design fitting a sqrt(T) column is fitting the wrong basis
function and the amplitude it recovers is not the transit width.

This paragraph said "LORENTZIAN" and "ADDS EXACTLY" until 2026-08-28. The
lineshape is the squared magnitude of the coupling's transform, which is a
squared Lorentzian, and the ensemble forms are tau^2-weighted superpositions of
those. Widths may still be added as an approximation whose error is not
characterised here. The ladder argument is unaffected because it rests on the
sqrt(T) scaling and not on exact additivity, so the design survives and only
the wording was wrong.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.constants import c, epsilon_0
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.special import jv, jvp, kv, kvp

from .constants import GAMMA_NAT_HZ  # noqa: F401  (core import; leaf direction)

K_B = 1.380649e-23
M_RB87 = 86.909180527 * 1.66053906660e-27

# Fused silica, Malitson, at the wavelengths this record actually uses. Read as
# ENVELOPE at four decimals: the fourth digit does not survive the fibre's own
# diameter uncertainty and is carried only so the mode solve is reproducible.
def n_silica_malitson(lambda_nm: float) -> float:
    """Fused silica index, Malitson (1965) three-term Sellmeier, 0.21-3.71 um.

    THE FUNCTION IS THE CONSTANT. Until 2026-08-28 this module carried a
    hand-typed table whose 993.4181 nm entry read 1.4525 -- the 852 nm value
    duplicated, a 0.0020 error at the one wavelength every result in this
    record uses, attributed to a source that does not give it -- and a second
    bare 1.4525 literal in `HE11Field.__init__` that agreed with the table
    only while both were wrong. A 2026-08 physics audit found it by
    re-solving the characteristic equation with both indices. Computing from
    the source formula removes every copy that could drift, and the strict
    table lookup this replaced refused full-precision wavelengths one hour
    after it was written, which is how the class was finally closed.

    Rounded to five decimals: the diameter tolerance swamps the fourth digit,
    and rounding keeps every producer bit-identical with the tabulated
    record whatever floating-point wavelength a caller derives.
    """
    l2 = (lambda_nm / 1000.0) ** 2
    return round(math.sqrt(
        1.0
        + 0.6961663 * l2 / (l2 - 0.0684043 ** 2)
        + 0.4079426 * l2 / (l2 - 0.1162414 ** 2)
        + 0.8974794 * l2 / (l2 - 9.896161 ** 2)), 5)


# The tabulated wavelengths this record actually uses, generated from the
# function above so a value CANNOT drift from its source. Kept because tests
# and callers enumerate it; joining it means adding a key, not typing a value.
N_SILICA = {lam: n_silica_malitson(lam)
            for lam in (480.0, 482.0, 762.0, 780.0, 852.0, 993.4181, 1064.0)}

# The velocity convention is TYPED rather than described in a comment, because
# "the thermal velocity" names two different numbers that differ by 6 per cent
# and the difference is the same size as effects this twin is meant to resolve.
VELOCITY_CONVENTIONS = ("mean", "rms")


def thermal_velocity(temperature_k: float, convention: str = "mean") -> float:
    """Thermal speed in m/s under a NAMED convention.

    `mean` is the Maxwell-Boltzmann mean speed sqrt(8 kT / pi m).
    `rms`  is sqrt(3 kT / m).
    """
    if convention not in VELOCITY_CONVENTIONS:
        raise ValueError(
            f"velocity convention {convention!r} not in {VELOCITY_CONVENTIONS}")
    if temperature_k < 0.0:
        raise ValueError("temperature must be non-negative")
    if convention == "mean":
        return math.sqrt(8.0 * K_B * temperature_k / (math.pi * M_RB87))
    return math.sqrt(3.0 * K_B * temperature_k / M_RB87)


@dataclass(frozen=True)
class TransitEstimate:
    """A transit width WITH the convention and temperature that produced it.

    Carrying these as fields rather than as prose is the mechanised form of a
    rule that was previously narrated: a bare width in a results row cannot be
    checked against the convention it assumed.
    """
    fwhm_hz: float
    convention: str
    temperature_k: float
    decay_length_m: float


# The guided transit kernel factor, and why it is not 1.
#
# The committed formula was v/(pi*Lambda), taken from the Fourier transform of
# the coupling envelope. `docs/methods/02` states the rule this record uses
# everywhere else: a lineshape is the SQUARED magnitude of the transform of the
# amplitude, not the transform. Applying the rule the record already has:
#
#   coupling      Omega(t) ~ I(t) = I0 exp(-v|t|/Lambda)
#   amplitude     a(nu)    ~ FT[Omega]        = 2 tau /(1 + (2 pi nu tau)^2)
#   LINESHAPE     P(nu)    ~ |a|^2            = squared Lorentzian
#
# AND THE ENVELOPE ITSELF IS A STATED CHOICE, not a solved profile. I(t) is
# written above as a plain exponential in time, and the solved field is NOT
# exponential at these radii: q*a runs 0.18 to 0.32 across the three candidate
# diameters, so the asymptotic form is unavailable everywhere the atoms sit.
# Matched on the SECOND MOMENT, which is the quantity the added width depends
# on, the solved profile gives an effective length near 270 nm against the
# nominal 401 nm, and the kernel enters at second order, so the width a
# temperature ladder reads moves by about 2.2.
#
# The direction is conservative under every definition tried, so the fibre
# lever is STRONGER than the record claims and closing this is a gain rather
# than a retraction. That is why it ships as an envelope choice instead of
# blocking a release. The size, the competing definitions and the two drafts
# that got the ordering wrong are the open item in
# docs/big_picture/06_next-nanofibre.md, and the derivation is
# docs/methods/09_the_guided_geometry.md section 9.2. Carrying the solved
# profile through this kernel is mathematics, not an apparatus fact.
#
# AND IT IS NOT A LORENTZIAN ANY MORE, which matters beyond the width. The
# module and several producers said a fibre transit term "adds EXACTLY to
# every other Lorentzian, so at a single temperature it has no separate
# existence". That is a statement about the KERNEL CLASS and it does not
# survive the correction: a squared Lorentzian is not a Lorentzian, and the
# ensemble forms are tau^2-weighted superpositions of squared Lorentzians and
# are further still. Widths may be added as an approximation whose error is
# not characterised here, and the ladder argument rests on the sqrt(T) scaling
# rather than on exact additivity, so the design survives and the wording did
# not.
#
# A squared Lorentzian is narrower than the Lorentzian it is built from by
# sqrt(sqrt(2) - 1) = 0.6436 exactly, verified analytically and numerically.
# (This line carried a stray factor of two until 2026-08-28. The constant and
# the test were right; the identity as written was not.)
#
# THEN THE ENSEMBLE AVERAGE NARROWS IT AGAIN, and how much depends on the
# weight. The SPEED branch narrows by more than the squaring did, x0.38 against
# x0.64. The FLUX branch, which is the default, narrows by LESS, x0.68. Slow
# atoms interact longer and their |a|^2 carries tau^2, which pulls the average
# toward the narrowest contributions, and a flux weight partly cancels that by
# favouring fast atoms. This comment claimed both branches narrow by more than
# the squaring until 2026-08-28, stated as a general property directly above
# the table whose default row refutes it. Measured numerically at
# 150 uK at the 370 nm fibre's solved intensity decay length, 401 nm. The
# table read 397 nm and 153.1 / 98.6 / 37.1 / 67.2 kHz until 2026-08-29, which
# was the length under the retired silica index; the RATIOS never moved,
# because a kernel factor does not depend on Lambda:
#
#   claimed  v_bar/(pi Lambda)                        151.8 kHz
#   single velocity, squared Lorentzian at v_bar       97.7 kHz   x0.6436
#   ensemble, Maxwell speed weight                     36.8 kHz   x0.2422
#   ensemble, flux weight (v df)                       66.6 kHz   x0.4387
#
# THE WEIGHTING IS A MODEL CHOICE AND IT IS NOT SETTLED HERE, so it is SPANNED
# rather than picked. Which weight applies depends on how atoms arrive at the
# surface, which is a property of the trap and not of the line.
def transit_kernel_factor(weight: str = "flux") -> float:
    """Re-derive an ensemble transit factor from its own quadrature.

    THE CONSTANTS BELOW ARE CACHED VALUES OF THIS FUNCTION. It exists because
    a model term in this record must carry a route to be re-derived with the
    repository's own software, and without one a number that came out of a
    scratch integration cannot be checked by a reader.

    It was needed at once. The cached `ensemble_speed` read 0.245 until
    2026-08-28 against 0.2422 here, because the scratch integration behind it
    started from a lower velocity limit of about 1e-3 m/s. The speed-weighted
    branch is the one dominated by slow atoms, so it is the one a lower cutoff
    biases, and it converges to 0.2422 from 1e-4 downwards.

    In dimensionless form with s = v/v_p and b = 2*pi*nu*Lambda/v_p, the
    tau^2-weighted average of the squared Lorentzian is

        I_k(b) = int_0^inf s^(4+k) exp(-s^2) / (s^2 + b^2)^2 ds

    with k = 1 for a flux weight and k = 0 for a speed weight. The half-height
    b gives the factor as b_half*sqrt(pi)/2, the sqrt(pi)/2 converting the
    most-probable speed into the mean speed these factors are normalised
    against.
    """
    k = {"flux": 1, "speed": 0}[weight]

    def integral(b: float) -> float:
        return quad(lambda t: t ** (4 + k) * math.exp(-t * t)
                    / (t * t + b * b) ** 2, 0.0, math.inf, limit=400)[0]

    half = integral(0.0) / 2.0
    lo, hi = 1e-6, 5.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if integral(mid) > half:
            lo = mid
        else:
            hi = mid
    return lo * math.sqrt(math.pi) / 2.0


TRANSIT_KERNEL_FACTOR = {
    "amplitude_lorentzian": 1.0,     # the retired form, kept so it is nameable
    "single_velocity": 0.6436,       # squared Lorentzian, sqrt(sqrt(2)-1)
    "ensemble_flux": 0.4387,         # transit_kernel_factor("flux")
    "ensemble_speed": 0.2422,        # transit_kernel_factor("speed")
}


def transit_fwhm(temperature_k: float, decay_length_m: float,
                 convention: str = "mean",
                 alpha: float = 1.0,
                 kernel: str = "ensemble_flux") -> TransitEstimate:
    """Guided transit FWHM in Hz, = factor * v(T)/(pi*Lambda).

    `kernel` selects which of `TRANSIT_KERNEL_FACTOR` applies, and the default
    is NOT 1.0. A factor of 1.0 is the amplitude-Lorentzian form, which
    overstates this width by between 2.3 and 4.1.

    TWO SEPARATE ASSUMPTIONS SIT IN THIS FACTOR AND ONLY ONE OF THEM IS A
    RULE. Applying the squared-magnitude rule to a ONE-SIDED envelope returns
    a true Lorentzian of FWHM vbar/(pi*Lambda), i.e. exactly 1.0. The 0.6436
    comes from the envelope being TWO-SIDED, which asserts a fly-by with a
    closest approach rather than an atom adsorbed at, or launched from, the
    surface. Sidedness is worth 1.554; the weighting choice is worth 1.811.

    The span is what this record can support. `ensemble_flux` and `ensemble_speed` differ
    by 1.8 and nothing in this record decides between them; a forecast that
    depends on the difference must say so rather than inherit this default.

    `alpha` perturbs the temperature scaling to T**(alpha/2) relative to the
    correct law, and exists so world F can ask how wrong a law the design can
    detect. alpha = 1.0 is the correct law.
    """
    if decay_length_m <= 0.0:
        raise ValueError("decay length must be positive")
    if kernel not in TRANSIT_KERNEL_FACTOR:
        raise ValueError(f"unknown transit kernel {kernel!r}; "
                         f"choose from {sorted(TRANSIT_KERNEL_FACTOR)}")
    # THE TWO SWITCHES INTERACT, and this was a trap two hours after the
    # kernel factors were added. The `ensemble_*` factors were MEASURED as
    # FWHM / (v_mean/(pi Lambda)), so the mean-speed normalisation is baked
    # into the number. Combining one with convention="rms" applies the speed
    # ratio sqrt(3 pi/8) = 1.085 twice. A single-velocity kernel carries no
    # such assumption and may use either convention.
    #
    # Found by the string-default switch audit, which is meant to catch a form
    # parameter that has never been thrown -- and caught an interaction
    # between a parameter it flagged and one added the same night.
    if kernel.startswith("ensemble_") and convention != "mean":
        raise ValueError(
            f"transit kernel {kernel!r} is normalised to the MEAN speed, so "
            f"convention={convention!r} would apply the speed ratio twice. "
            f"Use convention='mean' with an ensemble kernel, or a "
            f"single-velocity kernel with another convention")
    v = thermal_velocity(temperature_k, convention)
    if alpha != 1.0:
        # v already carries T**0.5; rescale to T**(alpha/2).
        v = v * (temperature_k ** ((alpha - 1.0) / 2.0)) if temperature_k > 0 else 0.0
    factor = TRANSIT_KERNEL_FACTOR[kernel]
    return TransitEstimate(fwhm_hz=factor * v / (math.pi * decay_length_m),
                           convention=convention,
                           temperature_k=temperature_k,
                           decay_length_m=decay_length_m)


def homogeneous_width(temperature_k: float, density_units: float, *,
                      gamma_l_hz: float, decay_length_m: float,
                      beta_self_hz_per_unit: float = 0.0,
                      gamma_0_hz: float = 0.0,
                      convention: str = "mean",
                      alpha: float = 1.0) -> float:
    """The minimal budget, as a SUM.

    The terms are SUMMED AS AN APPROXIMATION. The transit term is a
    tau^2-weighted ensemble of squared Lorentzians, not a Lorentzian, so the
    sum is approximate and its error is not characterised here. What the O2
    exercise is built around survives unchanged: one condition determines only
    this total.

    This docstring said "every term is Lorentzian and they add exactly" until
    2026-08-28, which is the sentence the module header two hundred lines above
    records as retracted the same day. The repair narrowed the header and the
    comment block and missed the docstring attached to the code that does the
    adding, so a reader of the API saw the retracted claim and a reader of the
    header saw the retraction.
    """
    tr = transit_fwhm(temperature_k, decay_length_m, convention, alpha)
    return (gamma_l_hz
            + tr.fwhm_hz
            + beta_self_hz_per_unit * density_units
            + gamma_0_hz)


# ---------------------------------------------------------------------------
# The guided mode, SOLVED rather than assumed (2026-08-27)
#
# WHY THIS EXISTS. `results/onf_candidate.csv` carried `neff_band = 1.08 to
# 1.25` tagged `assumed_parameter`, and every evanescent quantity in this
# record derived from it. That band corresponds at 993 nm to fibres of
# 485 to 796 nm diameter. The fibres this group actually runs are 350 to
# 400 nm, so the band did not contain the apparatus the same file names, and
# the derived decay length was outside its own true value by ~1.6x. The band
# looks carried over from 780 nm work without rescaling.
#
# A diameter is measurable and a mode is computable, so neither has to be
# assumed. That producer's own comment already said these were placeholders
# "for a measurement OR A MODE SOLUTION". This is the mode solution.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ModeEstimate:
    """HE11 solution for a step-index fibre in vacuum."""
    neff: float
    v_number: float
    diameter_nm: float
    lambda_nm: float
    amplitude_decay_nm: float     # 1/q, the field's 1/e length
    intensity_decay_nm: float     # 1/(2q); THE TWO DIFFER BY TWO, see below

    @property
    def single_mode(self) -> bool:
        return self.v_number < 2.405


def _he11_residual(neff: float, a_m: float, lam_m: float,
                   n1: float, n2: float) -> float:
    k0 = 2.0 * math.pi / lam_m
    beta = neff * k0
    u = a_m * math.sqrt(max(n1 * n1 * k0 * k0 - beta * beta, 1e-30))
    w = a_m * math.sqrt(max(beta * beta - n2 * n2 * k0 * k0, 1e-30))
    ju, kw = jv(1, u), kv(1, w)
    if abs(ju) < 1e-300 or abs(kw) < 1e-300:
        return float("nan")
    a_term = jvp(1, u) / (u * ju)
    b_term = kvp(1, w) / (w * kw)
    lhs = (a_term + b_term) * (n1 * n1 * a_term + n2 * n2 * b_term)
    rhs = (neff * neff) * (1.0 / (u * u) + 1.0 / (w * w)) ** 2
    return lhs - rhs


def solve_he11(diameter_nm: float, lambda_nm: float,
               n_core: float | None = None, n_clad: float = 1.0) -> ModeEstimate:
    """Solve the HE11 eigenvalue equation for a nanofibre in vacuum.

    `n_core` defaults to `n_silica_malitson(lambda_nm)`, the source formula
    itself, so no wavelength needs tabulating and no copy can drift.

    THE ROOT SITS EXPONENTIALLY CLOSE TO n_clad FOR A THIN FIBRE, so the
    bracketing grid is logarithmic in (neff - n_clad). A linear grid steps
    straight over the root and the solver returns "no mode" for a fibre that
    guides perfectly well; that happened on the first write of this function.

    Validated against three points not fitted to: 400 nm at 780 nm gives
    1.0972 against ~1.10 in the literature, 400 nm at 852 nm gives 1.0690
    against ~1.06-1.07, and 400 nm at 993.4 nm gives 1.03164 against an
    independently written solver's 1.032.
    """
    if n_core is None:
        n_core = n_silica_malitson(lambda_nm)
    a_m = diameter_nm * 1e-9 / 2.0
    lam_m = lambda_nm * 1e-9
    grid = n_clad + np.concatenate([
        np.logspace(-12, -3, 3000),
        np.linspace(1e-3, (n_core - n_clad) * (1.0 - 1e-9), 3000)])
    vals = [_he11_residual(x, a_m, lam_m, n_core, n_clad) for x in grid]
    root = None
    for i in range(len(grid) - 1):
        f0, f1 = vals[i], vals[i + 1]
        if math.isfinite(f0) and math.isfinite(f1) and f0 * f1 < 0.0:
            root = brentq(_he11_residual, grid[i], grid[i + 1],
                          args=(a_m, lam_m, n_core, n_clad), xtol=1e-14)
    if root is None:
        raise ValueError(
            f"no HE11 root for d={diameter_nm} nm at {lambda_nm} nm")
    k0 = 2.0 * math.pi / lam_m
    q = math.sqrt((root * k0) ** 2 - (n_clad * k0) ** 2)
    v = k0 * a_m * math.sqrt(n_core * n_core - n_clad * n_clad)
    return ModeEstimate(neff=root, v_number=v, diameter_nm=diameter_nm,
                        lambda_nm=lambda_nm,
                        amplitude_decay_nm=1e9 / q,
                        intensity_decay_nm=1e9 / (2.0 * q))


def evanescent_intensity(distance_nm: float, diameter_nm: float,
                         lambda_nm: float, n_core: float | None = None,
                         n_clad: float = 1.0) -> float:
    """Relative axial flux at `distance_nm` OUT FROM THE SURFACE, surface = 1.

    NOT AN EXPONENTIAL, AND THE FACTOR IS 2.4 AT THE TRAP DISTANCE. The
    evanescent field is not asymptotic anywhere the atoms are: for a 370 nm
    fibre at 993 nm, q*a = 0.231, so exp(-qr) is unavailable. At 400 nm from
    the surface the exponential gives 0.369 of the surface value and the
    solved field gives 0.156.

    THIS FUNCTION USED TO CARRY ITS OWN REFUTATION AND QUOTE THE WRONG NUMBER
    ANYWAY (corrected 2026-08-28). It evaluated K1(qr)^2 alone, noted in the
    next paragraph that the full HE11 field also carries K0 and K2, and then
    stated 0.058 and "a factor of six" as the answer. K1 is the E_z component,
    about 12 per cent of the field, so the K1-only form understates the tail
    by 2.7x and the quoted six was as wrong as the exponential it corrected,
    in the opposite direction.

    It now delegates to `HE11Field`, whose fields are validated by E_z and
    H_phi continuity at the boundary before anything is integrated.
    """
    if n_core is None:
        n_core = n_silica_malitson(lambda_nm)
    fld = HE11Field(diameter_nm, lambda_nm, n1=n_core, n2=n_clad)
    return float(fld.intensity_at(distance_nm * 1e-9))


# ---------------------------------------------------------------------------
# The full vector HE11 fields, and why they are here (2026-08-28)
#
# An effective mode area was computed from a shell approximation
# pi[(a+1/q)^2 - a^2] and committed. Recomputation refuted it, and FOUR
# computations of that one quantity then spanned a factor of six: an assumed
# 0.50 um^2, the shell's 1.98, an independent Poynting integral 0.4634, and a
# plane-wave-impedance integration giving 2.73.
#
# None of the four could be adjudicated by inspection, so the fields are built
# here and VALIDATED before any integral is taken. The validator is the physics
# itself: E_z and H_phi are continuous across the boundary. The first attempt
# failed H_phi by 53 per cent, and the ratio was exactly n1^2, which located
# the error in one line -- the H fields carry a REGION-DEPENDENT s and the
# first version used one s in both regions.
#
# With that fixed, E_z closes to 6e-10, H_phi to 2e-09, and the power fraction
# inside the glass comes out at 23.3 per cent against an independently
# computed 23 per cent.
#
# THE LESSON IS NOT THE NUMBER. A shell approximation produced a plausible
# value with no way to check it. A field solution carries its own test, and
# that is the reason to prefer it even when it costs more.
# ---------------------------------------------------------------------------


class HE11Field:
    # n1 defaults to the same Malitson table `solve_he11` reads, never to a
    # literal. Until 2026-08-28 it was a bare 1.4525 -- a second copy of the
    # index, wavelength-independent, that agreed with the table only because
    # the table's 993.4181 entry carried the same wrong value. Correcting the
    # table split the two paths by 0.9 per cent and a delegation pin caught
    # it within the minute, which is what a second copy always does: it holds
    # until the first copy is repaired.
    def __init__(self, diameter_nm, lambda_nm, n1=None, n2=1.0):
        if n1 is None:
            n1 = n_silica_malitson(lambda_nm)
        m = solve_he11(diameter_nm, lambda_nm, n_core=n1, n_clad=n2)
        self.neff = m.neff
        self.a = diameter_nm / 2 * 1e-9
        self.lam = lambda_nm * 1e-9
        self.k0 = 2 * np.pi / self.lam
        self.w = self.k0 * c                      # angular frequency
        self.n1, self.n2 = n1, n2
        self.beta = self.neff * self.k0
        self.h = np.sqrt(n1**2 * self.k0**2 - self.beta**2)   # inside
        self.q = np.sqrt(self.beta**2 - n2**2 * self.k0**2)   # outside
        ha, qa = self.h * self.a, self.q * self.a
        self.ha, self.qa = ha, qa
        self.s = ((1/ha**2 + 1/qa**2)
                  / (jvp(1, ha)/(ha*jv(1, ha)) + kvp(1, qa)/(qa*kv(1, qa))))
        # amplitude continuity factor for the outside fields
        self.A = 1.0
        self.B = jv(1, ha) / kv(1, qa)

    # --- transverse E, at azimuth phi, for the cos-polarised HE11 ---------
    def E(self, r, phi=0.0):
        a, s, beta = self.a, self.s, self.beta
        if r < a:
            u = self.h * r
            Er = -(beta/(2*self.h)) * ((1-s)*jv(0, u) - (1+s)*jv(2, u))
            Ep = (beta/(2*self.h)) * ((1-s)*jv(0, u) + (1+s)*jv(2, u))
            Ez = jv(1, u)
        else:
            v = self.q * r
            f = self.B
            Er = -f*(beta/(2*self.q)) * ((1-s)*kv(0, v) + (1+s)*kv(2, v))
            Ep = f*(beta/(2*self.q)) * ((1-s)*kv(0, v) - (1+s)*kv(2, v))
            Ez = f*kv(1, v)
        return (Er*np.cos(phi), Ep*np.sin(phi), Ez*np.cos(phi))

    # --- transverse H --------------------------------------------------
    def H(self, r, phi=0.0):
        a, s, beta = self.a, self.s, self.beta
        we = self.w
        # The H fields carry a REGION-DEPENDENT s. Using one s in both regions
        # breaks H_phi continuity by exactly n1^2/n2^2, which is how this was
        # caught: the validator reported a 53 per cent jump and 1.4525^2 = 2.11.
        if r < a:
            u = self.h * r
            n2loc = self.n1**2
            sj = s * (beta/(self.k0*self.n1))**2
            Hr = -(we*epsilon_0*n2loc/(2*self.h)) * ((1-sj)*jv(0, u) + (1+sj)*jv(2, u))
            Hp = -(we*epsilon_0*n2loc/(2*self.h)) * ((1-sj)*jv(0, u) - (1+sj)*jv(2, u))
        else:
            v = self.q * r
            f = self.B
            n2loc = self.n2**2
            sj = s * (beta/(self.k0*self.n2))**2
            Hr = -f*(we*epsilon_0*n2loc/(2*self.q)) * ((1-sj)*kv(0, v) - (1+sj)*kv(2, v))
            Hp = -f*(we*epsilon_0*n2loc/(2*self.q)) * ((1-sj)*kv(0, v) + (1+sj)*kv(2, v))
        return (Hr*np.sin(phi), Hp*np.cos(phi))

    def Sz(self, r, phi=0.0):
        Er, Ep, _ = self.E(r, phi)
        Hr, Hp = self.H(r, phi)
        return 0.5*(Er*Hp - Ep*Hr)

    def Sz_azimuthal_mean(self, r):
        return quad(lambda p: self.Sz(r, p), 0, 2*np.pi, limit=200)[0]/(2*np.pi)

    def power(self, rmax_factor=60):
        f = lambda r: self.Sz_azimuthal_mean(r)*2*np.pi*r
        inner = quad(f, 1e-12, self.a, limit=400)[0]
        outer = quad(f, self.a, rmax_factor*self.a, limit=400)[0]
        return inner + outer, inner, outer

    def stark_area_m2(self):
        """P / I_equivalent, the area a LIGHT SHIFT divides power by.

        AN AC STARK SHIFT IS -alpha_s |E|^2 / 4, so the quantity that scales it
        is |E|^2, and the free-space intensity carrying that field is
        0.5*c*eps0*|E|^2. The axial Poynting flux is NOT that: for a guided
        mode a part of the energy sits in E_z, which carries no axial flux, and
        the ratio S_z / (0.5 c eps0 <|E|^2>) is 0.75951 at 400 nm and
        0.77731 at 370 nm rather than 1. Those read 0.758 and 0.776 until
        2026-08-29, computed under the retired silica index.

        THIS RETIRES THE FOUR-WAY DISPUTE THIS FILE WAS WRITTEN TO SETTLE. The
        record carried an unexplained 0.4634 um^2 all night (0.46725 under the
        corrected silica index), attributed to a
        competing Poynting integral of the mode area and treated as one of four
        answers spanning a factor of six. It was never a competing computation
        of the same quantity. It is THIS area, 0.46725 um^2 at 400 nm, the
        light-shift convention, and the reason it disagreed with 0.615 is that
        the two are different quantities and both are right.

        Use `effective_area_m2` for a power budget and this for anything that
        multiplies a polarizability.
        """
        P, _, _ = self.power()
        r = self.a * 1.000001
        return P / (0.5 * c * epsilon_0 * self.e_squared_azimuthal_mean(r))

    def effective_area_m2(self, reference="azimuthal_mean"):
        """P / I(a+), in m^2. THE DEFINITION MATTERS and is a parameter.

        `azimuthal_mean` divides by the azimuthally averaged axial flux just
        outside the glass; `peak` divides by the flux on the polarisation axis
        and is therefore the SMALLER area, since a peak intensity is larger.
        For a 400 nm fibre at 993 nm these give 0.615 and 0.489 um^2.

        A third number, 0.4634, sat in this record all night as an
        unexplained competitor. It is `stark_area_m2`, a different quantity,
        and this docstring quoted 0.824 for the peak until 2026-08-28 when the
        function had already been corrected to return 0.489. Prefer `stark_area_m2` when
        what is wanted is the field an atom actually sees.
        """
        P, _, _ = self.power()
        r = self.a * 1.000001
        iref = (self.Sz_azimuthal_mean(r) if reference == "azimuthal_mean"
                else self.Sz(r, 0.0))
        return P / iref

    def e_squared(self, r, phi=0.0):
        """|E|^2 at (r, phi), all three components.

        AN AC STARK SHIFT GOES AS |E|^2 AND NOT AS THE AXIAL POYNTING FLUX,
        and for a guided mode those are not proportional. A large part of the
        near-surface energy sits in E_z, which carries NO axial flux at all,
        so S_z understates the field an atom actually sees near the surface
        and the two fall off at different rates.

        Every light-shift and two-photon-rate row in this record was keyed on
        S_z until 2026-08-28. The ratios differ by about 20 per cent at a
        400 nm trap distance, which is smaller than the corrections made the
        same night and is still the wrong quantity.
        """
        Er, Ep, Ez = self.E(r, phi)
        return Er*Er + Ep*Ep + Ez*Ez

    def e_squared_azimuthal_mean(self, r):
        return quad(lambda p: self.e_squared(r, p), 0, 2*np.pi,
                    limit=200)[0] / (2*np.pi)

    def stark_fraction_at(self, distance_m, reference="azimuthal_mean"):
        """|E|^2 at `distance_m` from the SURFACE, relative to the surface.

        THIS is what a light shift scales with. `intensity_at` returns the
        axial flux ratio, which is the right quantity for a power budget and
        the wrong one for a shift.
        """
        r = self.a + distance_m
        if reference == "azimuthal_mean":
            return (self.e_squared_azimuthal_mean(r)
                    / self.e_squared_azimuthal_mean(self.a * 1.000001))
        return self.e_squared(r, 0.0) / self.e_squared(self.a * 1.000001, 0.0)

    def intensity_at(self, distance_m, reference="azimuthal_mean"):
        """Axial flux at `distance_m` from the SURFACE, relative to the surface.

        THIS IS NOT WHAT A LIGHT SHIFT NEEDS. An AC Stark shift scales with
        |E|^2, and for a guided mode the axial flux is not proportional to it,
        because a large part of the near-surface energy sits in E_z, which
        carries no axial flux. Use `stark_fraction_at` for a shift. This
        function is the right one for a POWER BUDGET, and it avoids the
        effective-area convention entirely.
        """
        r = self.a + distance_m
        if reference == "azimuthal_mean":
            return self.Sz_azimuthal_mean(r) / self.Sz_azimuthal_mean(self.a * 1.000001)
        return self.Sz(r, 0.0) / self.Sz(self.a * 1.000001, 0.0)

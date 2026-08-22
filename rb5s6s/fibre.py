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
Lorentzian transit contribution from a temperature-independent homogeneous
one. `q_surf(t)`, a detection-channel object, and everything else wait until
that is answered.

THIS MODULE IS A LEAF. It imports core; core never imports it. Enforced by
tests/test_module_boundaries.py, not by intention.

THE TRANSIT KERNEL IS LORENTZIAN, which is the whole reason this is hard.
Its FWHM is v/(pi*Lambda), and a Lorentzian transit term ADDS EXACTLY to every
other Lorentzian term in the budget. So at a single temperature it has no
separate existence at all, and only the ladder can separate it.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .constants import GAMMA_NAT_HZ  # noqa: F401  (core import; leaf direction)

K_B = 1.380649e-23
M_RB87 = 86.909180527 * 1.66053906660e-27

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


def transit_fwhm(temperature_k: float, decay_length_m: float,
                 convention: str = "mean",
                 alpha: float = 1.0) -> TransitEstimate:
    """Lorentzian transit FWHM = v(T)/(pi*Lambda), in Hz.

    `alpha` perturbs the temperature scaling to T**(alpha/2) relative to the
    correct law, and exists so world F can ask how wrong a law the design can
    detect. alpha = 1.0 is the correct law.
    """
    if decay_length_m <= 0.0:
        raise ValueError("decay length must be positive")
    v = thermal_velocity(temperature_k, convention)
    if alpha != 1.0:
        # v already carries T**0.5; rescale to T**(alpha/2).
        v = v * (temperature_k ** ((alpha - 1.0) / 2.0)) if temperature_k > 0 else 0.0
    return TransitEstimate(fwhm_hz=v / (math.pi * decay_length_m),
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

    Every term is Lorentzian and they add exactly, which is the fact the whole
    O2 exercise is built around: one condition determines only this total.
    """
    tr = transit_fwhm(temperature_k, decay_length_m, convention, alpha)
    return (gamma_l_hz
            + tr.fwhm_hz
            + beta_self_hz_per_unit * density_units
            + gamma_0_hz)

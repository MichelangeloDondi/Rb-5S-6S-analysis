"""Blackbody radiation as a CAMPAIGN BOUNDARY: how hot the cell may run.

WHAT THIS IS FOR. Raising the cell temperature is the density lever, and the
density lever is what a self-broadening measurement lives on. It is also what
raises the thermal field the atoms sit in. This module answers the design
question that pairing creates: **above which temperature does blackbody
radiation enter the systematic budget at a given target precision?** The
answer is a FAMILY indexed by that target, not a single ceiling, because a
campaign chasing 10 kHz and one chasing 1 kHz have different ceilings.

THE ATOMIC DATA IS SEPARATE FROM THE EXPERIMENT. `Transition` and
`occupation` know nothing about rubidium. `RB_5S6S_SHIFT_HZ` is one preset,
and another species is another preset.

WHAT IS NOT RECOMPUTED HERE, deliberately. The differential 5S-6S shift is a
PRINCIPAL VALUE through the 6S-6P poles, and `scripts/run_blackbody_channels.py`
records three earlier attempts that were each wrong in an instructive way: a
uniform grid that wobbled by 10 Hz depending on how it straddled the poles, a
band cut that left an unquantified residue, and a symmetric pairing whose
windows merged the two poles so its centre was the midpoint rather than a
pole. Reimplementing that integral here would create a second source of truth
for a delicate number. The committed values are carried instead, with the
scaling fitted to them and its validity domain stated.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

__all__ = [
    "Transition",
    "occupation",
    "einstein_a",
    "stimulated_rate",
    "RB_5S6S_SHIFT_HZ",
    "shift_hz",
    "t_max",
]

_H = 6.62607015e-34
_C = 299792458.0
_KB = 1.380649e-23
_HBAR = _H / (2.0 * math.pi)
_EPS0 = 8.8541878128e-12
_E_C = 1.602176634e-19
_A0 = 5.29177210903e-11


@dataclass(frozen=True)
class Transition:
    """One radiative channel: a wavelength, a dipole and a label.

    ``d_au`` is the reduced dipole matrix element in atomic units, which is
    how the polarizability tables in this repository carry it.
    """

    label: str
    wavelength_m: float
    d_au: float

    def occupation(self, t_k: float) -> float:
        return occupation(self.wavelength_m, t_k)

    def einstein_a(self) -> float:
        return einstein_a(self.wavelength_m, self.d_au)

    def stimulated_rate(self, t_k: float) -> float:
        return stimulated_rate(self.wavelength_m, self.d_au, t_k)


def occupation(lam_m: float, t_k: float) -> float:
    """Planck occupation number of one mode. The number that sets everything.

    At 403 K the photon spectrum peaks near 9.1 um, so a cascade line at 1.3 um
    sits far out on the exponential tail and its occupation is of order 1e-12.
    That single fact is why blackbody light does not re-drive this cascade.
    """
    if t_k <= 0.0:
        raise ValueError(f"temperature must be positive: {t_k}")
    x = _H * _C / (lam_m * _KB * t_k)
    return 1.0 / math.expm1(x) if x < 700.0 else 0.0


def einstein_a(lam_m: float, d_au: float) -> float:
    """Spontaneous rate from a reduced dipole, per second."""
    omega = 2.0 * math.pi * _C / lam_m
    d = d_au * _E_C * _A0
    return omega ** 3 * d ** 2 / (3.0 * math.pi * _EPS0 * _HBAR * _C ** 3 * 2)


def stimulated_rate(lam_m: float, d_au: float, t_k: float) -> float:
    """Blackbody-driven rate on this channel: the spontaneous rate times nbar."""
    return einstein_a(lam_m, d_au) * occupation(lam_m, t_k)


# MEASURED-HERE, provenance results/blackbody_channels.csv quantity
# `bbr_stark_shift`: the differential 5S-6S shift on the transition axis in Hz,
# with the committed alpha_6s band carried through as the error. Reproduced
# exactly under the environment of record on 2026-08-19.
RB_5S6S_SHIFT_HZ: dict[float, tuple[float, float]] = {
    343.15: (-79.9349, 0.3396),
    363.15: (-101.983, 0.4332),
    383.15: (-128.738, 0.5469),
    403.15: (-160.963, 0.6838),
}

# Fitted to the four committed points: d ln|shift| / d ln T is 4.30, 4.35 and
# 4.39 across the three intervals. A pure quadratic Stark shift in a thermal
# field would give exactly 4; the excess is the near-resonant 6S-6P
# contribution, whose weight grows with temperature. Using 4 rather than this
# would understate the shift at high T, which is the direction that matters
# for a ceiling.
_SHIFT_EXPONENT = 4.35
_SHIFT_ANCHOR_T = 403.15
_SHIFT_ANCHOR_HZ = 160.963
_SHIFT_ANCHOR_ERR = 0.6838
# The committed points span 343 to 403 K. Extrapolation is flagged rather than
# silently allowed, because the exponent itself drifts across that span.
_FITTED_RANGE = (343.15, 403.15)


def shift_hz(t_k: float, with_error: bool = False):
    """Magnitude of the differential blackbody shift at ``t_k``, in Hz.

    Interpolates the committed values through the fitted power law. Outside
    343 to 403 K this is an EXTRAPOLATION of an exponent that is itself
    drifting, and the returned value should be treated as an envelope.
    """
    if t_k <= 0.0:
        raise ValueError(f"temperature must be positive: {t_k}")
    ts = sorted(RB_5S6S_SHIFT_HZ)
    if ts[0] <= t_k <= ts[-1]:
        # INSIDE the committed span, interpolate the committed points in
        # log-log rather than riding a single fitted exponent. The exponent
        # drifts from 4.30 to 4.39 across this range, so a single power law
        # anchored at one end is 0.1 per cent out at the other, and there is
        # no reason to accept that where the points themselves exist.
        hi = next(i for i, tt in enumerate(ts) if tt >= t_k)
        if ts[hi] == t_k:
            v, e = RB_5S6S_SHIFT_HZ[t_k]
            return (abs(v), e) if with_error else abs(v)
        t0, t1 = ts[hi - 1], ts[hi]
        (v0, e0), (v1, e1) = RB_5S6S_SHIFT_HZ[t0], RB_5S6S_SHIFT_HZ[t1]
        w = math.log(t_k / t0) / math.log(t1 / t0)
        value = abs(v0) * (abs(v1) / abs(v0)) ** w
        err = e0 * (e1 / e0) ** w
    else:
        scale = (t_k / _SHIFT_ANCHOR_T) ** _SHIFT_EXPONENT
        value, err = _SHIFT_ANCHOR_HZ * scale, _SHIFT_ANCHOR_ERR * scale
    return (value, err) if with_error else value


def is_extrapolated(t_k: float) -> bool:
    """True where ``shift_hz`` leaves the range its exponent was fitted on."""
    return not (_FITTED_RANGE[0] <= t_k <= _FITTED_RANGE[1])


def t_max(target_hz: float, corrected: bool = False) -> float:
    """The temperature at which blackbody enters the budget, in kelvin.

    THE FAMILY, not a number: pass the target precision and receive its
    ceiling.

    ``corrected=False`` is the conservative branch, for a campaign that does
    not subtract the shift: the ceiling is where the SHIFT ITSELF reaches the
    target. ``corrected=True`` is for a campaign that computes and subtracts
    it, where only the shift's own uncertainty remains, so the ceiling is far
    higher. The gap between the two branches is the value of doing the
    correction, and it is large.
    """
    if target_hz <= 0.0:
        raise ValueError(f"target precision must be positive: {target_hz}")
    anchor = _SHIFT_ANCHOR_ERR if corrected else _SHIFT_ANCHOR_HZ
    return _SHIFT_ANCHOR_T * (target_hz / anchor) ** (1.0 / _SHIFT_EXPONENT)

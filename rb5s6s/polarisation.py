"""What an imperfect polarisation does to this line, and what it cannot do.

THE QUESTION THIS ANSWERS. The two-photon 5S to 6S line is protected against
a laboratory magnetic field because the driving operator is scalar: it takes
m_F to the same m_F, and the shift then cancels between two S states with the
same g_F. That protection belongs to Delta m_F = 0 and to nothing else, so
the components that break it are the ones worth sizing.

WHY Delta m_F = +-2 IS NOT ON THE LIST, stated as a physicist would check it
rather than as a rank. Two sigma-plus photons carry two units of angular
momentum, and the natural expectation is that the atom takes them. IT CANNOT.
The electron's m_J runs over exactly two values in an S state, minus one half
and plus one half, so the largest change any operator can make is ONE unit.
The nucleus could absorb the other unit, but the electric dipole operator
does not touch the nucleus. So a sigma-plus sigma-plus pair has nowhere to
put its second unit and the matrix element is ZERO, not small: that
polarisation combination does not drive an S to S two-photon transition at
all, which is why this spectroscopy is done with linear or with opposite
circular light.

Zero at that level of description, and then the usual caveat: the statement
relies on the electronic and nuclear coordinates factorising, which the
intermediate states spoil through their own hyperfine structure. At this
drive the mixing is one part in 1e5 in amplitude, so 1e-10 in rate. If the
channel WERE open it would matter, since a Delta m_F = 2 component carries
2 g_F mu_B B with nothing cancelling, 700 kHz at the Earth's field on the
rubidium-87 lines, which is 13 per cent of the observed width. It is not
open.

WHAT ELLIPTICITY ACTUALLY DOES, which is two different things of very
different size.

ROUTE 1, THE VECTOR LIGHT SHIFT. Elliptical light shifts each m_F sublevel
by an amount odd in m_F. That is a real spread of the line rather than a
shift of it, and its size is set by the ratio of the differential VECTOR
polarizability to the differential scalar one. Computed from this package's
own line lists at the drive wavelength that ratio is about 0.017, so the
spread is under five kilohertz at the campaign's highest power even for
FULLY circular light, against per-condition width errors near thirty. It is
proportional to power, which is the only reason to carry it at all: that is
the one signature it shares with the light shift being measured.

ROUTE 2, A POLARISATION MISMATCH BETWEEN THE TWO BEAMS. **RETRACTED
2026-08-20, the same day it was written, and the retraction is the more
useful result.** The first version of this module said that a mismatch opens
a rank-1 coupling, makes Delta m_F = +-1 weakly allowed, and lets those
components carry the full uncancelled g_F mu_B B, 350 kHz at the Earth's
field. THAT CHANNEL DOES NOT EXIST, for a reason that closes it far more
firmly than any bound.

Write the two-photon amplitude out:

    A = sum_n [ <f|d.e2|n><n|d.e1|i> / (E_n - E_i - hbar w1)
              + <f|d.e1|n><n|d.e2|i> / (E_n - E_i - hbar w2) ]

Both photons come from ONE laser, so w1 = w2, the two denominators are equal,
and the bracket is manifestly SYMMETRIC under exchanging e1 and e2. A
symmetric bilinear in the two polarisation vectors has no antisymmetric part,
and the antisymmetric part is exactly rank 1. So for a DEGENERATE two-photon
transition the operator carries ranks 0 and 2 only, whatever the two
polarisations are:

    rank 0, proportional to e1.e2   ->  Delta m_F = 0     the line
    rank 1, absent by the symmetry  ->  Delta m_F = +-1   not available
    rank 2, zero for J = 1/2        ->  Delta m_F = +-2   not available

Only Delta m_F = 0 survives, and a sigma-pi pair's Delta m of one lives in
the same two unavailable ranks.

RANK 1 NEEDS TWO THINGS AT ONCE, and the first version of this docstring
named only one. Writing the two time orderings with denominators D1 and D2,
the rank-1 weight is

    (1/D1 - 1/D2)  x  (e1 x e2)

so it vanishes if the two photons have the SAME ENERGY, whatever the
polarisations, and it vanishes if the two polarisation vectors are PARALLEL,
whatever the energies. Saying the transition is protected at the level of the
matrix element rather than by a cross product was therefore half the story,
and the half it dropped is the one this apparatus actually leans on.

BOTH FACTORS ARE SMALL HERE, AND NEITHER IS ZERO. On 2026-08-20 it became clear
that the Doppler-free geometry makes the energy factor
nonzero for every atom that is moving, which is the whole ensemble. In the
atom's rest frame the forward photon is blue-shifted and the retro photon is
red-shifted, so the pair the Doppler-free signal is built from differs by
2 nu v / c. At 130 C the one-dimensional rms speed is 196 m/s and that split
is 395 MHz, sixteen times the 25 MHz an EOM sideband pair would give, and the
energy factor is 5.2e-6 in amplitude against the 75.3 THz detuning.

What keeps the channel shut is therefore the POLARISATION factor, which an
ideal retro sets to zero exactly. A mismatch of angle theta reopens rank 1 at
sin(theta) x 5.2e-6 in amplitude, which is 2.1e-13 in rate at five degrees.
`rank_one_leak_rate` computes it. The retraction's CONCLUSION stands, since
that is three orders below the cooperative pair channel and two below the
hyperfine one, but it stands on two legs rather than on the one this module
first claimed, and the EOM sideband case is the smaller of the two energy
splits rather than the only one.

THE DISTINCTION THAT MATTERS, and the one the first version missed. The
TRANSITION operator is built from e1 e2, two absorptions, and is symmetric.
The LIGHT SHIFT operator is built from e* e, an absorption and a stimulated
emission, and its antisymmetric part e* x e does NOT vanish for elliptical
light. That is the vector polarizability of route 1, which is real. So
ellipticity shifts LEVELS and cannot open transition CHANNELS, and conflating
the two is what produced the retracted paragraph.

The sizing functions below are kept because they answer a question worth
being able to answer, WHAT IT WOULD COST IF THE CHANNEL WERE OPEN, which is
what a ceiling test needs. They do not describe a mechanism this apparatus
has.

THE ISOTOPES STILL SUPPLY A TEST, and it is now a CONSISTENCY CHECK rather
than a constraint. Any g_F-squared-scaling broadening, from this mechanism or
from any other, must appear 2.25 times larger on the rubidium-87 lines than
on the rubidium-85 ones. The committed per-condition widths put that
difference at +4 +/- 18 kHz, consistent with zero, which is what the
selection rule above predicts and is worth having on the record as agreement
rather than as a limit. See `scripts/run_polarisation_bound.py`.
"""

from __future__ import annotations

import math

__all__ = ["doppler_photon_split_hz", "rank_one_leak_rate",
           "hyperfine_mixing_rate", "HFS_SPLIT_5P_HZ",
           "vector_ratio", "vector_spread_mhz", "zeeman_satellite_mhz",
           "mismatch_intensity", "extra_width_mhz", "GF_S_HALF"]

# g_F for an S1/2 state is +-g_J/(2I+1) to the accuracy that matters here.
GF_S_HALF = {"87Rb": 0.5, "85Rb": 1.0 / 3.0}

MU_B_MHZ_PER_UT = 9.2740100783e-24 / 6.62607015e-34 * 1e-6 / 1e6


# 87Rb 5P hyperfine manifold splittings, lowest F to highest, in Hz. These
# are the ONE external input this module adds beyond the committed line lists.
# Steck's rubidium-87 data, from the standard A and B constants: 5P1/2 is
# 2A with A = 407.24 MHz, and 5P3/2 spans F=0 to F=3.
HFS_SPLIT_5P_HZ = {"5P1/2": 814.5e6, "5P3/2": 496.6e6}


def hyperfine_mixing_rate() -> dict:
    """The single-atom Delta m_F = +-1 leakage, COMPUTED rather than asserted.

    The selection rule above holds to the extent that electronic and nuclear
    coordinates factorise, and the intermediate P states spoil that through
    their own hyperfine structure. The admixture is the hyperfine splitting
    over the detuning, and the rate is its square.

    WHY THIS FUNCTION EXISTS. An independent pass on 2026-08-20 found that
    1.1e-5, 6.0e-6 and 1.2e-10 appeared in three files and were computed in
    none, held up by mutual citation. They are all correct. They are now
    derived here from the committed detunings and the splittings above, so a
    line list that moves takes them with it.

    The `rate` key is the SUM over both fine-structure legs. The wiki's
    long-standing 1.2e-10 is the dominant leg alone, which is also returned.
    """
    from .polarizability import LINES_5S, E_6S_CM
    hw = E_6S_CM / 2.0
    out = {}
    for name, (term, _, _) in zip(("5P1/2", "5P3/2"), LINES_5S[:2]):
        detuning_hz = (term - hw) * 2.99792458e10
        out[name] = HFS_SPLIT_5P_HZ[name] / detuning_hz
    dominant = out["5P1/2"] ** 2
    return {"amplitudes": out,
            "rate_dominant_leg": dominant,
            "rate": sum(a * a for a in out.values())}


def doppler_photon_split_hz(t_c: float = 130.0, isotope: str = "87Rb") -> float:
    """Atom-frame energy difference between the two absorbed photons, in Hz.

    The Doppler-free signal is built from ONE forward and ONE retro photon.
    Their lab energies are equal, but a moving atom sees one blue-shifted and
    the other red-shifted, so in the rest frame where the perturbative energy
    denominators live they differ by 2 nu v / c. The SUM is what stays
    velocity-free, which is why the technique works, and the DIFFERENCE is
    what reopens rank 1.

    `v` here is the one-dimensional rms thermal speed along the beam.
    """
    kb, c = 1.380649e-23, 2.99792458e8
    mass = {"87Rb": 86.909180527, "85Rb": 84.911789738}[isotope] * 1.66053906660e-27
    from .polarizability import E_6S_CM
    nu = c / (1e7 / (E_6S_CM / 2.0) * 1e-9)
    return 2.0 * nu * math.sqrt(kb * (t_c + 273.15) / mass) / c


def rank_one_leak_rate(mismatch_deg: float, t_c: float = 130.0,
                       isotope: str = "87Rb") -> float:
    """Delta m_F = +-1 rate, as a fraction of the line, from the PRODUCT of
    the two factors rank 1 needs.

    Energy factor: the Doppler split above, over the detuning below 5P1/2.
    Polarisation factor: sin of the forward-to-retro mismatch angle, which an
    ideal retro sets to zero.

    Neither factor alone opens the channel and the product is what to quote.
    Returns a RATE fraction, so it is the square of the amplitude.
    """
    from .polarizability import LINES_5S, E_6S_CM
    detuning_hz = (LINES_5S[0][0] - E_6S_CM / 2.0) * 2.99792458e10
    energy = doppler_photon_split_hz(t_c, isotope) / detuning_hz
    return (math.sin(math.radians(abs(mismatch_deg))) * energy) ** 2


def vector_ratio(lam_nm: float = 993.4) -> float:
    """|d alpha_vector / d alpha_scalar| between 5S and 6S at this wavelength.

    Both sums run over the same committed line lists the scalar polarizability
    uses, with the J' = 1/2 and J' = 3/2 channels entering the vector sum with
    coefficients -1 and +1/2. That pair is what makes the vector term vanish
    when the fine structure is unresolved, which is the check that the sign
    convention is right: set the two detunings equal and the answer is zero.
    """
    from .polarizability import (LINES_5S, LINES_6S, CM_PER_HARTREE, E_6S_CM,
                                 alpha_5s, alpha_6s)
    w = 1.0 / (lam_nm * 1e-7) / CM_PER_HARTREE

    def vec(lines, e0):
        v = 0.0
        for i, (e_cm, d, _) in enumerate(lines):
            wn = (e_cm - e0) / CM_PER_HARTREE
            if wn <= 0.0:
                continue
            c = -1.0 if i % 2 == 0 else +0.5
            v += -(1.0 / 3.0) * c * d * d * w / (wn * wn - w * w)
        return v

    d_vec = vec(LINES_6S, E_6S_CM) - vec(LINES_5S, 0.0)
    d_sca = alpha_6s(lam_nm) - alpha_5s(lam_nm)
    return abs(d_vec / d_sca)


def vector_spread_mhz(s0_mhz: float, circular_degree: float,
                      lam_nm: float = 993.4) -> float:
    """Route 1: the m_F spread the vector light shift opens, in MHz.

    ``s0_mhz`` is the differential SCALAR shift at the same power, which is
    the quantity this record already measures, so the answer is expressed as
    a fraction of something committed rather than from an absolute intensity.
    ``circular_degree`` runs 0 for linear to 1 for fully circular.
    """
    return vector_ratio(lam_nm) * abs(circular_degree) * abs(s0_mhz)


def zeeman_satellite_mhz(isotope: str, b_field_ut: float) -> float:
    """Route 2: where a Delta m_F = +-1 component sits, in MHz from the line.

    Nothing cancels here, unlike the Delta m_F = 0 case, because the shift is
    g_F mu_B B rather than a difference of two nearly equal g_F.
    """
    return GF_S_HALF[isotope] * MU_B_MHZ_PER_UT * abs(b_field_ut)


def mismatch_intensity(mismatch_deg: float) -> float:
    """The Delta m_F = +-1 intensity a polarisation mismatch buys, relative
    to the scalar line: the antisymmetric part goes as sin of the angle and
    the scalar as its cosine, so the ratio is the tangent squared."""
    return math.tan(math.radians(abs(mismatch_deg))) ** 2


def extra_width_mhz(isotope: str, b_field_ut: float, mismatch_deg: float,
                    fwhm_mhz: float = 5.37) -> float:
    """How much wider the line gets from route 2, in MHz.

    A weak pair of satellites at +-s with fractional intensity f adds f s^2 to
    the second moment, and a Gaussian-equivalent width grows by
    (FWHM / 2) times that over the existing variance. Small-f expansion, which
    is the regime any real apparatus is in.
    """
    s = zeeman_satellite_mhz(isotope, b_field_ut)
    f = mismatch_intensity(mismatch_deg)
    var = (fwhm_mhz / 2.3548) ** 2
    return fwhm_mhz * 0.5 * f * s * s / var

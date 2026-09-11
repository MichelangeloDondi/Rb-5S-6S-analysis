"""Which decay branch the experiment collects, and what that choice costs.

WHY THIS IS A PARAMETER AND NOT A CONSTANT. The 2025 apparatus collects the
795 nm leg of the 6S cascade through about 50 dB of passband, and the whole
committed record is written under that choice. Another group has another
filter, and the choice is not cosmetic: the collected photon's wavelength
decides whether the signal is REABSORBED on its way out of the cell, and the
reabsorption is density-dependent, which puts it directly across every
density-linked amplitude claim. A model that hard-codes 795 nm cannot be
pointed at another bench, and cannot size the swap on this one.

THE THREE BRANCHES, and the physics that separates them.

* 795 nm, the D1 leg. 6S decays through 5P1/2, which then emits on the D1
  line. That photon is RESONANT WITH THE GROUND STATE, so ground-state atoms
  in the connected hyperfine level reabsorb it: radiation trapping with
  optical depth tau = f_hf * abundance * N(T) * sigma * L. This is the
  record's own configuration and `density.d1_optical_depth_per_cm` is the
  function that computes it.
* 780 nm, the D2 leg, through 5P3/2. ALSO resonant with the ground state, so
  it does NOT escape trapping. Its value is as a CONTRAST rather than as a
  cure: the two legs share one excitation and differ in reabsorption, so
  running both at one condition turns the trapping model from an assumption
  into a measurement. THIS MODULE DOES NOT SHIP A D2 CROSS-SECTION. The
  record carries only the D1 value, as an envelope, and inventing a second
  one would create a number with no source. Supply it explicitly.
* 1.32 to 1.37 um, the FIRST leg of the cascade, 6S -> 5P1/2 and 6S -> 5P3/2,
  carrying 34.09 and 65.91 per cent of the decays. NOT free of reabsorption,
  and saying it was is the error this module shipped with. Its
  Doppler-broadened cross-sections are 1.41 and 1.50e-11 cm^2, the same as
  D1's, so what separates the channels is POPULATION rather than wavelength.
  Inside the driven volume both legs are INVERTED, 4.81 and 5.25 to one,
  because 5P empties in 27 ns while the drive refills 6S, so there is no
  re-absorption where the signal is made. Outside it a 5P halo fed by trapped
  D-line photons re-excites at 1.07 per cent of the primary two-photon rate
  at 130 C, 0.08 at 110 C and nothing at 70 C. So this channel REDUCES the
  confound by about two orders at the top of the sweep rather than removing
  it, and the remainder is a term `scripts/run_trapping_channels.py` already
  computes. Needs an InGaAs detector, since the record's GaAs photocathode
  stops near 900 nm.

VALIDITY. `optical_depth_per_cm` inherits `SIGMA_D1_CM2`'s envelope status
for the D1 channel: the magnitude is order-of-magnitude, while the ISOTOPE
RATIO it implies is robust and is what drives differential trapping between
the four lines. For a channel supplied by the caller the returned depth is exactly
as good as the cross-section supplied with it, and no better.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

__all__ = ["DetectionChannel", "CHANNEL_795_D1", "CHANNEL_780_D2",
           "CHANNEL_1300_CASCADE", "default_channel",
           # the cascade's first leg, promoted here 2026-09-11; the three
           # names were left out of this list on the day they were added, so a
           # star-import of the module returned none of them while the package
           # surface test calls this list the package's own promise
           "einstein_a_per_s", "ir_branching_5p12", "mean_5p_lifetime_s"]


@dataclass(frozen=True)
class DetectionChannel:
    """The decay branch an apparatus collects.

    name              a short label, used in reports
    wavelength_nm     the collected photon's wavelength
    trapped           whether the photon is resonant with the GROUND state,
                      and therefore reabsorbed by the bulk vapour. Deliberately
                      narrow: a channel may still interact with an
                      excited-state population, which the infrared one does,
                      and that term belongs to run_trapping_channels.py
    sigma_cm2         the resonant absorption cross-section, required when
                      trapped is True and ignored otherwise. None means
                      none was supplied, which is an ERROR at the point of
                      use rather than a silent zero
    note              provenance of the numbers, carried so a report can
                      state where its trapping term came from
    """

    name: str
    wavelength_nm: float
    trapped: bool
    sigma_cm2: Optional[float] = None
    note: str = ""

    def optical_depth_per_cm(self, T_C: float, isotope: int,
                             f_hf: float = 0.5) -> float:
        """Resonant optical depth per cm of cell for this channel.

        Zero for an untrapped channel, by the physics rather than by a
        default. For a trapped channel without a cross-section this RAISES,
        because a missing cross-section is a missing input and silently
        returning zero would turn it into a claim that the photon escapes.
        """
        if not self.trapped:
            return 0.0
        if self.sigma_cm2 is None:
            raise ValueError(
                f"channel {self.name!r} is trapped but carries no "
                "sigma_cm2. Supply the resonant cross-section for this "
                "line; this module ships one only for D1, from the record.")
        from .constants import ABUNDANCE_RB85, ABUNDANCE_RB87
        from .density import number_density_cm3
        if isotope not in (85, 87):
            raise ValueError(
                f"isotope={isotope} is neither 85 nor 87; the abundances "
                f"here are rubidium's and any other value used to "
                f"receive Rb-87's silently.")
        ab = ABUNDANCE_RB85 if isotope == 85 else ABUNDANCE_RB87
        return f_hf * ab * number_density_cm3(T_C) * self.sigma_cm2


def _d1_sigma() -> float:
    from .constants import SIGMA_D1_CM2
    return SIGMA_D1_CM2


def _nm_from_terms(upper_cm: float, lower_cm: float) -> float:
    """Wavelength in nm from two term energies in inverse centimetres.

    The wavelengths below are COMPUTED from the NIST term energies this
    package already carries for its polarizability sums, rather than typed.
    A typed wavelength is a literal whose source no check can see, which is
    the defect class that put a retracted number on a public figure.
    """
    return 1.0e7 / (upper_cm - lower_cm)


def _levels():
    from .polarizability import E_5P12_CM, E_5P32_CM, E_6S_CM
    return E_5P12_CM, E_5P32_CM, E_6S_CM


_E_5P12, _E_5P32, _E_6S = _levels()

CHANNEL_795_D1 = DetectionChannel(
    name="795 nm (D1 leg)", wavelength_nm=_nm_from_terms(_E_5P12, 0.0),
    trapped=True, sigma_cm2=_d1_sigma(),
    note="the 2025 configuration; sigma from constants.SIGMA_D1_CM2, ENVELOPE")

CHANNEL_780_D2 = DetectionChannel(
    name="780 nm (D2 leg)", wavelength_nm=_nm_from_terms(_E_5P32, 0.0),
    trapped=True, sigma_cm2=None,
    note="the record ships no D2 cross-section; supply one to use this")

CHANNEL_1300_CASCADE = DetectionChannel(
    name="1.3 um (6S->5P leg)",
    wavelength_nm=0.5 * (_nm_from_terms(_E_6S, _E_5P12)
                         + _nm_from_terms(_E_6S, _E_5P32)),
    trapped=False,
    note="NOT trapped by the GROUND state, which is the mechanism the D-lines "
         "suffer, so the ground-state optical depth is zero by construction. "
         "It IS resonant with 5P at the same cross-section as D1, and the "
         "record computes what that costs: nothing inside the beam, where "
         "both legs are inverted 4.8 and 5.3 to 1, and about 1.07 per cent of "
         "the primary rate at 130 C from the halo outside it "
         "(results/trapping_channels.csv). Needs InGaAs")


def default_channel() -> DetectionChannel:
    """The channel the committed record was taken on.

    Every default in this package reproduces the 2025 apparatus, so a
    caller who changes nothing gets the record's own configuration and one
    who changes this gets their own.
    """
    return CHANNEL_795_D1


# ---------------------------------------------------------------------------
# THE CASCADE'S FIRST LEG, PROMOTED OUT OF A PRODUCER (2026-09-11)
# ---------------------------------------------------------------------------
# `scripts/run_trapping_channels.py` computed this branching from the package's
# own matrix elements and wrote it into `results/trapping_channels.csv`, and it
# was the only place that knew it. Then the platform twin needed it twice: the
# cascade's saturation renormalisation weights the 5P lifetime by it, and the
# fluorescence rows must multiply by the 795 nm share, which they did not. A
# numerical routine wanted at a second call site belongs in the package, so it
# is here.
#
# **THE PRODUCER STILL OWNS ITS COPY** (2026-09-11). The first form of this
# comment ended "and the producer calls this rather than its own copy", which
# was false when it was written: `scripts/run_trapping_channels.py` was not in
# that wave's staged set and still computes the branching from its own `_leg`
# and its own four SI literals. The two agree to 4e-7 by retyping, not by
# wiring. Migrating the producer is its own change, because it also owns the
# halo and the escape-factor arms that read those literals, and it is owed in
# `docs/plan/12`; until then this module is the second copy and says so.

def einstein_a_per_s(upper_cm: float, lower_cm: float, d_au: float) -> float:
    """Einstein A for one electric-dipole leg, from its energies and element.

    `d_au` is the reduced dipole matrix element in atomic units, as
    `polarizability.LINES_6S` carries it; the 2 in the denominator is the
    upper-state degeneracy factor for the 6S (J = 1/2) initial level.
    """
    import math

    from . import constants as _C
    lam = 1e7 / (upper_cm - lower_cm) * 1e-9
    omega = 2.0 * math.pi * _C.C_M_PER_S / lam
    d = d_au * _C.E_CHARGE_C * _C.A0_M
    return float(omega ** 3 * d ** 2
                 / (3.0 * math.pi * _C.EPS0 * _C.HBAR_JS * _C.C_M_PER_S ** 3 * 2))


def ir_branching_5p12() -> float:
    """The fraction of 6S decays taking the 5P1/2 leg, about 0.3409.

    THEORY-ONLY, and the results file says so: no published measurement of this
    branching exists (checked twice externally, 2026-09-06). 6S has no allowed
    decay to 5S, so the two infrared legs are the whole decay and their ratio
    is the branching.
    """
    from .polarizability import E_6S_CM, LINES_6S
    a12 = einstein_a_per_s(E_6S_CM, LINES_6S[0][0], LINES_6S[0][1])
    a32 = einstein_a_per_s(E_6S_CM, LINES_6S[1][0], LINES_6S[1][1])
    return float(a12 / (a12 + a32))


def mean_5p_lifetime_s() -> float:
    """The 5P lifetime a 6S atom actually waits out, weighted by the branching.

    The cascade's dead time and its saturation renormalisation both ask how
    long the atom is away, and it takes the 5P3/2 leg twice out of three. Using
    `TAU_5P12_S` alone, which every consumer did until 2026-09-11, overstates
    that wait by 3.6 per cent and the saturation factor by 0.8 per cent.
    Both lifetimes are Volz and Schmoranzer 1996, the same measurement.
    """
    from . import constants as _C
    b12 = ir_branching_5p12()
    return float(b12 * _C.TAU_5P12_S + (1.0 - b12) * _C.TAU_5P32_S)

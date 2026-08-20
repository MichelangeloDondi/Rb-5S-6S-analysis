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
  Inside the driven volume both legs are INVERTED, 4.81 and 5.26 to one,
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
           "CHANNEL_1300_CASCADE", "default_channel"]


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

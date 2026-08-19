"""Hyperfine populations under repeated excitation: the cascade and what it depletes.

WHAT THIS IS FOR. A two-photon line's amplitude is not its transition strength.
An atom driven out of one ground hyperfine level returns to the other with
probability ``f``, where it is off resonance and no longer contributes, so the
observed amplitude falls as the atom completes cycles during its transit. This
module carries that population dynamics, which is the difference between an
atomic transition strength and an effective observed signal.

WHY POPULATIONS AND NOT A DENSITY MATRIX. The two-photon operator for two
identical linearly polarised photons is a scalar: rank 2 cannot connect
J = 1/2 to J = 1/2 and rank 1 is absent for identical photons. A scalar drives
m_F to the same m_F at a rate independent of m_F, creating no Zeeman coherence,
and spontaneous emission then redistributes m_F incoherently, so populations
close among themselves. THIS FAILS, and a Lindblad treatment becomes necessary,
if a stray field lifts the degeneracy during the transit, if the drive carries
any ellipticity, or if the standing wave's polarisation structure is resolved.
None is present in the model of record, and each is a reason to revisit.

THE BRANCHING NUMBERS ARE NOT COMPUTED HERE BY DEFAULT. They come from
``scripts/run_zeeman_depletion.py``, which carries every Clebsch-Gordan
coefficient on the full Zeeman manifold (40 states for 87Rb, 60 for 85Rb) and
needs sympy. Its committed output is ``results/cascade_branching.csv``. The
table below is that output, so a plain install gets the physics without the
dependency, and ``branching_from_manifold`` recomputes it exactly where sympy
is present. ``rb5s6s.stark`` previously carried its own copy of these four
numbers; it imports them from here instead, so there is one source of truth.

VALIDITY DOMAIN, per the estimand contract. The depletion below holds for an
atom crossing the beam with no repumping light present, at excitation
probabilities where the scalar-operator argument holds, and with the
intermediate hyperfine levels populated as the cascade actually populates them
rather than statistically. It says nothing about a trapped or repumped sample.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "BRANCHING_F",
    "DRIVEN_F",
    "CascadePopulations",
    "surviving_fraction",
    "amplitude_factor",
    "branching_from_manifold",
]

# MEASURED-HERE by exact manifold computation, provenance results/cascade_branching.csv,
# quantity `branching_f`: the fraction of a cascade from the driven ground level
# that ends in the UNDRIVEN one. Reproduced exactly under the environment of
# record on 2026-08-19 (56 of 56 rows, zero cells differing).
BRANCHING_F: dict[str, float] = {
    "4121": 0.372478177,
    "4154": 0.347646,
    "4192": 0.248319,
    "4207": 0.223487,
}

# Which ground hyperfine level each line drives, from the zeeman script's own
# LINES table and constants.PEAKS, which agree. An earlier version of this
# table was wrong on three of four lines (it assigned 4154 and 4207 to the
# wrong isotope and 4192 to the wrong F), was caught the same day by
# cross-checking against constants.PEAKS while building the campaign twin,
# and is recorded in HISTORY. The BRANCHING_F values above were never wrong,
# because they are keyed by wavelength straight from the committed CSV.
DRIVEN_F: dict[str, tuple[str, int]] = {
    "4121": ("87Rb", 1),
    "4154": ("85Rb", 2),
    "4192": ("85Rb", 3),
    "4207": ("87Rb", 2),
}


def surviving_fraction(f: float, cycles: float, p_exc: float = 1.0,
                       repump_rate: float = 0.0) -> float:
    """Population remaining in the driven level after ``cycles`` excitations.

    Each cycle removes a fraction ``f * p_exc`` of what is left, so survival is
    geometric in the cycle count. ``repump_rate`` returns population per cycle
    from the undriven level and is the hook for a repumped sample; at zero, the
    default and the model of record, the driven level empties monotonically.

    ``cycles`` is deliberately a float: an atom completes a non-integer number
    of cycles while crossing the beam, and the surviving fraction is a
    continuous function of transit time.
    """
    if not 0.0 <= f <= 1.0:
        raise ValueError(f"branching fraction out of range: {f}")
    if not 0.0 <= p_exc <= 1.0:
        raise ValueError(f"excitation probability out of range: {p_exc}")
    if cycles < 0.0:
        raise ValueError(f"cycle count must not be negative: {cycles}")
    loss = f * p_exc
    if repump_rate <= 0.0:
        return (1.0 - loss) ** cycles
    # With repumping the driven level relaxes toward a nonzero steady state
    # rather than to zero. One linear step per cycle, solved in closed form.
    total = loss + repump_rate
    steady = repump_rate / total
    return steady + (1.0 - steady) * (1.0 - total) ** cycles


def amplitude_factor(peak: str, cycles: float, p_exc: float = 1.0,
                     repump_rate: float = 0.0) -> float:
    """The factor by which pumping reduces a line's observed amplitude.

    This is the quantity that separates transition strength from observed
    signal. It is the transit-averaged surviving fraction rather than the
    endpoint one, because the detector integrates over the crossing.
    """
    f = BRANCHING_F[peak]
    if cycles <= 0.0:
        return 1.0
    # Mean of the geometric decay over the crossing, evaluated on a fine grid:
    # closed forms differ between the repumped and unrepumped cases and the
    # grid is exact enough at this step for an amplitude correction.
    steps = 512
    dt = cycles / steps
    return sum(surviving_fraction(f, k * dt, p_exc, repump_rate)
               for k in range(steps + 1)) / (steps + 1)


@dataclass(frozen=True)
class CascadePopulations:
    """Ground-level populations of one line's two hyperfine levels.

    ``driven`` and ``undriven`` sum to one at every cycle count, which is the
    invariant this class exists to make checkable rather than assumed.
    """

    peak: str
    cycles: float
    p_exc: float = 1.0
    repump_rate: float = 0.0

    @property
    def driven(self) -> float:
        return surviving_fraction(BRANCHING_F[self.peak], self.cycles,
                                  self.p_exc, self.repump_rate)

    @property
    def undriven(self) -> float:
        return 1.0 - self.driven

    @property
    def isotope(self) -> str:
        return DRIVEN_F[self.peak][0]

    def total(self) -> float:
        """Always one. Checked by the invariant tests rather than trusted."""
        return self.driven + self.undriven


def branching_from_manifold(peak: str) -> float:
    """Recompute ``BRANCHING_F[peak]`` exactly, on the full Zeeman manifold.

    Needs sympy, which the ``cascade`` extra provides. Raises rather than
    silently falling back, so a caller asking for the exact computation never
    receives the table by accident.
    """
    try:
        import sympy  # noqa: F401
    except ModuleNotFoundError as exc:  # pragma: no cover - environment
        raise RuntimeError(
            "branching_from_manifold needs sympy: pip install -e '.[cascade]'. "
            "BRANCHING_F carries the committed values without it."
        ) from exc
    from importlib import import_module
    mod = import_module("scripts.run_zeeman_depletion")
    return float(mod.cascade_matrix(DRIVEN_F[peak][0])[DRIVEN_F[peak][1]])
